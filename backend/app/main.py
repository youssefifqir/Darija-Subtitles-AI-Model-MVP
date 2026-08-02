from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import jobs

app = FastAPI(title="Darija Subtitles — Demo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # demo only — lock this down before any real deployment
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
