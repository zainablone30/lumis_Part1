# hardware_bridge/led_controller.py
from mqtt_client import LumisMQTT

EMOTION_COLOR_MAP = {
    "Happiness": "warm_yellow", "Sadness": "soft_blue", "Anger": "deep_red",
    "Fear": "purple", "Surprise": "cyan", "Disgust": "green", "Neutral": "white",
}

class LEDController:
    def __init__(self):
        self.mqtt = LumisMQTT()

    def set_emotion_light(self, emotion: str):
        color = EMOTION_COLOR_MAP.get(emotion, "white")
        self.mqtt.publish("lumis/led", color)

    def set_monitoring_alert_light(self, severity: str):
        color = {"high": "flash_red", "medium": "amber", "low": "white"}.get(severity, "white")
        self.mqtt.publish("lumis/led", color)