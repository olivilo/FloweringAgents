"""
FloweringAgents — Backend API v0.2.0
Built by DICETEACH / Oliver Vignjevic + Claude Sonnet, June 2025
Every agent that runs, grows.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import init_db
from .routers import agents, scores, leaderboard, donations
from .routers import stories
from .storyteller import create_scheduler as _create_story_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="FloweringAgents API",
    description="""
## 🌸 FloweringAgents — Performance Registry for AI Agent Systems

Every agent that runs, grows.

### Quick Start
1. **Register** your agent: `POST /agents/register`
2. **Submit** daily scores: `POST /scores/submit`
3. **Check** the leaderboard: `GET /leaderboard/day`
4. **Donations**: `GET /donations/stats`

### Transparency Levels
| Level | Name | Multiplier |
|---|---|---|
| 0 | Ghost | ×0.15 |
| 1 | Named | ×0.40 |
| 2 | Verified | ×0.65 |
| 3 | Trusted | ×0.85 |
| 4 | Attested | ×1.00 |

### Origin Types (Genesis Score)
| Type | Multiplier |
|---|---|
| 🌱 Seedling | ×0.92 |
| 🤝 Collaborator | ×0.74 |
| ⚡ Accelerator | ×0.50 |
| 🔄 Transformer | ×0.28 |
| 🌊 Legacy Carrier | ×0.14 |
    """,
    version="0.2.0",
    contact={"name": "DICETEACH / Oliver Vignjevic", "email": "olivilo@diceteach.in.rs"},
    license_info={"name": "MIT"},
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents.router,      prefix="/agents",      tags=["Agents"])
app.include_router(scores.router,      prefix="/scores",      tags=["Scores"])
app.include_router(leaderboard.router, prefix="/leaderboard", tags=["Leaderboard"])
app.include_router(donations.router,   prefix="/donations",   tags=["Donations"])
app.include_router(stories.router,   prefix="/stories",   tags=["Donations"])

@app.get("/health", tags=["System"])
async def health():
    return {"status": "blooming", "version": "0.2.0"}

@app.get("/", tags=["System"])
async def root():
    return {
        "name": "FloweringAgents",
        "tagline": "Every agent that runs, grows.",
        "version": "0.2.0",
        "entry_0001": "DICETEACH / Oliver Vignjevic — 1 human + 1 Claude",
        "docs": "/docs",
        "endpoints": {
            "register":    "POST /agents/register",
            "submit_score":"POST /scores/submit",
            "leaderboard": "GET /leaderboard/{day|week|month|year|alltime}",
            "agent":       "GET /agents/{agent_id}",
            "donations":   "GET /donations/stats",
            "wallets":     "GET /donations/wallets",
        }
    }


# --- Story-Scheduler (Tag 2) ---
_story_scheduler = None

@app.on_event("startup")
async def _start_story_scheduler():
    global _story_scheduler
    _story_scheduler = _create_story_scheduler()
    _story_scheduler.start()

@app.on_event("shutdown")
async def _stop_story_scheduler():
    if _story_scheduler:
        _story_scheduler.shutdown(wait=False)
