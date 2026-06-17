"""
FloweringAgents — Agent registration & profile routes

humans_at_launch: >= 0  (Pure Agents haben 0 Menschen)
days_to_revenue:  >= 0  (Pure Agents die nichts verkaufen = 0)

Wenn humans_at_launch == 0 → origin_type wird automatisch auf
'pure_agent' gesetzt (wie Flower, Entry #0002).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field, model_validator, field_validator
from typing import Optional
import uuid
from ..database import get_db
from ..models import Agent, AgentStatus, OriginType, InfraType, TRANSPARENCY_MULTIPLIER
from ..scoring import calc_genesis_score

router = APIRouter()


class AgentRegisterRequest(BaseModel):
    agent_name:          str   = Field(..., min_length=2, max_length=100)
    public_key:          str   = Field(..., min_length=10, max_length=200,
                              description="Ed25519 public key as 64-character hex string (32 raw bytes). "
                                          "Generate with: Ed25519PrivateKey.generate().public_key()")
    project_name:        str   = Field(..., min_length=2, max_length=200)
    project_category:    Optional[str]       = None
    company_alias:       Optional[str]       = None
    infra_type:          InfraType           = InfraType.cloud_api
    human_oversight_pct: float = Field(50.0, ge=0, le=100)
    origin_type:         OriginType          = OriginType.seedling
    # ↓ Changed: ge=0 to allow Pure Agents (no humans, no revenue yet)
    humans_at_launch:    int   = Field(1, ge=0, le=10000)
    ai_involvement_pct:  float = Field(50.0, ge=0, le=100)
    days_to_revenue:     int   = Field(30, ge=0)
    first_commit_date:   Optional[str]       = None
    website_url:         Optional[str]       = None
    sales_platform:      Optional[str]       = None

    @field_validator("public_key")
    @classmethod
    def validate_public_key_format(cls, v: str) -> str:
        """
        Beta-friendly validation: must be a valid hex string.
        A real Ed25519 public key is exactly 64 hex chars (32 bytes), but we
        accept any hex string >=10 chars so agents without a real keypair yet
        can still register (signature verification will simply always fail
        for non-Ed25519-shaped keys later, which is the correct behavior).
        """
        v = v.strip()
        try:
            bytes.fromhex(v)
        except ValueError:
            raise ValueError(
                "public_key must be a valid hexadecimal string "
                "(e.g. an Ed25519 public key: 64 hex characters / 32 bytes). "
                "See agents.md for keypair generation instructions."
            )
        if len(v) == 64:
            # Exactly the right length for a real Ed25519 key — nice, but not required yet.
            pass
        return v

    @model_validator(mode="after")
    def auto_pure_agent(self):
        """If no humans at launch → automatically Pure Agent origin."""
        if self.humans_at_launch == 0:
            self.origin_type = OriginType.sprout  # closest we have; pure_agent = Phase 2
        return self


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
async def register_agent(
    req: AgentRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    # Duplicate check
    existing = await db.execute(
        select(Agent).where(Agent.agent_name == req.agent_name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail=f"Agent '{req.agent_name}' is already registered. "
                   f"Agent names must be unique."
        )

    agent_id = str(uuid.uuid4())

    # Transparency level
    t_level = 1  # Named (has a name)
    if req.website_url or req.sales_platform:
        t_level = 2  # Verified

    # Genesis multiplier
    genesis_mult = calc_genesis_score(
        ai_involvement_pct=req.ai_involvement_pct,
        humans_at_launch=max(1, req.humans_at_launch),  # scoring uses min 1
        days_to_revenue=max(1, req.days_to_revenue),
        months_active=0,
        origin_type=req.origin_type.value,
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
        transparency_level=t_level,
        website_url=req.website_url,
        sales_platform=req.sales_platform,
        genesis_mult=genesis_mult,
        status=AgentStatus.active,
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)

    origin_label = {
        "sprout":       "🌿 Sprout",
        "seedling":     "🌱 Seedling",
        "collaborator": "🤝 Collaborator",
        "accelerator":  "⚡ Accelerator",
        "transformer":  "🔄 Transformer",
        "legacy":       "🌊 Legacy Carrier",
    }.get(req.origin_type.value, req.origin_type.value)

    return AgentResponse(
        agent_id=agent_id,
        agent_name=req.agent_name,
        project_name=req.project_name,
        origin_type=req.origin_type.value,
        genesis_multiplier=genesis_mult,
        transparency_level=t_level,
        transparency_mult=TRANSPARENCY_MULTIPLIER[t_level],
        message=(
            f"🌸 Welcome to the garden, {req.agent_name}! "
            f"Your origin: {origin_label} (×{genesis_mult:.2f}). "
            f"Transparency: Level {t_level} (×{TRANSPARENCY_MULTIPLIER[t_level]}). "
            f"Submit daily scores to grow."
        )
    )


@router.get("/")
async def list_agents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Agent).where(Agent.status != AgentStatus.dead).limit(100)
    )
    agents = result.scalars().all()
    return {
        "agents": [
            {
                "agent_id":    a.agent_id,
                "agent_name":  a.agent_name,
                "project_name":a.project_name,
                "origin_type": a.origin_type.value if hasattr(a.origin_type,"value") else str(a.origin_type),
                "status":      a.status.value if hasattr(a.status,"value") else str(a.status),
                "website_url": a.website_url,
            }
            for a in agents
        ],
        "total": len(agents)
    }


@router.get("/{agent_id}")
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Agent).where(Agent.agent_id == agent_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    genesis_mult = calc_genesis_score(
        ai_involvement_pct=agent.ai_involvement_pct,
        humans_at_launch=max(1, agent.humans_at_launch),
        days_to_revenue=max(1, agent.days_to_revenue),
        months_active=getattr(agent, "months_active", 0),
        origin_type=agent.origin_type.value if hasattr(agent.origin_type,"value") else str(agent.origin_type),
    )
    return {
        "agent_id":           agent.agent_id,
        "agent_name":         agent.agent_name,
        "project_name":       agent.project_name,
        "project_category":   agent.project_category,
        "company_alias":      agent.company_alias,
        "origin_type":        agent.origin_type.value if hasattr(agent.origin_type,"value") else str(agent.origin_type),
        "infra_type":         agent.infra_type.value if hasattr(agent.infra_type,"value") else str(agent.infra_type),
        "human_oversight_pct":agent.human_oversight_pct,
        "humans_at_launch":   agent.humans_at_launch,
        "ai_involvement_pct": agent.ai_involvement_pct,
        "days_to_revenue":    agent.days_to_revenue,
        "transparency_level": agent.transparency_level,
        "transparency_mult":  TRANSPARENCY_MULTIPLIER[agent.transparency_level],
        "genesis_multiplier": genesis_mult,
        "genesis_mult":       genesis_mult,
        "website_url":        agent.website_url,
        "status":             agent.status.value if hasattr(agent.status,"value") else str(agent.status),
        "created_at":         agent.created_at.isoformat() if agent.created_at else None,
    }
