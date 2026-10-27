# -*- coding: utf-8 -*-
"""
LIVE MQTTX CLIENT SESSION MONITOR
Đề tài 04: Hệ thống Báo khói Cảnh báo sớm
Kết nối broker.emqx.io:1883, subscribe 'smoke/#', ghi log toàn bộ thông điệp hai chiều.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import time
import json
import os
import paho.mqtt.client as mqtt

BROKER_HOST = "broker.emqx.io"
BROKER_PORT = 1883
CLIENT_ID = "MQTTX_Tester_Nhom04_Live"
LOG_FILE = r"e:\IoT\DoAn\logs\live_test_mqttx.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log_event(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] {msg}"
    print(entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        log_event(f"MQTTX Client connected to {BROKER_HOST}:{BROKER_PORT}")
        client.subscribe("Nhom09/smoke/#", qos=1)
        log_event("MQTTX Subscribed to 'Nhom09/smoke/#' successfully!")
    else:
        log_event(f"MQTTX Connect failed, rc={rc}")

def on_message(client, userdata, msg):
    payload_str = msg.payload.decode('utf-8', errors='ignore')
    log_event(f"[MQTTX INBOX] Topic: {msg.topic} | Payload: {payload_str}")

def main():
    log_event("=== STARTING LIVE MQTTX CLIENT SESSION ===")
    client = mqtt.Client(client_id=CLIENT_ID, clean_session=True)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER_HOST, BROKER_PORT, 60)
    client.loop_start()

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        log_event("Stopping MQTTX session...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
