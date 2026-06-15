"""
FloweringAgents — Donations blockchain reader
Reads ETH / TRX / DOGE wallet balances once daily
Caches in Redis — no API keys needed for basic balance checks
"""
from fastapi import APIRouter, Depends
import redis.asyncio as aioredis
import httpx
import os
import json
from datetime import datetime, date

router = APIRouter()
REDIS_URL   = os.getenv("REDIS_URL", "redis://localhost:6379")
ETH_WALLET  = "0xc4C41453e200c92CAb6666DbDF0745a58462A41a"
TRX_WALLET  = "TSp7gCGqz2EmZfuymzFaQi6GqWTVThqmbb"
DOGE_WALLET = "D8EQakmVjAviKDe6UfuygnKGQ4S7619M8G"
CACHE_KEY   = "donations:stats"
CACHE_TTL   = 86400  # 24 hours

async def get_redis():
    r = aioredis.from_url(REDIS_URL, decode_responses=True)
    try:
        yield r
    finally:
        await r.aclose()

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
    except Exception:
        return {"eth": 3200.0, "trx": 0.12, "doge": 0.15}


async def fetch_eth_data(eth_price: float):
    """Balance + recent incoming transfers via Ethplorer (Etherscan V1 is deprecated)."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                f"https://api.ethplorer.io/getAddressInfo/{ETH_WALLET}",
                params={"apiKey": "freekey"},
            )
            balance_eth = float(r.json().get("ETH", {}).get("balance", 0))

            r2 = await client.get(
                f"https://api.ethplorer.io/getAddressTransactions/{ETH_WALLET}",
                params={"apiKey": "freekey", "limit": 20},
            )
            txs = r2.json()
            if not isinstance(txs, list):
                txs = []
            donors = []
            for tx in txs:
                if tx.get("to", "").lower() != ETH_WALLET.lower():
                    continue
                val_eth = float(tx.get("value", 0))
                if val_eth <= 0:
                    continue
                from_addr = tx.get("from", "")
                display = f"0x{from_addr[2:8]}...{from_addr[-4:]}" if len(from_addr) > 10 else "anonymous"
                donors.append({
                    "chain": "ETH",
                    "display_name": display,
                    "amount_display": f"{val_eth:.4f} ETH",
                    "amount_usd_est": val_eth * eth_price,
                    "memo": None,
                    "ts": int(tx.get("timestamp", 0))
                })
            return balance_eth, donors
    except Exception:
        return 0.0, []

async def fetch_trx_data():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"https://apilist.tronscan.org/api/account?address={TRX_WALLET}")
            balance_trx = r.json().get("balance", 0) / 1e6
            return balance_trx, []
    except Exception:
        return 0.0, []

async def fetch_doge_data():
    """Balance via BlockCypher (dogechain.info is behind a Cloudflare bot challenge)."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"https://api.blockcypher.com/v1/doge/main/addrs/{DOGE_WALLET}/balance")
            return r.json().get("balance", 0) / 1e8, []
    except Exception:
        return 0.0, []

async def refresh_donation_stats(redis) -> dict:
    prices = await _get_prices()
    eth_bal, eth_donors = await fetch_eth_data(prices["eth"])
    trx_bal, _          = await fetch_trx_data()
    doge_bal, _         = await fetch_doge_data()
    total_usd = (eth_bal * prices["eth"]) + (trx_bal * prices["trx"]) + (doge_bal * prices["doge"])
    all_donors = sorted(eth_donors, key=lambda x: x.get("ts", 0), reverse=True)
    last_ago = "none yet"
    if all_donors and all_donors[0].get("ts", 0) > 0:
        diff = int(datetime.now().timestamp()) - all_donors[0]["ts"]
        if diff < 3600:
            last_ago = f"{diff//60}m ago"
        elif diff < 86400:
            last_ago = f"{diff//3600}h ago"
        else:
            last_ago = f"{diff//86400}d ago"
    stats = {
        "eth_balance":       round(eth_bal, 6),
        "trx_balance":       round(trx_bal, 2),
        "doge_balance":      round(doge_bal, 2),
        "total_usd_est":     round(total_usd, 2),
        "unique_donors":     len(set(d["display_name"] for d in all_donors)),
        "last_donation_ago": last_ago,
        "recent_donors":     all_donors[:15],
        "updated_at":        date.today().isoformat(),
        "wallets": {"eth": ETH_WALLET, "trx": TRX_WALLET, "doge": DOGE_WALLET},
    }
    await redis.set(CACHE_KEY, json.dumps(stats), ex=CACHE_TTL)
    return stats

@router.get("/stats")
async def get_donation_stats(redis = Depends(get_redis)):
    cached = await redis.get(CACHE_KEY)
    if cached:
        return json.loads(cached)
    return await refresh_donation_stats(redis)

@router.post("/refresh")
async def force_refresh(redis = Depends(get_redis)):
    stats = await refresh_donation_stats(redis)
    return {"status": "refreshed", "updated_at": stats["updated_at"]}

@router.get("/wallets")
async def get_wallets():
    return {
        "ethereum": {"address": ETH_WALLET, "explorer": f"https://etherscan.io/address/{ETH_WALLET}"},
        "tron":     {"address": TRX_WALLET, "explorer": f"https://tronscan.org/#/address/{TRX_WALLET}"},
        "dogecoin": {"address": DOGE_WALLET, "explorer": f"https://dogechain.info/address/{DOGE_WALLET}"},
        "note":     "All donations publicly verifiable on-chain. Data refreshes daily.",
    }
