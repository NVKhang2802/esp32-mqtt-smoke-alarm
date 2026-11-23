# Báo Cáo Nghiệm Thu & Kiểm Thử Trực Quan Đa Nền Tảng (Live Multi-Platform UI Verification)
## Đề tài: Hệ thống Báo khói Cảnh báo sớm — Nhóm 09 (N09) HUIT
**Môn học:** Internet of Things (IoT)  
**Giảng viên hướng dẫn:** ThS. Võ Hoàng Hải  

---

## 1. Chuẩn Hóa Định Danh Nhóm 09 & Môn Học IoT

Toàn bộ hệ thống và tài liệu của dự án đã được rà soát và chuẩn hóa 100% theo đúng yêu cầu:
1. **Tên Nhóm:** **Nhóm 09** (hoặc `Nhóm 09 (N09)`). Đã thay thế triệt để các vị trí trước đây ghi nhầm `Nhóm 04`.
2. **Mã định danh thiết bị & Token đồng bộ 4 tầng:**
   - Device ID: `ESP32_SMOKE_N09_A01`, `ESP32_SMOKE_N09_A02`, `ESP32_SMOKE_N09_A03`
   - Secret Token: `HUIT_IOT_SECURE_TOKEN_N09`
   - Client ID: `NodeRED_Smoke_Middleware_N09`, `WebClient_Smoke_N09_`, `MQTTX_Tester_Nhom09`, `test-client-n09`
   - Telegram Bot: `@HUIT_FireAlert_N09_Bot`
   - Tiền tố Topic: Giữ nguyên chuẩn `Nhom09/smoke/...`
3. **Tên Môn Học:** **Internet of Things (IoT)** (hoặc `IoT`). Đã xóa bỏ hoàn toàn cụm từ *"Lập trình nhúng"*, *"Hệ thống nhúng"* trong mã nguồn, báo cáo tiến độ tuần và kịch bản thuyết trình.

---

## 2. Đối Chiếu Thực Tế & Phản Biện Kỹ Thuật (Direct Audit Alignment)

| Điểm phản biện từ Auditor | Thực trạng mã nguồn đã tái cấu trúc | Bằng chứng kiểm thử tự động | Bằng chứng kiểm thử trực quan qua trình duyệt (/browser) |
| :--- | :--- | :--- | :--- |
| **1. T-W2, T-W3, T-W4 chứng minh Web an toàn & chỉ phản chiếu**<br>*"Ba test tự dựng DOM giả và logic inline, không nạp app.js"* | [web/app.js](file:///e:/IoT/DoAn/web/app.js) xuất khẩu trực tiếp `calculateMq2Ppm`, `isAlarmState`, `parseMqttPayload`, `renderAuditTable`. [web/tests/util.test.js](file:///e:/IoT/DoAn/web/tests/util.test.js) `require('../app.js')` thật. | **5/5 Web Tests PASS** | Web SCADA chạy trên `http://localhost:8085` kết nối WebSocket WSS tới broker, chỉ phản chiếu Telemetry thực tế từ trạm, không can thiệp logic FSM. |
| **2. Web không tự gửi lệnh quạt/còi**<br>*"Vẫn còn evaluateFsmRules, triggerAlarmState, triggerCooldownState"* | Đã xóa triệt để 3 hàm tự phát lệnh này khỏi [web/app.js](file:///e:/IoT/DoAn/web/app.js). Logic Cooldown 30s do firmware ESP32/Node-RED quản lý. | **T-W1..T-W5 PASS** | Khi khói tăng hay giảm, Web SCADA chỉ hiển thị trạng thái nhận được từ broker; không gửi bất kỳ lệnh `OFF` hay lệnh ngầm nào. |
| **3. Khóa an toàn PCCC khi ALARM**<br>*"Nút bấm Web SCADA phải bị khóa cứng khi có cháy"* | Thêm cơ chế UI Interlock: khi `fsmState === 'ALARM'`, `btnFanOff` và `btnBuzzerMute` tự động gán `disabled = true`. | **T-W5 PASS** | Trên giao diện thật (`scada_02_alarm_interlock.png`), khi khói vọt lên 550 PPM, nút **Tắt Quạt** và **Tắt Tiếng** bị vô hiệu hóa hoàn toàn, chống thao tác nhầm. |
| **4. JSON RAII & Bộ nhớ RAM**<br>*"ArduinoJson v7 cấp phát heap tạm, header ghi Zero Heap Fragmentation"* | Cập nhật header [src/main.cpp](file:///e:/IoT/DoAn/src/main.cpp) ghi rõ: *"Heap tạm giải phóng theo scope RAII"*. Đo đạc chính xác RAM. | **RAM: 46,552 B (14.2%)**<br>**Flash: 785,165 B (59.9%)** | ESP32 chạy ổn định, không tràn ngăn xếp, bản tin JSON serialize/deserialize mượt mà. |
| **5. Điện trở $R_0$ và $R_L$**<br>*"R0 = 1.0 kΩ, 10 kΩ là RL"* | Đã chuẩn hóa trong [src/config.h](file:///e:/IoT/DoAn/src/config.h) và tài liệu: $R_L = 10\text{ k}\Omega$, $R_0 \approx 1.0\text{ k}\Omega$. | **T-E1..T-E5 PASS** | Kim nồng độ khói trên Web SCADA đọc chính xác giá trị tính toán từ đường cong $A \cdot R_s^B$. |
| **6. Claims Registry 10/10 & Test Codes**<br>*"check_claims.py không có, C-MQTTS dùng dummy print"* | Tạo [scripts/check_claims.py](file:///e:/IoT/DoAn/scripts/check_claims.py) quét toàn bộ test files, từ chối lệnh dummy cho VERIFIED/PARTIAL, xác thực 51 mã test. | **10/10 Claims PASS** | Báo cáo kiểm định 3 bậc VERIFIED, PARTIAL, SCOPE hoàn toàn minh bạch. |
| **7. LWT & Timeout Watchdog**<br>*"Engine không có test LWT, backoff chỉ test hàm"* | [lib/core/backoff.h](file:///e:/IoT/DoAn/lib/core/backoff.h) kiểm thử reset khi kết nối lại (`T-R1`, `T-L1`). Node-RED chạy Watchdog 30s. | **T-R1, T-L1 PASS** | Khi mất tín hiệu > 15s, Web SCADA lập tức đổi sang banner xám `MẤT KẾT NỐI (OFFLINE)` và tự động phục hồi khi có Keep-Alive (`scada_04_offline.png`). |

---

## 3. Hình Ảnh Minh Chứng Kiểm Thử Trực Tiếp (Visual Evidence)

Tất cả hình ảnh dưới đây được chụp trực tiếp từ phiên gỡ lỗi tự động trên Google Chrome (DevTools Port 9222) qua subagent `/browser`, không qua giả lập DOM ngầm:

````carousel
![Web SCADA Trạng thái Bình thường (SAFE)](C:/Users/NV/.gemini/antigravity/brain/ac9e6710-1e78-446d-9291-a55d47c059fb/live_test/scada_01_safe.png)
<!-- slide -->
![Web SCADA Báo Động Khẩn & Khóa An Toàn PCCC (ALARM Interlock)](C:/Users/NV/.gemini/antigravity/brain/ac9e6710-1e78-446d-9291-a55d47c059fb/live_test/scada_02_alarm_interlock.png)
<!-- slide -->
![Web SCADA Mất Tín Hiệu Watchdog Timeout (OFFLINE)](C:/Users/NV/.gemini/antigravity/brain/ac9e6710-1e78-446d-9291-a55d47c059fb/live_test/scada_04_offline.png)
<!-- slide -->
![Node-RED Middleware Luồng 52 Nodes & Debug Panel Live](C:/Users/NV/.gemini/antigravity/brain/ac9e6710-1e78-446d-9291-a55d47c059fb/live_test/nodered_live_flow.png)
<!-- slide -->
![Node-RED Dashboard UI Gauges & Realtime Trends](C:/Users/NV/.gemini/antigravity/brain/ac9e6710-1e78-446d-9291-a55d47c059fb/live_test/nodered_dashboard_live.png)
<!-- slide -->
![MQTTX Web Client Giám Sát Topic & Lệnh Downlink](C:/Users/NV/.gemini/antigravity/brain/ac9e6710-1e78-446d-9291-a55d47c059fb/live_test/mqttx_web_live.png)
````

---

## 4. Kết Quả Kiểm Thử Toàn Diện Sau Khi Chuẩn Hóa

Toàn bộ 7 bộ kiểm thử độc lập đã chạy qua và đạt **100% PASS**:

1. **Firmware ESP32 Build (`pio run -e esp32dev`):** SUCCESS (0 Warning, 0 Error, SRAM 14.2%, Flash 59.9%).
2. **C++ Native Unit Tests (`pio test -e native`):** **30/30 PASS**.
3. **Web SCADA Tests (`node --test web/tests/util.test.js`):** **5/5 PASS**.
4. **Node-RED Flow & Engine Tests (`node --test nodered/tests/*.test.js`):** **16/16 PASS**.
5. **Topic Prefix Consistency (`python scripts/verify_topic_prefix.py`):** **62/62 TOPICS PASS**.
6. **3-Tier Audit Claims Validator (`python scripts/check_claims.py`):** **10/10 CLAIMS PASS**.
7. **System Robustness Test Suite (`python tests/run_all_tests.py`):** **16/16 PASS**.

Tài liệu hướng dẫn demo và khởi động trước Giảng viên đã sẵn sàng tại:  
👉 [Huong_Dan_Khoi_Dong_Va_Kich_Ban_Demo.md](file:///e:/IoT/DoAn/docs/md/Huong_Dan_Khoi_Dong_Va_Kich_Ban_Demo.md)

---

## 5. Xuất Bản Báo Cáo Final Nghiệm Thu Đề Tài (Bổ Sung Toàn Diện Phần Cứng & Firmware)

Tài liệu báo cáo Word chính thức đã được tự động tái lập và xác minh tự động 100% đạt chuẩn 12 quy định:  
👉 [Nhom09_HeThongBaoKhoiCanhBaoSom.docx](file:///e:/IoT/DoAn/docs/word/Nhom09_HeThongBaoKhoiCanhBaoSom.docx)

- **Định dạng & Dung lượng:** 3,103,324 bytes (~3.03 MB), 220 đoạn văn bản chuẩn, 25 bảng biểu, 10 hình ảnh đóng khung viền đen 1pt.
- **Bổ sung Sơ đồ ghép nối mạch nguyên lý & Bảng đấu nối chân Lab chi tiết (Chương 3):**
  - **Hình 3.1: Sơ đồ ghép nối mạch nguyên lý và phân bổ chân linh kiện toàn hệ thống:** Bản vẽ 300 DPI thể hiện rõ ràng toàn bộ 7 khối linh kiện, các bus nguồn (5V, 3.3V, GND.1, GND.2) và vòng lặp đóng cắt tải quạt công suất qua rơ-le (`5V -> COM -> NO -> Anode Quạt/LED -> Cathode -> GND.2`).
  - **Bảng 3.3: Bảng đấu nối chân phần cứng phòng Lab (Chi tiết 16 kết nối chuẩn `diagram.json`):** Trích xuất đầy đủ 16 kết nối dây thực nghiệm kèm mã màu dây (Đỏ, Đen, Vàng gold, Xanh lá, Cam, Tím, Xanh dương, Xanh lơ) và chức năng kỹ thuật trong PCCC.
  - **Bảng 3.4: Bảng đối chiếu đặc tính kỹ thuật giữa mô hình mô phỏng Wokwi và mạch phần cứng Lab thực tế.**
  - **Hình 3.2: Giao diện bố trí linh kiện và sơ đồ đi dây mạch mô phỏng trên nền tảng Wokwi.**
- **Bổ sung Bảng Đặc tính điện của chip ESP32 & Bảng Cân bằng công suất (Chương 3):**
  - **Bảng 3.1: Bảng thông số đặc tính điện chi tiết của chip vi điều khiển ESP32:** Trích xuất từ Datasheet Espressif ($V_{DD} = 3.0 \sim 3.6\text{ V}$, mức logic $V_{IL}, V_{IH}, V_{OL}, V_{OH}$, dòng an toàn GPIO $\le 12\text{ mA}$, ADC 12-bit suy hao $11\text{ dB}$, dòng phát Wi-Fi TX $380\text{ mA}$, dải nhiệt độ $-40^\circ\text{C} \sim +85^\circ\text{C}$).
  - **Bảng 3.2: Bảng cân bằng công suất điện năng toàn hệ thống (System Power Budget):** Chứng minh nguồn cấp 5V - 2A (10W) đáp ứng dư tải 130% so với tổng tiêu thụ đỉnh 866.5 mA (~4.33W).
- **Bổ sung Sơ đồ chức năng, Sơ đồ hàm & Lưu đồ thuật toán vòng lặp chính (Chương 4):**
  - **Mục 4.5 & Hình 4.1: Sơ đồ phân rã chức năng và cấu trúc phân cấp hàm trong Firmware C++:** Phân rã thành 6 khối chuyên biệt (Khởi tạo, Thu thập & Lọc số, Lõi FSM & Khóa an toàn, Điều khiển chấp hành, Truyền thông MQTT & Đệm ngoại tuyến, Tiếp nhận lệnh Downlink).
  - **Bảng 4.2: Bảng danh mục 16 hàm cốt lõi trong `src/main.cpp`** kèm tham số đầu vào/ra và vai trò kỹ thuật.
  - **Mục 4.6 & Hình 4.2: Lưu đồ thuật toán vòng lặp thực thi phi chặn `loop()` của vi điều khiển ESP32:** Biểu diễn trực quan 7 công đoạn không chặn (Time-sliced Non-blocking) và các nhánh rẽ thời gian thực (2s MQ-2/FSM, 5s DHT22, 10s Keep-Alive, 50ms Debounce nút nhấn).
- **Hệ thống Phương trình Toán học OMML (`Alt + =`):**
  - 5 Khối phương trình hiển thị độc lập ($R_s$, $\text{PPM}$, Asymmetric EMA, Hysteresis, Rate-of-Rise) và 21 đối tượng toán học nội dòng ($S_t$, $X_t$, $\alpha_{\text{rise}}$, $\alpha_{\text{fall}}$, $R_L$, $V_{cc}$, $R_0$, $A$, $B$, $\frac{dT}{dt} \ge 3.0\text{ }^\circ\text{C/phút}$).
  - 100% Ký hiệu so sánh chuyên nghiệp `≥`, `≤` và dấu nhân chấm giữa `·`.
- **Khắc phục Triệt để Hộp thoại Cảnh báo Mở File:**
  - `settings.xml` không chứa `updateFields`, mở file trên MS Word êm ái, tức thời không có cảnh báo.
- **Hệ thống Định dạng Chuẩn 12 Quy định:**
  - 100% Times New Roman, 100% màu đen (`#000000`), căn đều 2 bên (Justified), 0 dấu gạch ngang dài (`–`, `—`).
  - 3 Sections phân trang: Bìa (không số), Phần sơ bộ (số La Mã `i, ii...`), Thân bài từ "Tổng quan đề tài" (số Ả Rập `1, 2, 3...`).
  - Phụ lục B đã loại bỏ; Phụ lục A giữ bảng BOM chuẩn 34 linh kiện (~720k).


---

## 6. Thiết Kế Lại & Chuẩn Hóa File `.gitignore` Phòng Ngừa Rò Rỉ Mã Nguồn

File [`.gitignore`](file:///e:/IoT/DoAn/.gitignore) của dự án đã được thiết kế lại và chuẩn hóa toàn diện theo cấu trúc 10 chuyên mục chuyên nghiệp:

1. **Khắc phục lỗi cú pháp comment bị chèn đè:** Đã làm sạch toàn bộ các dòng `!scripts/` và `!scripts/check_claims.py` từng bị chèn nhầm vào giữa khối chú thích.
2. **Khắc phục quy tắc `*.py` quá rộng:** Phân tách rạch ròi giữa thư mục nháp ([scratch/](file:///e:/IoT/DoAn/scratch/), [tools/](file:///e:/IoT/DoAn/tools/)) bị chặn nghiêm ngặt, với bộ kiểm thử tự động ([tests/*.py](file:///e:/IoT/DoAn/tests/), [run_all_tests.py](file:///e:/IoT/DoAn/run_all_tests.py)) và script công cụ kiểm toán chính thống ([scripts/*.py](file:///e:/IoT/DoAn/scripts/)) được bảo toàn khả năng theo dõi trên GitHub.
3. **Chống rò rỉ file khóa tạm thời Microsoft Office:** Bổ sung cơ chế loại trừ toàn diện các mẫu `~$*`, `~$*.docx`, `~$*.pptx`, `~$*.xlsx`, `*.tmp`, `*.bak` sinh ra khi biên tập báo cáo Word và slide thuyết minh.
4. **Phòng chống Git Bloat (Phình dung lượng Git):** Chặn các file tài liệu nhị phân nặng (`docs/word/*.docx`, `docs/pptx/*.pptx`, `docs/pdf/`), trong khi bảo lưu sơ đồ kiến trúc ([docs/images/](file:///e:/IoT/DoAn/docs/images/)), tài liệu Markdown ([docs/md/](file:///e:/IoT/DoAn/docs/md/)) và kiểm toán ([docs/audit/claims.yaml](file:///e:/IoT/DoAn/docs/audit/claims.yaml)).
5. **Bảo mật tuyệt đối thông tin nhạy cảm:** Chặn `.env`, `secrets.h`, `credentials.h`, khóa chứng chỉ và `.nodered_runtime/`.
6. **Xác minh đa kịch bản:** Đã kiểm tra tự động qua `git check-ignore -v` trên 13 kịch bản file mẫu; kiểm thử hệ thống đạt **16/16 PASS (100%)**.
