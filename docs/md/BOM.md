# BẢNG DỰ TOÁN CHI PHÍ LINH KIỆN & VẬT TƯ (BILL OF MATERIALS - BOM)
## Đề tài: Hệ Thống Báo Khói Cảnh Báo Sớm
**Nhóm:** N09 | **Đề tài:** 4 | **Giảng viên hướng dẫn:** ThS. Võ Hoàng Hải  
**Thành viên:** Nguyễn Vĩnh Khang (Nhóm trưởng), Nguyễn Văn Đức, Nguyễn Văn Mãnh  

---

### I. NGUYÊN TẮC THIẾT KẾ & DỰ TOÁN
1. **Phân cấp linh kiện:** Chia làm 2 nhóm rõ rệt:
   - **Nhóm A (Linh kiện mạch chính):** Các linh kiện cốt lõi của Tầng 1 (Sensing & Actuator).
   - **Nhóm B (Vật tư phụ trợ thực tế):** Phục vụ thi công đóng hộp, cấp nguồn, chống nhiễu và dự phòng hỏng hóc khi triển khai mạch thật.
2. **Hệ số dự phòng:** Lập 2 cột số lượng: **SL Tối thiểu (chạy demo)** và **SL Khuyến nghị (có linh kiện dự phòng)** để tránh gián đoạn tiến độ khi đo chập cháy linh kiện nhạy cảm (như ESP32, MQ2, DHT22).
3. **Nguồn giá tham khảo:** Căn cứ theo báo giá bán lẻ tại thị trường Việt Nam (Hshop.vn, Shopee, Thegioiic, IC Đây Rồi) thời điểm Quý 3/2026.

---

### II. BẢNG KÊ CHI TIẾT 18 HẠNG MỤC LINH KIỆN (BOM)

| STT | Tên Linh Kiện / Vật Tư | Thông Số Kỹ Thuật Chính | Mục Đích Sử Dụng Trong Hệ Thống | SL Tối Thiểu | SL Khuyến Nghị | Đơn Giá Tham Khảo (VNĐ) | Thành Tiền Khuyến Nghị (VNĐ) | Nơi Mua / Tham Khảo |
|:---:|:---|:---|:---|:---:|:---:|:---:|:---:|:---|
| **A** | **NHÓM LINH KIỆN CHÍNH (CORE HARDWARE)** | | | | | | | |
| 1 | **ESP32 DevKit V1 (ESP-WROOM-32)** | Dual-core Tensilica LX6 240MHz, Wi-Fi 2.4GHz + BLE, 38 chân, 520KB SRAM, 4MB Flash | Vi điều khiển trung tâm (MCU): Đọc cảm biến, xử lý local rule, kết nối Wi-Fi/MQTT | 1 | 2 | 115.000 | 230.000 | Hshop.vn / Shopee |
| 2 | **Cảm biến khí gas / khói MQ-2** | Cảm biến SnO2 nung nóng, phát hiện LPG, khói, cồn, Propane, ngõ ra AOUT (0-5V) và DOUT | Đo nồng độ khói phục vụ cảnh báo sớm cháy nổ | 1 | 2 | 35.000 | 70.000 | Hshop.vn |
| 3 | **Cảm biến nhiệt độ & độ ẩm DHT22 (AM2302)** | Giao tiếp 1-Wire, dải đo -40 đến +80°C (±0.5°C), 0-100% RH (±2%), điện áp 3.3V-5V | Giám sát nhiệt ẩm môi trường, tăng độ tin cậy cảnh báo cháy | 1 | 2 | 75.000 | 150.000 | Hshop.vn |
| 4 | **Còi báo động Active Buzzer 5V** | Còi chủ động (có mạch dao động sẵn), âm lượng 85dB @ 10cm, tần số ~2.3kHz | Cảnh báo âm thanh tại chỗ khi khói vượt ngưỡng | 1 | 2 | 8.000 | 16.000 | Hshop.vn / Linh kiện số |
| 5 | **Module Relay 1 kênh 5V (Opto cách ly)** | Kích mức Cao/Thấp (High/Low level trigger), tải tối đa AC 250V/10A hoặc DC 30V/10A | Đóng ngắt tiếp điểm cấp điện cho quạt hút khói | 1 | 2 | 18.000 | 36.000 | Hshop.vn |
| 6 | **Đèn LED báo trạng thái 5mm** | Siêu sáng, màu Xanh dương (hoặc Xanh lá), điện áp 2.8V - 3.2V, dòng 20mA | Mô phỏng trạng thái quay của Quạt hút DC (LED FAN) | 2 | 5 | 2.000 | 10.000 | Cửa hàng linh kiện |
| 7 | **Nút nhấn 4 chân (Tactile Pushbutton)** | Kích thước 12x12x7.3mm hoặc 6x6mm, cơ chế nhấn nhả, kèm nắp tròn | Công tắc thủ công bật/tắt quạt (Manual Fan Override) | 1 | 3 | 3.000 | 9.000 | Cửa hàng linh kiện |
| **B** | **NHÓM VẬT TƯ PHỤ TRỢ & THI CÔNG MÔ HÌNH** | | | | | | | |
| 8 | **Testboard cắm mạch (Breadboard MB-102)** | 830 lỗ cắm, có dải nguồn đôi hai bên, đế keo xốp | Cắm thử nghiệm mạch và đấu nối không cần hàn mạch | 1 | 1 | 32.000 | 32.000 | Hshop.vn |
| 9 | **Dây cắm Breadboard Đực - Đực (Male-Male)** | Chiều dài 20cm, lõi đồng nhiều sợi, tép 40 sợi | Đấu nối giữa các chân linh kiện trên testboard | 1 tép | 1 tép | 18.000 | 18.000 | Shopee / Hshop |
| 10 | **Dây cắm Breadboard Đực - Cái (Male-Female)** | Chiều dài 20cm, tép 40 sợi | Đấu nối từ chân cắm ESP32/Relay/Sensor ra ngoài | 1 tép | 1 tép | 18.000 | 18.000 | Shopee / Hshop |
| 11 | **Điện trở 10 kΩ (1/4W, sai số 1%)** | Điện trở màng kim loại, công suất 0.25W | Mạch chia áp an toàn R1 (5V -> 3.3V) cho chân AOUT MQ-2 | 5 | 10 | 500 | 5.000 | [CẦN KHẢO SÁT TIỆM ĐIỆN TỬ] |
| 12 | **Điện trở 20 kΩ (1/4W, sai số 1%)** | Điện trở màng kim loại, công suất 0.25W | Mạch chia áp an toàn R2 nối mass cho chân AOUT MQ-2 | 5 | 10 | 500 | 5.000 | [CẦN KHẢO SÁT TIỆM ĐIỆN TỬ] |
| 13 | **Điện trở 220 Ω (1/4W)** | Điện trở màng carbon/kim loại 220 Ohm | Điện trở hạn dòng bảo vệ đèn LED báo trạng thái | 5 | 10 | 500 | 5.000 | [CẦN KHẢO SÁT TIỆM ĐIỆN TỬ] |
| 14 | **Cáp nạp Micro-USB chống nhiễu** | Cáp truyền dữ liệu 4 dây chuẩn (Data + Power), chiều dài 1m | Nạp chương trình từ máy tính và cấp nguồn thử nghiệm | 1 | 1 | 25.000 | 25.000 | Cửa hàng phụ kiện |
| 15 | **Nguồn Adapter 5V - 2A (DC Jack / MicroUSB)** | Ngõ vào 100-240V AC, ngõ ra 5V DC 2A ổn dòng | Cấp nguồn độc lập liên tục cho hệ thống khi demo thật | 1 | 1 | 45.000 | 45.000 | Hshop.vn |
| 16 | **Quạt hút khói mini DC 5V (40x40x10mm)** | Động cơ Brushless DC 5V 0.15A, tốc độ gió 5000 RPM | Quạt hút khói vật lý thật khi demo ngoài mô hình | 1 | 1 | 25.000 | 25.000 | Shopee |
| 17 | **Hộp nhựa kỹ thuật bảo vệ mạch (Box ABS)** | Hộp nhựa ABS hoặc nắp mica trong suốt (150x100x50mm) | Đóng gói cố định phần cứng demo, đảm bảo mỹ thuật PCCC | 1 | 1 | 55.000 | 55.000 | Tiệm cơ khí / Shopee |
| 18 | **Vật tư phụ (Băng keo điện, ống co nhiệt, thiếc)** | Vật tư tiêu hao hỗ trợ cách điện mối nối | Bảo vệ an toàn chống chập ngắn mạch điện | 1 bộ | 1 bộ | 25.000 | 25.000 | Cửa hàng kim khí |

---

### III. TỔNG HỢP KINH PHÍ DỰ KIẾN
* **Phương án Tối thiểu (chỉ mua vừa đủ số lượng chạy):** $\approx 485.000\text{ VNĐ}$
* **Phương án Khuyến nghị (mua dự phòng MCU, cảm biến, mạch chia áp an toàn):** $\approx 720.000 - 820.000\text{ VNĐ}$
* **Chi phí bình quân trên mỗi thành viên (Nhóm 3 người):** $\approx 240.000 - 270.000\text{ VNĐ/người}$

---

### IV. GHI CHÚ KỸ THUẬT QUAN TRỌNG KHI TRIỂN KHAI PHẦN CỨNG THẬT
1. **Nguồn cấp cảm biến MQ-2:** Cuộn nung SnO2 của MQ-2 cần dòng sưởi ấm $\sim 150\text{mA}$ ở điện áp 5V. Vì vậy, trên mạch thật **bắt buộc cấp 5V từ Adapter rời** vào chân VCC của MQ-2 (không cấp qua cổng 3.3V của ESP32 để tránh sụt áp gây reset MCU).
2. **Bảo vệ ngõ vào ADC ESP32:** Tín hiệu analog AOUT của MQ-2 khi cấp 5V có thể vượt ngưỡng 3.3V. **Bắt buộc đấu qua mạch chia điện áp** gồm $R_1 = 10\text{k}\Omega$ và $R_2 = 20\text{k}\Omega$ với tỷ lệ:
   $$V_{ADC} = V_{AOUT} \times \frac{R_2}{R_1 + R_2} = V_{AOUT} \times \frac{20}{10 + 20} = 0.667 \times V_{AOUT}$$
   Khi $V_{AOUT} = 5.0\text{V}$, điện áp vào chân GPIO34 là $3.33\text{V}$ (hoàn toàn an toàn cho ADC của ESP32).
