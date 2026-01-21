import asyncio
import httpx
import time
from fastapi import FastAPI, Header, HTTPException
from contextlib import asynccontextmanager
from .database import init_db
import aiosqlite

# External simulation URLs
INTEGRATIONS = [f"https://httpbin.org/delay/1" for _ in range(5)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs on startup
    await init_db() 
    limits = httpx.Limits(max_connections=1000, max_keepalive_connections=500)
    app.state.client = httpx.AsyncClient(limits=limits, timeout=3.0)
    yield
    # Runs on shutdown
    await app.state.client.aclose()

app = FastAPI(lifespan=lifespan)

@app.post("/agent/call")
async def handle_call(x_api_key: str = Header(None)):
    async with aiosqlite.connect("probound.db") as db:
        async with db.execute("SELECT username FROM users WHERE api_key = ?", (x_api_key,)) as cursor:
            user = await cursor.fetchone()
        
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    client = app.state.client
    tasks = [client.get(url) for url in INTEGRATIONS]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    valid_responses = [r for r in results if isinstance(r, httpx.Response)]
    
    return {
    "status": "success" if len(valid_responses) == len(INTEGRATIONS) else "partial",
    "successful_integrations": len(valid_responses),
    "latency_safety_triggered": len(valid_responses) < len(INTEGRATIONS)
}