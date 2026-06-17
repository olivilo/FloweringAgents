"""
FloweringAgents — Favicon proxy with local caching

Statt das Frontend live & direkt von Google's Favicon-API laden zu lassen
(fragil: Rate-Limits, Ausfälle, Abhängigkeit von Drittanbieter bei jedem
Seitenaufruf), lädt das Backend Favicons EINMAL pro Domain herunter, cached
sie lokal auf Disk und liefert sie über einen eigenen Endpoint aus.

GET /favicons/{domain}.png
  → 1. Wenn lokal gecached (jünger als 30 Tage): direkt ausliefern
    2. Sonst: von Google's Favicon-Service holen, cachen, ausliefern
    3. Wenn das fehlschlägt: 404 (Frontend zeigt dann Initialen-Fallback)
"""
from fastapi import APIRouter, HTTPException, Response
from pathlib import Path
import httpx
import re
import time

router = APIRouter()

CACHE_DIR = Path("/app/favicon_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_MAX_AGE_SECONDS = 30 * 24 * 3600  # 30 days

_DOMAIN_RE = re.compile(r"^[a-zA-Z0-9.-]{1,253}$")


def _safe_filename(domain: str) -> str:
    """Sanitize domain to a safe cache filename."""
    domain = domain.lower().strip()
    if not _DOMAIN_RE.match(domain):
        raise HTTPException(status_code=400, detail="Invalid domain format")
    return domain.replace("/", "_") + ".png"


@router.get("/{domain}.png")
async def get_favicon(domain: str):
    filename = _safe_filename(domain)
    cache_path = CACHE_DIR / filename

    # Serve from cache if fresh
    if cache_path.exists():
        age = time.time() - cache_path.stat().st_mtime
        if age < CACHE_MAX_AGE_SECONDS:
            return Response(
                content=cache_path.read_bytes(),
                media_type="image/png",
                headers={"Cache-Control": "public, max-age=604800"},  # 7 days browser cache
            )

    # Fetch fresh from Google's favicon service
    try:
        async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
            resp = await client.get(
                "https://www.google.com/s2/favicons",
                params={"domain": domain, "sz": "64"},
            )
            resp.raise_for_status()
            content = resp.content
            # Guard against non-image responses (e.g. an HTML error page
            # that slipped through with a 200 status)
            content_type = resp.headers.get("content-type", "")
            if not content_type.startswith("image/") or len(content) < 50:
                raise ValueError(f"Unexpected favicon response: {content_type}, {len(content)} bytes")
    except Exception:
        # Stale cache is better than nothing
        if cache_path.exists():
            return Response(
                content=cache_path.read_bytes(),
                media_type="image/png",
                headers={"Cache-Control": "public, max-age=604800"},
            )
        # Explicit no-store so Cloudflare/browsers never cache a transient
        # failure (e.g. Google rate-limiting) as if it were permanent.
        return Response(
            content=b"",
            status_code=404,
            headers={"Cache-Control": "no-store"},
        )

    # Save to cache
    try:
        cache_path.write_bytes(content)
    except Exception:
        pass  # caching failure shouldn't break the response

    return Response(
        content=content,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=604800"},
    )
