from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="NCAE Strategy Skill API",
    description="Track 2 MCP Server: Quantopian for Crypto Agents",
    version="1.0.0"
)

# Mount the API routes
app.include_router(router)

@app.get("/health")
async def health_check():
    return {"status": "online", "mode": "Track 2 (Stateless)"}

# To run the server during development:
# uv run uvicorn app.main:app --reload
