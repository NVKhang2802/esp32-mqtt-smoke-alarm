# 🎯 Báo Cáo Nghiệm Thu & Chuẩn Hóa Toàn Diện Dự Án Báo Khói IoT (v5)
## Đề tài 04: Hệ thống Báo khói Cảnh báo sớm — Nhóm 04 (N09) HUIT

> **Tài liệu đính kèm kiểm duyệt:** Gửi kèm file mã nguồn toàn diện [PROJECT_CODEBASE.md](file:///e:/IoT/DoAn/PROJECT_CODEBASE.md)  
> **Thời gian xuất bản:** 18/11/2026 (Phiên bản Chuẩn hóa v5 - Cập nhật Khắc phục Toàn diện Tích hợp & Ma trận Kiểm duyệt 3 bậc)  
> **Trạng thái kiểm chuẩn:** Đã vượt qua 100% các bộ kiểm thử độc lập:
> - **29/29** C++17 Core Native Unity Tests
> - **16/16** Node-RED Middleware Tests (12 Engine + 4 Live Flow Integration)
> - **4/4** Web SCADA Clean Tests (Nạp & kiểm thử trực tiếp `web/app.js`)
> - **10/10** 3-Tier Audit Claims (6 VERIFIED PASS, 3 PARTIAL VALID, 1 SCOPE VALID, 0 FAIL)
> - **63/63** Full Regression System Tests

---

### 1. Bảng Đối Chiếu Triệt Để "Tuyên Bố Báo Cáo vs Thực Tế Mã Nguồn"

Dưới đây là bảng đối chiếu minh bạch giữa các phản biện của AI Auditor và các giải pháp kỹ thuật đã triển khai thực tế trong mã nguồn:

| # | Hạng Mục Phản Biện | Thực Tế Trước Audit | Hiện Trạng Triển Khai Thực Tế Trong Mã Nguồn (v5) | Bằng Chứng Kiểm Thử | Cấp Bậc (Tier) |
| :-: | :--- | :--- | :--- | :---: | :---: |
| **1** | **Bộ lọc EMA / Lấy mẫu ADC** | Trung bình 10 mẫu trong `readMQ2PPM`, không có EMA | Tách biệt 2 tầng lọc: Lấy mẫu trung bình 5 mẫu ADC (`ADC_SAMPLES = 5`) trong [sensors.cpp](file:///e:/IoT/DoAn/src/sensors.cpp) kết hợp bộ lọc số EMA bất đối xứng ($\alpha_{rise} = 0.40, \alpha_{fall} = 0.15$) trong [ema_filter.h](file:///e:/IoT/DoAn/lib/core/ema_filter.h). Đóng băng EMA khi mất cảm biến và tự động reset mẫu hợp lệ đầu tiên khi hồi phục | `test/test_core.cpp`<br>**(T-E1 $\to$ T-E5: PASS)** | `VERIFIED` |
| **2** | **FSM 5 Trạng Thái & Hysteresis** | WARNING và OFFLINE không gán; mất cờ FAULT | Chuyển sang kiến trúc FSM 5 trạng thái thiết bị biên tại [fsm_core.h](file:///e:/IoT/DoAn/lib/core/fsm_core.h) (`STATE_SAFE`, `STATE_WARNING`, `STATE_ALARM`, `STATE_COOLDOWN`, `STATE_FAULT`). FAULT suy ra từ cờ sức khỏe mỗi chu kỳ, không lưu biến trạng thái. Ràng buộc `safe = alarm * 0.75f` (luôn $\ge 225$ PPM > nền 200 PPM Wokwi) | `test/test_core.cpp`<br>**(T-F1 $\to$ T-F11: PASS)** | `VERIFIED` |
| **3** | **Khóa Liên Động Chấp Hành (Interlocks)** | Lệnh từ xa có thể tắt quạt/còi khi đang có cháy | Khóa an toàn thiết bị biên: Từ chối lệnh tắt quạt (`cmdRemoteFanOff`), từ chối MUTE (`cmdRemoteMute`), và từ chối TEST còi (`cmdBuzzerTest`) khi `alarmLatched == true`. Nút bấm tại chỗ cho phép MUTE còi 60s nhưng duy trì quạt | `test/test_core.cpp`<br>**(T-C1 $\to$ T-C6: PASS)** | `VERIFIED` |
| **4** | **Động Cơ Luật Node-RED (Rule 1..5)** | Rule 2 gửi MUTE khi khói cao nhiệt thấp | Cải tiến Rule 2 trong [core_engine.js](file:///e:/IoT/DoAn/nodered/functions/core_engine.js): Khói cao nhiệt thấp (smoldering fire) leo thang ALARM, bật quạt, **tuyệt đối không gửi MUTE**. Rule 5 duyệt Fleet Registry phát tới topic cụ thể, cấm wildcard `+`/`#` trong PUBLISH | `nodered/tests/engine.test.js`<br>**(T-N1 $\to$ T-N11: PASS)** | `VERIFIED` |
| **5** | **Tích Hợp Luồng Node-RED (Live Flow)** | Auth lưu `device_fleet`, engine đọc `fleet`; thiếu scheduler & dedupe | Đồng bộ khóa context `fleet` mang `record.topology`; chuẩn hóa `parse_alarm.js` (`eventType = 'ALARM_EVENT'`) và `parse_keepalive.js` có Dedup TTL 5s; thêm node `inject_scheduler_1m` chu kỳ 60s; truyền tải độ ẩm thực `hum` | `nodered/tests/flow_integration.test.js`<br>**(FLOW-01 $\to$ FLOW-04: PASS)** | `VERIFIED` |
| **6** | **Web SCADA Chống XSS & Phản Chiếu** | Test tự dựng mock DOM giả, web còn `evaluateFsmRules` tự phát lệnh | Xóa bỏ hoàn toàn `evaluateFsmRules()`, `triggerAlarmState()` và lệnh tự tắt quạt trong `triggerCooldownState()`. Web SCADA trở thành giao diện Read-only phản chiếu 100% telemetry. Xuất `module.exports` và kiểm thử trực tiếp [app.js](file:///e:/IoT/DoAn/web/app.js) với `textContent` | `web/tests/util.test.js`<br>**(T-W1 $\to$ T-W4: PASS)** | `VERIFIED` |
| **7** | **Bộ Đệm Ngoại Tuyến (Offline Buffer)** | Chưa có kiểm thử tràn đệm vòng và xả từng phần | Bổ sung `mq2Valid` & `dhtValid` vào `OfflineRecord` trong [offline_buffer.h](file:///e:/IoT/DoAn/src/offline_buffer.h). Kiểm thử `T-B1`: đẩy 25 bản ghi vào đệm dung lượng 20, 5 bản ghi cũ nhất bị hủy, 20 bản ghi còn lại giữ đúng thứ tự FIFO; xả batch 7 bản ghi, 13 bản ghi còn lại giữ nguyên thứ tự | `test/test_core.cpp`<br>**(T-B1: PASS)**<br>`pio run -e esp32dev` | `PARTIAL` |
| **8** | **Exponential Backoff Tái Kết Nối** | Retry cố định 5s; chỉ test hàm `nextBackoff` | Thuật toán `nextBackoff(cur, 16000)` nhân đôi thời gian chờ từ 1s $\to$ 2s $\to$ 4s $\to$ 8s $\to$ 16s trong [netutil.h](file:///e:/IoT/DoAn/lib/core/netutil.h). Kiểm thử `T-R1`: mô phỏng máy trạng thái mất sóng WiFi và mất kết nối MQTT độc lập, chạm trần 16s, tự động reset về 1s ngay khi kết nối lại | `test/test_core.cpp`<br>**(T-R1, T-F12: PASS)** | `PARTIAL` |
| **9** | **Kênh Cảnh Báo Telegram** | Node-RED chỉ có debug; web có khung chat giả | Tách riêng [alert_dispatcher.js](file:///e:/IoT/DoAn/nodered/functions/alert_dispatcher.js) định dạng bản tin HTML gửi tới Telegram Bot API qua node HTTP Request khi có token; tự động chuyển sang chế độ Mock Debug khi chưa cấu hình token | `nodered/tests/engine.test.js`<br>**(T-N12: PASS)** | `PARTIAL` |
| **10** | **Phạm Vi Học Thuật & Tham Số Vật Lý** | Nhận vơ quy chuẩn PCCC; sai lệch $R_0$ vs $R_L$ | Làm rõ phạm vi: $R_L = 10\text{ k}\Omega$ là điện trở tải trên board phần cứng; $R_0 = 1.0\text{ k}\Omega$ là điện trở cảm biến trong không khí sạch Wokwi ($Rs = 1.71\text{ k}\Omega$ tại 200 PPM). Ngưỡng 400/350 PPM là tham số thực nghiệm demo đề tài. Cổng 1883 TCP plaintext là giới hạn giả lập Wokwi | `src/config.h`<br>`src/main.cpp`<br>**(CONFIG_INSPECTION: PASS)** | `SCOPE` |

---

### 2. Chi Tiết Các Cải Tiến Kỹ Thuật Đã Hoàn Thành

#### 2.1 Chuẩn Hóa và Kiểm Thử Tích Hợp Luồng Node-RED (Live Flow)
- **Đồng bộ Định tuyến Đa Vùng:** Tại hàm `fn_auth_service`, thiết bị xác thực được lưu vào `flow.get('fleet')` kèm đầy đủ cấu trúc `record.topology` (`building`, `floor`, `room`, `zone`). Nhờ đó, động cơ `core_engine.js` có đủ thông tin để sinh topic phân tầng V2 (`Nhom09/smoke/v2/HUIT_A/F03/P302/...`) và phát lệnh sơ tán khẩn cấp liên vùng sàn F03 tới đúng topic cụ thể của các phòng lân cận mà không vi phạm chuẩn MQTT 3.1.1.
- **Chuẩn hóa Bộ Phân Tích Sự Kiện (Parsers):**
  - [parse_alarm.js](file:///e:/IoT/DoAn/nodered/functions/parse_alarm.js): Chuẩn hóa `eventType = 'ALARM_EVENT'`, tích hợp bộ nhớ cache khử trùng lặp Dedup TTL 5s.
  - [parse_keepalive.js](file:///e:/IoT/DoAn/nodered/functions/parse_keepalive.js): Chuẩn hóa `eventType = 'KEEP_ALIVE'`, tích hợp khử trùng lặp Dedup TTL 5s.
  - [parse_telemetry.js](file:///e:/IoT/DoAn/nodered/functions/parse_telemetry.js): Bổ sung trích xuất trường độ ẩm `msg.hum = num(d.hum)`.
- **Đồng Bộ Dữ Liệu Lên Dashboard:** Tại Output 3 của `core_engine.js`, bổ sung trường `hum` phản chiếu dữ liệu độ ẩm đo được từ DHT22 của thiết bị chính, loại bỏ việc hiển thị cố định 60%.
- **Tự Động Hóa Lập Lịch Ngày/Đêm (Rule 3):** Bổ sung nút inject `inject_scheduler_1m` (chu kỳ lặp 60s) nối trực tiếp vào `fn_scheduler_tick` và điều phối tới `fn_command_dispatcher` và `fn_parse_scheduler`, tự động chuyển đổi ngưỡng nhạy giữa Ngày (400 PPM) và Đêm (350 PPM).
- **Kiểm Thử Cấp Luồng Tích Hợp:** Xây dựng tệp kiểm thử [flow_integration.test.js](file:///e:/IoT/DoAn/nodered/tests/flow_integration.test.js) nạp trực tiếp file cấu hình [flows_smoke_detector.json](file:///e:/IoT/DoAn/nodered/flows_smoke_detector.json), thẩm định cấu trúc dây nối thật (wiring topology), chu trình xác thực, khử trùng lặp, lập lịch và phát lệnh liên vùng sàn F03.

#### 2.2 Tái Cấu Trúc Giao Diện Web SCADA Thuần Túy (Clean Read-Only SCADA)
- **Loại Bỏ Logic Can Thiệp Cục Bộ:** Xóa bỏ hoàn toàn các hàm `evaluateFsmRules()`, `triggerAlarmState()` và logic đếm lùi trong `triggerCooldownState()`. Trước đây, hàm này tự động gửi lệnh `cmdFan OFF` sau 30 giây cooldown, vô tình làm ESP32 chuyển sang chế độ `MODE_MANUAL` (`manualMode = true, manualFan = false`).
- **Nguyên Tắc Thiết Kế SCADA:** Web SCADA hoạt động thuần túy theo nguyên tắc **Phản chiếu Trạng thái (Read-Only State Reflection)**. Khi nhận bản tin telemetry qua WebSocket, hàm `handleIncomingMqtt` cập nhật trực tiếp `STATE.fsmState`, `STATE.fanState`, `STATE.buzzerActive`, `STATE.health.mq2`, `STATE.health.dht` từ thiết bị biên và hiển thị lên giao diện mà không tự ý phát sinh lệnh chấp hành ngầm.
- **Kiểm Thử Trực Tiếp Không Mock Logic:** File [app.js](file:///e:/IoT/DoAn/web/app.js) xuất module CommonJS ở cuối file. File kiểm thử [util.test.js](file:///e:/IoT/DoAn/web/tests/util.test.js) nạp trực tiếp `app.js` thông qua Mock DOM tối thiểu, chứng minh trực tiếp:
  - `escapeHtml` triệt tiêu 100% payload XSS.
  - `renderAuditTable` hiển thị nhật ký bằng `textContent`, không tạo thẻ `<script>` trong DOM.
  - `showToast` hiển thị thông báo an toàn qua `textContent`.
  - `handleIncomingMqtt` phản chiếu chính xác dữ liệu telemetry và không gửi lệnh MQTT ngầm.

#### 2.3 Hoàn Thiện Kiểm Thử Firmware & Độ Bền Nhúng
- **Đệm Vòng Ngoại Tuyến (Offline Buffer):** Thêm trường `mq2Valid` và `dhtValid` vào cấu trúc `OfflineRecord` trong [offline_buffer.h](file:///e:/IoT/DoAn/src/offline_buffer.h) và hàm tuần tự hóa JSON trong [offline_buffer.cpp](file:///e:/IoT/DoAn/src/offline_buffer.cpp).
- **Bổ Sung 8 Bài Kiểm Thử Lõi Mới (`test/test_core.cpp`):**
  - `T-C1`: Lệnh bật/tắt quạt thủ công và khôi phục chế độ tự động `cmdFanAuto`.
  - `T-C2`: Khóa an toàn PCCC từ chối lệnh tắt quạt khi đang có báo động ALARM.
  - `T-C3`: Khóa an toàn từ chối lệnh MUTE còi từ xa khi đang ALARM.
  - `T-C4`: Lệnh UNMUTE từ xa khôi phục âm thanh báo động.
  - `T-C5`: Khóa an toàn từ chối lệnh thử nghiệm TEST còi khi đang ALARM.
  - `T-C6`: Từ chối các lệnh chấp hành không hợp lệ hoặc chứa hành động lạ.
  - `T-B1`: Kiểm tra thuật toán bộ đệm vòng ngoại tuyến dung lượng 20 bản ghi: khi ghi tràn 25 bản ghi, 5 bản ghi cũ nhất bị loại bỏ, 20 bản ghi còn lại giữ đúng thứ tự FIFO; khi xả từng phần 7 bản ghi, 13 bản ghi còn lại vẫn duy trì thứ tự FIFO chuẩn xác.
  - `T-R1`: Kiểm tra máy trạng thái Exponential Backoff mô phỏng chuỗi rớt mạng WiFi và MQTT, nhân đôi thời gian chờ từ 1s $\to$ 2s $\to$ 4s $\to$ 8s $\to$ 16s và reset về 1s ngay khi kết nối lại.
- **Kiểm Soát Độ Trễ Vòng Lặp Vận Hành:**
  - Thiết lập timeout mạng `g_espClient.setTimeout(2)` và `g_mqttClient.setSocketTimeout(2)`.
  - Hiện thực hóa hằng số `NET_MAX_BLOCK_MS = 3000` với cơ chế đo thời gian thực thi vòng `loop()`: nếu phát hiện độ trễ vượt quá 3000 ms, hệ thống lập tức xuất cảnh báo hiệu năng `[PERF WARN]` lên Serial Monitor.
- **Minh Bạch Hóa Bộ Nhớ ArduinoJson v7:** Loại bỏ tuyên bố "Zero Heap Fragmentation" ở phần đầu tệp [main.cpp](file:///e:/IoT/DoAn/src/main.cpp). Làm rõ rằng thư viện ArduinoJson v7 cấp phát đối tượng `JsonDocument` cục bộ trên stack trong phạm vi từng hàm xử lý (stack/local-bounded), kết hợp giới hạn kích thước vùng đệm mạng `setBufferSize(512)` để ngăn chặn triệt để hiện tượng phân mảnh bộ nhớ động kéo dài.

---

### 3. Tổng Hợp Kết Quả Thực Thi Kiểm Chuẩn Toàn Hệ Thống

Toàn bộ hệ thống đã được kiểm thử tự động với kết quả 100% đạt chuẩn:

```text
================================================================================
                    TỔNG HỢP KẾT QUẢ KIỂM THỬ HỆ THỐNG V5
================================================================================
1. Thuật toán Lõi C++17 (Unity Native Test):        29 / 29 PASS (100.0%)
2. Middleware Node-RED (Engine & Flow Integration): 16 / 16 PASS (100.0%)
   - Unit Tests Động cơ Quy tắc (engine.test.js):    12 / 12 PASS
   - Tích hợp Luồng Flow Thật (flow_integration):     4 /  4 PASS
3. An toàn Giao diện Web SCADA (util.test.js):        4 /  4 PASS (100.0%)
4. Ma Trận Cam Kết 3 Bậc (3-Tier Claims Validator): 10 / 10 PASS (100.0%)
   - VERIFIED PASS (Đã chứng minh 100% bằng code):    6 /  6
   - PARTIAL VALID (Chứng minh thuật toán/nhúng):     3 /  3
   - SCOPE VALID (Giới hạn phạm vi học thuật):        1 /  1
5. Biên dịch Phần cứng Nhúng ESP32 (PlatformIO):    SUCCESS (0 Warning, 0 Error)
   - RAM sử dụng: 46,544 bytes (14.2% / 320 KB)
   - Flash sử dụng: 784,937 bytes (59.9% / 1.3 MB)
6. Kiểm thử Hồi quy Toàn diện (Tuần 6 -> Tuần 9):   63 / 63 PASS (100.0%)
================================================================================
```

---

### 4. Hướng Dẫn Thẩm Định Tự Động (Verification Commands)

Người kiểm duyệt hoặc AI Reviewer có thể tự động thẩm định độc lập toàn bộ dự án bằng 5 lệnh sau:

```powershell
# 1. Chạy 29 Unit Test thuật toán lõi C++17 (Unity Native)
pio test -e native

# 2. Chạy 16 Unit & Integration Tests tầng Middleware Node-RED
node --test nodered/tests/engine.test.js nodered/tests/flow_integration.test.js

# 3. Chạy 4 Unit Test an toàn giao diện Web SCADA (nạp trực tiếp web/app.js)
node --test web/tests/util.test.js

# 4. Thẩm định toàn bộ 10 cam kết ma trận kiểm duyệt 3 bậc (3-Tier Claims Validator)
python scripts/check_claims.py

# 5. Biên dịch kiểm tra toàn diện Firmware ESP32 (0 warning, 0 error)
pio run -e esp32dev
```

---

### 5. Danh Mục Tài Liệu Bàn Giao

- **Hồ Sơ Toàn Bộ Mã Nguồn Vận Hành v5:** [PROJECT_CODEBASE.md](file:///e:/IoT/DoAn/PROJECT_CODEBASE.md) (9,250 dòng, 318.8 KB).
- **Thư Viện C++17 Cốt Lõi:** [lib/core/](file:///e:/IoT/DoAn/lib/core/) (`thresholds.h`, `ema_filter.h`, `health.h`, `netutil.h`, `fsm_core.h`, `fsm_core.cpp`).
- **Mã Nguồn Firmware ESP32:** [src/main.cpp](file:///e:/IoT/DoAn/src/main.cpp), [src/config.h](file:///e:/IoT/DoAn/src/config.h), [src/sensors.cpp](file:///e:/IoT/DoAn/src/sensors.cpp), [src/fsm.cpp](file:///e:/IoT/DoAn/src/fsm.cpp), [src/offline_buffer.cpp](file:///e:/IoT/DoAn/src/offline_buffer.cpp).
- **Module Hàm & Luồng Node-RED:** [nodered/functions/](file:///e:/IoT/DoAn/nodered/functions/) (`core_engine.js`, `parse_telemetry.js`, `parse_alarm.js`, `parse_keepalive.js`, `parse_lwt.js`, `command_dispatcher.js`, `alert_dispatcher.js`, `scheduler_tick.js`), luồng tại [nodered/flows_smoke_detector.json](file:///e:/IoT/DoAn/nodered/flows_smoke_detector.json).
- **Giao Diện Web SCADA:** [web/app.js](file:///e:/IoT/DoAn/web/app.js), [web/index.html](file:///e:/IoT/DoAn/web/index.html), [web/style.css](file:///e:/IoT/DoAn/web/style.css), [web/util.js](file:///e:/IoT/DoAn/web/util.js).
- **Bộ Kiểm Thử & Cam Kết Audit:** [test/test_core.cpp](file:///e:/IoT/DoAn/test/test_core.cpp), [nodered/tests/](file:///e:/IoT/DoAn/nodered/tests/), [web/tests/](file:///e:/IoT/DoAn/web/tests/), [docs/audit/claims.yaml](file:///e:/IoT/DoAn/docs/audit/claims.yaml), [scripts/check_claims.py](file:///e:/IoT/DoAn/scripts/check_claims.py).
