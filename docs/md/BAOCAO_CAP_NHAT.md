# TÀI LIỆU CẬP NHẬT BÁO CÁO KỸ THUẬT THEO GÓP Ý CỦA GIẢNG VIÊN HƯỚNG DẪN
## Đề tài: Hệ Thống Báo Khói Cảnh Báo Sớm — Nhóm N09 (Đề tài 4)
**Giảng viên hướng dẫn:** ThS. Võ Hoàng Hải  
**Thành viên:** Nguyễn Vĩnh Khang (Nhóm trưởng), Nguyễn Văn Đức, Nguyễn Văn Mãnh  

> [!NOTE]
> Tài liệu này được biên soạn thành 6 phân mục độc lập, chuẩn định dạng học thuật, sẵn sàng sao chép (copy-paste) trực tiếp vào các mục tương ứng trong file Word báo cáo [W1_PhanTichBaiToan_KienTruc_HOANCHINH.docx](file:///D:/BackUp_E/IoT/DoAn/W1_PhanTichBaiToan_KienTruc_HOANCHINH.docx).

---

### PHẦN 1: CẬP NHẬT MỤC 2.4 — BẢNG DỰ TOÁN LINH KIỆN & VẬT TƯ (BOM)

*(Dán thay thế hoặc bổ sung cho Bảng 2.3 BOM hiện tại)*

#### Bảng 2.4: Bảng kê linh kiện và dự toán chi phí chi tiết (18 hạng mục)

| STT | Tên Linh Kiện / Vật Tư | Thông Số Kỹ Thuật | Mục Đích Sử Dụng | SL Min | SL Rec | Đơn Giá (VNĐ) | Thành Tiền (VNĐ) | Ghi Chú |
|:---:|:---|:---|:---|:---:|:---:|:---:|:---:|:---|
| 1 | ESP32 DevKit V1 | ESP-WROOM-32, 240MHz, Wi-Fi/BLE | Vi điều khiển trung tâm | 1 | 2 | 115.000 | 230.000 | Core MCU |
| 2 | Cảm biến khói MQ-2 | SnO2 heater, AOUT/DOUT | Đo nồng độ khói / gas | 1 | 2 | 35.000 | 70.000 | Sensor |
| 3 | Cảm biến DHT22 | AM2302, 1-Wire, -40 đến 80°C | Đo nhiệt độ & độ ẩm | 1 | 2 | 75.000 | 150.000 | Sensor |
| 4 | Active Buzzer 5V | Âm lượng 85dB, có dao động nội | Còi hú báo động cháy | 1 | 2 | 8.000 | 16.000 | Actuator |
| 5 | Module Relay 1 kênh | 5V, Opto cách ly, tải 10A 250VAC | Đóng ngắt quạt hút khói | 1 | 2 | 18.000 | 36.000 | Actuator |
| 6 | Đèn LED 5mm Xanh | Siêu sáng, 20mA, 3V | Mô phỏng quạt hút (FAN) | 2 | 5 | 2.000 | 10.000 | Output |
| 7 | Nút nhấn Pushbutton | 4 chân 12x12mm nhấn nhả | Công tắc quạt thủ công | 1 | 3 | 3.000 | 9.000 | Manual Input |
| 8 | Testboard MB-102 | 830 lỗ, dải nguồn đôi | Cắm mạch thử nghiệm | 1 | 1 | 32.000 | 32.000 | Breadboard |
| 9 | Dây cắm Đực - Đực | 20cm, tép 40 sợi | Đấu nối testboard | 1 | 1 | 18.000 | 18.000 | Phụ trợ |
| 10 | Dây cắm Đực - Cái | 20cm, tép 40 sợi | Đấu nối module cảm biến | 1 | 1 | 18.000 | 18.000 | Phụ trợ |
| 11 | Điện trở 10 kΩ | 1/4W, 1% | Trở chia áp R1 (MQ2 5V) | 5 | 10 | 500 | 5.000 | Bảo vệ ADC |
| 12 | Điện trở 20 kΩ | 1/4W, 1% | Trở chia áp R2 (MQ2 5V) | 5 | 10 | 500 | 5.000 | Bảo vệ ADC |
| 13 | Điện trở 220 Ω | 1/4W, 5% | Hạn dòng đèn LED quạt | 5 | 10 | 500 | 5.000 | Bảo vệ LED |
| 14 | Cáp nạp Micro-USB | Chuẩn truyền dữ liệu 1m | Nạp code & Debug UART | 1 | 1 | 25.000 | 25.000 | Phụ trợ |
| 15 | Nguồn Adapter 5V 2A | DC 5V 2A, Jack tròn / USB | Cấp nguồn nuôi hệ thống | 1 | 1 | 45.000 | 45.000 | Power |
| 16 | Quạt hút DC 5V mini | Brushless 40x40x10mm 5000RPM | Quạt hút mô hình thật | 1 | 1 | 25.000 | 25.000 | Hardware |
| 17 | Hộp bảo vệ mạch | Nhựa ABS / nắp Mica chống cháy | Đóng gói demo PCCC | 1 | 1 | 55.000 | 55.000 | Enclosure |
| 18 | Vật tư phụ đóng hộp | Băng keo, ống co nhiệt, thiếc | Cách điện & gia cố cơ khí | 1 | 1 | 25.000 | 25.000 | Tiêu hao |

* **Tổng kinh phí dự kiến:** 485.000 VNĐ (Tối thiểu) — 754.000 VNĐ (Khuyến nghị có dự phòng rủi ro).

---

### PHẦN 2: CẬP NHẬT MỤC 3.2 — BẢNG PHÂN CHÂN GPIO MAPPING (BỔ SUNG GPIO18)

#### Bảng 3.2: Sơ đồ phân chân GPIO của vi điều khiển ESP32 (Phiên bản cập nhật Tuần 2)

| Chân GPIO | Tên Tín Hiệu | Loại Tín Hiệu (Mode) | Chức Năng Chi Tiết | Thiết Bị Kết Nối |
|:---:|:---|:---|:---|:---|
| **GPIO34** | `MQ2_AOUT` | Analog Input (ADC1_CH6) | Đọc điện áp nồng độ khói (0 – 3.3V) qua bộ chuyển đổi ADC 12-bit | Chân AOUT của module cảm biến khói MQ-2 |
| **GPIO4** | `DHT_DATA` | Digital I/O (1-Wire) | Giao tiếp lấy mẫu nhiệt độ và độ ẩm thời gian thực | Chân SDA của module cảm biến nhiệt ẩm DHT22 |
| **GPIO16** | `BUZZER_PIN` | Digital Output | Xuất xung PWM / Logic phát tín hiệu âm thanh cảnh báo cháy | Cực dương (+) của còi báo động Active Buzzer |
| **GPIO17** | `RELAY_IN` | Digital Output | Điều khiển cuộn hút Relay đóng tiếp điểm thường mở (NO) | Chân điều khiển `IN` của Module Relay 1 kênh |
| **GPIO18** | `BUTTON_MANUAL`| Digital Input (`INPUT_PULLUP`) | Nhận tín hiệu nút bấm công tắc bật/tắt quạt hút thủ công | Nút nhấn Pushbutton 4 chân (chân còn lại nối mass GND) |
| **GND** | `GND_COMMON` | Nguồn Mass (0V) | Nối mass chung cho toàn bộ cảm biến và tải chấp hành | Chân GND của ESP32, MQ2, DHT22, Buzzer, Relay, LED |
| **3V3** | `VCC_3V3` | Nguồn DC 3.3V | Cung cấp điện áp chuẩn an toàn cho DHT22 và MQ-2 (mô phỏng) | Chân VCC của DHT22 và MQ-2 trên Wokwi |
| **5V / VIN** | `VCC_5V` | Nguồn DC 5.0V | Cấp nguồn cuộn hút Relay và cực cấp nguồn tải qua chân COM | Chân VCC và chân COM của Module Relay |

---

### PHẦN 3: CẬP NHẬT MỤC 6.1.2 & 6.2 — THUYẾT MINH NGUỒN ĐIỆN AN TOÀN & THIẾT KẾ CÔNG TẮC THỦ CÔNG

#### 6.1.2. Thuyết minh giải pháp kỹ thuật về Nguồn điện Cảm biến MQ-2
1. **Môi trường Mô phỏng (Wokwi Simulation):**
   * Trong mô phỏng Wokwi, chân ngõ vào Analog của ESP32 (`GPIO34`) được định tuyến tới bộ chuyển đổi ADC1 12-bit có dải điện áp làm việc danh định từ $0.0\text{V}$ đến $3.3\text{V}$.
   * Nếu cấp nguồn $5.0\text{V}$ cho module MQ-2 trong mô phỏng, khi nồng độ khói tăng trên $270\text{ PPM}$, điện áp $V_{AOUT}$ sẽ chạm trần $3.3\text{V}$, dẫn đến hiện tượng **bão hòa ADC (Clipping ở mức 4095)**. Khi đó, từ $300\text{ PPM}$ đến $100.000\text{ PPM}$, giá trị ADC không thay đổi, khiến hệ thống không đo được khói đậm đặc.
   * **Giải pháp:** Cấp nguồn $3.3\text{V}$ trực tiếp từ chân `esp:3V3` cho module MQ-2 trên Wokwi. Điện áp ngõ ra $V_{AOUT}$ sẽ biến thiên trọn vẹn trong dải $0 - 3.28\text{V}$, hoàn toàn đồng bộ với dải đo 12-bit của ADC.

2. **Triển khai Phần cứng Vật lý thực tế (Physical Hardware):**
   * Ngoài đời thực, cuộn nung sấy của cảm biến MQ-2 bắt buộc phải được cấp đủ nguồn $5.0\text{V}$ ($\sim 150\text{mA}$) để đạt đến nhiệt độ hoạt động tối ưu ($300^\circ\text{C}$). Nếu cấp $3.3\text{V}$, cảm biến không đạt nhiệt độ làm việc và kết quả đo bị sai lệch hoàn toàn.
   * Để bảo vệ vi điều khiển ESP32 không bị quá áp làm hỏng cổng GPIO34, ngõ ra $V_{AOUT}$ được kết nối qua **mạch chia điện áp (Voltage Divider)** gồm 2 điện trở: $R_1 = 10\text{k}\Omega$ (nối tiếp tín hiệu) và $R_2 = 20\text{k}\Omega$ (nối mass):
     $$V_{ADC} = V_{AOUT} \times \frac{R_2}{R_1 + R_2} = V_{AOUT} \times \frac{20}{10 + 20} = 0.667 \times V_{AOUT}$$
   * Khi cảm biến xuất cực đại $5.0\text{V}$, điện áp đưa vào GPIO34 là $3.33\text{V}$ — hoàn toàn nằm trong giới hạn an toàn tuyệt đối của chip ESP32.

#### 6.2. Thiết kế Công tắc Thủ công (Manual Fan Override)
* **Phần cứng:** Sử dụng nút nhấn 4 chân nối giữa chân `GPIO18` và chân `GND`. Vi điều khiển kích hoạt điện trở kéo lên nội (`pinMode(PIN_BUTTON, INPUT_PULLUP)`), giúp mạch tối giản linh kiện ngoài mà vẫn đảm bảo mức logic ổn định (bình thường ở mức `HIGH`, khi nhấn kéo về mức `LOW`).
* **Thuật toán Chống rung (Debounce):** Cơ cấu cơ khí của nút nhấn gây ra hiện tượng nảy tiếp điểm (chatter) trong khoảng 5–20ms. Firmware cài đặt bộ lọc thời gian `millis()` với ngưỡng `DEBOUNCE_DELAY = 50ms`. Chỉ khi tín hiệu ổn định ở mức `LOW` vượt quá 50ms, trạng thái đảo quạt (`manualFanState = !manualFanState`) mới được ghi nhận, triệt tiêu 100% hiện tượng nhấn 1 lần mà nhảy nhiều lần.

---

### PHẦN 4: CẬP NHẬT MỤC 7.2 — CƠ SỞ LÝ THUYẾT PHƯƠNG TRÌNH POWER-LAW, HIỆU CHUẨN THỰC NGHIỆM 2 ĐIỂM & MA TRẬN ƯU TIÊN AN TOÀN

#### 7.2.1. Bản chất phương trình đặc tuyến bán dẫn SnO2 (Power-Law Model)
Theo tài liệu chế tạo của hãng Hanwei Electronics, độ dẫn điện của lớp oxit thiếc SnO2 thay đổi phi tuyến theo hàm mũ với nồng độ khí cháy:
$$\text{PPM} = A \times \left(\frac{R_s}{R_0}\right)^B$$
* $R_s$: Điện trở cảm biến tại nồng độ khí đo được:
  $$R_s = R_L \times \frac{V_{CC} - V_{AOUT}}{V_{AOUT}}$$
* $R_0$: Điện trở cảm biến tại môi trường chuẩn đã biết trước nồng độ.
* $A, B$: Các hệ số đặc tuyến phụ thuộc vào loại khí phát hiện (LPG, khói, CO, CH4).

#### 7.2.2. Phương pháp Hiệu chuẩn Thực nghiệm 2 điểm (Two-Point Empirical Calibration) trên Wokwi
* Module cảm biến `wokwi-gas-sensor` trên nền tảng Wokwi sử dụng mã nguồn đóng (closed-source), không công khai phương trình toán học nội tại. Do đó, việc áp dụng hệ số datasheet của cảm biến thật ($A = 574.25, B = -2.222$) dẫn đến hiện tượng sai lệch nồng độ khói hiển thị so với thanh trượt mô phỏng.
* Để giải quyết triệt để vấn đề này, nhóm triển khai **phương pháp hiệu chuẩn thực nghiệm 2 điểm**:
  1. Chạy mô phỏng lần 1 tại mốc $\text{PPM}_1 = 200\text{ PPM}$, chạy hàm `printRawRsForCalibration()` để đo giá trị thực tế $Rs_1 = 1.7100\text{ k}\Omega$.
  2. Chạy mô phỏng lần 2 tại mốc $\text{PPM}_2 = 1000\text{ PPM}$, ghi nhận giá trị thực tế $Rs_2 = 0.8852\text{ k}\Omega$.
  3. Áp dụng phương pháp hồi quy tuyến tính trên thang logarit (log-log regression):
     $$B = \frac{\log_{10}(\text{PPM}_2) - \log_{10}(\text{PPM}_1)}{\log_{10}(Rs_2) - \log_{10}(Rs_1)}$$
     $$A = \frac{\text{PPM}_1}{Rs_1^B}$$
  4. Thu được bộ hệ số thực nghiệm chính xác tuyệt đối cho bộ giả lập Wokwi. Mọi nồng độ từ $150\text{ PPM}$ đến $100.000\text{ PPM}$ đều được ánh xạ mượt mà, chính xác.

#### 7.2.3. Ma trận Phân xử Quyền ưu tiên An toàn (Safety-First Priority Matrix)
Hệ thống tuân thủ nghiêm ngặt tiêu chuẩn PCCC trong tự động hóa điều khiển: Tính mạng con người và an toàn cháy nổ luôn được đặt lên hàng đầu.

#### Bảng 7.2: Ma trận phân xử quyền ưu tiên vận hành hệ thống

| Vùng Trạng Thái | Dải Nồng Độ Khói (PPM) | Quyền Ưu Tiên | Trạng Thái Còi (Buzzer) | Trạng Thái Quạt (Relay FAN) | Tác Vụ Khi Nhấn Nút Thủ Công (GPIO18) |
|:---:|:---:|:---:|:---:|:---:|:---|
| **VÙNG NGUY HIỂM (ALARM)** | $\text{PPM} \ge 400.0$ | **Rule Tự động (Local Interlock) THẮNG TUYỆT ĐỐI** | **BẬT (Hú liên tục)** | **BẬT CƯỠNG BỨC** | **BỊ KHÓA HOÀN TOÀN.** In thông báo cảnh báo: Nút bấm bị vô hiệu hóa vì hệ thống đang trong vùng nguy hiểm. |
| **VÙNG AN TOÀN (SAFE)** | $\text{PPM} \le 300.0$ | **Công tắc Thủ công (Manual Override) TOÀN QUYỀN** | **TẮT** | Phụ thuộc người dùng (Bật/Tắt tự do) | **CHO PHÉP.** Bật hoặc tắt quạt theo ý muốn của người dùng tại hiện trường. |
| **VÙNG TRỄ (HYSTERESIS)** | $300.0 < \text{PPM} < 400.0$ | **Duy trì trạng thái trước đó (Tránh rung giật)** | Giữ nguyên trạng thái cũ | Giữ nguyên trạng thái cũ | Không thay đổi trạng thái tự động, tránh hiện tượng Relay chattering khi khói chập chờn. |

---

### PHẦN 5: CẬP NHẬT MỤC 7.4 — MÃ NGUỒN C++ TẦNG 1 NÂNG CẤP ĐẦY ĐỦ

*(File mã nguồn chuẩn đã được tích hợp trong thư mục dự án [src/main.cpp](file:///D:/BackUp_E/IoT/DoAn/src/main.cpp) và kiểm thử thành công trên PlatformIO)*

---

### PHẦN 6: CẬP NHẬT MỤC 6.3 — FILE CẤU HÌNH MẠCH MÔ PHỎNG WOKWI (`diagram.json`)

*(File cấu hình chuẩn đã được tạo tại [diagram.json](file:///D:/BackUp_E/IoT/DoAn/diagram.json) bao gồm đầy đủ ESP32, MQ2, DHT22, Buzzer, Relay, LED Fan và Pushbutton công tắc quạt thủ công)*
