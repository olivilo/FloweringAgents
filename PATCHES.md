# PATCHES — Tag 2: Storyteller (DeepSeek) + i18n
# Änderungen an BESTEHENDEN Dateien. Neue Dateien einfach an die Pfade kopieren.

# ═══════════════════════════════════════════════════════════════════
# PATCH 1: backend/app/models.py — Story-Klasse am Ende anhängen
# (Imports prüfen: Text und JSON müssen aus sqlalchemy importiert sein)
# ═══════════════════════════════════════════════════════════════════

class Story(Base):
    __tablename__ = "stories"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    story_type   = Column(String(30), nullable=False)   # evening | sunday_morning | sunday_evening
    content_de   = Column(Text, nullable=False)
    content_en   = Column(Text, nullable=False)
    context_data = Column(JSON, nullable=True)

# ═══════════════════════════════════════════════════════════════════
# PATCH 2: backend/app/main.py
# ═══════════════════════════════════════════════════════════════════

# Imports oben ergänzen:
from .routers import stories as stories_router
from .storyteller import create_scheduler

# Startup/Shutdown ergänzen bzw. erweitern:
_scheduler = None

@app.on_event("startup")
async def startup():
    await init_db()
    global _scheduler
    _scheduler = create_scheduler()
    _scheduler.start()

@app.on_event("shutdown")
async def shutdown():
    if _scheduler:
        _scheduler.shutdown(wait=False)

# Router einbinden (bei den anderen include_router-Zeilen):
app.include_router(stories_router.router, prefix="/api")

# ═══════════════════════════════════════════════════════════════════
# PATCH 3: backend/requirements.txt — 2 Zeilen hinzufügen
# (httpx ist seit den Donations bereits drin!)
# ═══════════════════════════════════════════════════════════════════

apscheduler>=3.10.0
pytz>=2024.1

# ═══════════════════════════════════════════════════════════════════
# PATCH 4: infra/docker-compose.yml — beim backend-Service unter environment:
# ═══════════════════════════════════════════════════════════════════

      DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY}
      ADMIN_TOKEN: ${ADMIN_TOKEN}

# ═══════════════════════════════════════════════════════════════════
# PATCH 5: infra/.env — NUR AUF DER VM, NIEMALS IN GIT!
# ═══════════════════════════════════════════════════════════════════

DEEPSEEK_API_KEY=sk-DEIN_DEEPSEEK_KEY
# ADMIN_TOKEN generieren mit: openssl rand -hex 32
ADMIN_TOKEN=HIER_DAS_GENERIERTE_TOKEN

# Danach: chmod 600 ~/FloweringAgents/infra/.env

# ═══════════════════════════════════════════════════════════════════
# PATCH 6: infra/nginx.conf — im server-Block ergänzen
# ═══════════════════════════════════════════════════════════════════

    location = /story {
        return 301 /story.html;
    }
    location /js/ {
        root /var/www/floweringagents;
    }
    location /i18n/ {
        root /var/www/floweringagents;
    }
