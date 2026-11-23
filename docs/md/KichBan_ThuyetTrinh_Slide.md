# KỊCH BẢN PHÂN CHIA THUYẾT TRÌNH BÁO CÁO ĐỒ ÁN IoT (TUẦN 1 & TUẦN 2)
## Đề tài: Hệ Thống Báo Khói Cảnh Báo Sớm — Nhóm N09 (Đề tài 4)
**Tài liệu Slide đối chiếu:** `W2 - Báo cáo Đồ án Môn học Hệ thống Báo khói Cảnh báo sớm (IoT).pptx.pptx` (Tổng cộng 32 slide)  
**Giảng viên hướng dẫn:** ThS. Võ Hoàng Hải  
**Thành viên:**
1. Nguyễn Vĩnh Khang (MSSV: 2001230381) – Nhóm trưởng
2. Nguyễn Văn Đức (MSSV: 2001230186) – Thành viên
3. Nguyễn Văn Mãnh (MSSV: 2001230503) – Thành viên

---

### I. NGUYÊN TẮC PHÂN CHIA THUYẾT TRÌNH TỐI ƯU
1. **Khối lượng cân bằng:** Đảm bảo cả 3 thành viên đều có thời lượng trình bày tương đương nhau và nắm vững các phần trọng yếu của đồ án.
2. **Nguyên tắc "Mỗi người lên đúng 1 lần cho từng tuần":** Không đổi micro / đổi ca qua lại giữa các slide để tránh lúng túng, mất thời gian chuyển giao trước Hội đồng / Giảng viên.

---

### II. PHÂN CHIA CHI TIẾT TỪNG TUẦN VÀ SLIDE

```
[TUẦN 1: TỔNG QUAN & KIẾN TRÚC HỆ THỐNG]
Slide 01 - 07: Nguyễn Vĩnh Khang  (Bối cảnh, Mục tiêu, Phạm vi, Use Cases)
Slide 08 - 14: Nguyễn Văn Mãnh   (Kịch bản PCCC, Cảm biến/Chấp hành, Hysteresis, 4 Tầng)
Slide 15 - 21: Nguyễn Văn Đức    (Phân xử quyền, MQTT Tree, GPIO, BOM, Nghiệm thu W1)

[TUẦN 2: SIMULATION TẦNG 1 & FIRMWARE PROTOTYPE]
Slide 22 - 24: Nguyễn Văn Mãnh   (Mục tiêu Tuần 2, 18h kỹ thuật, Phân công cá nhân)
Slide 25 - 27: Nguyễn Văn Đức    (Linh kiện Wokwi, Mô phỏng Quạt LED + Relay, Bảng đấu dây)
Slide 28 - 32: Nguyễn Vĩnh Khang  (Firmware Non-blocking, Lộ trình W3/W7, Milestone M1, Q&A)
```

---

### III. NỘI DUNG THUYẾT TRÌNH CHI TIẾT THEO TỪNG THÀNH VIÊN

#### 🎤 GIAI ĐOẠN 1: BÁO CÁO TUẦN 1 (SLIDE 1 ĐẾN 21)

##### 1. Nguyễn Vĩnh Khang (Slide 1 $\rightarrow$ 7) — Mở đầu & Đặc tả Bài toán
* **Slide 1 (Bìa):** Chào Thầy và các bạn, giới thiệu tên đề tài "Hệ Thống Báo Khói Cảnh Báo Sớm" (Nhóm N09, Đề tài 4, GVHD: ThS. Võ Hoàng Hải) cùng 3 thành viên nhóm.
* **Slide 2 (Bối cảnh thực tiễn):** Trình bày thực trạng cháy nổ tại các khu dân cư, nhà xưởng và chung cư; nêu bật yêu cầu cấp bách của hệ thống cảnh báo sớm giảm thiểu thiệt hại nhân mạng.
* **Slide 3 (Mục tiêu dự án):** Phát hiện sớm khói và khí cháy, kích hoạt báo động tại chỗ (còi, quạt hút) kết hợp đẩy dữ liệu lên Cloud giám sát từ xa.
* **Slide 4 (Phạm vi Scope In/Out):** Rõ ràng ranh giới đồ án — những gì làm trong 10 tuần (mô phỏng, MQTT, Node-RED, Blynk) và những gì thuộc phạm vi mở rộng.
* **Slide 5 & 6 (Đặc tả Use Cases):** Tổng quan 7 Use Cases chính của hệ thống từ giám sát cảm biến đến điều khiển chấp hành và cảnh báo người dùng.
* **Slide 7 (Chi tiết UC01):** Phân tích luồng nghiệp vụ giám sát nồng độ khói thời gian thực.
* *Chuyển lời:* Mời bạn Nguyễn Văn Mãnh tiếp tục trình bày về kịch bản vận hành và các tầng kỹ thuật.

##### 2. Nguyễn Văn Mãnh (Slide 8 $\rightarrow$ 14) — Kịch bản PCCC & Thiết bị Ngoại vi
* **Slide 8 (Chi tiết UC03):** Đặc tả chức năng kích hoạt cảnh báo cháy khẩn cấp.
* **Slide 9 (Kịch bản tự động tại chỗ):** Luồng xử lý khi nồng độ khói vượt ngưỡng thì còi hú và quạt hút tự kích hoạt ngay lập tức.
* **Slide 10 (Kịch bản điều khiển từ xa):** Luồng người dùng từ xa bật/tắt thiết bị qua ứng dụng di động khi cần thông gió.
* **Slide 11 (Cảm biến đầu vào):** Giới thiệu nguyên lý cảm biến khói MQ-2 và cảm biến nhiệt ẩm DHT22.
* **Slide 12 (Cơ cấu chấp hành):** Giới thiệu Còi hú báo động Buzzer và Quạt thông gió hút khói (kích qua Relay).
* **Slide 13 (Thuật toán trễ Hysteresis):** Giải thích vùng đệm an toàn (Ngưỡng bật $\ge 400\text{ PPM}$, ngưỡng tắt $\le 300\text{ PPM}$) để chống hiện tượng bật/tắt liên tục làm cháy tiếp điểm Relay.
* **Slide 14 (Kiến trúc 4 tầng IoT):** Phân tích 4 tầng: Sensing/Physical $\rightarrow$ Network $\rightarrow$ Middleware $\rightarrow$ Application.
* *Chuyển lời:* Mời bạn Nguyễn Văn Đức trình bày về phân xử quyền điều khiển và kế hoạch nghiệm thu Tuần 1.

##### 3. Nguyễn Văn Đức (Slide 15 $\rightarrow$ 21) — Phân xử Quyền, Truyền thông & Kế hoạch
* **Slide 15 (Ma trận phân xử quyền ưu tiên):** Giải thích nguyên tắc an toàn PCCC: Khi có cháy ($\text{PPM} \ge 400$), rule tự động luôn thắng tuyệt đối và khóa quyền điều khiển từ xa/thủ công; khi an toàn ($\text{PPM} \le 300$), trả quyền cho người dùng.
* **Slide 16 (Luồng dữ liệu Uplink / Downlink):** Luồng gửi dữ liệu cảm biến lên Server và luồng lệnh điều khiển từ App xuống thiết bị.
* **Slide 17 (Cấu trúc MQTT Topic Tree):** Trình bày cây 6 topic MQTT chuẩn hóa của nhóm (`smoke/telemetry/...`, `smoke/cmd/...`).
* **Slide 18 (Bảng phân chân GPIO Mapping):** Giới thiệu kết nối phần cứng trên vi điều khiển ESP32.
* **Slide 19 (Bảng kê linh kiện BOM):** Bảng dự toán kinh phí linh kiện nhóm A và nhóm B.
* **Slide 20 (Tiến độ Roadmap 10 tuần):** Lộ trình 60h kỹ thuật theo đúng chuẩn phân bổ môn học.
* **Slide 21 (Nghiệm thu Tuần 1):** Tổng kết hoàn thành 100% mục tiêu Tuần 1 và bàn giao sang Tuần 2.

---

#### 🎤 GIAI ĐOẠN 2: BÁO CÁO TUẦN 2 (SLIDE 22 ĐẾN 32)

##### 1. Nguyễn Văn Mãnh (Slide 22 $\rightarrow$ 24) — Mục tiêu & Phân bổ Công việc Tuần 2
* **Slide 22 (Mục tiêu kỹ thuật Tuần 2):** Xây dựng thành công bản mô phỏng Tầng 1 (Sensing/Actuators) trên Wokwi, đọc cảm biến và điều khiển chấp hành đạt chuẩn Milestone M1 (10% tiến độ).
* **Slide 23 (Phân bổ 18h kỹ thuật):** Cấu trúc thời gian 6h/sinh viên (2h dựng mạch, 2h đọc sensor, 2h điều khiển actuator & kiểm tra wiring).
* **Slide 24 (Phân công nhiệm vụ cá nhân):** Bảng phân công chi tiết công việc cho Khang, Đức, Mãnh cùng vai trò Test Lead chéo.
* *Chuyển lời:* Mời bạn Nguyễn Văn Đức trình bày chi tiết về thiết kế mạch mô phỏng trên Wokwi.

##### 2. Nguyễn Văn Đức (Slide 25 $\rightarrow$ 27) — Thiết Kế Mạch Wokwi & Đấu Nối Ngoại Vi
* **Slide 25 (Cấu hình linh kiện trên Wokwi):** Bố trí ESP32, MQ-2, DHT22, Buzzer, Relay 1 kênh và nút nhấn Pushbutton.
* **Slide 26 (Giải pháp mô phỏng Quạt DC bằng Relay + Đèn LED):** Phân tích sáng kiến kỹ thuật: Vì Wokwi không có động cơ quạt DC quay, nhóm dùng tiếp điểm thường mở (NO) của Relay đóng điện cho đèn LED xanh sáng rực rỡ, vừa an toàn vừa trực quan hóa chính xác trạng thái quạt.
* **Slide 27 (Bảng sơ đồ đấu nối Wiring Pinout):** Chi tiết từng mối nối, cấp nguồn 3.3V/5V và mã màu dây quốc tế.
* *Chuyển lời:* Mời nhóm trưởng Nguyễn Vĩnh Khang trình bày về thiết kế firmware, nghiệm thu Milestone M1 và giải đáp câu hỏi.

##### 3. Nguyễn Vĩnh Khang (Slide 28 $\rightarrow$ 32) — Firmware, Nghiệm Thu Milestone M1 & Q&A
* **Slide 28 (Thiết kế Firmware Tầng 1):** Kiến trúc Non-blocking Timer dùng `millis()`, cơ chế chống nghẽn FreeRTOS, bộ lọc trung bình ADC và điều khiển còi bằng hàm `tone()`.
* **Slide 29 (Lộ trình kỹ thuật Tuần 3 & Tuần 7):** Giới thiệu định hướng phát triển thuật toán Moving Average Filter, FSM ở Tuần 3 và Sensor Fusion ở Tuần 7.
* **Slide 30 (Checklist nghiệm thu Milestone M1):** Đối chiếu 9 tiêu chí kỹ thuật đều đạt 100% (Pass baseline).
* **Slide 31 (Bàn giao sản phẩm):** Giới thiệu link Wokwi Public, mã nguồn GitHub và tài liệu kỹ thuật hoàn chỉnh.
* **Slide 32 (Lời cảm ơn & Q&A):** Cảm ơn Thầy và các bạn đã lắng nghe, mời Thầy và Hội đồng đặt câu hỏi phản biện.

---

### IV. 4 LUẬN ĐIỂM KỸ THUẬT PHẢN BIỆN CHẮC CHẮN VỚI GIẢNG VIÊN

1. **Về việc Slide ghi Potentiometer còn mạch dùng `wokwi-gas-sensor`:**
   * *Trả lời:* Trong tài liệu ban đầu, biến trở Potentiometer được đề xuất như một giải pháp mô phỏng điện áp tương tự. Tuy nhiên, để sát với thực tế PCCC, nhóm đã sử dụng linh kiện chuyên dụng `wokwi-gas-sensor` có thuộc tính `ppm` và thanh trượt nồng độ khí, giúp mô phỏng chân thực quá trình phản ứng oxy hóa của cảm biến khói MQ-2.
2. **Về việc cấp nguồn 3.3V cho MQ-2 trên Wokwi thay vì 5V:**
   * *Trả lời:* Trên Wokwi, bộ ADC của ESP32 kẹp trần ở 3.3V (12-bit). Nếu cấp 5V, nồng độ trên 270 PPM sẽ làm AOUT vượt 3.3V gây bão hòa ADC (clipping ở 4095), khiến dải đo từ 300 đến 100.000 PPM bị mất tác dụng. Do đó mô phỏng cấp 3.3V là tối ưu. Khi triển khai mạch thật, nhóm sẽ cấp nguồn 5V nung cuộn sấy và dùng mạch chia áp $R_1=10\text{k}\Omega, R_2=20\text{k}\Omega$ (tỷ lệ 0.667) để đưa điện áp về dải $0 - 3.3\text{V}$ an toàn cho vi điều khiển.
3. **Về độ trễ và hiện tượng khói giảm từ từ:**
   * *Trả lời:* Đây là đặc tính vật lý buồng khí (Gas Dissipation) được Wokwi mô phỏng kết hợp với vùng đệm trễ Hysteresis (400/300 PPM) của nhóm. Vùng trễ này giúp bảo vệ cơ học cho Relay không bị đóng ngắt liên tục (chattering) khi nồng độ khói dao động quanh ngưỡng báo động.
4. **Về phương trình đặc tuyến Power-Law và hiệu chuẩn 2 điểm:**
   * *Trả lời:* Cảm biến SnO2 có đặc tuyến phi tuyến $PPM = A \cdot (R_s/R_0)^B$. Do module gas sensor của Wokwi là closed-source, nhóm không dùng hệ số lý thuyết của datasheet thật mà áp dụng phương pháp Hiệu chuẩn thực nghiệm 2 điểm (tại 200 PPM và 1000 PPM), hồi quy log-log để tìm ra hệ số thực ($A = 741.6, B = -2.444$). Nhờ vậy chỉ số đo lường trên Terminal khớp 100% với nồng độ trên Wokwi.
