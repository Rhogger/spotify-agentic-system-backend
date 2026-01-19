from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {
        "status": "Online",
        "projeto": "Spotify Agentic System",
        "database_url": os.getenv("DATABASE_URL")
    }