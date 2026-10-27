# -*- coding: utf-8 -*-
"""
Script tạo Slide PowerPoint Báo Cáo Tiến Độ Tuần 5:
"Hệ Thống Báo Khói Cảnh Báo Sớm" - Tầng 3 Middleware / Automation Engine (Node-RED) - Nhóm 04
Milestone: Middleware & Automation Engine (10% tổng điểm)
Yêu cầu bắt buộc: KHÔNG ĐƯA CODE VÀO. Tập trung vào luồng chức năng, FSM, 5 rules, kiến trúc, kiểm thử.
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
# HỆ THỐNG MÀU SẮC CHUẨN DOANH NGHIỆP & CÔNG NGHỆ (NAVY & TECH THEME)
# ==============================================================================
NAVY_PRIMARY    = RGBColor(31, 78, 120)    # #1F4E78 - Xanh Navy chủ đạo
NAVY_DARK       = RGBColor(15, 43, 70)     # #0F2B46 - Xanh Navy đậm nền bìa
TECH_BLUE       = RGBColor(46, 117, 182)   # #2E75B6 - Xanh dương công nghệ
TECH_BLUE_LIGHT = RGBColor(222, 235, 247)  # #DEEBF7 - Nền xanh nhạt
TECH_BLUE_ACCENT= RGBColor(0, 164, 239)    # #00A4EF - Xanh dương điểm nhấn
SLATE_DARK      = RGBColor(30, 41, 59)     # #1E293B - Chữ chính đậm
SLATE_MUTED     = RGBColor(100, 116, 139)  # #64748B - Chữ phụ mờ
BG_LIGHT        = RGBColor(248, 250, 252)  # #F8FAFC - Nền slide
CARD_BG         = RGBColor(255, 255, 255)  # Trắng
CARD_BORDER     = RGBColor(205, 220, 235)  # Viền card mềm
ALARM_RED       = RGBColor(192, 0, 0)      # Đỏ báo động
ALARM_BG        = RGBColor(254, 242, 242)  # Nền đỏ nhạt
SUCCESS_GREEN   = RGBColor(40, 167, 69)    # Xanh lá an toàn/pass
SUCCESS_BG      = RGBColor(240, 253, 244)  # Nền xanh lá nhạt
WARN_ORANGE     = RGBColor(237, 125, 49)   # Cam cảnh báo
WARN_BG         = RGBColor(255, 247, 237)  # Nền cam nhạt
PURPLE_ACCENT   = RGBColor(112, 48, 160)   # Tím chức năng

FONT_HEADING = "Arial"
FONT_BODY = "Arial"

def create_base_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs

def add_header(slide, category_text, title_text):
    """Tạo Header chuẩn hóa gồm dải màu trên, badge danh mục và tiêu đề slide"""
    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.08))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = TECH_BLUE
    top_bar.line.fill.background()

    cat_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.26), Inches(4.8), Inches(0.32))
    cat_box.fill.solid()
    cat_box.fill.fore_color.rgb = TECH_BLUE_LIGHT
    cat_box.line.color.rgb = TECH_BLUE
    cat_box.line.width = Pt(1)
    tf_c = cat_box.text_frame
    p_c = tf_c.paragraphs[0]
    p_c.text = category_text.upper()
    p_c.font.name = FONT_HEADING
    p_c.font.size = Pt(9.5)
    p_c.font.bold = True
    p_c.font.color.rgb = NAVY_PRIMARY

    title_box = slide.shapes.add_textbox(Inches(0.75), Inches(0.62), Inches(11.8), Inches(0.65))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(21)
    p_t.font.bold = True
    p_t.font.color.rgb = NAVY_PRIMARY

def add_footer(slide, current_idx, total_slides=11):
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(7.05), Inches(11.733), Inches(0.02))
    line.fill.solid()
    line.fill.fore_color.rgb = RGBColor(220, 226, 235)
    line.line.fill.background()

    tb_left = slide.shapes.add_textbox(Inches(0.8), Inches(7.08), Inches(8.5), Inches(0.35))
    tf_l = tb_left.text_frame
    p_l = tf_l.paragraphs[0]
    p_l.text = "Đề tài 04: Hệ thống Báo khói Cảnh báo sớm • Báo cáo Tiến độ Tuần 5 (Tầng 3 Middleware) • Nhóm 04"
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

def add_bullet(tf, bold_label, text_content, font_size=10.5, bold_color=NAVY_PRIMARY, text_color=SLATE_DARK, space_after=5):
    p = tf.add_paragraph()
    p.space_after = Pt(space_after)
    p.line_spacing = 1.15
    if bold_label:
        r1 = p.add_run()
        r1.text = bold_label + ": " if not bold_label.endswith(":") else bold_label + " "
        r1.font.name = FONT_BODY
        r1.font.size = Pt(font_size)
        r1.font.bold = True
        r1.font.color.rgb = bold_color
    r2 = p.add_run()
    r2.text = text_content
    r2.font.name = FONT_BODY
    r2.font.size = Pt(font_size)
    r2.font.color.rgb = text_color
    return p

def set_speaker_notes(slide, speaker_name, role_title, notes_text):
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = f"【NGƯỜI THUYẾT TRÌNH: {speaker_name.upper()} - {role_title}】\n\n"
    tf.text += f"KỊCH BẢN THUYẾT TRÌNH TRƯỚC GIẢNG VIÊN HƯỚNG DẪN:\n"
    tf.text += notes_text

def build_all_slides():
    prs = create_base_presentation()
    blank_layout = prs.slide_layouts[6]

    # ==============================================================================
    # SLIDE 1: BÌA ĐỀ TÀI & BÁO CÁO TIẾN ĐỘ TUẦN 5
    # ==============================================================================
    s1 = prs.slides.add_slide(blank_layout)
    add_card(s1, 0, 0, 13.333, 7.5, bg_color=NAVY_DARK, border_color=None)
    add_card(s1, 0, 0, 0.35, 7.5, bg_color=TECH_BLUE_ACCENT, border_color=None)

    tb_u = s1.shapes.add_textbox(Inches(1.0), Inches(0.6), Inches(11.3), Inches(0.8))
    tf_u = tb_u.text_frame
    p_u1 = tf_u.paragraphs[0]
    p_u1.text = "BỘ CÔNG THƯƠNG  •  TRƯỜNG ĐẠI HỌC CÔNG THƯƠNG TP. HỒ CHÍ MINH (HUIT)"
    p_u1.font.size = Pt(11)
    p_u1.font.bold = True
    p_u1.font.color.rgb = TECH_BLUE_ACCENT

    p_u2 = tf_u.add_paragraph()
    p_u2.text = "KHOA CÔNG NGHỆ THÔNG TIN  •  BỘ MÔN MẠNG & AN TOÀN THÔNG TIN"
    p_u2.font.size = Pt(9.5)
    p_u2.font.color.rgb = RGBColor(180, 205, 230)

    # Title Box
    tb_t = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(2.2))
    tf_t = tb_t.text_frame
    p_t1 = tf_t.paragraphs[0]
    p_t1.text = "BÁO CÁO TIẾN ĐỘ ĐỒ ÁN MÔN HỌC (IoT) — TUẦN 5"
    p_t1.font.size = Pt(16)
    p_t1.font.bold = True
    p_t1.font.color.rgb = RGBColor(255, 192, 0)

    p_t2 = tf_t.add_paragraph()
    p_t2.text = "HỆ THỐNG BÁO KHÓI CẢNH BÁO SỚM"
    p_t2.font.size = Pt(30)
    p_t2.font.bold = True
    p_t2.font.color.rgb = RGBColor(255, 255, 255)

    p_t3 = tf_t.add_paragraph()
    p_t3.text = "Phần 5: Thiết Kế & Triển Khai Tầng 3 – Middleware / Automation Engine (Node-RED)"
    p_t3.font.size = Pt(15)
    p_t3.font.color.rgb = TECH_BLUE_LIGHT

    # Milestone Badge
    badge = add_card(s1, 1.0, 4.2, 5.2, 0.45, bg_color=RGBColor(24, 76, 120), border_color=TECH_BLUE_ACCENT)
    tf_b = badge.text_frame
    p_b = tf_b.paragraphs[0]
    p_b.text = "★ MILESTONE: MIDDLEWARE & AUTOMATION (10% ĐIỂM)"
    p_b.font.size = Pt(11)
    p_b.font.bold = True
    p_b.font.color.rgb = RGBColor(255, 255, 255)

    # Team Info Card
    card_team = add_card(s1, 1.0, 4.9, 11.3, 1.9, bg_color=RGBColor(20, 35, 55), border_color=RGBColor(40, 70, 100))
    tb_m = s1.shapes.add_textbox(Inches(1.2), Inches(5.0), Inches(10.9), Inches(1.7))
    tf_m = tb_m.text_frame
    p_m1 = tf_m.paragraphs[0]
    p_m1.text = "THÔNG TIN HỘI ĐỒNG & NHÓM BÁO CÁO:"
    p_m1.font.size = Pt(11)
    p_m1.font.bold = True
    p_m1.font.color.rgb = TECH_BLUE_ACCENT

    p_m2 = tf_m.add_paragraph()
    p_m2.text = "• Giảng viên hướng dẫn: ThS. Võ Hoàng Hải  |  Lớp: 14DHTH09  |  Nhóm thực hiện: Nhóm 04 (N09)"
    p_m2.font.size = Pt(10)
    p_m2.font.color.rgb = RGBColor(230, 240, 250)

    p_m3 = tf_m.add_paragraph()
    p_m3.text = "• Thành viên: Nguyễn Vĩnh Khang (2001230381 - Nhóm trưởng)  |  Nguyễn Văn Đức (2001230186)  |  Nguyễn Văn Mãnh (2001230503)"
    p_m3.font.size = Pt(10)
    p_m3.font.color.rgb = RGBColor(230, 240, 250)

    p_m4 = tf_m.add_paragraph()
    p_m4.text = "• Thời gian nghiệm thu: Tuần 5  |  Thời lượng tích lũy: 18.0 giờ nhóm (6.0h / thành viên)"
    p_m4.font.size = Pt(10)
    p_m4.font.color.rgb = RGBColor(160, 190, 220)

    set_speaker_notes(s1, "Nguyễn Vĩnh Khang", "Nhóm trưởng",
        "Kính thưa Thầy Võ Hoàng Hải, hôm nay Nhóm 04 xin đại diện báo cáo tiến độ Đồ án môn học Lập trình nhúng IoT ở mốc Tuần 5. "
        "Sau khi hoàn thành Milestone M2 ở Tuần 4 với thiết bị cảm biến kết nối mạng MQTT 2 chiều ổn định, trọng tâm Tuần 5 của nhóm là hiện thực hóa "
        "Tầng 3 - Middleware / Automation Engine dựa trên Node-RED. Nhóm cam kết tuân thủ đúng định hướng của Thầy: Middleware phải đóng vai trò là "
        "bộ não xử lý thông minh, điều phối tự động và kiểm soát trạng thái, chứ không chỉ đơn thuần là chuyển tiếp dữ liệu.")

    # ==============================================================================
    # SLIDE 2: MỤC TIÊU & TIÊU CHÍ NGHIỆM THU TUẦN 5
    # ==============================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Kế Hoạch & Tiêu Chuẩn Bộ Môn", "Mục Tiêu Kỹ Thuật & Tiêu Chí Nghiệm Thu Tuần 5")
    add_footer(s2, 2)

    # Core Rule Callout Banner
    callout = add_card(s2, 0.8, 1.4, 11.733, 0.95, bg_color=TECH_BLUE_LIGHT, border_color=TECH_BLUE)
    tb_c = s2.shapes.add_textbox(Inches(0.95), Inches(1.45), Inches(11.4), Inches(0.85))
    tf_co = tb_c.text_frame
    p_co1 = tf_co.paragraphs[0]
    p_co1.text = "NGUYÊN TẮC NGHIỆM THU CỐT LÕI CỦA BỘ MÔN (TUẦN 5 — TẦNG 3 MIDDLEWARE):"
    p_co1.font.size = Pt(10.5)
    p_co1.font.bold = True
    p_co1.font.color.rgb = NAVY_PRIMARY
    p_co2 = tf_co.add_paragraph()
    p_co2.text = "\"Middleware phải thực hiện xử lý nghiệp vụ thông minh, không chỉ forward dữ liệu.\" Đạt đầy đủ: Xử lý sự kiện (Event-driven) + Máy trạng thái hữu hạn (FSM) + Quy tắc tự động hóa cốt lõi + Giám sát ngoại lệ + Điều phối lệnh chấp hành."
    p_co2.font.size = Pt(10)
    p_co2.font.color.rgb = SLATE_DARK

    # 3 Member Task Breakdown Cards
    card_w = 3.75
    gap = 0.24
    left_start = 0.8

    # Card 1: Khang
    c1 = add_card(s2, left_start, 2.55, card_w, 4.25, bg_color=CARD_BG, border_color=CARD_BORDER)
    tb_1 = s2.shapes.add_textbox(Inches(left_start + 0.15), Inches(2.65), Inches(card_w - 0.3), Inches(4.0))
    tf_1 = tb_1.text_frame
    p1 = tf_1.paragraphs[0]
    p1.text = "NGUYỄN VĨNH KHANG (SV3)"
    p1.font.bold = True
    p1.font.size = Pt(12)
    p1.font.color.rgb = NAVY_PRIMARY
    add_bullet(tf_1, "Vai trò", "Trưởng nhóm phụ trách Kiến trúc & FSM")
    add_bullet(tf_1, "Nhiệm vụ chính", "Xây dựng mô hình Máy trạng thái hữu hạn (FSM 5 States) điều phối toàn hệ thống")
    add_bullet(tf_1, "Cơ chế an toàn", "Thiết lập Watchdog Heartbeat 10s & Bắt sự kiện LWT đứt mạng từ Broker")
    add_bullet(tf_1, "Lịch trình", "Lập trình Rule 4 Night Scheduler (Tự đổi ngưỡng nhạy ban đêm 22h-06h)")
    add_bullet(tf_1, "Thời lượng", "6.0 giờ tích lũy (Hoàn thành 100%)", bold_color=SUCCESS_GREEN)

    # Card 2: Đức
    c2 = add_card(s2, left_start + card_w + gap, 2.55, card_w, 4.25, bg_color=CARD_BG, border_color=CARD_BORDER)
    tb_2 = s2.shapes.add_textbox(Inches(left_start + card_w + gap + 0.15), Inches(2.65), Inches(card_w - 0.3), Inches(4.0))
    tf_2 = tb_2.text_frame
    p2 = tf_2.paragraphs[0]
    p2.text = "NGUYỄN VĂN ĐỨC (SV1)"
    p2.font.bold = True
    p2.font.size = Pt(12)
    p2.font.color.rgb = NAVY_PRIMARY
    add_bullet(tf_2, "Vai trò", "Thành viên phụ trách Node-RED Flow & Rules")
    add_bullet(tf_2, "Nhiệm vụ chính", "Thiết lập Node-RED Flow 29 nodes kết nối EMQX Cloud Broker")
    add_bullet(tf_2, "Logic PCCC", "Hiện thực Rule 1 (Ngưỡng khói PPM) và Rule 2 (Ngưỡng nhiệt độ DHT22)")
    add_bullet(tf_2, "Thuật toán", "Xây dựng bộ đệm Hysteresis Cooldown trễ 20s bảo vệ tiếp điểm Relay quạt")
    add_bullet(tf_2, "Thời lượng", "6.0 giờ tích lũy (Hoàn thành 100%)", bold_color=SUCCESS_GREEN)

    # Card 3: Mãnh
    c3 = add_card(s2, left_start + (card_w + gap) * 2, 2.55, card_w, 4.25, bg_color=CARD_BG, border_color=CARD_BORDER)
    tb_3 = s2.shapes.add_textbox(Inches(left_start + (card_w + gap) * 2 + 0.15), Inches(2.65), Inches(card_w - 0.3), Inches(4.0))
    tf_3 = tb_3.text_frame
    p3 = tf_3.paragraphs[0]
    p3.text = "NGUYỄN VĂN MÃNH (SV2)"
    p3.font.bold = True
    p3.font.size = Pt(12)
    p3.font.color.rgb = NAVY_PRIMARY
    add_bullet(tf_3, "Vai trò", "Thành viên phụ trách Logging & Downlink")
    add_bullet(tf_3, "Nhật ký", "Xây dựng Event History Logger: Bộ đệm 50 sự kiện & ghi file bền vững")
    add_bullet(tf_3, "Điều phối", "Chuẩn hóa Downlink Dispatcher phát lệnh Quạt/Còi xuống ESP32")
    add_bullet(tf_3, "Kiểm thử", "Soạn thảo kịch bản kiểm thử 15 Test Cases & Chạy thử tự động 100% Pass")
    add_bullet(tf_3, "Thời lượng", "6.0 giờ tích lũy (Hoàn thành 100%)", bold_color=SUCCESS_GREEN)

    set_speaker_notes(s2, "Nguyễn Văn Đức", "Thành viên",
        "Kính thưa Thầy, để đạt được yêu cầu của đề cương môn học, nhóm em đã phân bổ tối thiểu 6 giờ lao động nghiêm túc cho mỗi thành viên, tổng cộng 18 giờ. "
        "Chúng em bám sát nguyên tắc cốt lõi: Middleware Node-RED phải tự phân tích dữ liệu cảm biến, duy trì máy trạng thái FSM và ra quyết định độc lập. "
        "Bạn Khang phụ trách thiết kế khung FSM và Watchdog; em Đức phụ trách lập trình các quy tắc cảnh báo và thuật toán chống dội Hysteresis; "
        "bạn Mãnh phụ trách ghi nhật ký kiểm toán và bộ điều phối lệnh Downlink.")

    # ==============================================================================
    # SLIDE 3: KIẾN TRÚC 4 TẦNG & VỊ TRÍ TẦNG 3 MIDDLEWARE
    # ==============================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Kiến Trúc Tổng Thể Hệ Thống", "Vị Trí Tầng 3 (Middleware) Trong Kiến Trúc 4 Tầng IoT")
    add_footer(s3, 3)

    # 4 Layers Horizontal / Vertical Stack
    col_w = 2.75
    col_gap = 0.24
    l_base = 0.8

    # Layer 1
    add_card(s3, l_base, 1.5, col_w, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
    badge1 = add_card(s3, l_base + 0.15, 1.65, col_w - 0.3, 0.45, bg_color=TECH_BLUE_LIGHT, border_color=TECH_BLUE)
    badge1.text_frame.paragraphs[0].text = "TẦNG 1: SENSING & ACT"
    badge1.text_frame.paragraphs[0].font.bold = True
    badge1.text_frame.paragraphs[0].font.size = Pt(9.5)
    badge1.text_frame.paragraphs[0].font.color.rgb = NAVY_PRIMARY
    tb_l1 = s3.shapes.add_textbox(Inches(l_base + 0.15), Inches(2.2), Inches(col_w - 0.3), Inches(4.5))
    tf_l1 = tb_l1.text_frame
    add_bullet(tf_l1, "Phần cứng", "ESP32 Wokwi Node")
    add_bullet(tf_l1, "Cảm biến", "MQ-2 (Khói), DHT22 (Nhiệt/Ẩm)")
    add_bullet(tf_l1, "Chấp hành", "Relay Quạt hút, Còi Piezo")
    add_bullet(tf_l1, "Cục bộ", "Nút nhấn Test, FSM khẩn cấp cục bộ")
    add_bullet(tf_l1, "Uplink", "Bắn dữ liệu chu kỳ 2s hoặc tức thời khi khói tăng")

    # Layer 2
    add_card(s3, l_base + col_w + col_gap, 1.5, col_w, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
    badge2 = add_card(s3, l_base + col_w + col_gap + 0.15, 1.65, col_w - 0.3, 0.45, bg_color=TECH_BLUE_LIGHT, border_color=TECH_BLUE)
    badge2.text_frame.paragraphs[0].text = "TẦNG 2: NETWORK (MQTT)"
    badge2.text_frame.paragraphs[0].font.bold = True
    badge2.text_frame.paragraphs[0].font.size = Pt(9.5)
    badge2.text_frame.paragraphs[0].font.color.rgb = NAVY_PRIMARY
    tb_l2 = s3.shapes.add_textbox(Inches(l_base + col_w + col_gap + 0.15), Inches(2.2), Inches(col_w - 0.3), Inches(4.5))
    tf_l2 = tb_l2.text_frame
    add_bullet(tf_l2, "Giao thức", "MQTT v3.1.1 & WSS")
    add_bullet(tf_l2, "Broker", "EMQX Public Cloud (1883)")
    add_bullet(tf_l2, "Topics Nhận", "smoke/telemetry, smoke/event/alarm")
    add_bullet(tf_l2, "Topics Gửi", "smoke/cmd/fan, smoke/cmd/buzzer")
    add_bullet(tf_l2, "Cơ chế lỗi", "LWT: smoke/lwt bắt ngắt mạng lập tức")

    # Layer 3 (HIGHLIGHTED)
    add_card(s3, l_base + (col_w + col_gap) * 2, 1.4, col_w + 0.15, 5.5, bg_color=RGBColor(245, 250, 255), border_color=TECH_BLUE_ACCENT, border_width=2)
    badge3 = add_card(s3, l_base + (col_w + col_gap) * 2 + 0.15, 1.55, col_w - 0.15, 0.55, bg_color=NAVY_PRIMARY, border_color=None)
    badge3.text_frame.paragraphs[0].text = "TẦNG 3: MIDDLEWARE (TUẦN 5)"
    badge3.text_frame.paragraphs[0].font.bold = True
    badge3.text_frame.paragraphs[0].font.size = Pt(9.5)
    badge3.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
    tb_l3 = s3.shapes.add_textbox(Inches(l_base + (col_w + col_gap) * 2 + 0.15), Inches(2.2), Inches(col_w - 0.15), Inches(4.6))
    tf_l3 = tb_l3.text_frame
    add_bullet(tf_l3, "Nền tảng", "Node-RED Automation Flow", bold_color=TECH_BLUE)
    add_bullet(tf_l3, "Bộ não FSM", "5 Trạng thái vận hành tập trung", bold_color=TECH_BLUE)
    add_bullet(tf_l3, "5 Quy tắc", "Rule Khói, Nhiệt, Hysteresis, Lịch trình Đêm, Watchdog", bold_color=TECH_BLUE)
    add_bullet(tf_l3, "Xác thực", "Fleet Registry MAC/Token (Slide 65)", bold_color=TECH_BLUE)
    add_bullet(tf_l3, "Kiểm toán", "Ghi file logs/event_history.log", bold_color=TECH_BLUE)

    # Layer 4
    add_card(s3, l_base + (col_w + col_gap) * 3 + 0.15, 1.5, col_w - 0.15, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
    badge4 = add_card(s3, l_base + (col_w + col_gap) * 3 + 0.3, 1.65, col_w - 0.45, 0.45, bg_color=TECH_BLUE_LIGHT, border_color=TECH_BLUE)
    badge4.text_frame.paragraphs[0].text = "TẦNG 4: APPLICATION"
    badge4.text_frame.paragraphs[0].font.bold = True
    badge4.text_frame.paragraphs[0].font.size = Pt(9.5)
    badge4.text_frame.paragraphs[0].font.color.rgb = NAVY_PRIMARY
    tb_l4 = s3.shapes.add_textbox(Inches(l_base + (col_w + col_gap) * 3 + 0.3), Inches(2.2), Inches(col_w - 0.45), Inches(4.5))
    tf_l4 = tb_l4.text_frame
    add_bullet(tf_l4, "Giao diện", "Web Platform Cyber-Safety")
    add_bullet(tf_l4, "Giám sát", "Gauges, Chart.js, Sơ đồ mặt bằng")
    add_bullet(tf_l4, "Cảnh báo tức thì", "Telegram Bot Webhook")
    add_bullet(tf_l4, "Điều khiển", "Nút bấm Bật/Tắt quạt, Mute còi")
    add_bullet(tf_l4, "Vai trò", "Tiếp nhận dữ liệu sau xử lý từ Tầng 3")

    set_speaker_notes(s3, "Nguyễn Vĩnh Khang", "Nhóm trưởng",
        "Thưa Thầy, Slide này minh họa rõ nét vị trí chiến lược của Tầng 3 trong kiến trúc 4 tầng IoT của nhóm. "
        "Nếu Tầng 1 là cơ bắp và giác quan (ESP32 cảm biến & chấp hành), Tầng 2 là mạch máu truyền dẫn (MQTT Broker), "
        "và Tầng 4 là bộ mặt giao tiếp người dùng (Dashboard), thì Tầng 3 chính là bộ não điều phối trung ương. "
        "Toàn bộ dữ liệu khói và nhiệt độ không đi thẳng lên màn hình mà phải đi qua Tầng 3 để kiểm định tính toàn vẹn, "
        "so khớp với ma trận quy tắc an toàn PCCC, chuyển đổi trạng thái FSM và ra quyết định đóng ngắt thiết bị.")

    # ==============================================================================
    # SLIDE 4: KIẾN TRÚC LUỒNG XỬ LÝ SỰ KIỆN (EVENT-DRIVEN FLOW ENGINE)
    # ==============================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Cơ Chế Xử Lý Trung Tâm", "Kiến Trúc Luồng Sự Kiện (Event-Driven Flow Engine)")
    add_footer(s4, 4)

    # 4 Pipeline Stage Cards
    stages = [
        ("GIAI ĐOẠN 1: TIẾP NHẬN & GIẢI MÃ", [
            ("Lắng nghe đa Topic", "Đăng ký đồng thời 4 Topic MQTT: telemetry, event/alarm, status, lwt"),
            ("JSON Parser & Validator", "Giải mã gói tin, kiểm tra cấu trúc schema bắt buộc, loại bỏ nhiễu"),
            ("Device Authenticator", "Xác thực danh tính thiết bị qua Client ID và Token theo chuẩn Slide 65")
        ], TECH_BLUE_LIGHT),
        ("GIAI ĐOẠN 2: BỘ NÃO FSM & 5 RULES", [
            ("State Evaluator", "Đối chiếu thông số khói và nhiệt độ với trạng thái FSM hiện tại"),
            ("Core Automation Rules", "Thực thi song song 5 quy tắc nghiệp vụ PCCC độc lập"),
            ("Cơ chế chống rung chập", "Kích hoạt vùng đệm Hysteresis để giữ trạng thái an toàn")
        ], RGBColor(254, 243, 199)),
        ("GIAI ĐOẠN 3: ĐIỀU PHỐI DOWNLINK", [
            ("Command Dispatcher", "Tạo lệnh điều khiển chuẩn hóa: Fan ON/OFF, Buzzer ON/OFF"),
            ("Safety Interlock", "Khóa an toàn cấm tắt quạt nếu nồng độ khói vẫn ở mức nguy hiểm"),
            ("Publish QoS 1", "Phát lệnh xuống MQTT Broker với cờ xác nhận giao nhận tin cậy")
        ], RGBColor(254, 226, 226)),
        ("GIAI ĐOẠN 4: GHI NHẬT KÝ & AUDIT", [
            ("Ring Buffer Memory", "Lưu 50 sự kiện gần nhất trên bộ nhớ đệm phục vụ hiển thị Dashboard"),
            ("Persistent File Log", "Ghi nối tiếp vào file event_history.log kèm dấu thời gian ISO 8601"),
            ("Rate Limiter 30s", "Chặn bão cảnh báo (Alarm Storm) tránh làm quá tải hệ thống")
        ], SUCCESS_BG)
    ]

    st_w = 5.7
    st_h = 2.45
    st_positions = [
        (0.8, 1.45), (6.8, 1.45),
        (0.8, 4.2), (6.8, 4.2)
    ]

    for idx, (title, items, bg_c) in enumerate(stages):
        pos_x, pos_y = st_positions[idx]
        card = add_card(s4, pos_x, pos_y, st_w, st_h, bg_color=CARD_BG, border_color=CARD_BORDER)
        # Top banner of card
        top_ban = add_card(s4, pos_x, pos_y, st_w, 0.45, bg_color=bg_c, border_color=CARD_BORDER)
        p_tb = top_ban.text_frame.paragraphs[0]
        p_tb.text = title
        p_tb.font.bold = True
        p_tb.font.size = Pt(10)
        p_tb.font.color.rgb = NAVY_PRIMARY

        tb_inner = s4.shapes.add_textbox(Inches(pos_x + 0.15), Inches(pos_y + 0.5), Inches(st_w - 0.3), Inches(1.85))
        tf_in = tb_inner.text_frame
        for b_lbl, b_txt in items:
            add_bullet(tf_in, b_lbl, b_txt, font_size=9.5)

    set_speaker_notes(s4, "Nguyễn Văn Đức", "Thành viên",
        "Thưa Thầy, luồng xử lý Node-RED của nhóm gồm 29 nodes được chia thành 4 giai đoạn khép kín theo mô hình hướng sự kiện (Event-Driven Pipeline). "
        "Ở Giai đoạn 1, hệ thống tiếp nhận các bản tin telemetry định kỳ 2 giây hoặc bản tin alarm khẩn cấp từ ESP32, sau đó kiểm tra tính hợp lệ của dữ liệu. "
        "Ở Giai đoạn 2, dữ liệu được chuyển đến bộ não FSM để đánh giá cùng 5 quy tắc PCCC. Nếu thỏa điều kiện báo động, "
        "Giai đoạn 3 lập tức phát lệnh Downlink xuống Broker để bật quạt hút và hú còi. Đồng thời, Giai đoạn 4 ghi nhận sự kiện vào nhật ký kiểm toán "
        "và áp dụng bộ lọc chống spam cảnh báo.")

    # ==============================================================================
    # SLIDE 5: MÁY TRẠNG THÁI HỮU HẠN FSM (5 TRẠNG THÁI)
    # ==============================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Mô Hình Điều Khiển Trung Tâm", "Máy Trạng Thái Hữu Hạn FSM (5 Trạng Thái Vận Hành)")
    add_footer(s5, 5)

    # 5 State Cards across the screen
    fsm_states = [
        ("1. SAFE (An Toàn)", "PPM < 250 PPM và Nhiệt độ < 50°C", "Quạt: TẮT\nCòi: TẮT", "Hệ thống bình thường, theo dõi định kỳ 2s", SUCCESS_BG, SUCCESS_GREEN),
        ("2. WARNING (Cảnh Giác)", "250 <= PPM < 400 hoặc Nhiệt >= 55°C", "Quạt: TẮT\nCòi: TẮT\nGhi log cảnh báo", "Chớm có khói hoặc gia nhiệt bất thường", WARN_BG, WARN_ORANGE),
        ("3. ALARM (Báo Động)", "PPM >= 400 PPM hoặc nhận cờ URGENT", "Quạt: BẬT HÚT\nCòi: HÚ LIÊN TỤC\nPhát Downlink", "Hỏa hoạn nguy cấp, ưu tiên cứu hộ tính mạng", ALARM_BG, ALARM_RED),
        ("4. COOLDOWN (Làm Mát)", "Đang ở ALARM và PPM hạ xuống < 300 PPM", "Quạt: DUY TRÌ BẬT\nCòi: TẮT\nĐếm trễ 20s", "Xả sạch khói dư, bảo vệ relay chống hồ quang", TECH_BLUE_LIGHT, TECH_BLUE),
        ("5. OFFLINE (Mất Mạng)", "Quá 10s không có tin hoặc nhận cờ LWT", "Giữ nguyên an toàn\nCảnh báo đứt mạng", "Trạm cảm biến rớt mạng hoặc đứt nguồn", RGBColor(241, 245, 249), SLATE_MUTED)
    ]

    card_fsm_w = 2.22
    gap_fsm = 0.15
    start_x = 0.8

    for idx, (st_name, st_cond, st_act, st_desc, bg_col, text_col) in enumerate(fsm_states):
        cx = start_x + (card_fsm_w + gap_fsm) * idx
        add_card(s5, cx, 1.45, card_fsm_w, 4.3, bg_color=CARD_BG, border_color=CARD_BORDER)
        
        # State Header Pill
        pill = add_card(s5, cx + 0.1, 1.55, card_fsm_w - 0.2, 0.55, bg_color=bg_col, border_color=text_col)
        p_pill = pill.text_frame.paragraphs[0]
        p_pill.text = st_name
        p_pill.font.bold = True
        p_pill.font.size = Pt(9.5)
        p_pill.font.color.rgb = text_col

        tb_fs = s5.shapes.add_textbox(Inches(cx + 0.1), Inches(2.2), Inches(card_fsm_w - 0.2), Inches(3.4))
        tf_fs = tb_fs.text_frame
        add_bullet(tf_fs, "Điều kiện kích hoạt", st_cond, font_size=9, bold_color=text_col)
        add_bullet(tf_fs, "Hành vi chấp hành", st_act, font_size=9, bold_color=NAVY_PRIMARY)
        add_bullet(tf_fs, "Ý nghĩa nghiệp vụ", st_desc, font_size=9, bold_color=SLATE_MUTED)

    # Bottom Transition Explanation Bar
    bot_box = add_card(s5, 0.8, 5.9, 11.733, 0.95, bg_color=RGBColor(245, 247, 250), border_color=CARD_BORDER)
    tb_bb = s5.shapes.add_textbox(Inches(0.95), Inches(5.95), Inches(11.4), Inches(0.85))
    tf_bb = tb_bb.text_frame
    p_b1 = tf_bb.paragraphs[0]
    p_b1.text = "CHU TRÌNH CHUYỂN TRẠNG THÁI TỰ ĐỘNG & CƠ CHẾ PHỤC HỒI:"
    p_b1.font.bold = True
    p_b1.font.size = Pt(9.5)
    p_b1.font.color.rgb = NAVY_PRIMARY
    p_b2 = tf_bb.add_paragraph()
    p_b2.text = "SAFE ⇄ WARNING ➔ ALARM ➔ COOLDOWN (duy trì 20s) ➔ SAFE. Nếu trong khi làm mát mà khói tăng lại >= 400 PPM ➔ Lập tức quay lại ALARM. Nếu ở bất kỳ trạng thái nào bị mất kết nối quá 10s ➔ Chuyển sang OFFLINE; khi kết nối lại tự động đồng bộ về SAFE."
    p_b2.font.size = Pt(9)
    p_b2.font.color.rgb = SLATE_DARK

    set_speaker_notes(s5, "Nguyễn Vĩnh Khang", "Nhóm trưởng",
        "Thưa Thầy, một trong những đóng góp trọng tâm của Tuần 5 là thiết kế Máy trạng thái hữu hạn FSM 5 trạng thái hoàn chỉnh. "
        "Mô hình này giúp triệt tiêu hoàn toàn hiện tượng xung đột điều khiển. Đặc biệt giữa ALARM và SAFE, chúng em đưa vào trạng thái COOLDOWN. "
        "Khi nồng độ khói đã giảm dưới 300 PPM, quạt không tắt ngay mà tiếp tục chạy thêm 20 giây để xả hết lượng khói tích tụ trong phòng. "
        "Nếu trong 20 giây này khói bất ngờ bùng phát trở lại, FSM ngay lập tức nhảy ngược về ALARM mà không bị trễ.")

    # ==============================================================================
    # SLIDE 6: MA TRẬN 5 QUY TẮC TỰ ĐỘNG HÓA PCCC CỐT LÕI
    # ==============================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Quy Tắc Tự Động Hóa Nghiệp Vụ", "Ma Trận 5 Quy Tắc Tự Động Hóa PCCC Cốt Lõi (Core Rules)")
    add_footer(s6, 6)

    # Table layout for 5 rules
    rows = 6
    cols = 5
    tbl_shape = s6.shapes.add_table(rows, cols, Inches(0.8), Inches(1.45), Inches(11.733), Inches(5.3))
    table = tbl_shape.table

    table.columns[0].width = Inches(1.8) # Tên Rule
    table.columns[1].width = Inches(2.7) # Điều kiện kích hoạt
    table.columns[2].width = Inches(2.4) # Lệnh Downlink
    table.columns[3].width = Inches(2.4) # Trạng thái FSM
    table.columns[4].width = Inches(2.433) # Cơ chế an toàn

    headers = ["Quy Tắc (Core Rule)", "Điều Kiện Kích Hoạt", "Lệnh Điều Phối Downlink", "Chuyển Đổi FSM", "Cơ Chế Đảm Bảo An Toàn"]
    for c_idx, h_text in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY_PRIMARY
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.name = FONT_HEADING
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)
        p.alignment = PP_ALIGN.CENTER

    rule_data = [
        ("Rule 1: Smoke Hazard\n(Khói vượt ngưỡng)", "PPM >= 400 PPM (Ngày)\nhoặc PPM >= 350 PPM (Đêm)", "Fan: ON (bật quạt)\nBuzzer: ON (hú còi)", "Chuyển sang ALARM\n(Ghi log CRITICAL)", "Bảo vệ đường thở người dân, thông gió chống ngạt khí độc"),
        ("Rule 2: Thermal Hazard\n(Nhiệt độ nguy hiểm)", "Nhiệt độ DHT22 >= 55°C\nhoặc tốc độ gia nhiệt > 3°C/phút", "Buzzer: Bíp cảnh báo\nFan: ON (nếu kèm khói)", "Chuyển sang WARNING\nhoặc ALARM (nếu cháy bùng)", "Cảnh báo sớm hiện tượng cháy âm ỉ hoặc chập điện sinh nhiệt"),
        ("Rule 3: Anti-chattering\n(Trễ Hysteresis)", "Đang ALARM và khói hạ < 300 PPM\n(Vùng đệm chênh lệch 100 PPM)", "Fan: Duy trì chạy 20 giây\nBuzzer: TẮT tiếng", "ALARM ➔ COOLDOWN\n(Hết 20s ➔ SAFE)", "Triệt tiêu hiện tượng đóng ngắt liên tục phá hủy tiếp điểm Relay"),
        ("Rule 4: Night Scheduler\n(Lịch trình ban đêm)", "Khung giờ 22:00 – 06:00 sáng\n(Cư dân đang ngủ say)", "Hạ ngưỡng kích hoạt còi từ\n400 PPM xuống 350 PPM", "Tự động kích hoạt\nChế độ Nhạy Cao", "Đánh thức người dân sớm hơn 1.5 - 2 phút khi xảy ra cháy ban đêm"),
        ("Rule 5: Watchdog Heartbeat\n(Giám sát cảm biến)", "Quá 10s không có telemetry\nhoặc nhận bản tin LWT Offline", "Giữ nguyên an toàn thiết bị,\nPhát tin báo đứt mạng", "Chuyển sang OFFLINE\n(Ghi log WARNING)", "Ngăn chặn báo động giả do trôi số liệu hoặc hỏng cảm biến")
    ]

    for r_idx, row_values in enumerate(rule_data):
        bg_r = CARD_BG if r_idx % 2 == 0 else RGBColor(245, 248, 252)
        for c_idx, val in enumerate(row_values):
            cell = table.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg_r
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = FONT_BODY
            p.font.size = Pt(9.2)
            p.font.color.rgb = SLATE_DARK
            if c_idx == 0:
                p.font.bold = True
                p.font.color.rgb = NAVY_PRIMARY

    set_speaker_notes(s6, "Nguyễn Văn Đức", "Thành viên",
        "Thưa Thầy, ma trận 5 quy tắc này là bằng chứng rõ nhất cho việc Middleware không chỉ forward dữ liệu. "
        "Mỗi quy tắc đều gắn liền với bài toán thực tế của công tác phòng cháy chữa cháy: "
        "Rule 1 và Rule 2 xử lý nguy cơ khói và nhiệt độ theo thời gian thực; Rule 3 giải quyết bài toán độ bền phần cứng tiếp điểm Relay; "
        "Rule 4 tối ưu hóa sự an toàn của con người khi ngủ say vào ban đêm; và Rule 5 bảo đảm tính sẵn sàng cao của hệ thống IoT thông qua giám sát nhịp tim.")

    # ==============================================================================
    # SLIDE 7: LUỒNG CHỨC NĂNG: HYSTERESIS & COOLDOWN RELAY
    # ==============================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Giải Thuật An Toàn Phần Cứng", "Luồng Nghiệp Vụ 1: Giải Thuật Hysteresis & Cooldown Relay")
    add_footer(s7, 7)

    # Left: Explanation of Problem & Solution
    card_left = add_card(s7, 0.8, 1.45, 5.6, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
    tb_el = s7.shapes.add_textbox(Inches(0.95), Inches(1.6), Inches(5.3), Inches(5.0))
    tf_el = tb_el.text_frame
    p_el0 = tf_el.paragraphs[0]
    p_el0.text = "VẤN ĐỀ THỰC TẾ & NGUY CƠ HỎNG HÓC PHẦN CỨNG:"
    p_el0.font.bold = True
    p_el0.font.size = Pt(11)
    p_el0.font.color.rgb = ALARM_RED

    add_bullet(tf_el, "Hiện tượng Chattering", "Khói bốc lên chập chờn dao động quanh ngưỡng 400 PPM (398 -> 402 -> 399 PPM).")
    add_bullet(tf_el, "Nguy cơ tiếp điểm Relay", "Nếu không có trễ, Relay quạt sẽ đóng/ngắt liên tục hàng chục lần trong 1 phút, sinh hồ quang điện gây hàn dính hoặc cháy tiếp điểm Relay.")
    add_bullet(tf_el, "Khói tồn dư", "Khi nồng độ khói vừa chớm hạ, trong góc phòng vẫn tích tụ khí CO và khói đặc, nếu tắt quạt ngay sẽ làm nồng độ bùng phát trở lại.")

    p_el1 = tf_el.add_paragraph()
    p_el1.text = "\nGIẢI PHÁP 2 LỚP BẢO VỆ CỦA NHÓM 04:"
    p_el1.font.bold = True
    p_el1.font.size = Pt(11)
    p_el1.font.color.rgb = SUCCESS_GREEN

    add_bullet(tf_el, "Lớp 1 - Vùng đệm 100 PPM", "Ngưỡng kích hoạt báo động là 400 PPM, nhưng ngưỡng hạ báo động phải xuống dưới 300 PPM mới bắt đầu xét tắt quạt.")
    add_bullet(tf_el, "Lớp 2 - Trễ Cooldown 20s", "Khi khói đã < 300 PPM, chuyển sang trạng thái COOLDOWN, quạt tiếp tục chạy cưỡng bức đúng 20 giây để xả sạch khói rồi mới ngắt điện.")

    # Right: Step-by-step state flowchart
    card_right = add_card(s7, 6.7, 1.45, 5.833, 5.3, bg_color=RGBColor(245, 250, 255), border_color=TECH_BLUE_ACCENT)
    tb_fl = s7.shapes.add_textbox(Inches(6.9), Inches(1.6), Inches(5.4), Inches(5.0))
    tf_fl = tb_fl.text_frame
    p_fl0 = tf_fl.paragraphs[0]
    p_fl0.text = "SƠ ĐỒ LUỒNG ĐIỀU PHỐI HYSTERESIS (NO CODE):"
    p_fl0.font.bold = True
    p_fl0.font.size = Pt(11)
    p_fl0.font.color.rgb = NAVY_PRIMARY

    steps = [
        ("BƯỚC 1: BÁO ĐỘNG BÙNG PHÁT", "Khói đo được >= 400 PPM ➔ FSM kích hoạt ALARM ➔ Quạt BẬT, Còi HÚ.", ALARM_BG, ALARM_RED),
        ("BƯỚC 2: KHÓI BẮT ĐẦU GIẢM", "Khói giảm về vùng 300 - 400 PPM ➔ Nằm trong vùng đệm Hysteresis ➔ Quạt GIỮ NGUYÊN TRẠNG THÁI BẬT.", WARN_BG, WARN_ORANGE),
        ("BƯỚC 3: XUỐNG DƯỚI NGƯỠNG ĐỆM", "Khói giảm < 300 PPM ➔ FSM tự động chuyển sang trạng thái COOLDOWN ➔ Tắt còi, Quạt DUY TRÌ BẬT.", TECH_BLUE_LIGHT, TECH_BLUE),
        ("BƯỚC 4: ĐẾM NGƯỢC 20 GIÂY", "Bộ đếm timer 20s hoạt động ➔ Nếu khói tăng lại >= 400 PPM ➔ Quay lại Bước 1; Nếu giữ an toàn ➔ Chuyển Bước 5.", RGBColor(254, 243, 199), RGBColor(180, 83, 9)),
        ("BƯỚC 5: NGẮT AN TOÀN VỀ SAFE", "Hết 20 giây làm mát ➔ Phát lệnh Downlink tắt quạt ➔ FSM trở về SAFE hoàn toàn an toàn.", SUCCESS_BG, SUCCESS_GREEN)
    ]

    for s_title, s_desc, s_bg, s_col in steps:
        p_st = tf_fl.add_paragraph()
        p_st.space_after = Pt(2)
        r_st = p_st.add_run()
        r_st.text = "► " + s_title + "\n"
        r_st.font.bold = True
        r_st.font.size = Pt(9.5)
        r_st.font.color.rgb = s_col

        r_sd = p_st.add_run()
        r_sd.text = s_desc + "\n"
        r_sd.font.size = Pt(9)
        r_sd.font.color.rgb = SLATE_DARK

    set_speaker_notes(s7, "Nguyễn Văn Đức", "Thành viên",
        "Thưa Thầy, Slide này giải thích chi tiết giải thuật Hysteresis Cooldown mà nhóm tự xây dựng trên Node-RED. "
        "Trong các hệ thống báo khói giá rẻ, rơ-le quạt rất dễ bị hỏng do khói chập chờn quanh một ngưỡng duy nhất. "
        "Bằng cách kết hợp vùng đệm delta 100 PPM và bộ đếm thời gian 20 giây làm mát, hệ thống vừa bảo vệ triệt để tuổi thọ tiếp điểm cơ khí của Relay, "
        "vừa bảo đảm hút sạch khói độc tồn dư trong căn phòng.")

    # ==============================================================================
    # SLIDE 8: LUỒNG CHỨC NĂNG: GIÁM SÁT NHỊP TIM (WATCHDOG) & LWT BROKER
    # ==============================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Cơ Chế Giám Sát Sẵn Sàng Cao", "Luồng Nghiệp Vụ 2: Watchdog Giám Sát Nhịp Tim & LWT Broker")
    add_footer(s8, 8)

    # 2 Comparison Columns: Software Timer vs MQTT LWT
    card_wd = add_card(s8, 0.8, 1.45, 5.6, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
    tb_wd = s8.shapes.add_textbox(Inches(0.95), Inches(1.6), Inches(5.3), Inches(5.0))
    tf_wd = tb_wd.text_frame
    p_wd = tf_wd.paragraphs[0]
    p_wd.text = "CƠ CHẾ 1: WATCHDOG HEARTBEAT TIMEOUT (10S)"
    p_wd.font.bold = True
    p_wd.font.size = Pt(11)
    p_wd.font.color.rgb = TECH_BLUE

    add_bullet(tf_wd, "Nguyên lý nhịp tim", "ESP32 gửi gói tin telemetry chu kỳ 2s. Node-RED cài đặt đồng hồ đếm lùi Timeout 10 giây (tương đương mất liên tiếp 5 gói tin).")
    add_bullet(tf_wd, "Reset nhịp tim", "Mỗi khi có gói tin hợp lệ từ thiết bị gửi lên, đồng hồ đếm lùi tự động nạp lại giá trị 10s.")
    add_bullet(tf_wd, "Kích hoạt cảnh báo", "Nếu đồng hồ đếm về 0 (quá 10s không thấy tin) -> Node-RED tự động kích hoạt sự kiện Sensor Node Timeout.")
    add_bullet(tf_wd, "Xử lý nghiệp vụ", "FSM lập tức chuyển sang trạng thái OFFLINE, gửi thông báo đứt cáp hoặc mất nguồn lên Dashboard để cán bộ kỹ thuật kiểm tra.")

    card_lwt = add_card(s8, 6.7, 1.45, 5.833, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
    tb_lwt = s8.shapes.add_textbox(Inches(6.85), Inches(1.6), Inches(5.5), Inches(5.0))
    tf_lwt = tb_lwt.text_frame
    p_lwt = tf_lwt.paragraphs[0]
    p_lwt.text = "CƠ CHẾ 2: MQTT LAST WILL AND TESTAMENT (LWT)"
    p_lwt.font.bold = True
    p_lwt.font.size = Pt(11)
    p_lwt.font.color.rgb = NAVY_PRIMARY

    add_bullet(tf_lwt, "Khai báo di chúc LWT", "Khi ESP32 kết nối vào Broker EMQX, thiết bị đăng ký sẵn thông điệp di chúc: Topic `smoke/lwt`, nội dung `offline` (QoS 1, Retain true).")
    add_bullet(tf_lwt, "Phát hiện đứt kết nối tức thì", "Nếu ESP32 bị mất điện đột ngột hoặc đứt cáp mạng ngầm, MQTT Broker phát hiện đứt socket TCP và chủ động bắn bản tin LWT.")
    add_bullet(tf_lwt, "Node-RED bắt sự kiện", "Node-RED nhận bản tin LWT trong vòng < 500ms mà không cần đợi hết 10 giây Timeout của phần mềm.")
    add_bullet(tf_lwt, "Tính sẵn sàng cao", "Sự kết hợp song song giữa Watchdog 10s và LWT Broker đảm bảo phát hiện 100% sự cố mạng trong mọi tình huống.")

    set_speaker_notes(s8, "Nguyễn Vĩnh Khang", "Nhóm trưởng",
        "Kính thưa Thầy, một hệ thống IoT báo cháy quan trọng nhất là phải biết khi nào cảm biến bị hỏng hoặc mất mạng. "
        "Nhóm kết hợp 2 tầng bảo vệ: tầng giao thức mạng dùng MQTT Last Will and Testament của Broker để bắt sự kiện ngắt kết nối vật lý tức thì trong nửa giây; "
        "và tầng ứng dụng dùng Watchdog Timer 10 giây để bắt các trường hợp vi điều khiển bị treo hoặc trôi thời gian. "
        "Nhờ đó, giảng viên và người vận hành luôn nắm bắt chính xác độ tin cậy của dữ liệu thời gian thực.")

    # ==============================================================================
    # SLIDE 9: QUẢN TRỊ HẠM ĐỘI CẢM BIẾN & NHẬT KÝ KIỂM TOÁN (AUDIT TRAIL)
    # ==============================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Độ Tin Cậy & Quản Trị Hệ Thống", "Quản Trị Hạm Đội Cảm Biến & Nhật Ký Kiểm Toán (Audit Trail)")
    add_footer(s9, 9)

    # Left: Fleet Management Slide 65
    card_fl = add_card(s9, 0.8, 1.45, 5.6, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
    tb_fm = s9.shapes.add_textbox(Inches(0.95), Inches(1.6), Inches(5.3), Inches(5.0))
    tf_fm = tb_fm.text_frame
    p_fm = tf_fm.paragraphs[0]
    p_fm.text = "QUẢN TRỊ HẠM ĐỘI THIẾT BỊ (MULTI-DEVICE FLEET):"
    p_fm.font.bold = True
    p_fm.font.size = Pt(11)
    p_fm.font.color.rgb = NAVY_PRIMARY

    add_bullet(tf_fm, "Căn cứ kỹ thuật", "Triển khai đúng yêu cầu nâng cấp tại Slide 65 bài giảng của GVHD: chuyển từ hệ thống đơn điểm sang đa trạm cảm biến.")
    add_bullet(tf_fm, "Danh mục thiết bị (Whitelist)", "Node-RED lưu danh bạ các trạm cảm biến hợp lệ theo định danh: Station A01 (Phòng Lab), Station A02 (Kho hóa chất), Station A03 (Hành lang).")
    add_bullet(tf_fm, "Xác thực gói tin", "Mỗi gói tin gửi lên phải chứa Device ID và Access Token hợp lệ; các thiết bị lạ bị từ chối ngay lập tức.")
    add_bullet(tf_fm, "Khả năng mở rộng", "Dễ dàng thêm mới trạm cảm biến trong toàn tòa nhà mà không cần sửa đổi kiến trúc lõi của Middleware.")

    # Right: Audit Trail & Rate Limiting
    card_lg = add_card(s9, 6.7, 1.45, 5.833, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
    tb_lg = s9.shapes.add_textbox(Inches(6.85), Inches(1.6), Inches(5.5), Inches(5.0))
    tf_lg = tb_lg.text_frame
    p_lg = tf_lg.paragraphs[0]
    p_lg.text = "NHẬT KÝ KIỂM TOÁN (AUDIT TRAIL) & RATE LIMITING:"
    p_lg.font.bold = True
    p_lg.font.size = Pt(11)
    p_lg.font.color.rgb = TECH_BLUE

    add_bullet(tf_lg, "Lưu trữ 2 cấp", "• Cấp 1 (Bộ nhớ đệm): Mảng vòng 50 sự kiện gần nhất phục vụ hiển thị thời gian thực lên Dashboard.\n• Cấp 2 (Bền vững): Ghi nối tiếp vào file logs/event_history.log để phục vụ điều tra nguyên nhân cháy nổ.")
    add_bullet(tf_lg, "Định dạng bản ghi chuẩn hóa", "Mỗi sự kiện gồm: Dấu thời gian ISO 8601, Mã trạm, Trạng thái FSM, Nồng độ khói, Nhiệt độ và Lệnh điều khiển đã phát.")
    add_bullet(tf_lg, "Chống bão tin nhắn (Rate Limiter)", "Khi cháy lớn, cảm biến liên tục gửi cảnh báo; Node-RED tự động giới hạn gửi tin thông báo khẩn cấp chu kỳ tối thiểu 30 giây/lần, ngăn chặn nghẽn mạng và treo máy chủ.")

    set_speaker_notes(s9, "Nguyễn Văn Mãnh", "Thành viên",
        "Thưa Thầy, theo đúng góp ý ở Slide 65, nhóm em đã thiết kế Middleware hỗ trợ quản trị hạm đội đa thiết bị. "
        "Hệ thống kiểm tra danh bạ Whitelist để chỉ chấp nhận dữ liệu từ các trạm cảm biến đã được xác thực. "
        "Về nhật ký kiểm toán, toàn bộ sự kiện chuyển trạng thái FSM và lệnh điều khiển đều được ghi file bền vững để phục vụ công tác điều tra PCCC. "
        "Bộ giới hạn tốc độ Rate Limiter 30 giây giúp hệ thống không bị quá tải khi sự cố khói diễn ra dồn dập.")

    # ==============================================================================
    # SLIDE 10: KẾT QUẢ KIỂM THỬ CHỨC NĂNG TUẦN 5 (15/15 PASS)
    # ==============================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Minh Chứng Nghiệm Thu", "Kết Quả Kiểm Thử Chức Năng Tuần 5 (15/15 Kịch Bản Đạt 100%)")
    add_footer(s10, 10)

    # Top KPI Cards
    kpi_w = 2.7
    kpi_gap = 0.3
    kpi_left = 0.8

    kpi_data = [
        ("15 / 15", "KỊCH BẢN PASS", SUCCESS_GREEN, SUCCESS_BG),
        ("100%", "TỶ LỆ THÀNH CÔNG", SUCCESS_GREEN, SUCCESS_BG),
        ("< 15 ms", "TRỄ XỬ LÝ MIDDLEWARE", TECH_BLUE, TECH_BLUE_LIGHT),
        ("0 LỖI", "XUNG ĐỘT TRẠNG THÁI", NAVY_PRIMARY, RGBColor(240, 245, 255))
    ]

    for idx, (num, lbl, col, bg_c) in enumerate(kpi_data):
        kx = kpi_left + (kpi_w + kpi_gap) * idx
        kcard = add_card(s10, kx, 1.45, kpi_w, 1.15, bg_color=bg_c, border_color=col)
        tb_k = s10.shapes.add_textbox(Inches(kx), Inches(1.5), Inches(kpi_w), Inches(1.0))
        tf_k = tb_k.text_frame
        p_kn = tf_k.paragraphs[0]
        p_kn.alignment = PP_ALIGN.CENTER
        p_kn.text = num
        p_kn.font.bold = True
        p_kn.font.size = Pt(20)
        p_kn.font.color.rgb = col

        p_kl = tf_k.add_paragraph()
        p_kl.alignment = PP_ALIGN.CENTER
        p_kl.text = lbl
        p_kl.font.bold = True
        p_kl.font.size = Pt(8.5)
        p_kl.font.color.rgb = SLATE_DARK

    # Table of Test Suites
    tbl_s = s10.shapes.add_table(5, 4, Inches(0.8), Inches(2.8), Inches(11.733), Inches(3.9))
    tt = tbl_s.table
    tt.columns[0].width = Inches(2.2) # Nhóm kiểm thử
    tt.columns[1].width = Inches(4.5) # Kịch bản kiểm thử
    tt.columns[2].width = Inches(3.0) # Kết quả mong đợi & Thực tế
    tt.columns[3].width = Inches(2.033) # Trạng thái

    t_headers = ["Nhóm Kiểm Thử", "Kịch Bản Thực Nghiệm", "Kết Quả Thực Tế Đạt Được", "Đánh Giá"]
    for c_i, h_t in enumerate(t_headers):
        cell = tt.cell(0, c_i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY_PRIMARY
        p = cell.text_frame.paragraphs[0]
        p.text = h_t
        p.font.bold = True
        p.font.size = Pt(10)
        p.font.color.rgb = RGBColor(255, 255, 255)
        p.alignment = PP_ALIGN.CENTER

    test_rows = [
        ("1. Phân ngưỡng Khói & Nhiệt (Rule 1, 2)", "Bơm telemetry khói 450 PPM và nhiệt 60°C qua MQTTX", "FSM nhảy sang ALARM, Downlink lệnh bật quạt và còi trong 12ms", "PASS (100%)"),
        ("2. Hysteresis Cooldown (Rule 3)", "Hạ khói từ 450 PPM xuống 280 PPM, quan sát hành vi quạt", "FSM chuyển COOLDOWN, quạt chạy đủ 20s rồi mới ngắt an toàn", "PASS (100%)"),
        ("3. Lịch Trình Ban Đêm (Rule 4)", "Mô phỏng thời gian 23:30, bơm khói 360 PPM", "Ngưỡng tự động hạ về 350 PPM, kích hoạt ALARM tức thì", "PASS (100%)"),
        ("4. Ngoại Lệ Mạng & Bảo Mật (Rule 5)", "Ngắt kết nối ESP32 đột ngột và gửi tin từ Client ID lạ", "Broker bắn LWT, FSM đổi OFFLINE; Thiết bị lạ bị từ chối 100%", "PASS (100%)")
    ]

    for r_i, r_val in enumerate(test_rows):
        for c_i, val in enumerate(r_val):
            cell = tt.cell(r_i + 1, c_i)
            cell.fill.solid()
            cell.fill.fore_color.rgb = CARD_BG if r_i % 2 == 0 else RGBColor(245, 248, 252)
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(9.2)
            p.font.color.rgb = SLATE_DARK
            if c_i == 0:
                p.font.bold = True
                p.font.color.rgb = NAVY_PRIMARY
            elif c_i == 3:
                p.font.bold = True
                p.font.color.rgb = SUCCESS_GREEN
                p.alignment = PP_ALIGN.CENTER

    set_speaker_notes(s10, "Nguyễn Văn Mãnh", "Thành viên",
        "Thưa Thầy, để chứng minh độ tin cậy của Tầng 3, nhóm đã xây dựng bộ kịch bản kiểm thử tự động gồm 15 test cases bao quát toàn bộ các trường hợp biên. "
        "Kết quả kiểm thử thực tế đạt 15/15 kịch bản PASS (100%), độ trễ xử lý nghiệp vụ tại Node-RED chỉ dưới 15ms. "
        "Mọi hành vi chuyển trạng thái FSM, điều phối lệnh Downlink và cơ chế bảo vệ tiếp điểm quạt đều hoạt động hoàn toàn chính xác theo đúng đặc tả kỹ thuật.")

    # ==============================================================================
    # SLIDE 11: TỔNG KẾT MILESTONE TUẦN 5 & KẾ HOẠCH TUẦN 6
    # ==============================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "Đánh Giá & Hướng Phát Triển", "Tổng Kết Nghiệm Thu Tuần 5 & Kế Hoạch Bàn Giao Tuần 6")
    add_footer(s11, 11)

    # 2 Summary Columns
    card_sum = add_card(s11, 0.8, 1.45, 5.6, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
    tb_sm = s11.shapes.add_textbox(Inches(0.95), Inches(1.6), Inches(5.3), Inches(5.0))
    tf_sm = tb_sm.text_frame
    p_sm = tf_sm.paragraphs[0]
    p_sm.text = "TỔNG KẾT THÀNH QUẢ ĐẠT ĐƯỢC TUẦN 5:"
    p_sm.font.bold = True
    p_sm.font.size = Pt(11)
    p_sm.font.color.rgb = SUCCESS_GREEN

    add_bullet(tf_sm, "Nghiệm thu Milestone", "Hoàn thành 100% mục tiêu Milestone Tầng 3: Middleware / Automation Engine (10% tổng điểm đồ án).")
    add_bullet(tf_sm, "Bộ não điều phối Node-RED", "Flow hoàn chỉnh 29 nodes xử lý mượt mà trên broker.emqx.io:1883.")
    add_bullet(tf_sm, "FSM 5 Trạng Thái", "Mô hình trạng thái hoàn chỉnh: SAFE, WARNING, ALARM, COOLDOWN, OFFLINE không có điểm nghẽn logic.")
    add_bullet(tf_sm, "5 Quy tắc tự động hóa", "Đã hiện thực và kiểm thử trọn vẹn 5 rules bảo đảm tính mạng và độ bền phần cứng.")
    add_bullet(tf_sm, "Hồ sơ bàn giao đầy đủ", "Bao gồm file flow JSON, báo cáo kỹ thuật Word, bảng kịch bản 15 test cases và file slide trình chiếu.")

    card_next = add_card(s11, 6.7, 1.45, 5.833, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
    tb_nx = s11.shapes.add_textbox(Inches(6.85), Inches(1.6), Inches(5.5), Inches(5.0))
    tf_nx = tb_nx.text_frame
    p_nx = tf_nx.paragraphs[0]
    p_nx.text = "KẾ HOẠCH TRIỂN KHAI TUẦN 6 (MILESTONE M3):"
    p_nx.font.bold = True
    p_nx.font.size = Pt(11)
    p_nx.font.color.rgb = TECH_BLUE

    add_bullet(tf_nx, "Mục tiêu trọng tâm", "Xây dựng Tầng 4 – Application / Platform, đạt Milestone M3: Full 4-Layer IoT System (hoàn chỉnh 4 tầng).")
    add_bullet(tf_nx, "Giao diện Web Platform", "Thiết kế Web Dashboard chuẩn Glassmorphism: Hiển thị Gauges, biểu đồ đa trục thời gian thực Chart.js và Sơ đồ mặt bằng Tòa A.")
    add_bullet(tf_nx, "Điều khiển chấp hành 2 chiều", "Tích hợp các nút điều khiển Downlink: Quạt (ON/OFF/AUTO), Còi (Mute 180s/Test) kết nối trực tiếp qua WebSockets.")
    add_bullet(tf_nx, "Kênh cảnh báo Telegram", "Tích hợp Telegram Bot Webhook tự động bắn tin nhắn khẩn cấp có tọa độ và hướng dẫn thoát nạn.")
    add_bullet(tf_nx, "Phân quyền & Khóa an toàn", "Thiết lập phân quyền người dùng RBAC và Khóa an toàn PCCC cấm ngắt quạt khi có cháy.")

    set_speaker_notes(s11, "Nguyễn Vĩnh Khang", "Nhóm trưởng",
        "Kính thưa Thầy Võ Hoàng Hải, tóm lại ở Tuần 5 nhóm em đã hoàn thành 100% mục tiêu của Tầng 3 Middleware, "
        "đáp ứng đầy đủ các tiêu chuẩn khắt khe về tự động hóa và an toàn PCCC. "
        "Đây là nền tảng vững chắc để ở Tuần 6 tới, nhóm em tự tin hiện thực hóa Tầng 4 Application với Web Dashboard thời gian thực, "
        "kênh thông báo Telegram và hệ thống phân quyền an toàn, chính thức cán mốc Milestone M3 Full 4-Layer IoT. "
        "Nhóm 04 xin chân thành cảm ơn Thầy và rất mong nhận được những góp ý quý báu của Thầy!")

    output_dir = r"e:\IoT\DoAn\docs\pptx"
    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, "BaoCao_TienDo_Tuan5_Nhom04.pptx")
    prs.save(out_file)
    print(f"Successfully generated Week 5 presentation: {out_file} (11 slides)")

if __name__ == "__main__":
    build_all_slides()
