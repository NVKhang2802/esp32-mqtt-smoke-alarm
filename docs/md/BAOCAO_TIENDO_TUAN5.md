# BÁO CÁO TIẾN ĐỘ ĐỒ ÁN MÔN HỌC (IoT)
## PHẦN 5: THIẾT KẾ & TRIỂN KHAI TẦNG 3 – MIDDLEWARE / AUTOMATION ENGINE (NODE-RED)
**MILESTONE: MIDDLEWARE & AUTOMATION ENGINE (NGHIỆM THU TIẾN ĐỘ TUẦN 5 - 10%)**

---

### THÔNG TIN CHUNG
- **Đề tài 04:** HỆ THỐNG BÁO KHÓI CẢNH BÁO SỚM
- **Nhóm thực hiện:** Nhóm 09 (N09) - Lớp IoT IoT
- **Giảng viên hướng dẫn:** ThS. Võ Hoàng Hải
- **Đơn vị:** Trường Đại học Công Thương TP. Hồ Chí Minh (HUIT) - Khoa Công nghệ Thông tin
- **Năm học:** 2025 – 2026

#### BẢNG PHÂN CÔNG THỰC HIỆN TUẦN 5 (TỐI THIỂU 6 GIỜ / SINH VIÊN)
| Họ và tên thành viên | MSSV | Vai trò | Phân công chính Tuần 5 (Middleware / Automation) | Thời lượng |
| :--- | :---: | :---: | :--- | :---: |
| **Nguyễn Vĩnh Khang** | 2001230381 | Trưởng nhóm | Thiết kế Finite State Machine (FSM), Watchdog Heartbeat Timeout, Night Mode Scheduler (Rule 4, 5) | 6.0 giờ |
| **Nguyễn Văn Đức** | 2001230186 | Thành viên | Xây dựng luồng Flow Node-RED, Logic phân ngưỡng khói & nhiệt độ (Rule 1, 2), Thuật toán Hysteresis Cooldown (Rule 3) | 6.0 giờ |
| **Nguyễn Văn Mãnh** | 2001230503 | Thành viên | Xây dựng Event History Logger (Audit Trail), Command Downlink Dispatcher, Kịch bản kiểm thử tự động & Báo cáo | 6.0 giờ |
| **Tổng cộng** | | | **Tổng thời lượng thực hiện của nhóm (100% hoàn thành)** | **18.0 giờ** |

---

### 1. PHÂN TÍCH TỔNG QUAN & KẾ HOẠCH TRIỂN KHAI TUẦN 5

#### 1.1. Mục tiêu kỹ thuật Tuần 5 (Tầng 3 – Middleware / Automation Engine)
Theo đúng kế hoạch 10 tuần, Tuần 5 đóng vai trò xây dựng "bộ não điều phối trung tâm" (Automation Engine) tại Tầng 3 - Middleware. Sau khi thiết bị ESP32 đã kết nối mạng hai chiều thành công qua MQTT ở Milestone M2 (Tuần 4), Tầng 3 có nhiệm vụ tiếp nhận dữ liệu cảm biến, phân tích theo thời gian thực, quản lý trạng thái hệ thống và tự động ra quyết định điều khiển trả ngược lại thiết bị chấp hành.

**Nguyên tắc nghiệm thu cốt lõi của Bộ môn:**
> *"Middleware phải thực hiện xử lý, không chỉ forward dữ liệu."*

Để đạt và vượt yêu cầu này, nhóm triển khai nền tảng **Node-RED** kết hợp với **MQTT Broker (broker.emqx.io)** nhằm hiện thực hóa 5 mục tiêu kỹ thuật then chốt:
1. **Event-driven Flow:** Tiếp nhận dữ liệu từ các Topic MQTT chuẩn (`smoke/telemetry`, `smoke/event/alarm`, `smoke/status`, `smoke/lwt`), giải mã JSON, tiền xử lý và kiểm định tính hợp lệ.
2. **Finite State Machine (FSM):** Quản lý 5 trạng thái vận hành của toàn bộ hệ sinh thái báo khói: `SAFE` (An toàn), `WARNING` (Cảnh giác), `ALARM` (Báo động khẩn), `COOLDOWN` (Làm mát & xả khói) và `OFFLINE` (Mất kết nối trạm cảm biến).
3. **5 Quy tắc tự động hóa cốt lõi (Core Automation Rules):**
   - **Rule 1 (Smoke Hazard):** Ngưỡng nồng độ khói vượt mức kích hoạt còi, quạt và phát lệnh Downlink.
   - **Rule 2 (Thermal Hazard):** Cảnh báo nhiệt độ cao hoặc tốc độ gia nhiệt bất thường từ DHT22.
   - **Rule 3 (Anti-chattering Hysteresis):** Cơ chế trễ 20 giây làm mát trước khi tắt quạt, ngăn hồ quang phá hủy tiếp điểm Relay.
   - **Rule 4 (Night Sensitivity Scheduler):** Tự động chuyển đổi ngưỡng báo động theo thời gian thực (tăng độ nhạy vào ban đêm 22h-06h).
   - **Rule 5 (Heartbeat Watchdog):** Giám sát nhịp tim cảm biến, phát hiện đứt kết nối quá 10 giây hoặc qua tín hiệu LWT.
4. **Logging & Event History (Audit Trail):** Ghi nhật ký đa tầng: bộ đệm vòng 50 sự kiện trên giao diện và ghi nối tiếp vào tập tin `logs/event_history.log` bền vững.
5. **Command Downlink Dispatcher:** Điều phối lệnh điều khiển chuẩn hóa gửi trả xuống ESP32 (`smoke/cmd/fan`, `smoke/cmd/buzzer`).

#### 1.2. Phân bổ khung thời gian 6 giờ thực hiện chi tiết
- **Khung H1 – H3 (3h):** Thiết kế kiến trúc Flow & Triển khai Node-RED Middleware (cấu hình Broker, topic MQTT In, các hàm Parse JSON).
- **Khung H4 – H5 (2h):** Lập trình Threshold, Scheduler, Hysteresis, Watchdog & FSM Engine.
- **Khung H6 (1h):** Xây dựng Logging, Command Feedback, Rate Limiting chống spam tin nhắn, kiểm thử tự động và hoàn thiện tài liệu nghiệm thu.

---

### 2. KIẾN TRÚC TẦNG 3 TRONG MÔ HÌNH IOT 4 TẦNG

```
+-------------------------------------------------------------------------+
|           TẦNG 1: SENSING / ACTUATION (ESP32 Wokwi Node)                 |
+-------------------------------------------------------------------------+
      | (Uplink Telemetry/Alarm)             ^ (Downlink Commands)
      v                                      | (Fan/Buzzer Action)
+-------------------------------------------------------------------------+
|           TẦNG 2: NETWORK (MQTT Broker - broker.emqx.io:1883)            |
+-------------------------------------------------------------------------+
      | (MQTT Sub: smoke/#)                  ^ (MQTT Pub: smoke/cmd/*)
      v                                      |
+-------------------------------------------------------------------------+
|           TẦNG 3: MIDDLEWARE ENGINE (Node-RED Automation)               |
|                                                                         |
|  [1. Packet Decoder & Validator] --> Chuyển đổi JSON, kiểm tra hợp lệ   |
|  [2. Finite State Machine (FSM)] --> SAFE <-> WARN <-> ALARM <-> COOLDOWN|
|  [3. Automation Rule Evaluator]  --> 5 Core Rules (PPM, Temp, Hysteresis)|
|  [4. Night Mode Scheduler]       --> Tự động đổi ngưỡng nhạy ban đêm    |
|  [5. Heartbeat Watchdog Engine]  --> Bắt timeout > 10s hoặc LWT Offline |
|  [6. Audit Logger & Rate Limiter]--> Ghi file log, chống spam tin nhắn   |
|  [7. Command Dispatcher]         --> Định dạng lệnh gửi trả ESP32        |
+-------------------------------------------------------------------------+
      |                                      ^
      v                                      | (Manual Override Action)
+-------------------------------------------------------------------------+
|           TẦNG 4: APPLICATION (Node-RED Dashboard / Alerting)            |
+-------------------------------------------------------------------------+
```

---

### 3. THIẾT KẾ MÁY TRẠNG THÁI HỮU HẠN (FINITE STATE MACHINE - FSM)

| Trạng thái (State) | Ý nghĩa nghiệp vụ | Điều kiện kích hoạt (Entry Condition) | Hành vi thiết bị chấp hành | Trạng thái kế tiếp |
| :--- | :--- | :--- | :--- | :--- |
| **SAFE** | Môi trường an toàn, thông số bình thường | PPM < 250 PPM & Nhiệt độ < 50°C | Quạt: TẮT, Còi: TẮT | WARNING, ALARM, OFFLINE |
| **WARNING** | Chớm xuất hiện khói hoặc nhiệt độ cao | 250 PPM <= PPM < 400 PPM hoặc Nhiệt độ >= 55°C | Quạt: TẮT, Còi: TẮT, Ghi log cảnh báo | SAFE, ALARM, OFFLINE |
| **ALARM** | Báo động khẩn cấp có khói dày đặc | PPM >= 400 PPM hoặc nhận `URGENT_ALARM` | Quạt: BẬT, Còi: HÚ, Bắn tin cảnh báo | COOLDOWN, OFFLINE |
| **COOLDOWN** | Giai đoạn làm mát & xả khói tồn dư | Đang ở ALARM và PPM hạ xuống < 300 PPM | Quạt: DUY TRÌ BẬT trong 20s trễ Hysteresis | SAFE (hết trễ), ALARM (nếu khói tăng lại) |
| **OFFLINE** | Mất kết nối với trạm cảm biến ESP32 | Quá 10s không nhận Telemetry hoặc nhận LWT offline | Giữ nguyên trạng thái an toàn, phát cảnh báo đứt mạng | SAFE (khi có kết nối lại) |

---

### 4. ĐẶC TẢ 5 QUY TẮC TỰ ĐỘNG HÓA CỐT LÕI (CORE AUTOMATION RULES)

#### 4.1. Quy tắc 1 (Rule 1): Khói vượt ngưỡng & Kích hoạt Downlink khẩn cấp
- **Điều kiện:** Nồng độ khói PPM >= `ALARM_THRESHOLD` (400 PPM ở chế độ thường, 350 PPM ở chế độ ban đêm) hoặc nhận sự kiện tức thời `smoke/event/alarm`.
- **Hành động:**
  1. Chuyển trạng thái FSM sang `ALARM`.
  2. Tạo bản ghi Audit Log mức `CRITICAL` (sự kiện `SMOKE_ALARM_TRIGGERED`).
  3. Gửi đồng thời 2 lệnh Downlink qua MQTT:
     - `smoke/cmd/fan`: `{"action":"ON","reason":"RULE_1_SMOKE_ALARM","ppm":ppm}`
     - `smoke/cmd/buzzer`: `{"action":"UNMUTE","reason":"RULE_1_SMOKE_ALARM"}`
  4. Đẩy tin cảnh báo khẩn cấp tới Dashboard/Telegram với bộ lọc Rate Limiting.

#### 4.2. Quy tắc 2 (Rule 2): Cảnh báo quá nhiệt & Tốc độ gia nhiệt bất thường
- **Ngưỡng tĩnh:** Nếu Nhiệt độ môi trường >= 55.0°C -> Ghi log cảnh báo `HEAT_OVERHEAT` mức `WARN`, chuyển trạng thái FSM sang `WARNING`.
- **Tốc độ gia nhiệt động (Rate-of-Rise dT/dt):** Nếu trong khoảng thời gian >= 30s mà tốc độ tăng nhiệt độ dT/dt >= 5.0°C/phút -> Phát cảnh báo `HEAT_RAPID_RISE` giúp phát hiện cháy sớm ngay cả khi khói chưa bốc lên.

#### 4.3. Quy tắc 3 (Rule 3): Hysteresis & Cooldown tự động tắt quạt (Anti-chattering)
- **Vấn đề kỹ thuật:** Nếu chỉ có 1 ngưỡng (400 PPM), khi khói chao đảo quanh mức 400 PPM do gió, Relay quạt sẽ bị bật/tắt liên tục (Chattering), sinh tia lửa điện gây cháy motor và hỏng tiếp điểm.
- **Giải pháp:**
  - Vùng đệm trễ Hysteresis: Quạt bật khi >= 400 PPM, nhưng chỉ bắt đầu xem xét tắt khi PPM < 300 PPM (vùng đệm 100 PPM).
  - Cooldown Timer 20s: Khi khói < 300 PPM, chuyển sang `COOLDOWN` và duy trì quạt chạy thêm 20 giây để hút hết khí độc tồn dư.
  - Re-escalation Guard: Nếu khói tăng lại >= 300 PPM trong lúc đang đếm lùi, quá trình Cooldown bị hủy bỏ ngay lập tức, FSM quay lại `ALARM`.
  - Hết 20s an toàn: FSM về `SAFE` và phát lệnh Downlink tắt quạt `{"action":"OFF"}`.

#### 4.4. Quy tắc 4 (Rule 4): Bộ lập lịch tự động thay đổi độ nhạy ban đêm (Night Scheduler)
- **Khung giờ đêm (22:00 – 06:00):** Tự động chuyển `sensitivityMode = 'NIGHT'`, hạ ngưỡng báo động từ 400 PPM xuống 350 PPM, hạ ngưỡng an toàn từ 300 PPM xuống 250 PPM để bảo vệ người dân khi đang ngủ.
- **Khung giờ ngày (06:00 – 22:00):** Tự động trả về `sensitivityMode = 'NORMAL'` (ngưỡng 400 PPM) tránh báo động giả khi nấu nướng.

#### 4.5. Quy tắc 5 (Rule 5): Giám sát nhịp tim cảm biến (Heartbeat Watchdog & LWT)
- Chu kỳ kiểm tra 3 giây một lần: Nếu `now - lastSeen > 10000ms` (quá 10s không có dữ liệu) -> FSM chuyển sang `OFFLINE`, ghi log lỗi `HEARTBEAT_TIMEOUT`.
- Xử lý Last Will and Testament (LWT): Nhận `smoke/lwt` = `"offline"` -> FSM chuyển `OFFLINE` ngay lập tức.

---

### 5. CƠ CHẾ GHI NHẬT KÝ SỰ KIỆN (LOGGING & EVENT HISTORY - AUDIT TRAIL)

#### 5.1. Định dạng JSON có cấu trúc
```json
{
  "time": "19:15:30 05/10/2026",
  "level": "CRITICAL",
  "event": "SMOKE_ALARM_TRIGGERED",
  "desc": "Khói vượt ngưỡng (462.8 PPM >= 400.0 PPM). Kích hoạt còi và quạt hút!",
  "fsmState": "ALARM"
}
```

#### 5.2. Hai tầng lưu trữ
1. **In-memory Circular Buffer (50 mục):** Lưu trữ 50 sự kiện gần nhất trong flow context của Node-RED, hiển thị tức thì lên bảng giao diện Dashboard.
2. **Persistent File Append:** Ghi nối tiếp vào tập tin `logs/event_history.log` theo chuẩn ISO 8601, đóng vai trò "hộp đen" phục vụ điều tra PCCC.

#### 5.3. Rate Limiting chống bão tin nhắn
Giới hạn tối đa 1 thông điệp cảnh báo đẩy trong mỗi cửa sổ 30 giây khi nồng độ khói duy trì liên tục ở mức nguy cấp.

---

### 6. PHÂN TÍCH NGUY CƠ BẢO MẬT TẦNG 3 MIDDLEWARE (THEO SLIDE 12 & 21)

Căn cứ tài liệu bài giảng *"An toàn và Bảo mật IoT"* (ThS. Võ Hoàng Hải), Nhóm 09 phân tích và thiết lập các chốt chặn phòng thủ cho Tầng 3 Middleware:

| Nguy cơ (Slide 12 & 21) | Nhóm nguy cơ (Slide 12) | Yêu cầu an toàn | Kịch bản rủi ro trên Hệ thống Báo khói | Biện pháp kỹ thuật đã triển khai tại Tầng 3 |
| :--- | :--- | :--- | :--- | :--- |
| **Giả mạo dữ liệu PPM (Manipulate Sensor Data)** | Manipulate | Integrity | Kẻ tấn công gửi gói tin MQTT chứa `ppm: 10.0` khi phòng đang cháy thật -> Middleware không báo động (*Suppressed Alarm*). | Kiểm tra Schema JSON, Range Check miền giá trị (0 - 10.000 PPM); xác thực định danh thiết bị; đối chiếu chéo với cảm biến nhiệt DHT22. |
| **Bão tin nhắn cảnh báo (Alarm Flooding DoS)** | Disrupt | Availability | Tấn công bơm hàng nghìn tin cảnh báo/giây làm tắc nghẽn hàng đợi Node-RED và sập kênh thông báo. | Áp dụng thuật toán **Rate Limiting 30s**: Trong 30s chỉ cho phép đẩy tối đa 1 cảnh báo nguy cấp; cơ chế In-memory buffer giới hạn 50 mục. |
| **Tấn công dao động rơ-le (Relay Chattering Attack)** | Disrupt | Availability | Gửi nồng độ khói dao động quanh ngưỡng (399 <-> 401 PPM) làm rơ-le đóng ngắt liên tục gây cháy cuộn hút. | **Rule 3 - Hysteresis & Cooldown Trễ 20s**: Khi khói hạ dưới 300 PPM, FSM phải duy trì quạt thêm đúng 20 giây mới được tắt. |
| **Nút mạng giả mạo (Fake Sensor Node Injection)** | Manipulate | Authenticity | Cắm thêm ESP32 lạ vào mạng để phát thông tin rác hoặc gây nhiễu loạn logic điều phối. | **Fleet Device Whitelist**: Node-RED kiểm tra danh sách MAC/ID hợp lệ (`N09_SMOKE_DEV01`), lập tức DROP và ghi cảnh báo bảo mật nếu phát hiện Node lạ. |

---

### 7. CÁC TÀI LIỆU & MÃ NGUỒN NGHIỆM THU ĐÃ XUẤT BẢN

1. **File cấu hình Node-RED Flow:** `nodered/flows_smoke_detector.json` (29 nodes hoàn chỉnh, có thể Import 1-click vào Node-RED).
2. **Kịch bản kiểm thử tự động:** `test_middleware_simulator.py` (chạy kiểm thử tự động 12 test cases mô phỏng ESP32 và MQTT Broker).
3. **Báo cáo tiến độ chuẩn Word:** `docs/word/Phần 5.docx` (soạn thảo theo chuẩn học thuật HUIT, đầy đủ hình vẽ, bảng biểu, ma trận nguy cơ bảo mật Slide 12 & 21).
4. **Bảng kịch bản kiểm thử chuẩn Word:** `docs/word/Bang_Test_Case_Tuan5_Nhom04.docx` (12 test cases chi tiết, tỷ lệ Pass 100%).
5. **Hướng dẫn cài đặt & vận hành:** `docs/md/Huong_Dan_Cai_Dat_Va_Chay_NodeRED_Tuan5.md`.

---

### 8. KẾT LUẬN NGHIỆM THU MILESTONE TUẦN 5
Toàn bộ yêu cầu kỹ thuật, thời lượng 6 giờ/sinh viên (18h/nhóm) và điều kiện nghiệm thu "Middleware phải thực hiện xử lý, không chỉ forward dữ liệu" theo quy định của Kế hoạch 10 tuần – 60 giờ đã được Nhóm 09 hoàn thành 100%.

