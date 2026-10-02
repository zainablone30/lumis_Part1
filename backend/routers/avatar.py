from fastapi import APIRouter

router = APIRouter(prefix="/avatar", tags=["3D Avatar"])

@router.get("/info")
def avatar_info():
    return {
        "websocket_url": "ws://localhost:8100/ws/avatar",
        "viewer_url": "http://localhost:8100/static/index.html",
        "hologram_pyramid_supported": True,
    }