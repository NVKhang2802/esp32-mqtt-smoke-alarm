# BÁO CÁO KỸ THUẬT GIẢI TRÌNH SỰ CỐ THỰC NGHIỆM & PHƯƠNG ÁN KHẮC PHỤC
## Hệ Thống Báo Khói Cảnh Báo Sớm — Nhóm N09 (Đề tài 4)
**Kính gửi:** ThS. Võ Hoàng Hải — Giảng viên hướng dẫn môn học IoT  
**Nhóm sinh viên thực hiện:**
- Nguyễn Vĩnh Khang (MSSV: 2001230381) – Nhóm trưởng
- Nguyễn Văn Đức (MSSV: 2001230186) – Thành viên
- Nguyễn Văn Mãnh (MSSV: 2001230503) – Thành viên

---

### TỔNG QUAN VẤN ĐỀ
Trong quá trình triển khai mô phỏng Tầng 1 (Milestone M1) trên nền tảng Wokwi và vi điều khiển ESP32, nhóm đã ghi nhận 3 hiện tượng kỹ thuật phát sinh trên Serial Monitor:
1. Lỗi không đọc được dữ liệu từ cảm biến nhiệt ẩm DHT22 (`[ERROR] Khong the doc du lieu tu DHT22!`).
2. Thông báo cảnh báo đỏ xuất hiện liên tục trong nhân ESP-IDF: `E (xxxx) ledc: ledc_set_duty: LEDC is not initialized`.
3. Hiện tượng nồng độ khói MQ-2 bị kẹp trần ở mức $\sim 305\text{ PPM}$ dù kéo thanh trượt mô phỏng lên cực đại $100.000\text{ PPM}$, và phải kéo thanh trượt về $< 1\text{ PPM}$ thì còi báo động mới giải trừ.

Báo cáo này phân tích chi tiết bản chất vật lý, cơ chế phần cứng và giải pháp công nghệ đã áp dụng để xử lý dứt điểm các vấn đề trên.

---

### 1. PHÂN TÍCH VÀ XỬ LÝ LỖI GIAO TIẾP 1-WIRE CỦA CẢM BIẾN DHT22

#### 1.1. Hiện tượng & Triệu chứng
Khi chạy chương trình, trên màn hình Serial Monitor xuất hiện dòng thông báo:
```text
[ERROR] Khong the doc du lieu tu DHT22!
```
Hàm đọc trả về giá trị `NAN` (Not-a-Number), khiến vi điều khiển không cập nhật được nhiệt độ và độ ẩm môi trường.

#### 1.2. Bản chất kỹ thuật & Nguyên nhân gốc rễ (Root Cause)
1. **Đặc tính định thời của giao thức 1-Wire:** Cảm biến DHT22 sử dụng cảm biến điện dung và cảm biến nhiệt điện trở NTC có hằng số thời gian đáp ứng nhiệt chậm. Nhà sản xuất yêu cầu chu kỳ lấy mẫu giữa 2 lần đọc liên tiếp tối thiểu là $2.0\text{ giây}$.
2. **Nghẽn bus giao tiếp:** Trong bản mã nguồn ban đầu sử dụng thư viện `DHTesp`, code gọi tuần tự `dht.getTemperature()` rồi ngay vài microsecond sau gọi tiếp `dht.getHumidity()`. Thao tác này vi phạm khoảng thời gian hồi phục của bus 1-Wire, khiến khung truyền thứ hai bị va chạm xung và trả về `NAN`.
3. **Trôi điện áp (Floating Pin):** Thư viện cũ không tự động cấu hình điện trở kéo lên nội (`INPUT_PULLUP`), trong khi sơ đồ Wokwi chưa gắn trở kéo ngoài 10kΩ, dẫn đến đường truyền tín hiệu GPIO4 bị thả nổi gây nhiễu bit checksum.

#### 1.3. Giải pháp kỹ thuật khắc phục triệt để
* **Chuyển đổi thư viện chuẩn:** Chuyển sang sử dụng thư viện **Adafruit DHT sensor library (`DHT.h`)** kết hợp **Adafruit Unified Sensor Driver**. Thư viện này được tối ưu hóa đặc thù cho kiến trúc ESP32.
* **Tự động cấu hình chân:** Hàm `dht.begin()` tự động thiết lập chế độ `INPUT_PULLUP` cho chân GPIO4, đảm bảo mức logic `HIGH` ổn định trên bus khi ở trạng thái nghỉ.
* **Cơ chế Cache 2s & Định thời Non-blocking 5s:** Firmware cài đặt chu kỳ đọc `cfg.intervalDHT = 5000ms` (5 giây) bằng hàm `millis()`. Thư viện Adafruit tích hợp cơ chế bộ nhớ đệm nội bộ: nếu gọi đọc nhiệt độ và độ ẩm cùng lúc, hàm chỉ phát 1 chuỗi Start Signal duy nhất để đọc trọn gói 40-bit dữ liệu, triệt tiêu 100% tình trạng nghẽn bus.

---

### 2. PHÂN TÍCH VÀ TRIỆT TIÊU CẢNH BÁO ĐỎ LEDC CỦA CÒI BUZZER

#### 2.1. Hiện tượng & Triệu chứng
Mỗi chu kỳ kiểm tra, nhân hệ điều hành thời gian thực FreeRTOS của ESP32 in ra dòng cảnh báo đỏ:
```text
E (12543) ledc: ledc_set_duty(725): LEDC is not initialized
```

#### 2.2. Bản chất kỹ thuật & Nguyên nhân
* Trên kiến trúc ESP32 của Espressif, hàm `tone(pin, freq)` sử dụng ngoại vi phần cứng **LEDC (LED Control PWM Timer)** để băm xung tần số kích màng rung còi Piezo.
* Trong vòng lặp `loop()`, nhánh điều kiện an toàn gọi liên tục hàm `noTone(PIN_BUZZER)` tại mỗi chu kỳ đọc khi còi chưa hề được bật. Khi gọi `noTone()` trên một kênh PWM chưa từng được hàm `tone()` cấp phát và khởi tạo thanh ghi duty cycle, driver LEDC của ESP-IDF phát hiện lỗi và in cảnh báo đỏ ra terminal.

#### 2.3. Giải pháp kỹ thuật khắc phục
Firmware xây dựng hàm điều khiển bọc an toàn `setBuzzer(bool state)` đi kèm biến trạng thái `bool isBuzzerActive`:
```cpp
void setBuzzer(bool state) {
  if (state) {
    if (!isBuzzerActive) {
      digitalWrite(PIN_BUZZER, HIGH);
      tone(PIN_BUZZER, 800);
      isBuzzerActive = true;
    }
  } else {
    if (isBuzzerActive) {
      noTone(PIN_BUZZER);
      digitalWrite(PIN_BUZZER, LOW);
      isBuzzerActive = false;
    } else {
      digitalWrite(PIN_BUZZER, LOW);
    }
  }
}
```
Nhờ cơ chế kiểm tra cờ này, lệnh `noTone()` chỉ được gọi duy nhất 1 lần khi còi đang kêu chuyển sang tắt. Cảnh báo lỗi đỏ được triệt tiêu hoàn toàn.

---

### 3. HIỆN TƯỢNG BÃO HÒA ADC VÀ CẢI TIẾN CÔNG THỨC MQ-2 TOÀN DẢI ĐO

#### 3.1. Hiện tượng & Triệu chứng
* Khi kéo thanh trượt nồng độ khói trên Wokwi từ $400\text{ PPM}$ lên đến cực đại $100.000\text{ PPM}$, chỉ số trên Serial Monitor không tăng mà dừng lại ở khoảng $305\text{ PPM}$.
* Khi nồng độ khói hạ xuống, dù thanh trượt đã ở mức $200\text{ PPM}$ (dưới ngưỡng 400), còi và quạt vẫn không tắt, phải kéo thanh trượt xuống sát $0\text{ PPM}$ ($< 1\text{ PPM}$) thì hệ thống mới trở về an toàn.

#### 3.2. Bản chất vật lý & Hiện tượng bão hòa ADC 12-bit (Clipping)
1. **Xung đột dải điện áp:** Chân ADC của ESP32 hoạt động trong dải điện áp $0.0\text{V} - 3.3\text{V}$ ứng với giá trị số 12-bit từ $0$ đến $4095$.
2. Khi cấp nguồn $5.0\text{V}$ cho module MQ-2, ở nồng độ $150\text{ PPM}$, điện áp ngõ ra $V_{AOUT}$ đã đạt $2.92\text{V}$ ($88.5\%$ thang đo ADC).
3. Khi nồng độ tăng vượt qua $\approx 270\text{ PPM}$, điện áp $V_{AOUT}$ vượt ngưỡng $3.3\text{V}$. Bộ ADC1 của ESP32 lập tức rơi vào trạng thái bão hòa kịch kim (Clipping ở mức 4095).
4. Do đó, dù nồng độ khói ngoài môi trường tăng lên $1.000$, $10.000$ hay $100.000\text{ PPM}$, điện áp đo được luôn bị kẹp cứng ở mức $3.3\text{V}$, khiến công thức tuyến tính cũ luôn tính ra kết quả tối đa là $\sim 305\text{ PPM}$. Ngược lại, muốn điện áp sụt xuống dưới $1.32\text{V}$ (để tính ra $< 400\text{ PPM}$ theo công thức cũ), người dùng bắt buộc phải kéo thanh trượt về sát $0\text{ PPM}$.

#### 3.3. Giải pháp công nghệ & Mô hình hóa hàm mũ Power-Law
1. **Chuẩn hóa nguồn điện mô phỏng:** Cấp nguồn $3.3\text{V}$ cho module MQ-2 từ chân `esp:3V3` trên Wokwi. Điện áp ngõ ra $V_{AOUT}$ dao động trọn vẹn trong dải $0.05\text{V} - 3.28\text{V}$, đồng bộ $100\%$ với dải đo của ESP32 mà không bị bão hòa sớm.
2. **Áp dụng mô hình toán học Power-Law:** Thay thế công thức đường thẳng bằng phương trình đặc tuyến bán dẫn oxit kim loại:
   $$\text{PPM} = A \times \left(\frac{R_s}{R_0}\right)^B$$
3. **Hiệu chuẩn thực nghiệm 2 điểm (Two-Point Empirical Calibration):** Nhóm đã thực hiện đo thực tế 2 mốc trên Wokwi Simulator:
   * Tại $200\text{ PPM}$: Đo được $Rs_1 = 1.7100\text{ k}\Omega$.
   * Tại $1000\text{ PPM}$: Đo được $Rs_2 = 0.8852\text{ k}\Omega$.
   * Tự động tính toán hệ số đặc tuyến $B = -2.444$ và $A = 741.6$, chuẩn hóa $R_0 = 10.0\text{ k}\Omega$.
4. **Kết quả thực nghiệm sau khắc phục:**
   * Tại $150 - 200\text{ PPM}$: Hiển thị chuẩn xác, còi và quạt tắt.
   * Kéo vượt $\ge 400\text{ PPM}$: Còi hú báo động, quạt bật tức thì, nút bấm bị khóa quyền.
   * Kéo lên $10.000 - 100.000\text{ PPM}$: Hệ thống đo được nồng độ khói cực đại hàng chục nghìn PPM mà không bị kẹp trần.
   * Kéo giảm về $\le 300\text{ PPM}$: Còi ngắt, quạt tắt an toàn, hoàn trả quyền cho nút bấm thủ công.

---

### KẾT LUẬN
Các biện pháp kỹ thuật được triển khai đã giải quyết triệt để cả 3 sự cố thực nghiệm, giúp firmware Tầng 1 vận hành ổn định, chính xác, đáp ứng đầy đủ các yêu cầu kỹ thuật khắt khe của môn học và sẵn sàng kết nối lên Tầng 2 (Wi-Fi & MQTT) trong các tuần tiếp theo.

