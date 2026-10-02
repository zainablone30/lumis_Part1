from fastapi import APIRouter
from pydantic import BaseModel
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../therapist_dashboard"))
from consent_linking import ConsentLinker
from aggregation_service import AggregationService

router = APIRouter(prefix="/therapist", tags=["Therapist Dashboard"])
linker = ConsentLinker()
agg = AggregationService()


class ConsentGrant(BaseModel):
    client_user_id: str
    professional_id: int


@router.post("/consent/grant")
def grant(req: ConsentGrant):
    linker.grant_consent(req.client_user_id, req.professional_id)
    return {"status": "consent granted"}


@router.post("/consent/revoke")
def revoke(req: ConsentGrant):
    linker.revoke_consent(req.client_user_id, req.professional_id)
    return {"status": "consent revoked"}


@router.get("/clients/{professional_id}")
def list_clients(professional_id: int):
    return linker.get_consented_clients(professional_id)


@router.get("/progress/{client_id}/{professional_id}")
def progress(client_id: str, professional_id: int):
    if not linker.has_consent(client_id, professional_id):
        return {"error": "No active consent for this client."}
    return {
        "emotion_trend": agg.emotion_trend(client_id),
        "communication_progress": agg.communication_progress(client_id),
        "physiological_trend": agg.physiological_trend(client_id),
        "alert_summary": agg.alert_summary(client_id),
    }