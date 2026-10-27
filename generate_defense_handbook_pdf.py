# -*- coding: utf-8 -*-
"""
Script tạo file PDF Sổ Tay Thuyết Trình NoteSpeak & Cẩm Nang Hỏi Xoáy Đáp Xoay
Đề tài 04: Hệ thống Báo khói Cảnh báo sớm - Nhóm 04 (Lớp N09) HUIT
Sử dụng ReportLab với font Arial tiếng Việt đầy đủ thanh điệu, layout chuẩn in ấn A4.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

# ==============================================================================
# 1. ĐĂNG KÝ PHÔNG CHỮ TIẾNG VIỆT UNICODE (ARIAL)
# ==============================================================================
font_dir = "C:/Windows/Fonts"
pdfmetrics.registerFont(TTFont("ArialVN", os.path.join(font_dir, "arial.ttf")))
pdfmetrics.registerFont(TTFont("ArialVN-Bold", os.path.join(font_dir, "arialbd.ttf")))
pdfmetrics.registerFont(TTFont("ArialVN-Italic", os.path.join(font_dir, "ariali.ttf")))
pdfmetrics.registerFont(TTFont("ArialVN-BoldItalic", os.path.join(font_dir, "arialbi.ttf")))

pdfmetrics.registerFontFamily(
    "ArialVN",
    normal="ArialVN",
    bold="ArialVN-Bold",
    italic="ArialVN-Italic",
    boldItalic="ArialVN-BoldItalic"
)

# ==============================================================================
# 2. BẢNG MÀU THIẾT KẾ CHUYÊN NGHIỆP
# ==============================================================================
NAVY_DARK    = HexColor("#0F172A")
NAVY_PRIMARY = HexColor("#1A365D")
TECH_BLUE    = HexColor("#2563EB")
TECH_LIGHT   = HexColor("#EFF6FF")
SLATE_DARK   = HexColor("#1E293B")
SLATE_MUTED  = HexColor("#64748B")
BORDER_LIGHT = HexColor("#E2E8F0")
WARN_GOLD    = HexColor("#D97706")
WARN_LIGHT   = HexColor("#FFFBEB")
ALARM_RED    = HexColor("#DC2626")
ALARM_LIGHT  = HexColor("#FEF2F2")
SAFE_GREEN   = HexColor("#059669")
SAFE_LIGHT   = HexColor("#ECFDF5")

# ==============================================================================
# 3. CANVAS ĐÁNH SỐ TRANG TỰ ĐỘNG (PAGE X OF Y)
# ==============================================================================
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        if self._pageNumber == 1:
            return  # Không vẽ header/footer ở trang bìa

        self.saveState()
        self.setFont("ArialVN", 8)
        self.setFillColor(SLATE_MUTED)

        # Header chạy trên đầu trang
        self.drawString(36, 805, "IT4735 — Đề tài 04: Hệ Thống Báo Khói Cảnh Báo Sớm • Nhóm 04 (N09) HUIT")
        self.drawRightString(559, 805, "SỔ TAY BẢO VỆ ĐỒ ÁN IOT ĐIỂM 10")
        self.setStrokeColor(BORDER_LIGHT)
        self.setLineWidth(0.5)
        self.line(36, 798, 559, 798)

        # Footer ở đáy trang
        self.line(36, 45, 559, 45)
        self.drawString(36, 33, "Bản quyền nội dung: Nhóm 04 (Khang - Đức - Mãnh) • Bộ môn Mạng & ATTT")
        self.drawRightString(559, 33, f"Trang {self._pageNumber} / {total_pages}")
        self.restoreState()

# ==============================================================================
# 4. HÀM CHÍNH TẠO FILE PDF
# ==============================================================================
def generate_pdf(output_pdf_path, markdown_source_path):
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=48,
        bottomMargin=48
    )

    # Đọc nội dung file Markdown
    with open(markdown_source_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    styles = getSampleStyleSheet()

    # Tùy biến các ParagraphStyles
    style_cover_unit = ParagraphStyle(
        "CoverUnit", fontName="ArialVN-Bold", fontSize=11, leading=15,
        textColor=TECH_BLUE, alignment=TA_CENTER
    )
    style_cover_sub = ParagraphStyle(
        "CoverSub", fontName="ArialVN", fontSize=9.5, leading=13,
        textColor=SLATE_MUTED, alignment=TA_CENTER
    )
    style_cover_title = ParagraphStyle(
        "CoverTitle", fontName="ArialVN-Bold", fontSize=21, leading=26,
        textColor=NAVY_PRIMARY, alignment=TA_CENTER, spaceBefore=14, spaceAfter=8
    )
    style_cover_desc = ParagraphStyle(
        "CoverDesc", fontName="ArialVN", fontSize=10.5, leading=15,
        textColor=SLATE_DARK, alignment=TA_CENTER
    )
    style_h1 = ParagraphStyle(
        "ChapH1", fontName="ArialVN-Bold", fontSize=14, leading=18,
        textColor=NAVY_PRIMARY, spaceBefore=16, spaceAfter=8, keepWithNext=True
    )
    style_h2 = ParagraphStyle(
        "SecH2", fontName="ArialVN-Bold", fontSize=11.5, leading=15,
        textColor=TECH_BLUE, spaceBefore=12, spaceAfter=6, keepWithNext=True
    )
    style_h3 = ParagraphStyle(
        "SubH3", fontName="ArialVN-Bold", fontSize=10, leading=13,
        textColor=NAVY_PRIMARY, spaceBefore=8, spaceAfter=4, keepWithNext=True
    )
    style_body = ParagraphStyle(
        "BodyTextCustom", fontName="ArialVN", fontSize=8.8, leading=12.2,
        textColor=SLATE_DARK, alignment=TA_JUSTIFY, spaceAfter=4
    )
    style_bullet = ParagraphStyle(
        "BulletCustom", fontName="ArialVN", fontSize=8.8, leading=12.2,
        textColor=SLATE_DARK, spaceBefore=1.5, spaceAfter=1.5
    )
    style_speech = ParagraphStyle(
        "SpeechText", fontName="ArialVN-Italic", fontSize=8.8, leading=12.8,
        textColor=NAVY_PRIMARY, alignment=TA_JUSTIFY
    )
    style_q_title = ParagraphStyle(
        "QTitle", fontName="ArialVN-Bold", fontSize=9.5, leading=13,
        textColor=ALARM_RED, spaceBefore=8, spaceAfter=2, keepWithNext=True
    )
    style_q_intent = ParagraphStyle(
        "QIntent", fontName="ArialVN-Italic", fontSize=8.5, leading=11.5,
        textColor=WARN_GOLD, spaceAfter=3
    )

    story = []

    # --------------------------------------------------------------------------
    # TRANG BÌA (COVER PAGE)
    # --------------------------------------------------------------------------
    story.append(Spacer(1, 20))
    story.append(Paragraph("BỘ CÔNG THƯƠNG — ĐẠI HỌC CÔNG THƯƠNG TP. HỒ CHÍ MINH (HUIT)", style_cover_unit))
    story.append(Paragraph("KHOA CÔNG NGHỆ THÔNG TIN — BỘ MÔN MẠNG & AN TOÀN THÔNG TIN", style_cover_sub))
    story.append(Spacer(1, 25))

    story.append(HRFlowable(width="100%", thickness=3, color=TECH_BLUE, spaceBefore=5, spaceAfter=20))
    story.append(Paragraph("HỌC PHẦN: IT4735 — INTERNET OF THINGS (IoT) VÀ ỨNG DỤNG", style_cover_unit))
    story.append(Paragraph("SỔ TAY BẢO VỆ ĐỒ ÁN IOT ĐIỂM 10", ParagraphStyle("CoverBigBadge", fontName="ArialVN-Bold", fontSize=13, textColor=WARN_GOLD, alignment=TA_CENTER, spaceBefore=6)))
    story.append(Paragraph("KỊCH BẢN THUYẾT TRÌNH NOTESPEAK &amp; CẨM NANG &quot;HỎI XOÁY ĐÁP XOAY&quot;", style_cover_title))
    story.append(Paragraph("Đề tài 04: HỆ THỐNG BÁO KHÓI CẢNH BÁO SỚM (Smart Smoke &amp; Fire Early Warning System)", style_cover_desc))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_LIGHT, spaceBefore=20, spaceAfter=25))

    # Khối thông tin sinh viên
    team_data = [
        [Paragraph("<b>NHÓM THỰC HIỆN: NHÓM 04  |  LỚP HỌC PHẦN: N09</b>", ParagraphStyle("THead", fontName="ArialVN-Bold", fontSize=9.5, textColor=TECH_BLUE))],
        [Paragraph("• <b>Nguyễn Vĩnh Khang</b> (MSSV: 2001230381) — Trưởng nhóm: Firmware ESP32, FSM &amp; Tích Hợp", style_body)],
        [Paragraph("• <b>Nguyễn Văn Đức</b> (MSSV: 2001230186) — Thành viên: Thiết Kế Ma Trận Topic, Payload JSON &amp; Downlink", style_body)],
        [Paragraph("• <b>Nguyễn Văn Mãnh</b> (MSSV: 2001230503) — Thành viên: Khóa An Toàn Safety Guard &amp; Web Dashboard", style_body)],
    ]
    t_team = Table(team_data, colWidths=[520])
    t_team.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), TECH_LIGHT),
        ('BOX', (0,0), (-1,-1), 1.2, TECH_BLUE),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_team)
    story.append(Spacer(1, 30))

    # 3 Khối tóm tắt nội dung
    sum_data = [
        [
            Paragraph("<b>CHƯƠNG I: NOTESPEAK</b><br/>Kịch bản thuyết trình chuẩn mực 4–5 phút theo bộ 8 slides hoàn chỉnh, bao quát phần cứng, MQTT broker và Web SCADA.", style_body),
            Paragraph("<b>CHƯƠNG II: TỪ ĐIỂN 6 CHIỀU</b><br/>Mổ xẻ 38 linh kiện, vật tư ốc vít, giao thức, thuật toán theo 6 góc độ: Bản chất, Chức năng, Nguyên lý, Why this, Tương tác, Số liệu.", style_body),
            Paragraph("<b>CHƯƠNG III: BỘ 30 CÂU Q&amp;A</b><br/>Đáp án chuẩn điểm 10 cho 30 câu hỏi phản biện gắt gao nhất về Phần cứng, MQTT Broker và Web Server.", style_body)
        ]
    ]
    t_sum = Table(sum_data, colWidths=[168, 168, 168])
    t_sum.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 0.8, BORDER_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_sum)
    story.append(Spacer(1, 40))

    story.append(Paragraph("TP. HỒ CHÍ MINH — THÁNG 10 NĂM 2026", ParagraphStyle("CoverFoot", fontName="ArialVN-Bold", fontSize=9, textColor=SLATE_MUTED, alignment=TA_CENTER)))
    story.append(PageBreak())

    # --------------------------------------------------------------------------
    # TRANG 2: MỤC LỤC TỔNG QUAN & CHIẾN LƯỢC BẢO VỆ
    # --------------------------------------------------------------------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("MỤC LỤC TỔNG QUAN NỘI DUNG SỔ TAY", ParagraphStyle("TOCTitle", fontName="ArialVN-Bold", fontSize=15, leading=19, textColor=NAVY_PRIMARY, alignment=TA_CENTER)))
    story.append(Paragraph("Hệ thống hóa toàn bộ kiến thức thuyết trình 8 Slides, thuật ngữ chuyên ngành và bộ 30 câu hỏi phản biện", ParagraphStyle("TOCSub", fontName="ArialVN-Italic", fontSize=9, leading=13, textColor=SLATE_MUTED, alignment=TA_CENTER, spaceBefore=3, spaceAfter=8)))
    story.append(HRFlowable(width="100%", thickness=1.5, color=TECH_BLUE, spaceBefore=4, spaceAfter=12))

    toc_table_data = [
        [
            Paragraph("<b>CHƯƠNG / NỘI DUNG</b>", ParagraphStyle("TH1", fontName="ArialVN-Bold", fontSize=8.5, textColor=NAVY_PRIMARY)),
            Paragraph("<b>TRỌNG TÂM CHI TIẾT &amp; CÁC PHÂN MỤC</b>", ParagraphStyle("TH2", fontName="ArialVN-Bold", fontSize=8.5, textColor=NAVY_PRIMARY)),
            Paragraph("<b>ĐỊNH HƯỚNG</b>", ParagraphStyle("TH3", fontName="ArialVN-Bold", fontSize=8.5, textColor=NAVY_PRIMARY, alignment=TA_CENTER)),
        ],
        [
            Paragraph("<b>BẢNG TRA CỨU NHANH:<br/>THUẬT NGỮ, TỪ VIẾT TẮT,<br/>KÝ HIỆU &amp; NHÀ SẢN XUẤT</b>", ParagraphStyle("TC0", fontName="ArialVN-Bold", fontSize=8.0, leading=11, textColor=TECH_BLUE)),
            Paragraph("• <b>26 Từ viết tắt chuyên ngành:</b> SoC, SAR ADC, GPIO, FSM, FreeRTOS, WDT, EMA, SPIFFS, MQTT, QoS, LWT, SCADA, BLDC, IP54, PCB, FR4, HASL, EMI, NO/NC/COM, AWG, RTT, RBAC, PPM...<br/>"
                      "• <b>Ký hiệu vật lý &amp; Công thức:</b> R_s, R_0, R_H (31Ω), V_H (5V), P_H (900mW), cầu phân áp R1=10kΩ/R2=20kΩ hạ 5V->3.3V, V_iso (5000Vrms), alpha (0.2), V=-L·di/dt, dB, CFM, RPM.<br/>"
                      "• <b>Nhà sản xuất &amp; Tiêu chuẩn:</b> Espressif Systems, Hanwei, Aosong, Texas Instruments, Songle, Sharp, IEC 60529, DIN 934, UL94-V0.", style_body),
            Paragraph("<b>Cơ sở lý thuyết</b>", ParagraphStyle("TP0", fontName="ArialVN-Bold", fontSize=8, textColor=TECH_BLUE, alignment=TA_CENTER)),
        ],
        [
            Paragraph("<b>CHƯƠNG I:<br/>KỊCH BẢN THUYẾT TRÌNH (NOTESPEAK)<br/>4–5 PHÚT CHUẨN BỘ 8 SLIDES</b>", ParagraphStyle("TC1", fontName="ArialVN-Bold", fontSize=8.0, leading=11, textColor=TECH_BLUE)),
            Paragraph("• <b>Slide 1:</b> Trang Bìa &amp; Khái Quát Đề Tài (~30s)<br/>"
                      "• <b>Slide 2:</b> Part 1 - Thiết Kế Phần Cứng, Nguồn Datasheet &amp; FreeRTOS FSM (~40s)<br/>"
                      "• <b>Slide 3:</b> Part 1 - Bảng BOM Vật Tư Phần A (18 Linh Kiện Điện Tử) (~40s)<br/>"
                      "• <b>Slide 4:</b> Part 1 - Cơ Khí Lắp Ráp &amp; Bảng BOM Phần B (16 Hạng Mục Cơ Khí &amp; ~720k) (~35s)<br/>"
                      "• <b>Slide 5:</b> Part 2 - Dịch Vụ MQTT Trên Server &amp; Cây Topic Phân Cấp (~40s)<br/>"
                      "• <b>Slide 6:</b> Tích Hợp Hệ Thống - Luồng Dữ Liệu 2 Chiều &amp; Khóa An Toàn PCCC (~45s)<br/>"
                      "• <b>Slide 7:</b> Part 3 - Ứng Dụng Web Server: 4 Trụ Cột Nền Tảng (~40s)<br/>"
                      "• <b>Slide 8:</b> Kết Quả Thực Nghiệm - RTT Benchmark &amp; 16 Test Cases M4 (~40s)", style_body),
            Paragraph("<b>Bộ 8 Slides</b>", ParagraphStyle("TP1", fontName="ArialVN-Bold", fontSize=8, textColor=TECH_BLUE, alignment=TA_CENTER)),
        ],
        [
            Paragraph("<b>CHƯƠNG II:<br/>TỪ ĐIỂN BÁCH KHOA TOÀN THƯ<br/>MỔ XẺ 6 CHIỀU 38 KHÁI NIỆM &amp; LINH KIỆN</b><br/><font size=7 color='#64748B'><i>(Bản chất, Chức năng, Nguyên lý, Lý do chọn, Tương tác, Thông số)</i></font>", ParagraphStyle("TC2", fontName="ArialVN-Bold", fontSize=8.0, leading=11, textColor=TECH_BLUE)),
            Paragraph("• <b>Khối 1: Vi Điều Khiển &amp; Điều Khiển:</b> ESP32 DevKit V1, FreeRTOS Dual-Core, LM393 vi chỉnh, Relay Opto PC817, Active Buzzer 5V, LED Đỏ/Xanh 5mm, Trở hạn dòng 330Ω, Nút nhấn 12x12mm, Trở kéo Pull-up 10kΩ.<br/>"
                      "• <b>Khối 2: Cảm Biến Môi Trường:</b> MQ-2 (sấy 5V riêng, ngõ ra AOUT qua cầu phân áp 10k/20k), DHT22 (Single-Wire, NTC, dung dung).<br/>"
                      "• <b>Khối 3: Nguồn Công Suất &amp; Bảo Vệ:</b> Quạt hút BLDC 12V, Lưới thép 80mm, Adapter 12V 2A, Buck LM2596S (92%), Cầu chì 2A Fast-blow, Hộp đế PCB, Tụ hóa 100µF + Tụ gốm 100nF, Công tắc KCD11.<br/>"
                      "• <b>Khối 4: Đấu Nối, Vỏ Hộp &amp; Cơ Khí Ốc Vít:</b> Jack DC 5.5x2.1mm, Cọc KF301-2P/3P, Header cái 2.54mm, Dây silicon 22AWG, Dây Dupont, Gen co nhiệt, Vỏ ABS IP54, PCB FR4 1.6mm, Trụ đồng M3, Vít bake M3 Inox 304, Đệm Nylon, Bu-lông M4x35 quạt, Vít nở tắc kê phi 6, Gioăng cao su Grommet phi 12mm.<br/>"
                      "• <b>Khối 5: Truyền Thông &amp; SCADA:</b> MQTT 3.1.1, Namespace Nhom09, LWT, Lọc EMA (α=0.2), FSM Hysteresis, Safety Interlock Guard, RTT Benchmark &amp; 16 Test Cases M4.", style_body),
            Paragraph("<b>Kho kiến thức 100% BOM</b>", ParagraphStyle("TP2", fontName="ArialVN-Bold", fontSize=8, textColor=TECH_BLUE, alignment=TA_CENTER)),
        ],
        [
            Paragraph("<b>CHƯƠNG III:<br/>BỘ 30 CÂU HỎI &quot;HỎI XOÁY ĐÁP XOAY&quot;<br/>VÀ ĐÁP ÁN CHUẨN ĐIỂM 10</b><br/><font size=7 color='#64748B'><i>(Phân tích ý đồ bẫy &amp; câu trả lời chuẩn xác)</i></font>", ParagraphStyle("TC3", fontName="ArialVN-Bold", fontSize=8.0, leading=11, textColor=TECH_BLUE)),
            Paragraph("• <b>Phần A (Câu 1–10):</b> 10 câu hỏi hóc búa về Phần Cứng &amp; Điện Tử Nguồn (LM2596 vs 7805, sấy MQ-2 5V, cầu phân áp 10k/20k, ADC nhiễu, FreeRTOS Watchdog, Cầu H...).<br/>"
                      "• <b>Phần B (Câu 11–20):</b> 10 câu hỏi hóc búa về Mạng, MQTT &amp; Bảo Mật (Nghẽn Broker, QoS 0 vs QoS 1, Keep Alive, Topic ACL, LWT, Wi-Fi rớt...).<br/>"
                      "• <b>Phần C (Câu 21–30):</b> 10 câu hỏi hóc búa về Thuật Toán &amp; Web SCADA (Độ trễ EMA, FSM Deadband, Khóa Safety Interlock, WebSocket vs HTTP, RTT 115ms, 16 Test Cases M4...).", style_body),
            Paragraph("<b>Vấn đáp điểm 10</b>", ParagraphStyle("TP3", fontName="ArialVN-Bold", fontSize=8, textColor=TECH_BLUE, alignment=TA_CENTER)),
        ],
    ]
    t_toc = Table(toc_table_data, colWidths=[140, 305, 75])
    t_toc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 5),
        ('BACKGROUND', (0,1), (-1,1), HexColor("#F8FAFC")),
        ('BACKGROUND', (0,2), (-1,2), HexColor("#FFFFFF")),
        ('BACKGROUND', (0,3), (-1,3), HexColor("#F8FAFC")),
        ('BACKGROUND', (0,4), (-1,4), HexColor("#FFFFFF")),
    ]))
    story.append(t_toc)
    story.append(Spacer(1, 10))

    # Khối chiến lược vấn đáp
    strategy_data = [
        [
            Paragraph("<b>4 NGUYÊN TẮC VÀNG KHI ĐỐI ĐÁP PHẢN BIỆN TRƯỚC HỘI ĐỒNG:</b>", ParagraphStyle("StratHead", fontName="ArialVN-Bold", fontSize=8.5, textColor=NAVY_PRIMARY)),
        ],
        [
            Paragraph(
                "1. <b>Bình tĩnh &amp; Lắng nghe trọn vẹn:</b> Không ngắt lời Thầy/Cô. Dành 2 giây xác nhận lại bản chất câu hỏi trước khi trả lời.<br/>"
                "2. <b>Đi thẳng vào nguyên lý cốt lõi:</b> Áp dụng cấu trúc 6 chiều (Bản chất → Nguyên lý → Vì sao chọn giải pháp này thay vì giải pháp khác).<br/>"
                "3. <b>Chứng minh bằng số liệu đo đạc thực tế:</b> Nêu rõ thông số kiểm thử (độ trễ phản hồi &lt;50ms, sai số EMA &plusmn;3%, dòng tiêu thụ đỉnh 250mA).<br/>"
                "4. <b>Phối hợp ăn ý giữa 3 thành viên:</b> Phân định rõ phạm vi trách nhiệm (Firmware / MQTT / Web &amp; Safety Guard) nhưng luôn chủ động bọc lót đồng đội.",
                style_body
            )
        ]
    ]
    t_strat = Table(strategy_data, colWidths=[520])
    t_strat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), HexColor("#FEF3C7")),
        ('BOX', (0,0), (-1,-1), 1, WARN_GOLD),
        ('PADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_strat)

    # --------------------------------------------------------------------------
    # CHUYỂN ĐỔI NỘI DUNG MARKDOWN SANG REPORTLAB FLOWABLES
    # --------------------------------------------------------------------------
    lines = md_text.split("\n")
    i = 0
    in_speech_box = False
    speech_buffer = []

    def clean_text_formatting(txt):
        txt = txt.replace("&", "&amp;")
        # Công thức toán học và ký hiệu
        txt = re.sub(r'\$\\Delta V\s*=\s*12\\text\{V\}\s*-\s*5\\text\{V\}\s*=\s*7\\text\{V\}\$', 'ΔV = 12V - 5V = 7V', txt)
        txt = re.sub(r'\$P\s*=\s*7\\text\{V\}\s*\\times\s*0\.5\\text\{A\}\s*=\s*3\.5\\text\{W\}\$', 'P = 7V × 0.5A = 3.5W', txt)
        txt = re.sub(r'\$P_\{in\}\s*\\approx\s*P_\{out\}\$', 'Pin ≈ Pout', txt)
        txt = re.sub(r'\$V\s*=\s*-L\s*\\cdot\s*di/dt\$', 'V = -L × (di/dt)', txt)
        txt = re.sub(r'\$di/dt\$', 'di/dt', txt)
        txt = re.sub(r'\$L\$', 'L', txt)
        txt = re.sub(r'\$\\ge\$', '≥', txt)
        txt = re.sub(r'\$\\le\$', '≤', txt)
        txt = re.sub(r'\$\\pm\$', '±', txt)
        txt = re.sub(r'\$([^$]+)\$', r'<i>\1</i>', txt)
        
        # Markdown formatting
        txt = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', txt)
        txt = re.sub(r'\*(.*?)\*', r'<i>\1</i>', txt)
        txt = re.sub(r'`(.*?)`', r'<font color="#2563EB"><b>\1</b></font>', txt)

        # Dọn dẹp dấu nháy kép bọc asterisk còn sót lại
        txt = re.sub(r':\s*\*"', ': "', txt)
        txt = re.sub(r'^\*\"', '"', txt)
        txt = re.sub(r'\"\*$', '"', txt)
        txt = re.sub(r'\"\*\s*$', '"', txt)
        txt = re.sub(r'^\*', '', txt)
        txt = re.sub(r'\*$', '', txt)
        return txt

    def flush_speech_box():
        nonlocal speech_buffer
        if speech_buffer:
            txt = " ".join(speech_buffer)
            clean_txt = clean_text_formatting(txt)
            box_data = [[
                Paragraph("<b>LỜI THOẠI THUYẾT TRÌNH (NOTESPEAK):</b>", ParagraphStyle("SpkHead", fontName="ArialVN-Bold", fontSize=8.5, textColor=NAVY_PRIMARY)),
            ], [
                Paragraph(clean_txt, style_speech)
            ]]
            t_box = Table(box_data, colWidths=[520])
            t_box.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), TECH_LIGHT),
                ('BOX', (0,0), (-1,-1), 1, TECH_BLUE),
                ('PADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,0), 4),
                ('BOTTOMPADDING', (0,-1), (-1,-1), 6),
            ]))
            story.append(t_box)
            story.append(Spacer(1, 6))
            speech_buffer = []

    # Nhảy qua phần đầu markdown đến tận trước "# CHƯƠNG I"
    has_reached_ch1 = False
    while i < len(lines):
        line = lines[i].strip()
        if not has_reached_ch1:
            if line.startswith("# CHƯƠNG I"):
                has_reached_ch1 = True
            else:
                i += 1
                continue

        # Xử lý khối lời thoại NoteSpeak ">"
        if line.startswith(">"):
            content = line.lstrip("> ").strip()
            speech_buffer.append(content)
            i += 1
            continue
        else:
            if speech_buffer:
                flush_speech_box()

        if not line:
            i += 1
            continue

        # Tiêu đề Chương (H1)
        if line.startswith("# CHƯƠNG"):
            story.append(PageBreak())
            story.append(HRFlowable(width="100%", thickness=2, color=TECH_BLUE, spaceBefore=4, spaceAfter=8))
            story.append(Paragraph(line.lstrip("# ").replace("&", "&amp;"), style_h1))
            story.append(HRFlowable(width="100%", thickness=0.8, color=BORDER_LIGHT, spaceBefore=2, spaceAfter=10))
            i += 1
            continue

        # Tiêu đề Nhóm / Phần (H2)
        if line.startswith("## "):
            story.append(Spacer(1, 6))
            story.append(Paragraph(line.lstrip("# ").replace("&", "&amp;"), style_h2))
            i += 1
            continue

        # Tiêu đề Mục con (H3)
        if line.startswith("### "):
            txt = clean_text_formatting(line.lstrip("# "))
            story.append(Spacer(1, 4))
            story.append(Paragraph(txt, style_h3))
            i += 1
            continue

        # Câu hỏi phản biện H4
        if line.startswith("#### Câu "):
            q_txt = clean_text_formatting(line.lstrip("# "))
            story.append(Spacer(1, 6))
            story.append(Paragraph(q_txt, style_q_title))
            i += 1
            continue

        # Ý đồ của giảng viên
        if line.startswith("- **Ý đồ của giảng viên:**"):
            intent_content = line.replace("- **Ý đồ của giảng viên:**", "").strip()
            intent_txt = "<b>• Ý đồ bắt bẻ của Hội đồng:</b> " + clean_text_formatting(intent_content)
            story.append(Paragraph(intent_txt, style_q_intent))
            i += 1
            continue

        # Đáp án chuẩn điểm 10
        if line.startswith("- **Đáp án chuẩn điểm 10:**"):
            ans_lead = "<b>• Đáp án chuẩn điểm 10:</b>"
            story.append(Paragraph(ans_lead, ParagraphStyle("AnsHead", fontName="ArialVN-Bold", fontSize=9, textColor=SAFE_GREEN, spaceBefore=3, spaceAfter=2)))
            i += 1
            continue

        # Xử lý Markdown Table (Bắt đầu bằng |)
        if line.startswith("|"):
            tbl_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl_lines.append(lines[i].strip())
                i += 1
            tbl_data = []
            for r_idx, r_line in enumerate(tbl_lines):
                if all(c in ' :-|' for c in r_line.strip()):
                    continue
                cells = [c.strip() for c in r_line.strip('|').split('|')]
                row_cells = []
                for cell in cells:
                    cell_clean = clean_text_formatting(cell)
                    if r_idx == 0:
                        row_cells.append(Paragraph(f"<b>{cell_clean}</b>", ParagraphStyle("THCell", fontName="ArialVN-Bold", fontSize=7.5, leading=10, textColor=NAVY_PRIMARY)))
                    else:
                        row_cells.append(Paragraph(cell_clean, ParagraphStyle("TBCell", fontName="ArialVN", fontSize=7.2, leading=9.5, textColor=SLATE_DARK)))
                tbl_data.append(row_cells)
            if tbl_data:
                col_cnt = len(tbl_data[0])
                if col_cnt == 3:
                    col_widths = [105, 145, 270]
                elif col_cnt == 4:
                    col_widths = [110, 110, 140, 160]
                else:
                    col_widths = [520 / col_cnt] * col_cnt
                t_render = Table(tbl_data, colWidths=col_widths)
                t_render.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), HexColor("#E2E8F0")),
                    ('GRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
                    ('PADDING', (0,0), (-1,-1), 4),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ]))
                story.append(Spacer(1, 4))
                story.append(t_render)
                story.append(Spacer(1, 6))
            continue

        # Dòng bullet thông thường
        if line.startswith("- ") or line.startswith("• "):
            b_txt = clean_text_formatting(line.lstrip("- •").strip())
            story.append(Paragraph(f"• {b_txt}", style_bullet))
            i += 1
            continue

        # Dòng phân cách HR
        if line.startswith("---"):
            story.append(Spacer(1, 4))
            story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_LIGHT, spaceBefore=4, spaceAfter=6))
            i += 1
            continue

        # Khối code / mermaid / công thức
        if line.startswith("```"):
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # bỏ qua dòng đóng ```
            raw_code = "\n".join(code_lines).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            code_data = [[Paragraph(f"<font face='ArialVN' size=7.5 color='#1E293B'><pre>{raw_code}</pre></font>", style_body)]]
            t_code = Table(code_data, colWidths=[520])
            t_code.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), HexColor("#F1F5F9")),
                ('BOX', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
                ('PADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(t_code)
            story.append(Spacer(1, 4))
            continue

        # Văn bản thông thường
        p_txt = clean_text_formatting(line)
        story.append(Paragraph(p_txt, style_body))
        i += 1

    if speech_buffer:
        flush_speech_box()

    # Biên dịch tài liệu PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[THÀNH CÔNG] Đã tạo file PDF Sổ tay tại: {output_pdf_path}")

if __name__ == "__main__":
    out_pdf = r"e:\IoT\DoAn\docs\pdf\So_Tay_Thuyet_Trinh_Va_Hoi_Xoay_Dap_Xoay.pdf"
    src_md  = r"e:\IoT\DoAn\docs\pdf\So_Tay_Thuyet_Trinh_Va_Hoi_Xoay_Dap_Xoay.md"
    generate_pdf(out_pdf, src_md)
