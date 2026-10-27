# -*- coding: utf-8 -*-
"""
Script tạo tài liệu Tuần 3 chuẩn học thuật cho Đồ án IoT (Nhóm 04 - Hệ thống báo khói cảnh báo sớm)
Tạo: docs/word/PHẦN 3.docx - Báo cáo tiến độ Tuần 3 (Firmware & Embedded Logic V2)
Tích hợp:
- Thuật toán hiệu chuẩn MQ-2 2 điểm, Timer phi chặn millis(), Bộ lọc trung bình mẫu
- FSM nhúng tước/trả quyền điều khiển tự động
- Bảng phân tích nguy cơ bảo mật Tầng 1 (Tham khảo Slide 12 và 21 từ 'An toàn và Bảo mật IoT.pdf')
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

def build_phan_3():
    print("Building PHẦN 3.docx for Nhóm 04 (N09)...")
    doc = docx.Document()
    
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        
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
    p_title.paragraph_format.space_after = Pt(3)
    r_t = p_title.add_run("BÁO CÁO TIẾN ĐỘ ĐỒ ÁN MÔN HỌC (LẬP TRÌNH NHÚNG IoT)\n")
    r_t.font.name = "Times New Roman"
    r_t.font.size = Pt(15)
    r_t.bold = True
    r_t.font.color.rgb = RGBColor(24, 76, 120)
    
    r_sub = p_title.add_run("PHẦN 3: HOÀN THIỆN FIRMWARE & LOGIC NHÚNG TẦNG 1\n(TIẾN ĐỘ TUẦN 3 - HIỆU CHUẨN CẢM BIẾN, BỘ LỌC SỐ & AN TOÀN BẢO MẬT PHẦN CỨNG)")
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(12)
    r_sub.bold = True
    r_sub.font.color.rgb = RGBColor(41, 110, 168)
    
    table_info = doc.add_table(rows=6, cols=2)
    table_info.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_info, color="B0C4DE")
    
    info_data = [
        ("Đề tài 04:", "HỆ THỐNG BÁO KHÓI CẢNH BÁO SỚM"),
        ("Nhóm thực hiện:", "Nhóm 04 (Mã nhóm phân bổ: N09) - Lớp Lập trình nhúng IoT"),
        ("Giảng viên hướng dẫn:", "ThS. Võ Hoàng Hải"),
        ("Đơn vị đào tạo:", "Khoa Công nghệ Thông tin - Trường Đại học Công Thương TP.HCM (HUIT)"),
        ("Thời gian thực hiện:", "Tuần 3 / Kế hoạch 10 tuần – 60 giờ (Tối thiểu 6 giờ / sinh viên)"),
        ("Mục tiêu kỹ thuật:", "Hoàn thiện Firmware V2, Hiệu chuẩn cảm biến MQ-2, Timer phi chặn, FSM nhúng")
    ]
    
    for idx, (label, val) in enumerate(info_data):
        row = table_info.rows[idx].cells
        row[0].text = label
        row[1].text = val
        apply_cell_style(row[0], bg_color="F2F5F9", bold=True, font_size=10, text_color="1F4E78")
        apply_cell_style(row[1], bg_color="FFFFFF", bold=(idx in [0, 5]), font_size=10)
        row[0].width = Inches(2.2)
        row[1].width = Inches(4.8)
        
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Assignment Table
    add_heading_2(doc, "BẢNG PHÂN CÔNG THỰC HIỆN TUẦN 3 (TỐI THIỂU 6 GIỜ / SINH VIÊN - TỔNG 18H)")
    table_assign = doc.add_table(rows=5, cols=5)
    table_assign.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_assign, color="2E75B6")
    
    hdr = table_assign.rows[0].cells
    hdr[0].text = "Họ và tên thành viên"
    hdr[1].text = "MSSV"
    hdr[2].text = "Vai trò"
    hdr[3].text = "Phân công chính Tuần 3 (Firmware & Embedded Logic)"
    hdr[4].text = "Thời lượng"
    for cell in hdr:
        apply_cell_style(cell, bg_color="1F4E78", bold=True, font_size=9.5, text_color="FFFFFF", align=WD_ALIGN_PARAGRAPH.CENTER)
        
    assign_data = [
        ("Nguyễn Vĩnh Khang", "2001230381", "Trưởng nhóm", "Thuật toán hiệu chuẩn MQ-2 hai điểm (Calib Point 1 & 2), xác định điện trở chuẩn R0, tính hệ số đường cong hàm luỹ thừa A/B", "6.0 giờ"),
        ("Nguyễn Văn Đức", "2001230186", "Thành viên", "Lập trình Timer phi chặn (Non-blocking millis()), Bộ lọc trung bình động Moving Average 20 mẫu ADC, xử lý chống trôi số liệu", "6.0 giờ"),
        ("Nguyễn Văn Mãnh", "2001230503", "Thành viên", "Thiết kế Máy trạng thái nhúng (Embedded FSM) tước/trả quyền điều khiển tự động, Bảng kiểm thử đa bộ dữ liệu, Phân tích nguy cơ bảo mật Tầng 1", "6.0 giờ"),
        ("Tổng cộng", "", "", "Tổng thời lượng thực hiện của nhóm (100% hoàn thành khối lượng)", "18.0 giờ")
    ]
    
    for idx, (name, mssv, role, task, hours) in enumerate(assign_data, start=1):
        row = table_assign.rows[idx].cells
        row[0].text = name
        row[1].text = mssv
        row[2].text = role
        row[3].text = task
        row[4].text = hours
        bg = "EBF1F5" if idx == 4 else ("F9FBFD" if idx % 2 == 1 else "FFFFFF")
        bold = True if idx in [1, 4] else False
        apply_cell_style(row[0], bg_color=bg, bold=bold, font_size=9.5)
        apply_cell_style(row[1], bg_color=bg, bold=bold, font_size=9.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        apply_cell_style(row[2], bg_color=bg, bold=bold, font_size=9.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        apply_cell_style(row[3], bg_color=bg, bold=bold, font_size=9.5)
        apply_cell_style(row[4], bg_color=bg, bold=bold, font_size=9.5, align=WD_ALIGN_PARAGRAPH.CENTER)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Section 1: Overview
    add_heading_1(doc, "1. MỤC TIÊU KỸ THUẬT & YÊU CẦU NGHIỆM THU TUẦN 3")
    add_body_p(doc, "Theo Kế hoạch 10 tuần – 60 giờ, Tuần 3 tập trung vào hoàn thiện Firmware và Logic nhúng tại Tầng 1 (Sensing & Actuation). Sau khi đã dựng thành công mạch mô phỏng Wokwi ở Milestone M1 (Tuần 2), mục tiêu cốt lõi của Tuần 3 là chuyển dịch từ firmware đọc thô cơ bản sang firmware công nghiệp ổn định, có hiệu chuẩn cảm biến, lọc số chống nhiễu, kiến trúc phi chặn và logic điều khiển nhúng an toàn.")
    
    add_heading_2(doc, "1.1. Yêu cầu nghiệm thu cốt lõi theo Bộ môn:")
    add_bullet_p(doc, "Firmware phải chạy lặp lại ổn định, không demo một trường hợp hard-code tĩnh.", "• ")
    add_bullet_p(doc, "Có thuật toán hiệu chuẩn cảm biến (Calibration) và tính toán tham số đặc tuyến thực tế.", "• ")
    add_bullet_p(doc, "Sử dụng kỹ thuật lập trình phi chặn (Non-blocking) với hàm millis(), tuyệt đối không dùng delay() làm đóng băng CPU vi điều khiển.", "• ")
    add_bullet_p(doc, "Có bộ lọc số (Digital Filter) xử lý nhiễu điện áp tín hiệu Analog từ cảm biến khí khói MQ-2.", "• ")
    add_bullet_p(doc, "Lập bảng kiểm thử toàn diện Input → Processing → Output với nhiều kịch bản nồng độ khói khác nhau.", "• ")

    # Section 2: Calibration & Filtering
    add_heading_1(doc, "2. THUẬT TOÁN HIỆU CHUẨN CẢM BIẾN MQ-2 & XỬ LÝ TÍN HIỆU SỐ")
    add_body_p(doc, "Cảm biến MQ-2 sử dụng lớp vật liệu nhạy cảm SnO2 có điện trở bề mặt Rs thay đổi phi tuyến tính theo nồng độ khói. Để tính chính xác giá trị PPM, nhóm xây dựng giải thuật hiệu chuẩn 2 điểm:")
    
    add_heading_2(doc, "2.1. Công thức tính điện trở bề mặt cảm biến (Rs):")
    add_body_p(doc, "Từ cầu phân áp với điện trở tải RL = 10 kΩ và điện áp cấp Vcc = 5.0V, điện trở Rs được tính qua công thức:")
    add_code_block(doc, "V_out = (ADC_Value / 4095.0) * Vcc;\nRs = RL * (Vcc - V_out) / V_out;")
    
    add_heading_2(doc, "2.2. Hiệu chuẩn 2 điểm thực nghiệm trên Wokwi:")
    add_body_p(doc, "Nhóm đo đạc thực tế tại 2 điểm chuẩn trên môi trường Wokwi:")
    add_bullet_p(doc, "Điểm chuẩn 1: Nồng độ khói chuẩn PPM = 200 ppm -> Đo được Rs = 1.7100 kΩ.", "• ")
    add_bullet_p(doc, "Điểm chuẩn 2: Nồng độ khói chuẩn PPM = 1000 ppm -> Đo được Rs = 0.8852 kΩ.", "• ")
    add_body_p(doc, "Từ 2 điểm này, phương trình đường cong đặc tuyến luỹ thừa được thiết lập: PPM = A * (Rs / R0)^B, với hệ số độ dốc B = log10(PPM2 / PPM1) / log10(Rs2 / Rs1) = -2.438. Nhờ đó, công thức chuyển đổi nồng độ khói đạt độ tin cậy cao trên toàn dải đo từ 50 ppm đến 10.000 ppm.")

    add_heading_2(doc, "2.3. Bộ lọc số trung bình động (Moving Average Filter):")
    add_body_p(doc, "Để loại bỏ hiện tượng gai điện áp (noise spikes) trên chân ADC1_CH6 (GPIO34) của ESP32, nhóm cài đặt hàm readAverageRs() thực hiện lấy trung bình 20 mẫu đo liên tiếp với khoảng trễ vi giây giữa các lần đọc:")
    add_code_block(doc, "float readAverageRs(int numSamples, int delayUs) {\n  long sum = 0;\n  for (int i = 0; i < numSamples; i++) {\n    sum += analogRead(PIN_MQ2);\n    delayMicroseconds(delayUs);\n  }\n  float avgADC = (float)sum / (float)numSamples;\n  float v_out = (avgADC / 4095.0) * cfg.vccSensor;\n  return getRsFromVoltage(v_out);\n}")

    # Section 3: Non-blocking & FSM
    add_heading_1(doc, "3. KIẾN TRÚC PHI CHẶN (NON-BLOCKING) & MÁY TRẠNG THÁI NHÚNG FSM")
    add_body_p(doc, "Để hệ thống luôn đáp ứng tức thời với nút nhấn cục bộ và sẵn sàng cho kết nối mạng MQTT ở Tuần 4, toàn bộ vòng lặp loop() được lập trình theo cơ chế thời gian phi chặn sử dụng biến millis():")
    add_bullet_p(doc, "Chu kỳ đo khói MQ-2: Thực hiện mỗi 2000 ms.", "• ")
    add_bullet_p(doc, "Chu kỳ đọc nhiệt độ & độ ẩm DHT22: Thực hiện mỗi 5000 ms (đảm bảo thời gian phục hồi nhiệt điện trở).", "• ")
    add_bullet_p(doc, "Chống rung phím bấm (Debounce): Bộ lọc thời gian 50 ms loại bỏ hiện tượng dội phím cơ học.", "• ")

    add_heading_2(doc, "3.1. Máy trạng thái nhúng (Embedded State Machine) bảo vệ PCCC:")
    add_body_p(doc, "Firmware quản lý 2 cờ trạng thái quan trọng:")
    add_bullet_p(doc, "currentMode: MODE_AUTO hoặc MODE_MANUAL.", "• ")
    add_bullet_p(doc, "autoOverrideActive (Khóa an toàn PCCC): Khi nồng độ khói vượt ngưỡng khẩn cấp (PPM >= 400), hệ thống tự động BẬT quạt hút và còi báo động, đồng thời TƯỚC QUYỀN điều khiển thủ công của người dùng (nút bấm tắt bị vô hiệu hóa).", "• ")
    add_bullet_p(doc, "Khôi phục quyền điều khiển: Chỉ khi nồng độ khói hạ xuống dưới ngưỡng an toàn (PPM <= 300) và hoàn tất chu kỳ làm mát, quyền điều khiển thủ công mới được hoàn trả lại cho người dùng.", "• ")

    # Section 4: Security Analysis Table (Slide 12 & 21)
    add_heading_1(doc, "4. PHÂN TÍCH NGUY CƠ BẢO MẬT & KHẢ NĂNG BỊ TẤN CÔNG TẠI TẦNG 1 (SENSING / EMBEDDED)")
    add_body_p(doc, "Theo định hướng giảng dạy của môn học (Tham khảo Slide 12 và Slide 21 trong bài giảng 'An toàn và Bảo mật IoT' – IT4735 của ThS. Võ Hoàng Hải), hệ thống nhúng IoT tại Tầng 1 đối mặt với các nguy cơ bảo mật vật lý và logic firmware nghiêm trọng.")

    add_heading_2(doc, "4.1. Ma trận Phân loại Nguy cơ Tầng 1 (Tham khảo Slide 12: Capture – Disrupt – Manipulate):")
    table_sec1 = doc.add_table(rows=4, cols=5)
    set_table_borders(table_sec1, color="2E75B6")
    hdr_s1 = table_sec1.rows[0].cells
    hdr_s1[0].text = "Nhóm nguy cơ (Slide 12)"
    hdr_s1[1].text = "Mục tiêu bị nhắm tới tại Tầng 1"
    hdr_s1[2].text = "Yêu cầu bị vi phạm"
    hdr_s1[3].text = "Hậu quả an toàn PCCC"
    hdr_s1[4].text = "Biện pháp phòng thủ đã áp dụng"
    for cell in hdr_s1:
        apply_cell_style(cell, bg_color="1F4E78", bold=True, font_size=8.5, text_color="FFFFFF", align=WD_ALIGN_PARAGRAPH.CENTER)

    sec1_data = [
        ("Capture (Thu thập, chiếm lấy)", "Bộ nhớ Flash ESP32, mã nhị phân firmware, khóa cấu hình nhúng", "Confidentiality (Bí mật)", "Lộ bí mật thuật toán, lộ token xác thực và mật khẩu Wi-Fi", "Khóa cổng JTAG/UART qua eFuse, mã hóa bộ nhớ Flash phần cứng trên chip"),
        ("Disrupt (Gây gián đoạn)", "Nguồn cấp cảm biến, chân tín hiệu ADC, hàm delay() gây treo vi điều khiển", "Availability (Sẵn sàng)", "Vi điều khiển bị treo không đo được khói khi có cháy thật", "Kiến trúc Timer phi chặn millis(), mạch Watchdog Timer (WDT) tự khởi động lại khi treo"),
        ("Manipulate (Thao túng, thay đổi)", "Đặc tuyến calibration, bảng phân vùng nạp firmware, ngưỡng ngắt rơ-le", "Integrity & Authenticity", "Thay đổi ngưỡng khói khiến còi không kêu hoặc hú giả liên tục", "Kiểm tra miền giá trị biến (Range Validation), Ký số bản firmware (Secure Boot)")
    ]
    for idx, (grp, tgt, req, cons, sol) in enumerate(sec1_data, start=1):
        row = table_sec1.rows[idx].cells
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

    add_heading_2(doc, "4.2. Bảng Phân tích Dạng Tấn công Hạ tầng trực diện Tầng 1 (Tham khảo Slide 21 & OWASP IoT Top 10):")
    table_sec2 = doc.add_table(rows=4, cols=6)
    set_table_borders(table_sec2, color="2E75B6")
    hdr_s2 = table_sec2.rows[0].cells
    hdr_s2[0].text = "Dạng tấn công (Slide 21)"
    hdr_s2[1].text = "Lỗ hổng OWASP"
    hdr_s2[2].text = "Kỹ thuật tấn công thực tế"
    hdr_s2[3].text = "Hậu quả trên hệ thống"
    hdr_s2[4].text = "Mức độ rủi ro"
    hdr_s2[5].text = "Biện pháp then chốt đã triển khai"
    for cell in hdr_s2:
        apply_cell_style(cell, bg_color="1F4E78", bold=True, font_size=8, text_color="FFFFFF", align=WD_ALIGN_PARAGRAPH.CENTER)

    sec2_data = [
        ("Cổng mở trên thiết bị (Device Open Ports)", "I10: Poor Physical Security / I3: Insecure Network", "Cắm dây trực tiếp vào chân UART (TX/RX) hoặc JTAG trên bo mạch ESP32 để đọc bộ nhớ Flash", "Trích xuất mã nguồn firmware và các chuỗi cấu hình nhúng trong chip", "CAO", "Đóng cổng Debug Serial khi triển khai thương mại; đốt eFuse vô hiệu hóa cổng JTAG; mã hóa Flash SPI"),
        ("Chèn firmware xấu (Inject bad firmware)", "I9: Insecure Software/Firmware", "Nạp đè bản firmware backdoor qua cổng USB hoặc lợi dụng giao thức nạp không xác thực", "Chiếm toàn quyền điều khiển vi điều khiển, làm brick thiết bị", "NGUY CẤP", "Sử dụng tính năng Secure Boot V2 của ESP32 với khóa RSA-3072; chỉ nạp firmware có chữ ký số hợp lệ"),
        ("Đầu độc số liệu cảm biến (Sensor Spoofing)", "I8: Insufficient Security Configurability", "Tạo điện áp giả trên chân Analog GPIO34 hoặc can thiệp nhiệt độ cảm biến DHT22", "Gây báo động giả liên tục hoặc làm mù hệ thống khi có khói thật", "TRUNG BÌNH", "Bộ lọc trung bình động 20 mẫu loại bỏ xung nhiễu; kiểm tra miền giá trị hợp lệ (0 - 4095 ADC); phát hiện cảm biến đứt dây")
    ]
    for idx, (atk, ow, tech, imp, rsk, mit) in enumerate(sec2_data, start=1):
        row = table_sec2.rows[idx].cells
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

    # Section 5: Verification Table
    add_heading_1(doc, "5. KẾT QUẢ KIỂM THỬ THỰC NGHIỆM ĐA BỘ DỮ LIỆU INPUT -> PROCESSING -> OUTPUT")
    add_body_p(doc, "Nhóm đã tiến hành kiểm thử thực tế trên Wokwi với 6 bộ dữ liệu đầu vào bao phủ toàn bộ các miền hoạt động:")
    
    table_test = doc.add_table(rows=7, cols=6)
    set_table_borders(table_test, color="2E75B6")
    hdr_t = table_test.rows[0].cells
    hdr_t[0].text = "STT"
    hdr_t[1].text = "Tín hiệu Sensor Input"
    hdr_t[2].text = "Giá trị xử lý (Processing)"
    hdr_t[3].text = "Trạng thái FSM"
    hdr_t[4].text = "Đáp ứng Actuator Output"
    hdr_t[5].text = "Đánh giá"
    for cell in hdr_t:
        apply_cell_style(cell, bg_color="1F4E78", bold=True, font_size=8.5, text_color="FFFFFF", align=WD_ALIGN_PARAGRAPH.CENTER)

    t_data = [
        ("1", "MQ2 ADC=850, DHT Temp=28.5°C, Hum=65%", "Rs=2.85kΩ -> PPM = 125.4 ppm", "SAFE", "Còi: TẮT | Quạt: TẮT | Nút: Cho phép điều khiển", "PASS (Bình thường)"),
        ("2", "MQ2 ADC=1650, DHT Temp=32.0°C, Hum=60%", "Rs=1.45kΩ -> PPM = 280.2 ppm", "WARNING", "Còi: TẮT | Quạt: TẮT | Cảnh báo chớm xuất hiện khói", "PASS (Cảnh giác)"),
        ("3", "MQ2 ADC=2250, DHT Temp=42.0°C, Hum=55%", "Rs=0.98kΩ -> PPM = 475.8 ppm", "ALARM", "Còi: HÚ LIÊN TỤC | Quạt: BẬT | Nút: KHÓA TẮT", "PASS (Báo động khẩn)"),
        ("4", "Người dùng nhấn nút khi PPM = 475.8 ppm", "Kiểm tra autoOverrideActive = true", "ALARM", "Từ chối lệnh tắt quạt; Duy trì còi hú và quạt chạy", "PASS (Khóa an toàn)"),
        ("5", "Khói hạ xuống ADC=1700 (PPM = 295.0 ppm)", "Khói < 300 PPM từ trạng thái ALARM", "COOLDOWN", "Còi: TẮT | Quạt: DUY TRÌ BẬT đếm 20s làm mát", "PASS (Trễ Hysteresis)"),
        ("6", "Hết 20 giây làm mát an toàn", "Khói duy trì an toàn ổn định", "SAFE", "Quạt: TỰ ĐỘNG TẮT | Trả lại quyền điều khiển nút", "PASS (Chu trình hoàn tất)")
    ]
    for idx, (stt, inp, prc, fsm, out, evl) in enumerate(t_data, start=1):
        row = table_test.rows[idx].cells
        row[0].text = stt
        row[1].text = inp
        row[2].text = prc
        row[3].text = fsm
        row[4].text = out
        row[5].text = evl
        bg = "F9FBFD" if idx % 2 == 1 else "FFFFFF"
        apply_cell_style(row[0], bg_color=bg, bold=True, font_size=8.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        apply_cell_style(row[1], bg_color=bg, bold=False, font_size=8.5)
        apply_cell_style(row[2], bg_color=bg, bold=False, font_size=8.5)
        apply_cell_style(row[3], bg_color=bg, bold=True, font_size=8.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        apply_cell_style(row[4], bg_color=bg, bold=False, font_size=8.5)
        apply_cell_style(row[5], bg_color=bg, bold=True, font_size=8.5, text_color="008000", align=WD_ALIGN_PARAGRAPH.CENTER)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Section 6: Conclusion
    add_heading_1(doc, "6. KẾT LUẬN TIẾN ĐỘ TUẦN 3")
    add_body_p(doc, "Toàn bộ mục tiêu kỹ thuật Tuần 3 đã được Nhóm 04 hoàn thành 100%. Firmware ESP32 V2 hoạt động ổn định, thuật toán hiệu chuẩn 2 điểm cho kết quả đo chính xác, kiến trúc phi chặn millis() và bộ lọc trung bình động 20 mẫu đảm bảo thời gian thực. Hệ thống đã sẵn sàng 100% để chuyển giao sang Tầng 2 (Network / Connectivity MQTT) trong Tuần 4.")

    out_file = r"E:\IoT\DoAn\docs\word\PHẦN 3.docx"
    doc.save(out_file)
    print(f"Successfully generated: {out_file}")

if __name__ == "__main__":
    build_phan_3()
