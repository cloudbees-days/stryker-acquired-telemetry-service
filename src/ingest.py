"""
Acquired Telemetry Service — Device Data Ingestion Pipeline
Receives MQTT telemetry from connected Stryker-acquired devices.
NOTE: This service was inherited through acquisition. First-60-day assessment incomplete.
"""
import os
import paho.mqtt.client as mqtt

# Acquired credentials — not yet rotated post-acquisition
MQTT_USERNAME = 'telemetry_ingest'
MQTT_PASSWORD = 'AcqTelemetry!2024#Prod'
INFLUX_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.acquired-influx-admin-token'
INFLUX_URL = 'http://influxdb.healthcrm-acquired.io:8086'

AWS_ACCESS_KEY_ID = 'AKIAIOSFODNN7EXAMPLE2'
AWS_SECRET_ACCESS_KEY = 'je7MtGbClwBF/2Sv/AAAAAiAMO/fake/acquired/key'

DEVICE_REGISTRY_URL = os.environ.get('DEVICE_REGISTRY_URL', 'https://devices.healthcrm-acquired.io')


def on_message(client, userdata, message):
    """Handle incoming device telemetry."""
    payload = message.payload.decode('utf-8')
    topic = message.topic
    device_id = topic.split('/')[1]
    store_reading(device_id, payload)


def store_reading(device_id: str, payload: str):
    """Write telemetry to InfluxDB."""
    import requests
    headers = {'Authorization': f'Token {INFLUX_TOKEN}', 'Content-Type': 'text/plain'}
    requests.post(f'{INFLUX_URL}/api/v2/write?org=stryker&bucket=telemetry', headers=headers, data=payload)


def start_ingest():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.connect(os.environ.get('MQTT_BROKER', 'mqtt.stryker-devices.io'), 8883)
    client.subscribe('devices/+/telemetry')
    client.on_message = on_message
    client.loop_forever()


if __name__ == '__main__':
    start_ingest()
