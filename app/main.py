# app/main.py
from fastapi import FastAPI
from app.models.base import Base
from app.models.user import User
from app.models.playlist import Playlist
from app.models.track import Track
from app.core.database import engine

app = FastAPI(
    title="Spotify Agentic System",
    description="Backend para orquestração de agentes e integração com Spotify",
    version="0.1.0"
)

# Criar tabelas ao iniciar a aplicação
Base.metadata.create_all(bind=engine)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)