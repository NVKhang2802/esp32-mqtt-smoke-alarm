# HƯỚNG DẪN KHỞI ĐỘNG, CẤU HÌNH & KỊCH BẢN DEMO BẢO VỆ ĐỒ ÁN IoT

## ĐỀ TÀI 04: HỆ THỐNG BÁO KHÓI CẢNH BÁO SỚM

**Đơn vị:** Khoa Công nghệ Thông tin — Trường Đại học Công Thương TP.HCM (HUIT)
**Giảng viên hướng dẫn:** ThS. Võ Hoàng Hải
**Nhóm thực hiện:** Nhóm 09 (Mã phân bổ hệ thống: `N09` / `Nhom09`)
**Thành viên:** Nguyễn Vĩnh Khang (Trưởng nhóm), Nguyễn Văn Đức, Nguyễn Văn Mãnh

---

## 📌 MỤC TIÊU CỦA TÀI LIỆU NÀY

Tài liệu này được biên soạn nhằm giúp bạn:

1. **Khởi động trơn tru toàn bộ 4 nền tảng** của dự án (Wokwi ESP32, Node-RED, Web SCADA, và MQTTX Desktop) chỉ trong **2 phút** trước khi bước vào phòng bảo vệ.
2. **Nạp 1-click toàn bộ kịch bản kiểm thử mẫu** vào ứng dụng **MQTTX Desktop** trên máy tính mà không cần phải gõ tay bất kỳ đoạn mã JSON nào trước mặt Giảng viên.
3. **Thuyết trình & Demo chuẩn xác theo từng phút (10 – 12 phút)** với lời thoại mẫu, chỉ rõ thao tác chuột/bàn phím tương ứng.
4. **Nắm vững "Bộ phao cứu sinh Q&A"** để tự tin trả lời xuất sắc mọi câu hỏi phản biện chuyên sâu từ Thầy Cô.

---

# CHƯƠNG 1: BỐ CỤC MÀN HÌNH & HƯỚNG DẪN KHỞI ĐỘNG TỪNG BƯỚC

## 1.1. Chuẩn bị Bố cục Màn hình (Screen Layout 4 Cửa Sổ)

Để Giảng viên quan sát rõ ràng **tính đồng bộ thời gian thực** giữa các tầng, hãy sắp xếp màn hình theo dạng lưới:

```
┌─────────────────────────────────┬─────────────────────────────────┐
│ CỬA SỔ 1 (Góc trên - Trái):      │ CỬA SỔ 2 (Góc trên - Phải):     │
│ WOKWI SIMULATOR (Tầng 1)        │ NODE-RED FLOWS & DEBUG (Tầng 3) │
│ - Mạch ESP32, MQ-2, DHT22       │ - http://localhost:1880         │
│ - Serial Monitor in nhật ký loop│ - Mở sẵn tab Debug bên phải     │
├─────────────────────────────────┼─────────────────────────────────┤
│ CỬA SỔ 3 (Góc dưới - Trái):      │ CỬA SỔ 4 (Góc dưới - Phải):     │
│ MQTTX DESKTOP (Tầng 2)          │ WEB SCADA DASHBOARD (Tầng 4)    │
│ - Ứng dụng Desktop trên máy     │ - http://localhost:8085         │
│ - Nạp sẵn Collection bản tin    │ - Đồng hồ kim, FSM, Quạt/Còi    │
└─────────────────────────────────┴─────────────────────────────────┘
```

---

## 1.2. Khởi động Tầng 4: Web SCADA Server (Port 8085)

Mở một cửa sổ PowerShell hoặc Terminal tại thư mục gốc dự án (`E:\IoT\DoAn`), gõ lệnh:

```powershell
python -m http.server 8085 --directory web
```

* **Kiểm tra thành công:** Mở trình duyệt Chrome truy cập `http://localhost:8085`.
* **Dấu hiệu sẵn sàng:** Góc trên bên phải hiển thị badge xanh lá: `EMQX Online (WSS)`. Đồng hồ kim hiển thị nồng độ khói, FSM Chip hiện `AN TOÀN (SAFE)`.

---

## 1.3. Khởi động Tầng 3: Node-RED Middleware (Port 1880)

Mở cửa sổ PowerShell/Terminal thứ 2 tại thư mục dự án, chạy lệnh:

```powershell
node-red nodered/flows_smoke_detector.json
```

*(Hoặc nếu bạn dùng thư mục runtime riêng: `node-red --userDir .nodered_runtime nodered/flows_smoke_detector.json`)*

* **Kiểm tra thành công:** Truy cập `http://localhost:1880`.
* **Dấu hiệu sẵn sàng:**
  1. Luồng 52 nodes hiển thị đầy đủ các nhánh: *Auth Service, Deduplication Parsers, Core Engine (5 Rules), Scheduler 1m, Watchdog 3s*.
  2. Các node `mqtt in` và `mqtt out` đều có chấm tròn xanh lá kèm chữ `connected`.
  3. Bấm vào biểu tượng con bọ **Debug messages** (góc trên bên phải) để xem các gói tin JSON đang lưu thông.
  4. Mở tab phụ truy cập `http://localhost:1880/ui` để xem Node-RED Dashboard.

---

## 1.4. Khởi động Tầng 1: Wokwi Simulator (ESP32 Firmware)

Bạn có thể chạy mô phỏng theo 2 cách cực kỳ tiện lợi:

### Cách 1: Chạy trực tiếp trong VS Code / Antigravity IDE (Khuyên dùng)

1. Trong cửa sổ soạn thảo, mở file [diagram.json](../../diagram.json).
2. Nhấn tổ hợp phím `F1` (hoặc `Ctrl + Shift + P`).
3. Gõ tìm kiếm: `Wokwi: Start Simulator` rồi nhấn Enter.
4. Mạch ESP32 sẽ lập tức khởi chạy, cấp nguồn cho cảm biến MQ-2, DHT22 và nạp file nhị phân firmware `.pio/build/esp32dev/firmware.bin`.
5. Quan sát cửa sổ Terminal / Serial Monitor bên dưới:
   ```text
   [WIFI] Connected to Wokwi-GUEST | IP: 10.0.1.x
   [MQTT] Connected to broker.emqx.io:1883
   [FSM] State initialized: SAFE | Baseline: 200 PPM
   ```

### Cách 2: Mở Wokwi trên trình duyệt Web (Dự phòng)

Nếu máy tính bị giật lag, bạn có thể mở đường link Wokwi Web của dự án trên trình duyệt Chrome và bấm nút **Play (Tam giác màu xanh)**.

---

## 1.5. Cấu hình & Nạp Kịch Bản 1-Click Vào MQTTX Desktop (Tầng 2)

Ứng dụng **MQTTX Desktop** trên máy bạn là công cụ đắc lực nhất để gây ấn tượng với Giảng viên về tính chuyên nghiệp!

### Bước 1: Mở MQTTX Desktop & Thiết lập Kết nối

1. Khởi động phần mềm **MQTTX** từ Desktop / Start Menu.
2. Nhấn nút **New Connection** (hoặc chọn kết nối có sẵn như trong hình của bạn):
   - **Name:** `ESP32 Smoke Test Nhóm 09`
   - **Client ID:** `MQTTX_Tester_Nhom09` (hoặc nhấn nút xoay vòng tạo ID ngẫu nhiên)
   - **Host:** `broker.emqx.io`
   - **Port:** `1883` (giao thức `mqtt://`)
   - **Keep Alive:** `60` giây
   - **Clean Start:** Tích chọn `true`
3. Nhấn nút **Connect** (Màu xanh lá ở góc trên phải) $\rightarrow$ Trạng thái chuyển sang `Connected`.

### Bước 2: Đăng ký Nhận Tin (Subscribe)

Nhấn nút **+ New Subscription**:

- **Topic:** `Nhom09/smoke/#`
- **QoS:** `0`
- **Color:** Chọn màu cam hoặc đỏ để dễ nhìn.
- Nhấn **Confirm**. Giờ đây, mọi gói tin Telemetry của Wokwi và lệnh điều khiển của Web SCADA/Node-RED đều sẽ xuất hiện trên màn hình MQTTX!

### Bước 3: Nạp 1-Click Bộ Kịch Bản Mẫu (Import Collection)

Bạn không cần phải tự gõ từng lệnh JSON trước mặt Thầy:

1. Trên thanh menu trên cùng của MQTTX, chọn **File** $\rightarrow$ **Import Data** (hoặc biểu tượng hộp công cụ `</>` bên thanh điều hướng trái).
2. Chọn đường dẫn tới file:
   📁 **`E:\IoT\DoAn\tests\mqttx_scenario_collection.json`**
3. Nhấn **Open / Import**.
4. Toàn bộ **23 kịch bản kiểm thử mẫu** (bật/tắt quạt, tắt còi tạm, đổi ngưỡng ngày/đêm, bơm sự cố MQ-2) sẽ nằm gọn trong danh sách gửi của bạn!

---

# CHƯƠNG 2: HƯỚNG DẪN ĐĂNG NHẬP & PHÂN QUYỀN TRÊN WEB SCADA

Trên giao diện Web SCADA (`http://localhost:8085`), tìm góc trên bên phải thanh điều hướng có mục **Vai trò người dùng**:

```
[ Người dùng: ▼ Quản trị viên (Admin) ]   [ MQTT: ● EMQX Online ]
```

### 1. Vai trò Cư dân (`Cư dân (Viewer)`):

- **Mục đích demo:** Chứng minh hệ thống có cơ chế phân quyền bảo mật **RBAC (Role-Based Access Control)**.
- **Hành vi:** Cư dân chỉ được xem chỉ số môi trường (nồng độ khói, nhiệt độ, độ ẩm) và theo dõi sơ đồ thoát hiểm.
- **Thử nghiệm:** Khi đang ở role `Viewer`, nếu click vào nút **"Bật Quạt"** $\rightarrow$ Giao diện lập tức hiện Toast cảnh báo màu vàng: *"Bạn không có quyền thực hiện thao tác này (Chỉ xem)"*, lệnh không bị đẩy xuống broker.

### 2. Vai trò Quản trị viên (`Quản trị viên (Admin)`):

- **Hành vi:** Mở khóa toàn quyền điều khiển thủ công các thiết bị chấp hành (Quạt hút, Còi hú, chuyển đổi độ nhạy Ngày/Đêm, xác nhận sự cố).
- **Nhật ký:** Mọi lần chuyển đổi vai trò đều được ghi lại vào bảng **Nhật ký kiểm toán (Audit Trail)** ở cuối trang.

---

# CHƯƠNG 3: KỊCH BẢN THUYẾT MINH & DEMO 10–12 PHÚT (STEP-BY-STEP)

Dưới đây là kịch bản chuẩn được phân chia từng phút, có sẵn **lời thoại thuyết minh** và **hành động tương ứng**:

```mermaid
timeline
    title KỊCH BẢN DEMO ĐỒ ÁN IOT (TỔNG THỜI GIAN: 11 PHÚT)
    00:00 - 02:00 : Giới thiệu Kiến trúc 4 tầng & Luồng Baseline 200 PPM
    02:00 - 04:00 : Phân quyền RBAC & Điều khiển hai chiều Closed-Loop ACK
    04:00 - 07:00 : BÁO ĐỘNG CHÁY & KIỂM CHỨNG KHÓA AN TOÀN PCCC (ĐIỂM NHẤN)
    07:00 - 09:00 : Hạ khói Cooldown 30s & Chu trình xả khói Purge
    09:00 - 11:00 : Giả lập sự cố đứt cáp cảm biến & Watchdog Offline
```

---

### 🎬 PHÂN ĐOẠN 1 (0:00 – 2:00): GIỚI THIỆU TỔNG QUAN & DỮ LIỆU ĐỒNG BỘ

* **Hành động trên màn hình:** Chỉ tay vào 4 cửa sổ đang mở song song (Wokwi, MQTTX, Node-RED, Web SCADA).
* **Lời thoại thuyết minh:**
  > *"Kính thưa Thầy Võ Hoàng Hải và Hội đồng Giảng viên, nhóm chúng em xin phép trình diễn demo vận hành thực tế Hệ thống Báo khói Cảnh báo sớm. Hệ thống được xây dựng chuẩn theo Kiến trúc 4 tầng IoT:
  >
  > - **Tầng 1:** Thiết bị biên vi điều khiển ESP32 chạy trên Wokwi, kết nối cảm biến khói MQ-2, nhiệt ẩm DHT22, rơ-le quạt và còi PWM.
  > - **Tầng 2:** Kênh truyền thông MQTT bảo mật trên EMQX Cloud với tiền tố định danh riêng `Nhom09/smoke/...`, đang được giám sát bởi trạm kiểm soát MQTTX Desktop.
  > - **Tầng 3:** Middleware trung tâm Node-RED gồm 52 nodes xử lý 5 Business Rules PCCC và tự động hóa liên vùng.
  > - **Tầng 4:** Ứng dụng điều hành Web SCADA trực quan dành cho ban quản lý tòa nhà.
  >   Hiện tại, ở điều kiện không khí sạch bình thường, cảm biến MQ-2 đo được 200 PPM. Thầy có thể thấy cả 4 màn hình đều nhận đúng 200.0 PPM, nhiệt độ 28°C, độ ẩm 60% và máy trạng thái FSM đều đồng nhất ở trạng thái SAFE."*
  >

---

### 🎬 PHÂN ĐOẠN 2 (2:00 – 4:00): PHÂN QUYỀN RBAC & ĐIỀU KHIỂN HAI CHIỀU CLOSED-LOOP

* **Hành động trên màn hình:**
  1. Trên Web SCADA: Chuyển dropdown vai trò sang `Cư dân (Viewer)`.
  2. Bấm thử nút **"Bật quạt"** $\rightarrow$ Thấy thông báo từ chối.
  3. Chuyển lại vai trò `Quản trị viên (Admin)`.
  4. Bấm nút **"Bật quạt" (Fan ON)**.
  5. Chỉ vào cửa sổ Wokwi: Rơ-le đóng `tách`, đèn LED xanh lá (FAN) bật sáng.
  6. Chỉ vào cửa sổ MQTTX: Gói tin lệnh `{"action":"ON"}` gửi đi và nhận lại ACK xác nhận.
  7. Chỉ vào Web SCADA: Badge quạt chuyển sang `ĐANG CHẠY`.
* **Lời thoại thuyết minh:**
  > *"Để đảm bảo an toàn vận hành, hệ thống tích hợp phân quyền RBAC. Khi ở vai trò Cư dân, nút điều khiển bị chặn hoàn toàn. Khi chuyển sang Quản trị viên, em thực hiện bật quạt thông gió. Điểm đặc biệt của nhóm là cơ chế điều khiển khép kín Closed-Loop ACK: Web không tự vẽ trạng thái ảo, mà chỉ đổi màu sang 'ĐANG CHẠY' sau khi rơ-le trên mạch phần cứng Wokwi thực sự đã đóng và gửi gói tin xác nhận ngược trở lại."*
  >

---

### 🎬 PHÂN ĐOẠN 3 (4:00 – 7:00): BÁO ĐỘNG CHÁY & KIỂM CHỨNG KHÓA AN TOÀN PCCC (ĐIỂM NHẤN CAO NHẤT)

* **Hành động trên màn hình:**
  1. Trên Wokwi: Nhấp vào cảm biến MQ-2, kéo thanh trượt từ 200 PPM lên **550 PPM** (hoặc trên Web SCADA mở modal Test Bench bấm nút *"Báo động Khẩn (550 PPM)"*).
  2. **Quan sát phản ứng đồng loạt:**
     - **Wokwi:** FSM chuyển sang `STATE_ALARM`. Còi hú liên tục, quạt bật hết công suất.
     - **Node-RED:** Kích hoạt Rule 1 (Cháy thật) và **Rule 5 (Sơ tán khẩn cấp liên vùng toàn tầng F03)**: tự động gửi lệnh hú còi tới topic các phòng lân cận `Nhom09/smoke/v2/HUIT_A/F03/+/cmd/buzzer`.
     - **Web SCADA:** Nhấp nháy banner đỏ rực: *"BÁO ĐỘNG HỎA HOẠN: KHÓI VƯỢT NGƯỠNG NGUY CẤP!"*, còi trên web phát chuông báo cháy.
  3. **THỰC HIỆN BƯỚC PHÁ HOẠI THỬ NGHIỆM ĐỂ LẤY ĐIỂM TUYỆT ĐỐI:**
     - Thử dùng chuột bấm nút **"Tắt quạt"** (`#btnFanOff`) trên Web SCADA $\rightarrow$ Nút bị khóa cứng (`disabled = true`), con trỏ chuột hiện dấu cấm!
     - Mở cửa sổ **MQTTX Desktop**, chọn lệnh publish tắt quạt:`Topic: Nhom09/smoke/cmd/fan` | `Payload: {"action":"OFF"}`Bấm **Send** để cố tình tắt quạt từ xa!
     - Nhìn vào Serial Monitor Wokwi: Firmware in ra dòng cảnh báo đỏ:
       ```text
       [SAFETY LOCK] Refused remote Fan OFF during ALARM! Safety Interlock engaged.
       ```
     - Đèn quạt Wokwi vẫn tiếp tục sáng, quạt vẫn quay, firmware gửi trả về mã `ACK_SAFETY_LOCK`.
* **Lời thoại thuyết minh:**
  > *"Khi nồng độ khói vọt lên 550 PPM, hệ thống kích hoạt chế độ báo động khẩn cấp. Tại tầng Node-RED, Rule 5 lập tức phát lệnh sơ tán các phòng lân cận cùng tầng F03.
  > Và đây là tính năng cốt lõi ăn điểm của đồ án: **Khóa An Toàn PCCC (Safety Interlock)**. Theo tiêu chuẩn PCCC, trong cơn hỏa hoạn, tuyệt đối không ai được phép tắt quạt hút khói cứu nạn. Trên giao diện Web, nút Tắt quạt đã bị khóa hoàn toàn. Thậm chí nếu một kẻ xấu dùng phần mềm MQTTX cố tình gửi gói tin ép tắt quạt qua mạng, lõi firmware C++ của ESP32 sẽ lập tức từ chối và bảo vệ tính mạng con người."*
  >

---

### 🎬 PHÂN ĐOẠN 4 (7:00 – 9:00): HẠ KHÓI, CHU TRÌNH COOLDOWN 30S & TỰ PHỤC HỒI

* **Hành động trên màn hình:**
  1. Trên Wokwi: Kéo thanh trượt MQ-2 từ 550 PPM hạ xuống **270 PPM** (dưới ngưỡng an toàn).
  2. Quan sát Web SCADA: FSM chip đổi sang màu xanh dương **`ĐANG XẢ KHÓI (COOLDOWN)`**.
  3. Chỉ vào đồng hồ đếm ngược 30 giây: Quạt vẫn tiếp tục quay để hút sạch lượng khói độc còn sót lại.
  4. Sau khi hết 30 giây: FSM tự động trở về `AN TOÀN (SAFE)`, còi tắt hẳn, quạt tự động dừng.
* **Lời thoại thuyết minh:**
  > *"Khi khói đã giảm về mức 270 PPM, hệ thống không tắt quạt ngay lập tức mà kích hoạt chu trình Cooldown 30 giây (Post-Purge Cycle). Chu trình này vừa giúp hút sạch lượng khói độc tồn đọng trong phòng, vừa giải quyết triệt để hiện tượng trễ Hysteresis, ngăn ngừa rơ-le bị bật tắt liên tục làm cháy tiếp điểm cơ khí."*
  >

---

### 🎬 PHÂN ĐOẠN 5 (9:00 – 11:00): GIẢ LẬP SỰ CỐ CẢM BIẾN & MẤT KẾT NỐI (WATCHDOG)

* **Hành động trên màn hình:**
  1. Mở **MQTTX Desktop**, bấm nút gửi lệnh kịch bản `MQ2_DISCONNECT` (hoặc gửi topic `Nhom09/smoke/cmd/inject_fault` với `{"type":"MQ2_DISCONNECT"}`).
  2. Quan sát: Cảm biến MQ-2 báo lỗi `mq2_valid: false`, FSM chuyển sang màu vàng `LỖI CẢM BIẾN (FAULT)`. Còi Wokwi chuyển sang tiếng bíp ngắt quãng (Fault Beep). Web SCADA hiện thẻ cảnh báo phần cứng. Node-RED nhận biết sự cố nên không báo cháy giả.
  3. Mở MQTTX gửi `{"type":"CLEAR"}` $\rightarrow$ Cảm biến phục hồi về bình thường.
  4. Thử ngắt kết nối Wokwi hoặc rút mạng mô phỏng trong 15 giây $\rightarrow$ Quá thời gian nhịp tim Heartbeat, Web SCADA chuyển sang màu xám `MẤT KẾT NỐI (OFFLINE)` nhờ cơ chế Watchdog LWT.
* **Lời thoại thuyết minh:**
  > *"Hệ thống được thiết kế chống chọi lỗi toàn diện. Khi cảm biến bị đứt dây hoặc chập tín hiệu, FSM lập tức chuyển sang chế độ FAULT, cảnh báo cho đội kỹ thuật bảo trì mà không gây hoảng loạn báo cháy giả cho cư dân. Ngoài ra, cơ chế Heartbeat Watchdog 15 giây và LWT đảm bảo nếu trạm biên bị mất điện hay đứt cáp quang, phòng điều hành sẽ lập tức phát hiện trong vòng 15 giây."*
  >

---

# CHƯƠNG 4: BẢNG "PHAO CỨU SINH" & CÂU HỎI PHẢN BIỆN CỦA GIẢNG VIÊN (Q&A)

Dưới đây là 6 câu hỏi kinh điển nhất mà Giảng viên thường chất vấn sinh viên, kèm câu trả lời chuẩn xác giúp bạn đạt điểm tối đa:

### ❓ Câu 1: "Tại sao nhóm dùng bộ lọc EMA mà không lấy trung bình cộng 10 mẫu đơn giản?"

* **Trả lời chuẩn:**
  > *"Dạ thưa Thầy, bộ lọc trung bình cộng (SMA) bắt buộc phải cấp phát mảng nhớ lưu $N$ phần tử trong RAM và phản ứng chậm như nhau ở cả hai chiều. Nhóm em sử dụng **Bộ lọc Trung bình Động Hàm mũ Bất đối xứng (Asymmetric EMA)** với công thức:
  >
  > $$
  > S_t = \alpha \cdot X_t + (1 - \alpha) \cdot S_{t-1}$$  
  > Khi khói tăng, hệ thống dùng $\alpha_{\text{rise}} = 0.40$ để bắt cháy thật cực nhanh chỉ sau 1–2 chu kỳ; khi khói giảm, dùng $\alpha_{\text{fall}} = 0.15$ để tránh hiện tượng xung nhiễu ADC làm tắt còi báo động sớm. Đặc biệt, EMA chỉ tốn đúng 4 byte RAM (lưu $S_{t-1}$), hoàn toàn không tốn mảng nhớ."*
  > $$
  >

---

### ❓ Câu 2: "Cơ chế Khóa An Toàn PCCC (Safety Interlock) được thực hiện ở tầng nào?"

* **Trả lời chuẩn:**
  > *"Dạ thưa Thầy, hệ thống áp dụng nguyên tắc **Bảo vệ Đa tầng (Defense in Depth)** trên cả 2 tầng:
  >
  > 1. **Tầng Giao diện (Web SCADA):** Ngay khi `fsmState === 'ALARM'`, các nút Tắt quạt và Tắt tiếng bị vô hiệu hóa `disabled = true` để chống người dùng thao tác nhầm.
  > 2. **Tầng Nhúng (Firmware C++):** Trong hàm `applyFanAction()`, firmware kiểm tra cờ `alarmLatched`. Nếu đang có cháy, lệnh `OFF` bị từ chối dứt khoát ở mức phần cứng và trả về mã lỗi `ACK_SAFETY_LOCK`. Do đó, kể cả hacker có can thiệp trực tiếp vào broker MQTT cũng không thể tắt được quạt."*
  >

---

### ❓ Câu 3: "Nếu hệ thống bị mất kết nối Wi-Fi đúng lúc xảy ra hỏa hoạn thì sao?"

* **Trả lời chuẩn:**
  > *"Dạ thưa Thầy, kiến trúc của nhóm là **Edge-First (Xử lý độc lập tại biên)**:
  > Máy trạng thái FSM, còi hú và rơ-le quạt được điều khiển trực tiếp trên chân GPIO của ESP32 qua timer ngắt non-blocking, hoàn toàn không phụ thuộc vào Internet.
  > Khi mất mạng, ESP32 vẫn tự hú còi và bật quạt cứu hộ ngay lập tức, đồng thời lưu toàn bộ số đo vào **Bộ đệm vòng Offline (Circular Ring Buffer 20 bản ghi)** trong RAM. Khi có mạng trở lại, hàm `flushOfflineBuffer()` sẽ tự động đồng bộ trả nợ dữ liệu về máy chủ."*
  >

---

### ❓ Câu 4: "Tại sao hệ thống lại chia làm 2 ngưỡng Ngày (400 PPM) và Đêm (350 PPM)?"

* **Trả lời chuẩn:**
  > *"Dạ thưa Thầy, đây là **Quy tắc Thích ứng Ngày/Đêm (Adaptive Day/Night - Rule 3)**:
  >
  > - **Ban ngày:** Hoạt động nấu nướng và giao thông sinh ra nhiều khói bụi nền, nên đặt ngưỡng 400 PPM để tránh báo động giả.
  > - **Ban đêm (sau 22h):** Cư dân ngủ say, phản xạ chậm và nguy cơ ngạt khói tử vong rất cao. Node-RED tự động kích hoạt lập lịch hạ ngưỡng xuống 350 PPM để tăng độ nhạy, phát hiện hỏa hoạn sớm nhất có thể."*
  >

---

### ❓ Câu 5: "Làm thế nào để tránh việc relay đóng ngắt liên tục khi nồng độ khói dao động quanh ngưỡng 400 PPM?"

* **Trả lời chuẩn:**
  > *"Dạ thưa Thầy, nhóm áp dụng 2 lớp giải pháp:
  >
  > 1. **Vùng trễ Hysteresis:** Ngưỡng kích hoạt bật là $\ge 400\text{ PPM}$, nhưng ngưỡng tắt phải hạ sâu xuống $\le 300\text{ PPM}$.
  > 2. **Máy trạng thái Cooldown 30s:** Khi khói giảm dưới 300 PPM, hệ thống chưa cho tắt ngay mà khóa ở trạng thái `COOLDOWN` tối thiểu 30 giây, loại bỏ hoàn toàn hiện tượng rung tiếp điểm (chattering) bảo vệ rơ-le."*
  >

---

### ❓ Câu 6: "Mã nguồn ESP32 chạy liên tục nhiều ngày có bị tràn RAM hay rò rỉ bộ nhớ (Memory Leak) không?"

* **Trả lời chuẩn:**
  > *"Dạ thưa Thầy, toàn bộ mã nguồn C++ của nhóm đã được thẩm định nghiêm ngặt:
  >
  > - Không sử dụng `String` động của Arduino, tất cả chuỗi đều dùng buffer tĩnh `char[]` có kích thước giới hạn cố định.
  > - Thư viện `ArduinoJson v7` được khai báo dưới dạng biến cục bộ trong từng hàm xử lý theo nguyên lý **RAII (Resource Acquisition Is Initialization)**, bộ nhớ heap tạm được giải phóng 100% ngay khi thoát hàm.
  > - Bộ nhớ tĩnh biên dịch của firmware chiếm **46,552 Byte (14.2% SRAM)** và dung lượng Flash **785,165 Byte (59.9%)**, đảm bảo ESP32 vận hành ổn định bền bỉ 24/7."*
  >

---

# TỔNG KẾT BẢO VỆ

Chúc bạn và Nhóm 09 có một buổi bảo vệ đồ án thành công rực rỡ và đạt điểm số cao nhất! 🎯
