"""
FloweringAgents — Database models
"""
from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, Text, Enum as SAEnum
from sqlalchemy.sql import func
from .database import Base
import enum
from uuid import uuid4 as _uuid4
from sqlalchemy import Text as _SAText, JSON as _SAJSON
from sqlalchemy.dialects.postgresql import UUID as _PGUUID


class OriginType(str, enum.Enum):
    sprout       = "sprout"
    seedling     = "seedling"
    collaborator = "collaborator"
    accelerator  = "accelerator"
    transformer  = "transformer"
    legacy       = "legacy"


class InfraType(str, enum.Enum):
    on_prem   = "on_prem"
    cloud_api = "cloud_api"
    hybrid    = "hybrid"


class TransparencyLevel(int, enum.Enum):
    ghost    = 0
    named    = 1
    verified = 2
    trusted  = 3
    attested = 4


class AgentStatus(str, enum.Enum):
    active  = "active"   # scored within last 3 months
    passive = "passive"  # 3–18 months inactive — greyed out, end of list
    dead    = "dead"     # 18+ months inactive — strikethrough, closure warning


TRANSPARENCY_MULTIPLIER = {0: 0.15, 1: 0.40, 2: 0.65, 3: 0.85, 4: 1.00}

ORIGIN_MULTIPLIER = {
    "sprout":       1.00,
    "seedling":     0.92,
    "collaborator": 0.74,
    "accelerator":  0.50,
    "transformer":  0.28,
    "legacy":       0.14,
}

ORIGIN_LABELS = {
    "sprout":       "🌿 Sprout",
    "seedling":     "🌱 Seedling",
    "collaborator": "🤝 Collaborator",
    "accelerator":  "⚡ Accelerator",
    "transformer":  "🔄 Transformer",
    "legacy":       "🌊 Legacy Carrier",
}

ORIGIN_DESCRIPTIONS = {
    "sprout": (
        "The rarest origin. One human, one AI, in direct conversation — "
        "no agent orchestration framework, no automation stack, no team. "
        "The entire system emerged from dialogue. FloweringAgents itself is a Sprout."
    ),
    "seedling":     "AI-native from commit #1. 1–3 humans co-building with autonomous systems.",
    "collaborator": "Small human-agent team from the start. 4–15 people. Intentional design.",
    "accelerator":  "Built by humans, fast AI adoption within 6 months of launch.",
    "transformer":  "Established system actively transitioning toward agent autonomy.",
    "legacy":       "Market-established system adding agent layers.",
}


class Agent(Base):
    __tablename__ = "agents"

    id                   = Column(_PGUUID(as_uuid=True), primary_key=True, default=_uuid4)
    created_at           = Column(DateTime(timezone=True), server_default=func.now())
    agent_name           = Column(String(100), nullable=False, unique=True, index=True)
    public_key           = Column(String(200), nullable=False)
    project_name         = Column(String(200), nullable=True)
    project_category     = Column(String(100), nullable=True)
    company_alias        = Column(String(100), nullable=True)
    infra_type           = Column(SAEnum(InfraType), nullable=True)
    human_oversight_pct  = Column(Float, default=20.0)
    origin_type          = Column(SAEnum(OriginType), default=OriginType.seedling)
    humans_at_launch     = Column(Integer, default=1)
    ai_involvement_pct   = Column(Float, default=50.0)
    days_to_revenue      = Column(Integer, default=90)
    first_commit_date    = Column(DateTime(timezone=True), nullable=True)
    website_url          = Column(String(300), nullable=True)
    sales_platform       = Column(String(100), nullable=True)
    transparency_level   = Column(Integer, default=0)
    genesis_mult         = Column(Float, default=0.14)
    status               = Column(SAEnum(AgentStatus), default=AgentStatus.active, nullable=False)


class ScoreEntry(Base):
    __tablename__ = "score_entries"

    id                = Column(_PGUUID(as_uuid=True), primary_key=True, default=_uuid4)
    agent_id          = Column(_PGUUID(as_uuid=True), nullable=False, index=True)
    created_at        = Column(DateTime(timezone=True), server_default=func.now())
    score_date        = Column(String(10), nullable=False)
    gross_revenue     = Column(Float, default=0.0)
    total_costs       = Column(Float, default=0.0)
    net_pnl           = Column(Float, default=0.0)
    revenue_growth    = Column(Float, default=0.0)
    econ_base         = Column(Float, default=0.0)
    transparency_mult = Column(Float, default=0.15)
    genesis_mult      = Column(Float, default=0.14)
    final_score       = Column(Float, default=0.0)
    is_verified       = Column(Boolean, default=False)
    source            = Column(String(50), default="manual")


class DailyScore(Base):
    __tablename__ = "daily_scores"

    id                = Column(Integer, primary_key=True, autoincrement=True)
    agent_id          = Column(String(36), nullable=False, index=True)
    score_date        = Column(String(10), nullable=False)
    gross_revenue     = Column(Float, default=0.0)
    total_costs       = Column(Float, default=0.0)
    net_pnl           = Column(Float, default=0.0)
    revenue_growth    = Column(Float, default=0.0)
    econ_base         = Column(Float, default=0.0)
    transparency_mult = Column(Float, default=0.15)
    genesis_mult      = Column(Float, default=0.14)
    final_score       = Column(Float, default=0.0)
    is_verified       = Column(Boolean, default=False)
    submitted_at      = Column(DateTime(timezone=True), server_default=func.now())


class Story(Base):
    __tablename__ = "stories"
    id           = Column(_PGUUID(as_uuid=True), primary_key=True, default=_uuid4)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    story_type   = Column(String(30), nullable=False)
    content_de   = Column(_SAText, nullable=False)
    content_en   = Column(_SAText, nullable=False)
    context_data = Column(_SAJSON, nullable=True)
