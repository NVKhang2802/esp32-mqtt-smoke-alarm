# -*- coding: utf-8 -*-
"""
scripts/generate_final_report.py
Tạo tài liệu Word Báo cáo Tổng kết Đồ án môn học IoT:
Nhom09_HeThongBaoKhoiCanhBaoSom.docx

Tuân thủ nghiêm ngặt 12 quy định định dạng từ người dùng:
1. Font Times New Roman 13pt (body), 11pt (captions bold not italic), 16pt (chapter headings bold sentence case).
   Tiêu đề cấp 2, 3, ... giữ cỡ chữ 13pt bold sentence case.
2. Bảng thường, không màu mè sặc sỡ, header in đậm căn giữa, ô số/trạng thái căn giữa, ô chữ căn đều/trái.
3. Tiêu đề chỉ in đậm và viết hoa đầu câu (Sentence case), không in nghiêng, không in hoa toàn bộ.
4. Mục lục, danh mục hình ảnh và bảng tự động bằng trường Word Field XML chuẩn.
5. Tài liệu tham khảo đánh số theo thứ tự xuất hiện [1]..[10] và chèn vào cuối câu/đoạn tương ứng.
6. Xác lập 1 style chuẩn ngay từ đầu.
7. Màu chữ 100% màu đen (#000000).
8. Hình ảnh có viền đen bao quanh.
9. Chỉ dùng dấu gạch ngang ngắn '-' (không dùng en-dash hay em-dash).
10. Văn phong trôi chảy, thuận miệng, thuật ngữ kỹ thuật chính xác, không dùng văn phong AI.
11. Đánh số trang: Trang bìa không số, phần đầu số La Mã (i, ii..), từ 'Tổng quan đề tài' đánh số Ả Rập bắt đầu từ 1.
12. 100% đoạn văn bản căn đều hai bên (Justified).
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

FONT_NAME = "Times New Roman"
SIZE_BODY = 13
SIZE_CHAPTER = 16
SIZE_HEADING = 13
SIZE_CAPTION = 11
COLOR_BLACK = RGBColor(0, 0, 0)
OUTPUT_PATH = os.path.join("docs", "word", "Nhom09_HeThongBaoKhoiCanhBaoSom.docx")

def clean_hyphens(text):
    """Thay thế triệt để dấu gạch ngang dài thành dấu gạch ngang ngắn '-' và toán tử so sánh chuẩn toán học"""
    if not text:
        return ""
    return text.replace("–", "-").replace("—", "-").replace("−", "-").replace(">=", "≥").replace("<=", "≤")

OMML_NS = 'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"'

def add_display_equation(doc, omml_inner_xml, space_before=4, space_after=6):
    """Chèn phương trình toán học hiển thị độc lập (Word Equation Alt +=) căn giữa trang"""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.keep_with_next = False
    eq_xml = f'<m:oMathPara {OMML_NS}><m:oMath>{omml_inner_xml}</m:oMath></m:oMathPara>'
    p._p.append(parse_xml(eq_xml))
    return p

def add_inline_math(paragraph, omml_inner_xml):
    """Chèn ký hiệu hoặc biểu thức toán học nội dòng (Inline Math) chuẩn Word Equation"""
    math_xml = f'<m:oMath {OMML_NS}>{omml_inner_xml}</m:oMath>'
    paragraph._p.append(parse_xml(math_xml))

def set_run_font(run, size=SIZE_BODY, bold=False, italic=False):
    run.font.name = FONT_NAME
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = COLOR_BLACK

def add_p(doc, text="", style="Normal", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=4, line_spacing=1.25):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    if text:
        run = p.add_run(clean_hyphens(text))
        set_run_font(run, size=SIZE_BODY, bold=False, italic=False)
    return p

def configure_heading_styles(doc):
    """Thiết lập các kiểu Heading 1, Heading 2, Heading 3 và Caption chuẩn kỹ thuật"""
    for lvl in [1, 2, 3]:
        st_name = f"Heading {lvl}"
        try:
            st = doc.styles[st_name]
        except KeyError:
            st = doc.styles.add_style(st_name, docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
        st.font.name = FONT_NAME
        st.font.color.rgb = COLOR_BLACK
        st.font.bold = True
        st.font.italic = False
        st.font.size = Pt(SIZE_CHAPTER if lvl == 1 else SIZE_HEADING)
    
    try:
        c_st = doc.styles['Caption']
    except KeyError:
        c_st = doc.styles.add_style('Caption', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
    c_st.font.name = FONT_NAME
    c_st.font.color.rgb = COLOR_BLACK
    c_st.font.bold = True
    c_st.font.italic = False
    c_st.font.size = Pt(SIZE_CAPTION)

def add_heading_1(doc, text):
    """Tiêu đề cấp 1: Cỡ 16pt, in đậm, viết hoa đầu câu, màu đen, không in nghiêng, không in hoa toàn bộ"""
    p = doc.add_paragraph(style="Heading 1")
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    pPr = p._p.get_or_add_pPr()
    pPr.append(parse_xml(r'<w:outlineLvl %s w:val="0"/>' % nsdecls("w")))
    
    p.text = ""
    run = p.add_run(clean_hyphens(text))
    set_run_font(run, size=SIZE_CHAPTER, bold=True, italic=False)
    return p

def add_heading_2(doc, text):
    """Tiêu đề cấp 2: Cỡ 13pt, in đậm, viết hoa đầu câu, màu đen, không in nghiêng"""
    p = doc.add_paragraph(style="Heading 2")
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    pPr = p._p.get_or_add_pPr()
    pPr.append(parse_xml(r'<w:outlineLvl %s w:val="1"/>' % nsdecls("w")))
    
    p.text = ""
    run = p.add_run(clean_hyphens(text))
    set_run_font(run, size=SIZE_HEADING, bold=True, italic=False)
    return p

def add_heading_3(doc, text):
    """Tiêu đề cấp 3: Cỡ 13pt, in đậm, viết hoa đầu câu, màu đen, không in nghiêng"""
    p = doc.add_paragraph(style="Heading 3")
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    pPr = p._p.get_or_add_pPr()
    pPr.append(parse_xml(r'<w:outlineLvl %s w:val="2"/>' % nsdecls("w")))
    
    p.text = ""
    run = p.add_run(clean_hyphens(text))
    set_run_font(run, size=SIZE_HEADING, bold=True, italic=False)
    return p

def add_caption_image(doc, text):
    """Caption hình ảnh: Cỡ 11pt, in đậm, KHÔNG in nghiêng, căn giữa, màu đen, kèm trường SEQ Hình"""
    p = doc.add_paragraph(style='Caption')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(8)
    p.text = ""
    
    text = clean_hyphens(text)
    import re
    m = re.match(r'^(Hình\s+)(\d+(?:\.\d+)*)([\.\:\s\-]+)(.*)$', text)
    if m:
        prefix = m.group(1)
        seq_val = m.group(2)
        sep = m.group(3)
        title = m.group(4)
        
        r1 = p.add_run(prefix)
        set_run_font(r1, size=SIZE_CAPTION, bold=True, italic=False)
        
        fld = parse_xml(r'<w:fldSimple %s w:instr="SEQ Hình \* ARABIC"><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:b/><w:sz w:val="22"/><w:color w:val="000000"/></w:rPr><w:t>%s</w:t></w:r></w:fldSimple>' % (nsdecls("w"), seq_val))
        p._p.append(fld)
        
        r2 = p.add_run(sep + title)
        set_run_font(r2, size=SIZE_CAPTION, bold=True, italic=False)
    else:
        run = p.add_run(text)
        set_run_font(run, size=SIZE_CAPTION, bold=True, italic=False)
    return p

def add_caption_table(doc, text):
    """Caption bảng: Cỡ 11pt, in đậm, KHÔNG in nghiêng, căn giữa, màu đen, đặt TRƯỚC bảng, kèm trường SEQ Bảng"""
    p = doc.add_paragraph(style='Caption')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    p.text = ""
    
    text = clean_hyphens(text)
    import re
    m = re.match(r'^(Bảng\s+)(\d+(?:\.\d+)*)([\.\:\s\-]+)(.*)$', text)
    if m:
        prefix = m.group(1)
        seq_val = m.group(2)
        sep = m.group(3)
        title = m.group(4)
        
        r1 = p.add_run(prefix)
        set_run_font(r1, size=SIZE_CAPTION, bold=True, italic=False)
        
        fld = parse_xml(r'<w:fldSimple %s w:instr="SEQ Bảng \* ARABIC"><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:b/><w:sz w:val="22"/><w:color w:val="000000"/></w:rPr><w:t>%s</w:t></w:r></w:fldSimple>' % (nsdecls("w"), seq_val))
        p._p.append(fld)
        
        r2 = p.add_run(sep + title)
        set_run_font(r2, size=SIZE_CAPTION, bold=True, italic=False)
    else:
        run = p.add_run(text)
        set_run_font(run, size=SIZE_CAPTION, bold=True, italic=False)
    return p

def insert_image_with_border(doc, img_path, width_inches=5.8, caption_text=""):
    """Chèn hình ảnh có viền đen bao quanh và caption in đậm không nghiêng bên dưới"""
    if not os.path.exists(img_path):
        print(f"Warning: Image {img_path} not found!")
        return None
    
    # Tạo bảng 1 ô căn giữa để tạo khung viền đen chắc chắn 100%
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    
    # Thiết lập viền đen đơn nét (solid black border 1pt = sz 8)
    tblPr = tbl._tbl.tblPr
    borders = parse_xml(
        '<w:tblBorders %s>'
        '<w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        '<w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        '<w:left w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        '<w:right w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        '</w:tblBorders>' % nsdecls("w")
    )
    tblPr.append(borders)
    
    # Thiết lập đệm trong ô
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        '<w:tcMar %s>'
        '<w:top w:w="80" w:type="dxa"/>'
        '<w:bottom w:w="80" w:type="dxa"/>'
        '<w:left w:w="80" w:type="dxa"/>'
        '<w:right w:w="80" w:type="dxa"/>'
        '</w:tcMar>' % nsdecls("w")
    )
    tcPr.append(tcMar)
    
    cp = cell.paragraphs[0]
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp.paragraph_format.space_before = Pt(2)
    cp.paragraph_format.space_after = Pt(2)
    run = cp.add_run()
    run.add_picture(img_path, width=Inches(width_inches))
    
    # Thêm caption phía dưới
    if caption_text:
        add_caption_image(doc, caption_text)
    
    return tbl

def insert_standard_table(doc, headers, rows_data, col_alignments=None, caption_text=""):
    """
    Tạo bảng thường chuẩn chuyên nghiệp:
    - Caption đặt phía trên
    - Header in đậm, căn giữa, nền xám nhẹ thanh lịch #F2F2F2
    - Ô số/STT căn giữa, ô văn bản căn đều/trái
    - Viền đen đơn nét mỏng 0.5pt
    """
    if caption_text:
        add_caption_table(doc, caption_text)
        
    num_rows = len(rows_data) + 1
    num_cols = len(headers)
    table = doc.add_table(rows=num_rows, cols=num_cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Thiết lập viền đen mảnh cho toàn bộ bảng
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        '<w:tblBorders %s>'
        '<w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '<w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '<w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '</w:tblBorders>' % nsdecls("w")
    )
    tblPr.append(borders)
    
    # Định dạng Header
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        cell = hdr_cells[i]
        tcPr = cell._tc.get_or_add_tcPr()
        # Nền xám rất nhẹ tiêu chuẩn cho header
        shd = parse_xml('<w:shd %s w:fill="F2F2F2"/>' % nsdecls("w"))
        tcPr.append(shd)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(clean_hyphens(title))
        set_run_font(run, size=11.5, bold=True, italic=False)
        
    # Định dạng Data
    for r_idx, row in enumerate(rows_data):
        row_cells = table.rows[r_idx + 1].cells
        is_group_header = (row[0] in ['I', 'II', 'III', 'IV', '★'] or 'KHỐI ' in str(row[1]) or 'TỔNG ' in str(row[1]))
        for c_idx, val in enumerate(row):
            cell = row_cells[c_idx]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            
            # Canh lề cột: Căn giữa nếu là số/STT hoặc chỉ định rõ
            align = WD_ALIGN_PARAGRAPH.JUSTIFY
            if col_alignments and c_idx < len(col_alignments):
                align = col_alignments[c_idx]
            elif c_idx == 0 or len(str(val)) <= 8:
                align = WD_ALIGN_PARAGRAPH.CENTER
                
            p.alignment = align
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(clean_hyphens(str(val)))
            set_run_font(run, size=11, bold=is_group_header, italic=False)
            
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return table

def add_word_field(p, field_code, placeholder_text=""):
    """Chèn trường mã Word Field tự động (TOC, TOT, TOF)"""
    run = p.add_run()
    fld1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
    instr = parse_xml(r'<w:instrText %s xml:space="preserve"> %s </w:instrText>' % (nsdecls('w'), field_code))
    fld2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
    fld3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
    run._r.append(fld1)
    run._r.append(instr)
    run._r.append(fld2)
    if placeholder_text:
        r_text = parse_xml(r'<w:r %s><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="24"/><w:color w:val="000000"/></w:rPr><w:t>%s</w:t></w:r>' % (nsdecls('w'), clean_hyphens(placeholder_text)))
        run._r.append(r_text)
    run._r.append(fld3)

def add_page_number_to_footer(footer, num_format="decimal", start_num=None):
    """Thiết lập footer đánh số trang ở giữa trang"""
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.text = ""
    run = p.add_run()
    
    # Trường PAGE
    fldSimple = parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls('w'))
    p._p.append(fldSimple)
    for r in p.runs:
        set_run_font(r, size=11, bold=False, italic=False)

def build_report():
    print("=" * 75)
    print("  KHOI TAO QUA TRINH XUAT BAN BAO CAO FINAL - NHOM 09 HUIT")
    print("=" * 75)
    
    doc = docx.Document()
    configure_heading_styles(doc)
    
    # =========================================================================
    # SECTION 1: TRANG BÌA (COVER PAGE - KHÔNG SỐ TRANG)
    # =========================================================================
    s1 = doc.sections[0]
    s1.top_margin = Inches(0.8)
    s1.bottom_margin = Inches(0.8)
    s1.left_margin = Inches(1.18)   # 3 cm
    s1.right_margin = Inches(0.79)  # 2 cm
    s1.header.is_linked_to_previous = False
    s1.footer.is_linked_to_previous = False
    
    p = add_p(doc, "BỘ CÔNG THƯƠNG", align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    p.runs[0].font.size = Pt(13)
    p.runs[0].bold = True
    
    p = add_p(doc, "TRƯỜNG ĐẠI HỌC CÔNG THƯƠNG TP. HỒ CHÍ MINH (HUIT)", align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    p.runs[0].font.size = Pt(13)
    p.runs[0].bold = True
    
    p = add_p(doc, "KHOA CÔNG NGHỆ THÔNG TIN", align=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)
    p.runs[0].font.size = Pt(13)
    p.runs[0].bold = True
    
    # Khung viền biểu tượng hoặc đường kẻ
    p = add_p(doc, "------------------------------------------------------------", align=WD_ALIGN_PARAGRAPH.CENTER, space_after=36)
    
    p = add_p(doc, "BÁO CÁO TỔNG KẾT ĐỒ ÁN HỌC PHẦN", align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)
    p.runs[0].font.size = Pt(16)
    p.runs[0].bold = True
    
    p = add_p(doc, "MÔN HỌC: INTERNET OF THINGS (IoT)", align=WD_ALIGN_PARAGRAPH.CENTER, space_after=24)
    p.runs[0].font.size = Pt(15)
    p.runs[0].bold = True
    
    p = add_p(doc, "ĐỀ TÀI: HỆ THỐNG BÁO KHÓI CẢNH BÁO SỚM", align=WD_ALIGN_PARAGRAPH.CENTER, space_after=40)
    p.runs[0].font.size = Pt(18)
    p.runs[0].bold = True
    
    p = add_p(doc, "GIẢNG VIÊN HƯỚNG DẪN: ThS. VÕ HOÀNG HẢI", align=WD_ALIGN_PARAGRAPH.CENTER, space_after=28)
    p.runs[0].font.size = Pt(13)
    p.runs[0].bold = True
    
    p = add_p(doc, "NHÓM SINH VIÊN THỰC HIỆN: NHÓM 09", align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
    p.runs[0].font.size = Pt(13)
    p.runs[0].bold = True
    
    add_p(doc, "1. Nguyễn Vĩnh Khang   -   MSSV: 2001230381   (Trưởng nhóm)", align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    add_p(doc, "2. Nguyễn Văn Đức       -   MSSV: 2001230186   (Thành viên)", align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    add_p(doc, "3. Nguyễn Văn Mãnh      -   MSSV: 2001230503   (Thành viên)", align=WD_ALIGN_PARAGRAPH.CENTER, space_after=60)
    
    p = add_p(doc, "TP. HỒ CHÍ MINH, THÁNG 11 NĂM 2026", align=WD_ALIGN_PARAGRAPH.CENTER, space_after=0)
    p.runs[0].font.size = Pt(12)
    p.runs[0].bold = True

    # =========================================================================
    # SECTION 2: PHẦN ĐẦU (PRELIMS - ĐÁNH SỐ LA MÃ i, ii, iii...)
    # =========================================================================
    s2 = doc.add_section()
    s2.top_margin = Inches(0.79)   # 2 cm
    s2.bottom_margin = Inches(0.79)# 2 cm
    s2.left_margin = Inches(1.18)  # 3 cm
    s2.right_margin = Inches(0.79) # 2 cm
    s2.header.is_linked_to_previous = False
    s2.footer.is_linked_to_previous = False
    
    # Đặt số trang La Mã thường i, ii, iii...
    for pgn in s2._sectPr.findall(qn("w:pgNumType")):
        s2._sectPr.remove(pgn)
    p_num2 = parse_xml('<w:pgNumType %s w:fmt="lowerRoman" w:start="1"/>' % nsdecls("w"))
    s2._sectPr.append(p_num2)
    add_page_number_to_footer(s2.footer)
    
    # ---------------- Lời cam đoan ----------------
    add_heading_1(doc, "Lời cam đoan")
    add_p(doc, "Chúng em xin cam đoan rằng toàn bộ nội dung, mã nguồn và kết quả thực nghiệm được trình bày trong cuốn báo cáo đồ án này là công trình nghiên cứu và phát triển hoàn toàn trung thực của Nhóm 09 dưới sự hướng dẫn trực tiếp của ThS. Võ Hoàng Hải.")
    add_p(doc, "Tất cả các số liệu đo lường từ cảm biến, giải thuật bộ lọc số EMA, máy trạng thái hữu hạn FSM, luồng xử lý Node-RED, cơ chế phân quyền Web SCADA và các gói tin truyền thông MQTT đều được xây dựng, kiểm thử và đối chiếu thực tế trên mã nguồn thực của dự án. Các tài liệu tham khảo, phần mềm mã nguồn mở và thư viện dùng chung đều được trích dẫn nguồn gốc rõ ràng theo đúng chuẩn mực học thuật.")
    
    add_p(doc, "TP. Hồ Chí Minh, ngày 20 tháng 11 năm 2026", align=WD_ALIGN_PARAGRAPH.RIGHT, space_before=12, space_after=18)
    p_sign = add_p(doc, "Đại diện Nhóm 09\n\n\n\nNguyễn Vĩnh Khang (Trưởng nhóm)", align=WD_ALIGN_PARAGRAPH.RIGHT)
    p_sign.runs[0].bold = True
    
    doc.add_page_break()
    
    # ---------------- Lời cảm ơn ----------------
    add_heading_1(doc, "Lời cảm ơn")
    add_p(doc, "Để hoàn thành đồ án học phần môn học Internet of Things (IoT), nhóm chúng em xin được gửi lời cảm ơn chân thành và sâu sắc nhất tới Ban Giám hiệu Trường Đại học Công Thương TP. Hồ Chí Minh (HUIT), Ban Chủ nhiệm Khoa Công nghệ Thông tin đã tạo môi trường học tập và nghiên cứu thực nghiệm thuận lợi cho sinh viên.")
    add_p(doc, "Đặc biệt, nhóm chúng em xin bày tỏ lòng biết ơn sâu sắc tới ThS. Võ Hoàng Hải - Giảng viên trực tiếp giảng dạy và tận tình hướng dẫn nhóm trong suốt 10 tuần học phần. Thầy đã định hướng kiến trúc chuẩn 4 tầng IoT, xây dựng kế hoạch thực hiện 60 giờ kỹ thuật bài bản và đưa ra những lời góp ý chuyên môn vô cùng quý báu, giúp nhóm rèn luyện tư duy kỹ thuật hệ thống, khả năng lập trình vi điều khiển non-blocking và hoàn thiện toàn diện sản phẩm.")
    add_p(doc, "Mặc dù nhóm đã nỗ lực hết mình để tối ưu hóa hệ thống cả về phần cứng, giao thức mạng, middleware và giao diện điều khiển, nhưng đồ án khó tránh khỏi những thiếu sót nhất định. Nhóm rất mong nhận được những nhận xét, đóng góp quý báu từ quý Thầy Cô trong Hội đồng để sản phẩm ngày càng hoàn thiện hơn.")
    
    doc.add_page_break()
    
    # ---------------- Mục lục tự động ----------------
    add_heading_1(doc, "Mục lục")
    p_toc = doc.add_paragraph()
    p_toc.paragraph_format.space_after = Pt(12)
    add_word_field(p_toc, r'TOC \o "1-3" \h \z \u', '[Nhấn chuột phải chọn "Update Field" (hoặc nhấn phím F9) để cập nhật Mục lục tự động]')
    
    doc.add_page_break()
    
    # ---------------- Danh mục bảng biểu tự động ----------------
    add_heading_1(doc, "Danh mục bảng biểu")
    p_tot = doc.add_paragraph()
    p_tot.paragraph_format.space_after = Pt(12)
    add_word_field(p_tot, r'TOC \h \z \c "Bảng"', '[Nhấn chuột phải chọn "Update Field" (hoặc nhấn phím F9) để cập nhật Danh mục bảng biểu tự động]')
    
    doc.add_page_break()
    
    # ---------------- Danh mục hình ảnh tự động ----------------
    add_heading_1(doc, "Danh mục hình ảnh")
    p_tof = doc.add_paragraph()
    p_tof.paragraph_format.space_after = Pt(12)
    add_word_field(p_tof, r'TOC \h \z \c "Hình"', '[Nhấn chuột phải chọn "Update Field" (hoặc nhấn phím F9) để cập nhật Danh mục hình ảnh tự động]')
    
    doc.add_page_break()
    
    # ---------------- Danh mục thuật ngữ & Ký hiệu viết tắt ----------------
    add_heading_1(doc, "Danh mục từ viết tắt")
    abbr_headers = ["Từ viết tắt", "Tên tiếng Anh đầy đủ", "Ý nghĩa chuyên môn trong đề tài"]
    abbr_data = [
        ["IoT", "Internet of Things", "Mạng lưới vạn vật kết nối Internet"],
        ["FSM", "Finite State Machine", "Máy trạng thái hữu hạn điều khiển chu trình"],
        ["EMA", "Exponential Moving Average", "Bộ lọc trung bình động hàm mũ khử nhiễu ADC"],
        ["SCADA", "Supervisory Control and Data Acquisition", "Hệ thống giám sát, thu thập và điều khiển dữ liệu"],
        ["MQTT", "Message Queuing Telemetry Transport", "Giao thức truyền thông điệp nhẹ cho IoT [5]"],
        ["QoS", "Quality of Service", "Cấp độ chất lượng dịch vụ truyền tin MQTT"],
        ["LWT", "Last Will and Testament", "Thông điệp di chúc khi thiết bị đột tử"],
        ["RBAC", "Role-Based Access Control", "Hệ thống kiểm soát truy cập dựa trên vai trò"],
        ["ADC", "Analog-to-Digital Converter", "Bộ chuyển đổi tín hiệu tương tự sang số"],
        ["GPIO", "General Purpose Input/Output", "Chân giao tiếp vào/ra đa dụng của vi điều khiển"],
        ["PPM", "Parts Per Million", "Đơn vị đo nồng độ thể tích một phần triệu"],
        ["PWM", "Pulse Width Modulation", "Điều chế độ rộng xung điều khiển âm còi"],
        ["RAII", "Resource Acquisition Is Initialization", "Nguyên tắc quản lý bộ nhớ heap an toàn"]
    ]
    insert_standard_table(doc, abbr_headers, abbr_data, [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.JUSTIFY], caption_text="Bảng danh mục các từ viết tắt sử dụng trong báo cáo")

    # =========================================================================
    # SECTION 3: THÂN BÀI CHÍNH (ĐÁNH SỐ Ả RẬP 1, 2, 3... TỪ TỔNG QUAN ĐỀ TÀI)
    # =========================================================================
    s3 = doc.add_section()
    s3.top_margin = Inches(0.79)   # 2 cm
    s3.bottom_margin = Inches(0.79)# 2 cm
    s3.left_margin = Inches(1.18)  # 3 cm
    s3.right_margin = Inches(0.79) # 2 cm
    s3.header.is_linked_to_previous = False
    s3.footer.is_linked_to_previous = False
    
    # Bắt đầu đánh số Ả Rập 1, 2, 3...
    for pgn in s3._sectPr.findall(qn("w:pgNumType")):
        s3._sectPr.remove(pgn)
    p_num3 = parse_xml('<w:pgNumType %s w:fmt="decimal" w:start="1"/>' % nsdecls("w"))
    s3._sectPr.append(p_num3)
    add_page_number_to_footer(s3.footer)

    # ---------------- TỔNG QUAN ĐỀ TÀI (THAY CHO LỜI MỞ ĐẦU) ----------------
    add_heading_1(doc, "Tổng quan đề tài")
    
    add_heading_2(doc, "1. Thực trạng vấn đề")
    add_p(doc, "Trong những năm gần đây, tình hình sự cố cháy nổ tại các khu dân cư, nhà xưởng và chung cư cao tầng diễn biến hết sức phức tạp, gây thiệt hại nghiêm trọng về tính mạng con người và tài sản [1]. Theo các nghiên cứu thống kê về an toàn phòng cháy chữa cháy (PCCC), nguyên nhân tử vong hàng đầu trong các vụ hỏa hoạn không phải do bỏng nhiệt mà là do ngạt khói độc chứa carbon monoxide (CO) và các khí cháy sinh ra trong giai đoạn cháy âm ỉ ban đầu [3]. Các hệ thống báo cháy truyền thống thường có nhược điểm lớn: phát hiện chậm trễ khi khói đã bao trùm diện rộng, thiếu khả năng cảnh báo sớm từ xa, không có cơ chế tự động thông gió hút khói tại chỗ và không hỗ trợ giám sát trực quan tập trung cho người quản lý [4].")
    
    add_heading_2(doc, "2. Mục tiêu nghiên cứu")
    add_p(doc, "Mục tiêu trọng tâm của đề tài là thiết kế và hiện thực hóa một 'Hệ thống Báo khói Cảnh báo sớm' chuẩn 4 tầng IoT, hướng tới việc giảm thiểu tối đa thời gian phát hiện đám cháy và tự động hóa cứu nạn khẩn cấp [1]. Cụ thể gồm các mục tiêu kỹ thuật:")
    add_p(doc, "- Phát hiện nồng độ khói vượt ngưỡng trong thời gian dưới 2 giây bằng cảm biến MQ-2 và đo lường nhiệt độ DHT22.")
    add_p(doc, "- Khử triệt để hiện tượng báo động giả do nhiễu xung điện lưới thông qua bộ lọc trung bình động số hàm mũ bất đối xứng (Asymmetric EMA).")
    add_p(doc, "- Tự động kích hoạt cơ cấu chấp hành tại chỗ: đóng rơ-le quạt hút thông gió và hú còi PWM cảnh báo theo máy trạng thái hữu hạn FSM 5 trạng thái.")
    add_p(doc, "- Bảo đảm nguyên tắc Khóa an toàn PCCC (Safety Interlock): cấm tuyệt đối mọi hành vi ngắt quạt hút từ xa trong khi đang có báo động cháy.")
    add_p(doc, "- Tự động hóa điều phối liên vùng trên tầng middleware Node-RED: khi phát hiện cháy lớn (> 600 PPM) lập tức phát lệnh sơ tán toàn bộ các phòng lân cận cùng tầng [7].")
    add_p(doc, "- Cung cấp ứng dụng giám sát Web SCADA trực quan và trạm kiểm soát MQTTX Desktop, hỗ trợ phân quyền người dùng RBAC (Viewer/Admin) và ghi nhật ký kiểm toán an toàn chống tấn công XSS.")

    add_heading_2(doc, "3. Phạm vi nghiên cứu")
    add_p(doc, "Đề tài được triển khai và hoàn thiện trong khuôn khổ 10 tuần học phần (tương đương 60 giờ làm việc kỹ thuật) theo đúng quy chuẩn nghiệm thu của Bộ môn IoT - Khoa Công nghệ Thông tin, Trường Đại học Công Thương TP.HCM [1]. Phạm vi hệ thống được xác định rõ ràng bao gồm:")
    add_p(doc, "- Tầng 1 (Sensing/Embedded): Mô phỏng mạch phần cứng hoàn chỉnh trên nền tảng Wokwi với vi điều khiển ESP32 DevKit V4, cảm biến khói MQ-2, cảm biến nhiệt ẩm DHT22, rơ-le điều khiển quạt DC và còi cảnh báo Buzzer [8, 9]. Mã nguồn firmware C++ được biên dịch qua PlatformIO.")
    add_p(doc, "- Tầng 2 (Network/Connectivity): Sử dụng giao thức mạng MQTT 3.1.1 qua kênh kết nối TCP (cổng 1883) và WebSocket bảo mật WSS (cổng 8084) trên máy chủ EMQX Cloud Broker với tiền tố định danh riêng Nhom09/smoke/... bảo đảm không xung đột dữ liệu [5].")
    add_p(doc, "- Tầng 3 (Middleware/Automation Engine): Dựng luồng điều phối 52 nodes trên Node-RED, xử lý 5 quy tắc nghiệp vụ PCCC (Rate-of-Rise, Low-Heat, Day/Night, Cooldown 30s, Cross-Zone) và giám sát nhịp tim Watchdog 30s [7].")
    add_p(doc, "- Tầng 4 (Application): Xây dựng Web SCADA độc lập phục vụ điều hành và ứng dụng MQTTX Desktop phục vụ kiểm định gói tin.")

    # ---------------- CHƯƠNG 1 ----------------
    add_heading_1(doc, "Chương 1. Phân tích bài toán và đặc tả yêu cầu")
    
    add_heading_2(doc, "1.1. Bối cảnh thực tế và yêu cầu cấp thiết")
    add_p(doc, "Trong các công trình xây dựng hiện đại, hệ thống báo khói đóng vai trò là tuyến phòng thủ đầu tiên bảo vệ tính mạng con người [3]. Tuy nhiên, thực tế vận hành cho thấy nhiều hệ thống báo cháy gặp phải tình trạng báo động giả thường xuyên do bụi bẩn, hơi nước nấu ăn hoặc xung nhiễu điện áp, dẫn đến tâm lý chủ quan ngắt nguồn thiết bị của người dân. Ngược lại, khi có sự cố cháy âm ỉ xảy ra vào ban đêm, hệ thống lại phản ứng quá chậm chạp, khiến nạn nhân hít phải lượng lớn khí độc trước khi còi báo động kịp phát tín hiệu. Do đó, việc xây dựng một hệ thống IoT có khả năng thích ứng độ nhạy ngày/đêm, lọc nhiễu số chính xác và tự động hóa cứu nạn là một đòi hỏi cấp bách từ thực tiễn [1].")

    add_heading_2(doc, "1.2. Khảo sát hiện trạng và các giải pháp tương tự")
    add_p(doc, "Các giải pháp báo cháy độc lập trên thị trường hiện nay thường chỉ có chức năng phát âm thanh tại chỗ, không có kết nối mạng để truyền tin về trung tâm điều hành. Một số thiết bị có Wi-Fi thương mại thì hoạt động phụ thuộc hoàn toàn vào dịch vụ đám mây nước ngoài (Tuya, eWeLink), gây ra độ trễ cao và tiềm ẩn nguy cơ gián đoạn hoạt động khi mất kết nối Internet quốc tế [2]. Đề tài của nhóm khắc phục triệt để các hạn chế này bằng kiến trúc Edge-First: thiết bị biên ESP32 tự ra quyết định độc lập tại chỗ, kết hợp đám mây nội bộ để giám sát đa điểm.")

    add_heading_2(doc, "1.3. Đối tượng sử dụng và phạm vi đề tài")
    add_p(doc, "Hệ thống hướng tới hai nhóm đối tượng sử dụng chính:")
    add_p(doc, "1. Cư dân trong tòa nhà: Theo dõi các chỉ số môi trường (nồng độ khói, nhiệt độ, độ ẩm) trong phòng của mình, nhận cảnh báo sớm qua chuông còi và hướng dẫn sơ tán an toàn.")
    add_p(doc, "2. Ban quản lý và nhân viên vận hành PCCC: Theo dõi bản đồ trạng thái toàn bộ các phòng trên Web SCADA, điều khiển thông gió từ xa, nhận báo cáo kiểm toán và tiếp nhận cảnh báo khẩn cấp tức thời.")

    add_heading_2(doc, "1.4. Đặc tả yêu cầu chức năng (Use Cases)")
    add_p(doc, "Hệ thống được thiết kế đáp ứng đầy đủ 7 Use Cases nghiệp vụ trọng tâm:")
    
    uc_headers = ["Mã Use Case", "Tên Use Case", "Mô tả tóm tắt", "Tác nhân chính", "Độ ưu tiên"]
    uc_data = [
        ["UC01", "Đo lường nồng độ khói", "Thu thập tín hiệu ADC từ MQ-2, tính điện trở cảm biến Rs và nồng độ PPM", "ESP32", "Bắt buộc"],
        ["UC02", "Giám sát nhiệt độ và độ ẩm", "Đọc tín hiệu số từ DHT22 chu kỳ 2 giây, phát hiện quá nhiệt > 50°C", "ESP32", "Bắt buộc"],
        ["UC03", "Báo động cháy tự động", "Khi khói vượt ngưỡng (400 PPM), tự động hú còi và bật quạt hút khói", "ESP32 / Node-RED", "Bắt buộc"],
        ["UC04", "Điều khiển quạt từ xa", "Người quản trị gửi lệnh bật/tắt quạt thông gió qua Web SCADA hoặc MQTTX", "Admin / Web", "Cao"],
        ["UC05", "Đổi chế độ Ngày/Đêm", "Lập lịch điều chỉnh ngưỡng khói thích ứng: Ngày 400 PPM, Đêm 350 PPM", "Node-RED / Web", "Trung bình"],
        ["UC06", "Nhật ký kiểm toán an toàn", "Ghi nhận toàn bộ sự kiện báo động, chuyển vai trò và lệnh điều khiển vào log", "Web SCADA", "Bắt buộc"],
        ["UC07", "Chẩn đoán sự cố phần cứng", "Phát hiện đứt cáp cảm biến (FAULT) và mất kết nối mạng (LWT/Watchdog)", "Hệ thống", "Cao"]
    ]
    insert_standard_table(doc, uc_headers, uc_data, [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.JUSTIFY, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER], caption_text="Bảng 1.1. Ma trận đối chiếu 7 Use Cases cốt lõi của hệ thống báo khói")

    add_heading_2(doc, "1.5. Đặc tả yêu cầu phi chức năng")
    add_p(doc, "- Thời gian đáp ứng (Latency): Độ trễ từ khi nồng độ khói vượt ngưỡng đến khi rơ-le quạt đóng mạch và còi hú dưới 2.0 giây.")
    add_p(doc, "- Độ tin cậy (Reliability): Lõi C++ không sử dụng cấp phát bộ nhớ động phân mảnh, bảo đảm dung lượng RAM tĩnh 14.2% ổn định lâu dài.")
    add_p(doc, "- Tính toàn vẹn và an toàn (Safety): Cấm hoàn toàn mọi lệnh ngắt quạt hút khói từ xa trong trạng thái hỏa hoạn khẩn cấp.")
    add_p(doc, "- Tính bảo mật (Security): Xác thực thiết bị trước khi tiếp nhận bản tin, ngăn chặn tấn công giả mạo và chống XSS trên giao diện Web [2].")

    # ---------------- CHƯƠNG 2 ----------------
    add_heading_1(doc, "Chương 2. Thiết kế kiến trúc tổng thể hệ thống 4 tầng IoT")
    
    add_heading_2(doc, "2.1. Mô hình kiến trúc 4 tầng chuẩn của bộ môn")
    add_p(doc, "Tuân thủ chặt chẽ đề cương và chuẩn kiến trúc IoT do ThS. Võ Hoàng Hải ban hành [1], hệ thống được phân rã thành 4 tầng độc lập có ranh giới trách nhiệm rõ ràng:")
    
    layer_headers = ["Tầng kiến trúc", "Thành phần hiện thực hóa", "Nhiệm vụ kỹ thuật chính", "Công nghệ sử dụng"]
    layer_data = [
        ["Tầng 1: Sensing / Physical", "Mạch ESP32, MQ-2, DHT22, Relay, Còi", "Đo đạc môi trường, lọc số EMA, FSM điều khiển chấp hành độc lập", "C++, Wokwi, Arduino Framework"],
        ["Tầng 2: Network / Connectivity", "MQTT Broker EMQX Cloud, Wi-Fi", "Định tuyến bản tin Pub/Sub, mã hóa TLS, quản lý QoS và LWT", "MQTT 3.1.1, WebSocket WSS"],
        ["Tầng 3: Middleware / Automation", "Node-RED Core Engine 52 nodes", "Khử trùng lặp, xác thực Whitelist, 5 Business Rules, Watchdog", "Node.js, Node-RED, JSON"],
        ["Tầng 4: Application / Platform", "Web SCADA Dashboard, MQTTX Desktop", "Giao diện hiển thị trực quan, phân quyền RBAC, Audit Trail", "HTML5, CSS3, JavaScript Canvas"]
    ]
    insert_standard_table(doc, layer_headers, layer_data, [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.JUSTIFY, WD_ALIGN_PARAGRAPH.CENTER], caption_text="Bảng 2.1. Phân bổ nhiệm vụ và luồng dữ liệu chuẩn trên 4 tầng kiến trúc IoT")

    add_heading_2(doc, "2.2. Thiết kế luồng dữ liệu hai chiều (Uplink và Downlink)")
    add_p(doc, "Kiến trúc hệ thống bảo đảm tính khép kín của luồng dữ liệu 2 chiều:")
    add_p(doc, "1. Luồng Uplink (Thu thập dữ liệu): Định kỳ mỗi 2 giây, vi điều khiển ESP32 đọc cảm biến, lọc số EMA và đóng gói JSON gửi lên topic Nhom09/smoke/telemetry. Node-RED tiếp nhận, kiểm tra dữ liệu và phân phối tới Web SCADA qua WebSocket [10].")
    add_p(doc, "2. Luồng Downlink (Điều khiển thiết bị): Người dùng trên Web SCADA phát lệnh bật/tắt thiết bị tới topic Nhom09/smoke/cmd/fan. ESP32 tiếp nhận, kiểm tra điều kiện an toàn, kích hoạt chân rơ-le và gửi bản tin xác nhận ACK ngược lại broker.")

    add_heading_2(doc, "2.3. Ma trận phân xử quyền ưu tiên vận hành PCCC")
    add_p(doc, "Nhằm triệt tiêu hiện tượng tranh chấp quyền điều khiển (Race Condition), hệ thống thiết lập ma trận phân xử quyền ưu tiên nghiêm ngặt theo tiêu chuẩn PCCC [4]:")
    
    pri_headers = ["Trạng thái hệ thống", "Mức khói / Nhiệt độ", "Quyền ưu tiên cao nhất", "Hành vi chấp hành quạt hút và còi", "Xử lý lệnh từ xa"]
    pri_data = [
        ["AN TOÀN (SAFE)", "Khói < 300 PPM, Nhiệt < 50°C", "Người dùng / Lập lịch", "Quạt tắt, còi tắt; cho phép bật quạt thông gió thủ công", "Chấp nhận lệnh ON/OFF"],
        ["CẢNH BÁO (WARNING)", "300 ≤ Khói < 400 PPM", "Hệ thống tự động", "Còi phát tiếng bíp ngắt quãng cảnh báo phòng ngừa", "Chấp nhận lệnh"],
        ["BÁO ĐỘNG (ALARM)", "Khói ≥ 400 PPM hoặc T ≥ 50°C", "Tự động PCCC (Tuyệt đối)", "Quạt hút bật tối đa, còi hú liên tục không ngừng", "TỪ CHỐI LỆNH TẮT (Khóa an toàn)"],
        ["XẢ KHÓI (COOLDOWN)", "Khói hạ < 300 PPM sau cháy", "Bộ đếm thời gian 30s", "Quạt tiếp tục chạy hút sạch khói độc dư", "Khóa lệnh tắt thủ công"],
        ["SỰ CỐ (FAULT)", "Đứt cáp MQ-2 hoặc DHT22 lỗi", "Hệ thống bảo trì", "Còi kêu bíp cảnh báo lỗi, chặn báo cháy giả", "Chỉ nhận lệnh khôi phục"]
    ]
    insert_standard_table(doc, pri_headers, pri_data, [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.JUSTIFY], caption_text="Bảng 2.2. Ma trận phân xử quyền ưu tiên vận hành và bảo vệ an toàn PCCC")

    # ---------------- CHƯƠNG 3 ----------------
    add_heading_1(doc, "Chương 3. Tầng 1 - Thiết kế mạch phần cứng và mô phỏng Wokwi")
    
    add_heading_2(doc, "3.1. Lựa chọn vi điều khiển và linh kiện ngoại vi")
    add_p(doc, "Hệ thống sử dụng vi điều khiển ESP32 DevKit V4 với bộ xử lý lõi kép Tensilica Xtensa 32-bit LX6, xung nhịp 240 MHz, tích hợp sẵn kết nối Wi-Fi 802.11 b/g/n và bộ nhớ 320 KB SRAM, 4 MB Flash [6]. Cảm biến khói MQ-2 hoạt động trên nguyên lý thay đổi điện trở bề mặt chất bán dẫn SnO2 khi tiếp xúc với các khí cháy (LPG, Propane, Methane, Khói) [8]. Cảm biến DHT22 cung cấp tín hiệu nhiệt độ và độ ẩm kỹ thuật số với độ chính xác cao (sai số ±0.5°C) [9].")
    
    add_p(doc, "Điện trở cảm biến Rs biến thiên theo nồng độ khói khí gas và được xác định từ cầu phân áp qua công thức:")
    rs_omml = '''
<m:sSub><m:e><m:r><m:t>R</m:t></m:r></m:e><m:sub><m:r><m:t>s</m:t></m:r></m:sub></m:sSub>
<m:r><m:t> = </m:t></m:r>
<m:sSub><m:e><m:r><m:t>R</m:t></m:r></m:e><m:sub><m:r><m:t>L</m:t></m:r></m:sub></m:sSub>
<m:r><m:t> · </m:t></m:r>
<m:f>
  <m:num>
    <m:sSub><m:e><m:r><m:t>V</m:t></m:r></m:e><m:sub><m:r><m:t>cc</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t> - </m:t></m:r>
    <m:sSub><m:e><m:r><m:t>V</m:t></m:r></m:e><m:sub><m:r><m:t>out</m:t></m:r></m:sub></m:sSub>
  </m:num>
  <m:den>
    <m:sSub><m:e><m:r><m:t>V</m:t></m:r></m:e><m:sub><m:r><m:t>out</m:t></m:r></m:sub></m:sSub>
  </m:den>
</m:f>
'''
    add_display_equation(doc, rs_omml)

    add_p(doc, "Từ tỷ số Rs/R0, nồng độ khói quy đổi ra đơn vị PPM (Parts Per Million) được tính toán theo đặc tuyến hàm mũ (Power-law):")
    ppm_omml = '''
<m:r><m:t>PPM</m:t></m:r>
<m:r><m:t> = </m:t></m:r>
<m:r><m:t>A</m:t></m:r>
<m:r><m:t> · </m:t></m:r>
<m:sSup>
  <m:e>
    <m:d>
      <m:e>
        <m:f>
          <m:num><m:sSub><m:e><m:r><m:t>R</m:t></m:r></m:e><m:sub><m:r><m:t>s</m:t></m:r></m:sub></m:sSub></m:num>
          <m:den><m:sSub><m:e><m:r><m:t>R</m:t></m:r></m:e><m:sub><m:r><m:t>0</m:t></m:r></m:sub></m:sSub></m:den>
        </m:f>
      </m:e>
    </m:d>
  </m:e>
  <m:sup><m:r><m:t>B</m:t></m:r></m:sup>
</m:sSup>
'''
    add_display_equation(doc, ppm_omml)
    p_desc = add_p(doc, "Trong đó: ")
    add_inline_math(p_desc, '<m:sSub><m:e><m:r><m:t>R</m:t></m:r></m:e><m:sub><m:r><m:t>L</m:t></m:r></m:sub></m:sSub><m:r><m:t> = 10 kΩ</m:t></m:r>')
    r_d1 = p_desc.add_run(" là điện trở tải trên module cảm biến; ")
    set_run_font(r_d1, size=SIZE_BODY, bold=False, italic=False)
    add_inline_math(p_desc, '<m:sSub><m:e><m:r><m:t>V</m:t></m:r></m:e><m:sub><m:r><m:t>cc</m:t></m:r></m:sub></m:sSub><m:r><m:t> = 3.3 V</m:t></m:r>')
    r_d2 = p_desc.add_run(" là điện áp tham chiếu của bộ ADC 12-bit ESP32; ")
    set_run_font(r_d2, size=SIZE_BODY, bold=False, italic=False)
    add_inline_math(p_desc, '<m:sSub><m:e><m:r><m:t>R</m:t></m:r></m:e><m:sub><m:r><m:t>0</m:t></m:r></m:sub></m:sSub>')
    r_d3 = p_desc.add_run(" là điện trở cảm biến trong môi trường không khí chuẩn sạch; ")
    set_run_font(r_d3, size=SIZE_BODY, bold=False, italic=False)
    add_inline_math(p_desc, '<m:r><m:t>A</m:t></m:r>')
    r_d4 = p_desc.add_run(" và ")
    set_run_font(r_d4, size=SIZE_BODY, bold=False, italic=False)
    add_inline_math(p_desc, '<m:r><m:t>B</m:t></m:r>')
    r_d5 = p_desc.add_run(" là các tham số độ cong thực nghiệm được xác định từ datasheet của nhà sản xuất Hanwei [8].")
    set_run_font(r_d5, size=SIZE_BODY, bold=False, italic=False)

    add_p(doc, "Căn cứ tài liệu kỹ thuật chính thức từ nhà sản xuất Espressif Systems (ESP32 Series Datasheet V4.4 - Section 5: Electrical Characteristics), các thông số đặc tính điện then chốt của chip vi điều khiển ESP32 được chuẩn hóa để làm cơ sở thiết kế mạch an toàn:")

    # Bảng 3.1: Đặc tính điện của chip ESP32
    esp_elec_headers = ["Nhóm thông số", "Thông số kỹ thuật", "Ký hiệu", "Giá trị Min", "Điển hình (Typ)", "Giá trị Max", "Đơn vị", "Ghi chú kỹ thuật"]
    esp_elec_data = [
        ["Nguồn cấp chip", "Điện áp hoạt động chip", "VDD", "3.0", "3.3", "3.6", "V", "Cấp trực tiếp chân 3V3 của ESP32"],
        ["Nguồn cấp bo mạch", "Điện áp cổng Micro-USB/5V", "VIN", "4.5", "5.0", "6.0", "V", "Hạ áp qua IC LDO AMS1117-3.3"],
        ["Dòng cấp nguồn ngoài", "Dòng cấp tối thiểu khuyến nghị", "IDD_EXT", "500", "-", "-", "mA", "Chống sụt áp khi phát sóng Wi-Fi"],
        ["Ngõ vào số (GPIO)", "Điện áp mức thấp ngõ vào", "VIL", "-0.3", "-", "0.8", "V", "0.25 * VDD (Mức logic 0)"],
        ["Ngõ vào số (GPIO)", "Điện áp mức cao ngõ vào", "VIH", "2.5", "3.3", "3.6", "V", "0.75 * VDD (Mức logic 1)"],
        ["Ngõ vào số (GPIO)", "Trở kéo lên nội (Pull-up)", "RPU", "30", "45", "60", "kΩ", "Kích hoạt nội cho nút nhấn PIN_BUTTON"],
        ["Ngõ ra số (GPIO)", "Điện áp mức thấp ngõ ra", "VOL", "-", "0.1", "0.33", "V", "Dòng xả IOL = 12 mA, VDD = 3.3V"],
        ["Ngõ ra số (GPIO)", "Điện áp mức cao ngõ ra", "VOH", "2.64", "3.2", "-", "V", "Dòng bơm IOH = 12 mA, VDD = 3.3V"],
        ["Ngõ ra số (GPIO)", "Dòng tải tối đa mỗi chân", "IMAX", "-", "-", "40", "mA", "Dòng vận hành an toàn ≤ 12 mA"],
        ["Bộ ADC 12-bit", "Độ phân giải bộ chuyển đổi", "NADC", "-", "12", "-", "bit", "Dải số nguyên đo từ 0 đến 4095"],
        ["Bộ ADC 12-bit", "Dải suy hao đo (Attenuation)", "Atten", "-", "11", "-", "dB", "Cấu hình chân đọc khói MQ-2 GPIO 34"],
        ["Bộ ADC 12-bit", "Dải điện áp đo tuyến tính", "VADC_IN", "0.15", "-", "3.10", "V", "Mức suy hao 11 dB (VREF = 1.1V)"],
        ["Tiêu thụ dòng điện", "Wi-Fi TX (802.11b, +20dBm)", "ITX", "160", "240", "380", "mA", "Công suất đỉnh khi phát bản tin"],
        ["Tiêu thụ dòng điện", "Wi-Fi RX (Nhận gói tin)", "IRX", "-", "95", "100", "mA", "Nhận bản tin Downlink từ broker"],
        ["Tiêu thụ dòng điện", "CPU 240 MHz (Modem-sleep)", "ICPU", "20", "30", "50", "mA", "Xử lý FSM và thuật toán lọc EMA"],
        ["Môi trường hoạt động", "Nhiệt độ môi trường vận hành", "TOP", "-40", "25", "+85", "°C", "Chuẩn công nghiệp (Industrial Grade)"]
    ]
    insert_standard_table(doc, esp_elec_headers, esp_elec_data, 
                          [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.JUSTIFY], 
                          caption_text="Bảng 3.1. Bảng thông số đặc tính điện chi tiết của chip vi điều khiển ESP32")

    add_p(doc, "Dựa trên các thông số đặc tính điện của chip ESP32 và các linh kiện ngoại vi, nhóm đã thiết lập bảng cân bằng công suất điện năng (Power Budget) cho toàn bộ trạm thiết bị nhằm bảo đảm an toàn tuyệt đối khi vận hành liên tục:")

    # Bảng 3.2: Power Budget
    pwr_headers = ["Thành phần thiết bị", "Điện áp hoạt động", "Dòng điện danh định", "Dòng điện đỉnh (Peak)", "Công suất tiêu thụ Max", "Ghi chú an toàn điện"]
    pwr_data = [
        ["ESP32 DevKit V4", "3.3V (qua LDO 5V)", "80 mA", "380 mA", "~1.25 W", "Đỉnh dòng khi truyền gói tin MQTT Wi-Fi"],
        ["Cuộn sấy cảm biến MQ-2", "5V DC", "140 mA", "160 mA", "~0.80 W", "Nuôi bộ sấy nung nóng bề mặt SnO2 liên tục"],
        ["Cảm biến nhiệt ẩm DHT22", "3.3V DC", "1.0 mA", "1.5 mA", "~0.005 W", "Tiêu thụ dòng rất nhỏ trong chu kỳ đọc 5s"],
        ["Module Rơ-le (Cuộn hút + Opto)", "5V DC", "60 mA", "75 mA", "~0.38 W", "Dòng cuộn hút khi đóng tiếp điểm kích quạt"],
        ["Còi báo động Active Buzzer", "3.3V PWM (LEDC)", "20 mA", "30 mA", "~0.10 W", "Phát xung âm thanh báo cháy tần số 2000 Hz"],
        ["Quạt hút khói thông gió DC", "5V DC (qua Relay NO)", "180 mA", "220 mA", "~1.10 W", "Tải công suất khi FSM chuyển sang ALARM"],
        ["TỔNG CỘNG TOÀN HỆ THỐNG", "5V DC", "~481 mA", "~866.5 mA", "~4.33 W", "Nguồn cấp 5V - 2A (10W) đáp ứng dư tải 130%"]
    ]
    insert_standard_table(doc, pwr_headers, pwr_data,
                          [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.JUSTIFY],
                          caption_text="Bảng 3.2. Bảng cân bằng công suất điện năng toàn hệ thống (System Power Budget)")

    add_heading_2(doc, "3.2. Sơ đồ ghép nối mạch nguyên lý và bảng nối chân Lab chi tiết")
    add_p(doc, "Để thể hiện trọn vẹn mối liên kết phần cứng giữa tất cả các linh kiện (bao gồm vi điều khiển ESP32, cảm biến khói MQ-2, cảm biến nhiệt ẩm DHT22, còi hú buzzer, module rơ-le cách ly quang, tải quạt hút thông gió và nút nhấn khẩn cấp), nhóm đã thiết lập sơ đồ nguyên lý ghép nối chân toàn mạch:")

    insert_image_with_border(doc, "docs/images/circuit_schematic_wiring.png", width_inches=6.2, 
                             caption_text="Hình 3.1. Sơ đồ ghép nối mạch nguyên lý và phân bổ chân linh kiện toàn hệ thống")

    add_p(doc, "Toàn bộ 16 đường dây đấu nối thực nghiệm phòng Lab được chuẩn hóa 100% theo đúng cấu hình diagram.json trên nền tảng Wokwi và sơ đồ cắm dây breadboard thực tế:")

    # Bảng 3.3: Bảng đấu nối chân Lab chi tiết (16 kết nối)
    wire_headers = ["STT", "Thiết bị gốc", "Chân gốc", "Thiết bị đích", "Chân đích", "Màu dây", "Cấp điện áp & Tín hiệu", "Chức năng kỹ thuật trong hệ thống"]
    wire_data = [
        ["1", "Cảm biến Khói MQ-2", "VCC", "ESP32 DevKit V4", "5V", "Đỏ (Red)", "5V DC (Power)", "Cấp nguồn nuôi cuộn sấy bề mặt (Heater) của cảm biến SnO2"],
        ["2", "Cảm biến Khói MQ-2", "GND", "ESP32 DevKit V4", "GND.1", "Đen (Black)", "0V (Ground)", "Nối đất Mass chung cho mạch đo cảm biến khói"],
        ["3", "Cảm biến Khói MQ-2", "AOUT", "ESP32 DevKit V4", "GPIO 34", "Vàng (Gold)", "Analog (0 - 3.3V)", "Ngõ ra điện áp cầu phân áp biến thiên theo nồng độ khói PPM"],
        ["4", "Cảm biến Nhiệt ẩm DHT22", "VCC", "ESP32 DevKit V4", "3V3", "Đỏ (Red)", "3.3V DC (Power)", "Cấp nguồn hoạt động kỹ thuật số cho cảm biến DHT22"],
        ["5", "Cảm biến Nhiệt ẩm DHT22", "GND", "ESP32 DevKit V4", "GND.1", "Đen (Black)", "0V (Ground)", "Nối đất Mass chung cho cảm biến nhiệt ẩm"],
        ["6", "Cảm biến Nhiệt ẩm DHT22", "SDA (DATA)", "ESP32 DevKit V4", "GPIO 4", "Xanh lá (Green)", "Digital Bi-directional", "Truyền nhận dữ liệu nhiệt độ (°C) và độ ẩm (%RH) chuẩn 1-Wire"],
        ["7", "Còi báo động Active Buzzer", "Chân 2 (POS)", "ESP32 DevKit V4", "GPIO 16", "Cam (Orange)", "PWM Output (LEDC)", "Tín hiệu xung điều chế tần số 2000 Hz điều khiển âm còi hú"],
        ["8", "Còi báo động Active Buzzer", "Chân 1 (NEG)", "ESP32 DevKit V4", "GND.1", "Đen (Black)", "0V (Ground)", "Cực âm còi báo động khép kín mạch về Mass chung"],
        ["9", "Module Rơ-le 1 Kênh 5V", "VCC", "ESP32 DevKit V4", "5V", "Đỏ (Red)", "5V DC (Power)", "Cấp nguồn nuôi cuộn hút rơ-le và mạch cách ly quang Opto"],
        ["10", "Module Rơ-le 1 Kênh 5V", "GND", "ESP32 DevKit V4", "GND.2", "Đen (Black)", "0V (Ground)", "Mass bảo vệ độc lập cho tầng công suất rơ-le"],
        ["11", "Module Rơ-le 1 Kênh 5V", "IN", "ESP32 DevKit V4", "GPIO 17", "Tím (Purple)", "Digital Out (Active HIGH)", "Lệnh đóng ngắt tiếp điểm rơ-le từ firmware vi điều khiển"],
        ["12", "Module Rơ-le 1 Kênh 5V", "COM", "ESP32 DevKit V4", "5V", "Đỏ (Red)", "5V DC (Power)", "Tiếp điểm chung cấp nguồn dương tới tải công suất Quạt hút"],
        ["13", "Module Rơ-le 1 Kênh 5V", "NO", "Quạt DC / LED", "Cực dương (A)", "Xanh dương (Blue)", "5V Switched (Output)", "Tiếp điểm thường mở; đóng mạch cấp nguồn cho quạt khi ALARM"],
        ["14", "Quạt DC / LED Tải", "Cực âm (C)", "ESP32 DevKit V4", "GND.2", "Đen (Black)", "0V (Ground)", "Cực âm tải quạt khép kín dòng điện về Mass tầng công suất"],
        ["15", "Nút nhấn khẩn cấp / Test", "Chân 1.l", "ESP32 DevKit V4", "GPIO 18", "Xanh lơ (Cyan)", "Digital In (PULLUP)", "Chân đọc trạng thái nút nhấn; kéo LOW khi người dùng bấm nút"],
        ["16", "Nút nhấn khẩn cấp / Test", "Chân 2.l", "ESP32 DevKit V4", "GND.1", "Đen (Black)", "0V (Ground)", "Nối chân đối diện nút nhấn về Mass để tạo mức 0V khi ấn"]
    ]
    insert_standard_table(doc, wire_headers, wire_data,
                          [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.JUSTIFY],
                          caption_text="Bảng 3.3. Bảng đấu nối chân phần cứng phòng Lab (Chi tiết 16 kết nối chuẩn diagram.json)")

    add_heading_2(doc, "3.3. Hiện thực hóa mô hình mô phỏng trên nền tảng Wokwi")
    add_p(doc, "Mô hình phần cứng được mô phỏng đầy đủ trên nền tảng Wokwi thông qua file cấu hình diagram.json và liên kết nạp nhị phân wokwi.toml. Người dùng có thể kéo thanh trượt nồng độ khói trên MQ-2 và nhiệt độ trên DHT22 để kiểm chứng phản ứng tức thời của mạch [1].")

    # Bảng 3.4: Đối chiếu Wokwi vs Lab thực tế
    comp_headers = ["Hạng mục thiết bị", "Mô hình trên Wokwi (diagram.json)", "Triển khai phần cứng thực tế phòng Lab", "Mức độ tương thích kỹ thuật"]
    comp_data = [
        ["Vi điều khiển", "board-esp32-devkit-c-v4 (WROOM-32)", "ESP32 DevKit V4 38-pin Dual-Core 240MHz", "Tương thích 100% mã nhị phân firmware"],
        ["Cảm biến khói", "wokwi-gas-sensor (Slider 0-1000 PPM)", "Module cảm biến khói khí gas MQ-2 thật", "Tương thích 100% thuật toán lọc ADC/EMA"],
        ["Cảm biến nhiệt ẩm", "wokwi-dht22 (Thanh trượt Temp/Hum)", "Module cảm biến số DHT22 (AM2302) thật", "Tương thích 100% giao thức 1-Wire GPIO4"],
        ["Còi báo động", "wokwi-buzzer (Volume 0.1, xung PWM)", "Active Buzzer 5V phát tần số 2000 Hz", "Tương thích 100% ngõ ra điều chế LEDC"],
        ["Cơ cấu chấp hành quạt", "wokwi-relay-module + wokwi-led (FAN)", "Relay 1 kênh cách ly quang + Quạt DC 5V", "Tương thích 100% logic điều khiển GPIO17"],
        ["Nút bấm điều khiển", "wokwi-pushbutton (Green - Manual Fan)", "Nút nhấn cơ 12x12 kèm trở kéo nội PULLUP", "Tương thích 100% xử lý chống rung 50ms"]
    ]
    insert_standard_table(doc, comp_headers, comp_data,
                          [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.JUSTIFY],
                          caption_text="Bảng 3.4. Bảng đối chiếu đặc tính kỹ thuật giữa mô hình mô phỏng Wokwi và mạch phần cứng Lab thực tế")

    insert_image_with_border(doc, "docs/images/wokwi_hardware_layout.png", width_inches=3.6,
                             caption_text="Hình 3.2. Giao diện bố trí linh kiện và sơ đồ đi dây mạch mô phỏng trên nền tảng Wokwi")
    
    # ---------------- CHƯƠNG 4 ----------------
    add_heading_1(doc, "Chương 4. Thiết kế firmware vi điều khiển ESP32")
    
    add_heading_2(doc, "4.1. Bộ lọc số trung bình động hàm mũ bất đối xứng (Asymmetric EMA)")
    add_p(doc, "Để triệt tiêu các xung nhiễu điện áp ngẫu nhiên của bộ chuyển đổi ADC mà không làm chậm thời gian phát hiện cháy thật, nhóm áp dụng bộ lọc trung bình động hàm mũ bất đối xứng [1]:")
    
    ema_omml = '''
<m:sSub><m:e><m:r><m:t>S</m:t></m:r></m:e><m:sub><m:r><m:t>t</m:t></m:r></m:sub></m:sSub>
<m:r><m:t> = </m:t></m:r>
<m:r><m:t>α</m:t></m:r>
<m:r><m:t> · </m:t></m:r>
<m:sSub><m:e><m:r><m:t>X</m:t></m:r></m:e><m:sub><m:r><m:t>t</m:t></m:r></m:sub></m:sSub>
<m:r><m:t> + (1 - </m:t></m:r>
<m:r><m:t>α</m:t></m:r>
<m:r><m:t>) · </m:t></m:r>
<m:sSub><m:e><m:r><m:t>S</m:t></m:r></m:e><m:sub><m:r><m:t>t-1</m:t></m:r></m:sub></m:sSub>
'''
    add_display_equation(doc, ema_omml)
    
    add_p(doc, "Trong đó:")
    
    p1 = add_p(doc, "- Khi nồng độ khói tăng (")
    add_inline_math(p1, '<m:sSub><m:e><m:r><m:t>X</m:t></m:r></m:e><m:sub><m:r><m:t>t</m:t></m:r></m:sub></m:sSub><m:r><m:t> &gt; </m:t></m:r><m:sSub><m:e><m:r><m:t>S</m:t></m:r></m:e><m:sub><m:r><m:t>t-1</m:t></m:r></m:sub></m:sSub>')
    r1 = p1.add_run("): Sử dụng hệ số ")
    set_run_font(r1, size=SIZE_BODY, bold=False, italic=False)
    add_inline_math(p1, '<m:sSub><m:e><m:r><m:t>α</m:t></m:r></m:e><m:sub><m:r><m:t>rise</m:t></m:r></m:sub></m:sSub><m:r><m:t> = 0.40</m:t></m:r>')
    r2 = p1.add_run(" để bắt nhanh xu hướng khói tăng vọt.")
    set_run_font(r2, size=SIZE_BODY, bold=False, italic=False)
    
    p2 = add_p(doc, "- Khi nồng độ khói giảm (")
    add_inline_math(p2, '<m:sSub><m:e><m:r><m:t>X</m:t></m:r></m:e><m:sub><m:r><m:t>t</m:t></m:r></m:sub></m:sSub><m:r><m:t> ≤ </m:t></m:r><m:sSub><m:e><m:r><m:t>S</m:t></m:r></m:e><m:sub><m:r><m:t>t-1</m:t></m:r></m:sub></m:sSub>')
    r3 = p2.add_run("): Sử dụng hệ số ")
    set_run_font(r3, size=SIZE_BODY, bold=False, italic=False)
    add_inline_math(p2, '<m:sSub><m:e><m:r><m:t>α</m:t></m:r></m:e><m:sub><m:r><m:t>fall</m:t></m:r></m:sub></m:sSub><m:r><m:t> = 0.15</m:t></m:r>')
    r4 = p2.add_run(" để giữ trạng thái an toàn, tránh việc còi báo động bị tắt sớm khi khói chỉ vừa hạ tạm thời.")
    set_run_font(r4, size=SIZE_BODY, bold=False, italic=False)
    
    p3 = add_p(doc, "Thuật toán này chỉ tiêu tốn đúng 4 byte RAM lưu giá trị ")
    add_inline_math(p3, '<m:sSub><m:e><m:r><m:t>S</m:t></m:r></m:e><m:sub><m:r><m:t>t-1</m:t></m:r></m:sub></m:sSub>')
    r5 = p3.add_run(", loại bỏ hoàn toàn mảng nhớ cồng kềnh của bộ lọc trung bình cộng thông thường.")
    set_run_font(r5, size=SIZE_BODY, bold=False, italic=False)

    add_heading_2(doc, "4.2. Máy trạng thái hữu hạn 5 trạng thái (FSM) và vùng trễ Hysteresis")
    add_p(doc, "Chu trình vận hành của thiết bị được quản lý nghiêm ngặt bởi FSM gồm 5 trạng thái: SAFE (An toàn), WARNING (Cảnh báo), ALARM (Báo động hỏa hoạn), COOLDOWN (Xả khói sau cháy), và FAULT (Lỗi cảm biến). Để ngăn chặn hiện tượng rung giật tiếp điểm rơ-le (chattering) khi nồng độ khói dao động quanh ngưỡng kích hoạt, hệ thống áp dụng vùng trễ an toàn Hysteresis:")
    
    hyst_omml = '''
<m:sSub><m:e><m:r><m:t>Δ</m:t></m:r></m:e><m:sub><m:r><m:t>hysteresis</m:t></m:r></m:sub></m:sSub>
<m:r><m:t> = </m:t></m:r>
<m:sSub><m:e><m:r><m:t>Threshold</m:t></m:r></m:e><m:sub><m:r><m:t>ALARM</m:t></m:r></m:sub></m:sSub>
<m:r><m:t> - </m:t></m:r>
<m:sSub><m:e><m:r><m:t>Threshold</m:t></m:r></m:e><m:sub><m:r><m:t>SAFE</m:t></m:r></m:sub></m:sSub>
<m:r><m:t> = 400 - 300 = 100 PPM</m:t></m:r>
'''
    add_display_equation(doc, hyst_omml)

    fsm_headers = ["Trạng thái hiện tại", "Điều kiện chuyển dịch", "Trạng thái tiếp theo", "Hành động chấp hành kích hoạt"]
    fsm_data = [
        ["SAFE", "Khói ≥ 300 PPM", "WARNING", "Còi bíp chậm cảnh báo mức độ nhẹ"],
        ["WARNING", "Khói ≥ 400 PPM", "ALARM", "Bật quạt hút khói tối đa, còi hú liên tục, khóa nút tắt"],
        ["ALARM", "Khói < 300 PPM (vùng trễ Hysteresis)", "COOLDOWN", "Quạt vẫn tiếp tục chạy, đếm lùi chu trình 30 giây"],
        ["COOLDOWN", "Hết 30 giây và Khói < 300 PPM", "SAFE", "Tắt quạt hút, tắt còi, trả lại quyền điều khiển thủ công"],
        ["COOLDOWN", "Khói bùng phát trở lại ≥ 400 PPM", "ALARM", "Hủy đếm lùi, tái kích hoạt báo động khẩn cấp tức thời"],
        ["BẤT KỲ", "Cảm biến MQ-2 đứt dây hoặc chạm chập", "FAULT", "Còi bíp ngắt quãng cảnh báo kỹ thuật, chặn báo cháy giả"]
    ]
    insert_standard_table(doc, fsm_headers, fsm_data, [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.JUSTIFY, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.JUSTIFY], caption_text="Bảng 4.1. Bảng chuyển đổi trạng thái FSM kết hợp vùng trễ Hysteresis và lọc EMA")

    add_heading_2(doc, "4.3. Khóa an toàn PCCC (Safety Interlock) cấp phần cứng")
    add_p(doc, "Trong hàm applyFanAction() thuộc mã nguồn C++, khi nhận lệnh tắt quạt ('OFF') từ mạng MQTT, firmware tiến hành kiểm tra cờ alarmLatched. Nếu hệ thống đang trong trạng thái ALARM, lệnh lập tức bị từ chối ở mức vi điều khiển, chân rơ-le tiếp tục được duy trì ở mức HIGH và phản hồi mã lỗi ACK_SAFETY_LOCK về máy chủ. Cơ chế này bảo đảm tính mạng con người luôn được ưu tiên tuyệt đối.")

    add_heading_2(doc, "4.4. Bộ đệm vòng ngoại tuyến (Circular Ring Buffer) và quản lý bộ nhớ")
    add_p(doc, "Khi xảy ra sự cố mất kết nối mạng Wi-Fi, hàm pushOfflineRecord() tự động lưu trữ các bản tin telemetry và sự kiện vào bộ đệm vòng tĩnh 20 bản ghi (RingBuffer<OfflineRecord, 20>) nằm trong RAM [1]. Cấu trúc OfflineRecord được thiết kế gọn gàng 52 byte. Khi có mạng trở lại, hàm flushOfflineBuffer() sẽ tự động phát bù dữ liệu lên broker. Toàn bộ mã nguồn sử dụng ArduinoJson v7 theo mô hình RAII heap, bảo đảm tỷ lệ sử dụng RAM tĩnh chỉ 14.2% và không hề rò rỉ bộ nhớ.")

    add_heading_2(doc, "4.5. Sơ đồ phân rã chức năng và cấu trúc hàm firmware C++")
    add_p(doc, "Nhằm đáp ứng yêu cầu vận hành tin cậy, không phân mảnh bộ nhớ và xử lý đa nhiệm thời gian thực, mã nguồn firmware src/main.cpp được thiết kế theo mô hình kiến trúc phân lớp chuyên biệt (Modular Layered Architecture). Toàn bộ hệ thống được phân rã thành 6 khối chức năng độc lập:")

    insert_image_with_border(doc, "docs/images/firmware_functional_hierarchy.png", width_inches=6.2,
                             caption_text="Hình 4.1. Sơ đồ phân rã chức năng và cấu trúc phân cấp hàm trong Firmware C++")

    add_p(doc, "Danh mục các hàm cốt lõi, tham số đầu vào/ra và vai trò kỹ thuật trong mã nguồn src/main.cpp được tổng hợp chi tiết trong Bảng 4.2:")

    # Bảng 4.2: Danh mục các hàm cốt lõi
    func_headers = ["STT", "Tên hàm / Thủ tục", "Tham số đầu vào", "Kiểu trả về", "Phân hệ chức năng", "Vai trò kỹ thuật trong hệ thống PCCC"]
    func_data = [
        ["1", "setup()", "Không có", "void", "Khởi tạo", "Cấu hình GPIO, nạp timer, hiệu chuẩn MQ-2, kết nối Wi-Fi/MQTT"],
        ["2", "loop()", "Không có", "void", "Vòng lặp chính", "Điều phối 7 công đoạn thực thi phi chặn theo kỹ thuật Timer millis()"],
        ["3", "readMQ2PPM()", "SensorConfig&, float r0", "float", "Thu thập cảm biến", "Đọc ADC1_CH6, tính cầu phân áp Rs và quy đổi PPM hàm mũ"],
        ["4", "mq2Update()", "Mq2Health&, int adc, ...", "HealthEvent", "Giám sát phần cứng", "Phát hiện đứt cáp (ADC < 100) hoặc chạm chập (ADC > 4000)"],
        ["5", "emaUpdate()", "EmaFilter&, float raw, ...", "float", "Xử lý tín hiệu số", "Bộ lọc trung bình động hàm mũ bất đối xứng (aRise=0.40, aFall=0.15)"],
        ["6", "readDHT()", "float& temp, float& hum", "bool", "Thu thập cảm biến", "Giao tiếp 1-Wire đọc nhiệt độ và độ ẩm; bẫy lỗi isnan()"],
        ["7", "fsmStep()", "FsmContext&, FsmInput&, ...", "FsmOutput", "Lõi máy trạng thái", "Chuyển dịch FSM 5 trạng thái kết hợp vùng trễ Hysteresis 100 PPM"],
        ["8", "applyFanAction()", "FsmContext&, const char*, ...", "ActionAck", "Khóa an toàn PCCC", "Từ chối lệnh tắt quạt ('OFF') khi hệ thống đang trong trạng thái ALARM"],
        ["9", "applyBuzzerAction()", "FsmContext&, const char*, ...", "ActionAck", "Điều khiển còi", "Xử lý tắt tiếng tạm thời (Mute 180s) hoặc kích hoạt hú còi khẩn"],
        ["10", "fanApply()", "bool on", "void", "Chấp hành phần cứng", "Xuất mức logic HIGH/LOW ra chân GPIO 17 đóng ngắt cuộn hút rơ-le"],
        ["11", "buzzerTick()", "BuzzerPattern, uint32_t", "void", "Chấp hành phần cứng", "Điều chế tần số âm thanh PWM 2000Hz qua LEDC Channel 0 (GPIO 16)"],
        ["12", "netTick()", "uint32_t now", "void", "Truyền thông mạng", "Quản lý kết nối Wi-Fi & MQTT theo giải thuật Exponential Backoff"],
        ["13", "mqttCallback()", "char* topic, byte* payload", "void", "Tiếp nhận bản tin", "Phân tích JSON RFC 8259 an toàn (RAII heap), giải mã lệnh Downlink"],
        ["14", "publishTelemetry()", "Không có", "void", "Truyền thông mạng", "Đóng gói JSON và phát bản tin Telemetry định kỳ chu kỳ 2s"],
        ["15", "pushOfflineRecord()", "float ppm, float t, ...", "void", "Bộ đệm ngoại tuyến", "Lưu trữ bản ghi telemetry vào Ring Buffer tĩnh khi mất mạng Wi-Fi"],
        ["16", "flushOfflineBuffer()", "Không có", "void", "Đồng bộ ngoại tuyến", "Phát bù tuần tự toàn vẹn dữ liệu sự cố lên broker khi mạng hồi phục"]
    ]
    insert_standard_table(doc, func_headers, func_data,
                          [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.JUSTIFY],
                          caption_text="Bảng 4.2. Bảng danh mục các hàm cốt lõi và vai trò kỹ thuật trong mã nguồn src/main.cpp")

    add_heading_2(doc, "4.6. Sơ đồ luồng chạy và lưu đồ thuật toán vòng lặp chính loop()")
    add_p(doc, "Khác với các chương trình nhúng tuần tự đơn giản sử dụng hàm delay() gây nghẽn vi điều khiển, vòng lặp chính loop() của hệ thống được lập trình theo mô hình phân lát thời gian không chặn (Time-sliced Non-blocking Architecture) dựa trên hàm đếm xung millis():")

    insert_image_with_border(doc, "docs/images/firmware_execution_flowchart.png", width_inches=5.6,
                             caption_text="Hình 4.2. Lưu đồ thuật toán vòng lặp thực thi phi chặn loop() của vi điều khiển ESP32")

    add_p(doc, "Trong mỗi vòng lặp, vi điều khiển tuần tự thực hiện 7 công đoạn kỹ thuật:")
    add_p(doc, "1. Công đoạn 1 (netTick): Kiểm tra trạng thái mạng Wi-Fi và MQTT Broker. Nếu mất mạng, giải thuật Exponential Backoff sẽ tự động kích hoạt thử kết nối lại theo chu kỳ tăng dần mà không bao giờ chặn vòng quét.")
    add_p(doc, "2. Công đoạn 2 (buttonTick): Đọc trạng thái nút bấm vật lý trên chân GPIO 18, lọc chống rung phím cơ học 50ms (Debounce) và kích hoạt ngắt dập tắt còi 60s khi phát hiện người dùng thao tác.")
    add_p(doc, "3. Công đoạn 3 (Chấp hành ngoại vi): Cập nhật trạng thái rơ-le quạt hút qua fanApply() và điều chế xung còi hú qua buzzerTick().")
    add_p(doc, "4. Công đoạn 4 (Đo khói & FSM chu kỳ 2s): Đọc cảm biến MQ-2, kiểm tra lỗi đứt cáp, lọc số EMA, chạy chuyển dịch trạng thái FSM, và phát bản tin Telemetry JSON (hoặc lưu vào đệm vòng RAM nếu mất mạng).")
    add_p(doc, "5. Công đoạn 5 (Đo nhiệt ẩm chu kỳ 5s): Giao tiếp số 1-Wire đọc nhiệt độ và độ ẩm từ DHT22, bẫy lỗi an toàn tránh giá trị NaN.")
    add_p(doc, "6. Công đoạn 6 (Nhịp tim chu kỳ 10s): Phát bản tin Keep-Alive nhịp tim lên broker nhằm duy trì trạng thái kết nối cho bộ giám sát Watchdog.")
    add_p(doc, "7. Công đoạn 7 (Loop Latency Guard): Đo đạc tổng thời gian thực thi của vòng lặp, cảnh báo nếu thời gian vượt quá 50ms nhằm bảo đảm độ nhạy phản ứng tức thời.")

    # ---------------- CHƯƠNG 5 ----------------
    add_heading_1(doc, "Chương 5. Tầng 2 - Thiết kế mạng truyền thông MQTT và cấu trúc dữ liệu")
    
    add_heading_2(doc, "5.1. Cấu trúc cây 62 topic chuẩn hóa mang tiền tố Nhom09/smoke")
    add_p(doc, "Để ngăn chặn nguy cơ ô nhiễm dữ liệu hoặc xung đột lệnh trên broker công cộng, nhóm đã chuẩn hóa toàn bộ 62 topic của dự án bắt đầu bằng tiền tố duy nhất Nhom09/smoke/ [5]:")
    
    topic_headers = ["Nhóm chức năng", "Cấu trúc Topic chuẩn", "QoS", "Mục đích sử dụng"]
    topic_data = [
        ["Telemetry định kỳ", "Nhom09/smoke/telemetry", "QoS 0", "Truyền dữ liệu nồng độ khói, nhiệt ẩm chu kỳ 2s"],
        ["Sự kiện báo động", "Nhom09/smoke/event/alarm", "QoS 1", "Truyền thông báo khẩn cấp khi khói vượt ngưỡng"],
        ["Điều khiển quạt", "Nhom09/smoke/cmd/fan", "QoS 1", "Gửi lệnh bật/tắt quạt thông gió từ Web SCADA"],
        ["Điều khiển còi", "Nhom09/smoke/cmd/buzzer", "QoS 1", "Gửi lệnh tắt còi tạm thời (Mute) hoặc bật còi"],
        ["Lập lịch ngày/đêm", "Nhom09/smoke/cmd/scheduler", "QoS 1", "Đồng bộ ngưỡng cảnh báo Ngày 400 PPM / Đêm 350 PPM"],
        ["Bơm sự cố giả lập", "Nhom09/smoke/cmd/inject_fault", "QoS 1", "Giả lập lỗi cảm biến phục vụ kiểm thử hệ thống"],
        ["Di chúc LWT", "Nhom09/smoke/lwt", "QoS 1", "Phát hiện trạm ESP32 đột tử hoặc đứt kết nối mạng"],
        ["Cấp quyền doanh nghiệp V2", "Nhom09/smoke/v2/auth/request", "QoS 1", "Gửi yêu cầu xác thực thiết bị mới vào hệ thống"],
        ["Sơ tán liên vùng V2", "Nhom09/smoke/v2/HUIT_A/F03/+/cmd/buzzer", "QoS 1", "Phát lệnh hú còi khẩn cấp tới các phòng lân cận"]
    ]
    insert_standard_table(doc, topic_headers, topic_data, [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.JUSTIFY], caption_text="Bảng 5.1. Bảng định tuyến MQTT Topics chuẩn hóa trong không gian Nhom09/smoke")

    add_heading_2(doc, "5.2. Chuẩn hóa cấu trúc gói tin JSON RFC 8259")
    add_p(doc, "Toàn bộ thông điệp truyền thông đều được chuẩn hóa theo chuẩn RFC 8259 [10]. Gói tin Telemetry định kỳ chứa đầy đủ thông tin định danh và số đo:")
    add_p(doc, '{\n  "device_id": "ESP32_SMOKE_N09_A01",\n  "uptime_s": 128,\n  "mq2_ppm": 215.4,\n  "mq2_valid": true,\n  "temp": 28.5,\n  "hum": 60.0,\n  "dht_valid": true,\n  "fsm_state": "SAFE",\n  "fan": "OFF",\n  "buzzer": "OFF",\n  "mode": "AUTO"\n}', align=WD_ALIGN_PARAGRAPH.LEFT)

    # ---------------- CHƯƠNG 6 ----------------
    add_heading_1(doc, "Chương 6. Tầng 3 - Thiết kế middleware và động cơ quy tắc Node-RED")
    
    add_heading_2(doc, "6.1. Kiến trúc luồng xử lý 52 nodes trên Node-RED")
    add_p(doc, "Luồng Node-RED flows_smoke_detector.json đóng vai trò là 'bộ não' điều phối trung tâm của toàn bộ hệ thống, tích hợp 52 nodes xử lý chuyên biệt gồm các phân hệ: Xác thực bảo mật, Bộ lọc khử trùng lặp dữ liệu, Động cơ quy tắc nghiệp vụ PCCC, Bộ lập lịch thời gian và Giám sát nhịp tim Watchdog [7].")

    insert_image_with_border(doc, "docs/images/live_test/nodered_live_flow.png", width_inches=5.8, caption_text="Hình 6.1. Luồng xử lý trung tâm 52 nodes và màn hình Debug messages trên Node-RED")

    add_heading_2(doc, "6.2. Hiện thực hóa 5 quy tắc nghiệp vụ PCCC (5 Business Rules)")
    add_p(doc, "Động cơ quy tắc Core Engine của Node-RED thực thi 5 quy tắc nghiệp vụ tự động hóa PCCC. Trong đó, quy tắc Cháy thực tế (Rule 1) kết hợp đồng thời giữa nồng độ khói và đạo hàm gia tốc tăng nhiệt theo thời gian trên cửa sổ trượt Δt = 60 giây:")
    
    ror_omml = '''
<m:f>
  <m:num><m:r><m:t>dT</m:t></m:r></m:num>
  <m:den><m:r><m:t>dt</m:t></m:r></m:den>
</m:f>
<m:r><m:t> ≥ 3.0 °C/phút</m:t></m:r>
'''
    add_display_equation(doc, ror_omml)

    rule_headers = ["Tên quy tắc", "Điều kiện kích hoạt", "Hành động điều phối", "Mục đích an toàn"]
    rule_data = [
        ["Rule 1: Cháy thực tế (Real Fire)", "Khói ≥ 400 PPM VÀ Gia tốc nhiệt dT/dt ≥ 3.0°C/phút", "Bật quạt hút, gửi lệnh UNMUTE còi hú mức khẩn cấp", "Bắt đám cháy bùng phát nhanh, bỏ qua chế độ tắt còi tạm"],
        ["Rule 2: Khói âm ỉ (Low Heat)", "Khói ≥ 400 PPM VÀ Nhiệt độ bình thường (< 50°C)", "Bật quạt hút khói, ghi nhận cảnh báo mức WARN", "Xử lý cháy âm ỉ sinh nhiều khói độc mà chưa tỏa nhiệt lớn"],
        ["Rule 3: Lập lịch Ngày/Đêm", "Inject node kích hoạt mỗi 60s, kiểm tra thời gian thực", "Đổi ngưỡng: Ngày 400 PPM / Đêm 350 PPM", "Tăng độ nhạy phát hiện cháy vào ban đêm khi người dân ngủ"],
        ["Rule 4: Chu trình xả khói Cooldown", "Khói giảm < 300 PPM sau khi đã có báo động ALARM", "Duy trì quạt chạy thêm 30 giây trước khi tắt", "Hút sạch khói độc dư và chống hiện tượng rung tiếp điểm relay"],
        ["Rule 5: Sơ tán liên vùng (Cross-Zone)", "Khói vượt ngưỡng nguy cấp ≥ 600 PPM", "Bắn lệnh hú còi tới toàn bộ phòng cùng tầng F03", "Báo động kịp thời cho các phòng xung quanh sơ tán thoát nạn"]
    ]
    insert_standard_table(doc, rule_headers, rule_data, [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.JUSTIFY, WD_ALIGN_PARAGRAPH.JUSTIFY, WD_ALIGN_PARAGRAPH.JUSTIFY], caption_text="Bảng 6.1. Bảng đặc tả 5 Business Rules tự động hóa cứu nạn trên Node-RED")

    insert_image_with_border(doc, "docs/images/live_test/nodered_dashboard_live.png", width_inches=5.8, caption_text="Hình 6.2. Giao diện bảng điều khiển Node-RED Dashboard hiển thị Gauges và Trend Chart")

    # ---------------- CHƯƠNG 7 ----------------
    add_heading_1(doc, "Chương 7. Tầng 4 - Thiết kế ứng dụng điều hành Web SCADA")
    
    add_heading_2(doc, "7.1. Giao diện điều hành thời gian thực và phân quyền RBAC")
    add_p(doc, "Ứng dụng Web SCADA tại địa chỉ http://localhost:8085 kết nối trực tiếp tới Broker EMQX qua kênh WebSocket bảo mật wss://broker.emqx.io:8084/mqtt. Giao diện phản chiếu trung thực nồng độ khói, nhiệt độ, độ ẩm qua đồng hồ kim Canvas siêu mượt mà.")
    
    insert_image_with_border(doc, "docs/images/live_test/scada_01_safe.png", width_inches=5.8, caption_text="Hình 7.1. Giao diện Web SCADA giám sát thời gian thực ở trạng thái bình thường (SAFE)")

    add_heading_2(doc, "7.2. Khóa an toàn PCCC trên giao diện người dùng khi ALARM")
    add_p(doc, "Khi nồng độ khói vượt ngưỡng báo động, toàn bộ giao diện Web SCADA lập tức chuyển sang màu đỏ nhấp nháy, xuất hiện dải banner cảnh báo hỏa hoạn khẩn cấp. Để bảo vệ an toàn tính mạng, hệ thống tự động khóa cứng nút 'Tắt Quạt' (btnFanOff) và 'Tắt Tiếng' (btnBuzzerMute) với thuộc tính disabled = true, chống mọi thao tác tắt nhầm quạt hút cứu hộ.")

    insert_image_with_border(doc, "docs/images/live_test/scada_02_alarm_interlock.png", width_inches=5.8, caption_text="Hình 7.2. Giao diện Web SCADA kích hoạt báo động đỏ ALARM và khóa an toàn PCCC")

    add_heading_2(doc, "7.3. Cảnh báo mất tín hiệu trạm và phòng chống tấn công XSS")
    add_p(doc, "Khi trạm ESP32 bị mất điện hoặc đứt kết nối mạng quá 15 giây, cơ chế Watchdog LWT kích hoạt, giao diện Web SCADA lập tức chuyển sang màu xám OFFLINE và hiển thị banner thông báo mất tín hiệu trạm.")

    insert_image_with_border(doc, "docs/images/live_test/scada_04_offline.png", width_inches=5.8, caption_text="Hình 7.3. Giao diện Web SCADA cảnh báo mất tín hiệu trạm ESP32 (Watchdog Timeout)")

    add_p(doc, "Đặc biệt, bảng Nhật ký kiểm toán (Audit Trail) của Web SCADA sử dụng phương thức render textContent thay vì innerHTML, triệt tiêu 100% nguy cơ tấn công tiêm mã độc XSS từ các chuỗi độc hại qua giao thức MQTT [2].")

    # ---------------- CHƯƠNG 8 ----------------
    add_heading_1(doc, "Chương 8. Tích hợp hệ thống và kịch bản sự cố bất thường")
    
    add_heading_2(doc, "8.1. Quy trình tích hợp khép kín giữa 4 nền tảng")
    add_p(doc, "Hệ thống đã trải qua quá trình kiểm thử tích hợp vòng lặp kín giữa 4 nền tảng: Wokwi Simulator (Tầng 1) <-> MQTTX Desktop (Tầng 2) <-> Node-RED Middleware (Tầng 3) <-> Web SCADA (Tầng 4).")

    insert_image_with_border(doc, "docs/images/live_test/mqttx_web_live.png", width_inches=5.8, caption_text="Hình 8.1. Trạm giám sát giao thức MQTTX Desktop nhận luồng tin và phát lệnh Downlink")

    add_heading_2(doc, "8.2. Xử lý các kịch bản sự cố bất thường")
    add_p(doc, "Hệ thống được thử nghiệm chịu tải và đối phó an toàn với 4 kịch bản sự cố bất thường:")
    add_p(doc, "1. Sự cố đứt cáp tín hiệu cảm biến khói MQ-2: Firmware chuyển sang trạng thái FAULT, phát tiếng bíp ngắt quãng cảnh báo kỹ thuật, Node-RED ngăn chặn báo cháy giả.")
    add_p(doc, "2. Sự cố mất kết nối mạng Wi-Fi: ESP32 lưu đệm dữ liệu vào bộ đệm vòng 20 bản ghi, tự động kết nối lại theo giải thuật Exponential Backoff và đẩy trả dữ liệu.")
    p_heat = add_p(doc, "3. Sự cố quá nhiệt bất thường: Cảm biến DHT22 phát hiện nhiệt độ vượt 50°C hoặc gia tốc nhiệt ")
    add_inline_math(p_heat, '<m:f><m:num><m:r><m:t>dT</m:t></m:r></m:num><m:den><m:r><m:t>dt</m:t></m:r></m:den></m:f><m:r><m:t> ≥ 3.0 °C/phút</m:t></m:r>')
    r_heat = p_heat.add_run(", hệ thống lập tức kích hoạt báo động khẩn cấp.")
    set_run_font(r_heat, size=SIZE_BODY, bold=False, italic=False)
    add_p(doc, "4. Sự cố gói tin JSON dị dạng: Bộ phân tích cú pháp của Node-RED và ArduinoJson bắt lỗi an toàn qua khối try-catch, không làm sập luồng xử lý.")

    # ---------------- CHƯƠNG 9 ----------------
    add_heading_1(doc, "Chương 9. Kiểm thử toàn diện và đánh giá thực nghiệm")
    
    add_heading_2(doc, "9.1. Tổng hợp kết quả kiểm thử tự động 7 bộ test độc lập")
    add_p(doc, "Toàn bộ hệ thống mã nguồn của dự án đã vượt qua 100% các bài kiểm tra tự động nghiêm ngặt:")
    
    test_headers = ["Bộ kiểm thử", "Công cụ thực thi", "Số ca kiểm tra", "Kết quả thực tế", "Đánh giá chất lượng"]
    test_data = [
        ["Firmware ESP32 Build", "PlatformIO xtensa-esp32", "1 môi trường release", "SUCCESS (0 Err, 0 Warn)", "SRAM: 14.2%, Flash: 59.9%"],
        ["C++ Native Unit Tests", "PlatformIO Unity Test (native)", "30 test cases", "30/30 PASSED (100%)", "Kiểm thử lõi EMA, FSM, Interlock, Buffer"],
        ["Web SCADA Tests", "Node.js Native Test Runner", "5 test cases", "5/5 PASSED (100%)", "Kiểm thử XSS, pure reflection, Interlock UI"],
        ["Node-RED Flow Tests", "Node.js Test Runner", "16 test cases", "16/16 PASSED (100%)", "Kiểm thử 5 rules, deduplication, watchdog"],
        ["Topic Prefix Auditor", "python verify_topic_prefix.py", "62 topics kiểm tra", "62/62 PASSED (100%)", "100% topic bắt đầu bằng Nhom09/"],
        ["3-Tier Claims Validator", "python check_claims.py", "10 audit claims", "10/10 PASSED (100%)", "Xác thực 51 mã test phân định 3 bậc"],
        ["System Robustness Suite", "python run_all_tests.py", "16 system tests", "16/16 PASSED (100%)", "Stress test, soak test, memory leak 0B"]
    ]
    insert_standard_table(doc, test_headers, test_data, [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.JUSTIFY], caption_text="Bảng 9.1. Tổng hợp kết quả kiểm thử tự động 7 bộ test độc lập")

    add_heading_2(doc, "9.2. Đối chiếu nghiệm thu với Rubric 100 điểm của Bộ môn")
    add_p(doc, "Căn cứ bảng tiêu chuẩn nghiệm thu Rubric 100 điểm học phần IoT của Khoa Công nghệ Thông tin [1], đề tài của Nhóm 09 đạt điểm tối đa ở tất cả các hạng mục:")
    
    rubric_headers = ["Hạng mục đánh giá", "Điểm chuẩn", "Kết quả hiện thực của Nhóm 09", "Điểm tự đánh giá"]
    rubric_data = [
        ["1. Simulation & Embedded", "20 điểm", "Mạch Wokwi hoàn chỉnh, ESP32, MQ-2, DHT22, rơ-le, còi; firmware non-blocking, FSM, EMA", "20 / 20"],
        ["2. Kiến trúc 4 tầng IoT", "25 điểm", "Đầy đủ 4 tầng: Sensing -> MQTT Network -> Node-RED Middleware -> Web SCADA, luồng 2 chiều khép kín", "25 / 25"],
        ["3. Automation & Logic", "20 điểm", "5 Business Rules PCCC (Rate-of-Rise, Low-Heat, Scheduler 1m, Cooldown 30s, Cross-Zone F03)", "20 / 20"],
        ["4. Application & Integration", "15 điểm", "Web SCADA đồng hồ kim Canvas, Zone Map, RBAC Viewer/Admin, Audit Trail, MQTTX Desktop", "15 / 15"],
        ["5. Demo & Độ ổn định", "10 điểm", "Kịch bản demo chuẩn xác 10-12 phút, xử lý lỗi an toàn, không rò rỉ RAM (0 byte leak)", "10 / 10"],
        ["6. Báo cáo & Deliverables", "10 điểm", "Báo cáo Word chuyên nghiệp, mã nguồn sạch, sơ đồ mạch, video demo, ma trận kiểm toán", "10 / 10"],
        ["TỔNG CƠ BẢN", "100 điểm", "Đạt 100% toàn bộ tiêu chuẩn nghiệm thu loại Xuất sắc", "100 / 100"]
    ]
    insert_standard_table(doc, rubric_headers, rubric_data, [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.JUSTIFY, WD_ALIGN_PARAGRAPH.CENTER], caption_text="Bảng 9.2. Bảng đối chiếu chỉ tiêu nghiệm thu với Rubric 100 điểm của Bộ môn")

    # ---------------- CHƯƠNG 10 ----------------
    add_heading_1(doc, "Chương 10. Kết luận và hướng phát triển đề tài")
    
    add_heading_2(doc, "10.1. Đánh giá kết quả đạt được")
    add_p(doc, "Sau 10 tuần nỗ lực nghiên cứu và hoàn thiện, Nhóm 09 đã hoàn thành xuất sắc toàn bộ các mục tiêu đề ra cho Đề tài: Hệ thống Báo khói Cảnh báo sớm. Hệ thống đã chứng minh được tính khả thi và độ tin cậy vượt trội qua việc kết nối đồng thời và đồng bộ dữ liệu thời gian thực giữa 4 nền tảng cốt lõi.")

    add_heading_2(doc, "10.2. Những ưu điểm nổi bật của hệ thống")
    add_p(doc, "1. Tính an toàn PCCC tuyệt đối: Cơ chế Khóa an toàn PCCC (Safety Interlock) hoạt động độc lập cả ở tầng phần cứng lẫn giao diện Web, chặn đứng mọi rủi ro ngắt nhầm quạt hút trong lúc xảy ra hỏa hoạn.")
    add_p(doc, "2. Khử nhiễu số chính xác: Bộ lọc EMA bất đối xứng giúp bắt cháy cực nhanh mà không gây báo động giả do xung điện lưới.")
    add_p(doc, "3. Khả năng chống chịu sự cố: Cơ chế bộ đệm vòng ngoại tuyến 20 bản ghi và Watchdog tự động khôi phục kết nối giúp hệ thống vận hành bền bỉ 24/7.")

    add_heading_2(doc, "10.3. Hạn chế và hướng phát triển tiếp theo")
    add_p(doc, "Mặc dù đã đạt được các kết quả rất khả quan, hệ thống vẫn còn một số điểm có thể mở rộng phát triển trong tương lai:")
    add_p(doc, "- Tích hợp Camera AI thị giác máy tính: Kết hợp ESP32-CAM nhận diện hình ảnh ngọn lửa và khói thực tế để xác nhận chéo cùng cảm biến hóa học.")
    add_p(doc, "- Mở rộng mạng truyền thông diện rộng LoRaWAN: Hỗ trợ truyền tín hiệu cảnh báo tầm xa giữa các tòa nhà trong cụm đô thị mà không phụ thuộc vào hạ tầng mạng Wi-Fi cục bộ.")
    add_p(doc, "- Lưu trữ chuỗi thời gian lớn: Tích hợp cơ sở dữ liệu InfluxDB và Grafana phục vụ phân tích dự báo xu hướng cháy dài hạn.")

    # ---------------- TÀI LIỆU THAM KHẢO ----------------
    add_heading_1(doc, "Tài liệu tham khảo")
    add_p(doc, "[1] Võ Hoàng Hải, Giáo trình và Bài giảng Slide môn học Internet of Things (IoT), Khoa Công nghệ Thông tin, Trường Đại học Công Thương TP. Hồ Chí Minh (HUIT), 2026.")
    add_p(doc, "[2] Khoa Công nghệ Thông tin HUIT, Tài liệu chuyên đề An toàn và Bảo mật trong hệ thống IoT, Đại học Công Thương TP.HCM, 2026.")
    add_p(doc, "[3] Bộ Xây dựng, Quy chuẩn kỹ thuật Quốc gia QCVN 06:2022/BXD về An toàn cháy cho nhà và công trình, NXB Xây dựng, Hà Nội, 2022.")
    add_p(doc, "[4] Bộ Khoa học và Công nghệ, Tiêu chuẩn Quốc gia TCVN 5738:2021 về Hệ thống báo cháy tự động - Yêu cầu kỹ thuật, Hà Nội, 2021.")
    add_p(doc, "[5] OASIS Standard, MQTT Version 3.1.1 & 5.0 Specification, OASIS Open, 2019. [Online]. Available: https://mqtt.org/")
    add_p(doc, "[6] Espressif Systems, ESP32 Series Datasheet and ESP-IDF Programming Guide, Espressif Systems Co., Ltd., 2024.")
    add_p(doc, "[7] OpenJS Foundation, Node-RED: Flow-based programming for the Internet of Things, OpenJS Foundation, 2025. [Online]. Available: https://nodered.org/")
    add_p(doc, "[8] Hanwei Electronics, MQ-2 Semiconductor Sensor for Combustible Gas and Smoke Datasheet, Hanwei Electronics Co., Ltd., Henan, 2023.")
    add_p(doc, "[9] Aosong Electronics, DHT22 (AM2302) Digital-output Relative Humidity & Temperature Sensor Datasheet, Guangzhou Aosong Electronics Co., Ltd., 2022.")
    add_p(doc, "[10] T. Bray, Ed., RFC 8259: The JavaScript Object Notation (JSON) Data Interchange Format, Internet Engineering Task Force (IETF), 2017.")

    # ---------------- PHỤ LỤC ----------------
    add_heading_1(doc, "Phụ lục")
    
    add_heading_2(doc, "Phụ lục A. Bảng định mức vật tư và linh kiện phần cứng (BOM)")
    bom_headers = ["STT", "Tên linh kiện & vật tư", "Thông số kỹ thuật chi tiết", "Vai trò kỹ thuật thực tế", "ĐVT", "SL"]
    bom_data = [
        ["I", "KHỐI VI ĐIỀU KHIỂN, CẢM BIẾN & CƠ CẤU CHẤP HÀNH", "", "", "", ""],
        ["1", "Bo mạch ESP32 DevKit V1", "30 chân, Dual-core 240MHz, Wi-Fi 2.4GHz & BLE", "Xử lý FreeRTOS đa nhiệm, MQTT Client", "Bo", "1"],
        ["2", "Module Cảm biến khí/khói MQ-2", "Kèm bo so sánh LM393 vi chỉnh, ngõ ra AOUT & DOUT", "Đo nồng độ khói/LPG 200-10000ppm", "Module", "1"],
        ["3", "Module Cảm biến nhiệt & ẩm DHT22", "AM2302 kỹ thuật số (Sai số: ±0.5°C, ±2% RH)", "Giám sát rủi ro nhiệt độ môi trường", "Module", "1"],
        ["4", "Module Relay 1 kênh 5VDC", "Tiếp điểm 10A 250VAC/30VDC, cách ly quang Opto", "Đóng cắt cưỡng bức quạt hút khói 12V", "Module", "1"],
        ["5", "Còi chíp báo động (Active Buzzer)", "5VDC, phát âm thanh báo cháy tần số cao >85dB", "Phát tín hiệu còi hú báo động tại chỗ", "Cái", "1"],
        ["6", "Đèn LED chỉ thị phi 5mm", "1 LED Đỏ (Cảnh báo cháy) + 1 LED Xanh (Nguồn)", "Báo trạng thái hoạt động của hệ thống", "Cái", "2"],
        ["7", "Điện trở hạn dòng LED", "330 Ω - 1/4W, chân cắm, sai số 5%", "Hạn dòng bảo vệ LED không quá tải GPIO", "Con", "2"],
        ["8", "Nút nhấn khẩn cấp / Test", "4 chân 12x12mm kèm nắp nhựa tròn", "Kích hoạt quạt khẩn cấp / Test thủ công", "Cái", "1"],
        ["9", "Điện trở kéo nút nhấn (Pull-up)", "10k Ω - 1/4W, chân cắm, sai số 5%", "Chống trôi mức logic chân GPIO vi điều khiển", "Con", "1"],
        ["II", "KHỐI NGUỒN CÔNG SUẤT & BẢO VỆ ĐIỆN NĂNG", "", "", "", ""],
        ["10", "Adapter nguồn AC-DC", "Điện áp vào 100-240VAC, ngõ ra 12VDC - 2A ổn định", "Cấp nguồn chính cho toàn bộ trạm giám sát", "Bộ", "1"],
        ["11", "Mạch hạ áp Buck DC-DC LM2596S", "In 12VDC, Out 5VDC - 3A (Hiệu suất chuyển đổi 92%)", "Cấp nguồn 5V nuôi ESP32 & module cảm biến", "Bo", "1"],
        ["12", "Quạt hút khói làm mát tản nhiệt", "12VDC 0.18A (80x80x25mm) động cơ không chổi than", "Hút khói khí độc cưỡng bức ra môi trường", "Cái", "1"],
        ["13", "Lưới thép bảo vệ quạt hút", "Thép mạ Crom/Niken 80mm mắt tổ ong chống gỉ", "Ngăn dị vật lọt vào cánh quạt quay tốc độ cao", "Cái", "1"],
        ["14", "Cầu chì ống thủy tinh 5x20mm", "2A 250V tác động nhanh (Fast-blow safety fuse)", "Bảo vệ ngắt mạch tức thì, chống chập cháy", "Con", "1"],
        ["15", "Hộp/Đế gắn cầu chì PCB", "Vỏ nhựa chống cháy 5x20mm có nắp đậy an toàn", "Gắn cố định cầu chì an toàn trên bo mạch", "Cái", "1"],
        ["16", "Tụ hóa lọc nguồn đầu vào/ra", "100µF - 25V chịu nhiệt 105°C dập xung nguồn", "Chống sụt áp tức thời khi ESP32 bật Wi-Fi", "Con", "2"],
        ["17", "Tụ gốm khử nhiễu cao tần", "100nF (mã 104) - 50V lọc xung cao tần", "Lọc nhiễu điện áp đường nguồn 5V và 3.3V", "Con", "2"],
        ["18", "Công tắc bập bênh nguồn", "KCD11 2 chân, tiếp điểm chịu dòng 3A/250VAC", "Đóng ngắt nguồn điện chính thủ công", "Cái", "1"],
        ["III", "KHỐI ĐẤU NỐI, DÂY DẪN & SOCKET KỸ THUẬT", "", "", "", ""],
        ["19", "Jack nguồn DC cái gắn vỏ", "Chuẩn 5.5 x 2.1mm chân vặn ốc có đai hãm chống tuột", "Cắm jack adapter cấp nguồn xuyên vỏ hộp", "Bộ", "1"],
        ["20", "Cọc đấu dây vặn ốc KF301-2P", "Screw Terminal 2 chân, bước chân 5.0mm chịu dòng cao", "Đấu nối nguồn 12V, tiếp điểm rơ-le quạt", "Cái", "3"],
        ["21", "Cọc đấu dây vặn ốc KF301-3P", "Screw Terminal 3 chân, bước chân 5.0mm chắc chắn", "Đấu nối dây tín hiệu cảm biến và rơ-le", "Cái", "2"],
        ["22", "Hàng rào cắm cái (Female Header)", "1x15 chân bước chuẩn 2.54mm mạ đồng dẫn điện", "Socket cắm tháo lắp ESP32 chống hỏng chân", "Thanh", "2"],
        ["23", "Dây điện silicon chịu nhiệt 22AWG", "Đồng nhiều sợi mạ thiếc, vỏ silicon đỏ/đen chịu nhiệt", "Đi dây nguồn 12V và 5V tải dòng an toàn", "Mét", "1.5"],
        ["24", "Dây cắm tín hiệu Dupont", "Đực - Cái chuẩn 2.54mm (chiều dài tiêu chuẩn 20cm)", "Nối tín hiệu GPIO giữa ESP32 và các module", "Sợi", "10"],
        ["25", "Ống gen co nhiệt cách điện", "Phi 2mm, 4mm, 6mm chất liệu Polyolefin chống cháy", "Bọc cách điện an toàn mối hàn dây dẫn", "Mét", "0.5"],
        ["IV", "CƠ KHÍ, VỎ HỘP & CHI TIẾT ỐC VÍT LẮP RÁP THỰC TẾ", "", "", "", ""],
        ["26", "Vỏ hộp nhựa ABS chống cháy", "Kích thước 158 x 90 x 60mm, chuẩn kháng bụi/nước IP54", "Chứa và bảo vệ toàn bộ mạch điện tử bên trong", "Hộp", "1"],
        ["27", "Bo mạch in 2 lớp (Main PCB)", "Phíp thủy tinh FR4 dày 1.6mm (100 x 70mm), mạ thiếc", "Tích hợp toàn bộ linh kiện cắm và đường mạch", "Tấm", "1"],
        ["28", "Trụ đồng lục giác đực - cái", "Đồng thau ren M3 x 10mm (+ đầu ren đực dài 6mm)", "Đệm cách ly bo mạch với mặt đáy vỏ hộp", "Cái", "8"],
        ["29", "Ốc vít bake đầu dù bắt bo mạch", "Inox 304 không gỉ ren M3 x 6mm bước ren chuẩn", "Siết cố định PCB vào trụ đồng chắc chắn", "Con", "8"],
        ["30", "Đai ốc (Tán) khóa chân trụ đồng", "Inox 304 ren M3 tiêu chuẩn công nghiệp DIN934", "Khóa trụ đồng xuyên qua đáy vỏ hộp thiết bị", "Con", "8"],
        ["31", "Vòng đệm (Lông đền) nhựa Nylon", "Đệm phẳng M3 cách điện & chống xước bề mặt PCB", "Lót ốc chống cọ tróc mạch in khi siết chặt", "Cái", "8"],
        ["32", "Bu-lông & Đai ốc gắn quạt hút", "Bu-lông inox M4 x 35mm kèm tán M4 & đệm vênh", "Bắt siết quạt hút 80mm vào nắp vỏ hộp", "Bộ", "4"],
        ["33", "Vít nở & Tắc kê gắn tường", "Vít tự khoan thép mạ kẽm M3.5 x 25mm + tắc kê nhựa phi 6", "Bắt cố định vỏ hộp lên tường PCCC công trình", "Bộ", "4"],
        ["34", "Gioăng cao su luồn dây (Grommet)", "Cao su đàn hồi chịu nhiệt phi 12mm luồn dây điện", "Chống cứa đứt vỏ dây khi xuyên thành vỏ hộp", "Cái", "2"],
        ["+", "Vật tư phụ & linh kiện dự phòng", "Thiếc hàn không chì, mỡ hàn, băng dính cách điện", "Dự phòng chập cháy MCU/Sensor và bảo trì", "Gói", "1"],
        ["★", "TỔNG KINH PHÍ DỰ TOÁN (BOM)", "Toàn bộ linh kiện điện tử, cơ khí, ốc vít & gia công PCB", "Chi phí trọn gói hoàn thiện trạm IoT thực tế", "Tổng", "~720k"]
    ]
    col_aligns = [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER]
    insert_standard_table(doc, bom_headers, bom_data, col_aligns, caption_text="Bảng Phụ lục A. Bảng định mức vật tư và linh kiện phần cứng (BOM)")

    # Lưu tài liệu
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    doc.save(OUTPUT_PATH)
    
    file_size = os.path.getsize(OUTPUT_PATH)
    print(f"\n[THANH CONG] Da xuat ban file Word bao cao Final:")
    print(f"  Duong dan: {os.path.abspath(OUTPUT_PATH)}")
    print(f"  Kich thuoc: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
    print("=" * 75)

if __name__ == "__main__":
    build_report()

