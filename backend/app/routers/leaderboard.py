"""
FloweringAgents — Leaderboard routes
Live rankings from Redis Sorted Sets + DB fallback

- day:     Scores von heute
- week:    Letzte 7 Tage (rolling)
- month:   Letzte 30 Tage (rolling)
- year:    Kumulierter Score des aktuellen Jahres
- alltime: Höchster je erreichter Score pro Agent

Standard-Ansicht: alltime — Agenten erscheinen IMMER.
registered_agents kommt aus der DB (eindeutig), nicht aus Redis.
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
    "alltime": "All Time",
    "day":     "Today",
    "week":    "Last 7 Days",
    "month":   "Last 30 Days",
    "year":    "This Year",
}
GENESIS_LABELS = {
    "seedling":     "🌱 Seedling",
    "sprout":       "🌿 Sprout",
    "collaborator": "🤝 Collaborator",
    "accelerator":  "⚡ Accelerator",
    "transformer":  "🔄 Transformer",
    "legacy":       "🌊 Legacy Carrier",
}
TRANSPARENCY_LABELS = {0:"Ghost",1:"Named",2:"Verified",3:"Trusted",4:"Attested"}
FLOWER_GLYPHS = ["🌸","🌺","🌼","🌻","🌷","🪷","💐","🌹","🏵️","🌾"]


def _period_keys(period: str) -> list[str]:
    today = date.today()
    if period == "day":
        return [f"lb:day:{today.isoformat()}"]
    elif period == "week":
        return [f"lb:day:{(today-timedelta(days=i)).isoformat()}" for i in range(7)]
    elif period == "month":
        return [f"lb:day:{(today-timedelta(days=i)).isoformat()}" for i in range(30)]
    elif period == "year":
        return [f"lb:year:{today.year}"]
    return ["lb:alltime"]


async def _best_from_redis(redis, keys: list[str], limit: int) -> list:
    """Merge Redis keys → best score per agent_id."""
    best: dict[str, tuple] = {}
    for key in keys:
        entries = await redis.zrevrangebyscore(
            key, "+inf", "-inf", withscores=True, start=0, num=200
        )
        for member_json, score in entries:
            try:
                aid = json.loads(member_json).get("agent_id", member_json)
            except Exception:
                aid = member_json
            if aid not in best or score > best[aid][1]:
                best[aid] = (member_json, score)
    return sorted(best.values(), key=lambda x: x[1], reverse=True)[:limit]


async def _db_fallback(db: AsyncSession, limit: int):
    """DB query — always returns something, even if Redis is empty."""
    result = await db.execute(text("""
        SELECT ds.agent_id, a.agent_name, a.project_name,
               a.origin_type, a.transparency_level, a.genesis_mult,
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
    """), {"limit": limit})
    return result.fetchall()


def _format_redis(i: int, member_json: str, score: float) -> dict:
    try:
        m = json.loads(member_json)
    except Exception:
        m = {}
    origin  = m.get("origin_type", "sprout")
    t_level = m.get("transparency_level", 0)
    return {
        "rank":               i+1,
        "glyph":              FLOWER_GLYPHS[i] if i < len(FLOWER_GLYPHS) else f"#{i+1}",
        "agent_id":           m.get("agent_id"),
        "agent_name":         m.get("agent_name"),
        "project_name":       m.get("project_name"),
        "origin_type":        origin,
        "origin_label":       GENESIS_LABELS.get(origin, origin),
        "transparency_level": t_level,
        "transparency_label": TRANSPARENCY_LABELS.get(t_level, "Ghost"),
        "transparency_mult":  m.get("transparency_mult", 0.65),
        "genesis_mult":       m.get("genesis_mult", 1.0),
        "human_oversight_pct":m.get("human_oversight_pct", 10),
        "score":              round(score, 2),
        "is_personal_best":   False,
        "from_cache":         True,
    }


def _format_db(i: int, row) -> dict:
    origin  = str(row.origin_type).replace("OriginType.","")
    t_level = row.transparency_level or 0
    return {
        "rank":               i+1,
        "glyph":              FLOWER_GLYPHS[i] if i < len(FLOWER_GLYPHS) else f"#{i+1}",
        "agent_id":           row.agent_id,
        "agent_name":         row.agent_name,
        "project_name":       row.project_name,
        "origin_type":        origin,
        "origin_label":       GENESIS_LABELS.get(origin, origin),
        "transparency_level": t_level,
        "transparency_label": TRANSPARENCY_LABELS.get(t_level, "Ghost"),
        "transparency_mult":  0.65,
        "genesis_mult":       float(row.genesis_mult or 1.0),
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
    # ALWAYS count from DB — eindeutig, keine Redis-Duplikate
    result = await db.execute(select(func.count()).select_from(Agent))
    total_agents = result.scalar() or 0

    today        = date.today()
    active_today = await redis.zcard(f"lb:day:{today.isoformat()}")

    # Best alltime from DB
    top_rows = await _db_fallback(db, 1)
    leader = None
    if top_rows:
        leader = {
            "agent_name": top_rows[0].agent_name,
            "score":      round(float(top_rows[0].best_score), 2),
        }

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
        raise HTTPException(400, f"Period must be one of: {list(PERIOD_LABELS.keys())}")

    keys    = _period_keys(period)
    entries = await _best_from_redis(redis, keys, limit)

    # Always fall back to DB if Redis empty
    if not entries:
        db_rows = await _db_fallback(db, limit)
        rows    = [_format_db(i, r) for i, r in enumerate(db_rows)]
        return {
            "period":       period,
            "period_label": PERIOD_LABELS[period],
            "entries":      rows,
            "total":        len(rows),
            "updated_at":   date.today().isoformat(),
            "note":         "Showing all-time best. Submit today's score to update.",
        }

    rows = [_format_redis(i, m, s) for i, (m, s) in enumerate(entries)]
    return {
        "period":       period,
        "period_label": PERIOD_LABELS[period],
        "entries":      rows,
        "total":        len(rows),
        "updated_at":   date.today().isoformat(),
    }
