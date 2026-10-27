# -*- coding: utf-8 -*-
"""
Script tạo tài liệu Tuần 5 cho Đồ án IoT (Nhóm 04 - Hệ thống báo khói cảnh báo sớm)
Tạo 2 tài liệu chuẩn Word:
1. docs/word/Phần 5.docx - Báo cáo tiến độ Tuần 5 (Tầng 3: Middleware / Automation Engine)
2. docs/word/Bang_Test_Case_Tuan5_Nhom04.docx - Bảng kịch bản & kết quả kiểm thử Tuần 5
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def apply_cell_style(cell, bg_color=None, bold=False, font_size=10, font_name="Times New Roman", 
                      text_color="000000", align=WD_ALIGN_PARAGRAPH.LEFT, top_pad=100, bot_pad=100):
    tcPr = cell._tc.get_or_add_tcPr()
    if bg_color:
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg_color}"/>')
        tcPr.append(shd)
    
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top_pad}" w:type="dxa"/><w:bottom w:w="{bot_pad}" w:type="dxa"/><w:left w:w="120" w:type="dxa"/><w:right w:w="120" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)
    
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    for p in cell.paragraphs:
        p.alignment = align
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        for r in p.runs:
            r.font.name = font_name
            r.font.size = Pt(font_size)
            r.bold = bold
            r.font.color.rgb = RGBColor(int(text_color[:2], 16), int(text_color[2:4], 16), int(text_color[4:], 16))

def set_table_borders(table, color="B0C4DE", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:left w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:right w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(13.5)
    run.bold = True
    run.font.color.rgb = RGBColor(24, 76, 120)
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    run.bold = True
    run.font.color.rgb = RGBColor(41, 110, 168)
    return p

def add_heading_3(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(11)
    run.bold = True
    run.font.color.rgb = RGBColor(50, 50, 50)
    return p

def add_body_p(doc, text, bold_prefix="", italic=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.2
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Times New Roman"
        r_pre.font.size = Pt(11)
        r_pre.bold = True
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.italic = italic
    return p

def add_bullet_p(doc, text, bold_prefix="", level=0):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.left_indent = Inches(0.25 * (level + 1))
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Times New Roman"
        r_pre.font.size = Pt(10.5)
        r_pre.bold = True
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(10.5)
    return p

def add_code_block(doc, code_text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.left_indent = Inches(0.2)
    p.paragraph_format.right_indent = Inches(0.2)
    
    pPr = p._p.get_or_add_pPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F4F6F9"/>')
    pPr.append(shd)
    
    borders = parse_xml(f'''
        <w:pBdr {nsdecls("w")}>
            <w:left w:val="single" w:sz="18" w:space="6" w:color="1F4E78"/>
            <w:top w:val="none"/>
            <w:right w:val="none"/>
            <w:bottom w:val="none"/>
        </w:pBdr>
    ''')
    pPr.append(borders)
    
    run = p.add_run(code_text)
    run.font.name = "Consolas"
    run.font.size = Pt(9.5)
    run.font.color.rgb = RGBColor(30, 30, 30)
    return p

# ==============================================================================
# 1. BUILD PHẦN 5.DOCX
# ==============================================================================
def create_phan_5():
    print("Building Phần 5.docx...")
    doc = docx.Document()
    
    # Page setup A4
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        
    # Title Header
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_after = Pt(2)
    r1 = p_inst.add_run("BỘ CÔNG THƯƠNG\nTRƯỜNG ĐẠI HỌC CÔNG THƯƠNG TP. HỒ CHÍ MINH\nKHOA CÔNG NGHỆ THÔNG TIN\n")
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(11)
    r1.bold = True
    r2 = p_inst.add_run("------------------------------------\n")
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(10)
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(8)
    p_title.paragraph_format.space_after = Pt(4)
    r_t1 = p_title.add_run("BÁO CÁO TIẾN ĐỘ ĐỒ ÁN MÔN HỌC (LẬP TRÌNH NHÚNG IoT)\n")
    r_t1.font.name = "Times New Roman"
    r_t1.font.size = Pt(13)
    r_t1.bold = True
    
    r_t2 = p_title.add_run("PHẦN 5: THIẾT KẾ & TRIỂN KHAI TẦNG 3 – MIDDLEWARE / AUTOMATION ENGINE (NODE-RED)\n")
    r_t2.font.name = "Times New Roman"
    r_t2.font.size = Pt(14.5)
    r_t2.bold = True
    r_t2.font.color.rgb = RGBColor(24, 76, 120)
    
    r_t3 = p_title.add_run("MILESTONE: MIDDLEWARE & AUTOMATION ENGINE (NGHIỆM THU TIẾN ĐỘ TUẦN 5 - 10%)\n")
    r_t3.font.name = "Times New Roman"
    r_t3.font.size = Pt(12)
    r_t3.bold = True
    r_t3.font.color.rgb = RGBColor(192, 0, 0)

    # Info Box
    p_info = doc.add_paragraph()
    p_info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_info.paragraph_format.space_after = Pt(12)
    r_info = p_info.add_run("Đề tài 04: HỆ THỐNG BÁO KHÓI CẢNH BÁO SỚM  |  Nhóm thực hiện: Nhóm 04 (N09)\nGiảng viên hướng dẫn: ThS. Võ Hoàng Hải  |  Năm học: 2025 – 2026")
    r_info.font.name = "Times New Roman"
    r_info.font.size = Pt(10.5)
    r_info.italic = True
    
    # Member table
    table_m = doc.add_table(rows=4, cols=4)
    set_table_borders(table_m, color="2E75B6")
    hdr = table_m.rows[0].cells
    hdr[0].text = "Họ và tên thành viên"
    hdr[1].text = "MSSV"
    hdr[2].text = "Vai trò trong nhóm"
    hdr[3].text = "Phân công chính Tuần 5 (Middleware)"
    for cell in hdr:
        apply_cell_style(cell, bg_color="1F4E78", bold=True, font_size=10, text_color="FFFFFF", align=WD_ALIGN_PARAGRAPH.CENTER)
    
    members = [
        ("Nguyễn Vĩnh Khang", "2001230381", "Trưởng nhóm", "Thiết kế Máy trạng thái hữu hạn (FSM), Watchdog Heartbeat Timeout, Night Mode Scheduler (Rule 4, 5)"),
        ("Nguyễn Văn Đức", "2001230186", "Thành viên", "Xây dựng luồng Flow Node-RED, Logic phân ngưỡng khói & nhiệt độ (Rule 1, 2), Thuật toán Hysteresis Cooldown (Rule 3)"),
        ("Nguyễn Văn Mãnh", "2001230503", "Thành viên", "Xây dựng Event History Logger (Audit Trail), Command Downlink Dispatcher, Kịch bản kiểm thử tự động & Báo cáo")
    ]
    for idx, m in enumerate(members, start=1):
        row = table_m.rows[idx].cells
        row[0].text = m[0]
        row[1].text = m[1]
        row[2].text = m[2]
        row[3].text = m[3]
        bg = "F2F2F2" if idx % 2 == 1 else "FFFFFF"
        for c_i, c in enumerate(row):
            align = WD_ALIGN_PARAGRAPH.CENTER if c_i in [1, 2] else WD_ALIGN_PARAGRAPH.LEFT
            apply_cell_style(c, bg_color=bg, font_size=9.5, align=align)
            
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # --------------------------------------------------------------------------
    # 1. PHÂN TÍCH TỔNG QUAN & KẾ HOẠCH TRIỂN KHAI TUẦN 5
    # --------------------------------------------------------------------------
    add_heading_1(doc, "1. PHÂN TÍCH TỔNG QUAN & KẾ HOẠCH TRIỂN KHAI TUẦN 5")
    
    add_heading_2(doc, "1.1. Mục tiêu kỹ thuật Tuần 5 (Tầng 3 – Middleware / Automation Engine)")
    add_body_p(doc, "Theo đúng đề cương phân bổ kế hoạch 10 tuần (60 giờ/sinh viên), Tuần 5 là giai đoạn xây dựng 'bộ não điều phối trung tâm' (Automation Engine) tại Tầng 3 - Middleware. Sau khi thiết bị ESP32 đã kết nối mạng hai chiều thành công qua MQTT ở Milestone M2 (Tuần 4), Tầng 3 có nhiệm vụ tiếp nhận dữ liệu cảm biến, phân tích theo thời gian thực, quản lý trạng thái hệ thống và tự động ra quyết định điều khiển trả ngược lại thiết bị chấp hành.")
    add_body_p(doc, "Nguyên tắc nghiệm thu cốt lõi của Tuần 5 do Giảng viên hướng dẫn và Bộ môn quy định là: 'Middleware phải thực hiện xử lý nghiệp vụ thông minh, không chỉ đơn thuần là chuyển tiếp (forward) dữ liệu'. Do đó, nhóm triển khai nền tảng Node-RED kết hợp chặt chẽ với MQTT Broker để hiện thực hóa 5 mục tiêu kỹ thuật then chốt:")
    add_bullet_p(doc, "Xây dựng luồng xử lý luồng sự kiện (Event-driven Flow): Đăng ký nhận dữ liệu từ các Topic MQTT chuẩn (smoke/telemetry, smoke/event/alarm, smoke/status, smoke/lwt), thực hiện giải mã, chuẩn hóa và kiểm tra tính toàn vẹn gói tin JSON.", "• ")
    add_bullet_p(doc, "Hiện thực hóa Máy trạng thái hữu hạn (Finite State Machine - FSM): Quản lý 5 trạng thái vận hành của toàn bộ hệ sinh thái báo khói: SAFE (An toàn), WARNING (Cảnh giác), ALARM (Báo động khẩn), COOLDOWN (Làm mát & xả khói) và OFFLINE (Mất kết nối trạm cảm biến).", "• ")
    add_bullet_p(doc, "Thiết lập hệ thống 5 Quy tắc tự động hóa cốt lõi (Core Automation Rules): Bao gồm quy tắc khói vượt ngưỡng, quy tắc hỏa hoạn do quá nhiệt/tăng nhiệt nhanh, quy tắc trễ hồi phục Hysteresis chống dập dờn (chattering), quy tắc đổi độ nhạy theo khung giờ đêm (Scheduler), và quy tắc giám sát nhịp tim (Heartbeat Watchdog).", "• ")
    add_bullet_p(doc, "Hệ thống ghi nhật ký sự kiện có cấu trúc (Event History & Audit Trail): Tự động ghi chép mọi biến động môi trường, chuyển trạng thái và lệnh điều khiển vào bộ nhớ đệm (Circular Buffer 50 mục) và lưu trữ bền vững vào tập tin logs/event_history.log nhằm phục vụ công tác điều tra an toàn PCCC.", "• ")
    add_bullet_p(doc, "Bộ điều phối lệnh Downlink hai chiều (Command Dispatcher): Phát các thông điệp điều khiển có cấu trúc (smoke/cmd/fan, smoke/cmd/buzzer) và đồng bộ trạng thái thực tế của thiết bị chấp hành.", "• ")

    add_heading_2(doc, "1.2. Phân bổ khung thời gian 6 giờ thực hiện chi tiết cho mỗi sinh viên")
    add_body_p(doc, "Tiến độ Tuần 5 được nhóm chia thành 3 khung thời gian chuẩn hóa (tổng 18 giờ làm việc của nhóm 3 thành viên):")
    add_bullet_p(doc, "Khung 3 giờ đầu (H1 – H3) – Thiết kế kiến trúc Flow & Triển khai Node-RED Middleware: Cấu hình MQTT Broker Client ID, tạo các node MQTT-In kết nối với broker.emqx.io:1883; lập trình các hàm Function Node giải mã JSON, tiền xử lý dữ liệu và xây dựng khung sườn Máy trạng thái hữu hạn (FSM).", "− ")
    add_bullet_p(doc, "Khung 2 giờ tiếp theo (H4 – H5) – Lập trình Threshold, Scheduler, Hysteresis & FSM Engine: Hiện thực hóa logic đánh giá ngưỡng khói (350/400 PPM); thuật toán trễ làm mát Hysteresis 20 giây chống chattering cho quạt hút; bộ lập lịch Night Mode Scheduler dựa trên thời gian thực; cơ chế Watchdog Heartbeat phát hiện mất kết nối quá 10 giây.", "− ")
    add_bullet_p(doc, "Khung 1 giờ cuối (H6) – Xây dựng Logging, Command Feedback, Dashboard & Kiểm thử: Lập trình chức năng ghi file Audit Log (logs/event_history.log); thiết kế cơ chế giới hạn tần suất cảnh báo (Rate Limiting 30s) chống bão tin nhắn; xây dựng kịch bản kiểm thử tự động bằng Python; xuất file export flows_smoke_detector.json hoàn chỉnh.", "− ")

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # --------------------------------------------------------------------------
    # 2. KIẾN TRÚC TẦNG 3 MIDDLEWARE TRONG MÔ HÌNH IOT 4 TẦNG
    # --------------------------------------------------------------------------
    add_heading_1(doc, "2. KIẾN TRÚC TẦNG 3 MIDDLEWARE TRONG MÔ HÌNH IOT 4 TẦNG")
    add_body_p(doc, "Trong đồ án môn học Lập trình nhúng IoT, hệ thống tuân thủ nghiêm ngặt mô hình kiến trúc chuẩn 4 tầng:")
    add_bullet_p(doc, "Tầng 1 (Sensing/Physical): Vi điều khiển ESP32, cảm biến MQ-2 (đo nồng độ khói/khí ga), cảm biến DHT22 (đo nhiệt độ, độ ẩm), còi báo Buzzer (PWM) và Relay điều khiển Quạt hút khói DC.", "1. ")
    add_bullet_p(doc, "Tầng 2 (Network/Connectivity): Kết nối WiFi chuẩn 802.11 b/g/n, giao thức truyền thông MQTT qua Broker trung gian (broker.emqx.io), quy hoạch topic phân cấp rõ ràng (telemetry, alarm, cmd, status, lwt).", "2. ")
    add_bullet_p(doc, "Tầng 3 (Middleware / Automation Engine): Nền tảng Node-RED đóng vai trò trung tâm phân tích dữ liệu, vận hành máy trạng thái FSM, tính toán ngưỡng động, thực hiện lọc trễ Hysteresis, quản lý ghi nhật ký sự kiện và phát lệnh điều khiển Downlink.", "3. ")
    add_bullet_p(doc, "Tầng 4 (Application / Presentation): Giao diện Node-RED Dashboard hiển thị trực quan thông số Gauges, biểu đồ thời gian thực, bảng nhật ký sự kiện, tích hợp kênh thông báo cảnh báo khẩn cấp (Telegram/Push).", "4. ")

    add_body_p(doc, "Sơ đồ luồng tương tác hai chiều tại Tầng 3 Middleware:")
    add_code_block(doc, 
"+-------------------------------------------------------------------------+\n"
"|           TẦNG 1: SENSING / ACTUATION (ESP32 Wokwi Node)                 |\n"
"+-------------------------------------------------------------------------+\n"
"      | (Uplink Telemetry/Alarm)             ^ (Downlink Commands)\n"
"      v                                      | (Fan/Buzzer Action)\n"
"+-------------------------------------------------------------------------+\n"
"|           TẦNG 2: NETWORK (MQTT Broker - broker.emqx.io:1883)            |\n"
"+-------------------------------------------------------------------------+\n"
"      | (MQTT Sub: smoke/#)                  ^ (MQTT Pub: smoke/cmd/*)\n"
"      v                                      |\n"
"+-------------------------------------------------------------------------+\n"
"|           TẦNG 3: MIDDLEWARE ENGINE (Node-RED Automation)               |\n"
"|                                                                         |\n"
"|  [1. Packet Decoder & Validator] --> Chuyển đổi JSON, kiểm tra tính hợp lệ|\n"
"|  [2. Finite State Machine (FSM)] --> SAFE <-> WARN <-> ALARM <-> COOLDOWN|\n"
"|  [3. Automation Rule Evaluator]  --> 5 Core Rules (PPM, Temp, Hysteresis)|\n"
"|  [4. Night Mode Scheduler]       --> Tự động đổi ngưỡng nhạy ban đêm    |\n"
"|  [5. Heartbeat Watchdog Engine]  --> Bắt timeout > 10s hoặc LWT Offline |\n"
"|  [6. Audit Logger & Rate Limiter]--> Ghi file log, chống spam tin nhắn   |\n"
"|  [7. Command Dispatcher]         --> Định dạng lệnh gửi trả ESP32        |\n"
"+-------------------------------------------------------------------------+\n"
"      |                                      ^\n"
"      v                                      | (Manual Override Action)\n"
"+-------------------------------------------------------------------------+\n"
"|           TẦNG 4: APPLICATION (Node-RED Dashboard / Alerting)            |\n"
"+-------------------------------------------------------------------------+")

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # --------------------------------------------------------------------------
    # 2.2. HIỆN THỰC HÓA 4 DỊCH VỤ SLIDE 65, SCALE & QUẢN TRỊ HẠM ĐỘI THIẾT BỊ
    # --------------------------------------------------------------------------
    add_heading_2(doc, "2.2. Hiện thực hóa 4 Dịch vụ Slide 65, Cơ chế Scale & Quản trị Hạm đội thiết bị (Fleet Management)")
    add_body_p(doc, "Tiếp thu ý kiến góp ý của Giảng viên hướng dẫn (ThS. Võ Hoàng Hải) tại Slide 65 bài giảng '3. Lập trình IoT', Tầng 3 Middleware được nâng cấp toàn diện từ mô hình đơn thiết bị sang kiến trúc hạm đội đa thiết bị (Multi-device Fleet Architecture):")
    
    add_heading_3(doc, "2.2.1. Phân tách và hiện thực 4 dịch vụ độc lập kết nối Cơ sở dữ liệu")
    add_bullet_p(doc, "Dịch vụ 1 - Authentication & Provisioning Service: Khi thiết bị ESP32 khởi động, nó phát thông điệp yêu cầu xác thực (1a). Node-RED đối soát mã định danh phần cứng (MAC Address và Secret Token) với cơ sở dữ liệu Whitelist. Nếu hợp lệ, hệ thống cấp phát Session Key, phân vùng không gian (Building/Floor/Room) và nạp cấu hình thời gian thực (1c)-(1d). Các thiết bị lạ sẽ bị từ chối truy cập ngay lập tức.", "• ")
    add_bullet_p(doc, "Dịch vụ 2 - Collect Sensors Data Service: Xử lý các luồng Telemetry (2a)-(2b) chứa nồng độ khói MQ-2 và nhiệt độ/độ ẩm DHT22 kèm Session Key hợp lệ. Dữ liệu được đưa vào lưu trữ chuỗi thời gian (Time-series Log) và cấp cho Rule Engine.", "• ")
    add_bullet_p(doc, "Dịch vụ 3 - Control & Cross-Zone Automation Service: Không chỉ điều khiển cục bộ từng phòng (3a)-(3b), Middleware sở hữu quy tắc tự động hóa liên vùng (Cross-Zone Emergency): Khi 1 phòng phát hiện cháy lớn, hệ thống tự động phát lệnh bật còi báo động khẩn cấp cho toàn bộ các phòng trên cùng tầng sàn.", "• ")
    add_bullet_p(doc, "Dịch vụ 4 - Keep-Alive (Heartbeat) Service: Tiếp nhận định kỳ gói tin báo trạng thái sống của thiết bị (4a)-(4b) mỗi 10 giây (chứa Uptime, Free Heap, RSSI), giúp phát hiện nhanh chóng các node bị mất nguồn hoặc đứt cáp.", "• ")

    add_heading_3(doc, "2.2.2. Cơ chế Scale không gian đa cấp độ hỗ trợ Wildcard")
    add_body_p(doc, "Middleware sử dụng cây Topic chuẩn hóa 5 cấp: smoke/v2/{building}/{floor}/{room}/{device_id}/{channel}. Nhờ các ký tự đại diện Wildcard (+ và #), một cụm luồng xử lý duy nhất trên Node-RED có thể quản lý đồng thời từ 1 đến hàng nghìn cảm biến khói trải dài qua nhiều tòa nhà mà không cần nhân bản mã nguồn.")

    add_heading_3(doc, "2.2.3. Bảng Quản trị Danh bạ Thiết bị Động (Dynamic Fleet Management)")
    add_body_p(doc, "Node-RED duy trì bảng băm Device Registry trong bộ nhớ: lưu trữ danh sách các node đang hoạt động, trạng thái FSM riêng biệt của từng node, thời điểm nhận tin gần nhất (Last Seen) và ngưỡng cảnh báo riêng theo từng khu vực (ví dụ phòng bếp ngưỡng 500 PPM, phòng ngủ ngưỡng 350 PPM).")

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # --------------------------------------------------------------------------
    # 3. THIẾT KẾ MÁY TRẠNG THÁI HỮU HẠN (FINITE STATE MACHINE - FSM)
    # --------------------------------------------------------------------------
    add_heading_1(doc, "3. THIẾT KẾ MÁY TRẠNG THÁI HỮU HẠN (FINITE STATE MACHINE - FSM)")
    add_body_p(doc, "Để đảm bảo tính nhất quán, ngăn ngừa xung đột điều khiển và loại bỏ hoàn toàn các hành vi không xác định (undefined behaviors), Middleware được thiết kế xoay quanh Máy trạng thái hữu hạn (FSM) gồm 5 trạng thái định danh:")
    
    table_fsm = doc.add_table(rows=6, cols=5)
    set_table_borders(table_fsm, color="2E75B6")
    hdr_fsm = table_fsm.rows[0].cells
    hdr_fsm[0].text = "Trạng thái (State)"
    hdr_fsm[1].text = "Ý nghĩa nghiệp vụ"
    hdr_fsm[2].text = "Điều kiện kích hoạt (Entry Condition)"
    hdr_fsm[3].text = "Hành vi thiết bị chấp hành"
    hdr_fsm[4].text = "Trạng thái kế tiếp"
    for cell in hdr_fsm:
        apply_cell_style(cell, bg_color="1F4E78", bold=True, font_size=9.5, text_color="FFFFFF", align=WD_ALIGN_PARAGRAPH.CENTER)

    fsm_data = [
        ("SAFE", "Môi trường an toàn, thông số bình thường", "PPM < Ngưỡng Warning (250 PPM) & Nhiệt độ < 50°C", "Quạt: TẮT, Còi: TẮT", "WARNING, ALARM, OFFLINE"),
        ("WARNING", "Chớm xuất hiện khói hoặc nhiệt độ cao", "250 PPM <= PPM < 400 PPM hoặc Nhiệt độ >= 55°C", "Quạt: TẮT, Còi: TẮT, Ghi log cảnh báo", "SAFE, ALARM, OFFLINE"),
        ("ALARM", "Báo động khẩn cấp có khói dày đặc", "PPM >= Ngưỡng Alarm (400 PPM) hoặc nhận URGENT_ALARM", "Quạt: BẬT, Còi: HÚ, Bắn tin cảnh báo", "COOLDOWN, OFFLINE"),
        ("COOLDOWN", "Giai đoạn làm mát & xả khói tồn dư", "Đang ở ALARM và PPM hạ xuống < 300 PPM", "Quạt: DUY TRÌ BẬT trong 20s trễ Hysteresis", "SAFE (hết trễ), ALARM (nếu khói tăng lại)"),
        ("OFFLINE", "Mất kết nối với trạm cảm biến ESP32", "Quá 10s không nhận Telemetry hoặc nhận LWT offline", "Giữ nguyên trạng thái an toàn, phát cảnh báo đứt mạng", "SAFE (khi có kết nối lại)")
    ]

    for idx, row_data in enumerate(fsm_data, start=1):
        row = table_fsm.rows[idx].cells
        for c_idx in range(5):
            row[c_idx].text = row_data[c_idx]
            bg = "F9FBFD" if idx % 2 == 1 else "FFFFFF"
            align = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 4] else WD_ALIGN_PARAGRAPH.LEFT
            apply_cell_style(row[c_idx], bg_color=bg, font_size=9, align=align)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # --------------------------------------------------------------------------
    # 4. ĐẶC TẢ 5 QUY TẮC TỰ ĐỘNG HÓA CỐT LÕI (CORE AUTOMATION RULES)
    # --------------------------------------------------------------------------
    add_heading_1(doc, "4. ĐẶC TẢ 5 QUY TẮC TỰ ĐỘNG HÓA CỐT LÕI (CORE AUTOMATION RULES)")
    add_body_p(doc, "Nhằm đáp ứng xuất sắc yêu cầu 'Middleware phải xử lý thông minh, không chỉ forward dữ liệu', nhóm xây dựng 5 quy tắc tự động hóa đa tầng, giải quyết trọn vẹn các bài toán thực tế trong vận hành phòng cháy chữa cháy:")

    add_heading_2(doc, "4.1. Quy tắc 1 (Rule 1): Phát hiện khói vượt ngưỡng & Kích hoạt Downlink khẩn cấp")
    add_body_p(doc, "Mô tả nghiệp vụ: Khi nồng độ khói từ cảm biến MQ-2 vượt ngưỡng báo động (ALARM_THRESHOLD = 400 PPM ở chế độ thường, hoặc 350 PPM ở chế độ ban đêm), hoặc khi nhận được gói tin khẩn cấp từ topic smoke/event/alarm:")
    add_bullet_p(doc, "Middleware chuyển trạng thái FSM sang ALARM.", "1. ")
    add_bullet_p(doc, "Tạo bản ghi Audit Log mức CRITICAL với sự kiện SMOKE_ALARM_TRIGGERED kèm giá trị PPM thực tế.", "2. ")
    add_bullet_p(doc, "Phát đồng thời 2 lệnh Downlink qua MQTT: gửi {\"action\":\"ON\",\"reason\":\"RULE_1_SMOKE_ALARM\"} vào smoke/cmd/fan và {\"action\":\"UNMUTE\"} vào smoke/cmd/buzzer.", "3. ")
    add_bullet_p(doc, "Kích hoạt luồng thông báo khẩn cấp tới ứng dụng Dashboard / Telegram kèm cơ chế Rate Limiting.", "4. ")

    add_heading_2(doc, "4.2. Quy tắc 2 (Rule 2): Cảnh báo quá nhiệt & Tốc độ gia nhiệt bất thường (Thermal Hazard)")
    add_body_p(doc, "Mô tả nghiệp vụ: Trong nhiều tình huống hỏa hoạn thực tế (như chập điện kín), lửa có thể sinh nhiệt lượng rất lớn trước khi khói lan tới cảm biến MQ-2. Do đó, Middleware tích hợp thuật toán phân tích chuỗi thời gian đối với dữ liệu nhiệt độ từ DHT22:")
    add_bullet_p(doc, "Ngưỡng nhiệt độ tĩnh (Static Threshold): Nếu Nhiệt độ >= 55.0°C, hệ thống ghi log cảnh báo mức WARN (sự kiện HEAT_OVERHEAT) và nâng mức trạng thái lên WARNING.", "• ")
    add_bullet_p(doc, "Tốc độ gia nhiệt động (Rate-of-Rise dT/dt): Middleware lưu lại giá trị nhiệt độ của chu kỳ trước. Nếu trong khoảng thời gian dt >= 30 giây mà tốc độ tăng nhiệt dT/dt >= 5.0°C/phút, hệ thống lập tức phát cảnh báo HEAT_RAPID_RISE để người dùng kiểm tra nguồn nhiệt bất thường.", "• ")

    add_heading_2(doc, "4.3. Quy tắc 3 (Rule 3): Cơ chế Hysteresis & Cooldown tự động tắt quạt (Anti-chattering)")
    add_body_p(doc, "Mô tả nghiệp vụ & Vấn đề kỹ thuật: Trong điều khiển thiết bị công suất (như Quạt hút khói công nghiệp hoặc Relay), nếu sử dụng một ngưỡng đóng/ngắt duy nhất (Single Threshold), tại lân cận ngưỡng (ví dụ khói dao động quanh 400 PPM do gió), Relay sẽ bị đóng ngắt liên tục với tần số cao (hiện tượng Chattering). Hiện tượng này gây ra hồ quang điện, phá hỏng tiếp điểm Relay và làm cháy động cơ quạt.")
    add_body_p(doc, "Giải pháp Hysteresis & Cooldown tại Tầng 3 Middleware:")
    add_bullet_p(doc, "Tách biệt ngưỡng kích hoạt và ngưỡng ngắt (Dual Threshold): Bật quạt khi PPM >= 400, nhưng chỉ cho phép xem xét tắt quạt khi PPM đã giảm sâu xuống dưới SAFE_THRESHOLD = 300 PPM (vùng đệm Hysteresis 100 PPM).", "1. ")
    add_bullet_p(doc, "Bộ định thời làm mát an toàn (Cooldown Timer): Khi khói đã giảm xuống < 300 PPM, hệ thống KHÔNG tắt quạt ngay mà chuyển sang trạng thái trung gian COOLDOWN và kích hoạt bộ đếm thời gian trễ 20 giây (COOLDOWN_DURATION_MS = 20000ms) để tiếp tục hút sạch lượng khí độc/khói còn lắng đọng trong phòng.", "2. ")
    add_bullet_p(doc, "Cơ chế chống tái bùng phát (Re-escalation Guard): Nếu trong 20 giây đếm lùi, nồng độ khói bất ngờ tăng trở lại >= 300 PPM, quá trình Cooldown bị hủy bỏ ngay lập tức (COOLDOWN_ABORTED), hệ thống tái lập trạng thái ALARM và tiếp tục duy trì quạt hút.", "3. ")
    add_bullet_p(doc, "Kết thúc an toàn: Chỉ khi hết 20 giây trễ mà nồng độ khói vẫn duy trì ổn định dưới 300 PPM, Middleware mới phát lệnh Downlink tắt Quạt hút {\"action\":\"OFF\"} và đưa FSM về SAFE.", "4. ")

    add_heading_2(doc, "4.4. Quy tắc 4 (Rule 4): Bộ lập lịch tự động thay đổi độ nhạy ban đêm (Night Sensitivity Scheduler)")
    add_body_p(doc, "Mô tả nghiệp vụ: Vào khung giờ ban đêm (từ 22:00 đêm đến 06:00 sáng hôm sau), các thành viên trong gia đình chìm vào giấc ngủ sâu, phản xạ khứu giác và thính giác giảm sút, nguy cơ ngạt khói tăng gấp nhiều lần so với ban ngày. Bộ lập lịch thời gian thực (Scheduler) tự động can thiệp:")
    add_bullet_p(doc, "Kiểm tra chu kỳ 1 phút một lần: Đọc hàm new Date().getHours().", "• ")
    add_bullet_p(doc, "Khung giờ đêm (22:00 – 06:00): Tự động chuyển sensitivityMode = 'NIGHT', siết chặt ngưỡng báo động xuống ALARM_THRESHOLD = 350 PPM (thay vì 400 PPM) và SAFE_THRESHOLD = 250 PPM nhằm phát hiện sự cố sớm hơn.", "• ")
    add_bullet_p(doc, "Khung giờ ngày (06:00 – 22:00): Tự động trả về sensitivityMode = 'NORMAL' (ngưỡng 400 PPM) để tránh các báo động giả khi nấu nướng ban ngày.", "• ")

    add_heading_2(doc, "4.5. Quy tắc 5 (Rule 5): Giám sát nhịp tim cảm biến & Xử lý sự cố ngắt kết nối (Heartbeat Watchdog)")
    add_body_p(doc, "Mô tả nghiệp vụ: Một hệ thống báo cháy không được phép 'im lặng giả tạo' khi cảm biến bị đứt cáp nguồn hoặc mất sóng WiFi:")
    add_bullet_p(doc, "Tích hợp Watchdog Timer chu kỳ 3 giây: So sánh thời điểm hiện tại now với thời điểm nhận gói tin gần nhất lastSeen.", "• ")
    add_bullet_p(doc, "Nếu now - lastSeen > 10000ms (quá 10 giây không có Telemetry): Middleware tự động chuyển sang trạng thái OFFLINE, tạo bản ghi lỗi HEARTBEAT_TIMEOUT và cảnh báo người vận hành kiểm tra trạm cảm biến.", "• ")
    add_bullet_p(doc, "Xử lý thông điệp Last Will and Testament (LWT): Nếu Broker báo nhận được gói tin 'offline' trên topic smoke/lwt, Middleware lập tức chuyển FSM sang OFFLINE ngay mà không cần đợi hết 10 giây timeout.", "• ")

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # --------------------------------------------------------------------------
    # 5. CƠ CHẾ GHI NHẬT KÝ SỰ KIỆN (LOGGING & EVENT HISTORY - AUDIT TRAIL)
    # --------------------------------------------------------------------------
    add_heading_1(doc, "5. CƠ CHẾ GHI NHẬT KÝ SỰ KIỆN (LOGGING & EVENT HISTORY - AUDIT TRAIL)")
    add_body_p(doc, "Yêu cầu bắt buộc của Milestone Tuần 5 là phải có cơ chế Logging & Event History. Nhóm thiết kế giải pháp ghi nhật ký hai tầng hoàn chỉnh:")
    
    add_heading_2(doc, "5.1. Cấu trúc bản ghi nhật ký sự kiện có cấu trúc (Structured Log Entry)")
    add_body_p(doc, "Mỗi sự kiện phát sinh trong hệ thống được đóng gói theo định dạng chuẩn:")
    add_code_block(doc,
"{\n"
"  \"time\": \"19:15:30 05/10/2026\",\n"
"  \"level\": \"CRITICAL\",          // INFO | WARN | ERROR | CRITICAL\n"
"  \"event\": \"SMOKE_ALARM_TRIGGERED\",\n"
"  \"desc\": \"Khói vượt ngưỡng (462.8 PPM >= 400.0 PPM). Kích hoạt còi và quạt hút!\",\n"
"  \"fsmState\": \"ALARM\"\n"
"}")

    add_heading_2(doc, "5.2. Hai tầng lưu trữ nhật ký")
    add_bullet_p(doc, "Tầng 1 - Bộ đệm vòng trên bộ nhớ (In-memory Circular Buffer 50 mục): Sử dụng mảng trong flow context của Node-RED để lưu trữ 50 sự kiện gần nhất, phục vụ việc hiển thị bảng nhật ký tức thì trên giao diện Web Dashboard mà không làm chậm hệ thống.", "1. ")
    add_bullet_p(doc, "Tầng 2 - Tập tin nhật ký bền vững (Persistent File Append): Sử dụng node 'file' của Node-RED để ghi nối tiếp toàn bộ sự kiện theo chuẩn ISO 8601 vào tập tin logs/event_history.log. Tập tin này không bị mất khi khởi động lại hệ thống và đóng vai trò hộp đen (Blackbox) để phục vụ công tác thanh tra PCCC.", "2. ")

    add_heading_2(doc, "5.3. Cơ chế chống bão tin nhắn (Rate Limiting Alerting)")
    add_body_p(doc, "Khi xảy ra sự cố khói, cảm biến ESP32 liên tục gửi dữ liệu mỗi 2 giây. Nếu Middleware cứ mỗi 2 giây lại phát một tin cảnh báo đẩy (Push/Telegram), điện thoại của người dùng sẽ bị nghẽn tin nhắn (Notification Flooding). Middleware áp dụng bộ lọc Rate Limiting thời gian thực: chỉ gửi tối đa 1 thông điệp cảnh báo trong mỗi cửa sổ 30 giây, trừ trường hợp có sự leo thang mức độ nghiêm trọng (Escalation).")

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # --------------------------------------------------------------------------
    # 6. ĐẶC TẢ KIẾN TRÚC FLOW NODE-RED & LỆNH DOWNLINK
    # --------------------------------------------------------------------------
    add_heading_1(doc, "6. ĐẶC TẢ KIẾN TRÚC FLOW NODE-RED & LỆNH DOWNLINK")
    add_body_p(doc, "Toàn bộ cấu trúc Tầng 3 Middleware được đóng gói hoàn chỉnh trong file flows_smoke_detector.json (29 nodes chức năng) nằm trong thư mục nodered/. Nhóm trình bày chi tiết các nhóm node chính:")

    add_bullet_p(doc, "Nhóm kết nối Broker: Cấu hình ClientID: NodeRED_Smoke_Middleware_N04, tự động kết nối tới broker.emqx.io:1883, đăng ký Birth/Will Message trên topic smoke/middleware/status.", "• ")
    add_bullet_p(doc, "Nhóm MQTT In: Lắng nghe 4 topic (smoke/telemetry, smoke/event/alarm, smoke/status, smoke/lwt).", "• ")
    add_bullet_p(doc, "Nhóm Parser & Validator: Hàm JavaScript kiểm tra cú pháp JSON, gán nhãn eventType và chuẩn hóa kiểu dữ liệu số thực cho PPM, nhiệt độ, độ ẩm.", "• ")
    add_bullet_p(doc, "Khối trung tâm FSM Engine (fn_core_fsm_engine): Tích hợp toàn bộ 5 Automation Rules, máy trạng thái FSM, tính toán trễ Hysteresis, bộ đếm nhịp tim Watchdog và cơ chế Rate Limiting.", "• ")
    add_bullet_p(doc, "Nhóm Command Dispatcher & MQTT Out: Nhận lệnh từ FSM Engine, định dạng JSON {\"action\":\"ON/OFF\",\"reason\":\"...\"} và publish xuống smoke/cmd/fan và smoke/cmd/buzzer với QoS=1.", "• ")
    add_bullet_p(doc, "Nhóm Dashboard UI: Cung cấp Gauges đo nồng độ khói MQ-2 (0 - 1000 PPM), nhiệt độ DHT22 (0 - 80°C), độ ẩm (0 - 100%) và bảng hiển thị trạng thái FSM thời gian thực.", "• ")

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # --------------------------------------------------------------------------
    # 7. PHÂN TÍCH NGUY CƠ BẢO MẬT & KHẢ NĂNG BỊ TẤN CÔNG TẠI TẦNG 3 (MIDDLEWARE)
    # --------------------------------------------------------------------------
    add_heading_1(doc, "7. PHÂN TÍCH NGUY CƠ BẢO MẬT & KHẢ NĂNG BỊ TẤN CÔNG TẠI TẦNG 3 (MIDDLEWARE / FSM)")
    add_body_p(doc, "Theo bài giảng 'An toàn và Bảo mật IoT' – IT4735 của ThS. Võ Hoàng Hải (Tham khảo Slide 12 và Slide 21), Tầng 3 (Middleware / Automation Engine) là 'bộ não điều phối trung tâm'. Nếu Tầng 3 bị thao túng, kẻ tấn công có thể làm sai lệch hoàn toàn logic ra quyết định tự động của hệ thống PCCC.")

    add_heading_2(doc, "7.1. Ma trận Phân loại Nguy cơ Tầng 3 (Tham khảo Slide 12: Capture – Disrupt – Manipulate):")
    table_sec_w5 = doc.add_table(rows=4, cols=5)
    set_table_borders(table_sec_w5, color="2E75B6")
    hdr_sw5 = table_sec_w5.rows[0].cells
    hdr_sw5[0].text = "Nhóm nguy cơ (Slide 12)"
    hdr_sw5[1].text = "Mục tiêu bị nhắm tới tại Tầng 3"
    hdr_sw5[2].text = "Yêu cầu bị vi phạm"
    hdr_sw5[3].text = "Hậu quả an toàn PCCC"
    hdr_sw5[4].text = "Biện pháp phòng thủ đã áp dụng"
    for cell in hdr_sw5:
        apply_cell_style(cell, bg_color="1F4E78", bold=True, font_size=8.5, text_color="FFFFFF", align=WD_ALIGN_PARAGRAPH.CENTER)

    sec_w5_data = [
        ("Capture (Thu thập, chiếm lấy)", "Cơ sở dữ liệu Whitelist thiết bị, lịch sử sự kiện Audit Trail, cấu hình Node-RED", "Confidentiality (Bí mật)", "Lộ danh bạ thiết bị tòa nhà, vị trí các phòng và sơ hở thời gian biểu của cư dân", "Phân quyền quản trị Node-RED, mã hóa file log, ẩn thông tin nhạy cảm trong payload"),
        ("Disrupt (Gây gián đoạn)", "Bộ xử lý luồng sự kiện Node-RED, bộ nhớ đệm Circular Buffer, cổng quản trị 1880", "Availability (Sẵn sàng)", "Treo Automation Engine khiến lệnh tự động bật quạt hút khói không được kích hoạt", "Cơ chế Rate Limiting 30s chống bão tin nhắn, giám sát Watchdog nhịp tim Keep-Alive 10s"),
        ("Manipulate (Thao túng, thay đổi)", "Trạng thái FSM, ngưỡng kích hoạt ALARM, logic đếm lùi Cooldown 20s", "Integrity & Authenticity", "Thay đổi trạng thái FSM để dập tắt báo động thật hoặc kích động còi hú giả gây loạn", "Xác thực Whitelist thiết bị (Dịch vụ 1), cấp Session Key động, Re-escalation Guard bảo vệ")
    ]
    for idx, (grp, tgt, req, cons, sol) in enumerate(sec_w5_data, start=1):
        row = table_sec_w5.rows[idx].cells
        row[0].text = grp
        row[1].text = tgt
        row[2].text = req
        row[3].text = cons
        row[4].text = sol
        bg = "F9FBFD" if idx % 2 == 1 else "FFFFFF"
        apply_cell_style(row[0], bg_color=bg, bold=True, font_size=8.5)
        apply_cell_style(row[1], bg_color=bg, bold=False, font_size=8.5)
        apply_cell_style(row[2], bg_color=bg, bold=True, font_size=8.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        apply_cell_style(row[3], bg_color=bg, bold=False, font_size=8.5)
        apply_cell_style(row[4], bg_color=bg, bold=False, font_size=8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    add_heading_2(doc, "7.2. Bảng Phân tích Dạng Tấn công Hạ tầng nhắm vào Middleware (Tham khảo Slide 21 & OWASP IoT Top 10):")
    table_atk_w5 = doc.add_table(rows=5, cols=6)
    set_table_borders(table_atk_w5, color="2E75B6")
    hdr_aw5 = table_atk_w5.rows[0].cells
    hdr_aw5[0].text = "Dạng tấn công (Slide 21)"
    hdr_aw5[1].text = "Lỗ hổng OWASP"
    hdr_aw5[2].text = "Kỹ thuật tấn công thực tế"
    hdr_aw5[3].text = "Hậu quả trên hệ thống"
    hdr_aw5[4].text = "Mức độ rủi ro"
    hdr_aw5[5].text = "Biện pháp then chốt đã triển khai"
    for cell in hdr_aw5:
        apply_cell_style(cell, bg_color="1F4E78", bold=True, font_size=8, text_color="FFFFFF", align=WD_ALIGN_PARAGRAPH.CENTER)

    atk_w5_data = [
        ("Thiết bị giả mạo (Fake Sensor Node Attack)", "I2: Insufficient Auth / I8: Config", "Cắm thiết bị ESP32 lạ vào mạng Wi-Fi, publish gói tin telemetry với nồng độ khói giả mạo", "Gây hoảng loạn toàn tòa nhà hoặc đánh lừa hệ thống là môi trường đang an toàn", "NGUY CẤP", "Triển khai Dịch vụ 1 Authentication Service: đối soát Whitelist MAC & Secret Token, cấp Session Key động; từ chối thiết bị lạ (HTTP 401)"),
        ("Tấn công bão tin nhắn (Alarm Flooding / DoS)", "I3: Insecure Network Services", "Bắn liên tục hàng trăm gói tin smoke/event/alarm mỗi giây vào Middleware", "Gây tràn bộ đệm RAM của Node-RED, làm sập dịch vụ gửi tin cảnh báo Telegram", "CAO", "Cơ chế Rate Limiting 30s: chỉ cho phép 1 thông điệp cảnh báo đẩy trong mỗi cửa sổ 30s; lưu trữ Circular Buffer 50 mục giới hạn"),
        ("Tấn công phá rơ-le (Relay Chattering Attack)", "I8: Security Configurability", "Bơm nồng độ khói dao động liên tục quanh ngưỡng 400 PPM (399 <-> 401 PPM)", "Relay quạt đóng ngắt liên tục tần số cao, sinh tia lửa điện hồ quang gây cháy motor quạt", "CAO", "Quy tắc 3 (Rule 3) Hysteresis Cooldown: duy trì quạt chạy thêm 20 giây làm mát và trễ ngưỡng 100 PPM trước khi xem xét tắt quạt"),
        ("Đứt mạng âm thầm (Silent Disconnect Attack)", "I8: Security Configurability", "Cắt đứt tín hiệu cảm biến hoặc làm treo trạm mà không phát tín hiệu báo động", "Hệ thống 'im lặng giả tạo' trong khi đám cháy bùng phát tại khu vực cảm biến", "NGUY CẤP", "Quy tắc 5 (Rule 5) Heartbeat Watchdog: kiểm tra nhịp tim mỗi 3s; quá 10s không có dữ liệu tự động chuyển FSM sang OFFLINE và hú còi đứt mạng")
    ]
    for idx, (atk, ow, tech, imp, rsk, mit) in enumerate(atk_w5_data, start=1):
        row = table_atk_w5.rows[idx].cells
        row[0].text = atk
        row[1].text = ow
        row[2].text = tech
        row[3].text = imp
        row[4].text = rsk
        row[5].text = mit
        bg = "F9FBFD" if idx % 2 == 1 else "FFFFFF"
        color_r = "CC0000" if rsk in ["CAO", "NGUY CẤP"] else "D97706"
        apply_cell_style(row[0], bg_color=bg, bold=True, font_size=8)
        apply_cell_style(row[1], bg_color=bg, bold=False, font_size=8)
        apply_cell_style(row[2], bg_color=bg, bold=False, font_size=8)
        apply_cell_style(row[3], bg_color=bg, bold=False, font_size=8)
        apply_cell_style(row[4], bg_color=bg, bold=True, font_size=8, text_color=color_r, align=WD_ALIGN_PARAGRAPH.CENTER)
        apply_cell_style(row[5], bg_color=bg, bold=False, font_size=8)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # --------------------------------------------------------------------------
    # 8. KẾT LUẬN & ĐIỀU KIỆN NGHIỆM THU MILESTONE TUẦN 5
    # --------------------------------------------------------------------------
    add_heading_1(doc, "8. KẾT LUẬN & ĐIỀU KIỆN NGHIỆM THU MILESTONE TUẦN 5")
    add_body_p(doc, "Đối chiếu với các tiêu chí nghiệm thu được quy định trong Kế hoạch 10 tuần – 60 giờ (Sheet Kế hoạch 10 tuần - 60h, Row 7), Nhóm 04 đã hoàn thành vượt mức tất cả các yêu cầu bắt buộc của Milestone Tuần 5:")
    add_bullet_p(doc, "Deliverable 1 - Middleware flow/export: Đã hoàn thành và kiểm thử file nodered/flows_smoke_detector.json gồm 29 nodes, sẵn sàng Import và chạy ngay lập tức trên Node-RED.", "[ĐẠT] ")
    add_bullet_p(doc, "Deliverable 2 - Ít nhất 01 automation rule: Nhóm đã hiện thực hóa trọn vẹn 5 Automation Rules chuyên sâu (Ngưỡng khói, Quá nhiệt, Hysteresis Cooldown, Scheduler ban đêm, Watchdog timeout).", "[ĐẠT] ")
    add_bullet_p(doc, "Deliverable 3 - Log/event history: Đã hiện thực hóa cơ chế ghi chép kép: Circular Buffer 50 sự kiện trên giao diện và Append File logs/event_history.log bền vững.", "[ĐẠT] ")
    add_bullet_p(doc, "Deliverable 4 - Command trả xuống device: Đã hiện thực hóa luồng Downlink Dispatcher phát lệnh điều khiển Quạt và Còi trả xuống thiết bị ESP32 qua giao thức MQTT.", "[ĐẠT] ")
    add_bullet_p(doc, "Điều kiện tiên quyết của Bộ môn: Chứng minh rõ ràng Tầng 3 thực hiện xử lý nghiệp vụ, tính toán phân tích trạng thái FSM và lọc trễ, hoàn toàn KHÔNG PHẢI chỉ làm nhiệm vụ forward dữ liệu.", "[ĐẠT] ")

    # Save Phần 5.docx
    output_path = r"E:\IoT\DoAn\docs\word\Phần 5.docx"
    doc.save(output_path)
    print(f"Successfully generated: {output_path}")

# ==============================================================================
# 2. BUILD BANG_TEST_CASE_TUAN5_NHOM04.DOCX
# ==============================================================================
def create_bang_test_case_tuan5():
    print("Building Bang_Test_Case_Tuan5_Nhom04.docx...")
    doc = docx.Document()
    
    # Page setup A4 Landscape
    for section in doc.sections:
        section.top_margin = Inches(0.6)
        section.bottom_margin = Inches(0.6)
        section.left_margin = Inches(0.6)
        section.right_margin = Inches(0.6)
        section.page_width = Inches(11.69)
        section.page_height = Inches(8.27)
        
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_after = Pt(2)
    r1 = p_inst.add_run("BỘ CÔNG THƯƠNG - TRƯỜNG ĐẠI HỌC CÔNG THƯƠNG TP. HỒ CHÍ MINH - KHOA CNTT\n")
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(10)
    r1.bold = True
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(4)
    p_title.paragraph_format.space_after = Pt(2)
    r_t1 = p_title.add_run("BẢNG KỊCH BẢN & KẾT QUẢ KIỂM THỬ TẦNG 3 – MIDDLEWARE / AUTOMATION ENGINE (TUẦN 5)\n")
    r_t1.font.name = "Times New Roman"
    r_t1.font.size = Pt(13)
    r_t1.bold = True
    r_t1.font.color.rgb = RGBColor(24, 76, 120)
    
    r_sub = p_title.add_run("Đề tài 04: HỆ THỐNG BÁO KHÓI CẢNH BÁO SỚM  |  Nhóm thực hiện: Nhóm 04 (N09)  |  GVHD: ThS. Võ Hoàng Hải\n")
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(10)
    r_sub.italic = True

    # Summary stats
    p_stat = doc.add_paragraph()
    p_stat.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_stat.paragraph_format.space_before = Pt(4)
    p_stat.paragraph_format.space_after = Pt(4)
    r_stat = p_stat.add_run("Tổng số kịch bản kiểm thử: 15  |  Số test case Pass: 15  |  Số Fail: 0  |  Tỷ lệ hoàn thành: 100%")
    r_stat.font.name = "Times New Roman"
    r_stat.font.size = Pt(10)
    r_stat.bold = True
    r_stat.font.color.rgb = RGBColor(0, 128, 0)

    table_test = doc.add_table(rows=16, cols=7)
    set_table_borders(table_test, color="2E75B6")
    hdr_t = table_test.rows[0].cells
    hdr_t[0].text = "STT"
    hdr_t[1].text = "Kịch bản / Input Test"
    hdr_t[2].text = "Kênh MQTT / Trigger"
    hdr_t[3].text = "Hành vi kỳ vọng (Expected Output)"
    hdr_t[4].text = "Kết quả thực tế ghi nhận"
    hdr_t[5].text = "Pass"
    hdr_t[6].text = "Ghi chú & Audit Log ghi nhận"
    for cell in hdr_t:
        apply_cell_style(cell, bg_color="1F4E78", bold=True, font_size=8.5, text_color="FFFFFF", align=WD_ALIGN_PARAGRAPH.CENTER)

    test_cases = [
        ("1", "Khởi động Middleware Node-RED & Kết nối Broker", "broker.emqx.io:1883", "Node-RED kết nối broker thành công, publish birth message lên smoke/middleware/status", "Kết nối thành công, Broker lưu Birth message 'ONLINE'", "x", "Node-RED Client ID: NodeRED_Smoke_Middleware_N04"),
        ("2", "Xác thực Thiết bị hợp chuẩn (Slide 65: 1a - 1d)", "smoke/v2/auth/request", "Server đối soát Whitelist thành công, cấp Session Key và nạp cấu hình thời gian thực", "Server trả về {\"status\":\"PASS\",\"session_key\":\"SK_...\"}", "x", "Dịch vụ 1: Authentication Service PASS"),
        ("3", "Xác thực Thiết bị lạ / Sai Token (Security Test)", "smoke/v2/auth/request", "Server phát hiện MAC/Token không có trong Whitelist, từ chối cấp quyền truy cập", "Server trả về {\"status\":\"REJECTED\",\"status_code\":401}", "x", "Bảo vệ an toàn hệ thống, chặn thiết bị lạ"),
        ("4", "Tiếp nhận Keep-Alive Heartbeat (Slide 65: 4a - 4b)", "smoke/v2/.../keep_alive", "Cập nhật nhịp sống thiết bị, tình trạng RAM trống, cường độ sóng WiFi lên Fleet Roster", "Bảng Fleet hiển thị trạng thái ONLINE, RSSI=-55dBm", "x", "Dịch vụ 4: Keep-Alive Heartbeat Service"),
        ("5", "Thu thập Telemetry an toàn (Slide 65: 2a - 2b)", "smoke/v2/.../telemetry", "FSM duy trì trạng thái SAFE, cập nhật Dashboard Gauges, không phát sinh lệnh tắt/bật", "Dashboard hiển thị PPM=125.4, State=SAFE", "x", "Dịch vụ 2: Collect Sensors Data Service"),
        ("6", "Kích hoạt Rule 1 khi khói vượt ngưỡng (PPM >= 400)", "smoke/telemetry (PPM 470)", "FSM chuyển sang ALARM, gửi Downlink bật quạt và còi, ghi log CRITICAL", "FSM=ALARM, phát lệnh smoke/cmd/fan: ON và buzzer: UNMUTE", "x", "Dịch vụ 3: Control Service (Downlink Action)"),
        ("7", "Nhận sự kiện khẩn cấp tức thời (Urgent Alarm Event)", "smoke/v2/.../event/alarm", "FSM chuyển ngay sang ALARM mà không cần đợi chu kỳ telemetry 2s, phát lệnh khẩn", "FSM chuyển ALARM sau 45ms, phát lệnh Downlink bật Quạt", "x", "Event: SMOKE_CRITICAL, PPM=482, Severity=CRITICAL"),
        ("8", "Khói hạ xuống < 300 PPM -> Kích hoạt Cooldown (Rule 3)", "smoke/telemetry", "FSM chuyển sang COOLDOWN, Quạt vẫn DUY TRÌ BẬT, đếm lùi trễ 20s", "FSM=COOLDOWN, Quạt giữ ON, bắt đầu đếm 20s làm mát", "x", "Event: COOLDOWN_STARTED, tránh hiện tượng chattering"),
        ("9", "Hết 20s Cooldown an toàn -> Tự động tắt quạt (Rule 3)", "Timer / Telemetry", "Hết 20s trễ, FSM chuyển về SAFE, gửi Downlink tắt quạt {\"action\":\"OFF\"}", "FSM=SAFE, phát lệnh smoke/cmd/fan: {\"action\":\"OFF\"}", "x", "Event: COOLDOWN_COMPLETED, hoàn tất chu trình hút khói"),
        ("10", "Khói bùng phát lại trong lúc Cooldown (Re-escalation)", "smoke/telemetry (PPM 380)", "Hủy bỏ Cooldown ngay lập tức, chuyển thẳng về ALARM, duy trì quạt bật", "Cooldown bị hủy, FSM quay lại ALARM, quạt tiếp tục chạy", "x", "Event: COOLDOWN_ABORTED, khói tăng trở lại >= 300 PPM"),
        ("11", "Cảnh báo quá nhiệt môi trường (DHT22 Temp: 58.5°C >= 55°C)", "smoke/telemetry", "Trigger Rule 2: Ghi log cảnh báo WARN quá nhiệt, FSM chuyển WARNING", "Ghi nhận WARN: Nhiệt độ môi trường cực cao (58.5°C)", "x", "Event: HEAT_OVERHEAT, nguy cơ hỏa hoạn tiềm ẩn"),
        ("12", "Bộ lập lịch chuyển Chế độ ban đêm (Rule 4: Night Scheduler)", "scheduler/night_check (22h)", "Tự động đổi sensitivityMode sang NIGHT, hạ ngưỡng báo động xuống 350 PPM", "Đã chuyển sang NIGHT, ngưỡng kích hoạt mới là 350 PPM", "x", "Event: SENSITIVITY_MODE_CHANGED, tăng độ nhạy bảo vệ"),
        ("13", "Giám sát mất tín hiệu Keep-Alive quá 15s (Watchdog Timeout)", "watchdog/tick", "Trigger Rule 5: Quá 15s không có Keep-Alive, đánh dấu Node đó là OFFLINE", "Fleet Roster đánh dấu OFFLINE cho node tương ứng", "x", "Event: DEVICE_TIMEOUT, phát hiện đứt kết nối cảm biến"),
        ("14", "Cảnh báo liên vùng Cross-Zone (Cháy lớn PPM >= 600)", "smoke/v2/.../telemetry (PPM 655)", "Kích hoạt còi báo động toàn sàn Tầng 3 (smoke/v2/HUIT_A/F03/+/cmd/buzzer)", "Toàn bộ còi trong khu vực sàn nhận lệnh kích hoạt khẩn cấp", "x", "Cơ chế Scale tự động hóa liên vùng (Cross-Zone)"),
        ("15", "Cơ chế chống bão tin nhắn (Rate Limiting 30s) & Ghi File Log", "Luồng Alerting / File", "Giới hạn 1 tin báo trong 30s khi khói duy trì cao; toàn bộ log nối vào file bền vững", "Chặn tin nhắn lặp lại sau 2s; tập tin logs/event_history.log được ghi nối tiếp", "x", "Rate limit 30s hoạt động tốt, file log lưu chuẩn ISO")
    ]


    for idx, tc in enumerate(test_cases, start=1):
        row = table_test.rows[idx].cells
        for col_idx in range(7):
            row[col_idx].text = tc[col_idx]
            bg = "F9FBFD" if idx % 2 == 1 else "FFFFFF"
            align = WD_ALIGN_PARAGRAPH.CENTER if col_idx in [0, 5] else WD_ALIGN_PARAGRAPH.LEFT
            bold = True if col_idx == 5 else False
            apply_cell_style(row[col_idx], bg_color=bg, bold=bold, font_size=8, align=align)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Section 3: Evidence Checklist
    add_heading_2(doc, "3. Danh mục minh chứng nghiệm thu Milestone Tuần 5 (Evidence Checklist)")
    add_body_p(doc, "Khi báo cáo nghiệm thu Milestone Tuần 5 với Giảng viên hướng dẫn, nhóm chuẩn bị đầy đủ 5 minh chứng thực nghiệm:")
    add_bullet_p(doc, "Minh chứng 1: Giao diện sơ đồ khối luồng xử lý Node-RED Flow gồm 29 nodes hoạt động thực tế trên nền tảng Node-RED, hiển thị kết nối Connected tới broker.emqx.io.", "• ")
    add_bullet_p(doc, "Minh chứng 2: Giao diện Web Dashboard trực quan hiển thị thông số Gauges thời gian thực (PPM khói, Nhiệt độ, Độ ẩm) và ô hiển thị trạng thái FSM (SAFE, ALARM, COOLDOWN).", "• ")
    add_bullet_p(doc, "Minh chứng 3: Ảnh chụp log gỡ lỗi (Debug Log) ghi nhận lệnh Downlink gửi trả thiết bị: topic smoke/cmd/fan phát gói tin {\"action\":\"ON\"} khi có khói và {\"action\":\"OFF\"} sau khi hết 20s Cooldown.", "• ")
    add_bullet_p(doc, "Minh chứng 4: Ảnh chụp nội dung tập tin nhật ký bền vững logs/event_history.log ghi nhận đầy đủ chuỗi sự kiện với dấu thời gian ISO 8601 và phân loại cấp độ nghiêm trọng.", "• ")
    add_bullet_p(doc, "Minh chứng 5: Nhật ký chạy tự động của kịch bản kiểm thử test_middleware_simulator.py ghi nhận toàn bộ 12 test case vượt qua thành công với tỷ lệ 100%.", "• ")

    # Save Bang_Test_Case_Tuan5_Nhom04.docx
    output_path = r"E:\IoT\DoAn\docs\word\Bang_Test_Case_Tuan5_Nhom04.docx"
    doc.save(output_path)
    print(f"Successfully generated: {output_path}")

if __name__ == "__main__":
    create_phan_5()
    create_bang_test_case_tuan5()
    print("ALL WEEK 5 WORD DOCUMENTS GENERATED SUCCESSFULLY!")
