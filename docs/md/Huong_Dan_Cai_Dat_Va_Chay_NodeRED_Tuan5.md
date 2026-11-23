# HƯỚNG DẪN CÀI ĐẶT & CHẠY THỬ NGHIỆM MIDDLEWARE NODE-RED (TUẦN 5)
## Đề tài 04: Hệ thống báo khói cảnh báo sớm - Nhóm 09 (N09)

---

### 1. GIỚI THIỆU
Tài liệu này hướng dẫn chi tiết cách thức triển khai Tầng 3 - Middleware / Automation Engine cho Hệ thống báo khói cảnh báo sớm bằng nền tảng **Node-RED**.

Bộ mã nguồn Tầng 3 được lưu trữ tại:
- **File Flow Node-RED:** `nodered/flows_smoke_detector.json`
- **Kịch bản kiểm thử tự động Python:** `test_middleware_simulator.py`
- **File nhật ký sự kiện:** `logs/event_history.log`

---

### 2. CÁC BƯỚC CÀI ĐẶT NODE-RED TRÊN MÁY TÍNH

#### Bước 1: Kiểm tra Node.js
Mở PowerShell hoặc Command Prompt và kiểm tra phiên bản Node.js:
```bash
node -v
npm -v
```
*(Nếu chưa có Node.js, tải và cài đặt bản LTS tại [nodejs.org](https://nodejs.org/)).*

#### Bước 2: Cài đặt Node-RED toàn cục
```bash
npm install -g --unsafe-perm node-red
```

#### Bước 3: Cài đặt thư viện Node-RED Dashboard (tùy chọn để hiển thị giao diện UI)
```bash
cd %USERPROFILE%\.node-red
npm install node-red-dashboard
```

#### Bước 4: Khởi động Node-RED
```bash
node-red
```
Khi khởi động xong, Node-RED sẽ chạy tại địa chỉ:
- Giao diện thiết kế Flow: `http://127.0.0.1:1880`
- Giao diện Dashboard hiển thị: `http://127.0.0.1:1880/ui`

---

### 3. HƯỚNG DẪN IMPORT FILE FLOW TUẦN 5

1. Mở trình duyệt và truy cập `http://127.0.0.1:1880`.
2. Nhấp vào biểu tượng menu **3 dấu gạch ngang** ở góc trên cùng bên phải.
3. Chọn **Import** (hoặc nhấn phím tắt `Ctrl + I`).
4. Chọn **select a file to import** và trỏ đến đường dẫn:
   ```
   e:\IoT\DoAn\nodered\flows_smoke_detector.json
   ```
5. Chọn **Import into: current flow** hoặc **new flow**, sau đó nhấn **Import**.
6. Nhấn nút màu đỏ **Deploy** ở góc trên bên phải để áp dụng toàn bộ luồng xử lý.

Sau khi Deploy thành công, các node MQTT sẽ hiển thị trạng thái chấm xanh **connected** tới Broker `broker.emqx.io`.

---

### 4. HƯỚNG DẪN KIỂM THỬ TẦNG 3 MIDDLEWARE

#### Cách 1: Sử dụng Kịch bản kiểm thử tự động Python (Khuyến nghị)
Nhóm đã phát triển sẵn script `test_middleware_simulator.py` mô phỏng đầy đủ luồng sự kiện của ESP32 để kiểm tra 5 Automation Rules:

Mở một cửa sổ dòng lệnh tại thư mục gốc dự án `e:\IoT\DoAn` và chạy:
```bash
python test_middleware_simulator.py
```

**Kịch bản sẽ tự động chạy qua 6 giai đoạn:**
1. **Giai đoạn 1:** Gửi trạng thái Online LWT.
2. **Giai đoạn 2:** Gửi Telemetry an toàn (PPM: 120, Temp: 28°C) -> FSM duy trì `SAFE`.
3. **Giai đoạn 3:** Gửi khói vượt ngưỡng (PPM: 462 >= 400) -> Trigger Rule 1, Node-RED gửi lệnh Downlink `smoke/cmd/fan: ON` và `smoke/cmd/buzzer: UNMUTE`.
4. **Giai đoạn 4:** Gửi sự kiện khẩn cấp `smoke/event/alarm` -> Node-RED phản hồi tức thời < 50ms.
5. **Giai đoạn 5:** Khói giảm về 150 PPM (< 300 PPM) -> Node-RED chuyển sang `COOLDOWN`, duy trì quạt chạy thêm 20 giây trễ Hysteresis, sau đó tự động phát lệnh `smoke/cmd/fan: OFF`.
6. **Giai đoạn 6:** Gửi nhiệt độ cao 58.5°C -> Trigger Rule 2 cảnh báo quá nhiệt `HEAT_OVERHEAT`.

Toàn bộ lệnh Downlink nhận được sẽ hiển thị chi tiết trên màn hình console.

#### Cách 2: Kết nối trực tiếp với ESP32 mô phỏng trên Wokwi
1. Mở dự án mô phỏng ESP32 trên Wokwi (chạy mã nguồn `src/main.cpp`).
2. ESP32 sẽ tự động kết nối WiFi `Wokwi-GUEST` và Broker `broker.emqx.io:1883`.
3. Kéo thanh trượt cảm biến khí ga MQ-2 trên Wokwi vượt ngưỡng 400 PPM:
   - Node-RED lập tức phát hiện nồng độ khói vượt ngưỡng.
   - Node-RED phát lệnh Downlink bật quạt xuống `smoke/cmd/fan`.
   - Trên Wokwi, đèn LED Quạt bật sáng và Còi Buzzer hú báo động.
4. Kéo thanh trượt MQ-2 về dưới 300 PPM:
   - Quan sát Node-RED chuyển trạng thái sang `COOLDOWN`.
   - Quạt trên Wokwi vẫn tiếp tục chạy trong 20 giây để làm mát.
   - Hết 20 giây, Node-RED gửi lệnh tắt quạt và quạt trên Wokwi tự động tắt.

---

### 5. KIỂM TRA TẬP TIN NHẬT KÝ SỰ KIỆN (AUDIT TRAIL LOG)
Mở tập tin:
```
e:\IoT\DoAn\logs\event_history.log
```
Bạn sẽ thấy toàn bộ nhật ký sự kiện được ghi nhận tuần tự theo thời gian:
```text
[2026-10-05T19:15:20.120Z] [INFO] [LWT_CONNECTED] Thiết bị ESP32 trực tuyến trở lại
[2026-10-05T19:15:25.340Z] [CRITICAL] [SMOKE_ALARM_TRIGGERED] Khói vượt ngưỡng (462.8 PPM >= 400.0 PPM). Kích hoạt còi báo động và quạt hút khói!
[2026-10-05T19:15:35.500Z] [INFO] [COOLDOWN_STARTED] Nồng độ khói đã giảm về vùng an toàn (150.0 PPM < 300.0 PPM). Bắt đầu làm mát trễ 20s.
[2026-10-05T19:15:55.510Z] [INFO] [COOLDOWN_COMPLETED] Chu kỳ làm mát kết thúc an toàn. Tự động gửi lệnh tắt quạt hút và còi.
[2026-10-05T19:16:02.100Z] [WARN] [HEAT_OVERHEAT] Nhiệt độ môi trường cực cao: 58.5°C! Nguy cơ bắt lửa.
```

---

### 6. TỔNG KẾT
Hệ thống Tầng 3 Middleware đáp ứng đầy đủ và hoàn hảo các tiêu chuẩn đánh giá của Milestone Tuần 5:
- Có file export Node-RED Flow (`nodered/flows_smoke_detector.json`).
- Có 5 quy tắc tự động hóa đa tầng (vượt xa yêu cầu tối thiểu 01 rule).
- Có cơ chế ghi chép lịch sử sự kiện kép (Memory Buffer & File Append).
- Có luồng phát lệnh Downlink điều khiển thiết bị chấp hành.
- Có chứng minh năng lực xử lý nghiệp vụ thông minh, không chỉ forward dữ liệu thô.

