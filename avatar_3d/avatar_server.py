"""
WebSocket server that streams avatar animation frames (lip-sync + emotion
blendshapes) to the browser-based 3D/hologram renderer in real time, synced
to TTS audio playback on the device.
"""
import asyncio
import json
import time
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles

from viseme_mapper import VisemeMapper
from expression_controller import ExpressionController

app = FastAPI(title="LUMIS Avatar Server")
app.mount("/static", StaticFiles(directory="web"), name="static")

viseme_mapper = VisemeMapper(fps=30)
expression_controller = ExpressionController()

connected_clients = set()


@app.websocket("/ws/avatar")
async def avatar_ws(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # keep-alive / client pings
    except Exception:
        pass
    finally:
        connected_clients.discard(websocket)


async def broadcast(frame: dict):
    dead = []
    for ws in connected_clients:
        try:
            await ws.send_text(json.dumps(frame))
        except Exception:
            dead.append(ws)
    for d in dead:
        connected_clients.discard(d)


async def play_avatar_response(audio_path: str, emotion: str, hologram_mode: bool = True):
    """
    Called right after TTS generates a response. Streams lip-sync frames
    timed to real playback so the avatar on screen / hologram stays in sync.
    """
    emotion_shapes = expression_controller.get_blendshapes(emotion)
    lipsync_frames = viseme_mapper.from_audio_envelope(audio_path)

    start_time = time.time()
    for frame in lipsync_frames:
        target_time = start_time + frame["time"]
        now = time.time()
        if target_time > now:
            await asyncio.sleep(target_time - now)

        merged = expression_controller.blend_with_lipsync(emotion_shapes, frame)
        await broadcast({"type": "animation_frame", "blendshapes": merged,
                          "hologram_mode": hologram_mode})

    await broadcast({"type": "animation_end"})