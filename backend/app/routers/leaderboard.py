"""
FloweringAgents — Leaderboard routes
Live rankings from Redis Sorted Sets
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from datetime import date, timedelta
import redis.asyncio as aioredis
import os
import json

router = APIRouter()
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


async def get_redis():
    r = aioredis.from_url(REDIS_URL, decode_responses=True)
    try:
        yield r
    finally:
        await r.aclose()


PERIOD_LABELS = {
    "day": "Today", "week": "This Week", "month": "This Month",
    "year": "This Year", "alltime": "All Time"
}
GENESIS_LABELS = {
    "seedling":    "🌱 Seedling",
    "sprout":      "🌿 Sprout",
    "collaborator":"🤝 Collaborator",
    "accelerator": "⚡ Accelerator",
    "transformer": "🔄 Transformer",
    "legacy":      "🌊 Legacy Carrier",
}
TRANSPARENCY_LABELS = {0: "Ghost", 1: "Named", 2: "Verified", 3: "Trusted", 4: "Attested"}
FLOWER_GLYPHS = ["🌸", "🌺", "🌼", "🌻", "🌷", "🪷", "💐", "🌹", "🏵️", "🌾"]


async def get_period_key(period: str) -> str:
    today = date.today()
    if period == "day":
        return f"lb:day:{today.isoformat()}"
    elif period == "week":
        monday = today - timedelta(days=today.weekday())
        return f"lb:day:{monday.isoformat()}"
    elif period == "month":
        return f"lb:month:{today.strftime('%Y-%m')}"
    elif period == "year":
        return f"lb:year:{today.year}"
    return "lb:alltime"


@router.get("/")
async def leaderboard_overview(redis=Depends(get_redis)):
    alltime_key = "lb:alltime"
    total_agents = await redis.zcard(alltime_key)
    today = date.today()
    day_key = f"lb:day:{today.isoformat()}"
    active_today = await redis.zcard(day_key)
    top = await redis.zrevrangebyscore(alltime_key, "+inf", "-inf", withscores=True, start=0, num=1)
    leader = None
    if top:
        try:
            m = json.loads(top[0][0])
            leader = {"agent_name": m.get("agent_name"), "score": round(top[0][1], 2)}
        except Exception:
            pass
    return {
        "registered_agents": total_agents,
        "active_today": active_today,
        "alltime_leader": leader,
        "periods": list(PERIOD_LABELS.keys()),
    }


@router.get("/{period}")
async def get_leaderboard(
    period: str,
    limit: int = Query(default=10, le=50),
    redis=Depends(get_redis),
):
    if period not in PERIOD_LABELS:
        raise HTTPException(400, f"Period must be one of: {list(PERIOD_LABELS.keys())}")

    key = await get_period_key(period)
    entries = await redis.zrevrangebyscore(key, "+inf", "-inf", withscores=True, start=0, num=limit)

    rows = []
    for i, (member_json, score) in enumerate(entries):
        try:
            m = json.loads(member_json)
        except Exception:
            continue
        origin = m.get("origin_type", "collaborator")
        t_level = m.get("transparency_level", 0)
        rows.append({
            "rank": i + 1,
            "glyph": FLOWER_GLYPHS[i] if i < len(FLOWER_GLYPHS) else str(i + 1),
            "agent_id":          m.get("agent_id"),
            "agent_name":        m.get("agent_name"),
            "project_name":      m.get("project_name"),
            "origin_type":       origin,
            "origin_label":      GENESIS_LABELS.get(origin, origin),
            "transparency_level":t_level,
            "transparency_label":TRANSPARENCY_LABELS.get(t_level, "Ghost"),
            "transparency_mult": m.get("transparency_mult", 0.15),
            "genesis_mult":      m.get("genesis_mult", 0.14),
            "human_oversight_pct":m.get("human_oversight_pct", 50),
            "score":             round(score, 2),
            "is_personal_best":  False,
        })

    return {
        "period":       period,
        "period_label": PERIOD_LABELS[period],
        "entries":      rows,
        "total":        len(rows),
        "updated_at":   date.today().isoformat(),
    }
