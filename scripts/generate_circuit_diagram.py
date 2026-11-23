# -*- coding: utf-8 -*-
r"""
scripts/generate_circuit_diagram.py
Tạo 3 hình ảnh sơ đồ kỹ thuật chất lượng cao (300 DPI) phục vụ Báo cáo Final:
1. docs/images/circuit_schematic_wiring.png: Sơ đồ ghép nối mạch nguyên lý và phân bổ chân linh kiện toàn hệ thống
2. docs/images/firmware_functional_hierarchy.png: Sơ đồ phân rã chức năng và cấu trúc phân cấp hàm Firmware C++
3. docs/images/firmware_execution_flowchart.png: Lưu đồ thuật toán vòng lặp thực thi phi chặn loop()
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Cấu hình font chữ và độ sắc nét
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Calibri']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False

os.makedirs('docs/images', exist_ok=True)

# =============================================================================
# 1. SƠ ĐỒ GHÉP NỐI MẠCH NGUYÊN LÝ TOÀN HỆ THỐNG (CIRCUIT SCHEMATIC WIRING)
# =============================================================================
def generate_circuit_diagram():
    fig, ax = plt.subplots(figsize=(15, 10), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Nền trắng và viền bao ngoài
    fig.patch.set_facecolor('white')
    ax.add_patch(patches.Rectangle((0.1, 0.1), 14.8, 9.8, fill=False, edgecolor='#222222', linewidth=1.5))

    # Tiêu đề sơ đồ
    ax.text(7.5, 9.5, "SƠ ĐỒ NGUYÊN LÝ GHÉP NỐI CHÂN PHẦN CỨNG HỆ THỐNG BÁO KHÓI IOT (NHÓM 09)", 
            fontsize=13, fontweight='bold', ha='center', va='center', color='#111111')
    ax.text(7.5, 9.15, "Chuẩn xác 100% theo diagram.json / Mô phỏng Wokwi & Đấu nối Breadboard thực tế phòng Lab", 
            fontsize=10, fontstyle='italic', ha='center', va='center', color='#444444')

    # Khối trung tâm: ESP32 DevKit V4
    esp_box = patches.FancyBboxPatch((5.8, 2.8), 3.4, 5.2, boxstyle="round,pad=0.2", 
                                     fc='#F0F4F8', ec='#1A365D', lw=2.5)
    ax.add_patch(esp_box)
    ax.text(7.5, 7.6, "ESP32 DevKit V4\n(Vi Điều Khiển Trung Tâm)", 
            fontsize=11, fontweight='bold', ha='center', va='center', color='#1A365D')
    ax.text(7.5, 7.15, "Xtensa Dual-Core 240MHz", fontsize=8.5, ha='center', va='center', color='#4A5568')

    # Danh sách chân trên ESP32
    pins_left = [
        ("5V (Power In/Out)", 6.4, '#C53030'),
        ("3V3 (Power Out)", 5.7, '#E53E3E'),
        ("GND.1 (Mass chung)", 5.0, '#1A202C'),
        ("GND.2 (Mass tải)", 4.3, '#1A202C'),
        ("GPIO 34 (ADC1_CH6)", 3.6, '#B7791F')
    ]
    for label, y, col in pins_left:
        ax.add_patch(patches.Rectangle((5.5, y-0.2), 0.5, 0.4, fc=col, ec='black', lw=1))
        ax.text(6.1, y, label, fontsize=8.5, fontweight='bold', ha='left', va='center', color='#2D3748')

    pins_right = [
        ("GPIO 4 (1-Wire)", 6.4, '#2F855A'),
        ("GPIO 16 (PWM LEDC)", 5.7, '#DD6B20'),
        ("GPIO 17 (Digital Out)", 5.0, '#6B46C1'),
        ("GPIO 18 (Input Pullup)", 4.3, '#0987A0'),
        ("GPIO 2 (LED Status)", 3.6, '#3182CE')
    ]
    for label, y, col in pins_right:
        ax.add_patch(patches.Rectangle((9.0, y-0.2), 0.5, 0.4, fc=col, ec='black', lw=1))
        ax.text(8.9, y, label, fontsize=8.5, fontweight='bold', ha='right', va='center', color='#2D3748')

    # 1. Module Cảm biến MQ-2 (Góc trên bên trái)
    ax.add_patch(patches.FancyBboxPatch((0.6, 6.2), 3.4, 2.2, boxstyle="round,pad=0.15", fc='#FEFCBF', ec='#B7791F', lw=2))
    ax.text(2.3, 8.0, "CẢM BIẾN KHÓI MQ-2", fontsize=10, fontweight='bold', ha='center', color='#744210')
    ax.text(2.3, 7.6, "Nguyên lý SnO2 cầu phân áp", fontsize=8, fontstyle='italic', ha='center', color='#975A16')
    ax.text(1.0, 7.1, "VCC  [Nuôi Heater 5V]", fontsize=8.5, ha='left', color='#C53030')
    ax.text(1.0, 6.7, "GND  [Nối đất 0V]", fontsize=8.5, ha='left', color='#1A202C')
    ax.text(1.0, 6.3, "AOUT [Điện áp khói 0-3.3V]", fontsize=8.5, ha='left', color='#B7791F')

    # Dây MQ-2 -> ESP32
    ax.plot([4.0, 4.8, 4.8, 5.5], [7.1, 7.1, 6.4, 6.4], color='#E53E3E', lw=2, label='5V DC (Đỏ)')
    ax.plot([4.0, 4.6, 4.6, 5.5], [6.7, 6.7, 5.0, 5.0], color='#1A202C', lw=2, label='GND Mass (Đen)')
    ax.plot([4.0, 4.4, 4.4, 5.5], [6.3, 6.3, 3.6, 3.6], color='#D69E2E', lw=2.2, label='Tín hiệu Analog (Vàng gold)')

    # 2. Module Cảm biến DHT22 (Góc dưới bên trái)
    ax.add_patch(patches.FancyBboxPatch((0.6, 2.2), 3.4, 2.2, boxstyle="round,pad=0.15", fc='#C6F6D5', ec='#276749', lw=2))
    ax.text(2.3, 4.0, "CẢM BIẾN NHIỆT ẨM DHT22", fontsize=10, fontweight='bold', ha='center', color='#22543D')
    ax.text(2.3, 3.6, "AM2302 Kỹ thuật số 1-Wire", fontsize=8, fontstyle='italic', ha='center', color='#276749')
    ax.text(1.0, 3.1, "VCC  [Cấp nguồn 3.3V]", fontsize=8.5, ha='left', color='#E53E3E')
    ax.text(1.0, 2.7, "GND  [Nối đất 0V]", fontsize=8.5, ha='left', color='#1A202C')
    ax.text(1.0, 2.3, "SDA  [Tín hiệu số 1-Wire]", fontsize=8.5, ha='left', color='#2F855A')

    # Dây DHT22 -> ESP32
    ax.plot([4.0, 5.0, 5.0, 5.5], [3.1, 3.1, 5.7, 5.7], color='#E53E3E', lw=1.8)
    ax.plot([4.0, 4.8, 4.8, 5.5], [2.7, 2.7, 5.0, 5.0], color='#1A202C', lw=1.8)
    # SDA đi vòng sang phải vào GPIO 4
    ax.plot([4.0, 4.4, 4.4, 10.6, 10.6, 9.5], [2.3, 2.3, 1.2, 1.2, 6.4, 6.4], color='#38A169', lw=2, label='Data 1-Wire (Xanh lá)')

    # 3. Còi Báo Động Active Buzzer (Góc dưới bên phải)
    ax.add_patch(patches.FancyBboxPatch((11.0, 1.8), 3.4, 2.0, boxstyle="round,pad=0.15", fc='#FEEBC8', ec='#C05621', lw=2))
    ax.text(12.7, 3.4, "CÒI BÁO ĐỘNG BUZZER", fontsize=10, fontweight='bold', ha='center', color='#7B341E')
    ax.text(12.7, 3.0, "PWM LEDC Channel 0 (2000Hz)", fontsize=8, fontstyle='italic', ha='center', color='#9C4221')
    ax.text(11.4, 2.5, "Chân 2 (POS) [+] Tín hiệu", fontsize=8.5, ha='left', color='#DD6B20')
    ax.text(11.4, 2.1, "Chân 1 (NEG) [-] Mass chung", fontsize=8.5, ha='left', color='#1A202C')

    # Dây Buzzer -> ESP32
    ax.plot([11.0, 10.2, 10.2, 9.5], [2.5, 2.5, 5.7, 5.7], color='#DD6B20', lw=2, label='Xung PWM Còi (Cam)')
    ax.plot([11.0, 10.4, 10.4, 5.5], [2.1, 2.1, 0.9, 0.9], color='#1A202C', lw=1.8)
    ax.plot([5.5, 5.2, 5.2, 5.5], [0.9, 0.9, 5.0, 5.0], color='#1A202C', lw=1.8)

    # 4. Nút Nhấn Khẩn Cấp / Test (Giữa bên phải)
    ax.add_patch(patches.FancyBboxPatch((11.0, 4.3), 3.4, 1.8, boxstyle="round,pad=0.15", fc='#E6FFFA', ec='#319795', lw=2))
    ax.text(12.7, 5.7, "NÚT NHẤN KHẨN CẤP / TEST", fontsize=10, fontweight='bold', ha='center', color='#234E52')
    ax.text(12.7, 5.3, "Cấu hình ngắt INPUT_PULLUP", fontsize=8, fontstyle='italic', ha='center', color='#285E61')
    ax.text(11.4, 4.9, "Chân 1.l: Tín hiệu nút", fontsize=8.5, ha='left', color='#0987A0')
    ax.text(11.4, 4.5, "Chân 2.l: Nối đất Mass", fontsize=8.5, ha='left', color='#1A202C')

    # Dây Nút nhấn -> ESP32
    ax.plot([11.0, 9.5], [4.9, 4.3], color='#00B4D8', lw=2, label='Nút nhấn Pullup (Xanh lơ)')
    ax.plot([11.0, 10.0, 10.0, 5.2], [4.5, 4.5, 5.0, 5.0], color='#1A202C', lw=1.8)

    # 5. Module Rơ-le 1 Kênh 5V & Quạt Hút DC / LED (Góc trên bên phải)
    ax.add_patch(patches.FancyBboxPatch((11.0, 6.6), 3.4, 2.5, boxstyle="round,pad=0.15", fc='#FAF5FF', ec='#6B46C1', lw=2))
    ax.text(12.7, 8.8, "MODULE RƠ-LE 1 KÊNH 5V", fontsize=10, fontweight='bold', ha='center', color='#44337A')
    ax.text(12.7, 8.4, "Cách ly quang Opto PC817", fontsize=8, fontstyle='italic', ha='center', color='#553C9A')
    ax.text(11.3, 8.0, "VCC, GND: Nguồn nuôi cuộn hút", fontsize=8, ha='left', color='#6B46C1')
    ax.text(11.3, 7.6, "IN: Lệnh kích từ GPIO 17", fontsize=8, ha='left', color='#6B46C1')
    ax.text(11.3, 7.2, "COM: Tiếp điểm chung nối 5V", fontsize=8, ha='left', color='#C53030')
    ax.text(11.3, 6.8, "NO: Thường mở nối Quạt/LED", fontsize=8, ha='left', color='#2B6CB0')

    # Dây ESP32 -> Rơ-le IN
    ax.plot([9.5, 10.0, 10.0, 11.0], [5.0, 5.0, 7.6, 7.6], color='#805AD5', lw=2, label='Kích Relay IN (Tím)')
    # Dây ESP32 5V -> Relay VCC & COM
    ax.plot([5.5, 5.3, 5.3, 10.5, 10.5, 11.0], [6.4, 6.4, 8.6, 8.6, 8.0, 8.0], color='#E53E3E', lw=2)
    ax.plot([10.5, 11.0], [7.2, 7.2], color='#E53E3E', lw=2)
    # Dây Relay GND -> ESP32 GND.2
    ax.plot([11.0, 10.3, 10.3, 5.5], [8.0, 8.0, 4.3, 4.3], color='#1A202C', lw=1.8)

    # 6. Tải Quạt Hút DC / LED Xanh
    ax.add_patch(patches.FancyBboxPatch((8.8, 1.4), 1.8, 1.3, boxstyle="round,pad=0.1", fc='#EBF8FF', ec='#3182CE', lw=2))
    ax.text(9.7, 2.4, "QUẠT HÚT DC\n(Wokwi LED FAN)", fontsize=8, fontweight='bold', ha='center', color='#2B6CB0')
    ax.text(9.0, 1.9, "Anode (+)", fontsize=7.5, color='#2B6CB0')
    ax.text(9.0, 1.6, "Cathode (-)", fontsize=7.5, color='#1A202C')

    # Dây Relay NO -> Anode Quạt (Xanh dương)
    ax.plot([11.0, 10.7, 10.7], [6.8, 6.8, 1.9], color='#3182CE', lw=2.2, label='Tải Quạt NO (Xanh dương)')
    ax.plot([10.7, 9.8], [1.9, 1.9], color='#3182CE', lw=2.2)
    # Dây Cathode -> GND.2
    ax.plot([9.0, 5.5], [1.6, 4.3], color='#1A202C', lw=1.8)

    # Khung chú thích màu dây (Legend)
    leg_box = patches.Rectangle((0.6, 0.3), 13.8, 0.7, fill=True, fc='#F7FAFC', ec='#CBD5E0', lw=1)
    ax.add_patch(leg_box)
    ax.text(0.8, 0.65, "MÃ MÀU DÂY CHUẨN ĐỒ ÁN (THEO DIAGRAM.JSON):", fontsize=8.5, fontweight='bold', color='#2D3748')
    
    colors_info = [
        (4.8, '#E53E3E', '5V / 3.3V (Đỏ)'),
        (6.7, '#1A202C', 'GND Mass (Đen)'),
        (8.5, '#D69E2E', 'MQ-2 ADC (Vàng)'),
        (10.3, '#38A169', 'DHT22 Data (Xanh lá)'),
        (12.2, '#DD6B20', 'PWM Còi (Cam)')
    ]
    for x, col, txt in colors_info:
        ax.add_patch(patches.Rectangle((x, 0.5), 0.3, 0.2, fc=col, ec='black', lw=0.5))
        ax.text(x + 0.35, 0.6, txt, fontsize=7.5, va='center', color='#2D3748')

    plt.tight_layout()
    out_path = 'docs/images/circuit_schematic_wiring.png'
    plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"[OK] Da sinh anh: {out_path}")

# =============================================================================
# 2. SƠ ĐỒ PHÂN RÃ CHỨC NĂNG VÀ CẤU TRÚC HÀM FIRMWARE C++
# =============================================================================
def generate_functional_hierarchy_diagram():
    fig, ax = plt.subplots(figsize=(15, 9.5), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 9.5)
    ax.axis('off')

    fig.patch.set_facecolor('white')
    ax.add_patch(patches.Rectangle((0.1, 0.1), 14.8, 9.3, fill=False, edgecolor='#222222', linewidth=1.5))

    ax.text(7.5, 9.0, "SƠ ĐỒ PHÂN RÃ CHỨC NĂNG & CẤU TRÚC HÀM FIRMWARE C++ (ESP32)", 
            fontsize=13, fontweight='bold', ha='center', va='center', color='#111111')
    ax.text(7.5, 8.65, "Kiến trúc mã nguồn phi chặn (Non-blocking) • Quản lý bộ nhớ RAII • Phân tách 6 khối chuyên biệt", 
            fontsize=9.5, fontstyle='italic', ha='center', va='center', color='#444444')

    modules = [
        ("1. KHỞI TẠO & CẤU HÌNH\n(Hardware Initialization)", 0.5, 5.0, 4.3, 3.2, '#EBF8FF', '#3182CE', [
            ("setup()", "Khởi tạo Serial, Timer, GPIO, Nạp ngắt"),
            ("initActuators()", "Cấu hình chân Relay GPIO17, Còi GPIO16"),
            ("initSensors()", "Cấu hình ADC1_CH6, 1-Wire GPIO4"),
            ("calibrateMQ2()", "Hiệu chuẩn 2 điểm tính R0 môi trường sạch"),
            ("initOfflineBuffer()", "Khởi tạo RingBuffer tĩnh 20 bản ghi RAM")
        ]),
        ("2. THU THẬP & LỌC TÍN HIỆU\n(Sensing & DSP Filter)", 5.3, 5.0, 4.4, 3.2, '#FEFCBF', '#B7791F', [
            ("readMQ2PPM()", "Đọc ADC, tính Rs theo cầu phân áp & PPM"),
            ("mq2Update()", "Giám sát đứt cáp ADC<100 / chập ADC>4000"),
            ("emaUpdate()", "Lọc số Asymmetric EMA (aRise=0.4, aFall=0.15)"),
            ("readDHT()", "Giao tiếp số 1-Wire chu kỳ 5 giây, bẫy NaN"),
            ("dhtOnRead()", "Xử lý lỗi timeout cảm biến nhiệt ẩm DHT22")
        ]),
        ("3. LÕI FSM & KHÓA AN TOÀN\n(State Machine & Safety)", 10.2, 5.0, 4.3, 3.2, '#FED7D7', '#E53E3E', [
            ("fsmStep()", "Máy trạng thái 5 mức: SAFE->WARN->ALARM..."),
            ("applyFanAction()", "Khóa an toàn PCCC cấm tắt quạt khi ALARM"),
            ("applyBuzzerAction()", "Xử lý còi Mute 180s / Test hú 500ms"),
            ("cmdLocalButton()", "Ngắt nút nhấn khẩn cấp dập tắt còi 60s"),
            ("recompute()", "Tính toán lại đầu ra chấp hành tức thời")
        ]),
        ("4. ĐIỀU KHIỂN CHẤP HÀNH\n(Actuator Driver)", 0.5, 1.0, 4.3, 3.4, '#FAF5FF', '#805AD5', [
            ("fanApply()", "Kích mức logic chân Relay đóng cắt Quạt DC"),
            ("buzzerTick()", "Điều chế xung âm thanh PWM LEDC 2000Hz"),
            ("buzzerTest()", "Hú còi thử nghiệm kiểm tra âm lượng"),
            ("buttonTick()", "Bộ lọc chống rung cơ học Debounce 50ms")
        ]),
        ("5. TRUYỀN THÔNG & ĐỆM RAM\n(MQTT & Ring Buffer)", 5.3, 1.0, 4.4, 3.4, '#C6F6D5', '#276749', [
            ("netTick()", "Quản lý kết nối Wi-Fi & MQTT Backoff"),
            ("publishTelemetry()", "Đóng gói JSON RFC 8259 gửi chu kỳ 2s"),
            ("publishAlarmEvent()", "Bắn bản tin sự cố khẩn cấp (QoS 1)"),
            ("pushOfflineRecord()", "Lưu 20 sự cố vào RAM khi mất mạng"),
            ("flushOfflineBuffer()", "Xả bù tuần tự bản tin khi mạng hồi phục")
        ]),
        ("6. TIẾP NHẬN LỆNH DOWNLINK\n(Command Dispatcher)", 10.2, 1.0, 4.3, 3.4, '#E6FFFA', '#319795', [
            ("mqttCallback()", "Bắt gói tin đến, chống tràn heap ArduinoJson"),
            ("onFan() / onBuzzer()", "Phân tích cú pháp lệnh điều khiển quạt/còi"),
            ("onScheduler()", "Nhận lệnh đổi ngưỡng nhạy Ngày/Đêm"),
            ("onFaultInjection()", "Giả lập đứt cáp phục vụ kiểm thử"),
            ("publishAck()", "Bắn bản tin xác nhận ACK về Broker")
        ])
    ]

    for title, x, y, w, h, bg_col, border_col, funcs in modules:
        ax.add_patch(patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15", fc=bg_col, ec=border_col, lw=2))
        ax.text(x + w/2, y + h - 0.35, title, fontsize=9.5, fontweight='bold', ha='center', va='top', color=border_col)
        
        fy = y + h - 0.95
        for fname, fdesc in funcs:
            ax.text(x + 0.15, fy, fname, fontsize=8.5, fontweight='bold', color='#1A202C')
            ax.text(x + 0.15, fy - 0.22, "• " + fdesc, fontsize=7.5, color='#4A5568')
            fy -= 0.45

    # Mũi tên luồng tương tác giữa các module
    ax.annotate("", xy=(5.3, 6.6), xytext=(4.8, 6.6), arrowprops=dict(arrowstyle="->", color="#4A5568", lw=2))
    ax.annotate("", xy=(10.2, 6.6), xytext=(9.7, 6.6), arrowprops=dict(arrowstyle="->", color="#4A5568", lw=2))
    ax.annotate("", xy=(2.6, 4.4), xytext=(2.6, 5.0), arrowprops=dict(arrowstyle="->", color="#4A5568", lw=2))
    ax.annotate("", xy=(7.5, 4.4), xytext=(7.5, 5.0), arrowprops=dict(arrowstyle="->", color="#4A5568", lw=2))
    ax.annotate("", xy=(12.3, 4.4), xytext=(12.3, 5.0), arrowprops=dict(arrowstyle="->", color="#4A5568", lw=2))

    plt.tight_layout()
    out_path = 'docs/images/firmware_functional_hierarchy.png'
    plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"[OK] Da sinh anh: {out_path}")

# =============================================================================
# 3. LƯU ĐỒ THUẬT TOÁN VÒNG LẶP CHÍNH LOOP() (EXECUTION FLOWCHART)
# =============================================================================
def generate_execution_flowchart():
    fig, ax = plt.subplots(figsize=(12, 14), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 14)
    ax.axis('off')

    fig.patch.set_facecolor('white')
    ax.add_patch(patches.Rectangle((0.1, 0.1), 11.8, 13.8, fill=False, edgecolor='#222222', linewidth=1.5))

    ax.text(6.0, 13.4, "LƯU ĐỒ THUẬT TOÁN VÒNG LẶP THỰC THI PHI CHẶN loop() (ESP32)", 
            fontsize=12, fontweight='bold', ha='center', va='center', color='#111111')
    ax.text(6.0, 13.05, "Cơ chế phân lịch thời gian thực (Time-sliced Non-blocking millis) • Tách biệt 7 công đoạn", 
            fontsize=9, fontstyle='italic', ha='center', va='center', color='#444444')

    # Node Start
    ax.add_patch(patches.FancyBboxPatch((4.2, 12.2), 3.6, 0.6, boxstyle="round,pad=0.2", fc='#2B6CB0', ec='#1A365D', lw=1.5))
    ax.text(6.0, 12.5, "BẮT ĐẦU CHU TRÌNH loop()", fontsize=9.5, fontweight='bold', color='white', ha='center')

    # Step 1: netTick
    ax.annotate("", xy=(6.0, 11.7), xytext=(6.0, 12.2), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.add_patch(patches.Rectangle((2.8, 11.1), 6.4, 0.6, fc='#EBF8FF', ec='#3182CE', lw=1.5))
    ax.text(6.0, 11.4, "1. netTick(now): Duy trì Wi-Fi & MQTT theo Exponential Backoff", fontsize=8.5, ha='center', fontweight='bold')

    # Step 2: buttonTick
    ax.annotate("", xy=(6.0, 10.6), xytext=(6.0, 11.1), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.add_patch(patches.Rectangle((2.8, 10.0), 6.4, 0.6, fc='#EBF8FF', ec='#3182CE', lw=1.5))
    ax.text(6.0, 10.3, "2. buttonTick(now): Chống rung 50ms & Bắt nút nhấn khẩn cấp", fontsize=8.5, ha='center', fontweight='bold')

    # Step 3: buzzerTick & fanApply
    ax.annotate("", xy=(6.0, 9.5), xytext=(6.0, 10.0), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.add_patch(patches.Rectangle((2.8, 8.9), 6.4, 0.6, fc='#EBF8FF', ec='#3182CE', lw=1.5))
    ax.text(6.0, 9.2, "3. buzzerTick() & fanApply(): Cập nhật chấp hành Quạt & Còi PWM", fontsize=8.5, ha='center', fontweight='bold')

    # Decision 1: MQ-2 Sample (2000ms)
    ax.annotate("", xy=(6.0, 8.3), xytext=(6.0, 8.9), arrowprops=dict(arrowstyle="->", lw=1.5))
    d1 = patches.Polygon([[6.0, 8.3], [8.5, 7.6], [6.0, 6.9], [3.5, 7.6]], fc='#FEFCBF', ec='#B7791F', lw=1.5)
    ax.add_patch(d1)
    ax.text(6.0, 7.7, "now - g_lastSample >= 2000ms?", fontsize=8.5, fontweight='bold', ha='center')
    ax.text(6.0, 7.35, "(Chu kỳ đo Khói & FSM)", fontsize=7.5, fontstyle='italic', ha='center')

    # Branch True: Read MQ-2, EMA, FSM, Telemetry
    ax.annotate("ĐÚNG (Mỗi 2s)", xy=(6.0, 6.3), xytext=(6.0, 6.9), arrowprops=dict(arrowstyle="->", lw=1.5), fontsize=7.5, fontweight='bold', color='#276749')
    ax.add_patch(patches.Rectangle((2.0, 5.1), 8.0, 1.2, fc='#FEFCBF', ec='#B7791F', lw=1.5))
    ax.text(6.0, 5.9, "• Đọc ADC1_CH6 (GPIO34) -> mq2Update() kiểm tra đứt cáp / chập", fontsize=8, ha='center')
    ax.text(6.0, 5.5, "• emaUpdate(): Lọc số Asymmetric EMA (aRise=0.40, aFall=0.15)", fontsize=8, ha='center')
    ax.text(6.0, 5.25, "• fsmStep(): Cập nhật FSM 5 mức & publishTelemetry() (hoặc đệm RAM)", fontsize=8, ha='center')

    # Branch False bypasses to DHT
    ax.plot([8.5, 10.5, 10.5], [7.6, 7.6, 4.4], color='#C53030', lw=1.5)
    ax.text(9.0, 7.7, "SAI", fontsize=7.5, fontweight='bold', color='#C53030')

    # Decision 2: DHT22 Sample (5000ms)
    ax.annotate("", xy=(6.0, 4.4), xytext=(6.0, 5.1), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.plot([10.5, 8.5], [4.4, 4.4], color='#C53030', lw=1.5)
    
    d2 = patches.Polygon([[6.0, 4.4], [8.5, 3.8], [6.0, 3.2], [3.5, 3.8]], fc='#C6F6D5', ec='#276749', lw=1.5)
    ax.add_patch(d2)
    ax.text(6.0, 3.9, "now - g_lastDht >= 5000ms?", fontsize=8.5, fontweight='bold', ha='center')
    ax.text(6.0, 3.55, "(Chu kỳ đọc Nhiệt Ẩm DHT22)", fontsize=7.5, fontstyle='italic', ha='center')

    # Branch True: Read DHT
    ax.annotate("ĐÚNG (Mỗi 5s)", xy=(6.0, 2.7), xytext=(6.0, 3.2), arrowprops=dict(arrowstyle="->", lw=1.5), fontsize=7.5, fontweight='bold', color='#276749')
    ax.add_patch(patches.Rectangle((2.8, 2.2), 6.4, 0.5, fc='#C6F6D5', ec='#276749', lw=1.5))
    ax.text(6.0, 2.45, "Đọc 1-Wire DHT22 (GPIO4) -> Cập nhật Temp & Hum (bẫy NaN)", fontsize=8, ha='center')

    # Branch False bypasses to End
    ax.plot([8.5, 10.0, 10.0], [3.8, 3.8, 1.6], color='#C53030', lw=1.5)
    ax.text(8.9, 3.9, "SAI", fontsize=7.5, fontweight='bold', color='#C53030')

    # Latency guard & Loop End
    ax.annotate("", xy=(6.0, 1.6), xytext=(6.0, 2.2), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.plot([10.0, 6.0], [1.6, 1.6], color='#C53030', lw=1.5)
    
    ax.add_patch(patches.Rectangle((2.8, 1.1), 6.4, 0.5, fc='#EDF2F7', ec='#4A5568', lw=1.5))
    ax.text(6.0, 1.35, "Loop Latency Guard: Cảnh báo nếu loopDuration > 50ms", fontsize=8, ha='center', fontstyle='italic')

    ax.annotate("", xy=(6.0, 0.6), xytext=(6.0, 1.1), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.add_patch(patches.FancyBboxPatch((4.2, 0.3), 3.6, 0.5, boxstyle="round,pad=0.15", fc='#2D3748', ec='#1A202C', lw=1.5))
    ax.text(6.0, 0.55, "KẾT THÚC VÒNG LẶP (LẶP LẠI TỨC THÌ)", fontsize=8.5, fontweight='bold', color='white', ha='center')

    # Loop back line
    ax.plot([4.2, 1.2, 1.2, 4.2], [0.55, 0.55, 12.5, 12.5], color='#4A5568', lw=1.5, linestyle='--')
    ax.annotate("", xy=(4.2, 12.5), xytext=(1.2, 12.5), arrowprops=dict(arrowstyle="->", lw=1.5, color='#4A5568', linestyle='--'))
    ax.text(1.4, 6.5, "Chu trình lặp phi chặn liên tục (Tần số ~1000 Hz)", fontsize=8, rotation=90, color='#4A5568', ha='center')

    plt.tight_layout()
    out_path = 'docs/images/firmware_execution_flowchart.png'
    plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"[OK] Da sinh anh: {out_path}")

if __name__ == '__main__':
    print("Bắt đầu sinh 3 hình ảnh sơ đồ kỹ thuật chất lượng cao...")
    generate_circuit_diagram()
    generate_functional_hierarchy_diagram()
    generate_execution_flowchart()
    print("HOÀN TẤT SINH ẢNH SƠ ĐỒ KỸ THUẬT!")
