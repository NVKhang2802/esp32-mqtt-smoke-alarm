# -*- coding: utf-8 -*-
"""
KỊCH BẢN KIỂM THỬ TẦNG 3 - MULTI-DEVICE SIMULATOR (CHUẨN SLIDE 65)
Đề tài: Hệ thống báo khói cảnh báo sớm - Nhóm 04
Kiểm thử 4 dịch vụ: Authentication (1a-1d), Collect (2a-2b), Control (3a-3b), Keep-Alive (4a-4b)
Kiểm thử cơ chế Scale hạm đội 3 thiết bị và Cảnh báo liên vùng (Cross-Zone)
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import time
import json
import paho.mqtt.client as mqtt

BROKER = "broker.emqx.io"
PORT = 1883

received_messages = []

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"[TEST CLIENT] Connected to {BROKER}:{PORT} (rc={rc})")
    # Đăng ký nhận phản hồi xác thực và toàn bộ lệnh Downlink
    client.subscribe("smoke/v2/auth/response/#")
    client.subscribe("smoke/v2/+/+/+/+/cmd/#")
    client.subscribe("smoke/v2/HUIT_A/F03/+/cmd/buzzer")
    client.subscribe("smoke/cmd/#")
    print("[TEST CLIENT] Subscribed to Auth Responses and Downlink Commands.")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode('utf-8')
    except:
        payload = str(msg.payload)
    print(f"\n[RECEIVE DOWNLINK] Topic: {msg.topic}")
    print(f"                  Payload: {payload}")
    received_messages.append({
        "topic": msg.topic,
        "payload": payload,
        "time": time.strftime("%H:%M:%S")
    })

def run_test_suite():
    print("=" * 70)
    print("  BẮT ĐẦU KIỂM THỬ HẠM ĐỘI ĐA THIẾT BỊ THEO CHUẨN SLIDE 65 (TUẦN 5)")
    print("=" * 70)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="Python_Fleet_Tester_N04")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER, PORT, keepalive=60)
        client.loop_start()
    except Exception as e:
        print(f"[ERROR] Không thể kết nối broker: {e}")
        return

    time.sleep(2)

    # ----------------------------------------------------
    # Case 1: Thử nghiệm Xác thực Thiết bị hợp chuẩn (Slide 65: 1a - 1d)
    # ----------------------------------------------------
    print("\n--- [CASE 1] Gửi Yêu cầu Xác thực cho Node 01 (Hợp chuẩn Whitelist) ---")
    auth_req_1 = {
        "msg_id": "REQ-AUTH-TEST-001",
        "device_id": "ESP32_SMOKE_N04_A01",
        "mac_address": "24:6F:28:AB:CD:10",
        "secret_token": "HUIT_IOT_SECURE_TOKEN_N04",
        "timestamp": int(time.time())
    }
    client.publish("smoke/v2/auth/request", json.dumps(auth_req_1), qos=1)
    time.sleep(3)

    # ----------------------------------------------------
    # Case 2: Thử nghiệm Thiết bị Lạ bị Từ chối (Security Test)
    # ----------------------------------------------------
    print("\n--- [CASE 2] Gửi Yêu cầu Xác thực từ Thiết bị Lạ (Không có trong Whitelist) ---")
    auth_req_bad = {
        "msg_id": "REQ-AUTH-TEST-002",
        "device_id": "ESP32_ROGUE_ATTACKER",
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "secret_token": "FAKE_TOKEN",
        "timestamp": int(time.time())
    }
    client.publish("smoke/v2/auth/request", json.dumps(auth_req_bad), qos=1)
    time.sleep(3)

    # ----------------------------------------------------
    # Case 3: Gửi Tín hiệu duy trì kết nối Keep-Alive (Slide 65: 4a - 4b)
    # ----------------------------------------------------
    print("\n--- [CASE 3] Gửi Gói tin Keep-Alive Heartbeat cho 2 Nodes ---")
    for dev_id, room in [("ESP32_SMOKE_N04_A01", "P302"), ("ESP32_SMOKE_N04_A02", "P303")]:
        keep_alive_pkg = {
            "session_key": "SK_SESSION_TEST_N04",
            "device_id": dev_id,
            "uptime_sec": 3600,
            "free_heap_bytes": 184520,
            "wifi_rssi_dbm": -55,
            "status": "HEALTHY"
        }
        topic = f"smoke/v2/HUIT_A/F03/{room}/{dev_id}/keep_alive"
        client.publish(topic, json.dumps(keep_alive_pkg), qos=0)
        print(f"  -> Keep-Alive sent for {dev_id} ({room})")
    time.sleep(3)

    # ----------------------------------------------------
    # Case 4: Thu thập dữ liệu Telemetry an toàn (Slide 65: 2a - 2b)
    # ----------------------------------------------------
    print("\n--- [CASE 4] Gửi Telemetry Môi trường an toàn (PPM: 125, Temp: 28C) ---")
    telemetry_safe = {
        "session_key": "SK_SESSION_TEST_N04",
        "device_id": "ESP32_SMOKE_N04_A01",
        "mq2_ppm": 125.4,
        "temp": 28.2,
        "hum": 64.0,
        "fan": "OFF",
        "mode": "AUTO"
    }
    client.publish("smoke/v2/HUIT_A/F03/P302/ESP32_SMOKE_N04_A01/telemetry", json.dumps(telemetry_safe), qos=0)
    time.sleep(3)

    # ----------------------------------------------------
    # Case 5: Kích hoạt Báo động khói cục bộ (PPM: 470 >= 400) -> Rule 1
    # ----------------------------------------------------
    print("\n--- [CASE 5] Khói cục bộ vượt ngưỡng báo động (PPM: 470 >= 400) ---")
    telemetry_alarm = {
        "session_key": "SK_SESSION_TEST_N04",
        "device_id": "ESP32_SMOKE_N04_A01",
        "mq2_ppm": 472.5,
        "temp": 33.0,
        "hum": 55.0,
        "fan": "OFF",
        "mode": "AUTO"
    }
    client.publish("smoke/v2/HUIT_A/F03/P302/ESP32_SMOKE_N04_A01/telemetry", json.dumps(telemetry_alarm), qos=0)
    print(">> Đang chờ lệnh Downlink bật Quạt hút...")
    time.sleep(4)

    # ----------------------------------------------------
    # Case 6: Cảnh báo liên vùng Cross-Zone (Cháy lớn PPM: 650 >= 600)
    # ----------------------------------------------------
    print("\n--- [CASE 6] Hỏa hoạn nghiêm trọng (PPM: 655 >= 600) -> Test Cross-Zone Emergency ---")
    telemetry_panic = {
        "session_key": "SK_SESSION_TEST_N04",
        "device_id": "ESP32_SMOKE_N04_A01",
        "mq2_ppm": 655.0,
        "temp": 42.0,
        "hum": 45.0,
        "fan": "ON",
        "mode": "AUTO"
    }
    client.publish("smoke/v2/HUIT_A/F03/P302/ESP32_SMOKE_N04_A01/telemetry", json.dumps(telemetry_panic), qos=0)
    print(">> Đang chờ lệnh kích hoạt Còi hú toàn bộ Tầng 3 (Cross-Zone)...")
    time.sleep(4)

    print("\n" + "=" * 70)
    print(f"  KẾT QUẢ KIỂM THỬ: Đã nhận {len(received_messages)} thông điệp phản hồi từ hệ thống.")
    for idx, item in enumerate(received_messages, 1):
        print(f"   {idx}. [{item['time']}] Topic: {item['topic']} -> {item['payload']}")
    print("=" * 70)

    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    run_test_suite()
