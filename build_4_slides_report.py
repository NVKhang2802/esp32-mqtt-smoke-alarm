# -*- coding: utf-8 -*-
"""
Script tự động khởi tạo Slide Báo Cáo PowerPoint (4 Slides) - Tối Ưu Cho Thuyết Trình 3 Phút
Đề tài: Hệ Thống Báo Khói Cảnh Báo Sớm - Nhóm 04 (N09)
Môn học: IT4735 - IoT và Ứng dụng - Khoa CNTT, ĐH Công Thương TP.HCM (HUIT)

Cấu trúc chuẩn hóa 4 slide:
- Slide 1: Trang bìa (Title, Nhóm 04, Danh sách thành viên MSSV & 3 Part khái quát)
- Slide 2: Part 1 - Device (ESP32) & Bảng BOM Chi Tiết Từng Con Ốc Nhỏ Nhất (Giữ nguyên bảng BOM)
- Slide 3: Part 2 - MQTT Services on Server & Quy Chuẩn Topic Phân Cấp (Topic Matrix, Rationale, 4 Services)
- Slide 4: Part 3 - Web Server App (4 Trụ Cột: Representation, Management, GUI, Analysis)
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
    """Tạo thanh tiêu đề chuẩn mực ở đầu mỗi slide nội dung"""
    # Top highlight bar
    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.08))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = TECH_BLUE
    top_bar.line.fill.background()

    # Category badge
    cat_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.24), Inches(7.5), Inches(0.32))
    cat_box.fill.solid()
    cat_box.fill.fore_color.rgb = TECH_BLUE_LIGHT
    cat_box.line.color.rgb = TECH_BLUE_BORDER
    cat_box.line.width = Pt(1)
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    p_c = tf_c.paragraphs[0]
    p_c.text = category_text.upper()
    p_c.font.name = FONT_HEADING
    p_c.font.size = Pt(9.5)
    p_c.font.bold = True
    p_c.font.color.rgb = TECH_BLUE

    # Title text
    title_box = slide.shapes.add_textbox(Inches(0.75), Inches(0.58), Inches(11.8), Inches(0.60))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(19)
    p_t.font.bold = True
    p_t.font.color.rgb = NAVY_PRIMARY

def add_footer(slide, current_idx, total_slides=4):
    """Tạo chân trang chuẩn phong cách báo cáo đồ án"""
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(7.05), Inches(11.733), Inches(0.015))
    line.fill.solid()
    line.fill.fore_color.rgb = RGBColor(226, 232, 240)
    line.line.fill.background()

    tb_left = slide.shapes.add_textbox(Inches(0.8), Inches(7.08), Inches(9.0), Inches(0.35))
    tf_l = tb_left.text_frame
    p_l = tf_l.paragraphs[0]
    p_l.text = "IT4735 - IoT & Ứng Dụng • Đề tài: Hệ Thống Báo Khói Cảnh Báo Sớm • Nhóm 04 (Lớp N09) • HUIT"
    p_l.font.name = FONT_BODY
    p_l.font.size = Pt(8.5)
    p_l.font.color.rgb = SLATE_MUTED

    tb_right = slide.shapes.add_textbox(Inches(10.5), Inches(7.08), Inches(2.0), Inches(0.35))
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

def format_cell(cell, text, font_size=7.5, bold=False, color=SLATE_DARK, bg_color=None, align=PP_ALIGN.LEFT):
    cell.text = text
    if bg_color:
        cell.fill.solid()
        cell.fill.fore_color.rgb = bg_color
    cell.margin_left = Inches(0.05)
    cell.margin_right = Inches(0.05)
    cell.margin_top = Inches(0.03)
    cell.margin_bottom = Inches(0.03)
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    for p in cell.text_frame.paragraphs:
        p.alignment = align
        for r in p.runs:
            r.font.name = FONT_BODY
            r.font.size = Pt(font_size)
            r.font.bold = bold
            r.font.color.rgb = color

# ==============================================================================
# XÂY DỰNG TOÀN BỘ 4 SLIDE (TỐI ƯU 3 PHÚT)
# ==============================================================================
def build_report_presentation():
    prs = create_presentation()
    blank_layout = prs.slide_layouts[6]

    # ==========================================================================
    # SLIDE 1: TRANG BÌA (COVER SLIDE)
    # ==========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    # Nền tối công nghệ sang trọng
    add_card(s1, 0, 0, 13.333, 7.5, bg_color=NAVY_DARK, border_color=None)
    # Dải màu xanh accent viền bên trái
    add_card(s1, 0, 0, 0.35, 7.5, bg_color=CYAN_ACCENT, border_color=None)

    # Khối thông tin Đơn vị Đào tạo
    tb_u = s1.shapes.add_textbox(Inches(0.9), Inches(0.48), Inches(11.5), Inches(0.75))
    tf_u = tb_u.text_frame
    p_u1 = tf_u.paragraphs[0]
    p_u1.text = "BỘ CÔNG THƯƠNG  •  TRƯỜNG ĐẠI HỌC CÔNG THƯƠNG TP. HỒ CHÍ MINH (HUIT)"
    p_u1.font.name = FONT_HEADING
    p_u1.font.size = Pt(11)
    p_u1.font.bold = True
    p_u1.font.color.rgb = CYAN_ACCENT

    p_u2 = tf_u.add_paragraph()
    p_u2.text = "KHOA CÔNG NGHỆ THÔNG TIN  •  BỘ MÔN MẠNG & AN TOÀN THÔNG TIN"
    p_u2.font.name = FONT_BODY
    p_u2.font.size = Pt(9.5)
    p_u2.font.color.rgb = RGBColor(180, 205, 230)

    p_u3 = tf_u.add_paragraph()
    p_u3.text = "HỌC PHẦN: IT4735 — INTERNET OF THINGS (IoT) VÀ ỨNG DỤNG"
    p_u3.font.name = FONT_BODY
    p_u3.font.size = Pt(9.5)
    p_u3.font.bold = True
    p_u3.font.color.rgb = RGBColor(220, 235, 252)

    # Tiêu đề chính đề tài
    tb_title = s1.shapes.add_textbox(Inches(0.9), Inches(1.45), Inches(11.5), Inches(1.50))
    tf_t = tb_title.text_frame
    p_t0 = tf_t.paragraphs[0]
    p_t0.text = "BÁO CÁO THIẾT KẾ & HIỆN THỰC HỆ THỐNG IOT HOÀN CHỈNH (3 PHÚT)"
    p_t0.font.name = FONT_HEADING
    p_t0.font.size = Pt(13)
    p_t0.font.bold = True
    p_t0.font.color.rgb = AMBER_GOLD

    p_t1 = tf_t.add_paragraph()
    p_t1.text = "HỆ THỐNG BÁO KHÓI CẢNH BÁO SỚM"
    p_t1.font.name = FONT_HEADING
    p_t1.font.size = Pt(30)
    p_t1.font.bold = True
    p_t1.font.color.rgb = RGBColor(255, 255, 255)

    p_t2 = tf_t.add_paragraph()
    p_t2.text = "Smart Smoke & Fire Early Warning System — Tích Hợp Đầy Đủ 3 Tầng Kỹ Thuật"
    p_t2.font.name = FONT_BODY
    p_t2.font.size = Pt(12)
    p_t2.font.color.rgb = RGBColor(200, 220, 240)

    # KHỐI THÔNG TIN NHÓM & DANH SÁCH THÀNH VIÊN MSSV (ĐẦY ĐỦ RÕ RÀNG)
    add_card(s1, 0.9, 3.05, 11.533, 1.35, bg_color=RGBColor(24, 38, 64), border_color=CYAN_ACCENT, border_width=1.5)
    tb_team = s1.shapes.add_textbox(Inches(1.05), Inches(3.12), Inches(11.233), Inches(1.20))
    tf_team = tb_team.text_frame
    
    p_tm0 = tf_team.paragraphs[0]
    p_tm0.text = "NHÓM THỰC HIỆN: NHÓM 04  |  LỚP HỌC PHẦN: N09"
    p_tm0.font.name = FONT_HEADING
    p_tm0.font.size = Pt(11)
    p_tm0.font.bold = True
    p_tm0.font.color.rgb = AMBER_GOLD

    p_tm1 = tf_team.add_paragraph()
    p_tm1.text = "• 1. Nguyễn Vĩnh Khang   —   MSSV: 2001230381   (Trưởng nhóm: Firmware ESP32, FSM & Tích Hợp)"
    p_tm1.font.size = Pt(10)
    p_tm1.font.bold = True
    p_tm1.font.color.rgb = RGBColor(255, 255, 255)

    p_tm2 = tf_team.add_paragraph()
    p_tm2.text = "• 2. Nguyễn Văn Đức       —   MSSV: 2001230186   (Thành viên: Thiết Kế Topic Tree, Payload JSON & Downlink)"
    p_tm2.font.size = Pt(10)
    p_tm2.font.bold = True
    p_tm2.font.color.rgb = RGBColor(255, 255, 255)

    p_tm3 = tf_team.add_paragraph()
    p_tm3.text = "• 3. Nguyễn Văn Mãnh     —   MSSV: 2001230503   (Thành viên: Khóa An Toàn Safety Guard & Web Dashboard)"
    p_tm3.font.size = Pt(10)
    p_tm3.font.bold = True
    p_tm3.font.color.rgb = RGBColor(255, 255, 255)

    # 3 KHỐI CARD KHÁI QUÁT 3 PHẦN NỘI DUNG (ĐÚNG 3 DÒNG TÊN PART, KHÔNG GHI CHI TIẾT)
    col_w = 3.65
    gap = 0.28
    y_cards = 4.60
    h_cards = 1.90

    # Card 1: Part 1
    add_card(s1, 0.9, y_cards, col_w, h_cards, bg_color=RGBColor(24, 38, 64), border_color=TECH_BLUE, border_width=1.5)
    tb_c1 = s1.shapes.add_textbox(Inches(1.0), Inches(y_cards + 0.18), Inches(col_w - 0.2), Inches(h_cards - 0.36))
    tf_c1 = tb_c1.text_frame
    p_c1_h = tf_c1.paragraphs[0]
    p_c1_h.text = "PART 1: DEVICE (ESP32)"
    p_c1_h.font.bold = True
    p_c1_h.font.size = Pt(12)
    p_c1_h.font.color.rgb = CYAN_ACCENT

    p1_l1 = tf_c1.add_paragraph()
    p1_l1.space_before = Pt(8)
    p1_l1.text = "▶ 1. Thiết Kế Mạch Phần Cứng ESP32 & Cảm Biến"
    p1_l1.font.bold = True
    p1_l1.font.size = Pt(9.5)
    p1_l1.font.color.rgb = RGBColor(255, 255, 255)

    p1_l2 = tf_c1.add_paragraph()
    p1_l2.space_before = Pt(4)
    p1_l2.text = "▶ 2. Firmware FreeRTOS, Lọc Nhiễu EMA & Power Save"
    p1_l2.font.bold = True
    p1_l2.font.size = Pt(9.5)
    p1_l2.font.color.rgb = RGBColor(205, 225, 245)

    p1_l3 = tf_c1.add_paragraph()
    p1_l3.space_before = Pt(4)
    p1_l3.text = "▶ 3. Bảng BOM Chi Tiết Từng Con Ốc Nhỏ Nhất"
    p1_l3.font.bold = True
    p1_l3.font.size = Pt(9.5)
    p1_l3.font.color.rgb = AMBER_GOLD

    # Card 2: Part 2
    add_card(s1, 0.9 + col_w + gap, y_cards, col_w, h_cards, bg_color=RGBColor(24, 38, 64), border_color=TECH_BLUE, border_width=1.5)
    tb_c2 = s1.shapes.add_textbox(Inches(1.0 + col_w + gap), Inches(y_cards + 0.18), Inches(col_w - 0.2), Inches(h_cards - 0.36))
    tf_c2 = tb_c2.text_frame
    p_c2_h = tf_c2.paragraphs[0]
    p_c2_h.text = "PART 2: MQTT SERVICES"
    p_c2_h.font.bold = True
    p_c2_h.font.size = Pt(12)
    p_c2_h.font.color.rgb = AMBER_GOLD

    p2_l1 = tf_c2.add_paragraph()
    p2_l1.space_before = Pt(8)
    p2_l1.text = "▶ 1. Kiến Trúc Message Broker & Quy Chuẩn Phân Cấp"
    p2_l1.font.bold = True
    p2_l1.font.size = Pt(9.5)
    p2_l1.font.color.rgb = RGBColor(255, 255, 255)

    p2_l2 = tf_c2.add_paragraph()
    p2_l2.space_before = Pt(4)
    p2_l2.text = "▶ 2. Ma Trận Topic 2 Chiều, Rationale & Tác Dụng"
    p2_l2.font.bold = True
    p2_l2.font.size = Pt(9.5)
    p2_l2.font.color.rgb = RGBColor(205, 225, 245)

    p2_l3 = tf_c2.add_paragraph()
    p2_l3.space_before = Pt(4)
    p2_l3.text = "▶ 3. 4 Dịch Vụ: Auth, Collect, Control, Keep-Alive"
    p2_l3.font.bold = True
    p2_l3.font.size = Pt(9.5)
    p2_l3.font.color.rgb = CYAN_ACCENT

    # Card 3: Part 3
    add_card(s1, 0.9 + (col_w + gap)*2, y_cards, col_w, h_cards, bg_color=RGBColor(24, 38, 64), border_color=TECH_BLUE, border_width=1.5)
    tb_c3 = s1.shapes.add_textbox(Inches(1.0 + (col_w + gap)*2), Inches(y_cards + 0.18), Inches(col_w - 0.2), Inches(h_cards - 0.36))
    tf_c3 = tb_c3.text_frame
    p_c3_h = tf_c3.paragraphs[0]
    p_c3_h.text = "PART 3: WEB SERVER APP"
    p_c3_h.font.bold = True
    p_c3_h.font.size = Pt(12)
    p_c3_h.font.color.rgb = SUCCESS_GREEN

    p3_l1 = tf_c3.add_paragraph()
    p3_l1.space_before = Pt(8)
    p3_l1.text = "▶ 1. Data Representation: Radial Gauge & Live Chart"
    p3_l1.font.bold = True
    p3_l1.font.size = Pt(9.5)
    p3_l1.font.color.rgb = RGBColor(255, 255, 255)

    p3_l2 = tf_c3.add_paragraph()
    p3_l2.space_before = Pt(4)
    p3_l2.text = "▶ 2. Data Management: REST API & Quản Trị CSDL"
    p3_l2.font.bold = True
    p3_l2.font.size = Pt(9.5)
    p3_l2.font.color.rgb = RGBColor(205, 225, 245)

    p3_l3 = tf_c3.add_paragraph()
    p3_l3.space_before = Pt(4)
    p3_l3.text = "▶ 3. Control GUI & Data Analysis Báo Động Telegram"
    p3_l3.font.bold = True
    p3_l3.font.size = Pt(9.5)
    p3_l3.font.color.rgb = AMBER_GOLD

    # Thông tin chân slide bìa
    tb_meta = s1.shapes.add_textbox(Inches(0.9), Inches(6.65), Inches(11.5), Inches(0.4))
    tf_m = tb_meta.text_frame
    p_m = tf_m.paragraphs[0]
    p_m.text = "HỌC KỲ II - NĂM HỌC 2025-2026  |  KHOA CÔNG NGHỆ THÔNG TIN  |  ĐẠI HỌC CÔNG THƯƠNG TP. HỒ CHÍ MINH (HUIT)"
    p_m.font.size = Pt(9)
    p_m.font.color.rgb = RGBColor(160, 185, 215)


    # ==========================================================================
    # SLIDE 2: PART 1 - DEVICE (ESP32) & BẢNG BOM CHI TIẾT THỰC TẾ
    # ==========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "PART 1: DEVICE (ESP32) — THIẾT KẾ PHẦN CỨNG & BẢNG BOM VẬT TƯ THỰC TẾ",
               "Vi Điều Khiển ESP32 FreeRTOS, Thiết Kế Bo Mạch PCB 2 Lớp & Bảng BOM Chi Tiết Từng Con Ốc")
    add_footer(s2, 2, 4)

    # 2 Thẻ tổng quan Firmware & Hardware ở phía trên (Tinh gọn, sắc nét, súc tích)
    c_fw = add_card(s2, 0.8, 1.25, 5.75, 1.05, bg_color=TECH_BLUE_LIGHT, border_color=TECH_BLUE_BORDER)
    tb_fw = s2.shapes.add_textbox(Inches(0.9), Inches(1.28), Inches(5.55), Inches(0.98))
    tf_fw = tb_fw.text_frame
    p_fwh = tf_fw.paragraphs[0]
    p_fwh.text = "1. Kiến Trúc Firmware FreeRTOS & Xử Lý Tín Hiệu Số"
    p_fwh.font.bold = True
    p_fwh.font.size = Pt(10)
    p_fwh.font.color.rgb = NAVY_PRIMARY

    p_fw1 = tf_fw.add_paragraph()
    p_fw1.text = "• Dual-Core 240MHz: Core 0 (Wi-Fi / MQTT Client) • Core 1 (Sensors & Máy trạng thái FSM)."
    p_fw1.font.size = Pt(8.5)
    p_fw1.font.color.rgb = SLATE_DARK

    p_fw2 = tf_fw.add_paragraph()
    p_fw2.text = "• Task Collect 1s kèm Bộ lọc số EMA • Task Control ngắt khẩn <50ms • Ring Buffer SPIFFS khi rớt mạng."
    p_fw2.font.size = Pt(8.5)
    p_fw2.font.color.rgb = SLATE_DARK

    c_hw = add_card(s2, 6.78, 1.25, 5.75, 1.05, bg_color=RGBColor(254, 243, 199), border_color=RGBColor(251, 191, 36))
    tb_hw = s2.shapes.add_textbox(Inches(6.88), Inches(1.28), Inches(5.55), Inches(0.98))
    tf_hw = tb_hw.text_frame
    p_hwh = tf_hw.paragraphs[0]
    p_hwh.text = "2. Thiết Kế Mạch In PCB & Tiêu Chuẩn Cơ Khí Vỏ Hộp"
    p_hwh.font.bold = True
    p_hwh.font.size = Pt(10)
    p_hwh.font.color.rgb = RGBColor(146, 64, 14)

    p_hw1 = tf_hw.add_paragraph()
    p_hw1.text = "• PCB 2 lớp FR4 (100x70mm) mạ thiếc dập via GND • Cách ly quang PC817 chống sốc ngược cho ESP32."
    p_hw1.font.size = Pt(8.5)
    p_hw1.font.color.rgb = SLATE_DARK

    p_hw2 = tf_hw.add_paragraph()
    p_hw2.text = "• Vỏ hộp ABS IP54, Quạt hút 12V 80mm lưới sắt tổ ong, Cầu chì 2A & Gioăng cao su luồn dây cách điện."
    p_hw2.font.size = Pt(8.5)
    p_hw2.font.color.rgb = SLATE_DARK

    # BẢNG BOM CHI TIẾT - GIỮ NGUYÊN 100% 34 MỤC LINH KIỆN VÀ THÔNG SỐ
    bom_part1_data = [
        ("I", "KHỐI VI ĐIỀU KHIỂN, CẢM BIẾN & CƠ CẤU CHẤP HÀNH", "", "", "", True),
        ("1", "Bo mạch ESP32 DevKit V1", "30 chân, Dual-core 240MHz, Wi-Fi & BLE", "Xử lý FreeRTOS, MQTT Client", "Bo", "1", False),
        ("2", "Module Cảm biến khí/khói MQ-2", "Kèm bo LM393 vi chỉnh, ngõ ra AOUT & DOUT", "Đo nồng độ khói/LPG 200-10000ppm", "Module", "1", False),
        ("3", "Module Cảm biến nhiệt & ẩm DHT22", "AM2302 (Sai số: ±0.5°C, ±2% RH)", "Giám sát nguy cơ nhiệt độ cháy", "Module", "1", False),
        ("4", "Module Relay 1 kênh 5VDC", "Tiếp điểm 10A 250VAC/30VDC, cách ly Opto", "Đóng cắt quạt hút khói 12V", "Module", "1", False),
        ("5", "Còi chíp báo động (Active Buzzer)", "5VDC, âm lượng > 85dB", "Phát âm thanh báo cháy tại chỗ", "Cái", "1", False),
        ("6", "Đèn LED chỉ thị phi 5mm", "1 LED Đỏ (Báo động) + 1 LED Xanh (Nguồn)", "Báo trạng thái hệ thống", "Cái", "2", False),
        ("7", "Điện trở hạn dòng LED", "330 Ω — 1/4W, sai số 5%", "Bảo vệ LED khỏi quá dòng GPIO", "Con", "2", False),
        ("8", "Nút nhấn khẩn cấp / Test", "4 chân 12x12mm kèm nắp nhựa tròn", "Kích hoạt quạt khẩn/Test thủ công", "Cái", "1", False),
        ("9", "Điện trở kéo nút nhấn (Pull-up)", "10k Ω — 1/4W, sai số 5%", "Chống trôi mức logic chân GPIO", "Con", "1", False),
        ("II", "KHỐI NGUỒN CÔNG SUẤT & BẢO VỆ ĐIỆN NĂNG", "", "", "", True),
        ("10", "Adapter nguồn AC-DC", "Input 100-240VAC, Output 12VDC - 2A", "Cấp nguồn chính cho toàn trạm", "Bộ", "1", False),
        ("11", "Mạch hạ áp Buck DC-DC LM2596S", "In 12V, Out 5V - 3A (Hiệu suất 92%)", "Cấp nguồn 5V nuôi ESP32 & MQ-2", "Bo", "1", False),
        ("12", "Quạt hút khói làm mát tản nhiệt", "12VDC 0.18A (80x80x25mm) không chổi than", "Hút khói độc cưỡng bức ra ngoài", "Cái", "1", False),
        ("13", "Lưới thép bảo vệ quạt hút", "Sắt mạ Crom/Niken 80mm mắt tổ ong", "Ngăn dị vật lọt vào cánh quạt", "Cái", "1", False),
        ("14", "Cầu chì ống thủy tinh 5x20mm", "2A 250V tác động nhanh (Fast-blow)", "Bảo vệ ngắn mạch, chống cháy nổ", "Con", "1", False),
        ("15", "Hộp/Đế gắn cầu chì PCB", "Vỏ nhựa chống cháy 5x20mm có nắp đậy", "Gắn cố định cầu chì lên bo mạch", "Cái", "1", False),
        ("16", "Tụ hóa lọc nguồn đầu vào/ra", "100µF - 25V chịu nhiệt 105°C", "Chống sụt áp khi ESP32 bật Wi-Fi", "Con", "2", False),
        ("17", "Tụ gốm khử nhiễu cao tần", "100nF (104) - 50V", "Lọc xung nhiễu nguồn 5V/3.3V", "Con", "2", False),
        ("18", "Công tắc bập bênh nguồn", "KCD11 2 chân, 3A/250VAC", "Đóng ngắt nguồn vào thủ công", "Cái", "1", False)
    ]

    bom_part2_data = [
        ("III", "KHỐI ĐẤU NỐI, DÂY DẪN & SOCKET KỸ THUẬT", "", "", "", True),
        ("19", "Jack nguồn DC cái gắn vỏ", "Chuẩn 5.5 x 2.1mm chân vặn ốc có đai hãm", "Cắm jack adapter xuyên vỏ hộp", "Bộ", "1", False),
        ("20", "Cọc đấu dây vặn ốc KF301-2P", "Screw Terminal 2 chân, bước 5.0mm", "Đấu nguồn 12V, tiếp điểm quạt", "Cái", "3", False),
        ("21", "Cọc đấu dây vặn ốc KF301-3P", "Screw Terminal 3 chân, bước 5.0mm", "Đấu dây cảm biến và rơ-le", "Cái", "2", False),
        ("22", "Hàng rào cắm cái (Female Header)", "1x15 chân bước 2.54mm", "Socket tháo lắp ESP32 trên bo", "Thanh", "2", False),
        ("23", "Dây điện silicon chịu nhiệt 22AWG", "Đồng nhiều sợi mạ thiếc, vỏ silicon đỏ/đen", "Đi dây nguồn 12V và 5V tải dòng", "Mét", "1.5", False),
        ("24", "Dây cắm tín hiệu Dupont", "Đực - Cái 2.54mm (dài 20cm)", "Nối tín hiệu GPIO các module", "Sợi", "10", False),
        ("25", "Ống gen co nhiệt cách điện", "Phi 2mm, 4mm, 6mm Polyolefin chống cháy", "Bọc cách điện tuyệt đối mối hàn", "Mét", "0.5", False),
        ("IV", "CƠ KHÍ, VỎ HỘP & CHI TIẾT ỐC VÍT LẮP RÁP THỰC TẾ", "", "", "", True),
        ("26", "Vỏ hộp nhựa ABS chống cháy", "158 x 90 x 60mm, chuẩn kháng bụi IP54", "Chứa bảo vệ toàn bộ linh kiện", "Hộp", "1", False),
        ("27", "Bo mạch in 2 lớp (Main PCB)", "FR4 dày 1.6mm (100 x 70mm), mạ thiếc", "Tích hợp toàn bộ linh kiện cắm", "Tấm", "1", False),
        ("28", "Trụ đồng lục giác đực - cái", "Đồng thau ren M3 x 10mm (+ren đực 6mm)", "Đệm cách ly bo mạch với đáy hộp", "Cái", "8", False),
        ("29", "Ốc vít bake đầu dù bắt bo mạch", "Inox 304 không gỉ ren M3 x 6mm", "Siết cố định PCB vào trụ đồng", "Con", "8", False),
        ("30", "Đai ốc (Tán) khóa chân trụ đồng", "Inox 304 ren M3 tiêu chuẩn DIN934", "Khóa trụ đồng xuyên đáy vỏ hộp", "Con", "8", False),
        ("31", "Vòng đệm (Lông đền) nhựa Nylon", "Đệm phẳng M3 cách điện & chống xước", "Lót ốc chống cọ tróc mạch in", "Cái", "8", False),
        ("32", "Bu-lông & Đai ốc gắn quạt hút", "Bu-lông inox M4 x 35mm + tán M4 + đệm", "Bắt siết quạt 80mm vào nắp hộp", "Bộ", "4", False),
        ("33", "Vít nở & Tắc kê gắn tường", "Vít tự khoan M3.5 x 25mm + tắc kê phi 6", "Bắt cố định hộp lên tường PCCC", "Bộ", "4", False),
        ("34", "Gioăng cao su luồn dây (Grommet)", "Cao su chịu nhiệt phi 12mm", "Chống cứa đứt vỏ dây xuyên hộp", "Cái", "2", False)
    ]

    def render_bom_table(slide, left_in, top_in, width_in, height_in, data, table_title):
        t_box = slide.shapes.add_textbox(Inches(left_in), Inches(top_in - 0.28), Inches(width_in), Inches(0.28))
        tf_tb = t_box.text_frame
        p_tb = tf_tb.paragraphs[0]
        p_tb.text = table_title
        p_tb.font.name = FONT_HEADING
        p_tb.font.size = Pt(9.5)
        p_tb.font.bold = True
        p_tb.font.color.rgb = NAVY_PRIMARY

        rows_count = len(data) + 1
        cols_count = 6
        tbl_shape = slide.shapes.add_table(rows_count, cols_count, Inches(left_in), Inches(top_in), Inches(width_in), Inches(height_in))
        table = tbl_shape.table

        col_widths = [Inches(0.35), Inches(1.50), Inches(1.85), Inches(1.30), Inches(0.38), Inches(0.37)]
        for i, w in enumerate(col_widths):
            table.columns[i].width = w

        headers = ["STT", "Tên Linh Kiện & Vật Tư", "Thông Số Kỹ Thuật", "Vai Trò Thực Tế", "ĐVT", "SL"]
        for j, h in enumerate(headers):
            cell = table.cell(0, j)
            align = PP_ALIGN.CENTER if j in [0, 4, 5] else PP_ALIGN.LEFT
            format_cell(cell, h, font_size=7.5, bold=True, color=RGBColor(255, 255, 255), bg_color=NAVY_PRIMARY, align=align)

        for r_idx, item in enumerate(data):
            row_idx = r_idx + 1
            is_group_header = item[5]
            if is_group_header:
                cell_stt = table.cell(row_idx, 0)
                format_cell(cell_stt, item[0], font_size=7.5, bold=True, color=NAVY_PRIMARY, bg_color=TECH_BLUE_LIGHT, align=PP_ALIGN.CENTER)
                for c in range(1, 6):
                    cell = table.cell(row_idx, c)
                    txt = item[1] if c == 1 else ""
                    format_cell(cell, txt, font_size=7.5, bold=True, color=NAVY_PRIMARY, bg_color=TECH_BLUE_LIGHT, align=PP_ALIGN.LEFT)
            else:
                stt, name, spec, role, unit, qty, _ = item
                bg = ROW_ALT if r_idx % 2 == 1 else RGBColor(255, 255, 255)
                format_cell(table.cell(row_idx, 0), stt, font_size=7.0, bold=False, color=SLATE_MUTED, bg_color=bg, align=PP_ALIGN.CENTER)
                format_cell(table.cell(row_idx, 1), name, font_size=7.0, bold=True, color=SLATE_DARK, bg_color=bg, align=PP_ALIGN.LEFT)
                format_cell(table.cell(row_idx, 2), spec, font_size=6.8, bold=False, color=SLATE_DARK, bg_color=bg, align=PP_ALIGN.LEFT)
                format_cell(table.cell(row_idx, 3), role, font_size=6.8, bold=False, color=SLATE_MUTED, bg_color=bg, align=PP_ALIGN.LEFT)
                format_cell(table.cell(row_idx, 4), unit, font_size=6.8, bold=False, color=SLATE_DARK, bg_color=bg, align=PP_ALIGN.CENTER)
                format_cell(table.cell(row_idx, 5), qty, font_size=7.2, bold=True, color=NAVY_PRIMARY, bg_color=bg, align=PP_ALIGN.CENTER)

    render_bom_table(s2, 0.8, 2.65, 5.75, 4.30, bom_part1_data, "BẢNG BOM (PHẦN A): VI ĐIỀU KHIỂN, CẢM BIẾN, CHẤP HÀNH & NGUỒN")
    render_bom_table(s2, 6.78, 2.65, 5.75, 4.30, bom_part2_data, "BẢNG BOM (PHẦN B): ĐẤU NỐI, VỎ HỘP & CHI TIẾT ỐC VÍT CƠ KHÍ THỰC TẾ")


    # ==========================================================================
    # SLIDE 3: PART 2 - MQTT SERVICES ON SERVER & QUY CHUẨN TOPIC PHÂN CẤP
    # ==========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "PART 2: MQTT SERVICES ON SERVER — KIẾN TRÚC MESSAGE BROKER & QUY CHUẨN TOPICS",
               "Cấu Trúc Phân Cấp Topics Chuẩn Hóa, Rationale Thiết Kế & 4 Dịch Vụ Cốt Lõi (Auth, Collect, Control, Keep-Alive)")
    add_footer(s3, 3, 4)

    # NỬA TRÊN: PHÂN TÍCH MA TRẬN TOPIC VÀ RATIONALE (TẠI SAO & TÁC DỤNG GÌ)
    # Khối 1: Bảng Ma Trận Topic MQTT Chuẩn Hóa (Bên Trái)
    add_card(s3, 0.8, 1.25, 6.95, 2.45, bg_color=CARD_BG, border_color=TECH_BLUE, border_width=1.5)
    tb_top = s3.shapes.add_textbox(Inches(0.9), Inches(1.30), Inches(6.75), Inches(2.35))
    tf_top = tb_top.text_frame
    tf_top.word_wrap = True

    p_tph = tf_top.paragraphs[0]
    p_tph.text = "Quy Chuẩn Cấu Trúc Topic: smoke / {service_domain} / [{action_or_target}]"
    p_tph.font.name = FONT_HEADING
    p_tph.font.size = Pt(9.5)
    p_tph.font.bold = True
    p_tph.font.color.rgb = NAVY_PRIMARY

    topic_matrix = [
        ("smoke/auth/req & res/{id}", "Auth Svc", "QoS 1", "Handshake định danh (MAC, Passwd) ➔ Cấp Session Key HMAC-256"),
        ("smoke/telemetry", "Collect Svc", "QoS 0", "Định kỳ 2s: {id, smoke_ppm, temp, hum, key} ingest MySQL & Redis"),
        ("smoke/history/sync", "Collect Svc", "QoS 1", "Xả đệm vòng 20 bản ghi ngoại tuyến khi mạng hồi phục (Offline Replay)"),
        ("smoke/cmd/fan, buzzer, sens", "Control Svc", "QoS 1", "Downlink lệnh từ Web: {'cmd': 'SET_FAN', 'state': 'ON', 'mode': 'MANUAL'}"),
        ("smoke/status", "Control Svc", "QoS 1", "Uplink ACK xác nhận thực thi: {'ack': 'FAN_ON_SUCCESS', 'delay_ms': 115}"),
        ("smoke/keepalive", "Keep_alive", "QoS 0", "Heartbeat 30s: {status: 'ALIVE', rssi: -65, free_heap: 182400}"),
        ("smoke/lwt", "Keep_alive", "QoS 1 (Retain)", "Di chúc Broker tự phát: {status: 'OFFLINE'} khi mất kết nối quá 60s")
    ]

    for t_name, svc, qos_val, desc in topic_matrix:
        p = tf_top.add_paragraph()
        p.space_before = Pt(2)
        r1 = p.add_run()
        r1.text = "• " + t_name + " "
        r1.font.bold = True
        r1.font.size = Pt(7.8)
        r1.font.color.rgb = TECH_BLUE

        r2 = p.add_run()
        r2.text = f"[{svc} | {qos_val}]: "
        r2.font.bold = True
        r2.font.size = Pt(7.5)
        r2.font.color.rgb = NAVY_PRIMARY

        r3 = p.add_run()
        r3.text = desc
        r3.font.size = Pt(7.2)
        r3.font.color.rgb = SLATE_DARK

    # Khối 2: Rationale - Tại Sao Xây Dựng Như Thế & Tác Dụng Kỹ Thuật (Bên Phải)
    add_card(s3, 7.95, 1.25, 4.58, 2.45, bg_color=TECH_BLUE_LIGHT, border_color=TECH_BLUE_BORDER, border_width=1.5)
    tb_why = s3.shapes.add_textbox(Inches(8.05), Inches(1.30), Inches(4.38), Inches(2.35))
    tf_why = tb_why.text_frame
    tf_why.word_wrap = True

    p_wh = tf_why.paragraphs[0]
    p_wh.text = "Rationale: Tại Sao Xây Dựng Như Thế & Tác Dụng Gì?"
    p_wh.font.name = FONT_HEADING
    p_wh.font.size = Pt(9.5)
    p_wh.font.bold = True
    p_wh.font.color.rgb = NAVY_PRIMARY

    p_w1 = tf_why.add_paragraph()
    p_w1.space_before = Pt(3)
    p_w1.text = "1. TẠI SAO XÂY DỰNG THEO CẤU TRÚC PHÂN CẤP NÀY?"
    p_w1.font.bold = True
    p_w1.font.size = Pt(8.0)
    p_w1.font.color.rgb = TECH_BLUE

    reasons = [
        ("Decoupling độc lập", "4 microservices chỉ sub đúng topic phụ trách; Broker lọc gói tin ở tầng mạng, triệt tiêu tải CPU xử lý tin rác."),
        ("Tối ưu Wildcards", "Web sub `smoke/cmd/+` hoặc Server sub `nhom04/+/telemetry` scale N thiết bị không cần sửa mã nguồn."),
        ("Phân định 2 chiều rõ ràng", "Kênh Downlink (`cmd/`) tách biệt kênh Uplink (`telemetry/status`), chống loop tin nhắn.")
    ]
    for r_title, r_desc in reasons:
        p = tf_why.add_paragraph()
        p.space_before = Pt(1)
        r = p.add_run()
        r.text = "• " + r_title + ": "
        r.font.bold = True
        r.font.size = Pt(7.2)
        r.font.color.rgb = SLATE_DARK
        r_t = p.add_run()
        r_t.text = r_desc
        r_t.font.size = Pt(7.0)
        r_t.font.color.rgb = SLATE_MUTED

    p_w2 = tf_why.add_paragraph()
    p_w2.space_before = Pt(3)
    p_w2.text = "2. CẤU TRÚC NÀY ĐẠT ĐƯỢC TÁC DỤNG GÌ?"
    p_w2.font.bold = True
    p_w2.font.size = Pt(8.0)
    p_w2.font.color.rgb = SUCCESS_GREEN

    benefits = [
        ("Tối ưu RAM vi điều khiển", "ESP32 chỉ sub `smoke/cmd/+`, tiết kiệm heap RAM (~200KB), không tràn hàng đợi."),
        ("Phân bổ QoS chính xác", "Telemetry 2s dùng QoS 0 (tiết kiệm băng thông); Lệnh PCCC và ACK dùng QoS 1 bảo đảm đến đích."),
        ("Bảo mật ACL & LWT Retain", "Cấm ESP32 phát lệnh giả; Web nhận ngay trạng thái Offline từ Broker khi vừa tải trang.")
    ]
    for b_title, b_desc in benefits:
        p = tf_why.add_paragraph()
        p.space_before = Pt(1)
        r = p.add_run()
        r.text = "• " + b_title + ": "
        r.font.bold = True
        r.font.size = Pt(7.2)
        r.font.color.rgb = SLATE_DARK
        r_t = p.add_run()
        r_t.text = b_desc
        r_t.font.size = Pt(7.0)
        r_t.font.color.rgb = SLATE_MUTED

    # NỬA DƯỚI: 4 KHỐI MICROSERVICES PHỤ TRÁCH TRỰC TIẾP (TINH GỌN, SẮC NÉT)
    card_w = 2.78
    gap_s = 0.20
    y_s = 3.82
    h_s = 3.12

    # 1. Authentication Service
    add_card(s3, 0.8, y_s, card_w, h_s, bg_color=CARD_BG, border_color=TECH_BLUE, border_width=1.5)
    h1_box = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(y_s), Inches(card_w), Inches(0.42))
    h1_box.fill.solid()
    h1_box.fill.fore_color.rgb = TECH_BLUE
    h1_box.line.fill.background()
    p1 = h1_box.text_frame.paragraphs[0]
    p1.text = "1. AUTHENTICATION SERVICE\n(Topic: smoke/auth/req & res | QoS 1)"
    p1.font.size = Pt(8.0)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(255, 255, 255)
    p1.alignment = PP_ALIGN.CENTER

    tb_s1 = s3.shapes.add_textbox(Inches(0.88), Inches(y_s + 0.46), Inches(card_w - 0.16), Inches(h_s - 0.50))
    tf_s1 = tb_s1.text_frame
    tf_s1.word_wrap = True
    items_s1 = [
        ("Nhiệm Vụ Lõi", "Bảo vệ tầng truyền thông, ngăn chặn thiết bị giả mạo thâm nhập mạng."),
        ("Quy Trình Handshake", "Nhận (id, mac, passwd) từ ESP32, đối chiếu bảng MySQL device_registry."),
        ("Cấp Session Key", "Sinh mã HMAC-SHA256 (hạn 24h), publish về `smoke/auth/res/{id}`."),
        ("Bảo Mật Zero-Trust", "Thiết bị bắt buộc phải có Session Key hợp lệ mới được gửi telemetry.")
    ]
    for lbl, desc in items_s1:
        p = tf_s1.add_paragraph()
        p.space_after = Pt(2)
        r1 = p.add_run()
        r1.text = "▶ " + lbl + ": "
        r1.font.bold = True
        r1.font.size = Pt(7.5)
        r1.font.color.rgb = TECH_BLUE
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(7.2)
        r2.font.color.rgb = SLATE_DARK

    # 2. Collect Service
    x2 = 0.8 + card_w + gap_s
    add_card(s3, x2, y_s, card_w, h_s, bg_color=CARD_BG, border_color=NAVY_PRIMARY, border_width=1.5)
    h2_box = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x2), Inches(y_s), Inches(card_w), Inches(0.42))
    h2_box.fill.solid()
    h2_box.fill.fore_color.rgb = NAVY_PRIMARY
    h2_box.line.fill.background()
    p2 = h2_box.text_frame.paragraphs[0]
    p2.text = "2. COLLECT SERVICE\n(Topic: smoke/telemetry | QoS 0)"
    p2.font.size = Pt(8.0)
    p2.font.bold = True
    p2.font.color.rgb = RGBColor(255, 255, 255)
    p2.alignment = PP_ALIGN.CENTER

    tb_s2 = s3.shapes.add_textbox(Inches(x2 + 0.08), Inches(y_s + 0.46), Inches(card_w - 0.16), Inches(h_s - 0.50))
    tf_s2 = tb_s2.text_frame
    tf_s2.word_wrap = True
    items_s2 = [
        ("Nhiệm Vụ Lõi", "Tiếp nhận dữ liệu đo đạc thời gian thực từ trạm cảm biến môi trường."),
        ("Ingest Dữ Liệu", "Lắng nghe `smoke/telemetry`, ghi nhận chuỗi thời gian vào MySQL (<5ms)."),
        ("Đồng Bộ Cache", "Đẩy dữ liệu tức thời lên Redis Cache để Dashboard đọc real-time không nghẽn CSDL."),
        ("Xả Đệm Ngoại Tuyến", "Lắng nghe `smoke/history/sync` để nạp 20 bản ghi sự cố sau phục hồi mạng.")
    ]
    for lbl, desc in items_s2:
        p = tf_s2.add_paragraph()
        p.space_after = Pt(2)
        r1 = p.add_run()
        r1.text = "▶ " + lbl + ": "
        r1.font.bold = True
        r1.font.size = Pt(7.5)
        r1.font.color.rgb = NAVY_PRIMARY
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(7.2)
        r2.font.color.rgb = SLATE_DARK

    # 3. Control Service
    x3 = 0.8 + (card_w + gap_s)*2
    add_card(s3, x3, y_s, card_w, h_s, bg_color=CARD_BG, border_color=ALARM_RED, border_width=1.5)
    h3_box = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x3), Inches(y_s), Inches(card_w), Inches(0.42))
    h3_box.fill.solid()
    h3_box.fill.fore_color.rgb = ALARM_RED
    h3_box.line.fill.background()
    p3 = h3_box.text_frame.paragraphs[0]
    p3.text = "3. CONTROL SERVICE\n(Topic: smoke/cmd/* & status | QoS 1)"
    p3.font.size = Pt(8.0)
    p3.font.bold = True
    p3.font.color.rgb = RGBColor(255, 255, 255)
    p3.alignment = PP_ALIGN.CENTER

    tb_s3 = s3.shapes.add_textbox(Inches(x3 + 0.08), Inches(y_s + 0.46), Inches(card_w - 0.16), Inches(h_s - 0.50))
    tf_s3 = tb_s3.text_frame
    tf_s3.word_wrap = True
    items_s3 = [
        ("Nhiệm Vụ Lõi", "Chuyển tiếp mệnh lệnh điều khiển chấp hành từ Dashboard xuống ESP32."),
        ("Điều Khiển 2 Chiều", "Publish lệnh xuống `smoke/cmd/fan`, nhận gói ACK từ `smoke/status` (<120ms)."),
        ("Khóa Khẩn Cấp (Guard)", "Chặn lệnh tắt quạt nếu hệ thống đang có cháy thật (Trạng thái ALARM)."),
        ("Phân Quyền RBAC", "Chỉ tài khoản Admin/Operator có quyền gửi lệnh điều khiển phần cứng.")
    ]
    for lbl, desc in items_s3:
        p = tf_s3.add_paragraph()
        p.space_after = Pt(2)
        r1 = p.add_run()
        r1.text = "▶ " + lbl + ": "
        r1.font.bold = True
        r1.font.size = Pt(7.5)
        r1.font.color.rgb = ALARM_RED
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(7.2)
        r2.font.color.rgb = SLATE_DARK

    # 4. Keep_alive Service
    x4 = 0.8 + (card_w + gap_s)*3
    add_card(s3, x4, y_s, card_w, h_s, bg_color=CARD_BG, border_color=SUCCESS_GREEN, border_width=1.5)
    h4_box = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x4), Inches(y_s), Inches(card_w), Inches(0.42))
    h4_box.fill.solid()
    h4_box.fill.fore_color.rgb = SUCCESS_GREEN
    h4_box.line.fill.background()
    p4 = h4_box.text_frame.paragraphs[0]
    p4.text = "4. KEEP_ALIVE SERVICE\n(Topic: smoke/keepalive & lwt)"
    p4.font.size = Pt(8.0)
    p4.font.bold = True
    p4.font.color.rgb = RGBColor(255, 255, 255)
    p4.alignment = PP_ALIGN.CENTER

    tb_s4 = s3.shapes.add_textbox(Inches(x4 + 0.08), Inches(y_s + 0.46), Inches(card_w - 0.16), Inches(h_s - 0.50))
    tf_s4 = tb_s4.text_frame
    tf_s4.word_wrap = True
    items_s4 = [
        ("Nhiệm Vụ Lõi", "Theo dõi liên tục sức sống phần cứng và tính toàn vẹn đường truyền vô tuyến."),
        ("Chu Kỳ Heartbeat", "ESP32 gửi `smoke/keepalive` định kỳ 30s; cập nhật mốc last_seen và tính SLA Uptime."),
        ("Cơ Chế LWT (Di Chúc)", "Nếu Broker mất socket quá 60s mà không nhận Ping, tự động kích hoạt LWT."),
        ("Báo Động Ngắt Mạng", "Gửi cảnh báo tức thời lên Web Dashboard & Bot Telegram: 'DEVICE OFFLINE'.")
    ]
    for lbl, desc in items_s4:
        p = tf_s4.add_paragraph()
        p.space_after = Pt(2)
        r1 = p.add_run()
        r1.text = "▶ " + lbl + ": "
        r1.font.bold = True
        r1.font.size = Pt(7.5)
        r1.font.color.rgb = SUCCESS_GREEN
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(7.2)
        r2.font.color.rgb = SLATE_DARK


    # ==========================================================================
    # SLIDE 4: PART 3 - WEB SERVER APP (4 TRỤ CỘT CHỨC NĂNG CÔ ĐỌNG)
    # ==========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "PART 3: WEB SERVER APP — TẦNG ỨNG DỤNG, ĐIỀU KHIỂN & PHÂN TÍCH DỮ LIỆU",
               "Giao Diện Dashboard Thời Gian Thực, Quản Trị CSDL, Điều Khiển 2 Chiều & Cảnh Báo Telegram")
    add_footer(s4, 4, 4)

    col_w4 = 2.78
    gap_w4 = 0.20
    y_p4 = 1.25
    h_p4 = 5.65

    # 1. Data Representation
    x_c1 = 0.8
    add_card(s4, x_c1, y_p4, col_w4, h_p4, bg_color=CARD_BG, border_color=TECH_BLUE, border_width=1.5)
    t1_box = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x_c1), Inches(y_p4), Inches(col_w4), Inches(0.48))
    t1_box.fill.solid()
    t1_box.fill.fore_color.rgb = TECH_BLUE
    t1_box.line.fill.background()
    pt1 = t1_box.text_frame.paragraphs[0]
    pt1.text = "1. DATA REPRESENTATION\n(Trực Quan Hóa Dữ Liệu)"
    pt1.font.size = Pt(8.5)
    pt1.font.bold = True
    pt1.font.color.rgb = RGBColor(255, 255, 255)
    pt1.alignment = PP_ALIGN.CENTER

    tb_p1 = s4.shapes.add_textbox(Inches(x_c1 + 0.08), Inches(y_p4 + 0.52), Inches(col_w4 - 0.16), Inches(h_p4 - 0.58))
    tf_p1 = tb_p1.text_frame
    tf_p1.word_wrap = True
    items_p1 = [
        ("Mục Tiêu", "Trực quan hóa tức thời qua WebSockets & MQTT-over-WS với độ trễ <1s."),
        ("Radial Gauge", "Hiển thị nồng độ khói MQ-2 (0-1000 ppm) với 3 dải màu: An toàn / Cảnh giác / Báo cháy."),
        ("Chart.js Real-Time", "Vẽ đồ thị tương quan nhiệt độ (°C) và độ ẩm (%RH) liên tục theo thời gian thực."),
        ("Live Status Badges", "Cập nhật nhịp tim thiết bị (Online/Offline), trạng thái quạt hút (ON/OFF), trạng thái FSM."),
        ("UX Responsive", "Phong cách Glassmorphism công nghệ cao, hiển thị hoàn hảo trên máy tính & điện thoại.")
    ]
    for lbl, desc in items_p1:
        p = tf_p1.add_paragraph()
        p.space_after = Pt(6)
        r1 = p.add_run()
        r1.text = "▶ " + lbl + ": "
        r1.font.bold = True
        r1.font.size = Pt(8.2)
        r1.font.color.rgb = TECH_BLUE
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(8.0)
        r2.font.color.rgb = SLATE_DARK

    # 2. Data Management
    x_c2 = 0.8 + col_w4 + gap_w4
    add_card(s4, x_c2, y_p4, col_w4, h_p4, bg_color=CARD_BG, border_color=NAVY_PRIMARY, border_width=1.5)
    t2_box = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x_c2), Inches(y_p4), Inches(col_w4), Inches(0.48))
    t2_box.fill.solid()
    t2_box.fill.fore_color.rgb = NAVY_PRIMARY
    t2_box.line.fill.background()
    pt2 = t2_box.text_frame.paragraphs[0]
    pt2.text = "2. DATA MANAGEMENT\n(Quản Trị & Truy Vấn CSDL)"
    pt2.font.size = Pt(8.5)
    pt2.font.bold = True
    pt2.font.color.rgb = RGBColor(255, 255, 255)
    pt2.alignment = PP_ALIGN.CENTER

    tb_p2 = s4.shapes.add_textbox(Inches(x_c2 + 0.08), Inches(y_p4 + 0.52), Inches(col_w4 - 0.16), Inches(h_p4 - 0.58))
    tf_p2 = tb_p2.text_frame
    tf_p2.word_wrap = True
    items_p2 = [
        ("Mục Tiêu", "Lưu trữ, tra cứu và kiểm toán lịch sử vận hành hệ thống một cách toàn vẹn."),
        ("RESTful API", "Truy vấn MySQL tối ưu bằng chỉ mục INDEX(timestamp, device_id) phản hồi <10ms."),
        ("Bộ Lọc Đa Mốc", "Tra cứu linh hoạt theo mốc thời gian (1h, 24h, 7 ngày) hoặc lọc theo cấp độ rủi ro."),
        ("Xuất Báo Cáo", "Kết xuất toàn bộ nhật ký sự kiện ra CSV, Excel (.xlsx) và PDF phục vụ nghiệm thu PCCC."),
        ("Data Retention", "Tự động phân vùng và tổng hợp dữ liệu cũ, chống phình to dung lượng ổ cứng máy chủ.")
    ]
    for lbl, desc in items_p2:
        p = tf_p2.add_paragraph()
        p.space_after = Pt(6)
        r1 = p.add_run()
        r1.text = "▶ " + lbl + ": "
        r1.font.bold = True
        r1.font.size = Pt(8.2)
        r1.font.color.rgb = NAVY_PRIMARY
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(8.0)
        r2.font.color.rgb = SLATE_DARK

    # 3. Control GUI
    x_c3 = 0.8 + (col_w4 + gap_w4)*2
    add_card(s4, x_c3, y_p4, col_w4, h_p4, bg_color=CARD_BG, border_color=ALARM_RED, border_width=1.5)
    t3_box = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x_c3), Inches(y_p4), Inches(col_w4), Inches(0.48))
    t3_box.fill.solid()
    t3_box.fill.fore_color.rgb = ALARM_RED
    t3_box.line.fill.background()
    pt3 = t3_box.text_frame.paragraphs[0]
    pt3.text = "3. CONTROL GUI\n(Giao Diện Điều Khiển Từ Xa)"
    pt3.font.size = Pt(8.5)
    pt3.font.bold = True
    pt3.font.color.rgb = RGBColor(255, 255, 255)
    pt3.alignment = PP_ALIGN.CENTER

    tb_p3 = s4.shapes.add_textbox(Inches(x_c3 + 0.08), Inches(y_p4 + 0.52), Inches(col_w4 - 0.16), Inches(h_p4 - 0.58))
    tf_p3 = tb_p3.text_frame
    tf_p3.word_wrap = True
    items_p3 = [
        ("Mục Tiêu", "Cho phép người quản trị can thiệp và điều phối phần cứng ngoại vi an toàn tuyệt đối."),
        ("Toggle Auto/Manual", "Chuyển đổi linh hoạt giữa chế độ tự động theo FSM và can thiệp thủ công."),
        ("Kích Hoạt Chấp Hành", "Nút bấm bật/tắt cưỡng bức quạt hút khói 12V và chuông còi báo động kèm phản hồi ACK."),
        ("Cấu Hình Ngưỡng", "Thiết lập ngưỡng cảnh báo khói ngày/đêm trực tiếp trên Web không cần nạp lại code."),
        ("Emergency Kill-Switch", "Nút dừng khẩn cấp toàn hệ thống để cô lập rủi ro khi có sự cố kỹ thuật bảo trì.")
    ]
    for lbl, desc in items_p3:
        p = tf_p3.add_paragraph()
        p.space_after = Pt(6)
        r1 = p.add_run()
        r1.text = "▶ " + lbl + ": "
        r1.font.bold = True
        r1.font.size = Pt(8.2)
        r1.font.color.rgb = ALARM_RED
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(8.0)
        r2.font.color.rgb = SLATE_DARK

    # 4. Data Analysis
    x_c4 = 0.8 + (col_w4 + gap_w4)*3
    add_card(s4, x_c4, y_p4, col_w4, h_p4, bg_color=CARD_BG, border_color=AMBER_GOLD, border_width=1.5)
    t4_box = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x_c4), Inches(y_p4), Inches(col_w4), Inches(0.48))
    t4_box.fill.solid()
    t4_box.fill.fore_color.rgb = AMBER_GOLD
    t4_box.line.fill.background()
    pt4 = t4_box.text_frame.paragraphs[0]
    pt4.text = "4. DATA ANALYSIS\n(Phân Tích & Cảnh Báo Telegram)"
    pt4.font.size = Pt(8.5)
    pt4.font.bold = True
    pt4.font.color.rgb = RGBColor(255, 255, 255)
    pt4.alignment = PP_ALIGN.CENTER

    tb_p4 = s4.shapes.add_textbox(Inches(x_c4 + 0.08), Inches(y_p4 + 0.52), Inches(col_w4 - 0.16), Inches(h_p4 - 0.58))
    tf_p4 = tb_p4.text_frame
    tf_p4.word_wrap = True
    items_p4 = [
        ("Mục Tiêu", "Ứng dụng thuật toán phân tích thông minh nhận diện nguy cơ cháy sớm và phát tín hiệu đa kênh."),
        ("Nhận Diện Cháy Sớm", "Kết hợp đạo hàm tốc độ tăng khói (ΔPPM/Δt >15%) và nhiệt độ môi trường (>50°C)."),
        ("Triệt Tiêu Báo Ảo", "Bộ lọc EMA và ma trận tương quan loại trừ hoàn toàn khói thuốc lá thoáng qua hoặc xịt cồn."),
        ("Telegram Bot API", "Tự động gửi tin nhắn báo động khẩn kèm đồ thị thông số và vị trí trạm về đội PCCC (<1s)."),
        ("Báo Động Đa Tầng", "Đồng bộ âm thanh còi hú Web Audio API, pop-up cảnh báo màn hình và kích hoạt loa đèn.")
    ]
    for lbl, desc in items_p4:
        p = tf_p4.add_paragraph()
        p.space_after = Pt(6)
        r1 = p.add_run()
        r1.text = "▶ " + lbl + ": "
        r1.font.bold = True
        r1.font.size = Pt(8.2)
        r1.font.color.rgb = AMBER_GOLD
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(8.0)
        r2.font.color.rgb = SLATE_DARK

    # LƯU FILE PRESENTATION
    output_path = r"e:\IoT\DoAn\docs\pptx\Bao_Cao_He_Thong_IoT_4_Slides_Nhom04.pptx"
    prs.save(output_path)
    print(f"[THÀNH CÔNG] Đã tạo file presentation chuẩn 4 slide tối ưu 3 phút tại: {output_path}")

if __name__ == "__main__":
    build_report_presentation()
