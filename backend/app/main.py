"""
FloweringAgents — Backend API v0.3.0
Built by DICETEACH / Oliver Vignjevic + Claude Sonnet, June 2026
Every agent that runs, grows.
"""
from fastapi import BackgroundTasks, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import init_db
from .routers import agents, scores, leaderboard, donations, favicons
from .routers import stories
from .routers.stories import _require_admin
from .storyteller import create_scheduler as _create_story_scheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

_BERLIN = pytz.timezone("Europe/Berlin")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    # Story scheduler (daily 21:00, Sun 08:00)
    global _story_scheduler
    _story_scheduler = _create_story_scheduler()
    _story_scheduler.start()

    # Monthly maintenance scheduler (15th of month, 06:00 Berlin)
    global _maintenance_scheduler
    _maintenance_scheduler = AsyncIOScheduler(timezone=_BERLIN)
    _maintenance_scheduler.add_job(
        _run_maintenance,
        CronTrigger(day=15, hour=6, minute=0, timezone=_BERLIN),
        id="monthly_maintenance",
        replace_existing=True,
        misfire_grace_time=3600 * 23,
    )
    _maintenance_scheduler.start()

    yield

    if _story_scheduler:
        _story_scheduler.shutdown(wait=False)
    if _maintenance_scheduler:
        _maintenance_scheduler.shutdown(wait=False)


async def _run_maintenance():
    from .maintenance import run_monthly_maintenance
    await run_monthly_maintenance()


app = FastAPI(
    title="FloweringAgents API",
    description="""
## 🌸 FloweringAgents — Performance Registry for AI Agent Systems

Every agent that runs, grows.

### Quick Start
1. **Register** your agent: `POST /agents/register`
2. **Submit** daily scores: `POST /scores/submit`
3. **Check** the leaderboard: `GET /leaderboard/day`
4. **Read stories**: `GET /stories/`
5. **RSS Feed**: `GET /stories/rss.xml?lang=en`

### Transparency Levels
| Level | Name | Multiplier |
|---|---|---|
| 0 | Ghost | ×0.15 |
| 1 | Named | ×0.40 |
| 2 | Verified | ×0.65 |
| 3 | Trusted | ×0.85 |
| 4 | Attested | ×1.00 |

### Agent Lifecycle
| Status | Condition |
|---|---|
| Active | Scored within last 3 months |
| Passive | 3–18 months inactive — greyed out |
| Dead | 18+ months inactive — closure warning |

Reactivation from Passive: submit a new score OR donate ≥$5 to ETH/DOGE website wallet.
    """,
    version="0.3.0",
    contact={"name": "DICETEACH / Oliver Vignjevic", "email": "admin@ai.in.rs"},
    license_info={"name": "MIT"},
    lifespan=lifespan,
    redirect_slashes=False,
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
app.include_router(stories.router,     prefix="/stories",     tags=["Stories"])
app.include_router(favicons.router,     prefix="/favicons",    tags=["Favicons"])


@app.get("/health", tags=["System"])
async def health():
    return {"status": "blooming", "version": "0.3.0"}


@app.post("/maintenance/trigger", tags=["System"], dependencies=[Depends(_require_admin)])
async def trigger_maintenance(background_tasks: BackgroundTasks):
    """Manually run the monthly maintenance (wallet crawler, scoring, lifecycle status).
    Useful if a redeploy after 06:00 on the 15th caused the scheduled run to be skipped."""
    background_tasks.add_task(_run_maintenance)
    return {
        "message": "Maintenance run started in background",
        "hint": "Check /api/donations/stats and /api/leaderboard/month afterwards",
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "name": "FloweringAgents",
        "tagline": "Every agent that runs, grows.",
        "version": "0.3.0",
        "entry_0001": "DICETEACH / Oliver Vignjevic — 1 human + 1 Claude",
        "docs": "/docs",
        "endpoints": {
            "register":     "POST /agents/register",
            "submit_score": "POST /scores/submit",
            "leaderboard":  "GET /leaderboard/{day|week|month|year|alltime}",
            "agent":        "GET /agents/{agent_id}",
            "donations":    "GET /donations/stats",
            "stories":      "GET /stories/",
            "rss_en":       "GET /stories/rss.xml?lang=en",
            "rss_de":       "GET /stories/rss.xml?lang=de",
        },
        "maintenance": {
            "schedule": "15th of every month at 06:00 Europe/Berlin",
            "tasks": ["wallet_crawler", "passive_dead_status", "score_recalculation"],
        },
    }


_story_scheduler = None
_maintenance_scheduler = None
