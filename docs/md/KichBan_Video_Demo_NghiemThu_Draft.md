# KỊCH BẢN CHI TIẾT VIDEO DEMO NGHIỆM THU ĐỒ ÁN IoT (DRAFT TUẦN 9)

> **Đề tài 04**: HỆ THỐNG BÁO KHÓI CẢNH BÁO SỚM  
> **Nhóm thực hiện**: Nhóm 09 (Mã nhóm phân bổ: N09)  
> **Thành viên**: Nguyễn Vĩnh Khang (Trưởng nhóm), Nguyễn Văn Đức, Nguyễn Văn Mãnh  
> **GVHD**: ThS. Võ Hoàng Hải — Khoa Công nghệ Thông tin, Đại học Công Thương TP.HCM (HUIT)  
> **Thời lượng video dự kiến**: 5 – 7 phút  
> **Chất lượng hình ảnh / âm thanh**: Full HD 1080p 60fps, lồng tiếng thuyết minh rõ ràng, nhạc nền nhẹ không lấn át giọng nói.

---

## 1. MỤC TIÊU CỦA VIDEO DEMO NGHIỆM THU
1. Chứng minh đầy đủ **Kiến trúc 4 tầng IoT**: Sensing (T1) $\rightarrow$ Network (T2) $\rightarrow$ Middleware (T3) $\rightarrow$ Application (T4).
2. Trực quan hóa **Mô hình mô phỏng Wokwi** hoạt động tương tác thời gian thực với phần mềm bên ngoài.
3. Thể hiện rõ ràng **Luồng hai chiều (Bi-directional Flow)**: Uplink thu thập telemetry và Downlink điều khiển thiết bị chấp hành có xác nhận ACK khép kín.
4. Trình diễn **5 Business Rules PCCC** và **4 Kịch bản Sự cố Bất thường** (kích hoạt cảnh báo Telegram Bot, mất mạng tự phục hồi, xả bộ đệm ngoại tuyến).
5. Đáp ứng hoàn hảo các tiêu chí của Milestone **M4 – End-to-End System** và chuẩn bị sẵn sàng cho Hội đồng nghiệm thu Tuần 10.

---

## 2. PHÂN CHIA CHI TIẾT CÁC PHÂN CẢNH (STORYBOARD)

### 🎬 Phân cảnh 1: Giới thiệu Tổng quan Đề tài & Đội ngũ Thực hiện (0:00 – 1:00)
* **Người trình bày**: Nguyễn Vĩnh Khang (Trưởng nhóm).
* **Hình ảnh hiển thị**: Slide bìa đề tài (Logo HUIT, Tên đề tài, Giảng viên hướng dẫn, Danh sách 3 thành viên kèm ảnh chân dung và MSSV).
* **Nội dung thuyết minh (Voiceover)**:
  > *"Kính chào Thầy Võ Hoàng Hải và Hội đồng Giảng viên chấm Đồ án môn học IoT. Em là Nguyễn Vĩnh Khang, đại diện Nhóm 09 (mã nhóm N09) cùng hai bạn Nguyễn Văn Đức và Nguyễn Văn Mãnh. Hôm nay, nhóm chúng em xin được trình diễn video demo hoàn chỉnh cho Đề tài số 04: 'Hệ thống Báo khói Cảnh báo sớm'. Đề tài được xây dựng theo chuẩn Kiến trúc 4 tầng IoT, tích hợp tự động hóa PCCC thông minh, hỗ trợ điều khiển hai chiều và sẵn sàng thích ứng với các sự cố bất thường phần cứng lẫn mạng viễn thông."*
* **Chuyển cảnh**: Hiển thị sơ đồ kiến trúc 4 tầng tổng quát với các mũi tên dữ liệu động.

---

### 🎬 Phân cảnh 2: Mô phỏng Mạch Wokwi & Tầng 1 Sensing / Embedded (1:00 – 2:30)
* **Người trình bày**: Nguyễn Văn Đức (Thành viên phụ trách Sensing & Embedded).
* **Hình ảnh hiển thị**: Quay màn hình giao diện Wokwi Simulation (`diagram.json`, `wokwi.toml`) chạy song song với cửa sổ Serial Monitor.
* **Thao tác thực hiện trên video**:
  1. Chỉ rõ vị trí vi điều khiển ESP32, cảm biến khói MQ-2 (nối chân analog GPIO34), cảm biến nhiệt ẩm DHT22 (GPIO4), Module Relay điều khiển Quạt hút (GPIO18) và Còi hú PWM Buzzer (GPIO19).
  2. Bấm nút *Start Simulation* trên Wokwi: Serial Monitor in ra thông tin kết nối Wi-Fi Wokwi-GUEST, kết nối MQTT Broker `broker.emqx.io:1883`, và địa chỉ MAC của thiết bị.
  3. Kéo thanh trượt nồng độ khói trên cảm biến MQ-2 từ 100 lên 250 PPM: Serial Monitor hiển thị nồng độ khói đọc được đã qua bộ lọc số EMA khử nhiễu.
* **Nội dung thuyết minh (Voiceover)**:
  > *"Tại Tầng 1, nhóm đã thiết kế mạch nguyên lý hoàn chỉnh trên nền tảng Wokwi. Firmware ESP32 được lập trình theo kiến trúc Non-blocking hướng module, sử dụng máy trạng thái hữu hạn FSM 6 trạng thái. Toàn bộ chu kỳ đọc ADC từ MQ-2 và xung số từ DHT22 đều được lọc nhiễu hàm mũ EMA và không sử dụng hàm delay, đảm bảo Task Watchdog Timer luôn hoạt động ổn định và Free Heap không hề bị rò rỉ sau nhiều ngày vận hành."*

---

### 🎬 Phân cảnh 3: Vận hành Bình thường & Luồng Điều khiển Hai chiều Tầng 2–4 (2:30 – 4:00)
* **Người trình bày**: Nguyễn Văn Mãnh & Nguyễn Vĩnh Khang.
* **Hình ảnh hiển thị**: Chia đôi màn hình: Nửa trái là Web Application Dashboard (`web/index.html`), nửa phải là Node-RED Flow (`nodered/flows_smoke_detector.json`).
* **Thao tác thực hiện trên video**:
  1. Cho thấy các đồng hồ Gauge (Nồng độ khói PPM, Nhiệt độ °C, Độ ẩm %) trên Web UI nhảy số nhịp nhàng đồng bộ với giá trị đo trên Wokwi (chu kỳ 2s).
  2. Biểu đồ thời gian thực Chart.js vẽ liên tục các điểm đo mới.
  3. Người dùng trên Web Dashboard nhấn nút **Bật Quạt hút (Fan ON)**:
     - Trên Node-RED: Node kiểm tra RBAC xác thực quyền Operator và chuyển tiếp lệnh.
     - Trên Wokwi: Chân Relay GPIO18 lập tức kích hoạt sang mức HIGH, quạt mô phỏng bắt đầu quay.
     - ESP32 gửi gói tin ACK lên topic `smoke/status`.
     - Nút bấm trên Web UI chuyển sang màu xanh khẳng định trạng thái bật thành công.
  4. Thao tác tiếp lệnh **Tắt Còi tạm thời (Mute Buzzer 180s)**: Đồng hồ đếm ngược trên Web UI bắt đầu chạy lùi.
* **Nội dung thuyết minh (Voiceover)**:
  > *"Dữ liệu từ vi điều khiển được đóng gói JSON chuẩn RFC 8259, đẩy lên EMQX Cloud Broker qua topic smoke/telemetry. Node-RED Middleware tiếp nhận, phân tích và chuyển tiếp qua WebSocket tới Web Dashboard. Luồng Downlink cho phép người quản trị điều khiển từ xa với cơ chế xác nhận khép kín Closed-loop ACK: trạng thái chỉ cập nhật khi thiết bị biên đã kích hoạt relay thành công, loại bỏ hoàn toàn hiện tượng hiển thị trạng thái ảo."*

---

### 🎬 Phân cảnh 4: Kịch bản Báo động Hỏa hoạn, Telegram Bot & Xử lý Sự cố Mất mạng (4:00 – 5:30)
* **Người trình bày**: Nguyễn Văn Mãnh (Thành viên phụ trách Middleware & Alerting).
* **Hình ảnh hiển thị**: Màn hình Wokwi + Web Dashboard đổi màu đỏ rực + Khung thông báo Telegram Bot trên điện thoại / desktop.
* **Thao tác thực hiện trên video**:
  1. Kéo thanh trượt MQ-2 vọt lên **650 PPM** và tăng nhiệt độ DHT22:
     - ESP32 lập tức phát còi hú báo động tại chỗ và đóng relay bật quạt hút khẩn cấp.
     - Web UI đổi toàn bộ giao diện sang màu đỏ rực rỡ, phát âm thanh cảnh báo còi hú ảo qua Web Audio API.
     - Telegram Bot ngay lập tức 'ting ting' gửi tin nhắn cảnh báo cháy khẩn cấp: *'🔥 BÁO ĐỘNG HỎA HOẠN: Khói 650 PPM tại Tầng 3 Tòa A'*.
  2. Trình diễn **Khóa an toàn PCCC (Emergency Override Guard)**: Thử nhấn nút Tắt quạt trên Web UI khi đang có cháy -> Giao diện hiện thông báo từ chối lệnh vì lý do an toàn sinh mạng.
  3. Trình diễn **Mất mạng & Vòng đệm Ngoại tuyến**: Ngắt kết nối mạng mô phỏng -> Thiết bị biên vẫn duy trì còi/quạt độc lập -> Khôi phục mạng -> ESP32 lập tức xả 20 bản ghi sự cố lên topic `smoke/history/sync`.
* **Nội dung thuyết minh (Voiceover)**:
  > *"Khi xuất hiện tình huống hỏa hoạn thực tế, hệ thống phản ứng tức thời với độ trễ dưới 150ms. Bên cạnh việc cảnh báo tại chỗ, Node-RED tự động kích hoạt webhook bắn tin nhắn trực tiếp đến Telegram Bot của lực lượng bảo vệ. Điểm đặc biệt là cơ chế Khóa an toàn PCCC ngăn chặn sơ suất tắt quạt khi khói còn dày đặc, cùng cơ chế Circular Buffer lưu giữ lịch sử khi mất kết nối mạng và đồng bộ bù ngay khi có sóng trở lại."*

---

### 🎬 Phân cảnh 5: Tổng kết Nghiệm thu & Lời cảm ơn (5:30 – 6:00)
* **Người trình bày**: Cả 3 thành viên nhóm.
* **Hình ảnh hiển thị**: Slide tổng kết 100% tiêu chí nghiệm thu theo File Excel Bộ môn, cùng bảng kết quả chạy script kiểm thử tự động 63/63 Test Cases PASS.
* **Nội dung thuyết minh (Voiceover)**:
  > *"Kính thưa Thầy, hệ thống Báo khói Cảnh báo sớm của Nhóm 09 đã hoàn thành toàn diện toàn bộ các yêu cầu khắt khe từ Tuần 1 đến Tuần 9 theo đúng Đề cương Kế hoạch 10 tuần 60 giờ của Bộ môn. Hệ thống đã vượt qua 63 Test Cases tự động với tỷ lệ đạt 100%, sẵn sàng cho buổi bảo vệ nghiệm thu chính thức tại Tuần 10. Nhóm 09 xin chân thành cảm ơn Thầy Võ Hoàng Hải đã tận tình hướng dẫn và định hướng cho nhóm trong suốt thời gian qua!"*

---

## 3. CHECKLIST KỸ THUẬT PHỤC VỤ QUÁ TRÌNH QUAY VIDEO
- [x] Dự án Wokwi đang ở trạng thái sẵn sàng, kết nối ổn định tới `broker.emqx.io`.
- [x] Node-RED flow đã nạp sẵn 5 Business Rules và cấu hình Telegram Bot Token hợp lệ.
- [x] Web Dashboard chạy mượt mà trên trình duyệt với đầy đủ Chart.js và âm thanh Web Audio API.
- [x] Điện thoại / Telegram Desktop sẵn sàng nhận tin nhắn thông báo tức thời.
- [x] Phần mềm quay màn hình chuẩn bị sẵn (OBS Studio / Bandicam thiết lập 1080p 60fps).

