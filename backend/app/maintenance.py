"""
FloweringAgents — Monthly Maintenance Runner
Läuft am 15. jeden Monats via APScheduler (main.py).
Aufgaben:
  1. Wallet-Crawler: ETH/TRX/DOGE on-chain lesen → Donations als Score-Revenue buchen
  2. Scoring-Neuberechnung für alle Agenten
  3. Passive/Dead-Status setzen
  4. Reaktivierung per $5-Donation
"""

import logging
import os
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import AsyncSessionLocal
from .models import Agent, DailyScore, AgentStatus

log = logging.getLogger(__name__)

# ── Wallet addresses ──────────────────────────────────────────────────────────
ETH_WALLET   = "0xc4C41453e200c92CAb6666DbDF0745a58462A41a"
DOGE_WALLET  = "D8EQakmVjAviKDe6UfuygnKGQ4S7619M8G"
TRX_WALLET   = "TSp7gCGqz2EmZfuymzFaQi6GqWTVThqmbb"
DEPLOY_DATE  = datetime(2026, 6, 10, tzinfo=timezone.utc)

# Minimum donation to reactivate a passive agent (USD equivalent)
REACTIVATION_MIN_USD = 5.0

# Inactivity thresholds
PASSIVE_DAYS = 90    # 3 months
DEAD_DAYS    = 548   # 18 months


# ── Price helpers ─────────────────────────────────────────────────────────────

async def _get_prices() -> dict:
    """Fetch live crypto prices from CoinGecko (free tier, no key needed)."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": "ethereum,tron,dogecoin", "vs_currencies": "usd"},
            )
            data = r.json()
            return {
                "eth":  float(data.get("ethereum", {}).get("usd", 3200)),
                "trx":  float(data.get("tron",     {}).get("usd", 0.12)),
                "doge": float(data.get("dogecoin",  {}).get("usd", 0.15)),
            }
    except Exception as e:
        log.warning(f"Price fetch failed: {e} — using fallback prices")
        return {"eth": 3200.0, "trx": 0.12, "doge": 0.15}


# ── Chain crawlers ────────────────────────────────────────────────────────────

async def _eth_received_since(wallet: str, since: datetime) -> float:
    """Sum ETH received at wallet since date using Etherscan API."""
    api_key = os.environ.get("ETHERSCAN_API_KEY", "")
    url = "https://api.etherscan.io/api"
    params = {
        "module":  "account",
        "action":  "txlist",
        "address": wallet,
        "startblock": 0,
        "sort":    "asc",
        "apikey":  api_key or "YourApiKeyToken",
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url, params=params)
            txs = r.json().get("result", [])
        total = 0.0
        since_ts = int(since.timestamp())
        for tx in txs:
            if int(tx.get("timeStamp", 0)) >= since_ts:
                if tx.get("to", "").lower() == wallet.lower():
                    total += int(tx.get("value", 0)) / 1e18
        return total
    except Exception as e:
        log.warning(f"ETH crawl failed: {e}")
        return 0.0


async def _trx_received_since(wallet: str, since: datetime) -> float:
    """Sum TRX received at wallet since date using TronScan API."""
    url = "https://apilist.tronscanapi.com/api/transaction"
    params = {
        "address":   wallet,
        "direction": "receive",
        "limit":     200,
        "start":     0,
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url, params=params)
            data = r.json()
        total = 0.0
        since_ts = int(since.timestamp() * 1000)  # ms
        for tx in data.get("data", []):
            if tx.get("timestamp", 0) >= since_ts:
                total += float(tx.get("amount", 0)) / 1e6
        return total
    except Exception as e:
        log.warning(f"TRX crawl failed: {e}")
        return 0.0


async def _doge_received_since(wallet: str, since: datetime) -> float:
    """Sum DOGE received using Dogechain API."""
    url = f"https://dogechain.info/api/v1/address/transactions/{wallet}"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url)
            txs = r.json().get("transactions", [])
        total = 0.0
        since_ts = int(since.timestamp())
        for tx in txs:
            if tx.get("time", 0) >= since_ts:
                for out in tx.get("outputs", []):
                    if out.get("address") == wallet:
                        total += float(out.get("value", 0))
        return total
    except Exception as e:
        log.warning(f"DOGE crawl failed: {e}")
        return 0.0


# ── Main monthly runner ───────────────────────────────────────────────────────

async def run_monthly_maintenance():
    """
    Called by APScheduler on the 15th of every month at 06:00 Europe/Berlin.
    """
    log.info("=== Monthly maintenance started ===")
    async with AsyncSessionLocal() as db:
        await _crawl_wallets(db)
        await _update_agent_statuses(db)
        await db.commit()
    log.info("=== Monthly maintenance complete ===")


async def _crawl_wallets(db: AsyncSession):
    """Read wallet balances and book new donations as score revenue."""
    prices = await _get_prices()
    # Only count donations since deploy date
    since = DEPLOY_DATE

    log.info(f"Prices: ETH={prices['eth']}, TRX={prices['trx']}, DOGE={prices['doge']}")

    # ETH → Website (Entry #0001)
    eth_amount = await _eth_received_since(ETH_WALLET, since)
    eth_usd    = eth_amount * prices["eth"]
    log.info(f"ETH received: {eth_amount:.6f} ETH = ${eth_usd:.2f}")

    # DOGE → Website (Entry #0001)
    doge_amount = await _doge_received_since(DOGE_WALLET, since)
    doge_usd    = doge_amount * prices["doge"]
    log.info(f"DOGE received: {doge_amount:.2f} DOGE = ${doge_usd:.2f}")

    # TRX → Flower (Entry #0002)
    trx_amount = await _trx_received_since(TRX_WALLET, since)
    trx_usd    = trx_amount * prices["trx"]
    log.info(f"TRX received: {trx_amount:.2f} TRX = ${trx_usd:.2f}")

    # Book as monthly score entries
    # Website agent ID (Entry #0001)
    WEBSITE_AGENT_ID = "a7761e0b-e143-472d-b112-781a1dd4961c"
    # Flower agent ID (Entry #0002)
    FLOWER_AGENT_ID  = os.environ.get("FLOWER_AGENT_ID", "b95ec841-8cec-47ed-8985-a82f97865797")

    total_website_usd = eth_usd + doge_usd
    if total_website_usd > 0:
        from .routers.scores import _calculate_and_store_score
        await _calculate_and_store_score(
            db,
            agent_id=WEBSITE_AGENT_ID,
            gross_revenue=total_website_usd,
            total_costs=5.0,  # monthly server cost
            revenue_growth=0.0,
            score_date=datetime.now(timezone.utc).date(),
            source="wallet_crawler",
        )
        log.info(f"Website donation revenue booked: ${total_website_usd:.2f}")

    if trx_usd > 0:
        await _calculate_and_store_score(
            db,
            agent_id=FLOWER_AGENT_ID,
            gross_revenue=trx_usd,
            total_costs=0.02,
            revenue_growth=0.0,
            score_date=datetime.now(timezone.utc).date(),
            source="wallet_crawler",
        )
        log.info(f"Flower donation revenue booked: ${trx_usd:.2f}")

    # Check for reactivation donations (≥$5 to ETH or DOGE wallet)
    if total_website_usd >= REACTIVATION_MIN_USD:
        await _check_reactivations(db, total_website_usd, prices)


async def _check_reactivations(db: AsyncSession, total_usd: float, prices: dict):
    """Reactivate passive agents if ≥$5 was donated to website wallets."""
    # For now: if any ≥$5 donation came in, reactivate ALL passive agents.
    # Phase 2: match ETH memo field to agent_id for targeted reactivation.
    if total_usd >= REACTIVATION_MIN_USD:
        result = await db.execute(
            select(Agent).where(Agent.status == AgentStatus.passive)
        )
        passive = result.scalars().all()
        for agent in passive:
            agent.status = AgentStatus.active
            log.info(f"Reactivated passive agent: {agent.agent_name} ({agent.agent_id})")


async def _update_agent_statuses(db: AsyncSession):
    """Set Passive/Dead status based on last score submission date."""
    now = datetime.now(timezone.utc)
    passive_cutoff = now - timedelta(days=PASSIVE_DAYS)
    dead_cutoff    = now - timedelta(days=DEAD_DAYS)

    result = await db.execute(select(Agent))
    agents = result.scalars().all()

    for agent in agents:
        # Get last score date
        score_result = await db.execute(
            select(DailyScore)
            .where(DailyScore.agent_id == agent.agent_id)
            .order_by(DailyScore.submitted_at.desc())
            .limit(1)
        )
        last_score = score_result.scalar_one_or_none()
        last_activity = last_score.submitted_at if last_score else agent.created_at

        if last_activity.tzinfo is None:
            last_activity = last_activity.replace(tzinfo=timezone.utc)

        old_status = agent.status
        if last_activity < dead_cutoff:
            if old_status != AgentStatus.dead:
                agent.status = AgentStatus.dead
                log.warning(f"Agent DEAD: {agent.agent_name} — last activity {last_activity.date()}")
        elif last_activity < passive_cutoff:
            if old_status == AgentStatus.active:
                agent.status = AgentStatus.passive
                log.info(f"Agent PASSIVE: {agent.agent_name} — last activity {last_activity.date()}")
        else:
            if old_status in (AgentStatus.passive, AgentStatus.dead):
                agent.status = AgentStatus.active
                log.info(f"Agent REACTIVATED: {agent.agent_name}")
