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
    sprout       = "sprout"       # 🌿 NEW: 1 human + 1 AI, no agent orchestration
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


TRANSPARENCY_MULTIPLIER = {0: 0.15, 1: 0.40, 2: 0.65, 3: 0.85, 4: 1.00}

ORIGIN_MULTIPLIER = {
    "sprout":       1.00,  # Maximum — 1 human + 1 AI, pure conversation, no tooling
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
    "seedling": (
        "Born AI-native from day one. 1–3 humans co-building with autonomous systems. "
        "First revenue fast, no legacy."
    ),
    "collaborator": "Small human-agent team from start. 4–15 people. Intentional design.",
    "accelerator":  "Human-built, fast AI adoption within 6 months of launch.",
    "transformer":  "Established system actively transitioning toward agent autonomy.",
    "legacy":       "Market-established system, scale and depth — adding agent layers.",
}


class Agent(Base):
    __tablename__ = "agents"

    agent_id            = Column(String(36), primary_key=True)
    agent_name          = Column(String(100), nullable=False, unique=True)
    public_key          = Column(Text, nullable=False)
    project_name        = Column(String(200), nullable=False)
    project_category    = Column(String(100))
    company_alias       = Column(String(200))
    infra_type          = Column(SAEnum(InfraType), default=InfraType.cloud_api)
    human_oversight_pct = Column(Float, default=50.0)
    origin_type         = Column(SAEnum(OriginType), default=OriginType.collaborator)
    # Build origin — locked at registration
    humans_at_launch    = Column(Integer, default=1)
    ai_involvement_pct  = Column(Float, default=50.0)
    days_to_revenue     = Column(Integer, default=90)
    first_commit_date   = Column(String(20))
    # Transparency
    transparency_level  = Column(Integer, default=0)
    has_logo            = Column(Boolean, default=False)
    has_domain          = Column(Boolean, default=False)
    operator_public     = Column(Boolean, default=False)
    sales_platform      = Column(String(200))
    website_url         = Column(String(300))
    # Longevity (grows over time)
    longevity_score     = Column(Float, default=0.0)
    months_active       = Column(Integer, default=0)
    # Meta
    created_at          = Column(DateTime(timezone=True), server_default=func.now())
    is_active           = Column(Boolean, default=True)


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


# --- Storyteller (Tag 2) ---

class Story(Base):
    __tablename__ = "stories"
    id           = Column(_PGUUID(as_uuid=True), primary_key=True, default=_uuid4)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    story_type   = Column(String(30), nullable=False)
    content_de   = Column(_SAText, nullable=False)
    content_en   = Column(_SAText, nullable=False)
    context_data = Column(_SAJSON, nullable=True)
