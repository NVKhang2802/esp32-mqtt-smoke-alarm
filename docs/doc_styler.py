# -*- coding: utf-8 -*-
"""
THƯ VIỆN ĐỊNH DẠNG TÀI LIỆU DÙNG CHUNG (DOC STYLER & XML ENGINE)
Đề tài: Hệ thống Báo khói Cảnh báo sớm - Nhóm 09 (N09)
Khoa Công nghệ Thông tin - Trường Đại học Công Thương TP.HCM (HUIT)

Đóng gói toàn bộ các hàm định dạng bảng biểu, màu sắc, phông chữ Times New Roman
chuẩn quy cách văn bản tốt nghiệp & đồ án học phần IoT.
"""

import sys
import io
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

FONT_FAMILY_PRIMARY = "Times New Roman"
FONT_FAMILY_CODE = "Consolas"

# Bảng màu sắc chuẩn nhận diện tài liệu HUIT
COLOR_NAVY_TITLE = RGBColor(24, 76, 120)     # #184C78
COLOR_BLUE_SUB   = RGBColor(41, 110, 168)    # #296EA8
COLOR_DARK_TEXT  = RGBColor(50, 50, 50)      # #323232
COLOR_MUTED_TEXT = RGBColor(100, 116, 139)  # #64748B

def configure_utf8_console():
    """Bảo đảm in tiếng Việt có dấu trên console Windows"""
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    elif hasattr(sys.stdout, 'buffer'):
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        except Exception:
            pass

def setup_document_margins(doc, top=1.0, bottom=1.0, left=1.0, right=1.0):
    """Thiết lập lề trang chuẩn A4 theo quy chuẩn văn bản HUIT"""
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(top)
        section.bottom_margin = Inches(bottom)
        section.left_margin = Inches(left)
        section.right_margin = Inches(right)

def apply_cell_style(cell, bg_color=None, bold=False, font_size=10, font_name=FONT_FAMILY_PRIMARY, 
                      text_color="000000", align=WD_ALIGN_PARAGRAPH.LEFT, top_pad=100, bot_pad=100):
    """Định dạng màu nền, lề đệm và chữ trong ô bảng Word"""
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
    """Thiết lập đường viền bảng màu pastel tao nhã"""
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
    """Thêm tiêu đề mục cấp 1 chuẩn đồ án"""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = FONT_FAMILY_PRIMARY
    run.font.size = Pt(13.5)
    run.bold = True
    run.font.color.rgb = COLOR_NAVY_TITLE
    return p

def add_heading_2(doc, text):
    """Thêm tiêu đề mục cấp 2 chuẩn đồ án"""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = FONT_FAMILY_PRIMARY
    run.font.size = Pt(12)
    run.bold = True
    run.font.color.rgb = COLOR_BLUE_SUB
    return p

def add_heading_3(doc, text):
    """Thêm tiêu đề mục cấp 3 chuẩn đồ án"""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = FONT_FAMILY_PRIMARY
    run.font.size = Pt(11)
    run.bold = True
    run.font.color.rgb = COLOR_DARK_TEXT
    return p

def add_body_p(doc, text, bold_prefix="", italic=False):
    """Thêm đoạn văn nội dung thường có tiền tố in đậm tùy chọn"""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.2
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = FONT_FAMILY_PRIMARY
        r_pre.font.size = Pt(11)
        r_pre.bold = True
    r = p.add_run(text)
    r.font.name = FONT_FAMILY_PRIMARY
    r.font.size = Pt(11)
    r.italic = italic
    return p

def add_bullet_p(doc, text, bold_prefix="", level=0):
    """Thêm dòng danh sách có dấu chấm tròn (bullet point)"""
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.left_indent = Inches(0.25 * (level + 1))
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = FONT_FAMILY_PRIMARY
        r_pre.font.size = Pt(10.5)
        r_pre.bold = True
    r = p.add_run(text)
    r.font.name = FONT_FAMILY_PRIMARY
    r.font.size = Pt(10.5)
    return p

def add_callout_box(doc, text, box_type="NOTE"):
    """Thêm khung ghi chú / cảnh báo chuyên nghiệp"""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    
    bg_map = {
        "NOTE": ("F0F4F8", "184C78", "📌 LƯU Ý KỸ THUẬT: "),
        "IMPORTANT": ("FFFBEB", "D97706", "⚠️ QUAN TRỌNG: "),
        "SUCCESS": ("ECFDF5", "059669", "✅ KẾT QUẢ ĐẠT ĐƯỢC: ")
    }
    bg_color, border_color, prefix = bg_map.get(box_type, ("F8FAFC", "64748B", "ℹ️ THÔNG TIN: "))
    
    set_table_borders(tbl, color=border_color, sz="6")
    apply_cell_style(cell, bg_color=bg_color, top_pad=140, bot_pad=140)
    p = cell.paragraphs[0]
    p.paragraph_format.line_spacing = 1.2
    r_pre = p.add_run(prefix)
    r_pre.bold = True
    r_pre.font.name = FONT_FAMILY_PRIMARY
    r_pre.font.size = Pt(10.5)
    r = p.add_run(text)
    r.font.name = FONT_FAMILY_PRIMARY
    r.font.size = Pt(10.5)
    
    # Khoảng đệm sau bảng
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(4)

def add_code_block(doc, code_str):
    """Thêm khối mã nguồn hoặc payload JSON định dạng monospace"""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_table_borders(tbl, color="CBD5E1", sz="4")
    apply_cell_style(cell, bg_color="F1F5F9", top_pad=120, bot_pad=120)
    p = cell.paragraphs[0]
    p.paragraph_format.line_spacing = 1.15
    r = p.add_run(code_str)
    r.font.name = FONT_FAMILY_CODE
    r.font.size = Pt(9.5)
    
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(4)
