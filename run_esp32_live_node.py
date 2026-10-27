# -*- coding: utf-8 -*-
"""
LIVE ESP32 FIRMWARE NODE (MÔ PHỎNG PHẦN CỨNG WOKWI KẾT NỐI BROKER THẬT)
Đề tài 04: Hệ thống Báo khói Cảnh báo sớm - Nhóm 04 (N09)
Kết nối trực tiếp vào EMQX Cloud Broker (broker.emqx.io:1883):
- Publish telemetry mỗi 2s lên 'smoke/telemetry'
- Lắng nghe lệnh Downlink từ Web Dashboard và Node-RED
- Phản hồi gói tin xác nhận ACK lên 'smoke/status'
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
CLIENT_ID = "ESP32_Smoke_Nhom04_A01_Live"

TOPIC_TELEMETRY = "Nhom09/smoke/telemetry"
TOPIC_STATUS = "Nhom09/smoke/status"
TOPIC_LWT = "Nhom09/smoke/lwt"
TOPIC_CMD_FAN = "Nhom09/smoke/cmd/fan"
TOPIC_CMD_BUZZER = "Nhom09/smoke/cmd/buzzer"
TOPIC_CMD_SENSITIVITY = "Nhom09/smoke/cmd/sensitivity"

LOG_FILE = r"e:\IoT\DoAn\logs\live_test_esp32.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log_event(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] {msg}"
    print(entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")

class LiveEsp32Device:
    def __init__(self):
        self.fan_state = False
        self.buzzer_state = False
        self.is_muted = False
        self.mute_timer = 0
        self.fsm_state = "SAFE"
        self.ppm = 165.4
        self.temp = 28.5
        self.hum = 61.2
        self.alarm_threshold = 400.0
        self.safe_threshold = 300.0
        self.cycle_count = 0

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            log_event(f"ESP32 Connected to EMQX Cloud Broker ({BROKER_HOST}:{BROKER_PORT}) successfully!")
            client.subscribe([(TOPIC_CMD_FAN, 1), (TOPIC_CMD_BUZZER, 1), (TOPIC_CMD_SENSITIVITY, 1)])
            log_event("Subscribed to command topics: smoke/cmd/fan, smoke/cmd/buzzer, smoke/cmd/sensitivity")
        else:
            log_event(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload_str = msg.payload.decode('utf-8', errors='ignore')
        log_event(f"RECV COMMAND on topic [{topic}]: {payload_str}")

        try:
            data = json.loads(payload_str)
        except Exception:
            data = {"command": payload_str}

        cmd = data.get("command", "").upper()
        ack_type = "UNKNOWN"

        if topic == TOPIC_CMD_FAN:
            if cmd == "ON":
                self.fan_state = True
                ack_type = "FAN_ON_SUCCESS"
                log_event(">>> ACTION: Relay GPIO17 ON -> Fan is RUNNING")
            elif cmd == "OFF":
                if self.fsm_state == "ALARM":
                    ack_type = "REJECTED_SAFETY_INTERLOCK"
                    log_event(">>> BLOCKED: Safety interlock active! Cannot turn off fan during ALARM.")
                else:
                    self.fan_state = False
                    ack_type = "FAN_OFF_SUCCESS"
                    log_event(">>> ACTION: Relay GPIO17 OFF -> Fan is STOPPED")

        elif topic == TOPIC_CMD_BUZZER:
            if cmd == "MUTE":
                self.is_muted = True
                self.buzzer_state = False
                self.mute_timer = time.time()
                ack_type = "BUZZER_MUTED_180S"
                log_event(">>> ACTION: PWM GPIO16 Muted for 180s")
            elif cmd == "UNMUTE":
                self.is_muted = False
                if self.fsm_state == "ALARM":
                    self.buzzer_state = True
                ack_type = "BUZZER_UNMUTED"
                log_event(">>> ACTION: PWM GPIO16 Unmuted")

        elif topic == TOPIC_CMD_SENSITIVITY:
            mode = data.get("mode", "DAY").upper()
            if mode == "NIGHT":
                self.alarm_threshold = 350.0
                ack_type = "SENSITIVITY_NIGHT_APPLIED"
            else:
                self.alarm_threshold = 400.0
                ack_type = "SENSITIVITY_DAY_APPLIED"
            log_event(f">>> CONFIG: Alarm threshold set to {self.alarm_threshold} PPM ({mode})")

        # Publish ACK response to smoke/status
        ack_payload = {
            "device_id": "ESP32_SMOKE_N04_A01",
            "ack": ack_type,
            "fan": self.fan_state,
            "buzzer": self.buzzer_state,
            "state": self.fsm_state,
            "timestamp": time.time()
        }
        client.publish(TOPIC_STATUS, json.dumps(ack_payload), qos=1)
        log_event(f"SEND ACK on [{TOPIC_STATUS}]: {ack_payload}")

    def loop_telemetry(self, client):
        self.cycle_count += 1

        # Tạo dao động nhẹ tự nhiên
        drift = (self.cycle_count % 5) * 1.5
        current_ppm = self.ppm + drift

        # Nếu có cờ báo động cháy khẩn cấp trong file trigger
        trigger_file = r"e:\IoT\DoAn\logs\trigger_alarm.flag"
        if os.path.exists(trigger_file):
            current_ppm = 650.0
            self.fsm_state = "ALARM"
            self.fan_state = True
            if not self.is_muted:
                self.buzzer_state = True
        else:
            if current_ppm >= self.alarm_threshold:
                self.fsm_state = "ALARM"
                self.fan_state = True
                if not self.is_muted:
                    self.buzzer_state = True
            else:
                self.fsm_state = "SAFE"

        # Kiểm tra hết hạn Mute sau 180s
        if self.is_muted and (time.time() - self.mute_timer) > 180.0:
            self.is_muted = False
            if self.fsm_state == "ALARM":
                self.buzzer_state = True
            log_event(">>> TIMER: Mute period expired, buzzer restored.")

        telemetry_payload = {
            "device_id": "ESP32_SMOKE_N04_A01",
            "ppm": round(current_ppm, 1),
            "temp": round(self.temp, 1),
            "hum": round(self.hum, 1),
            "state": self.fsm_state,
            "fan": self.fan_state,
            "buzzer": self.buzzer_state,
            "timestamp": time.time(),
            "uptime_sec": self.cycle_count * 2
        }

        client.publish(TOPIC_TELEMETRY, json.dumps(telemetry_payload), qos=0)
        log_event(f"PUB TELEMETRY: PPM={telemetry_payload['ppm']} | State={telemetry_payload['state']} | Fan={telemetry_payload['fan']}")

def main():
    log_event("=== STARTING LIVE ESP32 FIRMWARE NODE ===")
    device = LiveEsp32Device()
    client = mqtt.Client(client_id=CLIENT_ID, clean_session=True)
    client.on_connect = device.on_connect
    client.on_message = device.on_message

    lwt_payload = json.dumps({"device_id": "ESP32_SMOKE_N04_A01", "status": "OFFLINE"})
    client.will_set(TOPIC_LWT, lwt_payload, qos=1, retain=True)

    client.connect(BROKER_HOST, BROKER_PORT, 60)
    client.loop_start()

    try:
        while True:
            device.loop_telemetry(client)
            time.sleep(2.0)
    except KeyboardInterrupt:
        log_event("Stopping Live ESP32 Node...")
    finally:
        client.loop_stop()
        client.disconnect()
        log_event("Disconnected from Broker.")

if __name__ == "__main__":
    main()
