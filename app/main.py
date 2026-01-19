# app/main.py
from fastapi import FastAPI

app = FastAPI(
    title="Spotify Agentic System",
    description="Backend para orquestração de agentes e integração com Spotify",
    version="0.1.0"
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)