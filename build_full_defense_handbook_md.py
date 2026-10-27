# -*- coding: utf-8 -*-
"""
Script tạo file Markdown toàn diện cho Sổ Tay Thuyết Trình & Cẩm Nang Hỏi Xoáy Đáp Xoay:
1. Bảng tra cứu 26 từ viết tắt (Acronyms), ký hiệu vật lý, công thức tính toán và tên riêng nhà sản xuất / tiêu chuẩn.
2. Kịch bản NoteSpeak 8 slides chi tiết từng giây, hành động trỏ laser và lời thoại học thuật.
3. Từ điển bách khoa 6 chiều mổ xẻ 38 linh kiện, vật tư ốc vít, IC, giao thức và giải thuật (chuẩn Datasheet Hanwei MQ-2 5V heater, divider 10k/20k).
4. Bộ 30 câu hỏi "Hỏi xoáy đáp xoay" chuẩn điểm 10.
"""

import os
import re

def create_markdown(output_path):
    # Đọc Chapter III từ file cũ để kế thừa và tinh chỉnh 30 câu hỏi
    src_old = r"e:\IoT\DoAn\docs\pdf\So_Tay_Thuyet_Trinh_Va_Hoi_Xoay_Dap_Xoay.md"
    with open(src_old, "r", encoding="utf-8") as f:
        old_text = f.read()

    idx_ch3 = old_text.find("# CHƯƠNG III: BỘ 30 CÂU HỎI")
    if idx_ch3 != -1:
        chapter_3_content = old_text[idx_ch3:]
    else:
        raise ValueError("Không tìm thấy Chương III trong file cũ!")

    # Tinh chỉnh Câu 9 trong Chapter 3: Thay R1=1k, R2=2k bằng R1=10k, R2=20k chuẩn xác theo BOM và Slide 2
    chapter_3_content = chapter_3_content.replace(
        "R_1 = 1\\text{k}\\Omega$ và $R_2 = 2\\text{k}\\Omega$",
        "R_1 = 10\\text{k}\\Omega$ và $R_2 = 20\\text{k}\\Omega$"
    )
    chapter_3_content = chapter_3_content.replace(
        "1 / (1 + 2) = 2/3",
        "20 / (10 + 20) = 2/3"
    )
    chapter_3_content = chapter_3_content.replace(
        "gồm 2 điện trở $R_1 = 1\\text{k}\\Omega$ và $R_2 = 2\\text{k}\\Omega$",
        "gồm 2 điện trở $R_1 = 10\\text{k}\\Omega$ và $R_2 = 20\\text{k}\\Omega$ (tổng trở $30\\text{k}\\Omega$ kéo dòng cực nhỏ ~0.16mA không làm sụt áp tín hiệu cảm biến)"
    )

    content_part1_and_glossary = """# BÍ KÍP BẢO VỆ ĐỒ ÁN IOT ĐIỂM 10: SỔ TAY THUYẾT TRÌNH NOTESPEAK & CẨM NANG "HỎI XOÁY ĐÁP XOAY"

**Học phần:** IT4735 — Internet of Things (IoT) và Ứng Dụng  
**Đơn vị:** Khoa Công Nghệ Thông Tin — Đại Học Công Thương TP. Hồ Chí Minh (HUIT)  
**Đề tài 04:** HỆ THỐNG BÁO KHÓI CẢNH BÁO SỚM (Smart Smoke & Fire Early Warning System)  
**Nhóm thực hiện:** Nhóm 04 (Lớp học phần: N09)  
**Thành viên đề tài:**
1. **Nguyễn Vĩnh Khang** — MSSV: 2001230381 *(Trưởng nhóm: Firmware ESP32, FSM & Tích Hợp Hệ Thống)*
2. **Nguyễn Văn Đức** — MSSV: 2001230186 *(Thành viên: Thiết Kế Ma Trận Topic, Payload JSON & Downlink)*
3. **Nguyễn Văn Mãnh** — MSSV: 2001230503 *(Thành viên: Khóa An Toàn Safety Guard & Web Dashboard)*

---

# BẢNG TRA CỨU NHANH THUẬT NGỮ, TỪ VIẾT TẮT, KÝ HIỆU & TÊN RIÊNG

### 1. Bảng Giải Mã Các Từ Viết Tắt Chuyên Ngành (Acronyms & Abbreviations)

| Từ viết tắt | Tên tiếng Anh đầy đủ | Định nghĩa & Ý nghĩa kỹ thuật trong đề tài |
| :--- | :--- | :--- |
| **SoC** | System on Chip | Hệ thống tích hợp trên một vi mạch duy nhất (ESP32 tích hợp CPU Dual-Core, RAM, ROM, Wi-Fi, BLE). |
| **ADC** | Analog-to-Digital Converter | Bộ chuyển đổi tín hiệu tương tự sang số 12-bit (0 – 4095) trên ESP32 đọc điện áp cảm biến. |
| **SAR ADC** | Successive Approximation Register ADC | Kiến trúc mạch ADC xấp xỉ liên tiếp tích hợp trong ESP32 giúp đọc điện áp cực nhanh. |
| **GPIO** | General Purpose Input/Output | Các chân ngõ vào/ra đa dụng của vi điều khiển để điều khiển LED, relay, nút nhấn, cảm biến. |
| **FSM** | Finite State Machine | Máy trạng thái hữu hạn điều phối 3 cấp độ cảnh báo an toàn: `SAFE` -> `WARN` -> `ALARM`. |
| **FreeRTOS**| Free Real-Time Operating System | Hệ điều hành thời gian thực đa nhiệm ưu tiên phân định trước chia tải trên 2 nhân CPU. |
| **WDT** | Hardware Watchdog Timer | Bộ định thời giám sát phần cứng; tự động cưỡng bức reset chip nếu CPU bị treo cứng quá 5 giây. |
| **EMA** | Exponential Moving Average | Bộ lọc trung bình trượt lũy thừa (alpha=0.2) làm mịn tín hiệu nồng độ khói, triệt tiêu gai nhiễu điện áp. |
| **SPIFFS** | Serial Peripheral Interface Flash File System | Phân vùng hệ thống tệp trên bộ nhớ Flash ngoài của ESP32 dùng làm bộ đệm vòng lưu 20 bản ghi sự cố khi mất Wi-Fi. |
| **MQTT** | Message Queuing Telemetry Transport | Giao thức truyền thông xuất bản/đăng ký siêu nhẹ tầng ứng dụng trên nền TCP/IP. |
| **QoS** | Quality of Service | Cấp độ dịch vụ phân phối tin MQTT: QoS 0 (At most once - Telemetry) và QoS 1 (At least once - Lệnh quạt). |
| **LWT** | Last Will and Testament | Bản tin "Di chúc" đăng ký trước; Broker tự động phát tán khi phát hiện trạm IoT bị sập nguồn đột ngột. |
| **SCADA** | Supervisory Control and Data Acquisition | Hệ thống điều khiển giám sát và thu thập dữ liệu công nghiệp (Web Dashboard P302). |
| **BLDC** | Brushless Direct Current Motor | Động cơ điện một chiều không chổi than của quạt hút 12V; không sinh tia lửa điện, an toàn chống cháy nổ. |
| **IP54** | Ingress Protection Code (54) | Tiêu chuẩn quốc tế bảo vệ vỏ hộp: Số 5 (chống bụi hạt mịn), Số 4 (chống nước bắn tung tóe mọi hướng). |
| **PCB** | Printed Circuit Board | Bo mạch in 2 lớp phíp thủy tinh FR4 chứa toàn bộ linh kiện kết nối trạm. |
| **FR4** | Flame Retardant 4 | Vật liệu sợi thủy tinh dệt gia cường nhựa epoxy có khả năng tự dập tắt lửa. |
| **HASL** | Hot Air Solder Leveling | Công nghệ mạ thiếc nóng bề mặt tiếp điểm đồng trên bo mạch in chống oxy hóa. |
| **EMI** | Electromagnetic Interference | Nhiễu điện từ trường sinh ra từ động cơ hoặc sóng vô tuyến. |
| **NO/NC/COM** | Normally Open / Normally Closed / Common | 3 tiếp điểm của rơ-le: Thường Mở (NO), Thường Đóng (NC) và Chân Chung (COM). |
| **SPST** | Single Pole Single Throw | Công tắc bập bênh 1 cực 1 tiếp điểm đóng/ngắt nguồn chính. |
| **AWG** | American Wire Gauge | Tiêu chuẩn đo kích cỡ dây dẫn của Mỹ (dây silicon 22AWG dẫn dòng 5V/12V). |
| **RTT** | Round-Trip Time | Thời gian trễ mạng khứ hồi (từ lúc Web click -> Broker -> ESP32 đóng quạt -> phản hồi ACK về Web). |
| **RBAC** | Role-Based Access Control | Cơ chế kiểm soát quyền truy cập dựa trên vai trò (Admin / Operator) trên Web Dashboard. |
| **PPM** | Parts Per Million | Đơn vị đo mật độ phần triệu của nồng độ hạt khói và khí cháy lơ lửng trong không khí. |
| **%RH** | Percent Relative Humidity | Đơn vị đo độ ẩm tương đối của không khí môi trường từ cảm biến DHT22. |

---

### 2. Bảng Ký Hiệu Vật Lý, Điện Tử & Công Thức Tính Toán

| Ký hiệu | Tên gọi & Đại lượng | Giá trị / Khoảng thực tế | Ý nghĩa kỹ thuật trong hệ thống |
| :--- | :--- | :--- | :--- |
| **R_s** | Điện trở màng cảm biến MQ-2 | 2kΩ - 20kΩ (thay đổi theo khói) | Điện trở vật liệu bán dẫn SnO2; giảm mạnh khi tiếp xúc khói/khí cháy. |
| **R_0** | Điện trở màng trong không khí sạch | Đo thực nghiệm khi hiệu chuẩn | Mốc chuẩn điện trở tham chiếu trong môi trường sạch (Clean Air). |
| **R_H** | Điện trở cuộn sấy bên trong MQ-2 | 31Ω ± 3Ω (theo Datasheet Hanwei) | Dây may-so nung nóng màng SnO2 lên 200°C - 300°C. |
| **V_H** | Điện áp cấp cho cuộn sấy MQ-2 | 5.0V ± 0.1V DC/AC | Bắt buộc lấy trực tiếp từ ngõ ra 5V của IC Buck LM2596S. |
| **P_H** | Công suất tiêu thụ của cuộn sấy | P_H = V_H^2 / R_H ≈ 800 - 900mW | Nhiệt lượng cần thiết để lớp SnO2 đạt trạng thái cân bằng hóa học bề mặt. |
| **AOUT** | Ngõ ra tín hiệu Analog của MQ-2 | 0 - 5.0V | Điện áp tương tự tỷ lệ nghịch với điện trở R_s. |
| **R1, R2** | Điện trở cầu phân áp ngõ ra AOUT | R1=10kΩ, R2=20kΩ | Tỷ số phân áp K = 20/(10+20) = 2/3. Hạ 5V -> 3.33V bảo vệ ADC GPIO 34. |
| **V_iso** | Điện áp cách ly của Opto PC817 | 5000Vrms | Độ an toàn cách ly giữa mạch logic ESP32 và cuộn cảm relay. |
| **V_F, I_F** | Điện áp rơi thuận & dòng LED | Đỏ: V_F ≈ 2.0V; Xanh: V_F ≈ 3.0V; I_F ≈ 4mA | Tính toán chọn trở hạn dòng: R = (3.3V - 2.0V)/330Ω = 3.94mA. |
| **alpha** | Hệ số làm mịn bộ lọc EMA | alpha = 0.2 | Cân bằng giữa độ mượt tín hiệu (80%) và độ nhạy thời gian thực (20%). |
| **S_t, X_t** | Giá trị lọc mượt & giá trị đo thô | S_t = alpha·X_t + (1-alpha)·S_{t-1} | Thuật toán đệ quy lọc nhiễu điện áp không tốn RAM vi điều khiển. |
| **V = -L·di/dt**| Suất điện động tự cảm ngược | Có thể vọt lên >100V khi ngắt rơ-le | Lý do bắt buộc phải có Diode Flyback 1N4148 dập xung ngược. |
| **Delta V** | Độ sụt áp chuyển đổi năng lượng | Delta V = 12V - 5V = 7V | Giải thích vì sao dùng LM2596S (tổn hao 0.2W) thay vì 7805 (tỏa nhiệt 3.5W làm sập trạm). |
| **dB** | Decibel (Cường độ âm thanh còi) | ≥ 85dB tại khoảng cách 10cm | Âm lượng còi chíp đủ cảnh tỉnh cư dân khi có báo động ALARM. |
| **CFM** | Cubic Feet per Minute (Lưu lượng gió) | ≈ 35 - 40 CFM | Công suất lưu lượng hút xả khói cưỡng bức của quạt 12V 80mm. |
| **RPM** | Revolutions Per Minute (Tốc độ quay) | ≈ 2800 RPM | Tốc độ quay của cánh quạt tản nhiệt hút khói. |

---

### 3. Bảng Tên Riêng Nhà Sản Xuất & Tiêu Chuẩn Công Nghiệp

| Tên riêng / Tiêu chuẩn | Quốc gia / Tổ chức | Lĩnh vực chuyên môn & Ứng dụng trong đồ án |
| :--- | :--- | :--- |
| **Espressif Systems** | Thượng Hải, Trung Quốc | Hãng thiết kế vi mạch bán dẫn chế tạo chip ESP32 (ESP32-WROOM-32, Tensilica Xtensa Dual-Core). |
| **Hanwei Electronics** | Trịnh Châu, Trung Quốc | Nhà sản xuất cảm biến khí hàng đầu thế giới; tác giả Datasheet cảm biến khí/khói MQ-2. |
| **Aosong Electronics** | Quảng Châu, Trung Quốc | Nhà sản xuất cảm biến nhiệt ẩm MEMS chế tạo module kỹ thuật số DHT22 (AM2302). |
| **Texas Instruments (TI)**| Dallas, Texas, Hoa Kỳ | Tập đoàn bán dẫn hàng đầu thế giới chế tạo IC hạ áp xung Buck LM2596 / LM2596S (150kHz 3A). |
| **Songle Relay** | Chiết Giang, Trung Quốc | Nhà sản xuất rơ-le điện từ công nghiệp chế tạo dòng relay SRD-05VDC-SL-C (tiếp điểm 10A). |
| **Sharp Corporation** | Osaka, Nhật Bản | Tập đoàn điện tử chế tạo bộ cách ly quang Optocoupler PC817 (cách điện 5000Vrms). |
| **Tensilica (Cadence)** | California, Hoa Kỳ | Hãng kiến trúc vi xử lý thiết kế lõi nhân Xtensa LX6 32-bit bên trong chip ESP32. |
| **IEC 60529** | Thụy Sĩ (Quốc tế) | Tiêu chuẩn quốc tế quy định cấp bảo vệ chống bụi và nước của vỏ thiết bị (Chuẩn IP54). |
| **DIN 934** | Đức (Deutsches Institut für Normung) | Tiêu chuẩn cơ khí công nghiệp chế tạo đai ốc (tán) Inox ren M3 dùng cố định trụ đồng. |
| **UL94-V0** | Hoa Kỳ (Underwriters Laboratories) | Tiêu chuẩn an toàn chống cháy vật liệu nhựa ABS (tự dập tắt ngọn lửa trong vòng 10 giây). |

---

# CHƯƠNG I: KỊCH BẢN THUYẾT TRÌNH (NOTESPEAK) 4–5 PHÚT CHUẨN BỘ 8 SLIDES

*(Lưu ý khi đứng thuyết trình: Phong thái đứng thẳng, ánh mắt bao quát hội đồng, giọng nói dứt khoát, tự tin, tay cầm bút chỉ laser trỏ chính xác vào từng khối card tương ứng trên slide).*

---

### 1. Slide 1: Trang Bìa & Khái Quát Đề Tài (Thời lượng: ~30 giây)

- **Hình ảnh trên máy chiếu:** Slide 1 - Nền xanh Navy công nghệ đậm, tiêu đề đề tài nổi bật màu trắng và cam, danh sách 3 thành viên Nhóm 04 (Lớp N09) kèm MSSV & 3 khối card khái quát 3 Part.
- **Hành động trỏ laser:** Quét laser qua tên đề tài, trỏ vào 3 Card tương ứng Part 1 (Device), Part 2 (MQTT Broker), Part 3 (Web Server).
- **Lời thoại NoteSpeak:**
> *"Kính thưa quý Thầy/Cô trong Hội đồng và các bạn sinh viên!  
> Em xin đại diện cho **Nhóm 04 (Lớp học phần N09)** xin được trình bày Báo cáo thiết kế và hiện thực hệ thống IoT hoàn chỉnh với đề tài: **'HỆ THỐNG BÁO KHÓI CẢNH BÁO SỚM — Smart Smoke & Fire Early Warning System'**.  
> Đề tài của nhóm chúng em được xây dựng bám sát theo kiến trúc tiêu chuẩn 3 tầng công nghệ IoT:
> - **Part 1 (Tầng Device):** Trạm cảm biến biên ESP32 tích hợp FreeRTOS đa nhiệm, bộ lọc nhiễu số EMA và bảng BOM vật tư chi tiết từng con ốc.
> - **Part 2 (Tầng Communication & Services):** Hạ tầng Message Broker MQTT chuẩn hóa cây topic phân cấp theo namespace cô lập `Nhom09/smoke/...` cùng 4 microservices lõi.
> - **Part 3 (Tầng Application):** Nền tảng Web SCADA chuẩn doanh nghiệp, giám sát dữ liệu thời gian thực, quản trị CSDL, điều khiển chấp hành 2 chiều và cảnh báo khẩn cấp Telegram Bot.  
> Sau đây, em xin phép đi vào chi tiết kỹ thuật từng slide của hệ thống."*

---

### 2. Slide 2: Part 1 - Thiết Kế Phần Cứng, Nguồn Datasheet & FreeRTOS FSM (Thời lượng: ~40 giây)

- **Hình ảnh trên máy chiếu:** Slide 2 - Bốn khối card đối xứng: Khối 1 (Thiết kế điện năng & An toàn phần cứng theo Datasheet), Khối 2 (Kiến trúc Firmware FreeRTOS Dual-Core), Khối 3 (Máy trạng thái FSM 3 cấp & Hysteresis), Khối 4 (Xử lý tín hiệu số EMA & Đệm SPIFFS).
- **Hành động trỏ laser:** Trỏ lần lượt vào mạch nguồn Buck LM2596S, cuộn sấy MQ-2, cầu phân áp 10k/20k; chuyển sang Dual-Core và kết lại ở vùng trễ Hysteresis 300-400 PPM.
- **Lời thoại NoteSpeak:**
> *"Bước vào Slide 2, nhóm em tập trung vào kỹ thuật phần cứng và firmware nhúng:
> - Về mặt an toàn điện theo đúng Datasheet: Nguồn chính 12VDC cấp riêng cho quạt hút; mạch Buck LM2596S hạ xuống 5V nuôi ESP32 và **cấp trực tiếp cuộn sấy MQ-2 (R_H ≈ 31Ω, P_H ≈ 900mW)** để nung màng SnO2 đạt nhiệt độ làm việc tối ưu. Tại ngõ ra analog AOUT (0 - 5V), nhóm bố trí **cầu phân áp R1=10kΩ, R2=20kΩ** hạ an toàn về 0 - 3.3V bảo vệ chân ADC GPIO 34 của ESP32 không bị quá áp. Toàn bộ rơ-le được cách ly quang Opto PC817 (5000Vrms) kèm diode 1N4148 dập xung ngược.
> - Về Firmware: ESP32 chạy FreeRTOS đa nhiệm tách biệt: Core 0 chuyên trách kết nối mạng Wi-Fi/MQTT; Core 1 xử lý cảm biến và điều phối máy trạng thái FSM 3 cấp (SAFE, WARN, ALARM) với vùng trễ Hysteresis 300-400 PPM chống rung rơ-le; đồng thời tích hợp bộ lọc số EMA (alpha=0.2) triệt tiêu hoàn toàn báo động giả do khói thuốc lá thoáng qua."*

---

### 3. Slide 3: Part 1 - Bảng BOM Vật Tư Phần A (18 Linh Kiện Điện Tử) (Thời lượng: ~40 giây)

- **Hình ảnh trên máy chiếu:** Slide 3 - Bảng BOM toàn diện 18 linh kiện điện tử chia làm 2 khối: Khối I (Vi điều khiển, Cảm biến & Cơ cấu chấp hành) và Khối II (Nguồn công suất & Bảo vệ điện năng).
- **Hành động trỏ laser:** Quét nhanh qua Khối I (ESP32, MQ-2, DHT22, Relay Opto, Buzzer, LED + Trở 330Ω, Nút nhấn + Trở 10kΩ) và Khối II (LM2596S, Cầu chì 2A Fast-blow, Tụ kép 100µF/100nF).
- **Lời thoại NoteSpeak:**
> *"Tại Slide 3, nhóm minh bạch toàn bộ 18 linh kiện điện tử trong Bảng BOM Phần A:
> - Ở Khối I: Bo mạch vi điều khiển trung tâm ESP32 DevKit V1 30 chân Dual-Core 240MHz; Module cảm biến khói MQ-2 kèm IC so sánh LM393 vi chỉnh; Cảm biến nhiệt ẩm số DHT22 độ chính xác cao; Module Relay 1 kênh 5VDC cách ly quang; Còi chíp Active Buzzer công suất âm trên 85dB; Đèn LED chỉ thị 5mm kèm trở hạn dòng 330Ω; và Nút bấm test khẩn cấp kèm trở kéo Pull-up 10kΩ chống trôi chân logic.
> - Ở Khối II: Mạch Buck LM2596S hiệu suất 92% thay thế hoàn hảo cho IC 7805 nóng bỏng; Quạt hút khói 12V 0.18A BLDC không phát sinh tia lửa điện; Cầu chì ống 2A tác động nhanh bảo vệ ngắn mạch; Cặp tụ lọc nguồn kép (tụ hóa 100µF dập sụt áp Wi-Fi và tụ gốm 100nF lọc xung cao tần 150kHz) và công tắc bập bênh nguồn KCD11 an toàn."*

---

### 4. Slide 4: Part 1 - Cơ Khí Lắp Ráp & Bảng BOM Phần B (16 Linh Kiện Cơ Khí & Chi Phí ~720k) (Thời lượng: ~35 giây)

- **Hình ảnh trên máy chiếu:** Slide 4 - Bảng BOM 16 hạng mục cơ khí, vỏ hộp, ốc vít cơ khí chi tiết và dòng nổi bật: TỔNG KINH PHÍ DỰ TOÁN (BOM) ~720.000 VNĐ.
- **Hành động trỏ laser:** Trỏ vào tiêu chuẩn IP54, bo mạch FR4 dày 1.6mm, các chi tiết ốc vít M3/M4 và nhấn mạnh dòng TỔNG KINH PHÍ DỰ TOÁN (~720k).
- **Lời thoại NoteSpeak:**
> *"Tiếp nối sang Slide 4, nhóm chuẩn hóa việc đóng gói phần cứng chuẩn công nghiệp qua 16 hạng mục cơ khí và đấu nối trong Bảng BOM Phần B:
> - Bo mạch chính PCB 2 lớp bằng phíp thủy tinh chống cháy FR4 dày 1.6mm mạ thiếc HASL; Vỏ hộp nhựa ABS chống cháy đạt chuẩn bảo vệ IP54 chống bụi và nước bắn; Socket rào cắm cái 2.54mm giúp tháo lắp ESP32 linh hoạt mà không bị sốc nhiệt mỏ hàn.
> - Chi tiết cơ khí được tính toán cẩn trọng từng con ốc: 8 trụ đồng lục giác M3x10mm nâng bo mạch cách đáy chống ẩm; 8 ốc vít bake Inox 304 kèm đệm Nylon chống trầy xước đường mạch; 4 bộ bu-lông M4x35mm kèm đệm vênh chống rung lắc quạt hút; và gioăng cao su grommet chống cứa dây điện.
> - Toàn bộ kinh phí hoàn thiện một trạm IoT thực tế chỉ xấp xỉ 720.000 VNĐ, rẻ hơn 70% so với tủ báo cháy trung tâm truyền thống, mang tính khả thi thương mại rất cao."*

---

### 5. Slide 5: Part 2 - Dịch Vụ MQTT Trên Server & Cây Topic Phân Cấp (Thời lượng: ~40 giây)

- **Hình ảnh trên máy chiếu:** Slide 5 - Cây Topic phân cấp chuẩn REST-like `Nhom09/smoke/...`, 4 luận điểm kỹ thuật Rationale và 4 khối Microservices Backend.
- **Hành động trỏ laser:** Trỏ vào tiền tố `Nhom09/smoke/`, nhấn mạnh QoS 0 vs QoS 1, trỏ 4 card Microservices (Auth, Collect, Control, Keep_alive).
- **Lời thoại NoteSpeak:**
> *"Tại Slide 5 - Tầng 2 Truyền thông và Message Broker:  
> Nhóm em thiết kế cây ma trận topic phân cấp chặt chẽ theo chuẩn công nghiệp: `Nhom09 / smoke / {service_domain} / [{action_or_target}]`.
> Thiết kế này đạt 4 tiêu chuẩn kỹ thuật cốt lõi:
> 1. Namespace Isolation: Tiền tố Nhom09 cô lập 100% dữ liệu trên Broker dùng chung, triệt tiêu xung đột tin nhắn.
> 2. Decoupling Độc Lập: Các Microservices backend chỉ subscribe đúng topic phụ trách, giảm tải CPU.
> 3. Tối ưu Heap RAM: ESP32 chỉ lắng nghe đúng topic lệnh cmd/+, tiết kiệm bộ nhớ vi điều khiển.
> 4. Phân định 2 chiều minh bạch: Kênh Downlink điều khiển dùng QoS 1 đảm bảo tin cậy; kênh Uplink telemetry dùng QoS 0 tránh nghẽn mạng.
> Bốn Microservices (Auth cấp Session Key, Collect ghi MySQL và Redis, Control điều phối lệnh quạt và Keep_alive giám sát LWT 60s) phối hợp hoàn hảo trên nền tảng Docker Container."*

---

### 6. Slide 6: Tích Hợp Hệ Thống - Luồng Dữ Liệu 2 Chiều & Khóa An Toàn PCCC (Thời lượng: ~45 giây)

- **Hình ảnh trên máy chiếu:** Slide 6 - Ba cột luồng tích hợp hệ thống trực quan: Cột 1 (Luồng Uplink Telemetry & Báo động), Cột 2 (Luồng Downlink Lệnh điều khiển & ACK), Cột 3 (Cơ chế Khóa an toàn PCCC - Safety Interlock Override).
- **Hành động trỏ laser:** Trỏ từ Cột 1 (cảm biến -> ESP32 -> Broker -> Web/Telegram <1.2s), sang Cột 2 (Web click -> Broker -> ESP32 đóng quạt -> ACK <120ms), và nhấn mạnh Cột 3 (Nguyên tắc an toàn PCCC tối thượng).
- **Lời thoại NoteSpeak:**
> *"Bước sang Slide 6 - Trọng tâm tích hợp hệ thống toàn diện:
> - Luồng Uplink: Cảm biến đọc dữ liệu liên tục chu kỳ 1s trên Core 1, lọc số EMA và publish gói tin JSON chuẩn RFC 8259 lên topic telemetry mỗi 2s. Khi phát hiện cháy khẩn cấp, Server lập tức kích hoạt Bot Telegram gửi cảnh báo đa kênh đến điện thoại quản lý dưới 1.2 giây.
> - Luồng Downlink: Khi người vận hành bật quạt trên Web, lệnh có cấu trúc gửi qua topic cmd/fan với QoS 1; ESP32 ngắt Core 1 đóng tiếp điểm rơ-le và lập tức gửi gói tin xác nhận ACK lên topic status với độ trễ khứ hồi RTT dưới 120ms.
> - Đặc biệt là Cơ chế Khóa an toàn PCCC (Safety Interlock Override): Nhóm áp dụng nguyên tắc 'Bảo toàn tính mạng con người là ưu tiên tối thượng'. Khi nồng độ khói chạm ngưỡng ALARM (≥400 PPM), cả Firmware ESP32 và Server đều kích hoạt khóa an toàn: TỪ CHỐI TUYỆT ĐỐI mọi lệnh Downlink đòi tắt quạt (FAN = OFF) gửi từ Web/App kèm mã lỗi ERR_SAFETY_INTERLOCK_OVERRIDE, chỉ cho phép tạm ngắt còi tối đa 180s để phục vụ cứu hộ."*

---

### 7. Slide 7: Part 3 - Ứng Dụng Web Server: 4 Trụ Cột Nền Tảng (Thời lượng: ~40 giây)

- **Hình ảnh trên máy chiếu:** Slide 7 - Bốn trụ cột công nghệ Web: 1. Data Representation (Dashboard thời gian thực), 2. Data Management (Quản trị CSDL), 3. Control GUI (Giao diện điều khiển 2 chiều), 4. Data Analysis (Phân tích dữ liệu & Cảnh báo Telegram).
- **Hành động trỏ laser:** Trỏ lần lượt qua đồng hồ đo khói Radial Gauge, biểu đồ Chart.js, CSDL MySQL Composite Index, các nút công tắc xúc giác và thuật toán phân tích gia tốc nhiệt cháy sớm.
- **Lời thoại NoteSpeak:**
> *"Tại Slide 7 - Tầng Ứng Dụng Web Server App, hệ thống vận hành trên 4 trụ cột vững chắc:
> 1. Data Representation: Dashboard thời gian thực kết nối MQTT over WebSockets độ trễ dưới 1s; trực quan hóa đồng hồ Radial Gauge 3 dải màu cảnh báo, đồ thị tương quan nhiệt - ẩm Chart.js và Live Status Badges.
> 2. Data Management: Quản trị CSDL MySQL tối ưu bằng chỉ mục Composite Index (timestamp, device_id) cho tốc độ truy vấn lịch sử dưới 10ms, hỗ trợ lọc đa mốc và xuất báo cáo PDF/CSV kiểm toán.
> 3. Control GUI: Điều phối 2 chiều linh hoạt giữa chế độ Tự động (Auto FSM) và Thủ công (Manual), nút ngắt khẩn cấp Kill-Switch và cấu hình ngưỡng nhạy Ngày/Đêm trực tiếp trên Web.
> 4. Data Analysis: Thuật toán thông minh nhận diện cháy sớm dựa trên tương quan gia tốc tăng khói và nhiệt độ môi trường (>50°C), loại trừ báo động giả và kích hoạt Bot Telegram gửi tin nhắn khẩn cấp kèm còi hú đa tầng Web Audio API."*

---

### 8. Slide 8: Kết Quả Thực Nghiệm - RTT Benchmark, 16 Test Cases Tích Hợp Pass 100% & Bền Vững Mạng (Thời lượng: ~40 giây)

- **Hình ảnh trên máy chiếu:** Slide 8 - Bốn thẻ nghiệm thu: Khối 1 (Đo lường độ trễ kỹ thuật Latency & RTT Benchmark), Khối 2 (Ma trận 16 Test Cases tích hợp Milestone M4 Pass 100%), Khối 3 (Tính bền vững mạng & Khả năng mở rộng Fleet Scale), Khối 4 (Tổng kết nghiệm thu đồ án & Tính ứng dụng thực tế).
- **Hành động trỏ laser:** Trỏ vào các con số đo lường thực tế: Downlink RTT 115ms, Uplink Latency 185ms, 16/16 Test Cases Pass 100%, LWT, Replay ngoại tuyến 20 bản ghi và tổng kết ~720k.
- **Lời thoại NoteSpeak:**
> *"Cuối cùng tại Slide 8 - Nhóm chứng minh sự thành công của đề tài bằng số liệu thực nghiệm định lượng:
> - Về độ trễ mạng thực tế: Độ trễ Uplink từ cảm biến lên Web đạt 185ms (vượt mục tiêu 1000ms); Độ trễ khứ hồi Downlink RTT đạt 115ms (vượt mục tiêu 500ms); Báo động Telegram dưới 1.15s; và tỷ lệ rớt gói tin bằng 0% trong 4 giờ kiểm thử liên tục.
> - Về kiểm thử tích hợp: Hệ thống vượt qua 100% Ma trận 16 Test Cases Milestone M4 (từ đọc ADC, FSM, lọc EMA, đóng ngắt rơ-le, khóa an toàn PCCC, đến mất mạng và tự động xả 20 bản ghi đệm vòng SPIFFS).
> - Về khả năng mở rộng: Cấu trúc topic cho phép nhân bản lên hơn 100 trạm cảm biến tòa nhà; cơ chế LWT phát hiện ngắt kết nối sau 60s; và kiến trúc vi dịch vụ không trạng thái dễ dàng đóng gói Docker Container.
> 
> Nhóm 04 chúng em đã hoàn thành 100% mục tiêu đồ án IT4735 với sản phẩm phần cứng thực tế, mã nguồn GitHub đầy đủ và sẵn sàng bảo vệ trước Hội đồng. Em xin chân thành cảm ơn quý Thầy/Cô đã chú ý lắng nghe!"*

---

# CHƯƠNG II: TỪ ĐIỂN BÁCH KHOA TOÀN THƯ MỔ XẺ 6 CHIỀU 38 KHÁI NIỆM & LINH KIỆN

*(Cẩm nang trang bị kiến thức kỹ thuật chuyên sâu cho toàn bộ 34 linh kiện BOM, vật tư ốc vít, IC, giao thức và giải thuật của đề tài).*

---

## KHỐI 1: VI ĐIỀU KHIỂN, MẠCH SO SÁNH & CƠ CẤU ĐIỀU KHIỂN

### 1. Bo Mạch Vi Điều Khiển ESP32 DevKit V1 (30 Chân)
- **1. Bản chất nó là gì?**  
  Là bo mạch phát triển vi điều khiển SoC (System on Chip) tích hợp vi xử lý 32-bit Tensilica Xtensa LX6 Dual-Core cùng module sóng RF Wi-Fi 802.11 b/g/n (2.4GHz) và Bluetooth v4.2 BR/EDR & BLE do Espressif Systems sản xuất.
- **2. Chức năng trong đề tài:**  
  Là "bộ não" trung tâm của trạm cảm biến; đọc tín hiệu analog từ MQ-2, tín hiệu số từ DHT22; thực thi thuật toán lọc nhiễu EMA; điều phối máy trạng thái FSM; đóng cắt rơ-le quạt hút và còi; đồng thời đóng vai trò MQTT Client gửi dữ liệu lên Broker.
- **3. Nguyên lý hoạt động chi tiết:**  
  Chip có 2 nhân (Core 0 và Core 1) chạy ở tần số xung nhịp 240MHz. SRAM 520KB và bộ nhớ flash ngoài 4MB giao tiếp qua chuẩn SPI. Bộ chuyển đổi Analog-to-Digital (ADC) 12-bit tích hợp đọc điện áp từ cảm biến MQ-2 qua ADC1 (GPIO 34).
- **4. Tại sao lại chọn nó mà không chọn Arduino hay STM32?**  
  - So với Arduino Uno (16MHz, 2KB RAM): Không có Wi-Fi, không chạy nổi FreeRTOS và MQTT.  
  - So với STM32F103: Không có Wi-Fi tích hợp, thêm module ESP8266 làm tăng diện tích PCB và rủi ro lỗi UART.  
  - So với Raspberry Pi: ESP32 giá chỉ ~100k, khởi động tức thì <1s, chạy Bare-metal/FreeRTOS không lo hỏng hệ điều hành khi mất điện đột ngột.
- **5. Liên kết / Tương tác:**  
  Nối MQ-2 (GPIO34), DHT22 (GPIO4), Nút nhấn (GPIO13), Relay (GPIO18), Còi (GPIO19), LED Đỏ (GPIO23), LED Xanh (GPIO2). Kết nối Wi-Fi tới Router và Broker MQTT.
- **6. Thông số cốt lõi:**  
  - Nguồn cấp: 5V vào chân Vin (hạ áp xuống 3.3V qua AMS1117).  
  - Dòng tiêu thụ đỉnh khi phát sóng Wi-Fi (+20.5dBm): ~240–260mA.  
  - Độ phân giải ADC: 12-bit (0–4095). Chân GPIO 34 thuộc ADC1 (không bị xung đột Wi-Fi).

---

### 2. Hệ Điều Hành Thời Gian Thực FreeRTOS & Phân Chia Dual-Core
- **1. Bản chất nó là gì?**  
  Là hệ điều hành thời gian thực mã nguồn mở theo cơ chế đa nhiệm ưu tiên định trước (Preemptive Priority-based Scheduler).
- **2. Chức năng trong đề tài:**  
  Phân tách tác vụ mạng và tác vụ cảm biến độc lập, bảo đảm việc đọc cảm biến và phản ứng báo cháy không bao giờ bị giật lag khi mạng Wi-Fi bị nghẽn.
- **3. Nguyên lý hoạt động chi tiết:**  
  - **Core 0 (Networking):** Chạy `Task_Network` duy trì kết nối Wi-Fi, vòng lặp MQTT `loop()`, xử lý gửi nhận tin và bộ đệm SPIFFS.  
  - **Core 1 (Sensing & FSM):** Chạy `Task_SenseControl` chu kỳ 100ms đọc cảm biến, lọc EMA, đánh giá ngưỡng FSM và kích hoạt còi/quạt lập tức.
- **4. Tại sao cần? Nếu dùng hàm `delay()` thông thường thì sao?**  
  Nếu dùng `delay(2000)`, chip bị "đóng băng" 2 giây. Nếu có cháy hoặc người dùng bấm nút khẩn cấp trong 2 giây đó, hệ thống sẽ bỏ sót. FreeRTOS chuyển ngữ cảnh chỉ mất vài micro-giây.
- **5. Liên kết / Tương tác:**  
  Điều phối các tác vụ trong firmware `main.cpp`, giao tiếp giữa 2 nhân qua FreeRTOS Queue.
- **6. Thông số cốt lõi:**  
  - Tick rate: 1000Hz (1 tick = 1ms).  
  - Ưu tiên: Task FSM An toàn đặt mức 3, Task Mạng đặt mức 1.

---

### 3. IC So Sánh Kép LM393 Trên Bo Mạch Cảm Biến MQ-2
- **1. Bản chất nó là gì?**  
  Là một IC tích hợp chứa 2 bộ khuếch đại so sánh điện áp độc lập (Voltage Comparator) ngõ ra cực thu hở (Open Collector).
- **2. Chức năng trong đề tài:**  
  So sánh điện áp ngõ ra của cảm biến MQ-2 với ngưỡng điện áp tham chiếu vi chỉnh qua biến trở xoay, cung cấp tín hiệu logic số DOUT ngắt khẩn cấp.
- **3. Nguyên lý hoạt động chi tiết:**  
  Nếu $V_{in(+)} > V_{ref}$, ngõ ra DOUT ở mức cao (High/3.3V qua trở kéo). Nếu nồng độ khói tăng làm $V_{in(+)}$ vượt ngưỡng, transistor đầu ra dẫn bão hòa kéo ngõ ra DOUT xuống mức thấp (Low/0V), kích hoạt đèn LED cảnh báo trên module.
- **4. Tại sao cần LM393 khi ESP32 đã có bộ đọc ADC?**  
  Ngõ ra AOUT dùng cho ADC ESP32 để đo PPM liên tục, còn ngõ ra DOUT của LM393 đóng vai trò ngắt phần cứng độc lập (Hardware Interrupt), phản ứng tức thì không phụ thuộc vào độ trễ tính toán phần mềm của vi điều khiển.
- **5. Liên kết / Tương tác:**  
  Nhận điện áp từ cầu phân áp của phần tử $SnO_2$, xuất chân DOUT và AOUT về bo mạch chính.
- **6. Thông số cốt lõi:**  
  - Dải điện áp hoạt động: 2V đến 36V.  
  - Thời gian đáp ứng: 1.3 micro-giây.

---

### 4. Module Relay 1 Kênh 5VDC Cách Ly Quang Opto PC817
- **1. Bản chất nó là gì?**  
  Là công tắc điện từ điều khiển bằng tín hiệu điện áp thấp, kết hợp bộ cách ly quang học (Optocoupler PC817 của hãng Sharp) để cô lập hoàn toàn mạch điều khiển với mạch tải công suất.
- **2. Chức năng trong đề tài:**  
  Nhận tín hiệu kích từ chân GPIO18 của ESP32 để đóng/cắt nguồn 12V cho quạt hút khói làm mát.
- **3. Nguyên lý hoạt động chi tiết:**  
  Khi GPIO18 xuất mức LOW (kích Active Low), LED hồng ngoại trong Opto PC817 phát sáng, kích phototransistor dẫn dòng, mở transistor NPN cấp dòng 5V qua cuộn hút relay Songle SRD-05VDC-SL-C. Lực từ trường hút tiếp điểm chuyển từ vị trí thường mở (NO) sang đóng mạch, cấp nguồn 12V cho quạt chạy.
- **4. Tại sao cần Opto và Diode Flyback 1N4148 trên module?**  
  - Opto PC817 ngăn xung gai điện áp tải công suất phóng ngược vào phá hỏng chân GPIO ESP32 (cách điện 5000Vrms).  
  - Diode Flyback 1N4148 mắc ngược song song với cuộn cảm relay để dập tắt xung điện áp cảm ứng ngược sinh ra khi ngắt dòng đột ngột ($V = -L \cdot di/dt$).
- **5. Liên kết / Tương tác:**  
  Chân IN nối GPIO18, tiếp điểm COM nối nguồn 12V, tiếp điểm NO nối dây dương của quạt hút khói.
- **6. Thông số cốt lõi:**  
  - Điện áp cuộn hút: 5VDC, dòng tiêu thụ: ~70mA.  
  - Tiếp điểm chịu tải: 10A / 250VAC hoặc 10A / 30VDC.

---

### 5. Còi Chíp Báo Động Active Buzzer 5VDC
- **1. Bản chất nó là gì?**  
  Là thiết bị phát âm thanh cảnh báo tích hợp sẵn mạch dao động nội bên trong (Active Buzzer).
- **2. Chức năng trong đề tài:**  
  Hú còi khẩn cấp tại chỗ với âm lượng lớn khi hệ thống chuyển sang trạng thái báo động ALARM.
- **3. Nguyên lý hoạt động chi tiết:**  
  Bên trong tích hợp mạch dao động tạo xung tần số ~2.3kHz và một màng rung áp điện (Piezoelectric Diaphragm). Chỉ cần cấp nguồn điện DC 5V (hoặc kích mức logic), mạch dao động tự kích màng rung co giãn cơ học phát ra tiếng còi hú chíp chíp liên tục.
- **4. Tại sao chọn Active Buzzer mà không chọn Passive Buzzer?**  
  Passive Buzzer đòi hỏi vi điều khiển phải xuất xung PWM liên tục bằng lệnh `tone()`, gây tốn tài nguyên Timer CPU. Active Buzzer chỉ cần xuất mức logic HIGH/LOW đơn giản trên GPIO19 là còi hú ngay.
- **5. Liên kết / Tương tác:**  
  Chân dương nối GPIO19, chân âm nối GND.
- **6. Thông số cốt lõi:**  
  - Điện áp: 3.5V – 5.5V. Cường độ âm thanh: >85dB ở khoảng cách 10cm. Dòng hoạt động: <30mA.

---

### 6. Bộ Đôi Đèn LED Chỉ Thị Trạng Thái Phi 5mm (Đỏ & Xanh)
- **1. Bản chất nó là gì?**  
  Là linh kiện bán dẫn phát quang (Light Emitting Diode) chuẩn chân cắm đường kính 5mm.
- **2. Chức năng trong đề tài:**  
  - LED Xanh: Báo nguồn hệ thống đang hoạt động và trạng thái kết nối mạng ổn định.  
  - LED Đỏ: Nhấp nháy cảnh báo nguy cấp khi nồng độ khói vượt ngưỡng an toàn.
- **3. Nguyên lý hoạt động chi tiết:**  
  Khi được phân cực thuận với điện áp vượt ngưỡng điện thế tiếp giáp p-n, các hạt electron tái hợp với lỗ trống giải phóng năng lượng dưới dạng photon ánh sáng nhìn thấy.
- **4. Tại sao cần cả 2 màu Đỏ và Xanh?**  
  Theo tiêu chuẩn an toàn PCCC quốc tế: Xanh biểu trưng cho Normal/Safe, Đỏ biểu trưng cho Fire/Danger, giúp nhận diện tức thì tình trạng trạm ở khoảng cách xa.
- **5. Liên kết / Tương tác:**  
  LED Đỏ nối chân GPIO23 qua trở hạn dòng, LED Xanh nối chân GPIO2.
- **6. Thông số cốt lõi:**  
  - Điện áp rơi thuận: LED Đỏ ~1.8V–2.0V; LED Xanh ~2.8V–3.2V.  
  - Dòng định mức hoạt động an toàn: 5mA – 15mA.

---

### 7. Điện Trở Hạn Dòng Cho LED 330Ω (1/4W, Sai Số 5%)
- **1. Bản chất nó là gì?**  
  Là linh kiện thụ động cản trở dòng điện theo định luật Ohm, sử dụng màng than (Carbon Film) công suất danh định 0.25W.
- **2. Chức năng trong đề tài:**  
  Giới hạn dòng điện chạy qua đèn LED không vượt quá giới hạn an toàn của chân GPIO ESP32.
- **3. Nguyên lý & Công thức tính toán chi tiết:**  
  Áp dụng định luật Ohm cho mạch nối tiếp với nguồn GPIO 3.3V và LED Đỏ có điện áp rơi thuận $V_F = 2.0\text{V}$:
  $$I_F = \frac{V_{GPIO} - V_F}{R} = \frac{3.3\text{V} - 2.0\text{V}}{330\Omega} = \frac{1.3\text{V}}{330\Omega} \approx 3.94\text{mA}$$
  Dòng điện ~4mA đủ để LED sáng rõ và hoàn toàn nằm trong dải an toàn của chân ESP32 (giới hạn chịu dòng là 12mA).
- **4. Tại sao không nối trực tiếp LED vào chân GPIO không cần điện trở?**  
  LED là linh kiện phi tuyến có nội trở động cực nhỏ. Nếu nối trực tiếp không qua điện trở, dòng điện qua tiếp giáp p-n sẽ vọt lên hàng trăm mA, gây sụt áp toàn chip và làm nổ tiếp giáp bán dẫn của chân GPIO ESP32 ngay lập tức.
- **5. Liên kết / Tương tác:**  
  Mắc nối tiếp giữa chân GPIO23/GPIO2 và cực Anode (+) của đèn LED.
- **6. Thông số cốt lõi:**  
  - Giá trị: 330Ω (Cam - Cam - Nâu - Vàng kim).  
  - Công suất tổn hao: $P = I^2 \cdot R \approx (0.004)^2 \cdot 330 \approx 0.005\text{W} \ll 0.25\text{W}$.

---

### 8. Nút Nhấn Khẩn Cấp / Test Thủ Công (12x12mm, 4 Chân)
- **1. Bản chất nó là gì?**  
  Là công tắc nút bấm cơ khí tức thời (Momentary Tactile Push Button) dạng tiếp điểm thường mở (Normally Open - NO).
- **2. Chức năng trong đề tài:**  
  Cho phép kỹ thuật viên bấm nút kiểm tra định kỳ (Test thủ công) hoặc cư dân kích hoạt quạt hút khói cưỡng bức trong tình huống khẩn cấp tại chỗ.
- **3. Nguyên lý hoạt động chi tiết:**  
  Ở trạng thái nghỉ, lò xo giữ tiếp điểm mở. Khi người dùng ấn nút, màng kim loại uốn cong tạo liên kết dẫn điện giữa các chân, kéo chân GPIO xuống mức GND (0V). Khi thả tay, lò xo đàn hồi trả tiếp điểm về trạng thái hở mạch.
- **4. Tại sao trong code cần thuật toán chống dội phím (Debounce)?**  
  Tiếp điểm kim loại khi va chạm cơ học sẽ bị rung dội cơ học (Bouncing) trong khoảng 5–10 mili-giây đầu tiên, sinh ra hàng chục xung HIGH/LOW liên tiếp. Nếu không có lọc debounce phần mềm, ESP32 sẽ hiểu nhầm là người dùng đã bấm nút hàng chục lần.
- **5. Liên kết / Tương tác:**  
  Một đầu nối chân GPIO13, đầu còn lại nối GND.
- **6. Thông số cốt lõi:**  
  - Tuổi thọ cơ khí: >100.000 lần bấm. Thời gian trễ lọc rung phím trong code: 50ms.

---

### 9. Điện Trở Treo Mức Cao Pull-Up 10kΩ Cho Nút Nhấn
- **1. Bản chất nó là gì?**  
  Là điện trở phân cực mức logic cao (Pull-up Resistor) nối giữa đường tín hiệu vào của chân vi điều khiển và nguồn điện dương 3.3V.
- **2. Chức năng trong đề tài:**  
  Đảm bảo chân GPIO13 luôn duy trì mức logic HIGH (1) ổn định khi nút nhấn đang ở trạng thái nhả (không bấm).
- **3. Nguyên lý hoạt động chi tiết:**  
  Khi nút nhấn hở mạch, không có dòng điện chạy vào chân ngõ vào có trở kháng rất cao của ESP32 ($I \approx 0$), giữ chân GPIO13 ở đúng mức điện thế 3.3V. Khi bấm nút, dòng điện chạy từ 3.3V qua 10kΩ xuống GND:
  $$I = \frac{3.3\text{V}}{10\text{k}\Omega} = 0.33\text{mA}$$
  Mức dòng 0.33mA cực nhỏ, tiêu thụ điện không đáng kể nhưng kéo chân GPIO13 về mức 0V dứt khoát.
- **4. Nếu không gắn điện trở kéo mà để chân hở thì sao?**  
  Chân GPIO sẽ rơi vào trạng thái "lơ lửng" (Floating Pin). Chân này hoạt động như một ăng-ten thu sóng điện từ xung quanh, làm mức logic nhảy loạn xạ giữa 0 và 1, khiến hệ thống tự động kích hoạt quạt hút và hú còi sai.
- **5. Liên kết / Tương tác:**  
  Nối giữa nguồn 3.3V và chân GPIO13.
- **6. Thông số cốt lõi:**  
  - Giá trị: 10kΩ (Nâu - Đen - Cam - Vàng kim). Công suất: 1/4W.

---

## KHỐI 2: CẢM BIẾN MÔI TRƯỜNG & KHÍ ĐỘC

### 10. Cảm Biến Khói & Khí Gas MQ-2 Chuẩn Datasheet Hanwei
- **1. Bản chất nó là gì?**  
  Là cảm biến khí điện hóa bán dẫn oxit kim loại (MOS Gas Sensor) sử dụng lớp màng nhạy khí Thiếc Đioxit ($SnO_2$) do tập đoàn Hanwei Electronics chế tạo.
- **2. Chức năng trong đề tài:**  
  Phát hiện sớm khói cháy nung âm ỉ và khí rò rỉ (LPG, Propane, Methane, khói gỗ/giấy) trong dải nồng độ từ 200 PPM đến 10.000 PPM.
- **3. Nguyên lý hoạt động chi tiết theo Datasheet Hanwei:**  
  - **Cuộn sấy nung nóng:** Cuộn dây sấy bên trong có điện trở $R_H \approx 31\Omega \pm 3\Omega$, tiêu thụ công suất $P_H \approx 800 - 900\text{mW}$ ($I_H \approx 150-160\text{mA}$), bắt buộc phải được cấp nguồn **$5.0\text{V} \pm 0.1\text{V}$ trực tiếp từ ngõ ra IC Buck LM2596S** để nung nóng màng $SnO_2$ đạt nhiệt độ làm việc tối ưu $200^\circ\text{C}-300^\circ\text{C}$.  
  - **Cơ chế nhạy khí:** Trong không khí sạch, các phân tử oxy bị hấp phụ trên bề mặt màng bán dẫn và bẫy electron tự do, làm điện trở màng cảm biến $R_s$ tăng cao. Khi có hạt khói hoặc khí cháy tiếp xúc, chúng phản ứng khử với các ion oxy bề mặt, giải phóng electron trả lại dải dẫn, làm điện trở $R_s$ tụt giảm đột ngột.  
  - **Cầu phân áp ngõ ra Analog ($A_{OUT}$):** Ngõ ra tín hiệu của cảm biến MQ-2 biến thiên từ $0 - 5\text{V}$. Do chân ADC ESP32 chỉ chịu tối đa 3.3V, mạch sử dụng **cầu phân áp $R_1=10\text{k}\Omega, R_2=20\text{k}\Omega$ (tỷ số phân áp $2/3$)** để hạ mức điện áp an toàn về $0 - 3.33\text{V}$ trước khi đưa vào GPIO 34.
- **4. Tại sao MQ-2 cắm vào bị nóng và nhảy số lung tung trong 5 phút đầu?**  
  Dây sấy tiêu thụ dòng ~160mA để nung nóng màng $SnO_2$ nên vỏ kim loại ấm nóng là hoàn toàn bình thường. Trong 5 phút đầu, lớp oxit chưa đạt trạng thái cân bằng nhiệt động học, do đó firmware phải cài đặt chế độ Warm-up sấy sơ bộ trước khi đo chính xác.
- **5. Liên kết / Tương tác:**  
  Chân VCC nối nguồn 5V LM2596S, chân AOUT qua cầu trở 10k/20k nối chân GPIO34 (ADC1_CH6) của ESP32.
- **6. Thông số cốt lõi:**  
  - Dải phát hiện: 200 – 10.000 PPM. Điện áp sấy: 5.0V ± 0.1V. Điện trở cuộn sấy: $31\Omega \pm 3\Omega$.

---

### 11. Cảm Biến Nhiệt Độ & Độ Ẩm Kỹ Thuật Số DHT22 (AM2302)
- **1. Bản chất nó là gì?**  
  Là module cảm biến môi trường số tích hợp sẵn bộ vi điều khiển 8-bit bên trong do Aosong Electronics chế tạo.
- **2. Chức năng trong đề tài:**  
  Đo nhiệt độ và độ ẩm không khí môi trường xung quanh trạm P302, phục vụ thuật toán phân tích gia tốc nhiệt độ để loại trừ báo động giả.
- **3. Nguyên lý hoạt động chi tiết:**  
  - Đo nhiệt độ: Sử dụng nhiệt điện trở hệ số nhiệt âm (NTC Thermistor) có điện trở giảm theo hàm mũ khi nhiệt độ tăng.  
  - Đo độ ẩm: Sử dụng màng polymer điện dung có điện dung thay đổi tỷ lệ thuận với lượng hơi ẩm hấp thụ trong không khí.  
  - Chip vi điều khiển tích hợp tự động đọc 2 cảm biến và đóng gói thành chuỗi xung số 40-bit gồm: 16 bit độ ẩm + 16 bit nhiệt độ + 8 bit mã kiểm tra sai số Checksum.
- **4. Tại sao chọn DHT22 thay vì DHT11?**  
  - DHT11 có sai số nhiệt độ rất lớn (±2°C), dải đo hẹp (0–50°C), không thể nhận diện được gia tốc tăng nhiệt nhỏ 1–2°C/phút khi có khói âm ỉ.  
  - DHT22 có độ chính xác cao gấp 4 lần: sai số nhiệt chỉ ±0.5°C, độ phân giải 0.1°C, dải đo rộng từ -40°C đến 80°C.
- **5. Liên kết / Tương tác:**  
  Chân Data nối chân GPIO4 của ESP32 kèm điện trở kéo lên 10kΩ.
- **6. Thông số cốt lõi:**  
  - Sai số nhiệt độ: ±0.5°C (độ phân giải 0.1°C). Sai số độ ẩm: ±2% RH. Chu kỳ đọc mẫu tối thiểu: 2 giây.

---

## KHỐI 3: NGUỒN CÔNG SUẤT, THIẾT BỊ CHẤP HÀNH & BẢO VỆ ĐIỆN NĂNG

### 12. Quạt Hút Khói & Tản Nhiệt DC 12V 0.18A (80x80x25mm)
- **1. Bản chất nó là gì?**  
  Là động cơ điện một chiều không chổi than (Brushless DC - BLDC Motor) kết hợp cánh quạt hướng trục (Axial Fan) kích thước tiêu chuẩn 80mm.
- **2. Chức năng trong đề tài:**  
  Tạo luồng gió cưỡng bức hút khí độc và hạt khói ra khỏi phòng qua đường ống thoát gió khi xảy ra hỏa hoạn, đồng thời làm mát vỏ trạm thiết bị.
- **3. Nguyên lý hoạt động chi tiết:**  
  Sử dụng mạch điều khiển điện tử tích hợp cảm biến Hall để đảo chiều dòng điện trong các cuộn dây stator theo góc quay của rotor nam châm vĩnh cửu. Nhờ không dùng chổi than cơ học, quạt không phát sinh tia lửa điện, bảo đảm an toàn chống cháy nổ tuyệt đối trong môi trường có khí gas rò rỉ.
- **4. Tại sao chọn quạt 12V mà không dùng quạt 5V?**  
  Quạt 5V có lưu lượng gió (CFM) rất yếu và áp suất tĩnh thấp, không thể đẩy khói qua màng lọc hoặc đường ống xả. Quạt 12V cho lưu lượng gió lớn hơn gấp 3 lần (đạt ~40 CFM), đủ lực hút khói hiệu quả.
- **5. Liên kết / Tương tác:**  
  Cực dương quạt nối tiếp điểm NO của Relay 1 kênh, cực âm nối GND chung nguồn 12V.
- **6. Thông số cốt lõi:**  
  - Điện áp danh định: 12VDC. Dòng tiêu thụ: 0.18A. Công suất: 2.16W. Tốc độ quay: ~2800 vòng/phút (RPM).

---

### 13. Lưới Thép Bảo Vệ Quạt 80mm Mạ Niken/Crom
- **1. Bản chất nó là gì?**  
  Là tấm lưới chắn bảo vệ cơ khí chế tạo từ các nan thép kéo nguội được hàn điểm và mạ điện phân Niken/Crom sáng bóng.
- **2. Chức năng trong đề tài:**  
  Lắp che phủ mặt hút của quạt 80mm trên nắp vỏ hộp, ngăn chặn ngón tay người thao tác hoặc dị vật (chuột, côn trùng, dây điện) lọt vào cánh quạt đang quay tốc độ cao.
- **3. Nguyên lý cơ học:**  
  Khoảng cách nan thép được tính toán theo tiêu chuẩn an toàn máy công nghiệp, vừa ngăn chặn dị vật có kích thước >5mm vừa bảo đảm diện tích thông gió mở >85%, không cản trở lưu lượng hút gió của quạt.
- **4. Tại sao cần mạ Niken/Crom?**  
  Trong môi trường khói cháy có chứa nhiều khí lưu huỳnh ($SO_2$) và hơi ẩm, thép thông thường sẽ bị rỉ sét ăn mòn rất nhanh. Lớp mạ Niken chống oxy hóa và chịu nhiệt độ cao vượt trội.
- **5. Liên kết / Tương tác:**  
  Kẹp chặt cùng quạt vào nắp vỏ hộp bằng 4 bộ bu-lông M4x35mm.

---

### 14. Adapter Nguồn AC-DC 12V - 2A (Flyback Converter)
- **1. Bản chất nó là gì?**  
  Là bộ nguồn chuyển mạch đóng cắt (Switch-Mode Power Supply - SMPS) biến đổi điện áp xoay chiều lưới điện 100–240VAC thành điện thế một chiều 12VDC cách ly.
- **2. Chức năng trong đề tài:**  
  Là nguồn cung cấp năng lượng sơ cấp cho toàn bộ trạm thiết bị P302 (nuôi trực tiếp quạt hút 12V và cấp điện cho mạch hạ áp LM2596S).
- **3. Nguyên lý hoạt động chi tiết:**  
  Điện áp 220VAC được chỉnh lưu cầu và lọc thành DC cao áp (~310V), sau đó IC điều khiển băm xung PWM đóng ngắt transistor MOSFET qua biến áp xung Flyback tần số cao (65kHz). Cuộn thứ cấp nắn dòng và lọc thành 12VDC ổn định. Vòng phản hồi cách ly bằng Opto PC817 và IC TL431 duy trì điện áp ngõ ra chuẩn xác.
- **4. Tại sao chọn nguồn 12V - 2A (công suất 24W)?**  
  Tổng dòng tiêu thụ cực đại của hệ thống khi toàn tải (Quạt 12V 0.18A + LM2596S cấp ESP32, MQ-2, Relay ~0.24A) là khoảng 0.42A tại 12V. Chọn nguồn 2A bảo đảm hệ số an toàn dư tải gấp 5 lần (~400%), giúp adapter chạy mát, không bị quá tải và bền bỉ suốt nhiều năm.
- **5. Liên kết / Tương tác:**  
  Cắm jack đực 5.5x2.1mm vào Jack cái gắn trên thành vỏ trạm thiết bị.
- **6. Thông số cốt lõi:**  
  - Điện áp ngõ vào: 100 – 240VAC 50/60Hz. Ngõ ra: 12VDC ± 5%, dòng tải định mức 2A.

---

### 15. Mạch Hạ Áp Buck DC-DC LM2596S (12V Xuống 5V - 3A)
- **1. Bản chất nó là gì?**  
  Là bo mạch hạ áp xung nguyên khối (Step-Down Switching Regulator) sử dụng IC LM2596S của hãng Texas Instruments.
- **2. Chức năng trong đề tài:**  
  Hạ áp 12V xuống 5V để nuôi vi điều khiển ESP32, cuộn sấy cảm biến MQ-2, cảm biến DHT22 và cuộn hút rơ-le.
- **3. Nguyên lý hoạt động chi tiết:**  
  Sử dụng cơ chế điều chế độ rộng xung PWM tần số cố định 150kHz đóng ngắt van bán dẫn DMOS nội bộ. Cuộn cảm 33µH tích trữ và giải phóng năng lượng kết hợp diode Schottky SS34 thoát dòng ngược, cho hiệu suất chuyển đổi lên tới 92%.
- **4. So sánh tổn hao nhiệt với IC 7805:**  
  7805 tỏa nhiệt 3.5W làm sập nguồn, trong khi LM2596S chỉ tổn hao 0.22W, mạch chạy mát và ổn định 24/7.
- **5. Liên kết / Tương tác:**  
  Đầu vào nối sau Cầu chì 2A từ nguồn 12V. Đầu ra nối chân Vin ESP32, chân sấy VCC MQ-2 và module cảm biến.
- **6. Thông số cốt lõi:**  
  - Tần số đóng cắt: 150kHz. Hiệu suất: 92%. Dòng ra tối đa: 3A.

---

### 16. Cầu Chì Ống Thủy Tinh 5x20mm 2A Fast-Blow
- **1. Bản chất nó là gì?**  
  Là linh kiện bảo vệ quá dòng tác động nhanh (Fast-Acting / Fast-Blow Fuse) chứa dây chảy bằng hợp kim chì-thiếc trong ống thủy tinh kín.
- **2. Chức năng trong đề tài:**  
  Ngắt mạch điện tức thì khi xảy ra ngắn mạch (chập tải) trên đường nguồn 12V hoặc sự cố chập sau LM2596S, bảo vệ adapter và chống cháy nổ trạm.
- **3. Nguyên lý hoạt động chi tiết:**  
  Khi dòng điện vượt quá 2A, nhiệt lượng sinh ra theo định luật Joule-Lenz làm dây kim loại nóng chảy đứt đoạn trong vòng vài mili-giây, cô lập hoàn toàn mạch điện khỏi nguồn cung cấp.
- **4. Tại sao chọn loại Fast-blow mà không chọn Slow-blow?**  
  Slow-blow dùng cho tải có dòng khởi động động cơ lớn. Trong mạch điện tử vi điều khiển, sự cố ngắn mạch cần phải được ngắt cực nhanh (dưới 20ms) để linh kiện bán dẫn không bị đánh thủng.
- **5. Liên kết / Tương tác:**  
  Mắc nối tiếp ngay sau cực dương của Jack nguồn DC 12V ngõ vào.

---

### 17. Hộp/Đế Gắn Cầu Chì PCB 5x20mm Có Nắp Đậy Bảo Vệ
- **1. Bản chất nó là gì?**  
  Là đế gắn cầu chì dạng chân cắm bo mạch in (PCB Mount Fuse Holder) chế tạo bằng nhựa PBT chống cháy kèm 2 ngàm kẹp bằng đồng phốt-pho mạ thiếc.
- **2. Chức năng trong đề tài:**  
  Giữ cố định cầu chì ống 5x20mm chắc chắn trên PCB và cho phép thay thế cầu chì nhanh chóng khi bị đứt mà không cần tháo mỏ hàn.
- **3. Cấu tạo cơ khí:**  
  Nắp nhựa trong suốt chụp kín bên ngoài giúp cách điện tuyệt đối, ngăn người thao tác chạm tay vào điện áp hở và chống bụi bẩn xâm nhập làm oxy hóa tiếp điểm.
- **4. Thông số cốt lõi:**  
  - Kích thước tương thích: Cầu chì ống 5x20mm. Dòng định mức tiếp điểm: 10A 250VAC.

---

### 18. Mạch Lọc Nguồn Kép: Tụ Hóa 100µF/25V Song Song Tụ Gốm 100nF
- **1. Bản chất nó là gì?**  
  Là sự kết hợp bù trừ đặc tính giữa tụ hóa dung lượng lớn (Electrolytic Capacitor) và tụ gốm cao tần (Ceramic Capacitor) mắc song song trên thanh dẫn nguồn.
- **2. Chức năng trong đề tài:**  
  - Tụ hóa 100µF: Bù sụt áp tức thời khi ESP32 phát xung sóng Wi-Fi RF (dòng tăng vọt 250mA trong micro-giây).  
  - Tụ gốm 100nF: Khử các gai xung điện áp cao tần 150kHz phát sinh từ bộ nguồn chuyển mạch LM2596S.
- **3. Nguyên lý phối hợp tần số:**  
  Tụ hóa có điện dung lớn nhưng độ tự cảm ký sinh (ESL) cao nên không lọc được tần số >100kHz. Tụ gốm có ESR và ESL cực nhỏ, phản ứng tức thời ở dải tần hàng chục MHz. Hai tụ mắc song song tạo thành bộ lọc thông thấp hoàn hảo cho toàn dải tần.
- **4. Vị trí bố trí trên PCB:**  
  Tụ gốm 100nF bắt buộc phải đặt càng sát chân Vin/VCC của chip ESP32 càng tốt (khoảng cách đường mạch <10mm) để giảm thiểu điện cảm đường mạch.

---

### 19. Công Tắc Bập Bênh Nguồn KCD11 (2 Chân, 3A/250VAC)
- **1. Bản chất nó là gì?**  
  Là công tắc bật/tắt cơ khí dạng bập bênh (Rocker Switch) 1 cực 1 tiếp điểm (SPST).
- **2. Chức năng trong đề tài:**  
  Đóng/ngắt nguồn điện chính 12V cấp vào toàn bộ trạm thiết bị một cách cơ động và an toàn khi lắp đặt hoặc bảo trì.
- **3. Cấu tạo cơ khí:**  
  Vỏ bằng nhựa Nylon 66 cách điện chịu nhiệt, ngàm cài đàn hồi cho phép ấn khóa cố định vào khe khoét trên mặt vỏ hộp thiết bị.
- **4. Thông số cốt lõi:**  
  - Dòng chịu tải: 3A / 250VAC (hoặc 6A / 12VDC). Tiếp điểm bằng đồng mạ bạc chống tia lửa điện.

---

## KHỐI 4: ĐẤU NỐI, VỎ HỘP & VẬT TƯ CƠ KHÍ LẮP RÁP THỰC TẾ

### 20. Jack Nguồn DC Cái Gắn Vỏ 5.5 x 2.1mm
- **1. Bản chất nó là gì?**  
  Là đầu nối nguồn DC chuẩn công nghiệp (DC Barrel Power Jack) dạng bắt xuyên bảng vỏ hộp (Panel Mount).
- **2. Chức năng trong đề tài:**  
  Tiếp nhận đầu cắm jack đực từ adapter 12V xuyên qua thành vỏ hộp nhựa, dẫn nguồn điện vào bo mạch bên trong.
- **3. Cấu tạo cơ học:**  
  Thân có ren vặn kèm đai ốc kim loại siết chặt từ mặt ngoài vỏ hộp, có vòng đệm cao su chống lỏng và chống thấm nước theo chuẩn IP54.
- **4. Kích thước chuẩn:**  
  Đường kính ngoài 5.5mm, đường kính kim cực dương ở tâm 2.1mm.

---

### 21. Cọc Đấu Dây Vặn Ốc KF301-2P & KF301-3P (Screw Terminal)
- **1. Bản chất nó là gì?**  
  Là khối cọc đấu nối dây điện công nghiệp vặn ốc (Terminal Block), bước chân tiêu chuẩn 5.0mm (Pitch 5.0mm).
- **2. Chức năng trong đề tài:**  
  - Cọc KF301-2P (2 chân): Đấu nối đường nguồn 12V vào và dây cấp nguồn cho động cơ quạt hút.  
  - Cọc KF301-3P (3 chân): Đấu nối dây tín hiệu VCC, GND, DATA của cảm biến rời.
- **3. Nguyên lý cơ học:**  
  Lá đồng đàn hồi ép chặt lõi dây điện thông qua vít siết bake, tạo mối tiếp xúc cơ-điện chắc chắn, chịu được rung động và không bị tuột dây.
- **4. Lợi ích kỹ thuật:**  
  Cho phép tháo lắp, thay thế linh kiện hoặc quạt hút nhanh chóng tại công trình chỉ bằng một chiếc tuốc-nơ-vít, không cần mang theo mỏ hàn chì.

---

### 22. Hàng Rào Cắm Cái (Female Header 1x15P Bước 2.54mm)
- **1. Bản chất nó là gì?**  
  Là socket cắm bo mạch gồm 15 lỗ chân cắm tiếp xúc bằng đồng mạ thiếc, khoảng cách chân chuẩn 2.54mm (0.1 inch).
- **2. Chức năng trong đề tài:**  
  Hàn cố định 2 hàng rào 15 chân lên bo mạch in Main PCB để tạo đế cắm tháo lắp linh hoạt cho board vi điều khiển ESP32 DevKit V1 (30 chân).
- **3. Lợi ích kỹ thuật cốt lõi:**  
  Tránh hàn nhiệt trực tiếp lên chân chip ESP32 (nguy cơ sốc nhiệt gây chết chip), đồng thời dễ dàng rút ESP32 ra cắm cáp nạp code hoặc thay thế chip dự phòng khi có sự cố.

---

### 23. Dây Điện Silicon Chịu Nhiệt 22AWG
- **1. Bản chất nó là gì?**  
  Là dây dẫn điện chuyên dụng chất lượng cao, lõi gồm 60 sợi đồng siêu nhỏ mạ thiếc xoắn lại, bọc ngoài bằng lớp vỏ cao su silicon chịu nhiệt độ cao (-60°C đến +200°C).
- **2. Chức năng trong đề tài:**  
  Đi dây cho các đường nguồn công suất 12V và 5V nối giữa adapter, mạch LM2596S, relay và quạt hút.
- **3. Ưu điểm so với dây điện PVC thông thường:**  
  Vỏ silicon không bị giòn gãy, không nóng chảy khi tiếp xúc với mỏ hàn hoặc nhiệt lượng của trạm PCCC, lõi đồng nhiều sợi mạ thiếc có khả năng chống oxy hóa tuyệt hảo và chịu uốn gập cơ học cao.

---

### 24. Dây Cắm Tín Hiệu Dupont 2.54mm (Đực - Cái, 20cm)
- **1. Bản chất nó là gì?**  
  Là dây dẫn tín hiệu mềm nhiều sợi, hai đầu được bấm cos vuông chuẩn Dupont và bọc vỏ nhựa cách điện bước 2.54mm.
- **2. Chức năng trong đề tài:**  
  Kết nối linh hoạt các chân tín hiệu logic (GPIO) giữa header của ESP32 với các module cảm biến và cơ cấu chấp hành trong giai đoạn kiểm thử.

---

### 25. Ống Gen Co Nhiệt Polyolefin (Phi 2mm, 4mm, 6mm)
- **1. Bản chất nó là gì?**  
  Là ống bọc cách điện chế tạo từ vật liệu polymer liên kết chéo (Cross-linked Polyolefin) có đặc tính co rút lại khi gặp nhiệt độ cao.
- **2. Chức năng trong đề tài:**  
  Bọc kín các mối nối dây điện, chân cắm jack DC và chân công tắc nguồn, cách ly hoàn toàn kim loại hở với môi trường.
- **3. Đặc tính kỹ thuật:**  
  Tỷ lệ co 2:1, nhiệt độ co ~100°C–125°C, khả năng chịu điện áp đánh thủng lên tới 600V, chống cháy lan.

---

### 26. Vỏ Hộp Nhựa ABS Chống Cháy Đạt Chuẩn Bảo Vệ IP54
- **1. Bản chất nó là gì?**  
  Là vỏ hộp bảo vệ thiết bị đúc nguyên khối từ nhựa Acrylonitrile Butadiene Styrene (ABS) nguyên sinh có pha phụ gia chống cháy lan, kích thước 158 x 90 x 60mm.
- **2. Chức năng trong đề tài:**  
  Chứa toàn bộ bo mạch điện tử, relay và mạch nguồn bên trong; bảo vệ mạch khỏi tác động cơ học va đập và môi trường bụi ẩm của hành lang PCCC.
- **3. Giải mã tiêu chuẩn IP54:**  
  - Chữ số 5 (Bảo vệ chống bụi): Ngăn chặn bụi mịn xâm nhập ở mức độ có thể làm ảnh hưởng đến sự vận hành bình thường của mạch điện.  
  - Chữ số 4 (Bảo vệ chống nước): Chống nước bắn tung tóe từ mọi hướng.
- **4. Thông số cốt lõi:**  
  - Khả năng chống cháy: Đạt tiêu chuẩn UL94-V0 (tự tắt lửa trong vòng 10 giây, không nhỏ giọt tàn cháy).

---

### 27. Bo Mạch In 2 Lớp (Main PCB FR4 Dày 1.6mm)
- **1. Bản chất nó là gì?**  
  Là bo mạch in 2 lớp mạch (Double-sided Printed Circuit Board) gia công trên phíp sợi thủy tinh chống cháy chuẩn FR4 (Flame Retardant 4) dày tiêu chuẩn 1.6mm, kích thước 100 x 70mm.
- **2. Chức năng trong đề tài:**  
  Tích hợp toàn bộ đường mạch điện, socket cắm ESP32, linh kiện thụ động R-C, relay và cọc đấu dây thành một khối mạch vững chắc chuyên nghiệp.
- **3. Đặc tính kỹ thuật bo mạch:**  
  - Phủ sơn hàn Solder Mask màu xanh lá cách điện và chống oxy hóa đường đồng.  
  - Bề mặt các lỗ chân cắm được mạ thiếc (HASL) giúp mối hàn ngấu chì bóng đẹp.  
  - Lớp mặt đáy phủ lưới đồng Mass GND (Copper Pour Ground Plane) có tác dụng che chắn sóng điện từ (EMI Shielding) và tản nhiệt cho toàn bo mạch.

---

### 28. Bộ Trụ Đồng Lục Giác M3x10mm Đực - Cái & Đai Ốc DIN934
- **1. Bản chất nó là gì?**  
  Là trụ đệm cơ khí chế tạo từ đồng thau nguyên khối (Brass Standoff), tiện ren tiêu chuẩn M3 (đường kính ren 3mm), chiều dài thân lục giác 10mm kèm đoạn ren đực dài 6mm.
- **2. Chức năng trong đề tài:**  
  Nâng bo mạch PCB cách mặt đáy vỏ hộp 10mm, tạo khoảng không gian cách ly an toàn.
- **3. Ý nghĩa kỹ thuật an toàn:**  
  Nếu đặt bo mạch sát đáy vỏ hộp, nước đọng ẩm hoặc các mối hàn sắc nhọn có thể chạm vào đáy gây chập mạch hoặc vỡ vỏ. Trụ đồng 10mm tạo độ thông thoáng tản nhiệt và chống ẩm hoàn hảo.

---

### 29. Ốc Vít Bake Đầu Dù M3x6mm Inox 304 & Vòng Đệm Nylon M3
- **1. Bản chất nó là gì?**  
  - Ốc vít bake (Phillips Pan Head Screw) ren M3 dài 6mm đúc từ thép không gỉ Austenitic Inox 304.  
  - Vòng đệm phẳng (Washer) chế tạo từ nhựa kỹ thuật Nylon trắng.
- **2. Chức năng trong đề tài:**  
  Siết chặt 4 góc của bo mạch PCB vào đầu ren trụ đồng.
- **3. Tác dụng của vòng đệm Nylon:**  
  Khi siết mạnh ốc kim loại vào bo mạch, cạnh sắc của đầu ốc có thể làm xước rách lớp sơn phủ xanh bảo vệ quanh lỗ khoan, gây chập đường mạch in với vỏ ốc. Vòng đệm Nylon đóng vai trò lớp lót đàn hồi cách điện và chống trầy xước bề mặt PCB.

---

### 30. Bu-Lông & Đai Ốc M4x35mm Kèm Đệm Vênh Gắn Quạt
- **1. Bản chất nó là gì?**  
  Là bộ bu-lông ren M4 dài 35mm bằng inox kèm đai ốc và vòng đệm vênh đàn hồi (Spring Lock Washer).
- **2. Chức năng trong đề tài:**  
  Xuyên qua nắp vỏ hộp và thân quạt 80x80x25mm cùng lưới thép bảo vệ để siết chặt toàn bộ cụm quạt hút vào vỏ trạm.
- **3. Tác dụng của đệm vênh:**  
  Động cơ quạt khi quay ở tốc độ cao (2800 RPM) sẽ sinh ra rung động cơ học liên tục. Đệm vênh tạo lực nén đàn hồi thường trực ngăn ốc tán bị tự xoay lỏng theo thời gian.

---

### 31. Vít Nở & Tắc Kê Nhựa Phi 6 Gắn Tường
- **1. Bản chất nó là gì?**  
  Bộ liên kết gồm tắc kê nhựa Polyethylene phi 6mm và vít tự khoan thép mạ kẽm M3.5 x 25mm.
- **2. Chức năng trong đề tài:**  
  Cố định trạm giám sát chắc chắn lên tường gạch hoặc vách thạch cao của hành lang khu vực P302.
- **3. Cơ chế chịu lực:**  
  Khi siết vít vào trong tắc kê nhựa đã đóng vào lỗ khoan tường, ren vít làm nở các cánh gai của tắc kê áp chặt vào thành lỗ khoan gạch, tạo lực ma sát chịu tải trọng kéo nhổ trên 15kg.

---

### 32. Gioăng Cao Su Luồn Dây Grommet Phi 12mm
- **1. Bản chất nó là gì?**  
  Là vòng đệm cao su tổng hợp chịu nhiệt đàn hồi có rãnh gờ giữ ở chu vi ngoài, đường kính lỗ luồn dây 12mm.
- **2. Chức năng trong đề tài:**  
  Lắp bịt kín mép lỗ khoét luồn dây điện xuyên qua thành vỏ hộp nhựa.
- **3. Tác dụng kỹ thuật an toàn:**  
  Thành vỏ nhựa sau khi khoan khoét có cạnh rất sắc. Sau thời gian dài rung lắc, cạnh sắc này có thể cứa đứt lớp vỏ bọc dây điện gây chập nguồn. Gioăng cao su tạo lớp đệm êm ái chống cứa dây và ngăn bụi ẩm lọt qua khe hở.

---

## KHỐI 5: TRUYỀN THÔNG, GIAO THỨC, GIẢI THUẬT & WEB SCADA

### 33. Giao Thức MQTT 3.1.1 & Topic Tree Phân Cấp Namespace `Nhom09/smoke/...`
- **1. Bản chất nó là gì?**  
  Là giao thức truyền thông mạng tầng ứng dụng theo mô hình Xuất bản / Đăng ký (Publish/Subscribe), hoạt động trên nền tảng TCP/IP với kích thước tiêu đề gói tin (Header) cực nhẹ chỉ từ 2 bytes.
- **2. Chức năng trong đề tài:**  
  Đóng vai trò xương sống truyền tải dữ liệu cảm biến đo đạc từ ESP32 lên máy chủ Broker và chuyển tiếp lệnh điều khiển từ Web Dashboard xuống thiết bị.
- **3. Cấu trúc Topic Tree phân cấp:**  
  `Nhom09 / smoke / {service_domain} / [{action_or_target}]`  
  - `telemetry`: Gửi chu kỳ 2s dữ liệu khói, nhiệt, ẩm, FSM.  
  - `status`: Báo trạng thái Online/Offline (LWT).  
  - `cmd/fan`, `cmd/buzzer`: Kênh Downlink điều khiển thiết bị chấp hành.  
  - `history/sync`: Đồng bộ dữ liệu sự cố lưu trong bộ nhớ SPIFFS khi mạng hồi phục.
- **4. Tại sao cần Namespace `Nhom09/`?**  
  Trên Broker công cộng hoặc máy chủ trường dùng chung cho nhiều nhóm sinh viên, tiền tố `Nhom09/` cô lập không gian tên hoàn toàn, ngăn chặn việc nhóm khác vô tình hay cố ý gửi tin đè làm nhiễu hệ thống.

---

### 34. Cơ Chế Di Chúc LWT (Last Will and Testament) & Keep-Alive
- **1. Bản chất nó là gì?**  
  Là tính năng phát hiện đứt kết nối đột ngột tích hợp sẵn trong giao thức MQTT 3.1.1.
- **2. Chức năng trong đề tài:**  
  Tự động thông báo cho Web Dashboard và các dịch vụ biết trạm cảm biến P302 đã bị sập nguồn hoặc mất mạng Wi-Fi ngay cả khi ESP32 không kịp gửi tin từ biệt.
- **3. Nguyên lý hoạt động chi tiết:**  
  Khi ESP32 gửi gói tin kết nối `CONNECT` ban đầu lên Broker, nó đăng ký kèm một bản tin LWT:  
  - Topic: `Nhom09/smoke/status`  
  - Payload: `{"status": "offline", "reason": "unexpected_disconnect"}`  
  - Cờ Retain: `true`, QoS: `1`.  
  Nếu kết nối TCP bị đứt đột ngột (rút nguồn, mất Wi-Fi), sau khoảng thời gian $1.5 \\times \\text{KeepAlive} = 45\\text{s}$ không nhận được gói tin ping `PINGREQ`, Broker sẽ chủ động xuất bản tin LWT này cho toàn bộ Client đang subscribe.

---

### 35. Bộ Lọc Số Làm Mịn Dữ Liệu EMA (Exponential Moving Average, α = 0.2)
- **1. Bản chất nó là gì?**  
  Là bộ lọc thông thấp kỹ thuật số đệ quy (Digital Low-Pass Filter) gán trọng số suy giảm theo hàm mũ cho các giá trị đo trong quá khứ.
- **2. Chức năng trong đề tài:**  
  Triệt tiêu đỉnh gai nhiễu điện áp ngẫu nhiên của bộ đọc ADC trên ESP32, làm mịn đường cong nồng độ khói PPM mà không tốn mảng bộ nhớ RAM.
- **3. Công thức toán học đệ quy:**  
  $$S_t = \\alpha \\cdot X_t + (1 - \\alpha) \\cdot S_{t-1}$$
  Trong đó: $S_t$ là giá trị lọc mượt hiện tại; $S_{t-1}$ là giá trị lọc chu kỳ trước; $X_t$ là giá trị đo thô tức thời; $\\alpha = 0.2$ là hệ số làm mịn.
- **4. Tại sao chọn $\\alpha = 0.2$ mà không dùng trung bình cộng Moving Average?**  
  Moving Average 10 phần tử đòi hỏi phải cấp phát mảng 10 phần tử và dịch mảng liên tục, tốn RAM và chu kỳ xử lý của vi điều khiển. EMA chỉ cần duy trì đúng 1 biến trạng thái duy nhất $S_{t-1}$, tiết kiệm RAM 100% và phản hồi nhanh dưới 1 giây.

---

### 36. Máy Trạng Thái Hữu Hạn FSM 3 Cấp & Vùng Trễ Hysteresis
- **1. Bản chất nó là gì?**  
  Là mô hình biểu diễn thuật toán điều khiển tuần tự gồm một tập hữu hạn các trạng thái logic và các điều kiện chuyển trạng thái nghiêm ngặt.
- **2. Chức năng trong đề tài:**  
  Quyết định chính xác hành vi của còi hú, quạt hút và giao diện theo 3 cấp độ: `SAFE` (<300 PPM) -> `WARN` (300-400 PPM) -> `ALARM` (≥400 PPM).
- **3. Vùng đệm trễ Hysteresis (300 - 400 PPM):**  
  Ngưỡng kích hoạt báo động khói là ≥400 PPM, nhưng quạt chỉ được phép tắt khi nồng độ khói hạ hẳn xuống ≤300 PPM. Vùng đệm 100 PPM này triệt tiêu hiện tượng rơ-le nhảy loạn đóng ngắt liên tục (Relay Chattering) khi khói dao động quanh ngưỡng, bảo vệ tiếp điểm rơ-le không bị hồ quang điện thiêu cháy.

---

### 37. Cơ Chế Khóa An Toàn PCCC (Safety Interlock Override)
- **1. Bản chất nó là gì?**  
  Là cơ chế khóa an toàn cấp hệ thống (System-wide Safety Guard Clause) hiện thực đồng bộ trên cả Firmware ESP32 và Web Dashboard Backend.
- **2. Chức năng trong đề tài:**  
  Ngăn chặn lỗi vô ý hoặc thao tác phá hoại của con người làm tắt quạt hút khói khi hệ thống đang trong tình trạng báo cháy thực sự (ALARM).
- **3. Nguyên lý hoạt động:**  
  Khi nồng độ khói chạm ngưỡng ALARM (≥400 PPM), hệ thống tự động kích hoạt Khóa an toàn PCCC. Mọi lệnh Downlink yêu cầu tắt quạt (`FAN = OFF`) gửi từ Web/App đều bị TỪ CHỐI TUYỆT ĐỐI kèm mã lỗi `ERR_SAFETY_INTERLOCK_OVERRIDE`. Lệnh tắt còi chỉ có hiệu lực tạm thời tối đa 180s để phục vụ công tác cứu nạn; sau 180s nếu còn khói còi sẽ tự động hú lại.

---

### 38. Nền Tảng Web SCADA, Benchmark RTT & 16 Test Cases Tích Hợp (M4)
- **1. Bản chất nó là gì?**  
  Là tổ hợp kiến trúc công nghệ Full-Stack (Node.js, Express, WebSocket, Chart.js, Telegram Bot API) kết hợp hệ thống đo lường độ trễ thực nghiệm và ma trận kiểm thử E2E tự động.
- **2. Chức năng trong đề tài:**  
  Trực quan hóa dữ liệu đo đạc thời gian thực (<1s), điều khiển chấp hành 2 chiều, lưu trữ CSDL MySQL, cảnh báo Telegram tức thời (<1.2s), và chứng minh độ tin cậy qua 16 Test Cases tích hợp Milestone M4 Pass 100% với RTT khứ hồi đạt 115ms.
"""

    full_md_content = content_part1_and_glossary + "\n\n" + chapter_3_content

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_md_content)

    print(f"[HOÀN TẤT] Đã tạo file Markdown mới tại: {output_path} (Dung lượng: {len(full_md_content)} bytes)")

if __name__ == "__main__":
    out_file = r"e:\IoT\DoAn\docs\pdf\So_Tay_Thuyet_Trinh_Va_Hoi_Xoay_Dap_Xoay.md"
    create_markdown(out_file)
