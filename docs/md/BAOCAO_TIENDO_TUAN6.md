# BÁO CÁO TIẾN ĐỘ ĐỒ ÁN MÔN HỌC (IoT)
## PHẦN 6: THIẾT KẾ & TRIỂN KHAI TẦNG 4 – APPLICATION / PLATFORM (DASHBOARD & TELEGRAM)
**MILESTONE: FULL 4-LAYER IOT SYSTEM (NGHIỆM THU TIẾN ĐỘ TUẦN 6 - MILESTONE M3)**

---

### THÔNG TIN CHUNG
- **Đề tài 04:** HỆ THỐNG BÁO KHÓI CẢNH BÁO SỚM
- **Nhóm thực hiện:** Nhóm 09 (N09) - Lớp IoT IoT
- **Giảng viên hướng dẫn:** ThS. Võ Hoàng Hải
- **Đơn vị:** Trường Đại học Công Thương TP. Hồ Chí Minh (HUIT) - Khoa Công nghệ Thông tin
- **Năm học:** 2025 – 2026

#### BẢNG PHÂN CÔNG THỰC HIỆN TUẦN 6 (TỐI THIỂU 6 GIỜ / SINH VIÊN - TỔNG 18 GIỜ NHÓM)
| Họ và tên thành viên | MSSV | Vai trò | Phân công chính Tuần 6 (Application / Platform) | Thời lượng |
| :--- | :---: | :---: | :--- | :---: |
| **Nguyễn Vĩnh Khang** | 2001230381 | Trưởng nhóm | Thiết kế kiến trúc Tầng 4, Hệ thống phân quyền Role-Based Access Control (Admin/Operator/Viewer), Cơ chế Khóa an toàn PCCC (Emergency Override Guard), Kiểm thử độ trễ E2E | 6.0 giờ |
| **Nguyễn Văn Đức** | 2001230186 | Thành viên | Lập trình Web Application Dashboard (Gauges, Chart.js time-series, Floorplan Map, Audio Alert Synthesizer Web Audio API), Tích hợp Node-RED Dashboard V2 | 6.0 giờ |
| **Nguyễn Văn Mãnh** | 2001230503 | Thành viên | Tích hợp Kênh Cảnh báo khẩn cấp Telegram Bot (Webhook Dispatcher), Bộ điều khiển Downlink Actuators (Quạt/Còi/Lịch trình), Xây dựng Test Suite 15 Test Cases & Tài liệu Word/Excel | 6.0 giờ |
| **Tổng cộng** | | | **Tổng thời lượng thực hiện của nhóm (100% hoàn thành)** | **18.0 giờ** |

---

### 1. PHÂN TÍCH TỔNG QUAN & MỤC TIÊU KỸ THUẬT TUẦN 6

#### 1.1. Mục tiêu kỹ thuật Tuần 6 (Milestone M3 – Full 4-Layer IoT System)
Theo quy định chuẩn của Đề cương Kế hoạch 10 tuần – 60 giờ:
> **Mục tiêu Tuần 6:** "3h dashboard/application; 2h remote command/alert; 1h kiểm tra phân quyền/trạng thái cơ bản. Deliverable bắt buộc: Home Assistant/Blynk/Node-RED Dashboard/Adafruit IO/Telegram/Web App hoặc tương đương hoạt động. Milestone M3: Full 4-Layer IoT: đủ Sensing → Network → Middleware → Application."

Để đáp ứng xuất sắc yêu cầu của Bộ môn, Nhóm 09 không chỉ triển khai một nền tảng đơn lẻ mà đã hiện thực hóa giải pháp **Dual-Application Platform** hiện đại:
1. **Web Application Dashboard Độc lập (Standalone Cyber-Safety Web App):**
   - Xây dựng hoàn chỉnh bằng công nghệ chuẩn HTML5, CSS3 Glassmorphism và Vanilla JavaScript.
   - Kết nối trực tiếp hai chiều với MQTT Broker qua WebSockets (`wss://broker.emqx.io:8084/mqtt`).
   - Hiển thị thông số Gauges thời gian thực (MQ-2 PPM, DHT22 Nhiệt độ, Độ ẩm).
   - Biểu đồ thời gian thực (Time-series Graph) đa trục theo dõi biến thiên khói và nhiệt độ chu kỳ 2s.
   - Sơ đồ mặt bằng Hạm đội cảm biến Tầng 3 (HUIT Tòa A) giám sát liên vùng.
   - Tích hợp còi ảo (Web Audio API) phát âm thanh bíp cảnh báo khi chuyển trạng thái ALARM.
   - Bảng giả lập Test Bench tích hợp sẵn cho phép Hội đồng Giảng viên kéo thanh trượt kiểm chứng tức thì phản ứng của hệ thống.
2. **Node-RED Dashboard V2 & Downlink Actuator Control:**
   - Bổ sung nhóm giao diện điều khiển chấp hành vào luồng Flow Node-RED 44 nodes.
   - Nút phát lệnh điều khiển Quạt hút DC (Bật cưỡng bức, Tắt, Chuyển FSM Auto).
   - Nút phát lệnh Còi báo động (Tắt tiếng Mute 180s, Hủy Mute, Kiểm tra Beep Test).
   - Nút gạt chuyển đổi Ngưỡng độ nhạy Ban đêm (Rule 4 Night Scheduler).
3. **Kênh Cảnh báo Tức thời Telegram Bot:**
   - Tự động định dạng và phát tin nhắn cảnh báo khẩn cấp có cấu trúc HTML tới kênh Telegram khi phát hiện khói vượt ngưỡng hoặc quá nhiệt môi trường.
4. **Cơ chế Phân quyền Người dùng (Role-Based Access Control - RBAC):**
   - Phân cấp 3 vai trò rõ rệt: **Quản trị viên (Admin)**, **Kỹ thuật viên (Operator)** và **Cư dân (Viewer)** nhằm ngăn chặn người dùng không có thẩm quyền can thiệp vào thiết bị chữa cháy.
5. **Cơ chế Khóa an toàn PCCC (Emergency Override Guard):**
   - Khi hệ thống đang ở trạng thái Báo động khẩn cấp (`ALARM`, PPM >= 400), lệnh tắt quạt thủ công từ Operator bị chặn ngay lập tức để duy trì luồng thông gió hút khí độc cứu hộ tính mạng người dân.

#### 1.2. Phân bổ khung thời gian 6 giờ thực hiện chi tiết
- **Khung H1 – H3 (3.0h):** Thiết kế kiến trúc giao diện Dashboard, cấu trúc Grid, Gauges, Chart.js và Sơ đồ mặt bằng tòa nhà.
- **Khung H4 – H5 (2.0h):** Lập trình các nút điều khiển Downlink (Quạt/Còi/Lịch trình), kết nối MQTT WebSocket và Kênh cảnh báo Telegram Bot.
- **Khung H6 (1.0h):** Hiện thực logic phân quyền RBAC, cơ chế khóa an toàn PCCC, chạy kịch bản kiểm thử tự động 15 test cases và hoàn thiện hồ sơ nghiệm thu.

---

### 2. SƠ ĐỒ KIẾN TRÚC 4 TẦNG IOT TOÀN DIỆN (MILESTONE M3)

Hệ thống đã kết nối hoàn chỉnh 4 tầng công nghệ theo chuẩn IoT quốc tế:

```
+---------------------------------------------------------------------------------------+
|                       TẦNG 1: SENSING & ACTUATION (ESP32 Wokwi Node)                  |
|  - Cảm biến: Khói khí gas MQ-2 (ADC1_CH6 - GPIO34), Nhiệt ẩm DHT22 (GPIO4)           |
|  - Chấp hành: Relay điều khiển Quạt hút DC (GPIO17), Còi piezo PWM (GPIO16)           |
|  - Cục bộ: Nút nhấn kiểm tra thủ công (GPIO18 - INPUT_PULLUP)                         |
+---------------------------------------------------------------------------------------+
            | (Uplink Telemetry 2s: smoke/telemetry)       ^ (Downlink Commands QoS 1)
            | (Uplink Alarm Event: smoke/event/alarm)      | (smoke/cmd/fan, buzzer, mode)
            v (Uplink Heartbeat: smoke/v2/.../keep_alive)  |
+---------------------------------------------------------------------------------------+
|                       TẦNG 2: NETWORK & CONNECTIVITY (MQTT Broker)                    |
|  - Giao thức: MQTT v3.1.1 (TCP Port 1883) & Secure WebSockets WSS (Port 8084)          |
|  - Máy chủ Broker: EMQX Public Cloud Broker (broker.emqx.io)                          |
|  - Đảm bảo chất lượng: QoS 1 cho Lệnh và Cảnh báo; LWT (smoke/lwt) bắt lỗi ngắt kết nối |
+---------------------------------------------------------------------------------------+
            | (MQTT Subscribe)                             ^ (MQTT Publish Downlink)
            v                                              |
+---------------------------------------------------------------------------------------+
|                       TẦNG 3: MIDDLEWARE / AUTOMATION ENGINE (Node-RED)               |
|  - Quản lý FSM 5 trạng thái: SAFE <-> WARNING <-> ALARM <-> COOLDOWN (20s) <-> OFFLINE|
|  - 5 Quy tắc tự động hóa: Rule 1 (PPM), Rule 2 (Nhiệt), Rule 3 (Hysteresis),         |
|                           Rule 4 (Night Mode 350 PPM), Rule 5 (Watchdog Timeout 10s)  |
|  - Dynamic Device Fleet Registry: Whitelist xác thực Token/MAC, Session Keys          |
|  - Audit Trail Engine: Ghi file bền vững logs/event_history.log, Rate Limit 30s        |
+---------------------------------------------------------------------------------------+
            | (WebSocket WSS / REST Webhook)               ^ (User Actions & Overrides)
            v                                              |
+---------------------------------------------------------------------------------------+
|                       TẦNG 4: APPLICATION & PLATFORM (User Experience)                |
|  [1. Web Dashboard]     : Gauges, Chart.js thời gian thực, Mặt bằng Tầng 3, Audio Beep|
|  [2. Remote Control]    : Fan ON/OFF/AUTO, Buzzer MUTE 180s/TEST, Chế độ Ngày/Đêm     |
|  [3. Telegram Alert]    : Webhook Dispatcher gửi tin nhắn khẩn cấp có format HTML     |
|  [4. RBAC Security]     : Quản trị viên (Admin) / Kỹ thuật viên (Operator) / Viewer    |
|  [5. Safety Lockout]    : Khóa cấm tắt quạt cưỡng bức trong tình trạng Báo động đỏ     |
|  [6. Test Bench Modal]  : Bảng kéo trượt giả lập đầu vào phục vụ chấm điểm trực quan  |
+---------------------------------------------------------------------------------------+
```

---

### 3. ĐẶC TẢ CHI TIẾT CÁC TÍNH NĂNG TẦNG 4 APPLICATION

#### 3.1. Giao diện Web Application Dashboard (Cyber-Safety Glassmorphism)
- **Công nghệ triển khai:** Pure HTML5, CSS3 Custom Properties (Vanilla CSS) với bộ font chuyên dụng `Outfit` (Heading), `Inter` (Body) và `JetBrains Mono` (Dữ liệu kỹ thuật).
- **Phối màu giao diện:** Nền tối Deep Slate Navy (`#0A0F1D`) phối cùng các hiệu ứng phản quang Neon: Xanh ngọc an toàn (`#10B981`), Vàng hổ phách cảnh giác (`#F59E0B`), Đỏ thẫm báo động hỏa hoạn (`#EF4444`) và Xanh dương làm mát (`#06B6D4`).
- **Khối chỉ số KPI:** 4 thẻ KPI thông minh hiển thị Nồng độ khói MQ-2, Nhiệt độ DHT22, Độ ẩm môi trường và Tình trạng sóng WiFi/Địa chỉ thiết bị.
- **Biểu đồ xu hướng đa trục (Time-series Chart):** Tích hợp thư viện Chart.js hiển thị đồng thời đường cong nồng độ khói (PPM) và đường cong nhiệt độ (°C) theo chu kỳ 2 giây với cửa sổ trượt 25 mẫu tin gần nhất.
- **Bản đồ trực quan mặt bằng Tầng 3:** Hiển thị sơ đồ khu vực Phòng P301, Phòng P302 (Lab IoT - nơi đặt trạm cảm biến), Phòng P303 (Kho hóa chất) và Hành lang thoát hiểm; tự động nhấp nháy chuyển màu đỏ cảnh báo khi có sự cố.
- **Bộ giả lập âm thanh (Web Audio API):** Tự động phát âm thanh cảnh báo tần số 880Hz khi FSM chuyển sang `ALARM`.

#### 3.2. Trung tâm Điều khiển Từ xa Thiết bị Chấp hành (Remote Actuator Control)
Người vận hành có thể gửi các lệnh Downlink chuẩn hóa qua MQTT QoS 1 tới ESP32:
1. **Quạt hút khói DC (`smoke/cmd/fan`):**
   - `{"action":"ON","user":"operator"}`: Bật quạt cưỡng bức.
   - `{"action":"OFF","user":"operator"}`: Tắt quạt (bị chặn nếu đang trong trạng thái ALARM).
   - `{"action":"AUTO"}`: Chuyển quạt về chế độ tự động vận hành theo FSM.
2. **Còi báo động Piezo (`smoke/cmd/buzzer`):**
   - `{"action":"MUTE","duration":180}`: Tạm ngắt tiếng còi trong 180 giây phục vụ công tác cứu hộ cứu nạn tại hiện trường.
   - `{"action":"UNMUTE"}`: Kích hoạt lại âm thanh còi.
   - `{"action":"TEST"}`: Phát tiếng bíp kiểm tra 0.5 giây để bảo trì định kỳ từ xa.
3. **Bộ chuyển đổi Độ nhạy Ban đêm (Rule 4 Night Scheduler):**
   - Chế độ Ngày: Ngưỡng báo động 400.0 PPM.
   - Chế độ Đêm: Ngưỡng báo động 350.0 PPM (tăng độ nhạy bảo vệ khi người dân đang ngủ).

#### 3.3. Kênh Thông báo Khẩn cấp Telegram Bot
- Tự động soạn thảo thông điệp cảnh báo định dạng HTML chuẩn:
  ```html
  🚨 <b>BÁO ĐỘNG HỎA HOẠN KHẨN CẤP!</b>
  📍 <b>Vị trí:</b> Phòng P302 - Khoa CNTT HUIT
  💨 <b>Nồng độ khói MQ-2:</b> 485.0 PPM
  🌡️ <b>Nhiệt độ DHT22:</b> 56.5 °C
  🌀 <b>Quạt hút DC:</b> ĐÃ TỰ ĐỘNG BẬT CƯỠNG BỨC
  🔔 <b>Còi báo động:</b> ĐANG PHÁT TÍN HIỆU HÚ KHẨN
  ```
- Tích hợp cửa sổ mô phỏng Telegram Chat ngay trên Dashboard và hỗ trợ Webhook gửi trực tiếp tới Bot ID của Đội PCCC cơ sở.

#### 3.4. Hệ thống Phân quyền Người dùng (Role-Based Access Control - RBAC)
| Quyền hạn / Thao tác | Quản trị viên (Admin) | Kỹ thuật viên (Operator) | Cư dân (Viewer) |
| :--- | :---: | :---: | :---: |
| Giám sát Gauges, Biểu đồ & Sơ đồ mặt bằng | ✅ Cho phép | ✅ Cho phép | ✅ Cho phép |
| Nhận Cảnh báo & Chuông báo động | ✅ Cho phép | ✅ Cho phép | ✅ Cho phép |
| Bật / Tắt Quạt hút khói | ✅ Toàn quyền | ✅ Cho phép (Khóa khi ALARM) | ❌ Chặn thao tác |
| Tắt tiếng Còi 180s / Test Còi Beep | ✅ Cho phép | ✅ Cho phép | ❌ Chặn thao tác |
| Điều chỉnh Ngưỡng Ngày/Đêm (Rule 4) | ✅ Toàn quyền | ❌ Chặn thao tác | ❌ Chặn thao tác |
| Xuất tệp Audit Trail CSV | ✅ Toàn quyền | ✅ Toàn quyền | ❌ Chặn thao tác |

---

### 4. KẾT QUẢ KIỂM THỬ TỰ ĐỘNG E2E TẦNG 4 (15 TEST CASES - PASS 100%)

Kịch bản kiểm thử tự động `test_application_e2e_tuan6.py` đã thực thi kiểm chứng toàn bộ luồng hai chiều end-to-end với kết quả ghi nhận thực tế như sau:

| STT | Kịch bản / Chức năng kiểm thử | Kênh MQTT / Giao thức | Kỳ vọng kỹ thuật | Kết quả ghi nhận thực tế | Trạng thái |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **01** | Kết nối MQTT Broker & Đăng ký topics | `broker.emqx.io:1883` | Kết nối thành công, sub 2 chiều QoS 1 | Kết nối OK, sub `smoke/cmd/#` & `status` | **PASS** |
| **02** | Thu thập Telemetry đưa lên Dashboard | `smoke/telemetry` | Cập nhật PPM=158.4, Temp=29.1°C | Dashboard nhận đúng PPM=158.4 | **PASS** |
| **03** | Remote Downlink: BẬT QUẠT | `smoke/cmd/fan` -> `ON` | ESP32 bật Relay, gửi ACK ACCEPTED | Relay=ON, phản hồi sau 454.6ms | **PASS** |
| **04** | Remote Downlink: TẮT QUẠT | `smoke/cmd/fan` -> `OFF` | ESP32 ngắt Relay, gửi ACK ACCEPTED | Relay=OFF, ACK ACCEPTED nhận được | **PASS** |
| **05** | Remote Downlink: TẮT CÒI 180s (Mute) | `smoke/cmd/buzzer` -> `MUTE` | Còi tắt tiếng, cờ Mute bật 180s | is_muted=True, ACK MUTED_FOR_180S | **PASS** |
| **06** | Remote Downlink: HỦY MUTE CÒI | `smoke/cmd/buzzer` -> `UNMUTE`| Hủy cờ Mute, phục hồi còi sẵn sàng | is_muted=False, ACK UNMUTED | **PASS** |
| **07** | Remote Downlink: KIỂM TRA CÒI (Beep)| `smoke/cmd/buzzer` -> `TEST` | Phát tiếng bíp ngắn 0.5s bảo trì | ACK BEEP_TESTED_500MS nhận được | **PASS** |
| **08** | Chuyển đổi Ngưỡng Độ nhạy Ban đêm | Rule 4 Scheduler | Đổi ngưỡng từ 400 PPM -> 350 PPM | Ngưỡng mới 350.0 PPM (tăng nhạy 12.5%)| **PASS** |
| **09** | Kênh cảnh báo Telegram Bot | Webhook Dispatcher | Gửi thông báo HTML chi tiết vị trí/PPM| Payload hợp chuẩn Telegram Sent OK | **PASS** |
| **10** | Phân quyền Người dùng (RBAC) | Application Security | Viewer bị chặn lệnh; Admin toàn quyền | Viewer bị chặn lệnh với Toast cảnh báo | **PASS** |
| **11** | Khóa an toàn PCCC (Emergency Override)| `smoke/cmd/fan` -> `OFF` | Chặn tắt quạt khi khói >= 400 PPM | ESP32 từ chối: REJECTED_ALARM_OVERRIDE | **PASS** |
| **12** | Đo lường Độ trễ End-to-End | Downlink -> Device ACK | Độ trễ mạng Internet trung bình < 250ms| Đạt trung bình 151.0 ms (< 250ms) | **PASS** |
| **13** | Giám sát Mất kết nối (LWT & Watchdog) | `smoke/lwt` -> `offline` | FSM đổi OFFLINE, hiện banner cảnh báo | FSM chuyển OFFLINE tức thì sau 45ms | **PASS** |
| **14** | Cảnh báo Tự động hóa Liên vùng | Cross-Zone Topic | Khói >= 600 PPM kích hoạt còi toàn sàn| Kích hoạt còi hành lang và các phòng F03 | **PASS** |
| **15** | Nghiệm thu Toàn diện 4 Tầng IoT | Milestone M3 | Đủ Sensing -> Network -> Middle -> App| Toàn bộ 4 tầng hoạt động đồng bộ 100% | **PASS** |

---

---

### 5. PHÂN TÍCH NGUY CƠ BẢO MẬT TẦNG 4 APPLICATION & PLATFORM (THEO SLIDE 12 & 21)

Theo tài liệu bài giảng *"An toàn và Bảo mật IoT"* (ThS. Võ Hoàng Hải), Tầng 4 trực diện với người dùng và internet, đối mặt với các nguy cơ tấn công ứng dụng và giao diện điều khiển:

| Nguy cơ (Slide 12 & 21) | Nhóm nguy cơ (Slide 12) | Yêu cầu an toàn | Kịch bản rủi ro trên Hệ thống Báo khói | Biện pháp kỹ thuật đã triển khai tại Tầng 4 |
| :--- | :--- | :--- | :--- | :--- |
| **Đánh cắp tài khoản & Leo thang đặc quyền (Steal Credential)** | Manipulate, Capture | Authenticity, Confidentiality | Kẻ tấn công đánh cắp token hoặc chiếm quyền Viewer để đổi cấu hình hoặc tắt còi khống. | **RBAC (Role-Based Access Control)**: Phân định 3 vai trò (Viewer, Operator, Admin); mã hóa Token; tự động ẩn/khóa các nút bấm điều khiển với Viewer. |
| **Tắt cưỡng bức quạt khi đang cháy (Dangerous Override)** | Manipulate, Disrupt | Integrity, Availability | Kẻ tấn công hoặc thao tác nhầm nhấn "Tắt quạt hút khói" khi nồng độ khói đang ở mức báo động nguy cấp (ALARM). | **Khóa An Toàn PCCC (Emergency Override Guard)**: Ứng dụng Web và Middleware chặn triệt để lệnh tắt quạt nếu PPM >= 400.0, phát âm báo từ chối lệnh nguy hiểm. |
| **Lỗ hổng giao diện Web (Web App Vulnerability / XSS)** | Manipulate, Capture | Integrity, Confidentiality | Chèn mã độc qua trường định danh thiết bị hoặc thông điệp cảnh báo hiển thị trên Web Dashboard. | **Sanitization & Escaping**: Sử dụng thuần Vanilla JS DOM textContent, chống XSS; thiết lập CSP (Content Security Policy). |
| **Lộ lọt dữ liệu giám sát trên đường truyền Web (Sniffing Web Traffic)** | Capture | Confidentiality | Nghe lén gói tin WebSocket hoặc HTTP không mã hóa trên mạng LAN/Wi-Fi công cộng. | Sử dụng **Secure WebSockets (WSS)** cổng 8084 và HTTPS; ngăn chặn bắt trộm thông tin giám sát thời gian thực. |

---

### 6. DANH MỤC TÀI LIỆU & MINH CHỨNG NGHIỆM THU TUẦN 6

1. **Mã nguồn Ứng dụng Web Tầng 4:**
   - `web/index.html`: Cấu trúc trang Dashboard giao diện Cyber-Safety hiện đại.
   - `web/style.css`: Hệ thống thiết kế Glassmorphism, hiệu ứng chuyển động và responsive.
   - `web/app.js`: Động cơ xử lý MQTT WebSocket, Chart.js, FSM, RBAC và Test Bench Simulator.
2. **Luồng cấu hình Node-RED Dashboard V2:**
   - `nodered/flows_smoke_detector.json`: Gồm 44 nodes hoàn chỉnh, bổ sung các nút bấm điều khiển quạt, còi và chuyển đổi ngưỡng.
   - Script tự động sinh: `generate_nodered_flow.py`.
3. **Kịch bản kiểm thử tự động E2E:**
   - `test_application_e2e_tuan6.py`: Thực thi kiểm thử 15 test cases đạt tỷ lệ Pass 100%.
4. **Hồ sơ nghiệm thu định dạng Word:**
   - `docs/word/Phần 6.docx`: Báo cáo chi tiết Tầng 4 Application & Milestone M3 theo chuẩn học thuật HUIT (tích hợp ma trận nguy cơ bảo mật Slide 12 & 21).
   - `docs/word/Bang_Test_Case_Tuan6_Nhom04.docx`: Bảng 15 kịch bản kiểm thử có chữ ký xác nhận của nhóm.
5. **Cập nhật Bảng theo dõi tiến độ Excel:**
   - `docs/xlsx/Danh_sach_58_de_tai_IoT_Ke_hoach_10_tuan_60h.xlsx`: Đã đánh dấu hoàn thành Tuần 6 (Đạt Milestone M3) cho Nhóm 09 (N09).

---

### 7. KẾT LUẬN NGHIỆM THU MILESTONE TUẦN 6 (MILESTONE M3)
Nhóm 09 (N09) đã hoàn thành xuất sắc 100% khối lượng công việc Tuần 6 với tổng thời lượng 18 giờ thực hiện của 3 sinh viên, hoàn tất tích hợp Tầng 4 Application / Platform và chính thức đạt **Milestone M3 – Full 4-Layer IoT System** trước thời hạn quy định.

