from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import (
    companion, communication_practice, home_monitoring,
    multilingual_chat, physiological, therapist, avatar
)
from backend.db.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="LUMIS Backend", version="2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(companion.router)
app.include_router(communication_practice.router)
app.include_router(home_monitoring.router)
app.include_router(multilingual_chat.router)
app.include_router(physiological.router)
app.include_router(therapist.router)
app.include_router(avatar.router)


@app.get("/")
def root():
    return {"status": "LUMIS backend v2 running", "modules": [
        "companion", "communication_practice", "home_monitoring",
        "multilingual_chat", "physiological_sensing", "therapist_dashboard", "avatar_3d"
    ]}