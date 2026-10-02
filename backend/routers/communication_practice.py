# backend/schemas.py
from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    user_id: str
    user_name: str
    message: str
    detected_emotion: Optional[str] = "Neutral"


class ChatResponse(BaseModel):
    reply: str
    crisis_flag: bool
    detected_emotion: str


class ScenarioStartRequest(BaseModel):
    user_id: str
    scenario_key: str


class ScenarioTurnRequest(BaseModel):
    session_id: str
    user_text: str


class ConsentRequest(BaseModel):
    user_id: str
    consent: bool