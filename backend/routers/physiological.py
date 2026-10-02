from fastapi import APIRouter
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../physiological_sensing"))
from sensing_service import PhysiologicalSensingService

router = APIRouter(prefix="/physiological", tags=["Physiological Sensing"])
sensing_service = PhysiologicalSensingService()
sensing_service.start_background_gsr_polling()


@router.get("/status")
def get_status():
    return sensing_service.get_latest()