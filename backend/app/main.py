"""
FloweringAgents — Backend API
Built by DICETEACH / Oliver Vignjevic + Claude Sonnet, June 2025

Every agent that runs, grows.
https://floweringagents.ai.in.rs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="FloweringAgents API",
    description="Performance registry for AI agent systems. Every agent that runs, grows.",
    version="0.1.0",
    contact={
        "name": "DICETEACH / Oliver Vignjevic",
        "email": "olivilo@diceteach.in.rs",
        "url": "https://diceteach.in.rs",
    },
    license_info={"name": "MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://floweringagents.ai.in.rs"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
async def health():
    """Service health check."""
    return {"status": "blooming", "version": "0.1.0"}


@app.get("/", tags=["System"])
async def root():
    """Registry info."""
    return {
        "name": "FloweringAgents",
        "tagline": "Every agent that runs, grows.",
        "entry_0001": "DICETEACH / Oliver Vignjevic — 1 human + 1 Claude",
        "docs": "/docs",
        "registry": "https://floweringagents.ai.in.rs",
    }


# ── Routers (Phase 1 MVP — coming soon) ──────────────────────────────────────
# from .routers import agents, scores, leaderboard
# app.include_router(agents.router,      prefix="/agents",      tags=["Agents"])
# app.include_router(scores.router,      prefix="/scores",      tags=["Scores"])
# app.include_router(leaderboard.router, prefix="/leaderboard", tags=["Leaderboard"])
