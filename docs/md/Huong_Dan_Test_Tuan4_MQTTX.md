# HƯỚNG DẪN CHI TIẾT KIỂM THỬ TUẦN 4: NETWORK & MQTT CONNECTIVITY

**Đề tài 04:** Hệ thống báo khói cảnh báo sớm
**Nhóm thực hiện:** Nhóm 09 (Lớp IoT IoT - GVHD: ThS. Võ Hoàng Hải)
**Milestone:** M2 – Connected Device (Nghiệm thu tiến độ Tuần 4 - Tỷ trọng 10%)

---

## I. MỤC TIÊU CẦN ĐẠT ĐƯỢC KHI TEST

1. Chứng minh **ESP32 (Wokwi)** kết nối thành công WiFi và MQTT Broker (`broker.emqx.io:1883`).
2. Chứng minh luồng **Uplink**: ESP32 gửi dữ liệu cảm biến định kỳ (`Nhom09/Nhom09/smoke/telemetry`) và cảnh báo khẩn cấp (`Nhom09/Nhom09/smoke/event/alarm`) lên MQTT Broker.
3. Chứng minh luồng **Downlink**: Dùng **MQTTX** gửi lệnh bật/tắt quạt (`Nhom09/Nhom09/smoke/cmd/fan`), còi (`Nhom09/Nhom09/smoke/cmd/buzzer`) xuống ESP32 và ESP32 thực thi thật.
4. Chứng minh **Ma trận an toàn PCCC (Safety Interlock)**: Khi khói nguy hiểm ($\ge$ 400 PPM), lệnh tắt quạt từ xa bị từ chối triệt để nhằm bảo vệ tính mạng con người.
5. **Chụp đủ 4 – 5 ảnh màn hình** sắc nét để dán vào báo cáo [Phần 4.docx](../word/Phần%204.docx) và [Bang_Test_Case_Tuan4_Nhom04.docx](../word/Bang_Test_Case_Tuan4_Nhom04.docx).

---

## II. CÔNG CỤ CẦN CHUẨN BỊ TRÊN MÁY TÍNH

1. **Môi trường chạy mô phỏng ESP32:**
   - Cách 1 (Khuyên dùng): Mở dự án trên **VS Code** với extension **Wokwi Simulator**, mở file `diagram.json` và bấm nút **Start Simulation**.
   - Cách 2: Mở trình duyệt vào [wokwi.com](https://wokwi.com), chọn ESP32 và copy toàn bộ code trong file `src/main.cpp` vào tab `sketch.ino`.
2. **Công cụ MQTT Client:**
   - Cách 1: Tải phần mềm **MQTTX Desktop** tại [https://mqttx.app/](https://mqttx.app/) (Khuyên dùng).
   - Cách 2: Dùng trực tiếp trên web tại [https://mqttx.app/web](https://mqttx.app/web) (Không cần cài đặt).

---

## III. THIẾT LẬP KẾT NỐI TRÊN MQTTX (CHỈ LÀM 1 LẦN)

> 💡 **Khuyên dùng Import 1-Click Bộ Kịch Bản:**
> Trên MQTTX, vào menu **File -> Import Data** (hoặc biểu tượng Import), chọn tệp `tests/mqttx_collection_slide65.json` trong thư mục dự án. Hệ thống sẽ tự động cấu hình sẵn toàn bộ kết nối, 11 kênh Subscribe và 15 lệnh mẫu (Slide 65 & V1) mà không cần nhập tay!

**Nếu muốn tạo kết nối thủ công:**
1. Mở MQTTX, bấm nút **+** hoặc **New Connection**.
2. Điền chính xác các thông số sau:
   - **Name:** `ESP32 Smoke Test Nhom 04`
   - **Host:** `broker.emqx.io`
   - **Port:** `1883` _(Nếu dùng MQTTX Web thì chọn protocol `ws://` và port `8083`)_
   - **Client ID:** Bấm nút xúc xắc (random) bên cạnh để tự sinh ID ngẫu nhiên.
   - **Username & Password:** 👉 **ĐỂ TRỐNG HOÀN TOÀN** (Không nhập gì cả).
3. Bấm **Connect** ở góc trên bên phải. Khi hiện chữ **Connected** màu xanh lá cây là kết nối thành công.
4. Bấm **+ New Subscription**:
   - **Topic:** `Nhom09/smoke/#` _(dấu `#` để nhận tất cả các topic của hệ thống Nhóm 09)_
   - **QoS:** `0` (hoặc `1`)
   - Bấm **Confirm**.

---

## IV. QUY TRÌNH 5 BƯỚC TEST & CHỤP ẢNH MINH CHỨNG (EVIDENCE)

> 💡 **Mẹo bố trí màn hình để chụp ảnh đẹp:**
> Chia đôi màn hình máy tính: Nửa bên trái để cửa sổ **VS Code (Wokwi Terminal + Sơ đồ mạch)**, nửa bên phải để cửa sổ **MQTTX**.

```
+------------------------------------------+------------------------------------------+
|          NỬA TRÁI: WOKWI SIMULATOR       |             NỬA PHẢI: MQTTX              |
|  - Sơ đồ cảm biến MQ2, LED Quạt, Buzzer  |  - Danh sách bản tin nhận (Uplink)       |
|  - Terminal hiển thị log thẳng hàng      |  - Khung Publish lệnh gửi xuống          |
+------------------------------------------+------------------------------------------+
```

---

### 📸 ẢNH 1: Khởi động hệ thống & Uplink Telemetry định kỳ

- **Mục đích:** Chứng minh thiết bị lên mạng thành công và tự động bắn dữ liệu môi trường.
- **Cách thực hiện:**
  1. Trên Wokwi, bấm nút **Start Simulation** (tam giác xanh).
  2. Để cảm biến MQ2 ở mức bình thường (< 300 PPM, ví dụ 150 - 280 PPM).
  3. Quan sát:
     - **Terminal Wokwi** in dòng kết nối WiFi, kết nối Broker thành công và dòng telemetry định kỳ mỗi 2 giây:
       ```text
       [WIFI] Ket noi WiFi thanh cong! IP: 10.0.0.15
       [MQTT] >>> KET NOI BROKER THANH CONG! <<<
       [#0005 | T= 10s] PPM: 185.4 | Nhiet: 28.5*C | Am: 65.0% | Quat: TAT | Coi: TAT | Mode: AUTO
         [MQTT UPLINK] -> Nhom09/smoke/telemetry (QoS 0) [OK]
       ```
     - **MQTTX** tự động nhận được các khối tin JSON trên topic `Nhom09/smoke/telemetry` mỗi 2 giây.
- 📸 **Hành động:** Chụp ảnh cả 2 màn hình (Wokwi Terminal + MQTTX có các gói tin `Nhom09/smoke/telemetry`).

---

### 📸 ẢNH 2: Điều khiển Bật / Tắt Quạt hút từ xa qua MQTTX (Downlink)

- **Mục đích:** Chứng minh điều khiển thiết bị chấp hành từ xa hai chiều khi môi trường an toàn.
- **Cách thực hiện:**
  1. Tại khung **Publish** phía dưới của MQTTX, điền:
     - **Topic:** `Nhom09/smoke/cmd/fan`
     - **Payload:**
       ```json
       { "action": "ON" }
       ```
     - Bấm nút gửi (mũi tên xanh).
  2. Quan sát:
     - Đèn LED màu xanh (FAN) trên mạch Wokwi **sáng lên**.
     - Terminal Wokwi hiện khung xác nhận:
       ```text
       ====================== [DOWNLINK COMMAND] ======================
       Topic   : Nhom09/smoke/cmd/fan
       Payload : {"action": "ON"}
       Ket qua : CHAP NHAN -> BAT QUAT (Chuyen sang MODE_MANUAL)
       ================================================================
       ```
     - MQTTX nhận phản hồi xác nhận trên topic `Nhom09/smoke/status` (`"result": "ACCEPTED"`).
  3. Gửi tiếp lệnh tắt quạt để kiểm tra:
     - **Payload:** `{"action": "OFF"}`
     - Đèn LED FAN trên Wokwi **tắt đi**.
- 📸 **Hành động:** Chụp ảnh màn hình lúc gửi lệnh `{"action": "ON"}` và đèn LED Fan đang sáng.

---

### 📸 ẢNH 3: Báo động khẩn cấp khi nồng độ khói vượt ngưỡng (Alarm Uplink)

- **Mục đích:** Chứng minh cơ chế ngắt tức thì phát hiện khói nguy hiểm ($PPM \ge 400$).
- **Cách thực hiện:**
  1. Trên sơ đồ Wokwi, bấm chuột vào cảm biến khói **MQ2**.
  2. Kéo thanh trượt nồng độ khói tăng vọt lên **$\ge$ 400 PPM** (ví dụ kéo lên 500 – 600 PPM).
  3. Quan sát phản ứng ngay lập tức (< 100ms):
     - Còi **Buzzer hú inh ỏi**, đèn **Relay Quạt tự động bật sáng cưỡng bức**.
     - Terminal Wokwi in dòng cảnh báo:
       ```text
       >>> [CANH BAO PCCC] PPM >= 400.0 -> COI & QUAT BAT CUONG BUC! <<<
         [MQTT EVENT] -> Nhom09/smoke/event/alarm (CRITICAL ALARM) [SENT]
       ```
     - Cửa sổ MQTTX lập tức nhảy ra gói tin khẩn cấp trên topic `Nhom09/smoke/event/alarm`:
       ```json
       {
         "device_id": "ESP32_Smoke_Nhom04",
         "event": "SMOKE_ALERT",
         "severity": "CRITICAL",
         "ppm": 520.8,
         "threshold": 400.0,
         "msg": "CANH BAO: Khoi vuot nguong! Coi va Quat da bat!"
       }
       ```
- 📸 **Hành động:** Chụp ảnh màn hình Wokwi (MQ2 đang ở mức cao, quạt sáng) và MQTTX nhận gói tin `Nhom09/smoke/event/alarm` màu đỏ nổi bật.

---

### 📸 ẢNH 4: Ma trận an toàn PCCC (Local Safety Interlock - Điểm cộng cao nhất!)

- **Mục đích:** Chứng minh tính an toàn hệ thống: Từ chối lệnh tắt quạt từ xa khi khói đang nguy hiểm.
- **Cách thực hiện:**
  1. **Vẫn giữ nồng độ khói MQ2 trên Wokwi ở mức cao** ($\ge$ 400 PPM).
  2. Trên MQTTX, cố tình gửi lệnh **TẮT QUẠT**:
     - **Topic:** `Nhom09/smoke/cmd/fan`
     - **Payload:** `{"action": "OFF"}`
     - Bấm gửi.
  3. Quan sát kết quả:
     - Quạt trên Wokwi **KHÔNG HỀ BỊ TẮT** (vẫn tiếp tục quay để cứu người).
     - Terminal Wokwi in cảnh báo từ chối lệnh rõ ràng:
       ```text
       ====================== [DOWNLINK COMMAND] ======================
       Topic   : Nhom09/smoke/cmd/fan
       Payload : {"action": "OFF"}
       Ket qua : TU CHOI! [PCCC Interlock] Khoi dang nguy hiem (520.8 >= 400.0)!
       Hanh vi : Duy tri QUAT BAT cuong buc de bao ve tinh mang!
       ================================================================
       ```
     - MQTTX nhận bản tin từ chối trên `Nhom09/smoke/status`:
       `"result": "REJECTED_SAFETY_LOCK"`.
- 📸 **Hành động:** Chụp lại Terminal Wokwi lúc hiện dòng `TU CHOI! [PCCC Interlock]` và MQTTX nhận kết quả `REJECTED_SAFETY_LOCK`.

---

### 📸 ẢNH 5 (Tùy chọn): Mute còi hú & Khôi phục về ngưỡng an toàn

1. Trong lúc khói cao, gửi lệnh Mute còi:
   - **Topic:** `Nhom09/smoke/cmd/buzzer`
   - **Payload:** `{"action": "MUTE"}`
   - Còi Buzzer im lặng trong 180s, quạt vẫn chạy.
2. Kéo thanh trượt MQ2 về lại mức thấp (< 300 PPM):
   - Hệ thống tự động tắt còi, trả quạt về chế độ ban đầu và phát thông điệp `SMOKE_SAFE` lên MQTTX.

---

## V. CÂU HỎI VẤN ĐÁP GIẢNG VIÊN CÓ THỂ HỎI & CÁCH TRẢ LỜI

| Câu hỏi của Thầy/Cô                                                                      | Câu trả lời chuẩn xác                                                                                                                                                                                                                                                                                                            |
| ---------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1. Tại sao nhóm dùng giao thức MQTT thay vì HTTP REST API?**                           | Dạ thưa Thầy, MQTT hoạt động theo mô hình Pub/Sub trên nền TCP với gói tin cực kỳ nhẹ (header chỉ từ 2 bytes), tiết kiệm năng lượng và băng thông cho vi điều khiển ESP32. Đặc biệt, MQTT cho phép nhận lệnh từ xa tức thì (bất đồng bộ) qua cơ chế Subscribe mà không cần ESP32 phải liên tục gửi Request hỏi vòng như HTTP.    |
| **2. Last Will and Testament (LWT) trong bài nhóm dùng để làm gì?**                      | Dạ LWT là tính năng của MQTT cho phép ESP32 đăng ký trước một thông điệp "chúc thư" (`Nhom09/smoke/lwt` payload `"offline"`). Khi ESP32 mất nguồn hoặc đứt WiFi đột ngột, Broker sẽ tự động phát thông điệp này đến App/Dashboard để người dùng biết trạm báo khói đã bị mất kết nối, kịp thời sửa chữa.                                |
| **3. Nếu mất kết nối WiFi/MQTT thì ESP32 có bị treo không?**                             | Dạ không thưa Thầy. Nhóm thiết kế giải thuật**Non-blocking Reconnect dùng `millis()`** với chu kỳ thử lại 5 giây một lần. Tuyệt đối không dùng `delay()` hay vòng lặp `while(!client.connected())`, nên cảm biến khói và còi hú PCCC tại chỗ vẫn hoạt động liên tục thời gian thực và không bao giờ bị kích hoạt Watchdog Reset. |
| **4. Nếu khói đang cao mà người dùng bấm tắt quạt trên App thì hệ thống xử lý thế nào?** | Dạ hệ thống áp dụng**Ma trận phân xử an toàn (Safety Interlock)**. Khi $PPM \ge 400$, luật bảo vệ tính mạng tại biên chiếm quyền tối cao, ESP32 sẽ **từ chối triệt để** mọi lệnh tắt quạt và gửi thông báo lỗi ngược lại cho App. Chỉ khi khói giảm về dưới 300 PPM thì người dùng mới được quyền tắt quạt thủ công.             |

---

## VI. BẢNG CHECKLIST NỘP BÀI TUẦN 4

- [ ] Chạy mô phỏng Wokwi không có lỗi biên dịch.
- [ ] Chạy MQTTX kết nối thành công đến `broker.emqx.io:1883`.
- [ ] Chụp đủ 4 ảnh: Telemetry, Lệnh bật quạt, Báo động khói khẩn cấp, Bị chặn tắt quạt do Safety Interlock.
- [ ] Mở tệp [Bang_Test_Case_Tuan4_Nhom04.docx](../word/Bang_Test_Case_Tuan4_Nhom04.docx) kiểm tra lại 12 test case.
- [ ] Nộp kèm link Wokwi public cho giảng viên.

