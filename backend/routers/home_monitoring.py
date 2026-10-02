# backend/routers/home_monitoring.py
from fastapi import APIRouter
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../home_monitoring"))
from monitoring_service import HomeMonitoringService
from backend.schemas import ConsentRequest

router = APIRouter(prefix="/monitoring", tags=["Home Monitoring"])
monitoring_service = HomeMonitoringService()


@router.post("/consent")
def set_consent(req: ConsentRequest):
    monitoring_service.set_consent(req.consent)
    return {"monitoring_active": monitoring_service.consented}


@router.get("/status")
def get_status():
    return monitoring_service.get_status()


@router.get("/alerts")
def get_alerts():
    return monitoring_service.get_alert_history()