"""
Stories API — public read, admin-only trigger.

SECURITY:
- GET endpoints are public (stories are public content)
- POST /trigger requires X-Admin-Token header matching ADMIN_TOKEN env var.
  Comparison uses secrets.compare_digest (timing-attack safe).
  Without ADMIN_TOKEN configured, trigger is disabled entirely (fail closed).
"""

import os
import secrets
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Story
from ..storyteller import generate_story

router = APIRouter(tags=["stories"])


def _require_admin(x_admin_token: str = Header(default="")):
    expected = os.environ.get("ADMIN_TOKEN", "")
    if not expected:
        # Fail closed: no token configured -> endpoint disabled
        raise HTTPException(503, "Trigger endpoint not configured")
    if not secrets.compare_digest(x_admin_token, expected):
        raise HTTPException(403, "Forbidden")


@router.get("/latest")
async def get_latest_story(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Story).order_by(Story.created_at.desc()).limit(1)
    )
    story = result.scalar_one_or_none()
    if not story:
        return {"story": None, "message": "No stories yet. The first will be written tonight."}
    return _fmt(story)


@router.get("/")
async def list_stories(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    limit = max(1, min(limit, 50))
    offset = max(0, offset)
    result = await db.execute(
        select(Story).order_by(Story.created_at.desc()).limit(limit).offset(offset)
    )
    return [_fmt(s) for s in result.scalars().all()]


@router.get("/{story_id}")
async def get_story(story_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Story).where(Story.id == story_id))
    story = result.scalar_one_or_none()
    if not story:
        raise HTTPException(404, "Story not found")
    return _fmt(story)


async def _generate_in_background(story_type: str):
    from ..database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        try:
            await generate_story(db, story_type)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(
                f"Background story failed ({story_type}): {type(e).__name__}")


@router.post("/trigger", dependencies=[Depends(_require_admin)])
async def trigger_story(
    background_tasks: BackgroundTasks,
    story_type: str = "evening",
):
    if story_type not in ("evening", "sunday_morning", "sunday_evening"):
        raise HTTPException(400, "story_type must be evening, sunday_morning, or sunday_evening")
    background_tasks.add_task(_generate_in_background, story_type)
    return {
        "message": "Story generation started in background",
        "hint": "Check /api/stories/latest in a few minutes",
    }


def _fmt(s: Story) -> dict:
    return {
        "id": str(s.id),
        "story_type": s.story_type,
        "created_at": s.created_at.isoformat(),
        "content_de": s.content_de,
        "content_en": s.content_en,
        # context_data intentionally NOT exposed — internal only
    }
