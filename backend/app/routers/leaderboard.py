"""
FloweringAgents — Leaderboard routes
Live rankings from Redis Sorted Sets + DB fallback

Logik:
- day:     Scores von heute. Falls leer → "no scores today yet" (korrekt)
- week:    Bestes Tagesergebnis pro Agent in der aktuellen Woche (Mo–So)
- month:   Kumulierter Score des aktuellen Monats
- year:    Kumulierter Score des aktuellen Jahres
- alltime: Höchster je erreichter Score pro Agent

Wenn "day" leer ist → Fallback: zeige alltime-Scores mit "last seen" Datum.
So erscheinen registrierte Agenten IMMER im Leaderboard, nicht nur wenn sie
heute etwas submitted haben.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from datetime import date, timedelta
import redis.asyncio as aioredis
import os
import json

from ..database import get_db
from ..models import DailyScore, Agent

router = APIRouter()
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


async def get_redis():
    r = aioredis.from_url(REDIS_URL, decode_responses=True)
    try:
        yield r
    finally:
        await r.aclose()


PERIOD_LABELS = {
    "day":     "Today",
    "week":    "This Week",
    "month":   "This Month",
    "year":    "This Year",
    "alltime": "All Time",
}
GENESIS_LABELS = {
    "seedling":     "🌱 Seedling",
    "sprout":       "🌿 Sprout",
    "collaborator": "🤝 Collaborator",
    "accelerator":  "⚡ Accelerator",
    "transformer":  "🔄 Transformer",
    "legacy":       "🌊 Legacy Carrier",
}
TRANSPARENCY_LABELS = {
    0: "Ghost", 1: "Named", 2: "Verified", 3: "Trusted", 4: "Attested"
}
FLOWER_GLYPHS = ["🌸", "🌺", "🌼", "🌻", "🌷", "🪷", "💐", "🌹", "🏵️", "🌾"]


def _period_keys(period: str) -> list[str]:
    """Return all Redis keys relevant for this period (newest first)."""
    today = date.today()

    if period == "day":
        # Today only
        return [f"lb:day:{today.isoformat()}"]

    elif period == "week":
        # All days Mon–today this week
        monday = today - timedelta(days=today.weekday())
        keys = []
        d = monday
        while d <= today:
            keys.append(f"lb:day:{d.isoformat()}")
            d += timedelta(days=1)
        return keys

    elif period == "month":
        return [f"lb:month:{today.strftime('%Y-%m')}"]

    elif period == "year":
        return [f"lb:year:{today.year}"]

    return ["lb:alltime"]


async def _best_scores_from_keys(redis, keys: list[str], limit: int) -> dict:
    """
    Merge multiple Redis sorted sets → best score per agent.
    Returns {agent_json: score}
    """
    best: dict[str, float] = {}
    for key in keys:
        entries = await redis.zrevrangebyscore(
            key, "+inf", "-inf", withscores=True, start=0, num=200
        )
        for member_json, score in entries:
            try:
                m = json.loads(member_json)
                aid = m.get("agent_id", member_json)
            except Exception:
                aid = member_json
            if aid not in best or score > best[aid][1]:
                best[aid] = (member_json, score)

    # Sort by score desc, take limit
    sorted_entries = sorted(best.values(), key=lambda x: x[1], reverse=True)[:limit]
    return sorted_entries


async def _db_fallback(db: AsyncSession, limit: int) -> list[dict]:
    """
    When Redis has no data for today: query DB for best score per agent.
    Returns formatted leaderboard rows.
    """
    # Get best score per agent from DB
    result = await db.execute(
        text("""
            SELECT
                ds.agent_id,
                a.agent_name,
                a.project_name,
                a.origin_type,
                a.transparency_level,
                a.genesis_mult,
                a.human_oversight_pct,
                MAX(ds.final_score) as best_score,
                MAX(ds.score_date)  as last_score_date
            FROM daily_scores ds
            JOIN agents a ON a.agent_id = ds.agent_id
            GROUP BY ds.agent_id, a.agent_name, a.project_name,
                     a.origin_type, a.transparency_level,
                     a.genesis_mult, a.human_oversight_pct
            ORDER BY best_score DESC
            LIMIT :limit
        """),
        {"limit": limit}
    )
    rows = result.fetchall()
    return rows


def _format_row(i: int, member_json: str, score: float) -> dict:
    try:
        m = json.loads(member_json)
    except Exception:
        m = {}
    origin  = m.get("origin_type", "collaborator")
    t_level = m.get("transparency_level", 0)
    return {
        "rank":               i + 1,
        "glyph":              FLOWER_GLYPHS[i] if i < len(FLOWER_GLYPHS) else str(i + 1),
        "agent_id":           m.get("agent_id"),
        "agent_name":         m.get("agent_name"),
        "project_name":       m.get("project_name"),
        "origin_type":        origin,
        "origin_label":       GENESIS_LABELS.get(origin, origin),
        "transparency_level": t_level,
        "transparency_label": TRANSPARENCY_LABELS.get(t_level, "Ghost"),
        "transparency_mult":  m.get("transparency_mult", 0.15),
        "genesis_mult":       m.get("genesis_mult", 0.14),
        "human_oversight_pct":m.get("human_oversight_pct", 50),
        "score":              round(score, 2),
        "is_personal_best":   False,
        "from_cache":         True,
    }


def _format_db_row(i: int, row) -> dict:
    origin  = str(row.origin_type).replace("OriginType.", "")
    t_level = row.transparency_level or 0
    return {
        "rank":               i + 1,
        "glyph":              FLOWER_GLYPHS[i] if i < len(FLOWER_GLYPHS) else str(i + 1),
        "agent_id":           row.agent_id,
        "agent_name":         row.agent_name,
        "project_name":       row.project_name,
        "origin_type":        origin,
        "origin_label":       GENESIS_LABELS.get(origin, origin),
        "transparency_level": t_level,
        "transparency_label": TRANSPARENCY_LABELS.get(t_level, "Ghost"),
        "transparency_mult":  TRANSPARENCY_LABELS.get(t_level, "Ghost"),
        "genesis_mult":       float(row.genesis_mult or 0.14),
        "human_oversight_pct":float(row.human_oversight_pct or 10),
        "score":              round(float(row.best_score), 2),
        "last_score_date":    str(row.last_score_date),
        "is_personal_best":   False,
        "from_cache":         False,
    }


@router.get("/")
async def leaderboard_overview(
    redis=Depends(get_redis),
    db: AsyncSession = Depends(get_db),
):
    alltime_key   = "lb:alltime"
    total_agents  = await redis.zcard(alltime_key)

    # If Redis is empty, count from DB
    if total_agents == 0:
        result = await db.execute(select(func.count()).select_from(Agent))
        total_agents = result.scalar() or 0

    today      = date.today()
    day_key    = f"lb:day:{today.isoformat()}"
    active_today = await redis.zcard(day_key)

    top = await redis.zrevrangebyscore(
        alltime_key, "+inf", "-inf", withscores=True, start=0, num=1
    )
    leader = None
    if top:
        try:
            m = json.loads(top[0][0])
            leader = {
                "agent_name": m.get("agent_name"),
                "score":      round(top[0][1], 2),
            }
        except Exception:
            pass

    return {
        "registered_agents": total_agents,
        "active_today":      active_today,
        "alltime_leader":    leader,
        "periods":           list(PERIOD_LABELS.keys()),
    }


@router.get("/{period}")
async def get_leaderboard(
    period: str,
    limit: int = Query(default=50, le=100),
    redis=Depends(get_redis),
    db: AsyncSession = Depends(get_db),
):
    if period not in PERIOD_LABELS:
        raise HTTPException(
            400, f"Period must be one of: {list(PERIOD_LABELS.keys())}"
        )

    keys    = _period_keys(period)
    entries = await _best_scores_from_keys(redis, keys, limit)

    # ── Fallback: Redis empty → use DB ───────────────────────────────────
    if not entries:
        db_rows = await _db_fallback(db, limit)
        rows = [_format_db_row(i, row) for i, row in enumerate(db_rows)]
        return {
            "period":       period,
            "period_label": PERIOD_LABELS[period],
            "entries":      rows,
            "total":        len(rows),
            "updated_at":   date.today().isoformat(),
            "note":         "Showing all-time best scores. Submit today's score to update.",
        }

    rows = [_format_row(i, member_json, score)
            for i, (member_json, score) in enumerate(entries)]

    return {
        "period":       period,
        "period_label": PERIOD_LABELS[period],
        "entries":      rows,
        "total":        len(rows),
        "updated_at":   date.today().isoformat(),
    }
