# ĐẶC TẢ THIẾT KẾ CHI TIẾT MESSAGE & PAYLOAD SCHEMA (CHUẨN HÓA THEO SLIDE 65)
## HỆ THỐNG BÁO KHÓI CẢNH BÁO SỚM - ĐỒ ÁN IoT (Nhóm 09)
**Căn cứ kỹ thuật:** Slide 65–67 bài giảng [3. Lập trình IoT.pptx](file:///e:/IoT/DoAn/docs/pdf/3.%20Lập%20trình%20IoT.pptx)  
**Giảng viên hướng dẫn:** ThS. Võ Hoàng Hải  

---

### I. TỔNG QUAN KIẾN TRÚC 4 DỊCH VỤ TRUYỀN THÔNG (SLIDE 65)

Theo mô hình kiến trúc chuẩn trong Slide 65, việc giao tiếp giữa **Thiết bị cảm biến (ESP32)** và **Hệ thống Server / Middleware** thông qua **MQTT Broker** được chia thành 4 dịch vụ độc lập, chuyên biệt:

```
+---------------------------------------------------------------------------------------+
|                                    MQTT BROKER                                        |
+---------------------------------------------------------------------------------------+
        ^ (1a) Pub Auth               | (1b) Sub Auth
        | (1d) Sub Result             v (1c) Pub Result
+--------------------+        +---------------------------------------------------------+
|                    |        | DỊCH VỤ 1: AUTHENTICATION SERVICE                       |
|                    |        | - Xác thực Device ID & Secret Token qua Database        |
|                    |        | - Cấp phát Session Key và cấu hình hoạt động ban đầu    |
|                    |        +---------------------------------------------------------+
|                    |
|                    |        +---------------------------------------------------------+
|                    |        | DỊCH VỤ 2: COLLECT SENSORS DATA SERVICE                 |
|   DEVICE (ESP32)   |        | - Thu thập Telemetry (MQ-2 PPM, DHT22 Nhiệt độ, Độ ẩm)  |
| - Đọc cảm biến     |        | - Kiểm tra tính toàn vẹn và lưu trữ lịch sử Time-series |
| - Điều khiển quạt  |        +---------------------------------------------------------+
| - Báo Keep-Alive   |                ^ (2a) Pub Data             | (2b) Sub Data
| - Xác thực Token   |                |                           v
|                    |        +---------------------------------------------------------+
|                    |        | DỊCH VỤ 3: CONTROL SERVICE & RULE ENGINE                |
|                    |        | - Phát lệnh điều khiển Quạt hút DC, Còi hú Buzzer       |
|                    |        | - Tiếp nhận gói tin xác nhận thi hành lệnh (Status ACK) |
|                    |        +---------------------------------------------------------+
|                    |                | (3a) Pub Command          ^ (3b) Sub Status ACK
|                    |                v                           |
|                    |        +---------------------------------------------------------+
|                    |        | DỊCH VỤ 4: KEEP-ALIVE (DEVICE HEARTBEAT SERVICE)        |
|                    |        | - Giám sát nhịp sống thiết bị, tình trạng RAM, WiFi     |
|                    |        | - Bắt sự cố mất nguồn, đứt cáp hoặc mất kết nối mạng    |
+--------------------+        +---------------------------------------------------------+
                                      ^ (4a) Pub Keep-Alive       | (4b) Sub Keep-Alive
```

---

### II. BỘ QUY HOẠCH TOPIC TREE PHÂN CẤP & KHẢ NĂNG MỞ RỘNG (SCALE)

Để hỗ trợ từ **1 thiết bị** đến **hàng trăm thiết bị** đặt tại các tầng và phòng khác nhau của tòa nhà mà không bị xung đột, Topic Tree được phân cấp theo cấu trúc chuẩn không gian (Spatial Hierarchy):

```
smoke/v2/{building_id}/{floor_id}/{room_id}/{device_id}/{service_channel}
```

- `building_id`: Mã tòa nhà (ví dụ: `HUIT_A`, `Building_01`).
- `floor_id`: Mã tầng (ví dụ: `F01`, `F03`).
- `room_id`: Mã phòng/Khu vực (ví dụ: `P302`, `Kitchen`, `ServerRoom`).
- `device_id`: Mã định danh vật lý duy nhất của ESP32 (ví dụ: `ESP32_SMOKE_01`).
- `service_channel`: Kênh chức năng tương ứng 4 dịch vụ (`auth`, `telemetry`, `cmd`, `status`, `keep_alive`, `event`).

#### Quy ước đăng ký Wildcard cho Middleware / Server:
- Lắng nghe toàn bộ cảm biến của Tòa nhà A: `smoke/v2/HUIT_A/+/+/+/telemetry`
- Lắng nghe sự cố khẩn cấp toàn hệ thống: `smoke/v2/+/+/+/+/event/#`
- Lắng nghe trạng thái sống Keep-alive: `smoke/v2/+/+/+/+/keep_alive`

---

### III. ĐẶC TẢ CHI TIẾT 4 DỊCH VỤ & PAYLOAD SCHEMA

---

#### 1. DỊCH VỤ 1: XÁC THỰC & ĐĂNG KÝ THIẾT BỊ (AUTHENTICATION SERVICE)

Mục đích: Thiết bị khi khởi động chưa được phép gửi Telemetry tự do. Thiết bị phải gửi mã ID và mật mã bí mật (Secret Hash) để Server kiểm tra Whitelist trong cơ sở dữ liệu. Nếu hợp lệ, Server cấp **Session Key** kèm cấu hình ngưỡng.

##### (1a) Bản tin Yêu cầu Xác thực (Device -> Server)
- **Topic:** `smoke/v2/auth/request`
- **QoS:** 1
- **JSON Payload:**
```json
{
  "msg_id": "REQ-AUTH-20261005-001",
  "device_id": "ESP32_SMOKE_N09_A01",
  "mac_address": "24:6F:28:AB:CD:10",
  "device_type": "SMOKE_DETECTOR_NODE",
  "hw_version": "v1.2",
  "fw_version": "v2.0.1",
  "secret_token": "HUIT_IOT_SECURE_TOKEN_N09",
  "timestamp": 1728130000
}
```

##### (1c & 1d) Bản tin Kết quả Xác thực (Server -> Device)
- **Topic:** `smoke/v2/auth/response/ESP32_SMOKE_N09_A01`
- **QoS:** 1 (Retain: false)
- **JSON Payload (Trường hợp THÀNH CÔNG):**
```json
{
  "msg_id": "RESP-AUTH-20261005-001",
  "status": "PASS",
  "status_code": 200,
  "session_key": "SK_SESSION_987654321_N04",
  "lease_duration_sec": 86400,
  "assigned_topology": {
    "building": "HUIT_A",
    "floor": "F03",
    "room": "P302",
    "zone_name": "Phòng Thí Nghiệm IoT"
  },
  "runtime_config": {
    "telemetry_interval_ms": 2000,
    "keep_alive_interval_ms": 10000,
    "alarm_threshold_ppm": 400.0,
    "warning_threshold_ppm": 250.0,
    "safe_threshold_ppm": 300.0,
    "overheat_threshold_c": 55.0
  }
}
```

- **JSON Payload (Trường hợp BỊ TỪ CHỐI):**
```json
{
  "msg_id": "RESP-AUTH-20261005-002",
  "status": "REJECTED",
  "status_code": 401,
  "error_code": "ERR_INVALID_SECRET_OR_NOT_IN_WHITELIST",
  "message": "Device MAC is not provisioned in database. Connection refused."
}
```

---

#### 2. DỊCH VỤ 2: THU THẬP DỮ LIỆU CẢM BIẾN (COLLECT SENSORS DATA SERVICE)

Mục đích: Sau khi đã có `session_key` hợp lệ, ESP32 thu thập định kỳ thông số từ cảm biến MQ-2 và DHT22, đóng gói kèm trạng thái hiện tại của Quạt/Còi và mã lỗi (nếu có).

##### (2a & 2b) Bản tin Thu thập Dữ liệu Telemetry (Device -> Server)
- **Topic:** `smoke/v2/HUIT_A/F03/P302/ESP32_SMOKE_N09_A01/telemetry`
- **QoS:** 0
- **JSON Payload:**
```json
{
  "session_key": "SK_SESSION_987654321_N04",
  "device_id": "ESP32_SMOKE_N09_A01",
  "seq": 1024,
  "timestamp": 1728130020,
  "sensors": {
    "mq2_ppm": 142.5,
    "mq2_raw_adc": 820,
    "temperature_c": 28.6,
    "humidity_pct": 63.2
  },
  "actuators": {
    "fan_relay": "OFF",
    "buzzer": "OFF"
  },
  "system_state": {
    "fsm_mode": "AUTO",
    "sensor_ok": true,
    "safety_lock": false
  }
}
```

##### Bản tin Sự kiện Khẩn cấp (Event-Driven Urgent Alarm)
Khi phát hiện khói vượt ngưỡng tức thời ($\ge 400\text{ PPM}$), ESP32 không đợi hết chu kỳ lấy mẫu 2 giây mà bắn ngay bản tin ngắt khẩn cấp:
- **Topic:** `smoke/v2/HUIT_A/F03/P302/ESP32_SMOKE_N09_A01/event/alarm`
- **QoS:** 1
- **JSON Payload:**
```json
{
  "session_key": "SK_SESSION_987654321_N04",
  "device_id": "ESP32_SMOKE_N09_A01",
  "event_code": "CRITICAL_SMOKE_HAZARD",
  "severity": "CRITICAL",
  "mq2_ppm": 485.6,
  "temperature_c": 32.1,
  "local_action_taken": {
    "fan": "ON",
    "buzzer": "ON"
  },
  "timestamp": 1728130025
}
```

---

#### 3. DỊCH VỤ 3: ĐIỀU KHIỂN THIẾT BỊ CHẤP HÀNH (CONTROL SERVICE)

Mục đích: Cho phép Server/Middleware gửi lệnh điều khiển xuống cơ cấu chấp hành (Quạt hút khói, Còi báo động), đồng thời ESP32 phải trả về bản tin phản hồi (ACK) để xác nhận lệnh đã thực thi thành công hay bị Ma trận An toàn PCCC chặn lại.

##### (3a) Bản tin Lệnh Điều khiển Downlink (Server -> Device)
- **Topic:** `smoke/v2/HUIT_A/F03/P302/ESP32_SMOKE_N09_A01/cmd/fan`
- **QoS:** 1
- **JSON Payload:**
```json
{
  "cmd_id": "CMD-20261005-0089",
  "action": "ON",
  "target": "EXHAUST_FAN_RELAY",
  "priority": "HIGH",
  "timeout_sec": 60,
  "reason": "RULE_1_SMOKE_ALARM_AUTO_TRIGGER",
  "issued_by": "MIDDLEWARE_NODE_RED",
  "timestamp": 1728130026
}
```

##### (3b) Bản tin Phản hồi Thực thi Lệnh (Device Status ACK -> Server)
- **Topic:** `smoke/v2/HUIT_A/F03/P302/ESP32_SMOKE_N09_A01/status`
- **QoS:** 1
- **JSON Payload (Trường hợp Chấp nhận lệnh):**
```json
{
  "cmd_id": "CMD-20261005-0089",
  "device_id": "ESP32_SMOKE_N09_A01",
  "status": "SUCCESS",
  "current_state": "ON",
  "safety_interlock": "NORMAL",
  "current_ppm": 485.6,
  "timestamp": 1728130027
}
```

- **JSON Payload (Trường hợp Từ chối do Ma trận An toàn PCCC - Interlock Lockout):**
```json
{
  "cmd_id": "CMD-20261005-0090",
  "device_id": "ESP32_SMOKE_N09_A01",
  "status": "REJECTED_SAFETY_LOCK",
  "current_state": "ON",
  "reason": "CANNOT_TURN_OFF_FAN_WHILE_PPM_EXCEEDS_ALARM_THRESHOLD",
  "current_ppm": 520.4,
  "timestamp": 1728130030
}
```

---

#### 4. DỊCH VỤ 4: TÍN HIỆU DUY TRÌ KẾT NỐI (KEEP-ALIVE / DEVICE HEARTBEAT SERVICE)

Mục đích: Báo cáo trạng thái sống của thiết bị vi điều khiển ESP32, tình trạng bộ nhớ RAM, sóng Wi-Fi và nguồn điện. Nếu quá 15 giây Server không nhận được gói tin này, Server chuyển trạng thái thiết bị sang `OFFLINE`.

##### (4a & 4b) Bản tin Keep-Alive Heartbeat (Device -> Server)
- **Topic:** `smoke/v2/HUIT_A/F03/P302/ESP32_SMOKE_N09_A01/keep_alive`
- **QoS:** 0
- **Chu kỳ gửi:** 10 giây / lần
- **JSON Payload:**
```json
{
  "session_key": "SK_SESSION_987654321_N04",
  "device_id": "ESP32_SMOKE_N09_A01",
  "uptime_sec": 7240,
  "free_heap_bytes": 182400,
  "wifi_rssi_dbm": -56,
  "power_source": "MAINS_AC_5V",
  "health_status": "HEALTHY",
  "timestamp": 1728130030
}
```

##### Bản tin Last Will and Testament (LWT)
Được cấu hình sẵn khi ESP32 bắt tay với Broker MQTT. Nếu ESP32 bị mất điện hoặc đứt mạng đột ngột, Broker sẽ tự động phát bản tin này:
- **Topic:** `smoke/v2/HUIT_A/F03/P302/ESP32_SMOKE_N09_A01/lwt`
- **QoS:** 1 (Retain: true)
- **Payload:** `"offline"`

---

### IV. CƠ CHẾ KIỂM SOÁT THÊM THIẾT BỊ MỚI (DEVICE ONBOARDING WORKFLOW)

Khi mở rộng hệ thống bằng cách lắp thêm cảm biến khói ESP32 mới vào mạng, quy trình kiểm soát được thực thi nghiêm ngặt:

1. **Giai đoạn Đăng ký trước (Pre-provisioning Whitelist):**
   - Người quản trị nạp địa chỉ MAC và mã Token của bo mạch mới vào Database (`Device_Whitelist_Table`).
2. **Giai đoạn Cấp nguồn & Bắt tay (Power-on & Auth Handshake):**
   - Thiết bị mới phát bản tin `smoke/v2/auth/request`.
   - Nếu thiết bị có trong Whitelist: Server sinh `Session Key`, chỉ định phòng/khu vực lắp đặt (`assigned_topology`), truyền tham số ngưỡng `runtime_config`.
   - Nếu thiết bị lạ (không có trong Whitelist): Server từ chối cấp quyền, Broker chặn không cho Subscribe/Publish vào các kênh điều khiển.
3. **Giai đoạn Tích hợp & Quản trị Hạm đội (Fleet Registry):**
   - Node-RED tự động bổ sung Node mới vào bảng quản trị (`Device Registry Table`), khởi tạo FSM riêng biệt và bắt đầu chu trình đếm nhịp Keep-alive 10s.

---

### V. ĐÁNH GIÁ ĐÁP ỨNG TIÊU CHÍ SLIDE 65 CỦA BÀI GIẢNG

| Tiêu chuẩn trong Slide 65 | Hiện thực của Nhóm 09 | Đánh giá |
| :--- | :--- | :---: |
| **Authentication topics & Result** | Kênh `auth/request` và `auth/response` kèm Session Key và Whitelist MAC | **ĐẠT 100%** |
| **Collect topics & Sensors data** | Kênh `telemetry` và `event/alarm` chuẩn hóa JSON Schema đầy đủ MQ-2 & DHT22 | **ĐẠT 100%** |
| **Control topic & Command feedback** | Kênh `cmd/fan` và `status` có mã xác nhận thi hành lệnh kèm Ma trận PCCC Interlock | **ĐẠT 100%** |
| **Keep_alive topic & Service** | Kênh `keep_alive` chu kỳ 10s giám sát Uptime, RAM, RSSI và LWT ngắt mạng | **ĐẠT 100%** |
| **Cơ chế Scale & Đa thiết bị** | Cấu trúc phân cấp 5 tầng hỗ trợ Wildcard `smoke/v2/+/+/+/+` và Dynamic Registry | **ĐẠT 100%** |

