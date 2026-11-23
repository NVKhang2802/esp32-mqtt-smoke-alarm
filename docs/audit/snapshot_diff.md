# Đối Chiếu Repo Thực Tế với Snapshot Kiến Trúc (Snapshot Diff)
## Đề tài 04: Hệ thống Báo khói Cảnh báo sớm | Nhóm 04 (N09) - HUIT
*Thời gian thực hiện: Phase 0 — Chuẩn bị (audit-fix-v5)*

---

## 1. Mục Đích Đối Chiếu
Tài liệu này ghi nhận sự khác biệt giữa hiện trạng mã nguồn thực tế tại commit tag `before-audit` và bản đặc tả mục tiêu trong [Kế hoạch khắc phục và chuẩn hóa dự án Báo khói IoT (v5).md](file:///e:/IoT/DoAn/docs/md/Kế%20hoạch%20khắc%20phục%20và%20chuẩn%20hóa%20dự%20án%20Báo%20khói%20IoT%20(v5).md).

---

## 2. Bảng Đối Chiếu Thành Phần

### 2.1 Firmware C++ (`src/`)
| Tệp Tin | Hiện Trạng Trong Repo Thật | Mục Tiêu Chuẩn Hóa Bản v5 | Đánh Giá Tác Động |
| :--- | :--- | :--- | :--- |
| `src/config.h` | Chỉ có `MQTT_CLIENT_PREFIX`, chưa có hằng số `DEVICE_ID` cố định; tham số lọc EMA chưa khai báo. | Khai báo `DEVICE_ID = "ESP32_SMOKE_N04_A01"`, hằng số EMA bất đối xứng ($\alpha_{rise}=0.40, \alpha_{fall}=0.15$), `LOCAL_ACK_MUTE_MS = 60000`. | Cần thêm hằng số, bỏ `SAFE_PPM_NIGHT`. |
| `src/fsm.h` & `src/fsm.cpp` | FSM phụ thuộc `Arduino.h`, gọi trực tiếp `digitalWrite` và `ledcWrite`; logic nằm lẫn với HAL. | Tách toàn bộ lõi thuần sang `lib/core/fsm_core.*` (không phụ thuộc `Arduino.h`), FSM chỉ trả về `FsmOutput` (fanOn, buzzerMode). `src/fsm.*` chỉ là wrapper hoặc thay thế bởi HAL. | Cần tái cấu trúc, viết test native trước. |
| `src/sensors.h` & `src/sensors.cpp` | Chỉ có trung bình cộng 10 mẫu `readAverageRs`; chưa có EMA; chẩn đoán lỗi còn điều kiện sai `rawADC > 4080`. | Tách `ema_filter.h` và `health.h` vào `lib/core/`; loại bỏ `rawADC > 4080`; bổ sung debounce 3 lần hồi phục và đếm 3 lần đọc hỏng cho DHT22. | Khắc phục F02, F19, F24. |
| `src/main.cpp` | Lệnh điều khiển dùng `strstr` (dễ nhầm `"ACTION"` thành `"ON"`); còi ghi LEDC trực tiếp trong handler; 1 biến reconnect 5s chung; LWT payload JSON. | Chuyển toàn bộ sang `JsonDocument` ArduinoJson v7; driver còi `buzzerTick` duy nhất ghi LEDC theo cạnh; 2 biến backoff độc lập ($1\text{s} \to 16\text{s}$). | Khắc phục F07, F08, F17, F18, F21. |
| `src/offline_buffer.*` | Mảng tĩnh 20 phần tử, nhưng `flushOfflineBuffer` xóa count mà không kiểm tra kết quả `publish`. | Tách logic đệm vào `lib/core/` để test native; kiểm tra `publish()` thành công mới trừ bản ghi đã gửi; đệm cả sự kiện ALARM khi mất mạng. | Khắc phục F23. |

---

### 2.2 Middleware Node-RED (`nodered/`)
| Tệp Tin | Hiện Trạng Trong Repo Thật | Mục Tiêu Chuẩn Hóa Bản v5 | Đánh Giá Tác Động |
| :--- | :--- | :--- | :--- |
| `nodered/generate_flows.py` | Toàn bộ function node viết dưới dạng chuỗi inline Python; node `mqtt out` có topic tĩnh ghi đè topic động; Rule 2 gửi lệnh MUTE; thiếu khử trùng lặp có TTL. | Tách function nodes thành các tệp độc lập trong `nodered/functions/*.js`; `generate_flows.py` chỉ đọc và nhúng tệp; để trống topic ở node `mqtt out`; khử trùng lặp V1/V2 bằng khóa có TTL 5s. | Khắc phục F04, F05, F09, F10, F11, F12. |
| `nodered/tests/` | Chưa có thư mục test độc lập cho Node-RED. | Tạo `nodered/tests/harness.js` và `nodered/tests/engine.test.js` chạy bằng `node --test`. | Đảm bảo 12 bài test `T-N1` đến `T-N12` PASS 100%. |

---

### 2.3 Web SCADA Application (`web/`)
| Tệp Tin | Hiện Trạng Trong Repo Thật | Mục Tiêu Chuẩn Hóa Bản v5 | Đánh Giá Tác Động |
| :--- | :--- | :--- | :--- |
| `web/app.js` | `renderAuditTable()` và `showToast()` nối chuỗi HTML trực tiếp; Web tự suy diễn trạng thái FSM qua `evaluateFsmRules()`. | Tạo `web/util.js` chứa hàm `escapeHtml()`; Web SCADA chỉ phản chiếu `fsm_state` từ firmware; vô hiệu hóa MUTE khi ALARM; hiển thị huy hiệu cảm biến. | Khắc phục F25, F26. |

---

## 3. Danh Sách Các Bài Test Đang Mô Tả Hành Vi Cũ (Cần Cập Nhật)

Đối chiếu với bộ 63 bài test trong `run_all_tests.py`:
1. **`tests/test_tuan7_business_rules.py` — Test 02 (Rule 2):**
   - *Hành vi cũ:* Kỳ vọng nhận lệnh `MUTE` từ Cloud khi khói $\ge 400\text{ PPM}$ và nhiệt độ $< 35^\circ\text{C}$.
   - *Hành vi mới chuẩn hóa (F04):* Cloud KHÔNG gửi lệnh MUTE còi; Cloud gửi lệnh bật quạt phụ trợ `FAN ON` và giữ nguyên trạng thái còi tự chủ của thiết bị biên.
2. **`tests/test_tuan9_system_robustness.py` — Test 09 (EMA Filter):**
   - *Hành vi cũ:* Tuyên bố xung gai 500 PPM được lọc xuống $< 196\text{ PPM}$.
   - *Hành vi mới chuẩn hóa (F19):* Xung đơn mẫu đến $700\text{ PPM}$ (nền 200 PPM) được lọc xuống $< 400\text{ PPM}$; bước nhảy $\ge 600\text{ PPM}$ kích hoạt báo cháy trong $\le 4\text{s}$.
3. **`tests/test_tuan9_system_robustness.py` — Test 12 (Reconnect Backoff):**
   - *Hành vi cũ:* Kiểm tra thời gian retry cố định.
   - *Hành vi mới chuẩn hóa (F21):* Kiểm tra Exponential Backoff $1\text{s} \to 2\text{s} \to 4\text{s} \to 8\text{s} \to 16\text{s}$.
4. **`tests/test_tuan6_application.py` — Topics & Timings:**
   - *Hành vi cũ:* Chưa có tiền tố `Nhom09/` và chưa đồng bộ callback `on_subscribe` khiến test phụ thuộc vào độ trễ mạng Internet public broker.
   - *Hành vi mới:* Chuẩn hóa tiền tố `Nhom09/` và đồng bộ chờ `on_subscribe`.

---

## 4. Kết Luận Phase 0
Mã nguồn thực tế đã được lập chỉ mục và đối chiếu đầy đủ. Toàn bộ các điểm sai lệch so với bản v5 đã được xác định rõ ràng và sẵn sàng để bước vào **Phase 1: Lõi Logic Thuần & Test Native**.
