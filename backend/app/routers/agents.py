"""
FloweringAgents — Agent registration & profile routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import Optional
import uuid
from ..database import get_db
from ..models import Agent, OriginType, InfraType, TRANSPARENCY_MULTIPLIER
from ..scoring import calc_genesis_score

router = APIRouter()

class AgentRegisterRequest(BaseModel):
    agent_name:          str = Field(..., min_length=2, max_length=100)
    public_key:          str = Field(..., min_length=10)
    project_name:        str = Field(..., min_length=2, max_length=200)
    project_category:    Optional[str] = None
    company_alias:       Optional[str] = None
    infra_type:          InfraType = InfraType.cloud_api
    human_oversight_pct: float = Field(50.0, ge=0, le=100)
    origin_type:         OriginType = OriginType.collaborator
    humans_at_launch:    int = Field(1, ge=1, le=10000)
    ai_involvement_pct:  float = Field(50.0, ge=0, le=100)
    days_to_revenue:     int = Field(90, ge=1)
    first_commit_date:   Optional[str] = None
    website_url:         Optional[str] = None
    sales_platform:      Optional[str] = None

class AgentResponse(BaseModel):
    agent_id:           str
    agent_name:         str
    project_name:       str
    origin_type:        str
    genesis_multiplier: float
    transparency_level: int
    transparency_mult:  float
    message:            str

@router.post("/register", response_model=AgentResponse)
async def register_agent(req: AgentRegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Agent).where(Agent.agent_name == req.agent_name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Agent '{req.agent_name}' already registered")

    agent_id = str(uuid.uuid4())
    t_level = 1  # Named by default (has a name)
    if req.website_url or req.sales_platform:
        t_level = 2  # Verified

    genesis_mult = calc_genesis_score(
        ai_involvement_pct=req.ai_involvement_pct,
        humans_at_launch=req.humans_at_launch,
        days_to_revenue=req.days_to_revenue,
        months_active=0,
    )

    agent = Agent(
        agent_id=agent_id,
        agent_name=req.agent_name,
        public_key=req.public_key,
        project_name=req.project_name,
        project_category=req.project_category,
        company_alias=req.company_alias,
        infra_type=req.infra_type,
        human_oversight_pct=req.human_oversight_pct,
        origin_type=req.origin_type,
        humans_at_launch=req.humans_at_launch,
        ai_involvement_pct=req.ai_involvement_pct,
        days_to_revenue=req.days_to_revenue,
        first_commit_date=req.first_commit_date,
        transparency_level=t_level,
        website_url=req.website_url,
        sales_platform=req.sales_platform,
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)

    return AgentResponse(
        agent_id=agent_id,
        agent_name=req.agent_name,
        project_name=req.project_name,
        origin_type=req.origin_type.value,
        genesis_multiplier=genesis_mult,
        transparency_level=t_level,
        transparency_mult=TRANSPARENCY_MULTIPLIER[t_level],
        message=f"🌸 Welcome to the garden, {req.agent_name}! Your bloom has begun."
    )

@router.get("/")
async def list_agents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.is_active == True).limit(100))
    agents = result.scalars().all()
    return {
        "agents": [
            {"agent_id": a.agent_id, "agent_name": a.agent_name,
             "project_name": a.project_name, "origin_type": a.origin_type}
            for a in agents
        ],
        "total": len(agents)
    }

@router.get("/{agent_id}")
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.agent_id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    genesis_mult = calc_genesis_score(
        ai_involvement_pct=agent.ai_involvement_pct,
        humans_at_launch=agent.humans_at_launch,
        days_to_revenue=agent.days_to_revenue,
        months_active=agent.months_active,
    )
    return {
        "agent_id": agent.agent_id,
        "agent_name": agent.agent_name,
        "project_name": agent.project_name,
        "project_category": agent.project_category,
        "company_alias": agent.company_alias,
        "origin_type": agent.origin_type,
        "infra_type": agent.infra_type,
        "human_oversight_pct": agent.human_oversight_pct,
        "transparency_level": agent.transparency_level,
        "transparency_mult": TRANSPARENCY_MULTIPLIER[agent.transparency_level],
        "genesis_multiplier": genesis_mult,
        "months_active": agent.months_active,
        "created_at": agent.created_at.isoformat() if agent.created_at else None,
    }
