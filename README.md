# 🚨 Hệ Thống Báo Khói Cảnh Báo Sớm IoT (Early Smoke Detection & Warning System)

> **Đề tài 04 - Nhóm 04 (N09)**  
> **Nền tảng:** ESP32 (ESP32-WROOM-32D) | FreeRTOS / Arduino Framework  
> **Giao thức:** MQTT (PubSubClient, ArduinoJson v7) | EMQX Public Broker  
> **Mô phỏng & Giám sát:** Wokwi Simulator | Node-RED Dashboard | Web Realtime Dashboard  

---

## 📌 1. Giới Thiệu Dự Án

Dự án nghiên cứu và phát triển **Hệ thống giám sát và cảnh báo khói sớm thông minh** ứng dụng vi điều khiển ESP32 và công nghệ IoT. Hệ thống có khả năng đo đạc liên tục các thông số môi trường (nồng độ khí gas/khói PPM, nhiệt độ, độ ẩm), áp dụng thuật toán lọc tín hiệu số và mô hình **Máy trạng thái hữu hạn (FSM)** để đưa ra các cấp độ phản ứng kịp thời: từ cảnh báo âm thanh, tự động kích hoạt quạt hút khói/relay, đến phát tín hiệu báo động khẩn cấp đa kênh qua MQTT Broker.

Dự án được xây dựng theo chuẩn **Lean & Clean Code**, kiểm soát bộ nhớ nghiêm ngặt (**Zero Heap Fragmentation**), đảm bảo hoạt động bền bỉ, tin cậy trong môi trường nhúng thực tế.

---

## 🌟 2. Tính Năng Nổi Bật (Key Features)

- **Đo lường & Phân tích môi trường thời gian thực:**
  - Cảm biến khói/khí gas **MQ-2** với thuật toán lấy mẫu trung bình động (**Moving Average 5 mẫu**) và tính toán đường cong đặc tuyến $R_s / R_0$.
  - Cảm biến nhiệt - ẩm kỹ thuật số **DHT22** độ chính xác cao.
- **Máy trạng thái hữu hạn (FSM - Finite State Machine):**
  - Quản lý 5 trạng thái vận hành chặt chẽ: `NORMAL` (Bình thường), `PRE_ALARM` (Tiền cảnh báo), `ALARM` (Báo động cháy), `FAULT` (Sự cố phần cứng), `COOLDOWN/TEST` (Hồi phục / Kiểm tra).
- **Bộ đệm vòng ngoại tuyến (Offline Circular Buffer):**
  - Tích hợp bộ nhớ đệm vòng lưu trữ dữ liệu cảm biến cục bộ khi mất kết nối mạng.
  - Tự động đồng bộ lịch sử (`history/sync`) lên Broker ngay khi kết nối mạng phục hồi, chống thất thoát dữ liệu quan trọng.
- **Cơ chế tự phục hồi kết nối (Self-Healing Network):**
  - Tự động tái kết nối WiFi và MQTT Broker theo thuật toán **Non-blocking Exponential Backoff**.
  - Đăng ký cơ chế **LWT (Last Will and Testament)** cảnh báo trạng thái thiết bị ngoại tuyến tức thì cho hệ thống trung tâm.
- **Bàn kiểm thử sự cố từ xa (Fault Injection Sandbox):**
  - Hỗ trợ nhận lệnh kiểm thử sự cố từ Web/MQTT: ngắt giả lập cảm biến MQ-2, làm đơ DHT22, hoặc kiểm tra lỗi truyền động (Actuator failure) nhằm đánh giá độ bền bỉ của hệ thống.
- **Web Dashboard & Node-RED thời gian thực:**
  - Giao diện Web trực quan hiển thị đồng hồ đo PPM khói (Gauge), biểu đồ nhiệt độ - độ ẩm, đèn LED hiển thị trạng thái FSM, điều khiển quạt / còi từ xa và phát âm thanh còi hú trực tiếp trên trình duyệt.

---

## 🔌 3. Sơ Đồ Đấu Nối Phần Cứng (Hardware Pinout)

Hệ thống được thiết kế và mô phỏng trên nền tảng **Wokwi** (`diagram.json`, `wokwi.toml`) với sơ đồ chân như sau:

| Linh Kiện / Thiết Bị | Loại Tín Hiệu | Chân ESP32 | Mô Tả Chức Năng |
| :--- | :---: | :---: | :--- |
| **Cảm biến khói MQ-2** | Analog In | **GPIO 34** (ADC1_CH6) | Đọc điện áp analog từ cầu phân áp, chuyển đổi sang nồng độ PPM |
| **Cảm biến DHT22** | Digital In/Out | **GPIO 4** | Giao thức 1-Wire đọc nhiệt độ (°C) và độ ẩm (%RH) |
| **Còi chíp (Buzzer)** | PWM Output | **GPIO 16** (LEDC Ch0) | Điều khiển tần số âm thanh (2000Hz base, 800Hz alarm, 50% duty) |
| **Relay Quạt Hút (Fan)** | Digital Out | **GPIO 17** | Kích hoạt quạt hút khói khẩn cấp / Đèn chỉ thị quạt |
| **Nút bấm nhấn nhả (Button)** | Digital In | **GPIO 18** (INPUT_PULLUP) | Nút bấm vật lý bật/tắt quạt thủ công với thuật toán chống rung (Debounce) |

---

## 📡 4. Giao Thức Mạng & Danh Mục MQTT Topics

Hệ thống giao tiếp qua máy chủ MQTT **`broker.emqx.io`** (Port: `1883`) với Client ID duy nhất dạng `ESP32_Smoke_Nhom04_<MAC>`. Định dạng gói tin sử dụng JSON chuẩn hóa:

| Nhóm Topic | MQTT Topic Path | Chiều Dữ Liệu | Mục Đích |
| :--- | :--- | :---: | :--- |
| **Telemetry** | `Nhom09/smoke/telemetry` | ESP32 ➔ Broker | Gửi định kỳ PPM khói, nhiệt độ, độ ẩm, trạng thái quạt/còi |
| **Event Alarm** | `Nhom09/smoke/event/alarm` | ESP32 ➔ Broker | Bản tin sự kiện khẩn cấp khi chuyển trạng thái `ALARM` |
| **Status** | `Nhom09/smoke/status` | ESP32 ➔ Broker | Báo cáo thông số hệ thống, chu kỳ lặp, trạng thái FSM |
| **Device Control** | `Nhom09/smoke/cmd/fan` | Broker ➔ ESP32 | Lệnh bật/tắt quạt từ xa (`{"state": "ON"|"OFF"}`) |
| **Buzzer Control** | `Nhom09/smoke/cmd/buzzer` | Broker ➔ ESP32 | Lệnh tắt âm còi báo khẩn cấp (`{"state": "OFF"}`) |
| **Mode Control** | `Nhom09/smoke/cmd/mode` | Broker ➔ ESP32 | Chuyển chế độ vận hành (`AUTO`, `MANUAL`, `TEST`) |
| **Fault Injection** | `Nhom09/smoke/cmd/inject_fault` | Broker ➔ ESP32 | Giả lập lỗi cảm biến / actuator phục vụ test bench |
| **LWT** | `Nhom09/smoke/lwt` | ESP32 ➔ Broker | Thông báo thiết bị mất nguồn / mất kết nối bất ngờ |
| **Offline Sync** | `Nhom09/smoke/history/sync` | ESP32 ➔ Broker | Đẩy toàn bộ gói tin lưu trong Offline Buffer khi có mạng lại |

---

## 💻 5. Giao Diện Web Dashboard

Thư mục `web/` chứa toàn bộ mã nguồn giao diện giám sát nền tảng Web:
- **`index.html`**: Cấu trúc giao diện ngữ nghĩa, thiết kế Dark Mode hiện đại, hỗ trợ Responsive trên Desktop và Mobile.
- **`style.css`**: Giao diện Glassmorphism, đổ bóng mượt mà, hiệu ứng động cho còi báo và quạt xoay.
- **`app.js`**: 
  - Kết nối trực tiếp đến MQTT Broker qua WebSocket (`wss://broker.emqx.io:8084/mqtt`).
  - Đồng hồ Gauge hiển thị nồng độ khói PPM theo thời gian thực.
  - Biểu đồ nhiệt độ - độ ẩm thời gian thực.
  - Web Audio API giả lập âm thanh còi hú khi hệ thống vào trạng thái `ALARM`.
  - Bộ điều khiển giả lập sự cố (Fault Injection Workbench).

---

## 🧪 6. Bộ Kịch Bản Kiểm Thử Tự Động Hóa (Python Test Suite)

Các kịch bản kiểm thử toàn diện được viết bằng Python giúp kiểm chứng hệ thống từ đầu đến cuối:
- **`run_all_tests.py`**: Trình điều phối chạy toàn bộ bộ kiểm thử tự động.
- **`test_application_e2e_tuan6.py`**: Kiểm thử tích hợp E2E từ cảm biến, luồng MQTT, đến kích hoạt cơ cấu chấp hành.
- **`test_business_rules_abnormal_tuan7.py`**: Kiểm tra các quy tắc nghiệp vụ khi dữ liệu cảm biến vượt ngưỡng bất thường.
- **`test_e2e_integration_tuan8.py`**: Kiểm tra tích hợp liên thông với hệ thống Node-RED và Web Dashboard.
- **`test_system_robustness_tuan9.py`**: Kiểm tra độ bền bỉ khi mạng chập chờn, mất kết nối và khả năng tự khôi phục dữ liệu qua Offline Buffer.
- **`test_middleware_simulator.py`**: Giả lập trạm nút biên ESP32 để kiểm thử chịu tải.

---

## 🚀 7. Hướng Dẫn Cài Đặt & Vận Hành

### Yêu Cầu Môi Trường
- **VS Code** đã cài tiện ích mở rộng: **PlatformIO IDE** và **Wokwi Simulator**.
- **Python 3.10+** (để chạy các script test tự động).

### 1. Biên dịch Firmware bằng PlatformIO
```powershell
# Di chuyển vào thư mục dự án
cd E:\IoT\DoAn

# Biên dịch mã nguồn ESP32
pio run

# Nạp vào board thực tế (nếu dùng phần cứng thật)
pio run --target upload
```

### 2. Chạy mô phỏng trên Wokwi
1. Cài đặt extension **Wokwi for VS Code**.
2. Mở file `diagram.json`.
3. Nhấn tổ hợp phím `F1` hoặc `Ctrl + Shift + P`, chọn **Wokwi: Start Simulator**.
4. ESP32 sẽ tự động kết nối mạng ảo Wokwi, kết nối broker MQTT và bắt đầu gửi dữ liệu.

### 3. Mở Web Dashboard
Mở trực tiếp file `web/index.html` bằng trình duyệt web (hoặc sử dụng Live Server trong VS Code). Dashboard sẽ tự động kết nối tới MQTT Broker và đồng bộ dữ liệu với ESP32 / Wokwi.

### 4. Chạy bộ kiểm thử tự động
```powershell
python run_all_tests.py
```

---

## 📂 8. Cấu Trúc Thư Mục Dự Án (Repository Structure)

```
E:\IoT\DoAn\
├── .gitignore                    # Cấu hình loại trừ file rác, build và docs nội bộ
├── README.md                     # Tài liệu giới thiệu tổng quan hệ thống (file này)
├── platformio.ini                # Cấu hình biên dịch PlatformIO cho ESP32 Dev Module
├── diagram.json                  # Sơ đồ mạch phần cứng mô phỏng Wokwi
├── wokwi.toml                    # File cấu hình liên kết Wokwi Simulator
│
├── src/                          # Mã nguồn Firmware C++ chính của ESP32
│   ├── config.h                  # Toàn bộ cấu hình chân, ngưỡng cảnh báo, tham số MQTT
│   ├── fsm.h / fsm.cpp           # Máy trạng thái hữu hạn (FSM) xử lý cảnh báo
│   ├── sensors.h / sensors.cpp   # Thuật toán đọc, lọc trung bình động cảm biến MQ-2, DHT22
│   ├── offline_buffer.h / .cpp   # Bộ đệm vòng lưu trữ dữ liệu offline tự đồng bộ
│   └── main.cpp                  # Luồng điều khiển trung tâm (Orchestrator)
│
├── web/                          # Web Dashboard thời gian thực
│   ├── index.html                # Giao diện người dùng
│   ├── style.css                 # Giao diện thiết kế Glassmorphism Dark Mode
│   └── app.js                    # Logic MQTT WebSocket, Chart, Gauge, Sound siren
│
├── nodered/                      # Kịch bản dòng dữ liệu Node-RED
│   └── flows_smoke_detector.json # Flow cấu hình xử lý cảnh báo và giao diện Node-RED
│
├── tests/                        # Bộ kiểm thử bổ trợ
│   └── mqttx_collection_slide65.json # Bộ kịch bản mẫu test bằng MQTTX
│
└── logs/                         # Thư mục lưu log thử nghiệm (đã ignore nội dung log)
    └── .gitkeep                  # Giữ thư mục trên repository
```

---

## 👥 9. Thông Tin Tác Giả & Bản Quyền

- **Học phần:** Đồ Án Internet of Things (IoT)
- **Đề tài 04:** Hệ thống báo khói cảnh báo sớm - Nhóm 04 (N09)
- **Giảng viên hướng dẫn:** Bộ môn IoT / Viễn thông
