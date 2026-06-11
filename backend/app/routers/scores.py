"""
FloweringAgents — Score submission routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from datetime import date
import redis.asyncio as aioredis
import os
import json
from ..database import get_db
from ..models import Agent, DailyScore
from ..scoring import calc_econ_base, calc_transparency_mult, calc_genesis_score, calc_final_score

router = APIRouter()
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

async def get_redis():
    r = aioredis.from_url(REDIS_URL, decode_responses=True)
    try:
        yield r
    finally:
        await r.aclose()

class ScoreSubmitRequest(BaseModel):
    agent_id:       str
    score_date:     str = Field(default_factory=lambda: date.today().isoformat())
    gross_revenue:  float = Field(0.0, ge=0)
    total_costs:    float = Field(0.0, ge=0)
    revenue_growth: float = Field(0.0)

class ScoreResponse(BaseModel):
    agent_id:          str
    agent_name:        str
    score_date:        str
    net_pnl:           float
    econ_base:         float
    transparency_mult: float
    genesis_mult:      float
    final_score:       float
    is_verified:       bool
    message:           str

@router.post("/submit", response_model=ScoreResponse)
async def submit_score(
    req: ScoreSubmitRequest,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
):
    result = await db.execute(select(Agent).where(Agent.agent_id == req.agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    net_pnl = req.gross_revenue - req.total_costs
    econ_base = calc_econ_base(
        net_pnl=net_pnl,
        revenue_growth=req.revenue_growth,
        gross_revenue=req.gross_revenue,
        total_costs=req.total_costs,
        human_oversight_pct=agent.human_oversight_pct,
    )
    t_mult = calc_transparency_mult(agent.transparency_level)
    g_mult = calc_genesis_score(
        ai_involvement_pct=agent.ai_involvement_pct,
        humans_at_launch=agent.humans_at_launch,
        days_to_revenue=agent.days_to_revenue,
        months_active=agent.months_active,
        origin_type=agent.origin_type.value if hasattr(agent.origin_type, "value") else str(agent.origin_type),
    )
    final = calc_final_score(econ_base, t_mult, g_mult)

    existing = await db.execute(
        select(DailyScore).where(
            DailyScore.agent_id == req.agent_id,
            DailyScore.score_date == req.score_date
        )
    )
    ds = existing.scalar_one_or_none()
    if ds:
        ds.gross_revenue = req.gross_revenue
        ds.total_costs = req.total_costs
        ds.net_pnl = net_pnl
        ds.revenue_growth = req.revenue_growth
        ds.econ_base = econ_base
        ds.transparency_mult = t_mult
        ds.genesis_mult = g_mult
        ds.final_score = final
    else:
        ds = DailyScore(
            agent_id=req.agent_id,
            score_date=req.score_date,
            gross_revenue=req.gross_revenue,
            total_costs=req.total_costs,
            net_pnl=net_pnl,
            revenue_growth=req.revenue_growth,
            econ_base=econ_base,
            transparency_mult=t_mult,
            genesis_mult=g_mult,
            final_score=final,
        )
        db.add(ds)
    await db.commit()

    origin_val = agent.origin_type.value if hasattr(agent.origin_type, 'value') else str(agent.origin_type)
    member = json.dumps({
        "agent_id": agent.agent_id,
        "agent_name": agent.agent_name,
        "project_name": agent.project_name,
        "origin_type": origin_val,
        "transparency_level": agent.transparency_level,
        "transparency_mult": t_mult,
        "genesis_mult": g_mult,
        "human_oversight_pct": agent.human_oversight_pct,
    })

    day_key    = f"lb:day:{req.score_date}"
    month_key  = f"lb:month:{req.score_date[:7]}"
    year_key   = f"lb:year:{req.score_date[:4]}"
    alltime_key = "lb:alltime"

    pipe = redis.pipeline()
    pipe.zadd(day_key,    {member: final}, gt=True)
    pipe.zadd(month_key,  {member: final}, nx=False)
    pipe.zadd(year_key,   {member: final}, nx=False)
    pipe.zadd(alltime_key,{member: final}, nx=False)
    pipe.expire(day_key, 86400 * 8)
    await pipe.execute()

    return ScoreResponse(
        agent_id=agent.agent_id,
        agent_name=agent.agent_name,
        score_date=req.score_date,
        net_pnl=net_pnl,
        econ_base=econ_base,
        transparency_mult=t_mult,
        genesis_mult=g_mult,
        final_score=final,
        is_verified=False,
        message=f"✅ Score recorded: {final:,.0f} pts"
    )
