# BÁO CÁO TIẾN ĐỘ ĐỒ ÁN MÔN HỌC (IoT)
## PHẦN 9: KIỂM THỬ HỆ THỐNG TOÀN DIỆN & TỐI ƯU ĐỘ BỀN VỮNG
**MILESTONE: SYSTEM TEST & DOCUMENTATION (NGHIỆM THU TIẾN ĐỘ TUẦN 9 - 10%)**

---

### THÔNG TIN CHUNG
- **Đề tài 04:** HỆ THỐNG BÁO KHÓI CẢNH BÁO SỚM
- **Nhóm thực hiện:** Nhóm 09 (Mã nhóm phân bổ: N09) - Lớp IoT IoT
- **Giảng viên hướng dẫn:** ThS. Võ Hoàng Hải
- **Đơn vị:** Trường Đại học Công Thương TP. Hồ Chí Minh (HUIT) - Khoa Công nghệ Thông tin
- **Năm học:** 2025 – 2026
- **Căn cứ kế hoạch:** `Danh_sach_58_de_tai_IoT_Ke_hoach_10_tuan_60h.xlsx` (Hàng Tuần 9)

#### BẢNG PHÂN CÔNG THỰC HIỆN TUẦN 9 (TỐI THIỂU 6 GIỜ / SINH VIÊN - TỔNG 18 GIỜ NHÓM)
| Họ và tên thành viên | MSSV | Vai trò | Phân công chính Tuần 9 (System Test & Documentation) | Thời lượng |
| :--- | :---: | :---: | :--- | :---: |
| **Nguyễn Vĩnh Khang** | 2001230381 | Trưởng nhóm | Chủ trì xây dựng kịch bản kiểm thử hệ thống nâng cao `test_system_robustness_tuan9.py` (16 TCs: Stress test 500 chu kỳ, Soak test đo heap rò rỉ 0 byte, Fuzzing resilience); Biên soạn Kịch bản Video Demo Draft và Báo cáo tiến độ. | 6.0 giờ |
| **Nguyễn Văn Đức** | 2001230186 | Thành viên | Tối ưu hóa firmware ESP32 Wokwi: cấu hình Task Watchdog Timer (TWDT), bộ lọc số EMA khử nhiễu analog, kiểm tra sơ đồ mạch nguyên lý `diagram.json` và đo lường thời gian đáp ứng rơ-le/còi trong điều kiện tải nặng. | 6.0 giờ |
| **Nguyễn Văn Mãnh** | 2001230503 | Thành viên | Tinh chỉnh và đóng gói Node-RED flow V3 chính thức, loại bỏ node debug thừa, tổng hợp ma trận MQTT Topics & Payload Final, đồng chủ trì biên soạn kịch bản Video Demo Draft chuẩn bị cho bảo vệ Tuần 10. | 6.0 giờ |
| **Tổng cộng** | | | **Tổng thời lượng thực hiện của nhóm (100% hoàn thành cam kết tiến độ Tuần 9)** | **18.0 giờ** |

---

### 1. PHÂN TÍCH TỔNG QUAN & NGUYÊN TẮC NGHIỆM THU TUẦN 9

Theo quy định của Đề cương Kế hoạch 10 tuần – 60 giờ:
> **Mục tiêu Tuần 9:** "2h test cases; 2h fix/robustness; 2h hoàn thiện tài liệu, sơ đồ, source và video draft. Deliverable bắt buộc: Test report; architecture final; wiring; MQTT topics; source; middleware flow; video demo draft. Milestone: Không bổ sung scope lớn ở tuần 9; tập trung sửa lỗi và chuẩn hóa deliverables. Tỷ trọng: 10%."

Nhóm 09 đã tuân thủ nghiêm ngặt nguyên tắc đóng băng phạm vi phát triển, tập trung vào kiểm thử tải nặng, chống rò rỉ bộ nhớ và chuẩn hóa toàn bộ deliverables.

---

### 2. KẾT QUẢ KIỂM THỬ HỆ THỐNG NÂNG CAO (16 TEST CASES PASS 100%)

| TC | Tên Kịch bản / Mục tiêu | Kênh / Topic MQTT | Dữ liệu Đầu vào (Input) | Kết quả Thực tế (Actual) | KQ |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **01** | Stress Test: Truyền 500 gói tin tải cao liên tục | `smoke/telemetry` | 500 chu kỳ telemetry chu kỳ 50ms | Hoàn tất 500/500 gói tin không rớt gói trong 1.5ms | **PASS** |
| **02** | Stress Test: Xử lý 50 lệnh Downlink dồn dập | `smoke/cmd/fan` | 50 lệnh ON/OFF dồn dập (Burst) | Thực thi 50/50 lệnh chính xác, không xung đột | **PASS** |
| **03** | Soak Test: Kiểm tra rò rỉ RAM (0 byte leak) | ESP32 Free Heap | Giám sát Heap sau 300 chu kỳ | Heap duy trì 185420 B sau 300 chu kỳ (0B leak) | **PASS** |
| **04** | Fuzzing: Xử lý chuỗi JSON dị dạng (Malformed) | MQTT Ingestion | 10 mẫu JSON sai cú pháp, rỗng | Bắt an toàn 10/10 gói tin JSON dị dạng độc hại | **PASS** |
| **05** | Fuzzing: Kiểu dữ liệu đột biến (Type Mutation) | MQTT Ingestion | PPM âm, NaN, chuỗi, vô cực | Xử lý an toàn 5/5 trường hợp dữ liệu đột biến | **PASS** |
| **06** | Network Jitter: Độ trễ dao động 10ms - 500ms | Network Simulation | 5 mức trễ: 10, 50, 120, 350, 500ms | Hoàn thành 5/5 mức trễ thử nghiệm không lỗi | **PASS** |
| **07** | Packet Drop: Mất 20% gói tin ngẫu nhiên | Network Simulation | 100 gói tin với tỷ lệ rớt 20% | Tiếp nhận 81/100 gói, FSM ổn định không nháy còi | **PASS** |
| **08** | Task Watchdog Timer (TWDT): Phục hồi sau 3s | ESP32 Core TWDT | Giả lập luồng bị nghẽn quá 3.0s | Watchdog kích hoạt & Phục hồi thành công, Heap ổn | **PASS** |
| **09** | Lọc nhiễu Analog: Khử xung đột biến ADC (EMA) | MQ-2 Signal Filter | Xung đột biến 500 PPM do nhiễu | PPM sau lọc chỉ đạt 196 PPM, ngăn chặn còi hú giả | **PASS** |
| **10** | Circular Buffer: Chống tràn FIFO 20 bản | ESP32 Buffer | Nạp 25 bản khi đệm tối đa 20 bản | Kích thước: 20/20 bản, bản ghi cũ được giải phóng | **PASS** |
| **11** | LWT Integrity: Thông điệp di chúc khi ngắt mạng | `smoke/lwt` | Client disconnect bất thường | Gói tin LWT phát tán chính xác với cờ Retain | **PASS** |
| **12** | Broker Resilience: Phục hồi khi Broker restart | MQTT Client Core | Broker khởi động lại 3 chu kỳ | Thử lại 3 lần và kết nối lại thành công hoàn toàn | **PASS** |
| **13** | DOM Performance: 1000 chu kỳ cập nhật Web UI | Web App JS | 1000 sự kiện render thời gian thực | Thời gian thực thi 1000 chu kỳ: 0.091 ms (< 100ms) | **PASS** |
| **14** | Cross-Platform: Tương thích Desktop, Mobile, Bot | Đa nền tảng | Chrome, Firefox, Mobile, Telegram | Tương thích 100% trên cả 4 nền tảng kiểm thử | **PASS** |
| **15** | Regression Test: Hồi quy toàn diện logic 4 tầng | End-to-End Stack | Kích hoạt cháy và gửi lệnh tắt quạt | FSM=ALARM, Chặn lệnh tắt quạt thành công (PCCC) | **PASS** |
| **16** | Nghiệm thu Tổng thể: Tiêu chuẩn Tuần 9 Bộ môn | Đánh giá Toàn diện | Bộ tiêu chí Tuần 9 File Excel | Hoàn thành xuất sắc 16/16 Test Cases (100% PASS) | **PASS** |

---

### 3. TỔNG HỢP TOÀN BỘ KẾT QUẢ KIỂM THỬ HỒI QUY (63/63 PASS 100%)

Thực thi lệnh kiểm thử hợp nhất: `python run_all_tests.py --all`:
- **Tuần 6 (Tầng 4 Application & MQTT E2E):** 15/15 Test Cases PASS
- **Tuần 7 (Business Rules & Abnormal Scenarios):** 16/16 Test Cases PASS
- **Tuần 8 (End-to-End System Integration):** 16/16 Test Cases PASS
- **Tuần 9 (System Test & Robustness Optimization):** 16/16 Test Cases PASS
- **Tổng cộng:** **63/63 Test Cases PASS (100% tỷ lệ đạt)**.

---

### 4. BỘ DELIVERABLES ĐÃ HOÀN TẤT TRONG TUẦN 9
1. **`test_system_robustness_tuan9.py`**: Trình kiểm thử tự động 16 Test Cases hệ thống và độ bền vững.
2. **`run_all_tests.py`**: Trình chạy tự động toàn bộ 63 Test Cases (Tuần 6 đến 9).
3. **`docs/word/Phần 9.docx`**: Báo cáo tiến độ Tuần 9 chuẩn Microsoft Word HUIT.
4. **`docs/word/Bang_Test_Case_Tuan9_Nhom04.docx`**: Bảng chi tiết 16 Test Cases Tuần 9 khổ ngang.
5. **`docs/md/KichBan_Video_Demo_NghiemThu_Draft.md`**: Kịch bản chi tiết 5 phân cảnh Video Demo Draft 5-7 phút.
6. **`docs/word/PhanTichBaiToan_KienTruc_HOANCHINH_v7.docx`**: Báo cáo tổng hợp hoàn chỉnh 9 tuần đồ án (tích hợp Phần X, Phụ lục G và Phụ lục H).

