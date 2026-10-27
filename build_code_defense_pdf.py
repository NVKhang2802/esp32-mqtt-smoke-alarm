# -*- coding: utf-8 -*-
"""
Script to generate the comprehensive, in-depth Code Defense Guide PDF
for e:\\IoT\\DoAn\\src\\main.cpp.
Output: docs/pdf/GiaiThich_ChiTiet_Code_main_cpp_BaoVeDoAn.pdf
"""

import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# Register Fonts
font_regular = r'C:\Windows\Fonts\arial.ttf'
font_bold    = r'C:\Windows\Fonts\arialbd.ttf'
font_italic  = r'C:\Windows\Fonts\ariali.ttf'
font_bolditalic = r'C:\Windows\Fonts\arialbi.ttf'

pdfmetrics.registerFont(TTFont('Arial', font_regular))
pdfmetrics.registerFont(TTFont('Arial-Bold', font_bold))
pdfmetrics.registerFont(TTFont('Arial-Italic', font_italic))
pdfmetrics.registerFont(TTFont('Arial-BoldItalic', font_bolditalic))

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
        
        # Header (page > 1)
        if self._pageNumber > 1:
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(40, 805, 555, 805)
            self.drawString(40, 810, "CẨM NANG BẢO VỆ MÃ NGUỒN (SRC/MAIN.CPP) — ĐỒ ÁN IOT BÁO KHÓI")
            self.drawRightString(555, 810, "KHOA CNTT • HUIT")

        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(40, 38, 555, 38)
        self.drawString(40, 26, "Tài liệu giải thích cặn kẽ từng dòng lệnh & thông số dành cho sinh viên bảo vệ trước GVHD")
        self.drawRightString(555, 26, f"Trang {self._pageNumber} / {page_count}")
        self.restoreState()

def build_pdf():
    pdf_dir = r"E:\IoT\DoAn\docs\pdf"
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, "GiaiThich_ChiTiet_Code_main_cpp_BaoVeDoAn.pdf")

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=48,
        bottomMargin=48
    )

    styles = getSampleStyleSheet()

    # Styles definition
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Normal'],
        fontName='Arial-Bold', fontSize=15, leading=19,
        textColor=colors.HexColor("#1F4E79"), alignment=1, spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle', parent=styles['Normal'],
        fontName='Arial-Bold', fontSize=10.5, leading=14,
        textColor=colors.HexColor("#2E75B6"), alignment=1, spaceAfter=8
    )
    meta_style = ParagraphStyle(
        'MetaText', parent=styles['Normal'],
        fontName='Arial', fontSize=8.5, leading=12,
        textColor=colors.HexColor("#475569"), alignment=1
    )
    h1_style = ParagraphStyle(
        'H1', parent=styles['Normal'],
        fontName='Arial-Bold', fontSize=11.5, leading=15,
        textColor=colors.HexColor("#1F4E79"), spaceBefore=12, spaceAfter=5, keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'H2', parent=styles['Normal'],
        fontName='Arial-Bold', fontSize=10, leading=13.5,
        textColor=colors.HexColor("#2E75B6"), spaceBefore=8, spaceAfter=4, keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontName='Arial', fontSize=8.5, leading=12.5,
        textColor=colors.HexColor("#1E293B"), spaceAfter=4
    )
    bullet_style = ParagraphStyle(
        'Bullet', parent=styles['Normal'],
        fontName='Arial', fontSize=8.5, leading=12,
        textColor=colors.HexColor("#1E293B"), leftIndent=12, spaceAfter=3
    )
    code_block_style = ParagraphStyle(
        'CodeSnippet', parent=styles['Normal'],
        fontName='Arial-Bold', fontSize=8, leading=11,
        textColor=colors.HexColor("#0F172A")
    )
    explain_box_style = ParagraphStyle(
        'ExplainText', parent=styles['Normal'],
        fontName='Arial', fontSize=8.5, leading=12.5,
        textColor=colors.HexColor("#0F172A")
    )
    question_style = ParagraphStyle(
        'QuestionP', parent=styles['Normal'],
        fontName='Arial-Bold', fontSize=9, leading=12.5,
        textColor=colors.HexColor("#B91C1C"), spaceBefore=6, spaceAfter=2, keepWithNext=True
    )
    answer_style = ParagraphStyle(
        'AnswerP', parent=styles['Normal'],
        fontName='Arial', fontSize=8.5, leading=12.5,
        textColor=colors.HexColor("#1E293B"), spaceAfter=6
    )
    table_header_style = ParagraphStyle(
        'TblHdr', parent=styles['Normal'],
        fontName='Arial-Bold', fontSize=8, leading=11,
        textColor=colors.white, alignment=1
    )
    table_cell_style = ParagraphStyle(
        'TblCell', parent=styles['Normal'],
        fontName='Arial', fontSize=7.5, leading=10.5,
        textColor=colors.HexColor("#1E293B")
    )

    story = []

    # --------------------------------------------------------------------------
    # HEADER BANNER
    # --------------------------------------------------------------------------
    story.append(Paragraph("TRƯỜNG ĐẠI HỌC CÔNG THƯƠNG TP. HỒ CHÍ MINH (HUIT) — KHOA CNTT", meta_style))
    story.append(Paragraph("BỘ MÔN MẠNG & AN TOÀN THÔNG TIN — ĐỒ ÁN LẬP TRÌNH NHÚNG IOT", meta_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1F4E79"), spaceAfter=8))

    story.append(Paragraph("TÀI LIỆU GIẢI THÍCH TOÀN DIỆN MÃ NGUỒN <code>SRC/MAIN.CPP</code>", title_style))
    story.append(Paragraph("CẨM NANG VẤN ĐÁP KỸ THUẬT DÀNH CHO SINH VIÊN BẢO VỆ TRƯỚC GIẢNG VIÊN", subtitle_style))
    
    meta_desc = (
        "<b>Đề tài:</b> Hệ thống Báo khói Cảnh báo sớm (Nhóm 04) &nbsp;|&nbsp; "
        "<b>GVHD:</b> ThS. Võ Hoàng Hải &nbsp;|&nbsp; "
        "<b>Phiên bản mã nguồn:</b> Tuần 4 - Tầng 2 Network MQTT (Milestone M2)<br/>"
        "<b>Mục đích:</b> Giúp sinh viên nắm rõ bản chất đến từng dòng lệnh, hiểu rõ lý do chọn từng hàm số liệu, "
        "và trả lời tự tin 100% các câu hỏi 'vặn vẹo' sâu của giảng viên."
    )
    story.append(Paragraph(meta_desc, meta_style))
    story.append(Spacer(1, 8))

    # Helper function for Code Explanation Card
    def add_code_explain_card(line_range, code_text, core_concept, deep_dive_text):
        content = []
        hdr = Paragraph(f"<b>ĐOẠN CODE DÒNG {line_range}:</b> {core_concept}", ParagraphStyle(
            'HdrCard', parent=styles['Normal'], fontName='Arial-Bold', fontSize=9, textColor=colors.HexColor("#1F4E79")
        ))
        content.append(hdr)
        content.append(Spacer(1, 2))

        # Code box
        t_code = Table([[Paragraph(f"<code>{code_text}</code>", code_block_style)]], colWidths=[515])
        t_code.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        content.append(t_code)
        content.append(Spacer(1, 3))

        # Explanation box
        t_exp = Table([[Paragraph(deep_dive_text, explain_box_style)]], colWidths=[515])
        t_exp.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
            ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor("#93C5FD")),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        content.append(t_exp)
        content.append(Spacer(1, 8))
        return KeepTogether(content)

    # --------------------------------------------------------------------------
    # CHƯƠNG 1: TỔNG QUAN KIẾN TRÚC NHÚNG
    # --------------------------------------------------------------------------
    story.append(Paragraph("1. KIẾN TRÚC MÃ NGUỒN VÀ NGUYÊN LÝ THỜI GIAN THỰC (REAL-TIME ARCHITECTURE)", h1_style))
    story.append(Paragraph(
        "Mã nguồn <code>src/main.cpp</code> được thiết kế theo kiến trúc <b>Vòng lặp siêu tuần hoàn bất đồng bộ (Non-blocking Super-loop with Time Slicing)</b>. "
        "Đây là kiến trúc chuẩn công nghiệp cho các hệ thống nhúng IoT an toàn khẩn cấp, khắc phục triệt để nhược điểm làm tê liệt vi điều khiển của lập trình tuần tự truyền thống.",
        body_style
    ))
    story.append(Paragraph("<b>Hai nguyên tắc cốt tử mà Giảng viên thường đánh giá cao:</b>", body_style))
    story.append(Paragraph("• <b>Nguyên tắc 1 — Tuyệt đối không dùng <code>delay()</code> trong <code>loop()</code>:</b> Lệnh <code>delay(N)</code> làm CPU rơi vào vòng lặp rỗng (NOP loop) đóng băng toàn bộ hệ thống. Trong hệ thống báo cháy, nếu dừng 2 giây thì khi khói bốc lên ngùn ngụt, vi điều khiển hoàn toàn bị 'mù', còi không kêu và quạt không bật. Vì vậy, nhóm sử dụng hàm <code>millis()</code> để phân chia các lát cắt thời gian ngầm (Time Slicing).", bullet_style))
    story.append(Paragraph("• <b>Nguyên tắc 2 — Tách rời logic mạng và an toàn biên (Decoupling):</b> Mạng WiFi hay MQTT Broker có thể chập chờn, mất kết nối hàng giờ, nhưng logic đọc cảm biến khói, điều khiển còi hú và quạt hút tại chỗ vẫn phải phản hồi tức thời dưới 10 mili-giây.", bullet_style))
    story.append(Spacer(1, 6))

    # --------------------------------------------------------------------------
    # CHƯƠNG 2: GIẢI THÍCH TỪNG DÒNG LỆNH CỤ THỂ
    # --------------------------------------------------------------------------
    story.append(Paragraph("2. GIẢI PHÁP CHI TIẾT TỪNG DÒNG LỆNH & THÔNG SỐ TRONG FILE <code>MAIN.CPP</code>", h1_style))

    # Đoạn 1: Thư viện & GPIO
    story.append(add_code_explain_card(
        "28 – 40",
        "#include &lt;Arduino.h&gt;<br/>"
        "#include &lt;WiFi.h&gt;<br/>"
        "#include &lt;PubSubClient.h&gt;<br/>"
        "#include \"DHT.h\"<br/>"
        "#define PIN_MQ2    34  // ADC1_CH6<br/>"
        "#define PIN_DHT    4   // Digital 1-Wire<br/>"
        "#define PIN_BUZZER 16<br/>"
        "#define PIN_RELAY  17<br/>"
        "#define PIN_BUTTON 18",
        "Khai báo Thư viện và Lựa chọn Chân GPIO Phần cứng",
        "<b>Hỏi sâu của Giảng viên:</b> <i>'Tại sao cảm biến MQ2 lại cắm vào chân GPIO 34 mà không cắm chân khác như GPIO 2, 4, 15?'</i><br/>"
        "<b>Trả lời chuẩn kỹ sư:</b><br/>"
        "1. Trên vi điều khiển ESP32 có 2 bộ chuyển đổi ADC: ADC1 (GPIO 32-39) và ADC2 (GPIO 0, 2, 4, 12-15, 25-27). <b>Khi bật bộ phát WiFi, ESP32 sẽ chiếm dụng hoàn toàn bộ ADC2</b> để điều chỉnh công suất sóng vô tuyến. Nếu cắm cảm biến Analog vào các chân ADC2 thì hàm <code>analogRead()</code> sẽ luôn trả về lỗi hoặc sai số nghiêm trọng! Chân GPIO 34 thuộc ADC1 (ADC1_CH6) nên hoạt động 100% độc lập, không bị xung đột với WiFi.<br/>"
        "2. Chân GPIO 34 là chân <b>Input-only</b> (không có điện trở kéo nội Pullup/Pulldown và không thể cấu hình Output), cực kỳ an toàn và chuyên dụng để đọc tín hiệu điện áp từ cảm biến.<br/>"
        "3. Chân GPIO 18 dùng cho nút nhấn được cấu hình <code>INPUT_PULLUP</code>, tận dụng điện trở kéo lên nguồn 3.3V có sẵn bên trong ESP32, tiết kiệm linh kiện ngoài."
    ))

    # Đoạn 2: Struct SensorConfig & Hysteresis
    story.append(add_code_explain_card(
        "61 – 86",
        "struct SensorConfig {<br/>"
        "  float vccSensor; float rlKOhm;<br/>"
        "  float curveA; float curveB;<br/>"
        "  float alarmThreshold; // 400.0 PPM<br/>"
        "  float safeThreshold;  // 300.0 PPM<br/>"
        "  unsigned long intervalMQ2; // 2000 ms<br/>"
        "  unsigned long intervalDHT; // 5000 ms<br/>"
        "};",
        "Cấu trúc Cấu hình Động & Vùng Đệm Trễ An toàn (Hysteresis)",
        "<b>Hỏi sâu của Giảng viên:</b> <i>'Tại sao lại dùng struct gom nhóm? Tại sao ngưỡng báo động là 400 mà ngưỡng an toàn lại là 300? Tại sao không dùng 1 ngưỡng 400 duy nhất?'</i><br/>"
        "<b>Trả lời chuẩn kỹ sư:</b><br/>"
        "1. Gom nhóm struct giúp mã nguồn hướng đối tượng, dễ dàng mở rộng nạp cấu hình từ bộ nhớ flash EEPROM hoặc cập nhật từ xa qua MQTT Downlink mà không phải sửa code.<br/>"
        "2. <b>Hiện tượng Rung rơ-le (Relay Chattering):</b> Nếu chỉ dùng duy nhất 1 ngưỡng 400 PPM: Khi khói dao động mấp mé quanh 399.9 và 400.1 PPM, rơ-le sẽ đóng ngắt liên tục hàng chục lần trong vài giây, gây phóng tia lửa điện làm cháy cuộn hút rơ-le và hỏng quạt! "
        "Khoảng chênh lệch giữa 400 PPM (Bật) và 300 PPM (Tắt) tạo ra một <b>Vùng đệm trễ (Hysteresis Band rộng 100 PPM)</b>: Phải trên 400 mới kích hoạt còi quạt, và phải giảm sâu xuống dưới 300 mới cho tắt, đảm bảo rơ-le hoạt động bền bỉ, êm ái."
    ))

    # Đoạn 3: Công thức chuyển đổi MQ-2 và Hiệu chuẩn 2 điểm
    story.append(add_code_explain_card(
        "167 – 215",
        "float v_out = (avgADC / 4095.0) * cfg.vccSensor;<br/>"
        "float rs = cfg.rlKOhm * (cfg.vccSensor - v_out) / v_out;<br/>"
        "cfg.curveB = (logPPM2 - logPPM1) / (logRs2 - logRs1);<br/>"
        "cfg.curveA = cfg.calibPoint1 / pow(rs1, cfg.curveB);<br/>"
        "float ppm = cfg.curveA * pow(ratio, cfg.curveB);",
        "Bản chất Vật lý Bán dẫn MQ-2 & Thuật toán Đường cong Logarit",
        "<b>Hỏi sâu của Giảng viên:</b> <i>'Tại sao lại chia cho 4095.0? Công thức tính Rs từ đâu ra? Tại sao lại lấy logarit để tính curveA và curveB?'</i><br/>"
        "<b>Trả lời chuẩn kỹ sư:</b><br/>"
        "1. <b>Tại sao là 4095.0?</b> Bộ ADC của ESP32 có độ phân giải 12-bit, tức là chia dải đo điện áp từ 0V đến 3.3V thành 2^12 = 4096 mức giá trị rời rạc (từ 0 đến 4095). Giá trị đọc cực đại tương ứng với 4095 nên phải chia cho 4095.0 để ra tỷ lệ điện áp chính xác.<br/>"
        "2. <b>Công thức Rs:</b> Mạch cảm biến MQ2 là mạch cầu phân áp giữa điện trở nhạy khí Rs và điện trở tải Rl (10 kOhm):<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;V_out = Vcc * [Rl / (Rs + Rl)] &rArr; Rs = Rl * (Vcc - V_out) / V_out.<br/>"
        "3. <b>Công thức PPM hàm mũ và Logarit:</b> Bán dẫn SnO2 của MQ2 có đặc tính nồng độ khí tuân theo hàm lũy thừa: PPM = A * (Rs/R0)^B. "
        "Lấy logarit cơ số 10 hai vế: log(PPM) = log(A) + B * log(Rs/R0). Đây là phương trình đường thẳng y = B*x + C trên hệ tọa độ Log-Log! "
        "Với 2 điểm thực nghiệm đo trên Wokwi (200 PPM &rarr; Rs1=1.71 kOhm; 1000 PPM &rarr; Rs2=0.8852 kOhm), nhóm giải hệ phương trình tìm được hệ số góc B âm và hệ số A chính xác tuyệt đối."
    ))

    # Đoạn 4: Debounce nút nhấn
    story.append(add_code_explain_card(
        "217 – 242",
        "void handleManualButton() {<br/>"
        "  bool reading = digitalRead(PIN_BUTTON);<br/>"
        "  if (reading != lastButtonState) lastDebounceTime = millis();<br/>"
        "  if ((millis() - lastDebounceTime) &gt; DEBOUNCE_DELAY) {<br/>"
        "    if (reading != currentButtonStable) { ... }<br/>"
        "  }<br/>"
        "}",
        "Thuật toán Chống nảy phím (Debounce) và Khóa an toàn PCCC",
        "<b>Hỏi sâu của Giảng viên:</b> <i>'Chống dội (Debounce) là gì? Nếu không có đoạn code này thì chuyện gì xảy ra? Biến DEBOUNCE_DELAY=50 nghĩa là sao?'</i><br/>"
        "<b>Trả lời chuẩn kỹ sư:</b><br/>"
        "1. <b>Bản chất cơ học:</b> Nút nhấn vật lý khi bấm vào không đóng tiếp điểm dứt khoát mà 2 lá đồng sẽ va đập vào nhau tạo ra hiện tượng rung cơ học (bouncing), sinh ra hàng chục xung HIGH/LOW liên tiếp trong khoảng 10-30 mili-giây. "
        "Nếu không có debounce, vi điều khiển với xung nhịp 240MHz sẽ hiểu là người dùng bấm nút 10-20 lần, khiến quạt bị bật tắt loạn xạ!<br/>"
        "2. <b>DEBOUNCE_DELAY = 50ms:</b> Hệ thống chỉ công nhận nút đã đổi trạng thái nếu tín hiệu giữ ổn định liên tục quá 50ms. 50ms là thời gian vàng: đủ dài để lọc sạch nhiễu rung kim loại nhưng đủ ngắn để con người không cảm thấy bị trễ (độ trễ phản xạ ngón tay người là ~150ms).<br/>"
        "3. <b>Khóa an toàn:</b> Dòng 228 kiểm tra <code>if (autoOverrideActive)</code>: Nếu đang báo cháy, nút bấm bị vô hiệu hóa hoàn toàn, ngăn chặn việc ai đó vô ý bấm tắt quạt tại chỗ."
    ))

    # Đoạn 5: Callback MQTT và Kỹ thuật Buffer an toàn
    story.append(add_code_explain_card(
        "245 – 254",
        "void mqttCallback(char* topic, byte* payload, unsigned int length) {<br/>"
        "  char message[256];<br/>"
        "  if (length &gt;= sizeof(message)) length = sizeof(message) - 1;<br/>"
        "  memcpy(message, payload, length);<br/>"
        "  message[length] = '\\0';<br/>"
        "}",
        "Tiếp nhận Bản tin Downlink và Kỹ thuật Null-Terminator Chống Crash",
        "<b>Hỏi sâu của Giảng viên:</b> <i>'Tại sao payload lại là byte* mà không phải char*? Tại sao phải memcpy và ép thêm ký tự \\0 ở cuối?'</i><br/>"
        "<b>Trả lời chuẩn kỹ sư:</b><br/>"
        "1. Thư viện PubSubClient nhận gói tin nhị phân TCP từ Broker dưới dạng mảng byte thô (raw byte array), không hề có ký tự kết thúc chuỗi <code>\\0</code> (Null-terminator).<br/>"
        "2. Nếu truyền trực tiếp con trỏ <code>payload</code> vào các hàm xử lý chuỗi trong C như <code>strcmp()</code>, <code>indexOf()</code> hoặc <code>Serial.print()</code>, hàm sẽ tiếp tục đọc tràn sang các ô nhớ RAM lân cận (Buffer Out-of-bounds Read) cho đến khi gặp ngẫu nhiên một byte 0. "
        "Hành vi này dẫn đến lỗi tràn bộ đệm (Memory Corruption) làm kích hoạt lỗi Panic Dump và Reset ESP32 ngay lập tức!<br/>"
        "3. Lệnh <code>message[length] = '\\0'</code> đóng vai trò biến mảng byte thô thành chuỗi C chuẩn (C-String) an toàn tuyệt đối."
    ))

    # Đoạn 6: Safety Interlock trên MQTT Downlink
    story.append(add_code_explain_card(
        "267 – 275",
        "if (msg.indexOf(\"OFF\") &gt;= 0) {<br/>"
        "  if (currentPPM &gt;= cfg.alarmThreshold) {<br/>"
        "    Serial.println(\"TU CHOI! [PCCC Interlock] Khoi nguy hiem!\");<br/>"
        "    publishStatusAck(\"cmd_fan_off\", \"REJECTED_SAFETY_LOCK\", ...);<br/>"
        "    return; // HUY BO LENH TAT QUAT<br/>"
        "  }<br/>"
        "  setFan(false);<br/>"
        "}",
        "Ma trận Phân xử An toàn PCCC (Local Safety Interlock) tại Tầng Biên",
        "<b>Hỏi sâu của Giảng viên:</b> <i>'Dòng code này thể hiện tính năng gì của Tầng 2? Tại sao lại có chữ return ở đây?'</i><br/>"
        "<b>Trả lời chuẩn kỹ sư:</b><br/>"
        "1. Đây là <b>Ma trận an toàn PCCC (Safety Interlock)</b> chạy độc lập tại biên (Edge Computing). Triết lý thiết kế là: An toàn tính mạng con người là ưu tiên số 1, thiết bị biên nắm quyền kiểm soát tối cao.<br/>"
        "2. Khi hiện trường cháy có nồng độ khói &ge; 400 PPM, nếu có lệnh từ xa gửi xuống đòi tắt quạt (do người dùng thao tác nhầm trên App hoặc bị tấn công mạng), lệnh <code>if (currentPPM &gt;= cfg.alarmThreshold)</code> sẽ bắt lại ngay.<br/>"
        "3. Từ khóa <code>return;</code> lập tức kết thúc hàm callback, ngăn chặn việc thực thi dòng <code>setFan(false)</code> bên dưới, giữ quạt hút tiếp tục chạy 100% công suất để cứu hộ và gửi cảnh báo vi phạm về máy chủ."
    ))

    # Đoạn 7: Mute Coi & Timer
    story.append(add_code_explain_card(
        "296 – 319",
        "if (msg.indexOf(\"MUTE\") &gt;= 0) {<br/>"
        "  isMuted = true;<br/>"
        "  muteStartTime = millis();<br/>"
        "  muteDurationMs = 180000; // 180s<br/>"
        "  setBuzzer(false);<br/>"
        "}",
        "Cơ chế Ngắt còi tạm thời (Mute Buzzer) Phục vụ Tác nghiệp Hiện trường",
        "<b>Hỏi sâu của Giảng viên:</b> <i>'Tại sao lại có tính năng Mute còi trong PCCC? 180000 là gì? Hết thời gian đó thì sao?'</i><br/>"
        "<b>Trả lời chuẩn kỹ sư:</b><br/>"
        "1. Trong thực tế PCCC, khi đội cứu hộ đã tiếp cận hiện trường, tiếng còi hú inh ỏi liên tục sẽ làm cản trở việc bộ đàm và trao đổi thông tin cứu nạn. Người chỉ huy cần quyền tắt còi tạm thời nhưng <b>quạt hút khói vẫn bắt buộc phải quay</b>.<br/>"
        "2. Con số <code>180000</code> là 180.000 mili-giây, tương đương 3 phút (180 giây). Nhóm không dùng <code>delay(180000)</code> mà lưu mốc thời gian <code>muteStartTime = millis()</code>.<br/>"
        "3. Ở dòng 480 trong vòng lặp <code>loop()</code>, hệ thống kiểm tra <code>if (now - muteStartTime &gt;= muteDurationMs)</code>: Hết 180 giây, cờ <code>isMuted</code> tự động mở lại; nếu khói vẫn còn (&ge;400 PPM), còi sẽ tự động hú tiếp để cảnh báo, tránh việc quên không bật lại còi!"
    ))

    # Đoạn 8: Non-blocking Network Reconnect
    story.append(add_code_explain_card(
        "339 – 376",
        "void handleNetworkConnection() {<br/>"
        "  unsigned long now = millis();<br/>"
        "  if (WiFi.status() != WL_CONNECTED) {<br/>"
        "    if (now - lastWifiRetry &gt;= RETRY_INTERVAL) {<br/>"
        "      lastWifiRetry = now; WiFi.begin(WIFI_SSID, WIFI_PASS);<br/>"
        "    }<br/>"
        "    return;<br/>"
        "  }<br/>"
        "  if (!mqttClient.connected()) { ... }<br/>"
        "}",
        "Giải thuật Tự phục hồi Kết nối Mạng Không Chặn (Non-blocking Auto-reconnect)",
        "<b>Hỏi sâu của Giảng viên:</b> <i>'Khi mất mạng WiFi thì hàm này hoạt động thế nào? Tại sao có lệnh return? Lệnh return ở đây có làm dừng toàn bộ chương trình không?'</i><br/>"
        "<b>Trả lời chuẩn kỹ sư:</b><br/>"
        "1. <b>Không bao giờ dừng vi điều khiển:</b> Nếu mất WiFi, lệnh <code>if (now - lastWifiRetry &gt;= 5000)</code> đảm bảo cứ đúng 5 giây nó mới thử gọi hàm kết nối lại một lần ngầm.<br/>"
        "2. <b>Bản chất lệnh return:</b> Lệnh <code>return;</code> chỉ thoát ra khỏi hàm <code>handleNetworkConnection()</code> để trở về hàm <code>loop()</code> chính. Nó <b>hoàn toàn không làm dừng chương trình</b>! "
        "Các dòng code tiếp theo trong <code>loop()</code> như đọc cảm biến MQ2, kiểm tra nồng độ khói và bật còi quạt vẫn tiếp tục được thực thi liên tục và mượt mà.<br/>"
        "3. Nếu không có bộ định thời 5s mà gọi <code>WiFi.begin()</code> liên tục trong mỗi vòng lặp loop, chip WiFi của ESP32 sẽ bị nghẽn lệnh và kích hoạt Watchdog Timer gây tự khởi động lại (Reboot loop)."
    ))

    # Đoạn 9: Last Will and Testament
    story.append(add_code_explain_card(
        "358 – 367",
        "const char* lwtMsg = \"{\\\"device_id\\\":\\\"ESP32_Smoke_Nhom04\\\",\\\"status\\\":\\\"offline\\\"}\";<br/>"
        "if (mqttClient.connect(uniqueClientId.c_str(), TOPIC_LWT, 1, true, lwtMsg)) {<br/>"
        "  mqttClient.publish(TOPIC_LWT, \"{\\\"status\\\":\\\"online\\\"}\", true);<br/>"
        "  mqttClient.subscribe(\"smoke/cmd/#\", 1);<br/>"
        "}",
        "Cơ chế Chúc thư LWT (Last Will & Testament) và Cờ Retained Messages",
        "<b>Hỏi sâu của Giảng viên:</b> <i>'LWT là gì? Tham số 1 và true trong hàm connect có ý nghĩa gì? Tại sao khi kết nối lại publish online kèm true?'</i><br/>"
        "<b>Trả lời chuẩn kỹ sư:</b><br/>"
        "1. <b>Ý nghĩa LWT:</b> Là cơ chế 'di chúc' của MQTT. Khi ESP32 bị mất nguồn đột ngột hoặc cháy đứt dây mạng, Broker không nhận được gói tin PINGREQ sẽ tự động phát gói tin <code>lwtMsg</code> này đến toàn bộ các bên theo dõi để cảnh báo trạm đo khói đã chết!<br/>"
        "2. <b>Tham số <code>1, true</code> trong hàm connect:</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;• <code>1</code>: Cấp độ đảm bảo truyền tin QoS 1 (đảm bảo thông điệp offline ít nhất 1 lần đến đích).<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;• <code>true</code>: Cờ <b>Retain = true</b>. Broker sẽ lưu vĩnh viễn thông điệp này trong bộ nhớ đệm, bất kỳ Client nào (Node-RED, Web, App) vừa mở lên kết nối vào topic <code>smoke/lwt</code> sẽ nhận ngay được trạng thái hiện thời của thiết bị.<br/>"
        "3. Khi vừa kết nối thành công, ESP32 publish ngay <code>online</code> với <code>Retain=true</code> để ghi đè (overwrite) bức chúc thư cũ, xác nhận thiết bị đã hồi sinh."
    ))

    # Đoạn 10: snprintf vs sprintf trong Telemetry
    story.append(add_code_explain_card(
        "380 – 397",
        "void publishTelemetry() {<br/>"
        "  if (!mqttClient.connected()) return;<br/>"
        "  char payload[256];<br/>"
        "  snprintf(payload, sizeof(payload),<br/>"
        "    \"{\\\"device_id\\\":\\\"ESP32_Smoke_Nhom04\\\",\\\"uptime_s\\\":%lu,\\\"mq2_ppm\\\":%.1f,...}\",<br/>"
        "    millis() / 1000, currentPPM, ...<br/>"
        "  );<br/>"
        "  mqttClient.publish(TOPIC_TELEMETRY, payload);<br/>"
        "}",
        "Đóng gói Payload JSON bằng hàm snprintf và Kiểm tra Trạng thái Kết nối",
        "<b>Hỏi sâu của Giảng viên:</b> <i>'Tại sao dùng snprintf mà không dùng sprintf hay String cộng chuỗi (+)? Nếu mất mạng mà gọi publish thì sao?'</i><br/>"
        "<b>Trả lời chuẩn kỹ sư:</b><br/>"
        "1. <b>Tại sao dùng snprintf?</b> Hàm <code>sprintf</code> truyền thống không kiểm tra kích thước bộ đệm. Nếu chuỗi sinh ra dài hơn 256 byte, nó sẽ ghi đè lên các vùng nhớ khác gây crash CPU. Hàm <code>snprintf(payload, sizeof(payload), ...)</code> bắt buộc giới hạn tối đa đúng 256 byte, nếu dài hơn sẽ tự động cắt ngắn an toàn.<br/>"
        "2. <b>Tại sao không dùng String cộng chuỗi?</b> Việc cộng chuỗi đối tượng <code>String s = s + ...</code> trên vi điều khiển sẽ liên tục cấp phát và giải phóng vùng nhớ Heap (Dynamic Memory Allocation), sau vài ngày chạy liên tục sẽ gây ra hiện tượng phân mảnh bộ nhớ (Heap Fragmentation) làm treo ESP32.<br/>"
        "3. Dòng <code>if (!mqttClient.connected()) return;</code> bảo vệ hệ thống: Nếu đang rớt mạng, hàm lập tức thoát ra, không tốn thời gian format chuỗi vô ích."
    ))

    # Đoạn 11: Setup & Loop chu kỳ 2s và 5s
    story.append(add_code_explain_card(
        "435 – 547",
        "// Trong setup(): delay(1000);<br/>"
        "// Trong loop():<br/>"
        "if (now - lastMQ2Time &gt;= cfg.intervalMQ2) { // 2000 ms<br/>"
        "  lastMQ2Time = now; currentPPM = readMQ2PPM(); ...<br/>"
        "}<br/>"
        "if (now - lastDHTTime &gt;= cfg.intervalDHT) { // 5000 ms<br/>"
        "  lastDHTTime = now; currentTemp = dht.readTemperature(); ...<br/>"
        "}",
        "Khởi tạo Hệ thống và Kỹ thuật Đa nhiệm Hợp tác (Cooperative Multitasking)",
        "<b>Hỏi sâu của Giảng viên:</b> <i>'Tại sao trong setup có lệnh delay(1000) mà trong loop lại không được có? Con số 2000ms và 5000ms có ý nghĩa gì? Lúc mới bật nguồn nó chạy thế nào?'</i><br/>"
        "<b>Trả lời chuẩn kỹ sư:</b><br/>"
        "1. <b>Lệnh <code>delay(1000)</code> trong <code>setup()</code>:</b> Hàm <code>setup()</code> chỉ chạy duy nhất 1 lần khi cấp điện. Lệnh delay 1 giây ở đây là cực kỳ cần thiết để chờ điện áp nguồn cấp ổn định và cổng UART Serial trên máy tính kịp nhận diện baudrate 115200.<br/>"
        "2. <b>Tại sao MQ2 đọc mỗi 2000ms còn DHT22 đọc mỗi 5000ms?</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;• <b>MQ-2 (2 giây):</b> Nồng độ khói khi cháy biến thiên rất nhanh, cần lấy mẫu chu kỳ ngắn (2s) để phát hiện và dập tắt hỏa hoạn kịp thời.<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;• <b>DHT-22 (5 giây):</b> Nhiệt độ và độ ẩm phòng biến thiên chậm. Quan trọng hơn, <b>cảm biến DHT22 có giới hạn phần cứng: tần số lấy mẫu tối đa là 0.5Hz (2 giây/lần)</b>. Nếu đọc DHT22 quá nhanh (dưới 2 giây), cảm biến sẽ bị tự sinh nhiệt làm sai số và hàm sẽ trả về giá trị lỗi <code>NaN</code> (Not a Number)! Chu kỳ 5 giây là khoảng cách an toàn lý tưởng.<br/>"
        "3. <b>Lúc mới bắt đầu chạy:</b> Vì biến <code>lastMQ2Time = 0</code>, nên ngay khi vào <code>loop()</code> lần đầu tiên (khi <code>now = 1000ms</code> chẳng hạn), biểu thức <code>now - lastMQ2Time &gt;= 2000</code> chưa thỏa, hệ thống sẽ chạy vòng lặp cực nhanh để kết nối mạng trước, sau đúng 2000ms đầu tiên nó mới đọc và in chu kỳ đo thứ nhất."
    ))

    # --------------------------------------------------------------------------
    # CHƯƠNG 3: BỘ CÂU HỎI VẶN VẸO CỦA GIẢNG VIÊN & ĐÁP ÁN ĐỈNH CAO
    # --------------------------------------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph("3. TỔNG HỢP 7 CÂU HỎI 'VẶN VẸO' KINH ĐIỂN CỦA GIẢNG VIÊN VÀ ĐÁP ÁN CHUẨN XÁC", h1_style))
    story.append(Paragraph(
        "Đây là các câu hỏi đào sâu về bản chất hệ thống mà các Thầy Cô trong Hội đồng chấm thi rất hay sử dụng để kiểm tra "
        "xem sinh viên tự viết code và thực sự hiểu sâu hay chỉ sao chép trên mạng:",
        body_style
    ))
    story.append(Spacer(1, 4))

    qa_list = [
        (
            "Câu hỏi 1: 'Hàm millis() trả về cái gì? Nếu hệ thống cắm điện chạy liên tục nhiều tháng thì hàm millis() có bị tràn số không? Lúc đó phép trừ (now - lastTime >= interval) có còn chạy đúng không?'",
            "<b>Đáp án chuẩn:</b><br/>"
            "• Hàm <code>millis()</code> trả về số mili-giây kể từ lúc vi điều khiển ESP32 bắt đầu khởi động, lưu trong kiểu dữ liệu số nguyên không dấu 32-bit (<code>unsigned long</code>).<br/>"
            "• <b>Hiện tượng tràn số (Roll-over):</b> Giá trị cực đại của <code>unsigned long</code> là 2^32 - 1 = 4.294.967.295 ms (tương đương khoảng <b>49.71 ngày</b>). Sau thời điểm này, biến sẽ tràn và quay ngược về số 0.<br/>"
            "• <b>Vẫn chạy đúng 100% nhờ toán học số bù hai (Two's complement):</b> Khi dùng phép trừ không dấu <code>(now - lastTime)</code>, ví dụ sau khi tràn: <code>now = 100</code> và <code>lastTime = 4.294.967.000</code>, phép trừ trong C vẫn cho kết quả chính xác tuyệt đối là khoảng chênh lệch thời gian thực tế mà không hề bị lỗi! Đây là lý do bắt buộc phải dùng <code>unsigned long</code> chứ không được dùng <code>signed long</code> hay <code>int</code>."
        ),
        (
            "Câu hỏi 2: 'Dòng tone(PIN_BUZZER, 800) nghĩa là gì? Con số 800 là cái gì? Tại sao không dùng digitalWrite(PIN_BUZZER, HIGH) bình thường?'",
            "<b>Đáp án chuẩn:</b><br/>"
            "• <b>Con số 800 là tần số âm thanh (800 Hz):</b> Tức là phát ra sóng vuông dao động 800 lần mỗi giây.<br/>"
            "• <b>Lý do kỹ thuật:</b> Còi báo trong mô hình là còi thụ động (Passive Buzzer). Nếu chỉ dùng <code>digitalWrite(HIGH)</code>, còi thụ động chỉ phát ra một tiếng 'tách' nhỏ rồi im lặng vì màng loa không dao động. Hàm <code>tone(pin, 800)</code> xuất xung PWM với tần số 800Hz — đây là dải tần số âm thanh đanh, chói tai nhất của tai người, đạt chuẩn quốc tế NFPA về còi báo cháy khẩn cấp."
        ),
        (
            "Câu hỏi 3: 'Tại sao lại dùng PubSubClient mà phải setBufferSize(512)? Mặc định của nó là bao nhiêu?'",
            "<b>Đáp án chuẩn:</b><br/>"
            "• Mặc định của thư viện PubSubClient chỉ có bộ đệm gói tin <b>128 bytes</b> (<code>MQTT_MAX_PACKET_SIZE = 128</code>).<br/>"
            "• Trong hệ thống của nhóm, gói tin JSON Telemetry hoặc gói tin Báo động khẩn cấp chứa nhiều trường dữ liệu (device_id, PPM, nhiệt độ, độ ẩm, trạng thái quạt còi, thông điệp tiếng Việt không dấu) có độ dài lên tới 180 – 220 bytes.<br/>"
            "• Nếu không có dòng lệnh <code>mqttClient.setBufferSize(512)</code> ở dòng 464, hàm <code>publish()</code> sẽ âm thầm trả về <code>false</code> và Broker sẽ hoàn toàn không nhận được gói tin!"
        ),
        (
            "Câu hỏi 4: 'Tại sao Client ID lại phải sinh chuỗi ngẫu nhiên random(0xffff) mà không đặt cố định một tên?'",
            "<b>Đáp án chuẩn:</b><br/>"
            "• Theo đặc tả chuẩn của giao thức MQTT, Broker không cho phép 2 Client có cùng một Client ID kết nối đồng thời. Nếu một thiết bị thứ hai đăng nhập trùng Client ID, Broker sẽ tự động ngắt kết nối (Kick) thiết bị thứ nhất.<br/>"
            "• Vì nhóm sử dụng Broker công cộng <code>broker.emqx.io</code>, nếu đặt tên cố định thì rất dễ trùng với sinh viên nhóm khác hoặc khi bạn mở thêm công cụ kiểm thử, hai bên sẽ 'đá' nhau liên tục gây rớt mạng. Việc ghép thêm 4 ký tự HEX ngẫu nhiên đảm bảo tính duy nhất toàn cầu (Globally Unique)."
        ),
        (
            "Câu hỏi 5: 'Tại sao khi đọc MQ-2 lại lấy mẫu trung bình 10 lần và delayMicroseconds(200)?'",
            "<b>Đáp án chuẩn:</b><br/>"
            "• Bộ ADC của vi điều khiển ESP32 vốn có đặc tính phi tuyến và độ nhiễu điện áp nội tại (ADC noise) khá cao.<br/>"
            "• Việc đọc lấy mẫu trung bình 10 lần giúp triệt tiêu các gai nhiễu tức thời (Spike noise).<br/>"
            "• Khoảng cách 200 micro-giây giữa các lần đọc là thời gian tối thiểu để tụ nạp mẫu bên trong bộ chuyển đổi SAR-ADC của ESP32 (Sample and Hold capacitor) nạp đủ điện tích, cho kết quả đọc ổn định và chuẩn xác nhất."
        ),
        (
            "Câu hỏi 6: 'Nếu trong lúc đang Mute còi (180 giây), nồng độ khói tăng vọt từ 400 lên 800 PPM thì quạt có chạy không? Còi có hú lại không?'",
            "<b>Đáp án chuẩn:</b><br/>"
            "• <b>Quạt hút:</b> Vẫn chạy 100% công suất! Hàm <code>setFan(true)</code> độc lập hoàn toàn với cờ <code>isMuted</code>.<br/>"
            "• <b>Còi hú:</b> Còi vẫn giữ im lặng trong đúng 180 giây đó theo yêu cầu của đội cứu hộ để trao đổi liên lạc. Tuy nhiên, gói tin khẩn cấp <code>smoke/event/alarm</code> với mức độ <code>CRITICAL</code> và giá trị 800 PPM vẫn được bắn liên tục lên Broker để máy chủ ghi nhận. Ngay khi hết 180s, còi sẽ tự động hú vang trở lại!"
        ),
        (
            "Câu hỏi 7: 'Hàm loop() của bạn một giây chạy được bao nhiêu vòng? Làm sao biết nó không bị nghẽn?'",
            "<b>Đáp án chuẩn:</b><br/>"
            "• Vì toàn bộ mã nguồn không chứa bất kỳ lệnh <code>delay()</code> chặn nào, thời gian thực thi một vòng lặp <code>loop()</code> thông thường chỉ mất khoảng <b>2 đến 5 micro-giây</b> (khi không đến chu kỳ đọc cảm biến) và mất khoảng <b>3 mili-giây</b> (khi đến chu kỳ đọc MQ2 lấy 10 mẫu trung bình).<br/>"
            "• Như vậy, trung bình một giây vòng lặp <code>loop()</code> có thể chạy hàng trăm nghìn lần! Điều này đảm bảo nút nhấn vật lý và các gói tin MQTT Downlink đến từ Broker được tiếp nhận và xử lý gần như tức thời."
        )
    ]

    for q, a in qa_list:
        content_qa = []
        content_qa.append(Paragraph(q, question_style))
        content_qa.append(Paragraph(a, answer_style))
        story.append(KeepTogether(content_qa))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully generated: {pdf_path}")

if __name__ == "__main__":
    build_pdf()
