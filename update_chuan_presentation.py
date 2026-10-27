# -*- coding: utf-8 -*-
"""
Script trực tiếp cập nhật file: docs/pptx/Bao_Cao_He_Thong_IoT_4_Slides_Nhom04_Chuan.pptx
Theo đúng các yêu cầu nghiêm ngặt của người dùng:
1. Slide 1: Bổ sung tên nhóm Nhóm 04 (Lớp N09) và 3 thành viên kèm MSSV/Vai trò; Xóa bỏ dòng tham chiếu Slide 7; 3 Card ghi đúng 3 dòng tên part khái quát.
2. Slide 2: Giữ nguyên 100% hai bảng BOM (Table 12 và Table 14 kèm hàng ~720k); Chỉ tinh gọn 2 khối trên (Firmware & Hardware) cho bài nói 3 phút.
3. Slide 3: Tái cấu trúc phân tích Topic MQTT sâu sắc (Cấu trúc phân cấp, Ma trận Topic, Tại sao xây dựng như thế, Tác dụng gì) + 4 Microservices.
4. Slide 4: Tinh gọn 4 trụ cột Web App thành các bullet đắt giá cho bài nói 45s.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import shutil
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Bảng màu
NAVY_PRIMARY     = RGBColor(26, 54, 93)     # #1A365D
NAVY_DARK        = RGBColor(15, 23, 42)     # #0F172A
TECH_BLUE        = RGBColor(37, 99, 235)    # #2563EB
TECH_BLUE_LIGHT  = RGBColor(239, 246, 255) # #EFF6FF
TECH_BLUE_BORDER = RGBColor(191, 219, 254) # #BFDBFE
CYAN_ACCENT      = RGBColor(6, 182, 212)    # #06B6D4
AMBER_GOLD       = RGBColor(245, 158, 11)   # #F59E0B
SLATE_DARK       = RGBColor(30, 41, 59)     # #1E293B
SLATE_MUTED      = RGBColor(100, 116, 139)  # #64748B
BG_LIGHT         = RGBColor(248, 250, 252)  # #F8FAFC
CARD_BG          = RGBColor(255, 255, 255)  # Trắng
CARD_BORDER      = RGBColor(226, 232, 240)  # #E2E8F0
ALARM_RED        = RGBColor(220, 38, 38)    # #DC2626
SUCCESS_GREEN    = RGBColor(22, 163, 74)    # #16A34A

FONT_HEADING = "Arial"
FONT_BODY    = "Arial"

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

def update_presentation():
    pptx_path = r"e:\IoT\DoAn\docs\pptx\Bao_Cao_He_Thong_IoT_4_Slides_Nhom04_Chuan.pptx"
    backup_path = r"e:\IoT\DoAn\docs\pptx\Bao_Cao_He_Thong_IoT_4_Slides_Nhom04_Chuan_Backup.pptx"
    
    # Backup
    shutil.copy2(pptx_path, backup_path)
    print(f"[BACKUP] Đã sao lưu file gốc tại: {backup_path}")

    prs = Presentation(pptx_path)

    # ==========================================================================
    # CẬP NHẬT SLIDE 1: TRANG BÌA (COVER)
    # ==========================================================================
    s1 = prs.slides[0]
    
    # Xóa sạch các shape nội dung từ index 1 trở đi (chỉ giữ shape 0 nền tối)
    shapes_to_remove = []
    for shape in list(s1.shapes)[1:]:
        shapes_to_remove.append(shape)
    
    for sh in shapes_to_remove:
        sp = sh._element
        sp.getparent().remove(sp)

    # Dải màu cyan viền bên trái
    add_card(s1, 0, 0, 0.35, 7.5, bg_color=CYAN_ACCENT, border_color=None)

    # 1. Khối thông tin Đơn vị Đào tạo
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

    # 2. Tiêu đề đề tài
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

    # 3. KHỐI THÔNG TIN NHÓM & DANH SÁCH THÀNH VIÊN KÈM MSSV
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

    # 4. 3 Khối Card dưới: ĐÚNG 3 DÒNG TÊN PART, KHÔNG GHI CHI TIẾT
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

    # Chân slide bìa
    tb_meta = s1.shapes.add_textbox(Inches(0.9), Inches(6.65), Inches(11.5), Inches(0.4))
    tf_m = tb_meta.text_frame
    p_m = tf_m.paragraphs[0]
    p_m.text = "HỌC KỲ II - NĂM HỌC 2025-2026  |  KHOA CÔNG NGHỆ THÔNG TIN  |  ĐẠI HỌC CÔNG THƯƠNG TP. HỒ CHÍ MINH (HUIT)"
    p_m.font.size = Pt(9)
    p_m.font.color.rgb = RGBColor(160, 185, 215)


    # ==========================================================================
    # CẬP NHẬT SLIDE 2: PART 1 - DEVICE (GIỮ NGUYÊN 100% 2 BẢNG BOM VÀ ~720K)
    # ==========================================================================
    s2 = prs.slides[1]
    # Chỉ cập nhật 2 khối trên (Shape 7 và Shape 9)
    tb_fw = s2.shapes[7]
    tf_fw = tb_fw.text_frame
    tf_fw.clear()
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

    tb_hw = s2.shapes[9]
    tf_hw = tb_hw.text_frame
    tf_hw.clear()
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

    # Table 12 và Table 14 được giữ nguyên vẹn 100%!


    # ==========================================================================
    # CẬP NHẬT SLIDE 3: PART 2 - MQTT SERVICES & QUY CHUẨN TOPIC PHÂN CẤP
    # ==========================================================================
    s3 = prs.slides[2]
    # Giữ lại shape 0 đến 5 (Header và Footer), xóa các shape nội dung cũ (shape 6 trở đi)
    shapes_s3_remove = []
    for shape in list(s3.shapes)[6:]:
        shapes_s3_remove.append(shape)
    for sh in shapes_s3_remove:
        sp = sh._element
        sp.getparent().remove(sp)

    # Cập nhật tiêu đề Slide 3 chuẩn mực
    s3.shapes[1].text_frame.paragraphs[0].text = "PART 2: MQTT SERVICES ON SERVER — KIẾN TRÚC MESSAGE BROKER & QUY CHUẨN TOPICS"
    s3.shapes[2].text_frame.paragraphs[0].text = "Cấu Trúc Phân Cấp Topics Chuẩn Hóa, Rationale Thiết Kế & 4 Dịch Vụ Cốt Lõi (Auth, Collect, Control, Keep-Alive)"

    # NỬA TRÊN: PHÂN TÍCH MA TRẬN TOPIC VÀ RATIONALE
    # 1. Bảng Ma Trận Topic MQTT Chuẩn Hóa (Bên Trái)
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

    # 2. Rationale: Tại Sao Xây Dựng Như Thế & Tác Dụng Gì? (Bên Phải)
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

    # NỬA DƯỚI: 4 KHỐI MICROSERVICES PHỤ TRÁCH TRỰC TIẾP
    card_w = 2.78
    gap_s = 0.20
    y_s = 3.82
    h_s = 3.12

    # 1. Auth Service
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
    # CẬP NHẬT SLIDE 4: PART 3 - WEB SERVER APP (4 TRỤ CỘT CÔ ĐỌNG)
    # ==========================================================================
    s4 = prs.slides[3]
    # Giữ lại shape 0 đến 5 (Header và Footer), xóa các shape nội dung cũ (shape 6 trở đi)
    shapes_s4_remove = []
    for shape in list(s4.shapes)[6:]:
        shapes_s4_remove.append(shape)
    for sh in shapes_s4_remove:
        sp = sh._element
        sp.getparent().remove(sp)

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

    # LƯU FILE TRỰC TIẾP VÀO FILE CHUẨN
    prs.save(pptx_path)
    print(f"[HOÀN TẤT 100%] Đã lưu trực tiếp file chuẩn tại: {pptx_path}")

    # ĐỒNG BỘ CẢ FILE PHỤ
    sub_path = r"e:\IoT\DoAn\docs\pptx\Bao_Cao_He_Thong_IoT_4_Slides_Nhom04.pptx"
    prs.save(sub_path)
    print(f"[ĐỒNG BỘ] Đã đồng bộ sang file: {sub_path}")

if __name__ == "__main__":
    update_presentation()
