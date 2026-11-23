# Hướng Dẫn Cài Đặt và Chạy Node-RED - Milestone Tuần 5

Tài liệu này hướng dẫn chi tiết cách thiết lập và vận hành Middleware Automation Engine tại Tầng 3 cho Hệ thống Báo khói cảnh báo sớm (Theo chuẩn Slide 65) của Nhóm 09.

## 1. Yêu Cầu Hệ Thống
- Đã cài đặt **Node.js** (Phiên bản khuyến nghị: v18.x trở lên. Hệ thống hiện tại đang sử dụng v24.19.0).
- Trình duyệt web (Chrome/Edge/Firefox) để truy cập giao diện.
- Kết nối Internet để tải các node và kết nối tới MQTT Broker Cloud (`broker.emqx.io`).

## 2. Cài Đặt và Khởi Chạy Node-RED

1. **Mở Terminal hoặc PowerShell** với quyền hạn bình thường hoặc Admin.
2. **Cài đặt Node-RED** trên toàn hệ thống (Global) bằng npm:
   ```powershell
   npm install -g --unsafe-perm node-red
   ```
3. **Khởi động Node-RED** bằng lệnh:
   ```powershell
   node-red
   ```
4. Đợi vài giây cho đến khi Terminal báo Server đã chạy, ví dụ: `Server now running at http://127.0.0.1:1880/`. Đừng đóng cửa sổ Terminal này trong suốt quá trình sử dụng hệ thống.

## 3. Cài Đặt Thư Viện Giao Diện (Node-RED Dashboard)

Middleware sử dụng các thành phần giao diện (Gauge, Text, Template) để hiển thị thông số và điều khiển hạm đội thiết bị, do đó cần cài đặt thư viện dashboard.

1. Mở trình duyệt web và truy cập vào **[http://localhost:1880](http://localhost:1880)**.
2. Tại giao diện chính của Node-RED, click vào nút **Menu** (biểu tượng 3 gạch ngang ở góc phải trên cùng).
3. Chọn **Manage palette**.
4. Chuyển sang tab **Install**, tìm kiếm từ khóa `node-red-dashboard`.
5. Bấm vào nút **Install** để tiến hành cài đặt. Chờ thông báo thành công.

## 4. Import Cấu Hình Middleware (Flows Tuần 5)

1. Mở Menu (góc phải trên) ➔ Chọn **Import**.
2. Chọn **select a file to import** và trỏ tới file cấu hình của nhóm: `e:\IoT\DoAn\nodered\flows_smoke_detector.json`.
3. Bấm **Import**.
4. Lúc này màn hình làm việc sẽ hiển thị luồng Flow hoàn chỉnh với 29 nodes, được cấu trúc theo 5 Rules (Quá nhiệt, Ngưỡng khói, Hysteresis Cooldown, Scheduler ban đêm, Watchdog).
5. Bấm nút **Deploy** (Màu đỏ ở góc phải trên) để bắt đầu khởi chạy hệ thống Middleware.

## 5. Truy Cập UI Dashboard và Kiểm Tra Sự Kiện (Test Cases)

### 5.1. Xem Dashboard Giao Diện (UI)
- Truy cập vào **[http://localhost:1880/ui](http://localhost:1880/ui)** bằng trình duyệt.
- Bạn sẽ thấy Bảng điều khiển gồm: Thông số Cảm biến Môi trường (Nhiệt độ, Khói, Độ ẩm), Máy trạng thái FSM (Safe, Warning, Alarm, Cooldown) và Danh bạ Hạm đội Thiết bị (Fleet Registry).

### 5.2. Kiểm Tra Lịch Sử Hoạt Động (Audit Trail & File Log)
- Hệ thống có cơ chế Ghi Log chuẩn theo ISO 8601. Các sự kiện, trạng thái FSM sẽ được lưu nối tiếp vào file: `logs/event_history.log` ngay trong thư mục gốc mà bạn đã chạy lệnh `node-red`.
- Bạn có thể mở file này bằng Notepad hoặc VS Code để trích xuất báo cáo hoặc thanh tra hệ thống.

### 5.3. Thực Hiện Test Case
Kết hợp với Bảng Test Case (`Bang_Test_Case_Tuan5_Nhom04.docx`), sử dụng các phần mềm MQTT Client (như MQTTX) kết nối cùng Broker (`broker.emqx.io`, port `1883`) để đẩy dữ liệu giả lập và quan sát phản ứng của Middleware:
- **Test Hysteresis (Rule 3):** Publish `{"ppm": 450}` lên topic `smoke/telemetry` để FSM chuyển sang `ALARM`. Sau đó publish `{"ppm": 280}` (Dưới 300) để FSM chuyển sang `COOLDOWN` đếm lùi 20s.
- **Test An Ninh (Dịch vụ 1):** Publish gói xác thực sai MAC lên `smoke/v2/auth/request` để kiểm chứng Middleware từ chối thiết bị lạ.
- **Test Quá Nhiệt (Rule 2):** Publish `{"temp": 58.5}` để Trigger cảnh báo quá nhiệt (ngưỡng 55°C).

Chúc Nhóm 09 nghiệm thu thành công tiến độ Milestone Tuần 5!

