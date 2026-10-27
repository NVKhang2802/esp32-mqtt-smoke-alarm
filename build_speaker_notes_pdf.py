# -*- coding: utf-8 -*-
"""
Script to generate the complete Presentation Assignment & Speaker Notes PDF
for Week 4: "Hệ Thống Báo Khói Cảnh Báo Sớm" - Nhóm 04
Output: docs/pdf/KeHoach_PhanCong_ThuyetTrinh_Va_SpeakerNotes_Tuan4_Nhom04.pdf
"""

import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# ------------------------------------------------------------------------------
# 1. REGISTER FONTS
# ------------------------------------------------------------------------------
font_regular = r'C:\Windows\Fonts\arial.ttf'
font_bold    = r'C:\Windows\Fonts\arialbd.ttf'
font_italic  = r'C:\Windows\Fonts\ariali.ttf'
font_bolditalic = r'C:\Windows\Fonts\arialbi.ttf'

pdfmetrics.registerFont(TTFont('Arial', font_regular))
pdfmetrics.registerFont(TTFont('Arial-Bold', font_bold))
pdfmetrics.registerFont(TTFont('Arial-Italic', font_italic))
pdfmetrics.registerFont(TTFont('Arial-BoldItalic', font_bolditalic))

# ------------------------------------------------------------------------------
# 2. NUMBERED CANVAS FOR HEADER & FOOTER
# ------------------------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Arial", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(40, 805, 555, 805)
            self.drawString(40, 810, "BÁO CÁO TUẦN 4: TẦNG 2 NETWORK (MQTT) — NHÓM 04 — HỆ THỐNG BÁO KHÓI")
            self.drawRightString(555, 810, "MILESTONE M2 (10%)")

        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(40, 38, 555, 38)
        self.drawString(40, 26, "Trường ĐH Công Thương TP.HCM • Khoa CNTT • Kế hoạch Thuyết trình & Speaker Notes")
        self.drawRightString(555, 26, f"Trang {self._pageNumber} / {page_count}")
        self.restoreState()

# ------------------------------------------------------------------------------
# 3. BUILD PDF DOCUMENT
# ------------------------------------------------------------------------------
def build_pdf():
    pdf_dir = r"E:\IoT\DoAn\docs\pdf"
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, "KeHoach_PhanCong_ThuyetTrinh_Va_SpeakerNotes_Tuan4_Nhom04.pdf")

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=48,
        bottomMargin=48
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#1F4E79"),
        alignment=1, # Center
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#2E75B6"),
        alignment=1,
        spaceAfter=10
    )
    meta_style = ParagraphStyle(
        'MetaText',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
        alignment=1
    )
    h1_style = ParagraphStyle(
        'Heading1Custom',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1F4E79"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#2E75B6"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=4
    )
    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E293B"),
        leftIndent=12,
        spaceAfter=3
    )
    speaker_box_style = ParagraphStyle(
        'SpeakerBoxText',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor("#0F172A")
    )
    cue_style = ParagraphStyle(
        'CueStyle',
        parent=styles['Normal'],
        fontName='Arial-BoldItalic',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#B91C1C")
    )
    table_header_style = ParagraphStyle(
        'TblHdr',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1
    )
    table_cell_style = ParagraphStyle(
        'TblCell',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1E293B")
    )
    table_cell_bold = ParagraphStyle(
        'TblCellBold',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1F4E79")
    )
    table_cell_center = ParagraphStyle(
        'TblCellCenter',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=8,
        leading=11,
        alignment=1,
        textColor=colors.HexColor("#1E293B")
    )

    story = []

    # --------------------------------------------------------------------------
    # HEADER BANNER
    # --------------------------------------------------------------------------
    banner_p1 = Paragraph("BỘ CÔNG THƯƠNG — TRƯỜNG ĐẠI HỌC CÔNG THƯƠNG TP. HỒ CHÍ MINH (HUIT)", meta_style)
    banner_p2 = Paragraph("KHOA CÔNG NGHỆ THÔNG TIN — BỘ MÔN MẠNG & AN TOÀN THÔNG TIN", meta_style)
    story.append(banner_p1)
    story.append(banner_p2)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1F4E79"), spaceAfter=10))

    story.append(Paragraph("KẾ HOẠCH PHÂN CÔNG THUYẾT TRÌNH & KỊCH BẢN CHI TIẾT (SPEAKER NOTES)", title_style))
    story.append(Paragraph("ĐỀ TÀI: HỆ THỐNG BÁO KHÓI CẢNH BÁO SỚM — BÁO CÁO TIẾN ĐỘ TUẦN 4 (TẦNG 2 MQTT)", subtitle_style))
    
    info_text = (
        "<b>Giảng viên hướng dẫn:</b> ThS. Võ Hoàng Hải &nbsp;|&nbsp; "
        "<b>Nhóm thực hiện:</b> Nhóm 04 (Lớp ĐH IoT) &nbsp;|&nbsp; "
        "<b>Nghiệm thu:</b> Milestone M2 (10%)<br/>"
        "<b>Thời gian báo cáo:</b> 15 phút trình bày (5 phút/thành viên) + 5 phút phản biện Q&A"
    )
    story.append(Paragraph(info_text, meta_style))
    story.append(Spacer(1, 10))

    # --------------------------------------------------------------------------
    # MỤC 1: BẢNG PHÂN CÔNG TỔNG QUAN
    # --------------------------------------------------------------------------
    story.append(Paragraph("1. NGUYÊN TẮC PHÂN CHIA & BẢNG PHÂN CÔNG THUYẾT TRÌNH LIỀN MẠCH", h1_style))
    story.append(Paragraph(
        "Nhằm đảm bảo buổi báo cáo trước Hội đồng diễn ra chuyên nghiệp, trang trọng và logic, "
        "nhóm áp dụng nguyên tắc <b>'Mỗi thành viên lên thuyết trình đúng 1 lần duy nhất, liền mạch 4 slide liên tiếp'</b> "
        "(tỷ lệ 4 – 4 – 4). Khi kết thúc phần của mình, người nói sẽ dùng câu chuyển tiếp tự nhiên (Handover Transition Cue) "
        "để mời thành viên tiếp theo, loại bỏ hoàn toàn tình trạng đổi người nói lộn xộn hoặc ngắt quãng.",
        body_style
    ))
    story.append(Spacer(1, 6))

    # Table of Assignment
    tbl_data = [
        [
            Paragraph("STT & Thành viên", table_header_style),
            Paragraph("Vai trò kỹ thuật", table_header_style),
            Paragraph("Phạm vi Slide", table_header_style),
            Paragraph("Nội dung báo cáo trọng tâm", table_header_style),
            Paragraph("Thời lượng", table_header_style)
        ],
        [
            Paragraph("<b>1. Nguyễn Vĩnh Khang</b><br/>MSSV: 2001230381<br/><i>(Lên đầu tiên)</i>", table_cell_style),
            Paragraph("Trưởng nhóm<br/>Firmware & WiFi/MQTT", table_cell_center),
            Paragraph("<b>Slide 01 → 04</b><br/>(4 slide)", table_cell_center),
            Paragraph("• Mở đầu, giới thiệu nhóm, giảng viên & đề tài.<br/>• Mục tiêu Tuần 4 & Phân bổ 18h kỹ thuật.<br/>• Kiến trúc mạng Tầng 2 & Mô hình MQTT Pub/Sub.<br/>• Cơ chế Chúc thư LWT (smoke/lwt) giám sát thiết bị.", table_cell_style),
            Paragraph("5 phút<br/>(0:00 - 5:00)", table_cell_center)
        ],
        [
            Paragraph("<b>2. Nguyễn Văn Đức</b><br/>MSSV: 2001230186<br/><i>(Lên thứ hai)</i>", table_cell_style),
            Paragraph("Thành viên<br/>Topic Tree & JSON", table_cell_center),
            Paragraph("<b>Slide 05 → 08</b><br/>(4 slide)", table_cell_center),
            Paragraph("• Sơ đồ Cây Topic MQTT 6 nhánh ngữ nghĩa.<br/>• Cấu trúc JSON Telemetry định kỳ & Alarm tức thời.<br/>• Luồng Downlink điều khiển Quạt & Mute Còi 180s.<br/>• Ma trận an toàn PCCC (Local Safety Interlock).", table_cell_style),
            Paragraph("5 phút<br/>(5:00 - 10:00)", table_cell_center)
        ],
        [
            Paragraph("<b>3. Nguyễn Văn Mãnh</b><br/>MSSV: 2001230503<br/><i>(Lên thứ ba)</i>", table_cell_style),
            Paragraph("Thành viên<br/>Testing & Reconnect", table_cell_center),
            Paragraph("<b>Slide 09 → 12</b><br/>(4 slide)", table_cell_center),
            Paragraph("• Kỹ thuật Non-blocking Reconnect bằng <code>millis()</code>.<br/>• Kết quả 12/12 Test Case chuẩn (100% Pass).<br/>• 5 Minh chứng thực nghiệm Wokwi & MQTTX.<br/>• Nghiệm thu M2, Kế hoạch Tuần 5 & Mở Q&A.", table_cell_style),
            Paragraph("5 phút<br/>(10:00 - 15:00)", table_cell_center)
        ]
    ]

    t_assign = Table(tbl_data, colWidths=[110, 85, 75, 195, 50])
    t_assign.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_assign)
    story.append(Spacer(1, 12))

    # --------------------------------------------------------------------------
    # MỤC 2: KỊCH BẢN THUYẾT TRÌNH CHI TIẾT THEO TỪNG THÀNH VIÊN
    # --------------------------------------------------------------------------
    story.append(Paragraph("2. KỊCH BẢN THUYẾT TRÌNH CHI TIẾT (SPEAKER NOTES THEO TỪNG SLIDE)", h1_style))
    story.append(Spacer(1, 4))

    # Helper function to render a slide block in PDF
    def add_slide_script(slide_num, title, speaker, bullets_summary, script_text, transition_cue=None):
        content = []
        # Header bar of slide block
        hdr_p = Paragraph(f"<b>SLIDE {slide_num:02d}: {title.upper()}</b> &nbsp;&nbsp;|&nbsp;&nbsp; Người nói: <b>{speaker}</b>", ParagraphStyle(
            'SlideHdr', parent=styles['Normal'], fontName='Arial-Bold', fontSize=9.5, textColor=colors.HexColor("#1F4E79")
        ))
        content.append(hdr_p)
        content.append(Spacer(1, 3))
        
        # Summary bullets
        sum_p = Paragraph(f"<b>Điểm cốt lõi trên slide:</b> {bullets_summary}", ParagraphStyle(
            'SummP', parent=styles['Normal'], fontName='Arial', fontSize=8.5, leading=11.5, textColor=colors.HexColor("#475569")
        ))
        content.append(sum_p)
        content.append(Spacer(1, 4))

        # Script Box
        box_data = [[
            Paragraph(f"<b>Lời dẫn nói thực tế:</b><br/>{script_text}", speaker_box_style)
        ]]
        t_box = Table(box_data, colWidths=[515])
        t_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
            ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor("#94A3B8")),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        content.append(t_box)

        if transition_cue:
            content.append(Spacer(1, 4))
            cue_p = Paragraph(f"👉 <b>CÂU NỐI CHUYỂN BÀN GIAO:</b> <i>\"{transition_cue}\"</i>", cue_style)
            content.append(cue_p)

        content.append(Spacer(1, 10))
        return KeepTogether(content)

    # --------------------------------------------------------------------------
    # THÀNH VIÊN 1: NGUYỄN VĨNH KHANG
    # --------------------------------------------------------------------------
    story.append(Paragraph("PHẦN 1: NGUYỄN VĨNH KHANG (Trưởng nhóm — Slide 01 đến 04)", h2_style))
    story.append(Paragraph("<i>Thời gian trình bày: 5 phút (0:00 – 5:00) • Mục tiêu: Tạo ấn tượng đầu trang trọng, làm rõ mục tiêu tuần và thiết lập kiến trúc truyền thông tổng thể.</i>", body_style))
    story.append(Spacer(1, 4))

    # Slide 1
    story.append(add_slide_script(
        1, "Bìa Đề tài & Giới thiệu Nhóm", "Nguyễn Vĩnh Khang",
        "Tên đề tài 'Hệ thống Báo Khói Cảnh Báo Sớm'; Báo cáo Tuần 4 (Tầng 2 MQTT); Milestone M2 (10%); Thông tin GVHD ThS. Võ Hoàng Hải và 3 thành viên.",
        "\"Kính chào Thầy Võ Hoàng Hải và các bạn sinh viên tham dự buổi báo cáo tiến độ đồ án IoT hôm nay! "
        "Em là Nguyễn Vĩnh Khang, đại diện cho Nhóm 04 gồm ba thành viên: em, bạn Nguyễn Văn Đức và bạn Nguyễn Văn Mãnh. "
        "Hôm nay, nhóm em rất vinh dự được trình bày báo cáo kỹ thuật Tuần 4 với chủ đề: 'Thiết kế và triển khai Tầng 2 – Network / Connectivity qua giao thức MQTT' "
        "nhằm nghiệm thu Milestone M2: Connected Device chiếm 10% tổng điểm đồ án.<br/><br/>"
        "Nếu như ở Milestone M1, hệ thống của nhóm em mới chỉ là một thiết bị đo cục bộ độc lập, thì trong Tuần 4 này, "
        "toàn bộ trạm cảm biến ESP32 đã được hòa mạng Internet, có khả năng truyền nhận dữ liệu hai chiều thời gian thực với độ trễ cực thấp và đảm bảo an toàn PCCC tuyệt đối. "
        "Sau đây, em xin phép bắt đầu phần trình bày về mục tiêu và phân bổ nguồn lực của nhóm!\""
    ))

    # Slide 2
    story.append(add_slide_script(
        2, "Mục tiêu Tuần 4 & Phân bổ 18h Kỹ thuật", "Nguyễn Vĩnh Khang",
        "4 Mục tiêu Tầng 2 (WiFi, MQTT, Hai chiều, An toàn biên/Reconnect); Khung phân bổ 18 giờ kỹ thuật (H1-H2, H3-H4, H5-H6); Chuyển đổi thành Connected Device.",
        "\"Thưa Thầy và các bạn, ở slide thứ 2, em xin trình bày về mục tiêu trọng tâm của Tuần 4 và phương án phân bổ 18 giờ làm việc kỹ thuật của nhóm.<br/><br/>"
        "Theo đề cương chi tiết môn học, mỗi sinh viên phải dành ít nhất 6 giờ học tập và làm việc độc lập mỗi tuần. Với nhóm 3 người, chúng em có tổng cộng 18 giờ kỹ thuật được chia thành 3 khung thời gian chuẩn hóa:<br/>"
        "• Khung H1-H2 (6 giờ nhóm): Cả 3 thành viên cùng phân tích yêu cầu, khảo sát các Broker như HiveMQ và EMQX, quy hoạch cây định danh Topic Tree và thiết kế cấu trúc JSON.<br/>"
        "• Khung H3-H4 (6 giờ nhóm): Nhóm bắt tay vào lập trình Firmware cho ESP32, xây dựng luồng Uplink đẩy dữ liệu cảm biến định kỳ mỗi 2 giây và gói tin cảnh báo khẩn cấp hướng sự kiện.<br/>"
        "• Khung H5-H6 (6 giờ nhóm): Triển khai luồng nhận lệnh Downlink, xây dựng Ma trận an toàn PCCC để chặn lệnh nguy hiểm, lập trình cơ chế Reconnect tự phục hồi và thực thi đo kiểm toàn bộ 12 Test Cases.<br/><br/>"
        "Kết quả đạt được giúp nhóm hoàn thành 100% tiêu chí nghiệm thu của Milestone M2, chuyển dịch từ thiết bị độc lập sang Connected Smart Device.\""
    ))

    # Slide 3
    story.append(add_slide_script(
        3, "Kiến trúc Truyền thông Tầng 2 & Mô hình MQTT Pub/Sub", "Nguyễn Vĩnh Khang",
        "Mô hình 3 khối (Edge ESP32, Broker EMQX 1883, Clients/Middleware); Sơ đồ dòng dữ liệu; 5 Ưu điểm vượt trội của MQTT đối với IoT PCCC.",
        "\"Kính thưa Thầy, chuyển sang Slide 3, em xin giải thích về kiến trúc truyền thông Tầng 2 và lý do nhóm lựa chọn mô hình MQTT Publish/Subscribe.<br/><br/>"
        "Hệ thống của nhóm được xây dựng trên mô hình 3 thành phần rõ rệt:<br/>"
        "1. Thiết bị biên (Edge Device): Là kit vi điều khiển ESP32 đảm nhận vai trò kép — vừa là Publisher đẩy dữ liệu cảm biến và cảnh báo, vừa là Subscriber đón nhận các lệnh điều khiển từ người dùng.<br/>"
        "2. Máy chủ trung gian (MQTT Broker): Nhóm sử dụng cụm Broker công cộng broker.emqx.io trên cổng TCP chuẩn 1883, hoàn toàn tương thích và không bị chặn khi chạy mô phỏng mạng ảo trên Wokwi. Chu kỳ Keep-Alive được thiết lập là 60 giây.<br/>"
        "3. Các ứng dụng đầu cuối: Hiện tại nhóm sử dụng công cụ chuyên dụng MQTTX để giám sát và gửi lệnh; sang Tuần 5 sẽ kết nối trực tiếp với Node-RED và Telegram Bot.<br/><br/>"
        "Lý do cốt lõi nhóm chọn MQTT thay vì HTTP truyền thống là bởi vì MQTT sử dụng cơ chế Push hướng sự kiện với Header chỉ vỏn vẹn từ 2 bytes, tách rời hoàn toàn không gian và thời gian giữa các bên. "
        "Đặc biệt trong bài toán PCCC, khi phát hiện nồng độ khói vượt ngưỡng, ESP32 chỉ mất chưa tới 65 mili-giây để đẩy bản tin báo động đến toàn bộ người dùng, nhanh hơn rất nhiều so với cơ chế Polling vòng lặp của HTTP!\""
    ))

    # Slide 4
    story.append(add_slide_script(
        4, "Cơ chế Chúc thư LWT (Last Will & Testament) tại smoke/lwt", "Nguyễn Vĩnh Khang",
        "Bài toán 'Làm sao biết cảm biến khói còn sống hay đã mất mạng?'; 3 Bước vòng đời LWT (Đăng ký Connect, Graceful Online, Ungraceful Trigger); Tầm quan trọng đối với PCCC.",
        "\"Thưa Thầy và các bạn, đây là một điểm kỹ thuật cực kỳ quan trọng mà Nhóm 04 đã thiết kế riêng cho bài toán An toàn phòng cháy chữa cháy: Cơ chế Chúc thư LWT (Last Will and Testament) tại topic smoke/lwt.<br/><br/>"
        "Trong thực tế PCCC, việc thiết bị đo khói bị mất nguồn, chập cháy đường dây tín hiệu hoặc mất sóng WiFi là nguy cơ tử huyệt. "
        "Nếu thiết bị âm thầm ngắt kết nối mà phần mềm máy chủ không biết, đám cháy bùng lên sẽ hoàn toàn không có ai ứng cứu!<br/><br/>"
        "Cơ chế LWT giải quyết triệt để vấn đề này theo 3 bước mạch lạc:<br/>"
        "• Bước 1: Ngay từ lúc gửi gói CONNECT bắt tay Broker, ESP32 'gửi gắm' một thông điệp chúc thư ghi rõ: 'status: offline' với cờ Retain=true và QoS=1.<br/>"
        "• Bước 2: Khi bắt tay thành công, ESP32 chủ động bắn đè lên topic này thông điệp 'status: online' để thông báo hệ thống đang hoạt động tốt.<br/>"
        "• Bước 3: Nếu xảy ra sự cố đột ngột (Ungraceful Disconnect) khiến ESP32 sập nguồn hoặc mất kết nối quá thời gian Keep-Alive (~22.5s), chính Broker trung gian sẽ tự động kích hoạt bức chúc thư này và gửi cảnh báo khẩn cấp đến Dashboard của người quản trị và Telegram Bot!\"",
        "Và để đi sâu vào chi tiết cách quy hoạch Topic và cấu trúc gói tin JSON của hệ sinh thái này, sau đây em xin kính mời bạn Nguyễn Văn Đức tiếp tục phần trình bày của nhóm!"
    ))

    # --------------------------------------------------------------------------
    # THÀNH VIÊN 2: NGUYỄN VĂN ĐỨC
    # --------------------------------------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph("PHẦN 2: NGUYỄN VĂN ĐỨC (Thành viên — Slide 05 đến 08)", h2_style))
    story.append(Paragraph("<i>Thời gian trình bày: 5 phút (5:00 – 10:00) • Mục tiêu: Thể hiện tính chuẩn hóa dữ liệu JSON, giao thức điều khiển 2 chiều và chiều sâu bảo vệ an toàn PCCC.</i>", body_style))
    story.append(Spacer(1, 4))

    # Slide 5
    story.append(add_slide_script(
        5, "Sơ đồ Cây Topic MQTT 6 Nhánh", "Nguyễn Văn Đức",
        "Quy hoạch Semantic Hierarchy: smoke/<nhóm>/<đối tượng>; Bảng 6 nhánh (telemetry, event/alarm, status, cmd/fan, cmd/buzzer, cmd/mode); Lợi ích của Wildcard smoke/cmd/#.",
        "\"Xin kính chào Thầy và các bạn, em là Nguyễn Văn Đức. Tiếp nối phần kiến trúc của bạn Khang, em xin đại diện nhóm trình bày chi tiết về bản thiết kế Cây Topic MQTT và cấu trúc Payload JSON.<br/><br/>"
        "Để hệ thống vận hành khoa học và có thể mở rộng lên hàng trăm Node cảm biến sau này, nhóm em đã quy hoạch Cây Topic theo nguyên tắc ngữ nghĩa phân tầng (Semantic Hierarchy) với cấu trúc gốc là: smoke/<chức năng>/<đối tượng>.<br/><br/>"
        "Cây topic được phân chia thành 6 nhánh chức năng cực kỳ rõ rệt:<br/>"
        "1. Nhánh Telemetry: smoke/telemetry đẩy dữ liệu đo liên tục mỗi 2s với QoS 0 để tiết kiệm băng thông.<br/>"
        "2. Nhánh Event: smoke/event/alarm dùng QoS 1 đẩy cảnh báo tức thì khi nồng độ khói vượt 400 PPM.<br/>"
        "3. Nhánh Status: smoke/status dùng QoS 1 và Retain=True để lưu trữ xác nhận trạng thái thực tế mới nhất của quạt và còi.<br/>"
        "4. Nhánh Command Downlink: Chia nhỏ thành smoke/cmd/fan, smoke/cmd/buzzer và smoke/cmd/mode. Việc chia nhỏ topic điều khiển giúp ESP32 dễ dàng phân loại lệnh mà không phải parse các cấu trúc JSON phức tạp, đồng thời ESP32 chỉ cần đăng ký duy nhất 1 bộ lọc wildcard: smoke/cmd/# là có thể lắng nghe toàn bộ chỉ thị điều khiển từ người dùng!\""
    ))

    # Slide 6
    story.append(add_slide_script(
        6, "Cấu trúc Payload JSON Telemetry Định kỳ & Gói tin Báo động Alarm", "Nguyễn Văn Đức",
        "Định dạng JSON RFC 8259 tối ưu StaticJsonDocument; Payload Telemetry mỗi 2s; Payload Alarm CRITICAL tức thời (<100ms, thực tế 65ms); QoS 0 vs QoS 1.",
        "\"Thưa Thầy và các bạn, toàn bộ dữ liệu truyền thông trong hệ thống của nhóm em đều tuân thủ chặt chẽ chuẩn JSON RFC 8259, sử dụng thư viện ArduinoJson tối ưu hóa bộ nhớ tĩnh StaticJsonDocument trên vi điều khiển ESP32.<br/><br/>"
        "Ở phía bên trái màn hình là gói tin Telemetry định kỳ gửi lên topic smoke/telemetry mỗi 2 giây. "
        "Gói tin này chứa đầy đủ thông tin định danh device_id, thời gian hoạt động uptime_s, nồng độ khói tính toán mq2_ppm, giá trị ADC thô, nhiệt độ, độ ẩm và trạng thái thực của Quạt, Còi. "
        "Dữ liệu này được thiết kế để vẽ đồ thị diễn tiến môi trường thời gian thực trên Web Dashboard.<br/><br/>"
        "Ở phía bên phải màn hình là gói tin sự kiện báo động khẩn cấp được đẩy lên smoke/event/alarm. "
        "Điểm đột phá ở đây là cơ chế truyền tin hướng sự kiện (Event-driven): Khi nồng độ khói vượt 400 PPM, ESP32 ngắt và phát gói tin này ngay lập tức với độ trễ đo được chỉ 65ms mà không cần đợi hết chu kỳ 2 giây! "
        "Gói tin được gán mức độ nghiêm trọng severity: CRITICAL và chạy trên QoS 1, buộc Broker phải có gói PUBACK xác nhận, đảm bảo thông tin hỏa hoạn đến đích an toàn 100%!\""
    ))

    # Slide 7
    story.append(add_slide_script(
        7, "Cơ chế Điều khiển Downlink từ xa qua MQTTX & Phản hồi Trạng thái", "Nguyễn Văn Đức",
        "3 Gói tin (cmd/fan, cmd/buzzer, status ACK); Tính năng override_duration_s (300s) và Mute (180s); Quy trình 4 bước xử lý lệnh khép kín trên Firmware.",
        "\"Kính thưa Thầy và các bạn, một hệ thống IoT hoàn chỉnh không thể chỉ gửi dữ liệu một chiều mà bắt buộc phải có khả năng tương tác hai chiều (Downlink Command).<br/><br/>"
        "Trên màn hình là 3 gói tin mẫu thể hiện luồng điều khiển Downlink của nhóm:<br/>"
        "• Thứ nhất, lệnh điều khiển quạt smoke/cmd/fan: Cho phép bật hoặc tắt quạt từ xa, hỗ trợ tham số override_duration_s để hẹn giờ chạy cưỡng bức trong 300 giây rồi tự động trả lại chế độ Auto.<br/>"
        "• Thứ hai, lệnh ngắt còi tạm thời smoke/cmd/buzzer: Trong tình huống cứu nạn, còi báo động kêu quá to sẽ làm cản trở việc liên lạc của đội cứu hộ. Người quản trị có thể gửi lệnh Mute để ngắt tiếng còi trong 180 giây, nhưng quạt hút khói vẫn được giữ chạy tối đa!<br/>"
        "• Thứ ba, gói tin phản hồi trạng thái smoke/status: Ngay sau khi xử lý lệnh, ESP32 sẽ Publish bản tin xác nhận kèm kết quả ACCEPTED (đã chấp thuận) hoặc REJECTED (bị từ chối) cùng IP mạng của thiết bị.<br/><br/>"
        "Toàn bộ quy trình 4 bước từ đón nhận callback, parse JSON an toàn, kiểm tra ma trận an toàn và điều khiển GPIO đều diễn ra bất đồng bộ chỉ trong vòng vài mili-giây!\""
    ))

    # Slide 8
    story.append(add_slide_script(
        8, "Ma trận Phân xử An toàn PCCC (Local Safety Interlock)", "Nguyễn Văn Đức",
        "Triết lý 'Edge nắm quyền tối thượng để bảo vệ tính mạng'; Ma trận 3 vùng khói (Nguy hiểm ≥400, Vùng trễ 300-400, An toàn <300); Đoạn code C++ chặn lệnh tắt quạt.",
        "\"Thưa Thầy và các bạn, Slide 8 chính là điểm sáng kỹ thuật mang tính sống còn của đề tài: Ma trận phân xử an toàn PCCC (Local Safety Interlock) được thực thi ngay tại tầng biên ESP32.<br/><br/>"
        "Trong ngành an toàn công nghiệp, một nguyên tắc vàng bất di bất dịch là: 'Thiết bị biên luôn nắm quyền tối thượng để bảo vệ tính mạng con người'. "
        "Hãy thử tưởng tượng kịch bản: Hiện trường đang xảy ra cháy khói ngập ngụa (PPM >= 400), quạt hút đang chạy hết công suất để thông gió cứu nạn. "
        "Nếu một người dùng từ xa bấm nhầm nút Tắt trên điện thoại, hoặc tệ hơn là bị kẻ xấu tấn công mạng gửi lệnh OFF, mà thiết bị nhắm mắt làm theo thì hậu quả sẽ vô cùng thảm khốc!<br/><br/>"
        "Chính vì vậy, Nhóm 04 đã lập trình Ma trận phân xử an toàn 3 vùng:<br/>"
        "1. Vùng Nguy hiểm (PPM >= 400): Bất kể lệnh nào gửi xuống đòi tắt quạt, ESP32 sẽ LẬP TỨC TỪ CHỐI TRIỆT ĐỂ (REJECTED), tiếp tục cưỡng bức quạt chạy 100%, còi hú inh ỏi và gửi bản tin cảnh báo vi phạm ngược về Broker.<br/>"
        "2. Vùng đệm trễ Hysteresis (300 đến 400 PPM): Khóa chốt trạng thái (Latch State) để triệt tiêu hiện tượng rơ-le đóng ngắt liên hồi gây hỏng phần cứng.<br/>"
        "3. Vùng An toàn (PPM < 300): Người dùng mới được trao toàn quyền bật tắt quạt thủ công.\"",
        "Để làm rõ cách hiện thực hóa giải thuật này trên vi điều khiển mà không gây treo hệ thống cùng kết quả đo kiểm 12 Test Cases, sau đây em xin kính mời bạn Nguyễn Văn Mãnh!"
    ))

    # --------------------------------------------------------------------------
    # THÀNH VIÊN 3: NGUYỄN VĂN MÃNH
    # --------------------------------------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph("PHẦN 3: NGUYỄN VĂN MÃNH (Thành viên — Slide 09 đến 12)", h2_style))
    story.append(Paragraph("<i>Thời gian trình bày: 5 phút (10:00 – 15:00) • Mục tiêu: Chứng minh kỹ thuật lập trình nhúng non-blocking, khẳng định độ tin cậy 12/12 Test Case, tổng kết Milestone M2 và mở phần Q&A.</i>", body_style))
    story.append(Spacer(1, 4))

    # Slide 9
    story.append(add_slide_script(
        9, "Kỹ thuật Firmware Non-blocking Reconnect bằng hàm millis()", "Nguyễn Văn Mãnh",
        "Đối chiếu Blocking delay(5000) vs Non-blocking millis(); Máy trạng thái FSM 5 bước; Bảo toàn chu kỳ đọc cảm biến <10ms; Đoạn code C++ handleNetworkConnection().",
        "\"Xin chào Thầy và các bạn, em là Nguyễn Văn Mãnh. Em xin phép phụ trách trình bày về kỹ thuật lập trình nhúng thời gian thực và toàn bộ kết quả kiểm thử nghiệm thu Milestone M2 của nhóm.<br/><br/>"
        "Ở Slide 9, nhóm em muốn nhấn mạnh một kỹ thuật lập trình then chốt: Cơ chế Non-blocking Reconnect bảo vệ thời gian thực bằng hàm millis().<br/><br/>"
        "Rất nhiều người mới làm IoT thường mắc một sai lầm nghiêm trọng là dùng vòng lặp Blocking: while (!client.connected()) { delay(5000); }. "
        "Đối với một hệ thống báo cháy khẩn cấp, việc làm dừng vi điều khiển 5 giây để đợi mạng WiFi là một thảm họa không thể chấp nhận: Khói bốc lên nhưng chip bị đơ, quạt không hút, còi không kêu, thậm chí bộ định thời Watchdog Timer của ESP32 sẽ kích hoạt làm vi điều khiển tự Reset liên tục!<br/><br/>"
        "Để giải quyết triệt để vấn đề này, Nhóm 04 đã tách rời hoàn toàn tác vụ mạng ra khỏi tác vụ an toàn. "
        "Như Thầy thấy trong đoạn code bên phải, hàm handleNetworkConnection() sử dụng các mốc thời gian millis() để kiểm tra kết nối lại ngầm mỗi 5 giây. "
        "Nhờ đó, dù mạng WiFi có bị đứt hay Broker bị sập thì vòng lặp giám sát khói và điều khiển còi quạt tại chỗ vẫn phản hồi tức thời dưới 10 mili-giây mà không hề bị treo!\""
    ))

    # Slide 10
    story.append(add_slide_script(
        10, "Tổng hợp Kết quả Kiểm thử 12/12 Test Case Chuẩn (100% Pass)", "Nguyễn Văn Mãnh",
        "Tỷ lệ hoàn thành 100% (12/12 Pass, 0 Fail); 4 Nhóm kịch bản kiểm thử: Nhóm A (Hạ tầng), Nhóm B (Uplink), Nhóm C (Downlink & Interlock), Nhóm D (Robustness/Reconnect).",
        "\"Thưa Thầy và các bạn, ở Slide 10 là bảng tổng hợp kết quả đo kiểm toàn diện 12/12 Test Case chuẩn mà Nhóm 04 đã thực hiện nghiêm ngặt trên phần mềm Wokwi kết hợp công cụ MQTTX. "
        "Tỷ lệ hoàn thành đạt tuyệt đối 100% Pass, không có bất kỳ ca lỗi hay hành vi bất thường nào.<br/><br/>"
        "12 Test Case này được chúng em quy hoạch thành 4 nhóm kịch bản rõ rệt:<br/>"
        "• Nhóm A (Case 1 và 2): Kiểm tra tầng mạng hạ tầng, ESP32 kết nối WiFi Wokwi-GUEST chỉ mất 2.1 giây, nhận IP và bắt tay Broker EMQX thành công.<br/>"
        "• Nhóm B (Case 3 và 4): Luồng Uplink, kiểm tra gói tin Telemetry đẩy đều đặn mỗi 2s và gói tin Báo động khẩn cấp phát ra chỉ sau 65ms khi kéo thanh trượt Gas lên trên 400 PPM.<br/>"
        "• Nhóm C (Case 5 đến 9): Luồng Downlink, kiểm tra tương tác bật tắt quạt, kiểm tra đặc tính quan trọng nhất là chặn lệnh tắt quạt khi đang có khói (Case 7), ngắt còi tạm thời 180s (Case 8) và chuyển mode AUTO/MANUAL (Case 9).<br/>"
        "• Nhóm D (Case 10 đến 12): Kiểm tra độ ổn định và phục hồi, chứng minh ESP32 không bị treo khi nhận JSON rác, tự động Reconnect sau 5s khi mạng chập chờn và Broker tự động phát chúc thư LWT khi thiết bị mất nguồn đột ngột!<br/><br/>"
        "Toàn bộ các bước kiểm thử này đều có minh chứng log thực nghiệm rõ ràng như nhóm sẽ trình bày ở slide tiếp theo.\""
    ))

    # Slide 11
    story.append(add_slide_script(
        11, "Minh chứng Thực nghiệm Mô phỏng Wokwi & MQTTX (5 Minh chứng)", "Nguyễn Văn Mãnh",
        "5 Khối minh chứng log thực tế: Khởi tạo mạng 2.1s; Telemetry nhận đều đặn; Alarm CRITICAL phát sau 65ms; Safety Interlock chặn lệnh OFF; Reconnect thành công sau 5s.",
        "\"Kính thưa Thầy và các bạn, đây là Slide trực quan hóa 5 minh chứng thực nghiệm đã được ghi nhận trực tiếp trên Serial Monitor của Wokwi và phần mềm MQTTX khi nghiệm thu Tuần 4:<br/><br/>"
        "• Minh chứng 1: Cho thấy quá trình khởi tạo mạng chỉ mất 2.1s, ESP32 nhận IP 10.0.0.15, kết nối broker.emqx.io, đăng ký LWT và Subscribe thành công.<br/>"
        "• Minh chứng 2: MQTTX nhận đều đặn gói tin Telemetry mỗi 2000ms với đầy đủ các trường nồng độ khói, nhiệt độ, độ ẩm và trạng thái I/O.<br/>"
        "• Minh chứng 3: Khi kéo nồng độ khói vượt 400 PPM (cụ thể là 520.8 PPM), trên Wokwi đèn Relay sáng, còi hú vang, và MQTTX nhận ngay gói tin khẩn cấp chỉ sau 65 mili-giây với severity là CRITICAL.<br/>"
        "• Minh chứng 4: Đây là minh chứng ấn tượng nhất: Người dùng cố tình gửi lệnh {'action':'OFF'} để tắt quạt trong khi khói đang cao. ESP32 lập tức in log từ chối REJECTED_SAFETY_LOCK, giữ quạt quay 100% và bắn bản tin báo cáo vi phạm về Broker!<br/>"
        "• Minh chứng 5: Thử nghiệm ngắt mạng đột ngột. ESP32 không hề bị treo, vẫn quét cảm biến đều đặn, và khi có mạng lại, hệ thống tự động kết nối lại Broker trong vòng 5 giây mà không cần con người can thiệp!\""
    ))

    # Slide 12
    story.append(add_slide_script(
        12, "Đánh giá Nghiệm thu Milestone M2, Kế hoạch Tuần 5 & Lời Cảm ơn", "Nguyễn Văn Mãnh",
        "Khẳng định hoàn thành 100% tiêu chí Milestone M2 (10%); Kế hoạch Tuần 5 (Node-RED Middleware, Telegram Bot, Blynk Cloud); Lời cảm ơn Thầy Võ Hoàng Hải & Khởi động Q&A.",
        "\"Kính thưa Thầy Võ Hoàng Hải và toàn thể các bạn sinh viên!<br/><br/>"
        "Để kết lại bài báo cáo tiến độ Tuần 4 của Nhóm 04 hôm nay, em xin được tổng kết lại các thành quả trọng tâm:<br/>"
        "1. Nhóm đã hoàn thành 100% các tiêu chí kỹ thuật của Milestone M2 (Connected Device), đưa hệ thống chuyển dịch thành công từ một thiết bị đo cục bộ sang một thiết bị IoT kết nối thông minh hai chiều qua giao thức MQTT.<br/>"
        "2. Toàn bộ 12 Test Case đều vượt qua xuất sắc với các tính năng vượt trội: Báo động tức thời 65ms, Chúc thư LWT giám sát sống còn thiết bị, Ma trận an toàn PCCC chặn lệnh tắt quạt khi có khói, và giải thuật Non-blocking Reconnect giữ hệ thống hoạt động liên tục không bao giờ treo.<br/>"
        "3. Nhóm đã sẵn sàng toàn bộ giao diện Topic và Payload JSON chuẩn hóa để bàn giao sang Tuần 5, triển khai Tầng 3 Middleware với Node-RED, gửi cảnh báo Telegram Bot tự động và thiết kế Dashboard trên Blynk IoT Cloud.<br/><br/>"
        "Thay mặt Nhóm 04 gồm Khang, Đức và Mãnh, em xin chân thành cảm ơn Thầy đã luôn theo sát, định hướng và hỗ trợ nhóm trong suốt quá trình thực hiện đồ án. "
        "Nhóm em rất mong nhận được những lời nhận xét, góp ý quý báu của Thầy để hoàn thiện sản phẩm hơn nữa. "
        "Bây giờ, nhóm em xin sẵn sàng lắng nghe các câu hỏi phản biện và giải đáp thắc mắc từ Thầy và các bạn. Em xin trân trọng cảm ơn!\""
    ))

    # --------------------------------------------------------------------------
    # MỤC 3: HƯỚNG DẪN TRẢ LỜI CÂU HỎI PHẢN BIỆN (Q&A CHEATSHEET)
    # --------------------------------------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph("3. HƯỚNG DẪN TRẢ LỜI CÂU HỎI PHẢN BIỆN (Q&A CHEATSHEET DỰ PHÒNG)", h1_style))
    story.append(Paragraph(
        "Dưới đây là 3 câu hỏi kỹ thuật trọng tâm mà Giảng viên hướng dẫn thường đặt ra cho sinh viên trong buổi nghiệm thu Milestone M2, "
        "kèm theo người phụ trách trả lời chính và ý trả lời chuẩn xác đã được nhóm chuẩn bị trước:",
        body_style
    ))
    story.append(Spacer(1, 6))

    qa_data = [
        [
            Paragraph("Câu hỏi trọng tâm từ GVHD", table_header_style),
            Paragraph("Người trả lời", table_header_style),
            Paragraph("Ý trả lời kỹ thuật chuẩn xác (Gợi ý câu trả lời)", table_header_style)
        ],
        [
            Paragraph("<b>Câu 1:</b> Tại sao lại dùng <b>broker.emqx.io</b> cổng 1883 không mã hóa mà không dùng SSL/TLS cổng 8883?", table_cell_style),
            Paragraph("<b>Nguyễn Vĩnh Khang</b><br/>(Trưởng nhóm)", table_cell_center),
            Paragraph(
                "<i>Dạ thưa Thầy:</i> Trong môi trường mô phỏng Wokwi, vi điều khiển ESP32 chạy trên mạng ảo NAT Wokwi-GUEST "
                "và việc bắt tay TLS mã hóa trên chip ảo đòi hỏi bộ nhớ heap lớn cũng như tải thêm chứng chỉ CA, có thể làm chậm quá trình khởi động. "
                "Cổng TCP 1883 là lựa chọn tối ưu để kiểm thử chức năng logic tầng mạng ở Milestone M2. "
                "Khi triển khai phần cứng thực tế ở Milestone M4, nhóm sẽ tích hợp WiFiClientSecure và xác thực mTLS trên cổng 8883 để bảo mật.",
                table_cell_style
            )
        ],
        [
            Paragraph("<b>Câu 2:</b> Tại sao <b>smoke/telemetry</b> lại chọn QoS 0 trong khi <b>smoke/event/alarm</b> lại chọn QoS 1?", table_cell_style),
            Paragraph("<b>Nguyễn Văn Đức</b><br/>(Topic & Payload)", table_cell_center),
            Paragraph(
                "<i>Dạ thưa Thầy:</i> Dữ liệu Telemetry được gửi định kỳ đều đặn mỗi 2 giây. Nếu mạng chập chờn rớt 1 gói tin thì 2 giây sau "
                "sẽ có gói tin mới bù đắp ngay, việc dùng QoS 0 giúp tiết kiệm băng thông và giảm thiểu độ trễ mạng. "
                "Ngược lại, gói Alarm khẩn cấp khi khói cháy vượt ngưỡng là dữ liệu mang tính sống còn, phát sinh không định kỳ. "
                "Vì vậy bắt buộc phải dùng QoS 1 để Broker trả về gói PUBACK xác nhận thông điệp cứu hỏa đã đến nơi an toàn!",
                table_cell_style
            )
        ],
        [
            Paragraph("<b>Câu 3:</b> Nếu mạng WiFi bị mất hoàn toàn trong 1 giờ thì cảm biến khói và còi quạt có còn hoạt động không?", table_cell_style),
            Paragraph("<b>Nguyễn Văn Mãnh</b><br/>(Firmware & Test)", table_cell_center),
            Paragraph(
                "<i>Dạ thưa Thầy:</i> Hoạt động hoàn toàn bình thường 100%! Nhờ giải thuật Non-blocking Reconnect bằng hàm <code>millis()</code>, "
                "ESP32 không bao giờ dùng lệnh <code>delay()</code> trong vòng lặp kết nối. Cứ mỗi 5 giây vi điều khiển chỉ 'liếc' qua kiểm tra mạng ngầm một lần. "
                "Vòng lặp chính vẫn quét cảm biến MQ2, tính toán PPM và kích hoạt Còi hú + Quạt hút tức thời trong vòng chưa tới 10ms nếu phát hiện khói, độc lập hoàn toàn với việc có mạng hay không!",
                table_cell_style
            )
        ]
    ]

    t_qa = Table(qa_data, colWidths=[150, 85, 280])
    t_qa.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_qa)
    story.append(Spacer(1, 14))

    # --------------------------------------------------------------------------
    # MỤC 4: LƯU Ý KHI THỰC HIỆN THUYẾT TRÌNH TRƯỚC HỘI ĐỒNG
    # --------------------------------------------------------------------------
    story.append(Paragraph("4. QUY TẮC PHỐI HỢP & PHONG THÁI THUYẾT TRÌNH CỦA NHÓM", h1_style))
    story.append(Paragraph("• <b>Đúng thời gian (Time Management):</b> Mỗi bạn làm chủ thời gian đúng 5 phút. Khi bạn trước đang nói câu chuyển giao, bạn tiếp theo chủ động đứng lên bục và cầm micro sẵn sàng.", bullet_style))
    story.append(Paragraph("• <b>Chuyển Slide nhịp nhàng:</b> Trưởng nhóm (Khang) hoặc người đang đứng cạnh máy tính sẽ bấm phím Space / PageDown chuyển slide ngay khi người nói bắt đầu chuyển ý.", bullet_style))
    story.append(Paragraph("• <b>Mắt hướng về Thầy & Khán giả (Eye Contact):</b> Không nhìn chăm chú vào slide trên máy chiếu, sử dụng slide như màn hình hiển thị trực quan và tập trung diễn đạt theo ngôn từ tự nhiên của mình.", bullet_style))
    story.append(Paragraph("• <b>Đồng bộ trang phục:</b> Áo sơ mi trắng hoặc áo đồng phục HUIT, phong thái tự tin, tác phong kỹ sư CNTT chuyên nghiệp.", bullet_style))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully generated: {pdf_path}")

if __name__ == "__main__":
    build_pdf()
