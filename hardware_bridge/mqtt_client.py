# hardware_bridge/mqtt_client.py
import paho.mqtt.client as mqtt

class LumisMQTT:
    def __init__(self, broker="localhost", port=1883):
        self.client = mqtt.Client()
        self.client.connect(broker, port, 60)

    def publish(self, topic, payload):
        self.client.publish(topic, payload)

    def start_loop(self):
        self.client.loop_start()