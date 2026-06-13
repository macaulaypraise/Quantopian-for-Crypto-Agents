from fastapi import FastAPI

app = FastAPI(
    title="NCAE Strategy Skill API",
    description="Track 2 MCP Server: Quantopian for Crypto Agents",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    return {"status": "online", "mode": "Track 2 (Stateless)"}

# To run the server during development:
# uv run uvicorn app.main:app --reload
