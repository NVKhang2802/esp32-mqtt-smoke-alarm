# -*- coding: utf-8 -*-
"""
Script tái khởi tạo toàn diện bộ slide PowerPoint 8 Slides Chuẩn Hóa
Đề tài: Hệ Thống Báo Khói Cảnh Báo Sớm - Nhóm 04 (N09) - HUIT
GVHD: ThS. Võ Hoàng Hải
Ghi đè trực tiếp vào file: docs/pptx/Bao_Cao_He_Thong_IoT_4_Slides_Nhom04_Chuan.pptx (Không tạo backup)

Cấu trúc 8 slide hoàn chỉnh theo Datasheet thực tế & Cỡ chữ tối ưu máy chiếu:
- Slide 1: Trang bìa (Cover Slide, Nhóm 04, Lớp N09, 3 thành viên MSSV & 3 Part khái quát)
- Slide 2: Part 1 - Device (ESP32) — Kỹ Thuật Phần Cứng Theo Datasheet, Mạch Phân Áp AOUT & Firmware FreeRTOS FSM
- Slide 3: Part 1 - Device (ESP32) — Bảng BOM Vật Tư Phần A (Vi điều khiển, Cảm biến, Chấp hành & Nguồn)
- Slide 4: Part 1 - Device (ESP32) — Cơ Khí Lắp Ráp & Bảng BOM Vật Tư Phần B (Vỏ hộp ABS IP54, Ốc vít & ~720k)
- Slide 5: Part 2 - MQTT Services on Server — Kiến Trúc Topic Phân Cấp, Rationale & 4 Microservices
- Slide 6: Tích Hợp Hệ Thống — Sơ Đồ Luồng Dữ Liệu Hai Chiều & Khóa An Toàn PCCC (Safety Interlock Override)
- Slide 7: Part 3 - Web Server App — 4 Trụ Cột Nền Tảng (Representation, Management, GUI, Analysis)
- Slide 8: Kết Quả Thực Nghiệm — Benchmark Độ Trễ RTT, Ma Trận 16 Test Cases Tích Hợp Pass 100% & M4
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ==============================================================================
# BẢNG MÀU CÔNG NGHỆ CHUẨN KỸ THUẬT (TECH & SAFETY PALETTE)
# ==============================================================================
NAVY_PRIMARY     = RGBColor(26, 54, 93)     # #1A365D - Xanh navy chủ đạo
NAVY_DARK        = RGBColor(15, 23, 42)     # #0F172A - Nền navy tối cho bìa
TECH_BLUE        = RGBColor(37, 99, 235)    # #2563EB - Xanh công nghệ
TECH_BLUE_LIGHT  = RGBColor(239, 246, 255) # #EFF6FF - Nền thẻ xanh nhạt
TECH_BLUE_BORDER = RGBColor(191, 219, 254) # #BFDBFE - Viền xanh nhạt
CYAN_ACCENT      = RGBColor(6, 182, 212)    # #06B6D4 - Điểm nhấn Cyan
AMBER_GOLD       = RGBColor(245, 158, 11)   # #F59E0B - Điểm nhấn vàng cam
SLATE_DARK       = RGBColor(30, 41, 59)     # #1E293B - Chữ chính đậm
SLATE_MUTED      = RGBColor(100, 116, 139)  # #64748B - Chữ phụ mờ
BG_LIGHT         = RGBColor(248, 250, 252)  # #F8FAFC - Nền slide
CARD_BG          = RGBColor(255, 255, 255)  # Trắng
CARD_BORDER      = RGBColor(226, 232, 240)  # #E2E8F0 - Viền thẻ
ROW_ALT          = RGBColor(248, 250, 252)  # Nền hàng xen kẽ
ALARM_RED        = RGBColor(220, 38, 38)    # #DC2626 - Đỏ cảnh báo PCCC
SUCCESS_GREEN    = RGBColor(22, 163, 74)    # #16A34A - Xanh lá an toàn

FONT_HEADING = "Arial"
FONT_BODY    = "Arial"

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs

def add_header(slide, category_text, title_text):
    """Tạo thanh tiêu đề chuẩn mực, không bị đè chữ hay tràn viền"""
    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.08))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = TECH_BLUE
    top_bar.line.fill.background()

    cat_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.18), Inches(9.2), Inches(0.30))
    cat_box.fill.solid()
    cat_box.fill.fore_color.rgb = TECH_BLUE_LIGHT
    cat_box.line.color.rgb = TECH_BLUE_BORDER
    cat_box.line.width = Pt(1)
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    p_c = tf_c.paragraphs[0]
    p_c.text = category_text.upper()
    p_c.font.name = FONT_HEADING
    p_c.font.size = Pt(9.2)
    p_c.font.bold = True
    p_c.font.color.rgb = TECH_BLUE

    title_box = slide.shapes.add_textbox(Inches(0.75), Inches(0.48), Inches(11.8), Inches(0.50))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = Inches(0.05)
    tf_t.margin_top = Inches(0.02)
    tf_t.margin_bottom = Inches(0.02)
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(16.5)
    p_t.font.bold = True
    p_t.font.color.rgb = NAVY_PRIMARY

def add_footer(slide, current_idx, total_slides=8):
    """Tạo chân trang chuẩn mực báo cáo"""
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(7.08), Inches(11.733), Inches(0.015))
    line.fill.solid()
    line.fill.fore_color.rgb = RGBColor(226, 232, 240)
    line.line.fill.background()

    tb_left = slide.shapes.add_textbox(Inches(0.8), Inches(7.10), Inches(9.0), Inches(0.32))
    tf_l = tb_left.text_frame
    p_l = tf_l.paragraphs[0]
    p_l.text = "IT4735 - IoT & Ứng Dụng • Đề tài: Hệ Thống Báo Khói Cảnh Báo Sớm • Nhóm 04 (Lớp N09) • HUIT"
    p_l.font.name = FONT_BODY
    p_l.font.size = Pt(8.5)
    p_l.font.color.rgb = SLATE_MUTED

    tb_right = slide.shapes.add_textbox(Inches(10.5), Inches(7.10), Inches(2.0), Inches(0.32))
    tf_r = tb_right.text_frame
    p_r = tf_r.paragraphs[0]
    p_r.alignment = PP_ALIGN.RIGHT
    p_r.text = f"Slide {current_idx:02d} / {total_slides:02d}"
    p_r.font.name = FONT_BODY
    p_r.font.size = Pt(8.5)
    p_r.font.bold = True
    p_r.font.color.rgb = TECH_BLUE

def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER, border_width=1):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(border_width)
    else:
        card.line.fill.background()
    return card

def format_cell(cell, text, font_size=9.2, bold=False, color=SLATE_DARK, bg_color=None, align=PP_ALIGN.LEFT):
    cell.text = text
    if bg_color:
        cell.fill.solid()
        cell.fill.fore_color.rgb = bg_color
    cell.margin_left = Inches(0.06)
    cell.margin_right = Inches(0.06)
    cell.margin_top = Inches(0.015)
    cell.margin_bottom = Inches(0.015)
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    for p in cell.text_frame.paragraphs:
        p.alignment = align
        for r in p.runs:
            r.font.name = FONT_BODY
            r.font.size = Pt(font_size)
            r.font.bold = bold
            r.font.color.rgb = color

def render_full_width_bom(slide, top_in, height_in, data, table_title):
    t_box = slide.shapes.add_textbox(Inches(0.8), Inches(top_in - 0.28), Inches(11.733), Inches(0.26))
    tf_tb = t_box.text_frame
    p_tb = tf_tb.paragraphs[0]
    p_tb.text = table_title
    p_tb.font.name = FONT_HEADING
    p_tb.font.size = Pt(10.5)
    p_tb.font.bold = True
    p_tb.font.color.rgb = NAVY_PRIMARY

    rows_count = len(data) + 1
    cols_count = 6
    tbl_shape = slide.shapes.add_table(rows_count, cols_count, Inches(0.8), Inches(top_in), Inches(11.733), Inches(height_in))
    table = tbl_shape.table

    col_widths = [Inches(0.55), Inches(2.80), Inches(3.70), Inches(3.28), Inches(0.70), Inches(0.70)]
    for i, w in enumerate(col_widths):
        table.columns[i].width = w

    headers = ["STT", "Tên Linh Kiện & Vật Tư", "Thông Số Kỹ Thuật Chi Tiết", "Vai Trò Kỹ Thuật Thực Tế", "ĐVT", "SL"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        align = PP_ALIGN.CENTER if j in [0, 4, 5] else PP_ALIGN.LEFT
        format_cell(cell, h, font_size=9.2, bold=True, color=RGBColor(255, 255, 255), bg_color=NAVY_PRIMARY, align=align)

    for r_idx, item in enumerate(data):
        row_idx = r_idx + 1
        is_group_header = item[6]
        if is_group_header:
            cell_stt = table.cell(row_idx, 0)
            format_cell(cell_stt, item[0], font_size=9.2, bold=True, color=NAVY_PRIMARY, bg_color=TECH_BLUE_LIGHT, align=PP_ALIGN.CENTER)
            for c in range(1, 6):
                cell = table.cell(row_idx, c)
                txt = item[1] if c == 1 else ""
                format_cell(cell, txt, font_size=9.2, bold=True, color=NAVY_PRIMARY, bg_color=TECH_BLUE_LIGHT, align=PP_ALIGN.LEFT)
        else:
            stt, name, spec, role, unit, qty, _ = item
            is_total_row = (stt == "★")
            if is_total_row:
                bg = RGBColor(254, 243, 199)
                txt_color = RGBColor(146, 64, 14)
                format_cell(table.cell(row_idx, 0), stt, font_size=9.5, bold=True, color=AMBER_GOLD, bg_color=bg, align=PP_ALIGN.CENTER)
                format_cell(table.cell(row_idx, 1), name, font_size=9.5, bold=True, color=txt_color, bg_color=bg, align=PP_ALIGN.LEFT)
                format_cell(table.cell(row_idx, 2), spec, font_size=9.0, bold=True, color=txt_color, bg_color=bg, align=PP_ALIGN.LEFT)
                format_cell(table.cell(row_idx, 3), role, font_size=9.0, bold=True, color=txt_color, bg_color=bg, align=PP_ALIGN.LEFT)
                format_cell(table.cell(row_idx, 4), unit, font_size=9.5, bold=True, color=txt_color, bg_color=bg, align=PP_ALIGN.CENTER)
                format_cell(table.cell(row_idx, 5), qty, font_size=10.0, bold=True, color=ALARM_RED, bg_color=bg, align=PP_ALIGN.CENTER)
            else:
                bg = ROW_ALT if r_idx % 2 == 1 else RGBColor(255, 255, 255)
                format_cell(table.cell(row_idx, 0), stt, font_size=9.0, bold=False, color=SLATE_MUTED, bg_color=bg, align=PP_ALIGN.CENTER)
                format_cell(table.cell(row_idx, 1), name, font_size=9.0, bold=True, color=SLATE_DARK, bg_color=bg, align=PP_ALIGN.LEFT)
                format_cell(table.cell(row_idx, 2), spec, font_size=8.8, bold=False, color=SLATE_DARK, bg_color=bg, align=PP_ALIGN.LEFT)
                format_cell(table.cell(row_idx, 3), role, font_size=8.8, bold=False, color=SLATE_MUTED, bg_color=bg, align=PP_ALIGN.LEFT)
                format_cell(table.cell(row_idx, 4), unit, font_size=9.0, bold=False, color=SLATE_DARK, bg_color=bg, align=PP_ALIGN.CENTER)
                format_cell(table.cell(row_idx, 5), qty, font_size=9.2, bold=True, color=NAVY_PRIMARY, bg_color=bg, align=PP_ALIGN.CENTER)

# ==============================================================================
# BẢNG DỮ LIỆU BOM (GIỮ NGUYÊN 100% 34 MỤC VÀ DỰ TOÁN ~720K)
# ==============================================================================
bom_part_a_data = [
    ("I", "KHỐI VI ĐIỀU KHIỂN, CẢM BIẾN & CƠ CẤU CHẤP HÀNH", "", "", "", "", True),
    ("1", "Bo mạch ESP32 DevKit V1", "30 chân, Dual-core 240MHz, Wi-Fi 2.4GHz & BLE", "Xử lý FreeRTOS đa nhiệm, MQTT Client", "Bo", "1", False),
    ("2", "Module Cảm biến khí/khói MQ-2", "Kèm bo so sánh LM393 vi chỉnh, ngõ ra AOUT & DOUT", "Đo nồng độ khói/LPG 200-10000ppm", "Module", "1", False),
    ("3", "Module Cảm biến nhiệt & ẩm DHT22", "AM2302 kỹ thuật số (Sai số: ±0.5°C, ±2% RH)", "Giám sát rủi ro nhiệt độ môi trường", "Module", "1", False),
    ("4", "Module Relay 1 kênh 5VDC", "Tiếp điểm 10A 250VAC/30VDC, cách ly quang Opto", "Đóng cắt cưỡng bức quạt hút khói 12V", "Module", "1", False),
    ("5", "Còi chíp báo động (Active Buzzer)", "5VDC, phát âm thanh báo cháy tần số cao >85dB", "Phát tín hiệu còi hú báo động tại chỗ", "Cái", "1", False),
    ("6", "Đèn LED chỉ thị phi 5mm", "1 LED Đỏ (Cảnh báo cháy) + 1 LED Xanh (Nguồn)", "Báo trạng thái hoạt động của hệ thống", "Cái", "2", False),
    ("7", "Điện trở hạn dòng LED", "330 Ω — 1/4W, chân cắm, sai số 5%", "Hạn dòng bảo vệ LED không quá tải GPIO", "Con", "2", False),
    ("8", "Nút nhấn khẩn cấp / Test", "4 chân 12x12mm kèm nắp nhựa tròn", "Kích hoạt quạt khẩn cấp / Test thủ công", "Cái", "1", False),
    ("9", "Điện trở kéo nút nhấn (Pull-up)", "10k Ω — 1/4W, chân cắm, sai số 5%", "Chống trôi mức logic chân GPIO vi điều khiển", "Con", "1", False),
    ("II", "KHỐI NGUỒN CÔNG SUẤT & BẢO VỆ ĐIỆN NĂNG", "", "", "", "", True),
    ("10", "Adapter nguồn AC-DC", "Điện áp vào 100-240VAC, ngõ ra 12VDC - 2A ổn định", "Cấp nguồn chính cho toàn bộ trạm giám sát", "Bộ", "1", False),
    ("11", "Mạch hạ áp Buck DC-DC LM2596S", "In 12VDC, Out 5VDC - 3A (Hiệu suất chuyển đổi 92%)", "Cấp nguồn 5V nuôi ESP32 & module cảm biến", "Bo", "1", False),
    ("12", "Quạt hút khói làm mát tản nhiệt", "12VDC 0.18A (80x80x25mm) động cơ không chổi than", "Hút khói khí độc cưỡng bức ra môi trường", "Cái", "1", False),
    ("13", "Lưới thép bảo vệ quạt hút", "Thép mạ Crom/Niken 80mm mắt tổ ong chống gỉ", "Ngăn dị vật lọt vào cánh quạt quay tốc độ cao", "Cái", "1", False),
    ("14", "Cầu chì ống thủy tinh 5x20mm", "2A 250V tác động nhanh (Fast-blow safety fuse)", "Bảo vệ ngắt mạch tức thì, chống chập cháy", "Con", "1", False),
    ("15", "Hộp/Đế gắn cầu chì PCB", "Vỏ nhựa chống cháy 5x20mm có nắp đậy an toàn", "Gắn cố định cầu chì an toàn trên bo mạch", "Cái", "1", False),
    ("16", "Tụ hóa lọc nguồn đầu vào/ra", "100µF - 25V chịu nhiệt 105°C dập xung nguồn", "Chống sụt áp tức thời khi ESP32 bật Wi-Fi", "Con", "2", False),
    ("17", "Tụ gốm khử nhiễu cao tần", "100nF (mã 104) - 50V lọc xung cao tần", "Lọc nhiễu điện áp đường nguồn 5V và 3.3V", "Con", "2", False),
    ("18", "Công tắc bập bênh nguồn", "KCD11 2 chân, tiếp điểm chịu dòng 3A/250VAC", "Đóng ngắt nguồn điện chính thủ công", "Cái", "1", False)
]

bom_part_b_data = [
    ("III", "KHỐI ĐẤU NỐI, DÂY DẪN & SOCKET KỸ THUẬT", "", "", "", "", True),
    ("19", "Jack nguồn DC cái gắn vỏ", "Chuẩn 5.5 x 2.1mm chân vặn ốc có đai hãm chống tuột", "Cắm jack adapter cấp nguồn xuyên vỏ hộp", "Bộ", "1", False),
    ("20", "Cọc đấu dây vặn ốc KF301-2P", "Screw Terminal 2 chân, bước chân 5.0mm chịu dòng cao", "Đấu nối nguồn 12V, tiếp điểm rơ-le quạt", "Cái", "3", False),
    ("21", "Cọc đấu dây vặn ốc KF301-3P", "Screw Terminal 3 chân, bước chân 5.0mm chắc chắn", "Đấu nối dây tín hiệu cảm biến và rơ-le", "Cái", "2", False),
    ("22", "Hàng rào cắm cái (Female Header)", "1x15 chân bước chuẩn 2.54mm mạ đồng dẫn điện", "Socket cắm tháo lắp ESP32 chống hỏng chân", "Thanh", "2", False),
    ("23", "Dây điện silicon chịu nhiệt 22AWG", "Đồng nhiều sợi mạ thiếc, vỏ silicon đỏ/đen chịu nhiệt", "Đi dây nguồn 12V và 5V tải dòng an toàn", "Mét", "1.5", False),
    ("24", "Dây cắm tín hiệu Dupont", "Đực - Cái chuẩn 2.54mm (chiều dài tiêu chuẩn 20cm)", "Nối tín hiệu GPIO giữa ESP32 và các module", "Sợi", "10", False),
    ("25", "Ống gen co nhiệt cách điện", "Phi 2mm, 4mm, 6mm chất liệu Polyolefin chống cháy", "Bọc cách điện an toàn mối hàn dây dẫn", "Mét", "0.5", False),
    ("IV", "CƠ KHÍ, VỎ HỘP & CHI TIẾT ỐC VÍT LẮP RÁP THỰC TẾ", "", "", "", "", True),
    ("26", "Vỏ hộp nhựa ABS chống cháy", "Kích thước 158 x 90 x 60mm, chuẩn kháng bụi/nước IP54", "Chứa và bảo vệ toàn bộ mạch điện tử bên trong", "Hộp", "1", False),
    ("27", "Bo mạch in 2 lớp (Main PCB)", "Phíp thủy tinh FR4 dày 1.6mm (100 x 70mm), mạ thiếc", "Tích hợp toàn bộ linh kiện cắm và đường mạch", "Tấm", "1", False),
    ("28", "Trụ đồng lục giác đực - cái", "Đồng thau ren M3 x 10mm (+ đầu ren đực dài 6mm)", "Đệm cách ly bo mạch với mặt đáy vỏ hộp", "Cái", "8", False),
    ("29", "Ốc vít bake đầu dù bắt bo mạch", "Inox 304 không gỉ ren M3 x 6mm bước ren chuẩn", "Siết cố định PCB vào trụ đồng chắc chắn", "Con", "8", False),
    ("30", "Đai ốc (Tán) khóa chân trụ đồng", "Inox 304 ren M3 tiêu chuẩn công nghiệp DIN934", "Khóa trụ đồng xuyên qua đáy vỏ hộp thiết bị", "Con", "8", False),
    ("31", "Vòng đệm (Lông đền) nhựa Nylon", "Đệm phẳng M3 cách điện & chống xước bề mặt PCB", "Lót ốc chống cọ tróc mạch in khi siết chặt", "Cái", "8", False),
    ("32", "Bu-lông & Đai ốc gắn quạt hút", "Bu-lông inox M4 x 35mm kèm tán M4 & đệm vênh", "Bắt siết quạt hút 80mm vào nắp vỏ hộp", "Bộ", "4", False),
    ("33", "Vít nở & Tắc kê gắn tường", "Vít tự khoan thép mạ kẽm M3.5 x 25mm + tắc kê nhựa phi 6", "Bắt cố định vỏ hộp lên tường PCCC công trình", "Bộ", "4", False),
    ("34", "Gioăng cao su luồn dây (Grommet)", "Cao su đàn hồi chịu nhiệt phi 12mm luồn dây điện", "Chống cứa đứt vỏ dây khi xuyên thành vỏ hộp", "Cái", "2", False),
    ("+", "Vật tư phụ & linh kiện dự phòng", "Thiếc hàn không chì, mỡ hàn, băng dính cách điện", "Dự phòng chập cháy MCU/Sensor và bảo trì", "Gói", "1", False),
    ("★", "TỔNG KINH PHÍ DỰ TOÁN (BOM)", "Toàn bộ linh kiện điện tử, cơ khí, ốc vít & gia công PCB", "Chi phí trọn gói hoàn thiện trạm IoT thực tế", "Tổng", "~720k", False)
]

def build_full_8_slides():
    prs = create_presentation()
    blank_layout = prs.slide_layouts[6]

    # ==========================================================================
    # SLIDE 1: TRANG BÌA (COVER SLIDE)
    # ==========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    add_card(s1, 0, 0, 13.333, 7.5, bg_color=NAVY_DARK, border_color=None)
    add_card(s1, 0, 0, 0.35, 7.5, bg_color=CYAN_ACCENT, border_color=None)

    tb_u = s1.shapes.add_textbox(Inches(0.9), Inches(0.45), Inches(11.5), Inches(0.75))
    tf_u = tb_u.text_frame
    p_u1 = tf_u.paragraphs[0]
    p_u1.text = "BỘ CÔNG THƯƠNG  •  TRƯỜNG ĐẠI HỌC CÔNG THƯƠNG TP. HỒ CHÍ MINH (HUIT)"
    p_u1.font.name = FONT_HEADING
    p_u1.font.size = Pt(11.5)
    p_u1.font.bold = True
    p_u1.font.color.rgb = CYAN_ACCENT

    p_u2 = tf_u.add_paragraph()
    p_u2.text = "KHOA CÔNG NGHỆ THÔNG TIN  •  BỘ MÔN MẠNG & AN TOÀN THÔNG TIN"
    p_u2.font.name = FONT_BODY
    p_u2.font.size = Pt(10)
    p_u2.font.color.rgb = RGBColor(180, 205, 230)

    p_u3 = tf_u.add_paragraph()
    p_u3.text = "HỌC PHẦN: IT4735 — INTERNET OF THINGS (IoT) VÀ ỨNG DỤNG"
    p_u3.font.name = FONT_BODY
    p_u3.font.size = Pt(10)
    p_u3.font.bold = True
    p_u3.font.color.rgb = RGBColor(220, 235, 252)

    tb_title = s1.shapes.add_textbox(Inches(0.9), Inches(1.42), Inches(11.5), Inches(1.50))
    tf_t = tb_title.text_frame
    p_t0 = tf_t.paragraphs[0]
    p_t0.text = "BÁO CÁO THIẾT KẾ & HIỆN THỰC HỆ THỐNG IOT HOÀN CHỈNH (8 SLIDES CHUẨN HÓA)"
    p_t0.font.name = FONT_HEADING
    p_t0.font.size = Pt(13.5)
    p_t0.font.bold = True
    p_t0.font.color.rgb = AMBER_GOLD

    p_t1 = tf_t.add_paragraph()
    p_t1.text = "HỆ THỐNG BÁO KHÓI CẢNH BÁO SỚM"
    p_t1.font.name = FONT_HEADING
    p_t1.font.size = Pt(31)
    p_t1.font.bold = True
    p_t1.font.color.rgb = RGBColor(255, 255, 255)

    p_t2 = tf_t.add_paragraph()
    p_t2.text = "Smart Smoke & Fire Early Warning System — Tích Hợp Đầy Đủ 3 Tầng Kỹ Thuật"
    p_t2.font.name = FONT_BODY
    p_t2.font.size = Pt(12.5)
    p_t2.font.color.rgb = RGBColor(200, 220, 240)

    # Khối Nhóm 04
    add_card(s1, 0.9, 3.02, 11.533, 1.40, bg_color=RGBColor(24, 38, 64), border_color=CYAN_ACCENT, border_width=1.5)
    tb_team = s1.shapes.add_textbox(Inches(1.05), Inches(3.08), Inches(11.233), Inches(1.25))
    tf_team = tb_team.text_frame
    
    p_tm0 = tf_team.paragraphs[0]
    p_tm0.text = "NHÓM THỰC HIỆN: NHÓM 04  |  LỚP HỌC PHẦN: N09"
    p_tm0.font.name = FONT_HEADING
    p_tm0.font.size = Pt(11.5)
    p_tm0.font.bold = True
    p_tm0.font.color.rgb = AMBER_GOLD

    p_tm1 = tf_team.add_paragraph()
    p_tm1.text = "• 1. Nguyễn Vĩnh Khang   —   MSSV: 2001230381   (Trưởng nhóm: Firmware ESP32, FSM & Tích Hợp)"
    p_tm1.font.size = Pt(10.8)
    p_tm1.font.bold = True
    p_tm1.font.color.rgb = RGBColor(255, 255, 255)

    p_tm2 = tf_team.add_paragraph()
    p_tm2.text = "• 2. Nguyễn Văn Đức       —   MSSV: 2001230186   (Thành viên: Thiết Kế Topic Tree, Payload JSON & Downlink)"
    p_tm2.font.size = Pt(10.8)
    p_tm2.font.bold = True
    p_tm2.font.color.rgb = RGBColor(255, 255, 255)

    p_tm3 = tf_team.add_paragraph()
    p_tm3.text = "• 3. Nguyễn Văn Mãnh     —   MSSV: 2001230503   (Thành viên: Khóa An Toàn Safety Guard & Web Dashboard)"
    p_tm3.font.size = Pt(10.8)
    p_tm3.font.bold = True
    p_tm3.font.color.rgb = RGBColor(255, 255, 255)

    # 3 Khối Card tổng quan 3 Part
    col_w = 3.65
    gap = 0.28
    y_cards = 4.58
    h_cards = 1.95

    # Card 1: Part 1
    add_card(s1, 0.9, y_cards, col_w, h_cards, bg_color=RGBColor(24, 38, 64), border_color=TECH_BLUE, border_width=1.5)
    tb_c1 = s1.shapes.add_textbox(Inches(1.0), Inches(y_cards + 0.16), Inches(col_w - 0.2), Inches(h_cards - 0.32))
    tf_c1 = tb_c1.text_frame
    p_c1_h = tf_c1.paragraphs[0]
    p_c1_h.text = "PART 1: DEVICE (ESP32)"
    p_c1_h.font.bold = True
    p_c1_h.font.size = Pt(12.5)
    p_c1_h.font.color.rgb = CYAN_ACCENT

    p1_l1 = tf_c1.add_paragraph()
    p1_l1.space_before = Pt(8)
    p1_l1.text = "▶ 1. Thiết Kế Mạch Phần Cứng, Cầu Phân Áp AOUT"
    p1_l1.font.bold = True
    p1_l1.font.size = Pt(10)
    p1_l1.font.color.rgb = RGBColor(255, 255, 255)

    p1_l2 = tf_c1.add_paragraph()
    p1_l2.space_before = Pt(5)
    p1_l2.text = "▶ 2. Firmware FreeRTOS, FSM 3 Cấp & Lọc EMA"
    p1_l2.font.bold = True
    p1_l2.font.size = Pt(10)
    p1_l2.font.color.rgb = RGBColor(205, 225, 245)

    p1_l3 = tf_c1.add_paragraph()
    p1_l3.space_before = Pt(5)
    p1_l3.text = "▶ 3. Bảng BOM Chi Tiết Từng Con Ốc (~720k)"
    p1_l3.font.bold = True
    p1_l3.font.size = Pt(10)
    p1_l3.font.color.rgb = AMBER_GOLD

    # Card 2: Part 2
    add_card(s1, 0.9 + col_w + gap, y_cards, col_w, h_cards, bg_color=RGBColor(24, 38, 64), border_color=TECH_BLUE, border_width=1.5)
    tb_c2 = s1.shapes.add_textbox(Inches(1.0 + col_w + gap), Inches(y_cards + 0.16), Inches(col_w - 0.2), Inches(h_cards - 0.32))
    tf_c2 = tb_c2.text_frame
    p_c2_h = tf_c2.paragraphs[0]
    p_c2_h.text = "PART 2: MQTT SERVICES"
    p_c2_h.font.bold = True
    p_c2_h.font.size = Pt(12.5)
    p_c2_h.font.color.rgb = AMBER_GOLD

    p2_l1 = tf_c2.add_paragraph()
    p2_l1.space_before = Pt(8)
    p2_l1.text = "▶ 1. Cấu Trúc Topic Phân Cấp & Rationale Kỹ Thuật"
    p2_l1.font.bold = True
    p2_l1.font.size = Pt(10)
    p2_l1.font.color.rgb = RGBColor(255, 255, 255)

    p2_l2 = tf_c2.add_paragraph()
    p2_l2.space_before = Pt(5)
    p2_l2.text = "▶ 2. 4 Dịch Vụ: Auth, Collect, Control, Keep-Alive"
    p2_l2.font.bold = True
    p2_l2.font.size = Pt(10)
    p2_l2.font.color.rgb = RGBColor(205, 225, 245)

    p2_l3 = tf_c2.add_paragraph()
    p2_l3.space_before = Pt(5)
    p2_l3.text = "▶ 3. Luồng Tương Tác 2 Chiều & Khóa Safety Guard"
    p2_l3.font.bold = True
    p2_l3.font.size = Pt(10)
    p2_l3.font.color.rgb = CYAN_ACCENT

    # Card 3: Part 3
    add_card(s1, 0.9 + (col_w + gap)*2, y_cards, col_w, h_cards, bg_color=RGBColor(24, 38, 64), border_color=TECH_BLUE, border_width=1.5)
    tb_c3 = s1.shapes.add_textbox(Inches(1.0 + (col_w + gap)*2), Inches(y_cards + 0.16), Inches(col_w - 0.2), Inches(h_cards - 0.32))
    tf_c3 = tb_c3.text_frame
    p_c3_h = tf_c3.paragraphs[0]
    p_c3_h.text = "PART 3: WEB SERVER APP"
    p_c3_h.font.bold = True
    p_c3_h.font.size = Pt(12.5)
    p_c3_h.font.color.rgb = SUCCESS_GREEN

    p3_l1 = tf_c3.add_paragraph()
    p3_l1.space_before = Pt(8)
    p3_l1.text = "▶ 1. 4 Trụ Cột Nền Tảng: Trực Quan, CSDL, GUI, Analysis"
    p3_l1.font.bold = True
    p3_l1.font.size = Pt(10)
    p3_l1.font.color.rgb = RGBColor(255, 255, 255)

    p3_l2 = tf_c3.add_paragraph()
    p3_l2.space_before = Pt(5)
    p3_l2.text = "▶ 2. Nhận Diện Cháy Sớm & Báo Động Bot Telegram"
    p3_l2.font.bold = True
    p3_l2.font.size = Pt(10)
    p3_l2.font.color.rgb = RGBColor(205, 225, 245)

    p3_l3 = tf_c3.add_paragraph()
    p3_l3.space_before = Pt(5)
    p3_l3.text = "▶ 3. Kết Quả Đo RTT & 16 Test Cases M4 Pass 100%"
    p3_l3.font.bold = True
    p3_l3.font.size = Pt(10)
    p3_l3.font.color.rgb = AMBER_GOLD

    tb_meta = s1.shapes.add_textbox(Inches(0.9), Inches(6.65), Inches(11.5), Inches(0.4))
    tf_m = tb_meta.text_frame
    p_m = tf_m.paragraphs[0]
    p_m.text = "HỌC KỲ II - NĂM HỌC 2025-2026  |  KHOA CÔNG NGHỆ THÔNG TIN  |  ĐẠI HỌC CÔNG THƯƠNG TP. HỒ CHÍ MINH (HUIT)"
    p_m.font.size = Pt(9.5)
    p_m.font.color.rgb = RGBColor(160, 185, 215)


    # ==========================================================================
    # SLIDE 2: PART 1 - KIẾN TRÚC PHẦN CỨNG & THUẬT TOÁN NHÚNG FREERTOS
    # ==========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "PART 1: DEVICE (ESP32) — THIẾT KẾ PHẦN CỨNG & THUẬT TOÁN NHÚNG FREERTOS",
               "Sơ Đồ Khối Điện Năng, Máy Trạng Thái FSM 3 Cấp & Bộ Lọc Tín Hiệu Số EMA Triệt Tiêu Báo Ảo")
    add_footer(s2, 2, 8)

    c_w = 5.75
    c_h_top = 2.72
    c_h_bot = 2.82
    x_l = 0.8
    x_r = 6.78
    y_t = 1.10
    y_b = 3.98

    # Khối 1: Thiết Kế Điện & An Toàn Phần Cứng (Trên Trái)
    add_card(s2, x_l, y_t, c_w, c_h_top, bg_color=CARD_BG, border_color=TECH_BLUE, border_width=1.5)
    h_b1 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x_l + 0.08), Inches(y_t + 0.08), Inches(c_w - 0.16), Inches(0.36))
    h_b1.fill.solid()
    h_b1.fill.fore_color.rgb = TECH_BLUE
    h_b1.line.fill.background()
    p = h_b1.text_frame.paragraphs[0]
    p.text = "1. THIẾT KẾ ĐIỆN NĂNG & AN TOÀN PHẦN CỨNG THEO DATASHEET"
    p.font.bold = True
    p.font.size = Pt(10.5)
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.alignment = PP_ALIGN.CENTER

    tb_b1 = s2.shapes.add_textbox(Inches(x_l + 0.10), Inches(y_t + 0.46), Inches(c_w - 0.20), Inches(c_h_top - 0.50))
    tf_b1 = tb_b1.text_frame
    tf_b1.word_wrap = True
    tf_b1.margin_top = Inches(0.02)
    tf_b1.margin_bottom = Inches(0.02)
    items_b1 = [
        ("Nguồn 12VDC - 2A", "Cấp dòng ổn định nuôi trực tiếp quạt hút khói 12V 80mm động cơ BLDC (dòng 0.18A)."),
        ("Buck LM2596S (5V - 3A)", "Hạ 12V -> 5V nuôi ESP32 và cấp trực tiếp cuộn sấy MQ-2 (R_H ≈ 31Ω, P_H ≈ 900mW) bảo đảm SnO2 đạt nhiệt độ làm việc tối ưu theo Datasheet Hanwei."),
        ("Cầu phân áp ngõ ra AOUT", "Tại ngõ ra tín hiệu AOUT của MQ-2 (0 - 5V), dùng trở R1=10kΩ, R2=20kΩ (hệ số 2/3) hạ về 0 - 3.3V, bảo vệ an toàn chân ADC (GPIO 34) ESP32 không bị quá áp."),
        ("Cách ly quang Opto PC817", "Cách ly hoàn toàn GPIO với cuộn hút relay 5V (cách điện 5000Vrms) kèm diode 1N4148 dập xung ngược, chống dòng cảm ứng làm treo MCU."),
        ("Bảo vệ đa tầng phần cứng", "Cầu chì 2A Fast-blow chống ngắn mạch, tụ hóa 100µF chống sụt áp khi phát Wi-Fi (+20dBm ~240mA), tụ gốm 100nF lọc xung cao tần.")
    ]
    for lbl, desc in items_b1:
        p = tf_b1.add_paragraph()
        p.space_before = Pt(3.0)
        r1 = p.add_run()
        r1.text = "• " + lbl + ": "
        r1.font.bold = True
        r1.font.size = Pt(9.8)
        r1.font.color.rgb = TECH_BLUE
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = SLATE_DARK

    # Khối 2: Kiến Trúc Firmware FreeRTOS Đa Nhiệm (Trên Phải)
    add_card(s2, x_r, y_t, c_w, c_h_top, bg_color=CARD_BG, border_color=NAVY_PRIMARY, border_width=1.5)
    h_b2 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x_r + 0.08), Inches(y_t + 0.08), Inches(c_w - 0.16), Inches(0.36))
    h_b2.fill.solid()
    h_b2.fill.fore_color.rgb = NAVY_PRIMARY
    h_b2.line.fill.background()
    p = h_b2.text_frame.paragraphs[0]
    p.text = "2. KIẾN TRÚC FIRMWARE FREERTOS ĐA NHIỆM (DUAL-CORE)"
    p.font.bold = True
    p.font.size = Pt(10.5)
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.alignment = PP_ALIGN.CENTER

    tb_b2 = s2.shapes.add_textbox(Inches(x_r + 0.10), Inches(y_t + 0.46), Inches(c_w - 0.20), Inches(c_h_top - 0.50))
    tf_b2 = tb_b2.text_frame
    tf_b2.word_wrap = True
    tf_b2.margin_top = Inches(0.02)
    tf_b2.margin_bottom = Inches(0.02)
    items_b2 = [
        ("Dual-Core 240MHz", "Tách tải xử lý độc lập hoàn toàn giữa truyền thông mạng và điều khiển phần cứng:"),
        ("Core 0 (Network Task)", "Quản lý kết nối Wi-Fi Station, MQTT Client Loop, phân giải DNS và Keep-Alive 30s."),
        ("Core 1 (Sensors & FSM)", "Đọc cảm biến chu kỳ 1s, ngắt phản hồi khẩn cấp nút bấm ngoại vi với độ trễ cực thấp <50ms."),
        ("Lập trình Non-blocking", "Sử dụng hàng đợi FreeRTOS Queue & vTaskDelay, triệt tiêu hoàn toàn delay() gây nghẽn CPU."),
        ("Hardware Watchdog", "Kích hoạt WDT phần cứng tự động reset phục hồi nếu vi điều khiển bị treo quá 5 giây.")
    ]
    for lbl, desc in items_b2:
        p = tf_b2.add_paragraph()
        p.space_before = Pt(3.0)
        r1 = p.add_run()
        r1.text = "• " + lbl + ": "
        r1.font.bold = True
        r1.font.size = Pt(9.8)
        r1.font.color.rgb = NAVY_PRIMARY
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = SLATE_DARK

    # Khối 3: Máy Trạng Thái Hữu Hạn FSM & Hysteresis (Dưới Trái)
    add_card(s2, x_l, y_b, c_w, c_h_bot, bg_color=CARD_BG, border_color=ALARM_RED, border_width=1.5)
    h_b3 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x_l + 0.08), Inches(y_b + 0.08), Inches(c_w - 0.16), Inches(0.36))
    h_b3.fill.solid()
    h_b3.fill.fore_color.rgb = ALARM_RED
    h_b3.line.fill.background()
    p = h_b3.text_frame.paragraphs[0]
    p.text = "3. MÁY TRẠNG THÁI HỮU HẠN FSM & VÙNG TRỄ HYSTERESIS"
    p.font.bold = True
    p.font.size = Pt(10.5)
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.alignment = PP_ALIGN.CENTER

    tb_b3 = s2.shapes.add_textbox(Inches(x_l + 0.10), Inches(y_b + 0.46), Inches(c_w - 0.20), Inches(c_h_bot - 0.50))
    tf_b3 = tb_b3.text_frame
    tf_b3.word_wrap = True
    tf_b3.margin_top = Inches(0.02)
    tf_b3.margin_bottom = Inches(0.02)
    items_b3 = [
        ("Trạng thái SAFE (< 300 PPM)", "Môi trường an toàn: Quạt OFF, Còi OFF, LED Xanh sáng, gửi Telemetry 2s."),
        ("Trạng thái WARN (300 - 400 PPM)", "Khói tăng bất thường: Quạt ON cấp 1 hút khí, LED Vàng chớp cảnh báo sơ bộ."),
        ("Trạng thái ALARM (≥ 400 PPM)", "Báo cháy khẩn cấp: Quạt hút cưỡng bức 100%, Còi hú ngắt quãng >85dB, khóa quyền tắt."),
        ("Vùng trễ Hysteresis (300-400 PPM)", "Bật quạt khi ≥ 400 PPM, chỉ tắt khi khói hạ hẳn ≤ 300 PPM; chống chattering bảo vệ rơ-le."),
        ("Phân xử quyền PCCC", "Khi có cháy thật (ALARM), rule tự động kích hoạt tại chỗ chiếm quyền ưu tiên tuyệt đối.")
    ]
    for lbl, desc in items_b3:
        p = tf_b3.add_paragraph()
        p.space_before = Pt(3.0)
        r1 = p.add_run()
        r1.text = "• " + lbl + ": "
        r1.font.bold = True
        r1.font.size = Pt(9.8)
        r1.font.color.rgb = ALARM_RED
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = SLATE_DARK

    # Khối 4: Xử Lý Tín Hiệu Số & Đệm Ngoại Tuyến (Dưới Phải)
    add_card(s2, x_r, y_b, c_w, c_h_bot, bg_color=CARD_BG, border_color=AMBER_GOLD, border_width=1.5)
    h_b4 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x_r + 0.08), Inches(y_b + 0.08), Inches(c_w - 0.16), Inches(0.36))
    h_b4.fill.solid()
    h_b4.fill.fore_color.rgb = AMBER_GOLD
    h_b4.line.fill.background()
    p = h_b4.text_frame.paragraphs[0]
    p.text = "4. XỬ LÝ TÍN HIỆU SỐ & BỘ ĐỆM VÒNG NGOẠI TUYẾN"
    p.font.bold = True
    p.font.size = Pt(10.5)
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.alignment = PP_ALIGN.CENTER

    tb_b4 = s2.shapes.add_textbox(Inches(x_r + 0.10), Inches(y_b + 0.46), Inches(c_w - 0.20), Inches(c_h_bot - 0.50))
    tf_b4 = tb_b4.text_frame
    tf_b4.word_wrap = True
    tf_b4.margin_top = Inches(0.02)
    tf_b4.margin_bottom = Inches(0.02)
    items_b4 = [
        ("Bộ lọc số EMA (alpha=0.2)", "Công thức: S_t = α·X_t + (1-α)·S_{t-1}. Làm mịn tín hiệu, triệt tiêu xung gai nhiễu điện áp."),
        ("Khử báo động giả", "Loại bỏ hoàn toàn tác động của khói thuốc lá thoáng qua hoặc xịt cồn vệ sinh ngắn hạn."),
        ("Hiệu chuẩn Power-Law", "Hiệu chuẩn thực nghiệm theo Datasheet Hanwei với hàm PPM = A·(Rs/R0)^B đo lường chính xác."),
        ("Ring Buffer SPIFFS", "Khi mất Wi-Fi, tự động ghi 20 bản ghi sự cố vào bộ đệm vòng trên flash SPIFFS vi điều khiển."),
        ("Đồng bộ Offline Replay", "Ngay khi mạng hồi phục, tự động xả tuần tự 20 bản ghi lên topic smoke/history/sync.")
    ]
    for lbl, desc in items_b4:
        p = tf_b4.add_paragraph()
        p.space_before = Pt(3.0)
        r1 = p.add_run()
        r1.text = "• " + lbl + ": "
        r1.font.bold = True
        r1.font.size = Pt(9.8)
        r1.font.color.rgb = AMBER_GOLD
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = SLATE_DARK


    # ==========================================================================
    # SLIDE 3: PART 1 - BẢNG BOM VẬT TƯ (PHẦN A)
    # ==========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "PART 1: DEVICE (ESP32) — THIẾT KẾ PHẦN CỨNG & BẢNG BOM VẬT TƯ (TRANG 1/2)",
               "Kiến Trúc Firmware FreeRTOS, Bộ Lọc Số EMA & Bảng BOM Vi Điều Khiển, Cảm Biến, Chấp Hành")
    add_footer(s3, 3, 8)

    c_fw1 = add_card(s3, 0.8, 1.05, 5.75, 0.78, bg_color=TECH_BLUE_LIGHT, border_color=TECH_BLUE_BORDER)
    tb_fw1 = s3.shapes.add_textbox(Inches(0.9), Inches(1.08), Inches(5.55), Inches(0.72))
    tf_fw1 = tb_fw1.text_frame
    p1_h = tf_fw1.paragraphs[0]
    p1_h.text = "1. Kiến Trúc Firmware FreeRTOS Đa Nhiệm"
    p1_h.font.bold = True
    p1_h.font.size = Pt(10.5)
    p1_h.font.color.rgb = NAVY_PRIMARY
    p1_1 = tf_fw1.add_paragraph()
    p1_1.text = "• Dual-Core 240MHz: Core 0 (Wi-Fi/MQTT) • Core 1 (Sensors & FSM) • Ngắt khẩn cấp <50ms."
    p1_1.font.size = Pt(9.5)
    p1_1.font.color.rgb = SLATE_DARK

    c_fw2 = add_card(s3, 6.78, 1.05, 5.75, 0.78, bg_color=TECH_BLUE_LIGHT, border_color=TECH_BLUE_BORDER)
    tb_fw2 = s3.shapes.add_textbox(Inches(6.88), Inches(1.08), Inches(5.55), Inches(0.72))
    tf_fw2 = tb_fw2.text_frame
    p2_h = tf_fw2.paragraphs[0]
    p2_h.text = "2. Xử Lý Tín Hiệu Số & Bộ Đệm Ngoại Tuyến"
    p2_h.font.bold = True
    p2_h.font.size = Pt(10.5)
    p2_h.font.color.rgb = NAVY_PRIMARY
    p2_1 = tf_fw2.add_paragraph()
    p2_1.text = "• Bộ lọc số EMA (alpha=0.2) triệt nhiễu khói • Ring Buffer SPIFFS lưu 20 bản ghi khi rớt mạng."
    p2_1.font.size = Pt(9.5)
    p2_1.font.color.rgb = SLATE_DARK

    render_full_width_bom(s3, 2.15, 4.80, bom_part_a_data, "BẢNG BOM (PHẦN A): VI ĐIỀU KHIỂN, CẢM BIẾN, CHẤP HÀNH & NGUỒN (KHỐI I & II)")


    # ==========================================================================
    # SLIDE 4: PART 1 - CƠ KHÍ LẮP RÁP & BẢNG BOM VẬT TƯ (PHẦN B)
    # ==========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "PART 1: DEVICE (ESP32) — CƠ KHÍ LẮP RÁP & BẢNG BOM VẬT TƯ (TRANG 2/2)",
               "Tiêu Chuẩn Cơ Khí Vỏ Hộp IP54, Bo Mạch In PCB & Bảng BOM Chi Tiết Từng Con Ốc Nhỏ Nhất")
    add_footer(s4, 4, 8)

    c_hw1 = add_card(s4, 0.8, 1.05, 5.75, 0.78, bg_color=RGBColor(254, 243, 199), border_color=RGBColor(251, 191, 36))
    tb_hw1 = s4.shapes.add_textbox(Inches(0.9), Inches(1.08), Inches(5.55), Inches(0.72))
    tf_hw1 = tb_hw1.text_frame
    ph1_h = tf_hw1.paragraphs[0]
    ph1_h.text = "1. Thiết Kế Mạch In PCB & Cách Ly Công Suất"
    ph1_h.font.bold = True
    ph1_h.font.size = Pt(10.5)
    ph1_h.font.color.rgb = RGBColor(146, 64, 14)
    ph1_1 = tf_hw1.add_paragraph()
    ph1_1.text = "• Bo mạch 2 lớp FR4 (100x70mm) mạ thiếc dập via GND • Cách ly quang PC817 chống sốc ngược."
    ph1_1.font.size = Pt(9.5)
    ph1_1.font.color.rgb = SLATE_DARK

    c_hw2 = add_card(s4, 6.78, 1.05, 5.75, 0.78, bg_color=RGBColor(254, 243, 199), border_color=RGBColor(251, 191, 36))
    tb_hw2 = s4.shapes.add_textbox(Inches(6.88), Inches(1.08), Inches(5.55), Inches(0.72))
    tf_hw2 = tb_hw2.text_frame
    ph2_h = tf_hw2.paragraphs[0]
    ph2_h.text = "2. Tiêu Chuẩn Cơ Khí Vỏ Hộp & An Toàn Vận Hành"
    ph2_h.font.bold = True
    ph2_h.font.size = Pt(10.5)
    ph2_h.font.color.rgb = RGBColor(146, 64, 14)
    ph2_1 = tf_hw2.add_paragraph()
    ph2_1.text = "• Hộp nhựa ABS chống cháy IP54 • Cầu chì 2A ngắt mạch • Gioăng cao su luồn dây & lưới thép quạt."
    ph2_1.font.size = Pt(9.5)
    ph2_1.font.color.rgb = SLATE_DARK

    render_full_width_bom(s4, 2.15, 4.80, bom_part_b_data, "BẢNG BOM (PHẦN B): ĐẤU NỐI, VỎ HỘP & CHI TIẾT ỐC VÍT CƠ KHÍ THỰC TẾ (KHỐI III & IV)")


    # ==========================================================================
    # SLIDE 5: PART 2 - MQTT SERVICES ON SERVER & QUY CHUẨN TOPICS
    # ==========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "PART 2: MQTT SERVICES ON SERVER — TẦNG TRUYỀN THÔNG & MESSAGE BROKER",
               "Cấu Trúc Phân Cấp Topics Chuẩn Hóa, Rationale Kỹ Thuật & 4 Dịch Vụ Cốt Lõi (Auth, Collect, Control, Keep-Alive)")
    add_footer(s5, 5, 8)

    # Nửa trên
    add_card(s5, 0.8, 1.12, 6.95, 2.30, bg_color=CARD_BG, border_color=TECH_BLUE, border_width=1.5)
    tb_top = s5.shapes.add_textbox(Inches(0.9), Inches(1.16), Inches(6.75), Inches(2.22))
    tf_top = tb_top.text_frame
    tf_top.word_wrap = True

    p_tph = tf_top.paragraphs[0]
    p_tph.text = "Quy Chuẩn Cấu Trúc Topic: Nhom09 / smoke / {service_domain} / [{action_or_target}]"
    p_tph.font.name = FONT_HEADING
    p_tph.font.size = Pt(11.0)
    p_tph.font.bold = True
    p_tph.font.color.rgb = NAVY_PRIMARY

    topic_matrix = [
        ("Nhom09/smoke/auth/req & res/{id}", "Auth Svc", "QoS 1", "Handshake định danh (MAC, Passwd) ➔ Cấp Session Key HMAC-256"),
        ("Nhom09/smoke/telemetry", "Collect Svc", "QoS 0", "Định kỳ 2s: Ingest MySQL chuỗi thời gian & cập nhật Redis Cache"),
        ("Nhom09/smoke/history/sync", "Collect Svc", "QoS 1", "Xả đệm vòng 20 bản ghi ngoại tuyến khi mạng hồi phục (Offline Replay)"),
        ("Nhom09/smoke/cmd/fan, buzzer", "Control Svc", "QoS 1", "Downlink lệnh điều khiển kèm ACK xác nhận thực thi từ ESP32"),
        ("Nhom09/smoke/keepalive & lwt", "Keep_alive", "QoS 0/1", "Heartbeat 30s + LWT Di chúc phát hiện ngắt mạng tức thời <60s")
    ]

    for t_name, svc, qos_val, desc in topic_matrix:
        p = tf_top.add_paragraph()
        p.space_before = Pt(3.0)
        r1 = p.add_run()
        r1.text = "• " + t_name + " "
        r1.font.bold = True
        r1.font.size = Pt(10.0)
        r1.font.color.rgb = TECH_BLUE
        r2 = p.add_run()
        r2.text = f"[{svc} | {qos_val}]: "
        r2.font.bold = True
        r2.font.size = Pt(9.8)
        r2.font.color.rgb = NAVY_PRIMARY
        r3 = p.add_run()
        r3.text = desc
        r3.font.size = Pt(9.8)
        r3.font.color.rgb = SLATE_DARK

    # Khối Rationale
    add_card(s5, 7.95, 1.12, 4.58, 2.30, bg_color=TECH_BLUE_LIGHT, border_color=TECH_BLUE_BORDER, border_width=1.5)
    tb_why = s5.shapes.add_textbox(Inches(8.05), Inches(1.16), Inches(4.38), Inches(2.22))
    tf_why = tb_why.text_frame
    tf_why.word_wrap = True

    p_wh = tf_why.paragraphs[0]
    p_wh.text = "Rationale: Tại Sao Thiết Kế Phân Cấp & Tác Dụng?"
    p_wh.font.name = FONT_HEADING
    p_wh.font.size = Pt(11.0)
    p_wh.font.bold = True
    p_wh.font.color.rgb = NAVY_PRIMARY

    reasons = [
        ("Namespace Isolation", "Tiền tố Nhom09/ cô lập hoàn toàn luồng tin trên Broker dùng chung, chống xung đột."),
        ("Decoupling Độc Lập", "4 microservices chỉ sub đúng topic phụ trách; triệt tiêu tải CPU xử lý tin rác."),
        ("Tối Ưu RAM Vi Điều Khiển", "ESP32 chỉ sub `Nhom09/smoke/cmd/+`, tiết kiệm heap RAM (~200KB), không tràn buffer."),
        ("Phân Định 2 Chiều Rõ Ràng", "Kênh Downlink (`cmd/`) tách biệt kênh Uplink (`telemetry/status`), chống loop tin nhắn.")
    ]
    for r_title, r_desc in reasons:
        p = tf_why.add_paragraph()
        p.space_before = Pt(3.0)
        r = p.add_run()
        r.text = "▶ " + r_title + ": "
        r.font.bold = True
        r.font.size = Pt(10.0)
        r.font.color.rgb = SLATE_DARK
        r_t = p.add_run()
        r_t.text = r_desc
        r_t.font.size = Pt(9.8)
        r_t.font.color.rgb = SLATE_MUTED

    # Nửa dưới: 4 Microservices
    card_w = 2.78
    gap_s = 0.20
    y_s = 3.52
    h_s = 3.42

    microservices = [
        ("1. AUTH SERVICE", TECH_BLUE, [
            ("Nhiệm Vụ Lõi", "Bảo vệ tầng truyền thông, ngăn chặn thiết bị giả mạo."),
            ("Handshake", "Xác thực (id, mac, passwd) qua bảng MySQL device_registry."),
            ("Session Key", "Sinh mã HMAC-SHA256 (hạn 24h), bắt buộc kèm theo telemetry.")
        ]),
        ("2. COLLECT SERVICE", NAVY_PRIMARY, [
            ("Nhiệm Vụ Lõi", "Tiếp nhận dữ liệu đo đạc thời gian thực từ trạm cảm biến."),
            ("Ingest & Cache", "Ghi MySQL (<5ms) đồng thời đẩy lên Redis Cache phục vụ Web."),
            ("Xả Đệm Ngoại Tuyến", "Nạp đồng bộ 20 bản ghi sự cố sau khi mạng Wi-Fi phục hồi.")
        ]),
        ("3. CONTROL SERVICE", ALARM_RED, [
            ("Nhiệm Vụ Lõi", "Chuyển tiếp mệnh lệnh điều khiển chấp hành an toàn tuyệt đối."),
            ("Điều Khiển 2 Chiều", "Publish lệnh xuống Nhom09/smoke/cmd/fan, nhận gói ACK (<120ms)."),
            ("Khóa Khẩn Cấp (Guard)", "Chặn lệnh tắt quạt nếu hệ thống đang có cháy (State ALARM).")
        ]),
        ("4. KEEP_ALIVE SERVICE", SUCCESS_GREEN, [
            ("Nhiệm Vụ Lõi", "Theo dõi liên tục sức sống phần cứng và tính toàn vẹn mạng."),
            ("Chu Kỳ Heartbeat", "ESP32 gửi Nhom09/smoke/keepalive 30s; cập nhật mốc last_seen."),
            ("Cơ Chế LWT (Di Chúc)", "Broker tự phát OFFLINE nếu mất kết nối quá 60s, báo ngay Web & Bot.")
        ])
    ]

    for idx, (title, color, items) in enumerate(microservices):
        x_pos = 0.8 + idx * (card_w + gap_s)
        add_card(s5, x_pos, y_s, card_w, h_s, bg_color=CARD_BG, border_color=color, border_width=1.5)

        t_box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x_pos + 0.08), Inches(y_s + 0.08), Inches(card_w - 0.16), Inches(0.44))
        t_box.fill.solid()
        t_box.fill.fore_color.rgb = color
        t_box.line.fill.background()
        pt = t_box.text_frame.paragraphs[0]
        pt.text = title
        pt.font.bold = True
        pt.font.size = Pt(10.5)
        pt.font.color.rgb = RGBColor(255, 255, 255)
        pt.alignment = PP_ALIGN.CENTER

        tb_content = s5.shapes.add_textbox(Inches(x_pos + 0.08), Inches(y_s + 0.54), Inches(card_w - 0.16), Inches(h_s - 0.60))
        tf_c = tb_content.text_frame
        tf_c.word_wrap = True
        for lbl, desc in items:
            p = tf_c.add_paragraph()
            p.space_before = Pt(4.5)
            r1 = p.add_run()
            r1.text = "• " + lbl + ": "
            r1.font.bold = True
            r1.font.size = Pt(10.0)
            r1.font.color.rgb = color
            r2 = p.add_run()
            r2.text = desc
            r2.font.size = Pt(9.8)
            r2.font.color.rgb = SLATE_DARK


    # ==========================================================================
    # SLIDE 6: TÍCH HỢP HỆ THỐNG — LUỒNG DỮ LIỆU HAI CHIỀU & KHÓA AN TOÀN PCCC
    # ==========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "TÍCH HỢP HỆ THỐNG — SƠ ĐỒ LUỒNG DỮ LIỆU HAI CHIỀU (UPLINK & DOWNLINK)",
               "Kiến Trúc Điều Phối Dữ Liệu Thời Gian Thực & Cơ Chế Khóa An Toàn PCCC (Safety Interlock Override)")
    add_footer(s6, 6, 8)

    col_w6_1 = 3.75
    col_w6_2 = 3.75
    col_w6_3 = 3.83
    gap_6 = 0.20
    y_6 = 1.10
    h_6 = 5.85

    # Cột 1: Luồng Uplink
    x6_1 = 0.8
    add_card(s6, x6_1, y_6, col_w6_1, h_6, bg_color=CARD_BG, border_color=TECH_BLUE, border_width=1.5)
    hb_u = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x6_1 + 0.08), Inches(y_6 + 0.08), Inches(col_w6_1 - 0.16), Inches(0.48))
    hb_u.fill.solid()
    hb_u.fill.fore_color.rgb = TECH_BLUE
    hb_u.line.fill.background()
    p = hb_u.text_frame.paragraphs[0]
    p.text = "1. LUỒNG UPLINK (TELEMETRY & BÁO ĐỘNG)"
    p.font.bold = True
    p.font.size = Pt(11.2)
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.alignment = PP_ALIGN.CENTER

    tb_u = s6.shapes.add_textbox(Inches(x6_1 + 0.12), Inches(y_6 + 0.60), Inches(col_w6_1 - 0.24), Inches(h_6 - 0.68))
    tf_u = tb_u.text_frame
    tf_u.word_wrap = True
    items_up = [
        ("Thu thập cảm biến", "Cảm biến MQ-2 đo nồng độ khói khí cháy và DHT22 đo nhiệt ẩm liên tục chu kỳ 1s trên Core 1 ESP32 theo đúng chu kỳ chuyển đổi ADC."),
        ("Lọc số & Đánh giá FSM", "Bộ lọc EMA (alpha=0.2) làm mịn tín hiệu đo, triệt tiêu xung gai nhiễu; máy trạng thái FSM phân cấp rủi ro SAFE / WARN / ALARM tức thời."),
        ("Publish Telemetry 2s", "ESP32 đóng gói chuỗi JSON chuẩn RFC 8259 gửi lên topic Nhom09/smoke/telemetry (QoS 0) định kỳ 2s bảo đảm thông suốt đường truyền."),
        ("Ingest & Caching", "Collect Service trên Server tiếp nhận gói tin, ghi nhận MySQL (<5ms) và cập nhật tức thời Redis Cache phục vụ Web Dashboard không nghẽn."),
        ("Báo động Telegram (<1.2s)", "Khi phát hiện rủi ro cháy khẩn cấp (Khói ≥400 PPM hoặc dT/dt ≥3°C/phút), Server kích hoạt Bot Telegram API gửi tin nhắn cảnh báo đa kênh.")
    ]
    for lbl, desc in items_up:
        p = tf_u.add_paragraph()
        p.space_before = Pt(13.0)
        r1 = p.add_run()
        r1.text = "▶ " + lbl + ": "
        r1.font.bold = True
        r1.font.size = Pt(11.2)
        r1.font.color.rgb = TECH_BLUE
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(10.8)
        r2.font.color.rgb = SLATE_DARK

    # Cột 2: Luồng Downlink
    x6_2 = x6_1 + col_w6_1 + gap_6
    add_card(s6, x6_2, y_6, col_w6_2, h_6, bg_color=CARD_BG, border_color=NAVY_PRIMARY, border_width=1.5)
    hb_d = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x6_2 + 0.08), Inches(y_6 + 0.08), Inches(col_w6_2 - 0.16), Inches(0.48))
    hb_d.fill.solid()
    hb_d.fill.fore_color.rgb = NAVY_PRIMARY
    hb_d.line.fill.background()
    p = hb_d.text_frame.paragraphs[0]
    p.text = "2. LUỒNG DOWNLINK (LỆNH ĐIỀU KHIỂN & ACK)"
    p.font.bold = True
    p.font.size = Pt(11.2)
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.alignment = PP_ALIGN.CENTER

    tb_d = s6.shapes.add_textbox(Inches(x6_2 + 0.12), Inches(y_6 + 0.60), Inches(col_w6_2 - 0.24), Inches(h_6 - 0.68))
    tf_d = tb_d.text_frame
    tf_d.word_wrap = True
    items_down = [
        ("Mệnh lệnh từ Web UI", "Người vận hành thao tác bấm nút Bật/Tắt quạt cưỡng bức hoặc thay đổi cấu hình ngưỡng nhạy Ngày/Đêm trực tiếp trên Web Dashboard."),
        ("Kiểm duyệt RBAC", "Control Service xác thực quyền hạn tài khoản (Admin/Operator) và kiểm tra tính hợp lệ của Token phiên làm việc bảo mật cao."),
        ("Publish lệnh Downlink", "Server phát lệnh điều khiển có cấu trúc xuống topic Nhom09/smoke/cmd/fan với mức QoS 1 bảo đảm đến đích tin cậy."),
        ("Kích hoạt phần cứng", "ESP32 nhận lệnh qua MQTT, ngắt Core 1 kéo mức logic chân GPIO đóng cắt Relay 5V kích hoạt quạt hút khói 12V làm mát."),
        ("Phản hồi gói tin ACK", "ESP32 lập tức phát gói tin xác nhận lên Nhom09/smoke/status (QoS 1, RTT khứ hồi <120ms), Web UI đồng bộ ngay trạng thái thực thi.")
    ]
    for lbl, desc in items_down:
        p = tf_d.add_paragraph()
        p.space_before = Pt(13.0)
        r1 = p.add_run()
        r1.text = "▶ " + lbl + ": "
        r1.font.bold = True
        r1.font.size = Pt(11.2)
        r1.font.color.rgb = NAVY_PRIMARY
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(10.8)
        r2.font.color.rgb = SLATE_DARK

    # Cột 3: Khóa An Toàn Safety Interlock
    x6_3 = x6_2 + col_w6_2 + gap_6
    add_card(s6, x6_3, y_6, col_w6_3, h_6, bg_color=CARD_BG, border_color=ALARM_RED, border_width=1.5)
    hb_g = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x6_3 + 0.08), Inches(y_6 + 0.08), Inches(col_w6_3 - 0.16), Inches(0.48))
    hb_g.fill.solid()
    hb_g.fill.fore_color.rgb = ALARM_RED
    hb_g.line.fill.background()
    p = hb_g.text_frame.paragraphs[0]
    p.text = "3. KHÓA AN TOÀN PCCC (SAFETY OVERRIDE)"
    p.font.bold = True
    p.font.size = Pt(11.2)
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.alignment = PP_ALIGN.CENTER

    tb_g = s6.shapes.add_textbox(Inches(x6_3 + 0.12), Inches(y_6 + 0.60), Inches(col_w6_3 - 0.24), Inches(h_6 - 0.68))
    tf_g = tb_g.text_frame
    tf_g.word_wrap = True
    items_guard = [
        ("Nguyên tắc PCCC tối thượng", "Trong tiêu chuẩn an toàn phòng cháy, việc bảo toàn tính mạng con người là ưu tiên tuyệt đối hơn mọi mệnh lệnh can thiệp từ xa."),
        ("Khóa cưỡng bức Interlock", "Khi nồng độ khói chạm ngưỡng ALARM (≥400 PPM), cả Firmware ESP32 và Server đều tự động kích hoạt Khóa an toàn PCCC."),
        ("Từ chối lệnh tắt quạt", "Mọi lệnh Downlink yêu cầu tắt quạt (FAN = OFF) gửi từ Web/App đều bị TỪ CHỐI TUYỆT ĐỐI kèm mã lỗi ERR_SAFETY_INTERLOCK_OVERRIDE."),
        ("Ngắt còi có kiểm soát (Mute)", "Lệnh tắt còi chỉ có hiệu lực tạm thời tối đa 180 giây phục vụ công tác cứu hộ; sau 180s nếu còn khói còi sẽ tự động hú lại."),
        ("Khôi phục tự động an toàn", "Chỉ khi nồng độ khói hạ hẳn dưới 300 PPM (vùng trễ Hysteresis an toàn), quyền can thiệp thủ công mới được trao trả cho người dùng.")
    ]
    for lbl, desc in items_guard:
        p = tf_g.add_paragraph()
        p.space_before = Pt(13.0)
        r1 = p.add_run()
        r1.text = "▶ " + lbl + ": "
        r1.font.bold = True
        r1.font.size = Pt(11.2)
        r1.font.color.rgb = ALARM_RED
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(10.8)
        r2.font.color.rgb = SLATE_DARK


    # ==========================================================================
    # SLIDE 7: PART 3 - WEB SERVER APP (4 TRỤ CỘT CHỨC NĂNG CÔ ĐỌNG)
    # ==========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "PART 3: WEB SERVER APP — TẦNG ỨNG DỤNG, ĐIỀU KHIỂN & PHÂN TÍCH DỮ LIỆU",
               "Giao Diện Dashboard Thời Gian Thực, Quản Trị CSDL, Điều Khiển 2 Chiều & Cảnh Báo Telegram")
    add_footer(s7, 7, 8)

    col_w7 = 2.78
    gap_w7 = 0.20
    y_p7 = 1.10
    h_p7 = 5.85

    pillars = [
        ("1. DATA REPRESENTATION", TECH_BLUE, [
            ("Mục Tiêu Lõi", "Trực quan hóa tức thời qua WebSockets & MQTT-over-WS độ trễ <1s."),
            ("Radial Gauge", "Đồng hồ đo nồng độ khói MQ-2 (0-1000 ppm) với 3 dải màu cảnh báo."),
            ("Chart.js Real-Time", "Vẽ đồ thị tương quan nhiệt độ (°C) và độ ẩm (%RH) liên tục theo thời gian thực."),
            ("Live Status Badges", "Cập nhật nhịp tim thiết bị (Online/Offline) và trạng thái quạt hút (ON/OFF)."),
            ("UX Responsive", "Thiết kế Glassmorphism công nghệ cao, hiển thị hoàn hảo trên PC & Mobile.")
        ]),
        ("2. DATA MANAGEMENT", NAVY_PRIMARY, [
            ("Mục Tiêu Lõi", "Lưu trữ, tra cứu và kiểm toán lịch sử vận hành hệ thống toàn vẹn."),
            ("RESTful API", "Truy vấn MySQL tối ưu bằng chỉ mục INDEX(timestamp, device_id) phản hồi <10ms."),
            ("Bộ Lọc Đa Mốc", "Tra cứu linh hoạt theo mốc 1h, 24h, 7 ngày hoặc lọc theo cấp độ rủi ro cháy."),
            ("Xuất Báo Cáo", "Kết xuất toàn bộ nhật ký sự kiện ra CSV, Excel (.xlsx) và PDF nghiệm thu PCCC."),
            ("Data Retention", "Tự động phân vùng và tổng hợp dữ liệu cũ, chống phình to dung lượng CSDL.")
        ]),
        ("3. CONTROL GUI", ALARM_RED, [
            ("Mục Tiêu Lõi", "Cho phép người quản trị can thiệp và điều phối phần cứng ngoại vi an toàn."),
            ("Toggle Chế Độ", "Chuyển đổi linh hoạt giữa Tự động (Auto theo FSM) và Điều khiển thủ công (Manual)."),
            ("Kích Hoạt Chấp Hành", "Nút bấm bật/tắt cưỡng bức quạt hút 12V và chuông còi báo động kèm gói tin ACK."),
            ("Cấu Hình Ngưỡng", "Thiết lập ngưỡng cảnh báo khói ngày/đêm trực tiếp trên Web không cần nạp lại code."),
            ("Kill-Switch Khẩn", "Nút ngắt khẩn cấp toàn trạm để cô lập rủi ro khi có sự cố kỹ thuật bảo trì.")
        ]),
        ("4. DATA ANALYSIS", AMBER_GOLD, [
            ("Mục Tiêu Lõi", "Ứng dụng thuật toán phân tích thông minh nhận diện nguy cơ cháy sớm đa kênh."),
            ("Nhận Diện Cháy Sớm", "Kết hợp đạo hàm tốc độ tăng khói (ΔPPM/Δt >15%) và nhiệt độ môi trường (>50°C)."),
            ("Triệt Tiêu Báo Ảo", "Bộ lọc số EMA và ma trận tương quan loại trừ hoàn toàn khói thuốc lá thoáng qua."),
            ("Bot Telegram API", "Tự động gửi tin nhắn báo động khẩn kèm đồ thị và vị trí trạm về đội PCCC (<1s)."),
            ("Báo Động Đa Tầng", "Đồng bộ âm thanh còi hú Web Audio API, pop-up cảnh báo màn hình và loa đèn.")
        ])
    ]

    for idx, (title, color, items) in enumerate(pillars):
        x_pos = 0.8 + idx * (col_w7 + gap_w7)
        add_card(s7, x_pos, y_p7, col_w7, h_p7, bg_color=CARD_BG, border_color=color, border_width=1.5)

        h_box = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x_pos + 0.08), Inches(y_p7 + 0.08), Inches(col_w7 - 0.16), Inches(0.44))
        h_box.fill.solid()
        h_box.fill.fore_color.rgb = color
        h_box.line.fill.background()
        ph = h_box.text_frame.paragraphs[0]
        ph.text = title
        ph.font.bold = True
        ph.font.size = Pt(10.5)
        ph.font.color.rgb = RGBColor(255, 255, 255)
        ph.alignment = PP_ALIGN.CENTER

        tb_body = s7.shapes.add_textbox(Inches(x_pos + 0.08), Inches(y_p7 + 0.58), Inches(col_w7 - 0.16), Inches(h_p7 - 0.65))
        tf_b = tb_body.text_frame
        tf_b.word_wrap = True
        for lbl, desc in items:
            p = tf_b.add_paragraph()
            p.space_before = Pt(8.0)
            r1 = p.add_run()
            r1.text = "▶ " + lbl + ": "
            r1.font.bold = True
            r1.font.size = Pt(10.2)
            r1.font.color.rgb = color
            r2 = p.add_run()
            r2.text = desc
            r2.font.size = Pt(9.8)
            r2.font.color.rgb = SLATE_DARK


    # ==========================================================================
    # SLIDE 8: KẾT QUẢ THỰC NGHIỆM - BENCHMARK HIỆU NĂNG & TEST CASES M4
    # ==========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "KẾT QUẢ THỰC NGHIỆM — BENCHMARK HIỆU NĂNG HỆ THỐNG & NGHIỆM THU MILESTONE M4",
               "Ma Trận 16 Test Cases Tích Hợp Pass 100%, Đo Lường Độ Trễ Mạng RTT & Độ Tin Cậy Vận Hành")
    add_footer(s8, 8, 8)

    # 4 Khối kết quả thực nghiệm với kích thước chuẩn xác
    # Khối 1: Đo lường độ trễ kỹ thuật (Trên Trái)
    add_card(s8, x_l, y_t, c_w, c_h_top, bg_color=CARD_BG, border_color=TECH_BLUE, border_width=1.5)
    hb_r1 = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x_l + 0.08), Inches(y_t + 0.08), Inches(c_w - 0.16), Inches(0.36))
    hb_r1.fill.solid()
    hb_r1.fill.fore_color.rgb = TECH_BLUE
    hb_r1.line.fill.background()
    p = hb_r1.text_frame.paragraphs[0]
    p.text = "1. ĐO LƯỜNG ĐỘ TRỄ KỸ THUẬT (LATENCY & RTT BENCHMARK)"
    p.font.bold = True
    p.font.size = Pt(10.5)
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.alignment = PP_ALIGN.CENTER

    tb_r1 = s8.shapes.add_textbox(Inches(x_l + 0.10), Inches(y_t + 0.46), Inches(c_w - 0.20), Inches(c_h_top - 0.50))
    tf_r1 = tb_r1.text_frame
    tf_r1.word_wrap = True
    tf_r1.margin_top = Inches(0.02)
    tf_r1.margin_bottom = Inches(0.02)
    items_r1 = [
        ("Uplink Telemetry Latency", "185ms (Sensor -> ESP32 -> Broker -> Web hiển thị, target <1000ms, vượt 81.5%)."),
        ("Downlink RTT Round-Trip", "115ms (Web click -> ESP32 đóng quạt -> Web ACK, target <500ms, vượt 77%)."),
        ("Báo động Telegram Bot", "1.15s (Phát hiện cháy khẩn cấp -> Bot gửi tin nhắn cảnh báo PCCC, target <3s)."),
        ("Truy vấn CSDL MySQL", "<8ms cho truy vấn 10.000 bản ghi lịch sử nhờ bộ chỉ mục INDEX(timestamp, device_id)."),
        ("Tỷ lệ rơi gói tin (Loss)", "0.00% trong điều kiện kiểm thử liên tục 4 giờ với 7.200 gói tin gửi liên tục.")
    ]
    for lbl, desc in items_r1:
        p = tf_r1.add_paragraph()
        p.space_before = Pt(3.0)
        r1 = p.add_run()
        r1.text = "• " + lbl + ": "
        r1.font.bold = True
        r1.font.size = Pt(9.8)
        r1.font.color.rgb = TECH_BLUE
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = SLATE_DARK

    # Khối 2: Ma trận 16 Test Cases tích hợp (Trên Phải)
    add_card(s8, x_r, y_t, c_w, c_h_top, bg_color=CARD_BG, border_color=SUCCESS_GREEN, border_width=1.5)
    hb_r2 = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x_r + 0.08), Inches(y_t + 0.08), Inches(c_w - 0.16), Inches(0.36))
    hb_r2.fill.solid()
    hb_r2.fill.fore_color.rgb = SUCCESS_GREEN
    hb_r2.line.fill.background()
    p = hb_r2.text_frame.paragraphs[0]
    p.text = "2. MA TRẬN 16 TEST CASES TÍCH HỢP (MILESTONE M4 PASS 100%)"
    p.font.bold = True
    p.font.size = Pt(10.5)
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.alignment = PP_ALIGN.CENTER

    tb_r2 = s8.shapes.add_textbox(Inches(x_r + 0.10), Inches(y_t + 0.46), Inches(c_w - 0.20), Inches(c_h_top - 0.50))
    tf_r2 = tb_r2.text_frame
    tf_r2.word_wrap = True
    tf_r2.margin_top = Inches(0.02)
    tf_r2.margin_bottom = Inches(0.02)
    items_r2 = [
        ("Nhóm TC 01-04 (Telemetry & FSM)", "Pass 4/4 (100%): Kiểm thử đọc ADC, lọc số EMA, chuyển trạng thái FSM và gửi JSON RFC 8259."),
        ("Nhóm TC 05-08 (Control & ACK)", "Pass 4/4 (100%): Kiểm thử bật/tắt quạt cưỡng bức, Mute còi 180s, đổi ngưỡng Day/Night và nhận ACK."),
        ("Nhóm TC 09-12 (Safety Guard)", "Pass 4/4 (100%): Kiểm thử khóa an toàn PCCC, từ chối lệnh tắt quạt khi ALARM, duy trì thông gió."),
        ("Nhóm TC 13-16 (Mất Mạng & Replay)", "Pass 4/4 (100%): Kiểm thử ghi 20 bản ghi đệm vòng SPIFFS, xả đệm replay và cơ chế LWT di chúc."),
        ("Đánh giá Milestone M4", "Hoàn thành 100% cam kết tiến độ tích hợp hệ thống End-to-End Tuần 8.")
    ]
    for lbl, desc in items_r2:
        p = tf_r2.add_paragraph()
        p.space_before = Pt(3.0)
        r1 = p.add_run()
        r1.text = "• " + lbl + ": "
        r1.font.bold = True
        r1.font.size = Pt(9.8)
        r1.font.color.rgb = SUCCESS_GREEN
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = SLATE_DARK

    # Khối 3: Tính Bền Vững & Khả Năng Mở Rộng Fleet (Dưới Trái)
    add_card(s8, x_l, y_b, c_w, c_h_bot, bg_color=CARD_BG, border_color=NAVY_PRIMARY, border_width=1.5)
    hb_r3 = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x_l + 0.08), Inches(y_b + 0.08), Inches(c_w - 0.16), Inches(0.36))
    hb_r3.fill.solid()
    hb_r3.fill.fore_color.rgb = NAVY_PRIMARY
    hb_r3.line.fill.background()
    p = hb_r3.text_frame.paragraphs[0]
    p.text = "3. TÍNH BỀN VỮNG MẠNG & KHẢ NĂNG MỞ RỘNG (FLEET SCALE)"
    p.font.bold = True
    p.font.size = Pt(10.5)
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.alignment = PP_ALIGN.CENTER

    tb_r3 = s8.shapes.add_textbox(Inches(x_l + 0.10), Inches(y_b + 0.46), Inches(c_w - 0.20), Inches(c_h_bot - 0.50))
    tf_r3 = tb_r3.text_frame
    tf_r3.word_wrap = True
    tf_r3.margin_top = Inches(0.02)
    tf_r3.margin_bottom = Inches(0.02)
    items_r3 = [
        ("Cơ chế LWT Di chúc (Retained)", "Broker tự động phát tín hiệu OFFLINE sau 60s mất socket ping, thông báo Web & Telegram tức thời."),
        ("Tự phục hồi mạng (Auto-Reconnect)", "ESP32 tự động thăm dò và tái lập kết nối Wi-Fi/Broker trong vòng 5s không cần người can thiệp."),
        ("Đồng bộ dữ liệu ngoại tuyến", "Xả toàn vẹn 20 bản ghi sự cố sau phục hồi kết nối, bảo đảm không thất thoát dữ liệu kiểm toán PCCC."),
        ("Khả năng mở rộng quy mô (Scale)", "Topic phân cấp cho phép nhân bản lên 100+ cảm biến tòa nhà: Nhom09/smoke/{bldg}/{floor}/{dev_id}."),
        ("Kiến trúc vi dịch vụ Stateless", "Dễ dàng nâng cấp backend chạy Docker Container hoặc Kubernetes phân tải.")
    ]
    for lbl, desc in items_r3:
        p = tf_r3.add_paragraph()
        p.space_before = Pt(3.0)
        r1 = p.add_run()
        r1.text = "• " + lbl + ": "
        r1.font.bold = True
        r1.font.size = Pt(9.8)
        r1.font.color.rgb = NAVY_PRIMARY
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = SLATE_DARK

    # Khối 4: Tổng Kết Nghiệm Thu & Khả Năng Ứng Dụng (Dưới Phải)
    add_card(s8, x_r, y_b, c_w, c_h_bot, bg_color=CARD_BG, border_color=AMBER_GOLD, border_width=1.5)
    hb_r4 = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x_r + 0.08), Inches(y_b + 0.08), Inches(c_w - 0.16), Inches(0.36))
    hb_r4.fill.solid()
    hb_r4.fill.fore_color.rgb = AMBER_GOLD
    hb_r4.line.fill.background()
    p = hb_r4.text_frame.paragraphs[0]
    p.text = "4. TỔNG KẾT NGHIỆM THU ĐỒ ÁN & TÍNH ỨNG DỤNG THỰC TẾ"
    p.font.bold = True
    p.font.size = Pt(10.5)
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.alignment = PP_ALIGN.CENTER

    tb_r4 = s8.shapes.add_textbox(Inches(x_r + 0.10), Inches(y_b + 0.46), Inches(c_w - 0.20), Inches(c_h_bot - 0.50))
    tf_r4 = tb_r4.text_frame
    tf_r4.word_wrap = True
    tf_r4.margin_top = Inches(0.02)
    tf_r4.margin_bottom = Inches(0.02)
    items_r4 = [
        ("Nghiệm thu 8 tuần (60h)", "Hoàn thành 100% mục tiêu môn học IT4735 từ Milestone M1 (Phần cứng) đến M4 (Tích hợp E2E)."),
        ("Hiệu quả kinh tế vượt trội", "Tổng chi phí vật tư chỉ ~720.000 VNĐ, rẻ hơn 70% so với tủ báo cháy trung tâm công nghiệp truyền thống."),
        ("Tính sẵn sàng triển khai", "Thiết kế vỏ hộp IP54 chống cháy, cách ly quang an toàn, phù hợp chung cư mini, phòng trọ, xưởng may."),
        ("Khả năng tích hợp mở rộng", "Sẵn sàng mở rộng tích hợp cảm biến nhiệt độ gia tăng và liên kết van xả nước chữa cháy tự động."),
        ("Sẵn sàng bảo vệ trước Hội đồng", "Đầy đủ mã nguồn GitHub, kịch bản MQTTX, dữ liệu đo kiểm và tài liệu kỹ thuật hoàn chỉnh.")
    ]
    for lbl, desc in items_r4:
        p = tf_r4.add_paragraph()
        p.space_before = Pt(3.0)
        r1 = p.add_run()
        r1.text = "• " + lbl + ": "
        r1.font.bold = True
        r1.font.size = Pt(9.8)
        r1.font.color.rgb = AMBER_GOLD
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = SLATE_DARK


    # Lưu trực tiếp vào file mục tiêu (KHÔNG TẠO BACKUP theo yêu cầu người dùng)
    output_path = r"e:\IoT\DoAn\docs\pptx\Bao_Cao_He_Thong_IoT_4_Slides_Nhom04_Chuan.pptx"
    prs.save(output_path)
    print(f"[THÀNH CÔNG] Đã ghi đè trực tiếp toàn bộ 8 slides chuẩn hóa vào: {output_path}")

if __name__ == "__main__":
    build_full_8_slides()
