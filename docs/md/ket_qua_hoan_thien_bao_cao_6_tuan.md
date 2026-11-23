# BÁO CÁO TỔNG KẾT HOÀN THIỆN TÀI LIỆU TIẾN ĐỘ & BÁO CÁO TỔNG 6 TUẦN

**Đề tài 04:** Hệ thống báo khói cảnh báo sớm (Smart Early Smoke Detection System)  
**Nhóm sinh viên thực hiện:** Nhóm 09 (Mã nhóm phân bổ: N09) – Lớp IoT K12  
**Khoa:** Công nghệ Thông tin – Trường Đại học Công Thương TP.HCM (HUIT)  
**Giảng viên hướng dẫn:** ThS. Võ Hoàng Hải  
**Môn học:** IT4735 – An toàn và Bảo mật IoT / Đồ án IoT Kế hoạch 10 tuần – 60 giờ  

---

## 1. TỔNG QUAN KẾT QUẢ THỰC HIỆN

Theo góp ý của Giảng viên hướng dẫn về việc bổ sung bảng phân tích nguy cơ, khả năng bị tấn công dựa trên **Slide 12 và Slide 21** của tài liệu bài giảng [An toàn và Bảo mật IoT.pdf](file:///e:/IoT/DoAn/docs/pdf/An%20to%C3%A0n%20v%C3%A0%20B%E1%BA%A3o%20m%E1%BA%ADt%20IoT.pdf), Nhóm 09 đã hoàn thành đồng bộ toàn diện trên hai trục tài liệu:

1. **Bổ sung Ma trận nguy cơ bảo mật chuyên sâu theo từng tầng công nghệ** vào 4 file Báo cáo tiến độ tuần tương ứng:
   - **Tuần 3 (Tầng 1 - Sensor & Embedded Logic):** Nguy cơ cổng UART/JTAG, nạp trộm firmware, tràn số, eFuse.
   - **Tuần 4 (Tầng 2 - Network & Connectivity MQTT):** Nguy cơ Sniffing cleartext, Fake Broker, MQTT SYN/Broker Flood, rò rỉ Token.
   - **Tuần 5 (Tầng 3 - Middleware / Automation Engine):** Nguy cơ giả mạo dữ liệu PPM, bão tin nhắn DoS, Relay Chattering Attack, Fake Node.
   - **Tuần 6 (Tầng 4 - Application / Platform):** Nguy cơ leo thang đặc quyền RBAC, lỗ hổng Web XSS/Injection, rò rỉ WebSocket, nguy cơ tắt quạt khi đang cháy.

2. **Hoàn thiện Báo cáo tổng hợp 6 tuần** ([PhanTichBaiToan_KienTruc_HOANCHINH_v4.docx](file:///e:/IoT/DoAn/docs/word/PhanTichBaiToan_KienTruc_HOANCHINH_v4.docx)):
   - Tích hợp liền mạch từ **Tuần 1 đến Tuần 6** (gồm 7 Phần lớn, 26 Chương nội dung).
   - Thiết lập riêng **PHẦN VII (Chương 24, 25, 26)** làm chương chuyên đề bảo mật toàn diện: Bảng ma trận Slide 12, Bảng 6 kịch bản tấn công Slide 21 và Bảng đối chiếu OWASP IoT Top 10.
   - Bổ sung **Phần Phụ lục** với Bảng 15 Test cases Pass 100%, đo kiểm độ trễ E2E và hướng dẫn vận hành.

---

## 2. HỆ THỐNG MA TRẬN BẢO MẬT THEO SLIDE 12 VÀ SLIDE 21

### 2.1. Ma trận Phân loại Nguy cơ & Yêu cầu Bảo mật IoT (Slide 12)

| Nhóm nguy cơ (Slide 12) | Định nghĩa theo bài giảng | Yêu cầu vi phạm | Biện pháp đối ứng trên Hệ thống Báo khói (Đề tài 04) |
| :--- | :--- | :--- | :--- |
| **Capture (Thu thập trái phép)** | Nghe lén, chụp bắt dữ liệu cảm biến, trích xuất mã nhị phân firmware hoặc khóa xác thực. | **Confidentiality (Bí mật)** | Mã hóa MQTTS TLS cổng 8883 / HTTPS / WSS cổng 8084; Khóa eFuse JTAG; Quản lý Token phân quyền RBAC. |
| **Disrupt (Làm gián đoạn/tê liệt)** | Tấn công từ chối dịch vụ (DoS/DDoS), làm nghẽn Broker, ngắt kết nối mạng, cạn kiệt pin hoặc rung lắc rơ-le (Chattering). | **Availability (Sẵn sàng)** | Watchdog Timer phần cứng (WDT 5s); Thuật toán tự kết nối lại Non-blocking; Rule 3 Hysteresis trễ 20s chống hỏng rơ-le; Rate Limiting 30s. |
| **Manipulate (Thao túng dữ liệu)** | Chèn ép ngưỡng cảm biến sai lệch, sửa đổi tin báo cháy (*Suppressed Alarm*), tiêm lệnh điều khiển khống tắt quạt PCCC. | **Integrity (Toàn vẹn)** & **Authenticity (Xác thực)** | Bộ lọc trung vị (Median Filter); Range Check miền giá trị (0 - 10.000 PPM); Session Key (Slide 65); Khóa an toàn PCCC (Emergency Override Guard). |

### 2.2. Bảng Phân tích 6 Dạng Tấn công Hạ tầng (Slide 21)

| Dạng tấn công (Slide 21) | Nhóm nguy cơ | Yêu cầu vi phạm | Kịch bản rủi ro trên Hệ thống Báo khói | Mức độ | Biện pháp kỹ thuật đã hiện thực |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Fake Control Server (Máy chủ điều khiển giả)** | Manipulate, Capture | Authenticity, Integrity | Giả mạo DNS/ARP để ESP32 kết nối nhầm Broker lạ -> Kẻ tấn công chặn tin báo cháy thật, phát lệnh khống. | **NGUY CẤP** | Xác thực máy chủ TLS, Certificate Pinning, Whitelist thiết bị & cấp Session Key theo phiên (Slide 65). |
| **2. Cổng mở trên thiết bị (Device open ports)** | Disrupt, Capture | Availability, Confidentiality | Quét cổng mở Telnet/HTTP trên ESP32, cắm dây cổng UART/JTAG đọc trộm Flash trích xuất khóa bí mật. | **CAO** | ESP32 chỉ chạy Outbound Client (đóng cổng lắng nghe); đốt eFuse khóa JTAG; mã hóa Flash SPI. |
| **3. Cổng mở trên máy chủ (Server open ports)** | Disrupt, Capture | Availability, Confidentiality | Tấn công SYN Flood, DoS / DDoS làm tê liệt Broker MQTT cổng 1883 hoặc Node-RED cổng 1880. | **CAO** | Tường lửa UFW/Cloud Security Groups; Rate Limiting 30s chống bão tin nhắn; Non-blocking Auto-reconnect. |
| **4. Đánh cắp thông tin xác thực (Steal Credential)** | Manipulate, Capture | Authenticity, Confidentiality | Đánh cắp token qua sniffing -> Chiếm quyền điều khiển tắt quạt khi đang cháy. | **NGUY CẤP** | Role-Based Access Control (RBAC 3 vai trò); Khóa an toàn PCCC (Emergency Override); Session Key ngắn hạn. |
| **5. Chèn cấu hình/firmware xấu (Inject bad config/fw)** | Manipulate, Disrupt | Integrity, Availability | Nạp đè firmware backdoor hoặc đổi ngưỡng báo động lên 10.000 PPM để còi không bao giờ hú. | **NGUY CẤP** | Secure Boot V2 ký số RSA-3072; Range Check miền giá trị tham số cấu hình; Re-escalation Guard bảo vệ. |
| **6. Nghe lén gói tin trên mạng (Sniff data on network)** | Capture | Confidentiality | Bắt trộm gói tin cleartext trên Wi-Fi -> Lộ dữ liệu nồng độ khói, phục vụ tấn công Replay. | **TRUNG BÌNH** | Mã hóa toàn bộ đường truyền bằng MQTTS TLS cổng 8883 / HTTPS / WSS cổng 8084; Wi-Fi WPA2/WPA3. |

---

## 3. DANH MỤC TÀI LIỆU WORD & MARKDOWN ĐÃ HOÀN THIỆN

### 3.1. Báo cáo Tổng hợp 6 Tuần Hoàn chỉnh
- **Tập tin:** [PhanTichBaiToan_KienTruc_HOANCHINH_v4.docx](file:///e:/IoT/DoAn/docs/word/PhanTichBaiToan_KienTruc_HOANCHINH_v4.docx)
- **Dung lượng:** 255.2 KB | **Đoạn văn (Paragraphs):** 1,144 | **Bảng biểu (Tables):** 25 bảng.
- **Cấu trúc:**
  - **Phần I:** Phân tích bài toán, Use case, BOM, Kiến trúc 4 tầng (Tuần 1).
  - **Phần II:** Thiết kế mạch Wokwi V1, Wiring, Firmware cơ bản, Milestone M1 (Tuần 2).
  - **Phần III:** Firmware V2 nâng cao, Calib 2 điểm, Timer phi chặn, Bộ lọc, FSM nhúng (Tuần 3).
  - **Phần IV:** Tầng 2 Network MQTT, Topic tree, Uplink/Downlink, LWT, Milestone M2 (Tuần 4).
  - **Phần V:** Tầng 3 Middleware Node-RED, FSM 5 trạng thái, 5 Core Rules, Fleet Whitelist, Audit Trail (Tuần 5).
  - **Phần VI:** Tầng 4 Application, Web Dashboard Cyber-Safety, Chart.js, Telegram, RBAC, Khóa an toàn PCCC, Milestone M3 (Tuần 6).
  - **Phần VII:** Chương Chuyên đề Toàn diện: Phân tích Nguy cơ & Khả năng bị tấn công (Slide 12 & 21, OWASP IoT Top 10).
  - **Phần Phụ lục:** Bảng 15 Test cases tự động Pass 100%, Phân tích độ trễ E2E, Hướng dẫn vận hành hệ thống.

### 3.2. Báo cáo Tiến độ từng tuần (Word)
1. [PHẦN 3.docx](file:///e:/IoT/DoAn/docs/word/PH%E1%BA%A6N%203.docx) (44.4 KB): Tiến độ Tuần 3 – Tầng 1 Sensor & Logic nhúng (Đã bổ sung Ma trận bảo mật Tầng 1 theo Slide 12 & 21).
2. [Phần 4.docx](file:///e:/IoT/DoAn/docs/word/Ph%E1%BA%A7n%204.docx) (54.6 KB): Tiến độ Tuần 4 – Tầng 2 Network / Connectivity MQTT (Đã bổ sung Ma trận bảo mật Tầng 2 theo Slide 12 & 21).
3. [Phần 5.docx](file:///e:/IoT/DoAn/docs/word/Ph%E1%BA%A7n%205.docx) (50.7 KB): Tiến độ Tuần 5 – Tầng 3 Middleware / Automation Node-RED (Đã bổ sung Ma trận bảo mật Tầng 3 theo Slide 12 & 21).
4. [Phần 6.docx](file:///e:/IoT/DoAn/docs/word/Ph%E1%BA%A7n%206.docx) (45.2 KB): Tiến độ Tuần 6 – Tầng 4 Application / Platform (Đã bổ sung Ma trận bảo mật Tầng 4 theo Slide 12 & 21).

### 3.3. Các Bảng Kịch bản Kiểm thử & Tiến độ
1. [Bang_Test_Case_Tuan4_Nhom04.docx](file:///e:/IoT/DoAn/docs/word/Bang_Test_Case_Tuan4_Nhom04.docx): 10 Test cases MQTT.
2. [Bang_Test_Case_Tuan5_Nhom04.docx](file:///e:/IoT/DoAn/docs/word/Bang_Test_Case_Tuan5_Nhom04.docx): 12 Test cases Middleware FSM & 5 Core Rules.
3. [Bang_Test_Case_Tuan6_Nhom04.docx](file:///e:/IoT/DoAn/docs/word/Bang_Test_Case_Tuan6_Nhom04.docx): 15 Test cases Toàn diện 4 tầng E2E.
4. [Danh_sach_58_de_tai_IoT_Ke_hoach_10_tuan_60h.xlsx](file:///e:/IoT/DoAn/docs/xlsx/Danh_sach_58_de_tai_IoT_Ke_hoach_10_tuan_60h.xlsx): Đã cập nhật trạng thái "Hoàn thành 100% - Đạt Milestone M3" cho Đề tài 04 - Nhóm 09 (N09).
5. [BAOCAO_TIENDO_TUAN5.md](file:///e:/IoT/DoAn/docs/md/BAOCAO_TIENDO_TUAN5.md) và [BAOCAO_TIENDO_TUAN6.md](file:///e:/IoT/DoAn/docs/md/BAOCAO_TIENDO_TUAN6.md): Đã đồng bộ mục Phân tích nguy cơ bảo mật Slide 12 & 21.

---

## 4. KẾT LUẬN & ĐÁNH GIÁ NGHIỆM THU

Bộ tài liệu của Nhóm 09 (N09) hiện đã đáp ứng trọn vẹn:
- Đúng chuẩn học thuật HUIT (Font Times New Roman, cấu trúc chương mục rõ ràng, bảng biểu viền màu đồng bộ).
- Bám sát yêu cầu nghiệp vụ của Giảng viên hướng dẫn ThS. Võ Hoàng Hải về an toàn và bảo mật IoT (Slide 12, 21 và Slide 65).
- Tích hợp đầy đủ cả 6 tuần nghiên cứu và thực nghiệm thực tế, sẵn sàng cho các đợt kiểm tra và đánh giá tiến độ môn học.

