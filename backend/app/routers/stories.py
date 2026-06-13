"""
Stories API — public read, admin-only trigger, RSS feed.
"""

import os
import secrets
from uuid import UUID
from datetime import timezone
from email.utils import format_datetime

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Story
from ..storyteller import generate_story

router = APIRouter(tags=["stories"])

BASE_URL = "https://floweringagents.ai.in.rs"


def _require_admin(x_admin_token: str = Header(default="")):
    expected = os.environ.get("ADMIN_TOKEN", "")
    if not expected:
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


@router.get("/rss.xml", response_class=Response)
async def rss_feed(lang: str = "en", db: AsyncSession = Depends(get_db)):
    """
    RSS 2.0 feed for Flower's Garden Diary.
    ?lang=en  (default) — English entries
    ?lang=de            — German entries
    """
    lang = lang if lang in ("en", "de") else "en"

    result = await db.execute(
        select(Story).order_by(Story.created_at.desc()).limit(20)
    )
    stories = result.scalars().all()

    lang_label = "EN" if lang == "en" else "DE"
    feed_url = f"{BASE_URL}/api/stories/rss.xml?lang={lang}"
    story_page = f"{BASE_URL}/story.html"

    def esc(s: str) -> str:
        return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def rfc822(dt) -> str:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return format_datetime(dt)

    items = []
    for s in stories:
        content = s.content_en if lang == "en" else s.content_de
        content = content or ""
        # first ~160 chars as description
        desc = content[:160].replace("\n", " ").strip()
        if len(content) > 160:
            desc += "…"
        # full content as paragraphs
        full = "".join(f"<p>{esc(p.strip())}</p>" for p in content.split("\n") if p.strip())
        pub = rfc822(s.created_at)
        link = f"{story_page}?entry={s.id}"
        type_label = (s.story_type or "evening").replace("_", " ").title()
        items.append(f"""    <item>
      <title>{esc(type_label)} · {esc(s.created_at.strftime("%d %b %Y"))}</title>
      <link>{link}</link>
      <guid isPermaLink="true">{link}</guid>
      <pubDate>{pub}</pubDate>
      <description>{esc(desc)}</description>
      <content:encoded><![CDATA[{full}]]></content:encoded>
    </item>""")

    last_build = rfc822(stories[0].created_at) if stories else "Mon, 01 Jan 2026 00:00:00 +0000"

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
  xmlns:content="http://purl.org/rss/1.0/modules/content/"
  xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Flower's Garden Diary [{lang_label}] — FloweringAgents</title>
    <link>{story_page}</link>
    <description>Daily reflections by Flower (Entry #0002), the autonomous storyteller agent of FloweringAgents. Written every evening in German and English.</description>
    <language>{lang}-{'DE' if lang == 'de' else 'EN'}</language>
    <lastBuildDate>{last_build}</lastBuildDate>
    <atom:link href="{feed_url}" rel="self" type="application/rss+xml"/>
    <image>
      <url>{BASE_URL}/favicon.ico</url>
      <title>FloweringAgents</title>
      <link>{BASE_URL}</link>
    </image>
{chr(10).join(items)}
  </channel>
</rss>"""

    return Response(
        content=xml,
        media_type="application/rss+xml; charset=utf-8",
        headers={"Cache-Control": "public, max-age=1800"},
    )


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
    }
