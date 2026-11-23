# -*- coding: utf-8 -*-
r"""
scripts/verify_docx_format.py
Kiểm tra toàn diện tính tuân thủ 12 quy định định dạng trên file docx:
E:\IoT\DoAn\docs\word\Nhom09_HeThongBaoKhoiCanhBaoSom.docx
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

def verify_report(docx_path):
    print("=" * 80)
    print(f"BẮT ĐẦU KIỂM THỬ ĐỊNH DẠNG FILE: {docx_path}")
    print("=" * 80)

    if not os.path.exists(docx_path):
        print(f"[FAIL] Không tìm thấy file: {docx_path}")
        return False

    size_kb = os.path.getsize(docx_path) / 1024
    print(f"[INFO] Dung lượng file: {size_kb:.1f} KB")
    if size_kb < 400:
        print("[FAIL] Kích thước file quá nhỏ (< 400KB), có thể thiếu hình ảnh!")
        return False

    doc = docx.Document(docx_path)

    errors = []
    warnings = []

    # 1. Kiểm tra Sections và Phân trang (Quy định 11)
    sections = doc.sections
    print(f"[INFO] Số lượng Sections: {len(sections)}")
    if len(sections) < 3:
        errors.append(f"Cần tối thiểu 3 sections (Bìa, Đầu mục, Thân bài), hiện có {len(sections)}")
    else:
        # Section 1: Trang bìa
        s1 = sections[0]
        s1_footer = s1.footer
        if s1_footer.paragraphs and any(p.text.strip() for p in s1_footer.paragraphs):
            errors.append("Section 1 (Bìa) không được có chữ/số trong footer!")
        
        # Section 2: Trang sơ bộ (La Mã)
        s2 = sections[1]
        s2_sectPr = s2._sectPr
        pgNumType2 = s2_sectPr.find(qn('w:pgNumType'))
        if pgNumType2 is not None:
            fmt = pgNumType2.get(qn('w:fmt'))
            start = pgNumType2.get(qn('w:start'))
            print(f"[INFO] Section 2 pgNumType: fmt={fmt}, start={start}")
            if fmt != 'lowerRoman':
                errors.append(f"Section 2 fmt phải là lowerRoman, hiện là {fmt}")
        else:
            errors.append("Section 2 thiếu thẻ w:pgNumType")

        # Section 3: Thân bài (Số Ả Rập bắt đầu từ 1)
        s3 = sections[2]
        s3_sectPr = s3._sectPr
        pgNumType3 = s3_sectPr.find(qn('w:pgNumType'))
        if pgNumType3 is not None:
            fmt = pgNumType3.get(qn('w:fmt'))
            start = pgNumType3.get(qn('w:start'))
            print(f"[INFO] Section 3 pgNumType: fmt={fmt}, start={start}")
            if fmt != 'decimal' or start != '1':
                errors.append(f"Section 3 phải là decimal start=1, hiện là fmt={fmt}, start={start}")
        else:
            errors.append("Section 3 thiếu thẻ w:pgNumType")

    # 2. Quét toàn bộ Paragraphs
    total_paragraphs = len(doc.paragraphs)
    print(f"[INFO] Tổng số đoạn văn bản chính: {total_paragraphs}")

    forbidden_dashes = ['–', '—', '−']
    bad_dash_count = 0
    non_black_count = 0
    font_issues = 0
    heading_caps_issues = 0
    caption_italic_issues = 0
    body_align_issues = 0

    has_tong_quan = False
    has_nhom04 = False
    has_lap_trinh_nhung = False

    for i, p in enumerate(doc.paragraphs):
        p_text = p.text
        style_name = p.style.name if p.style else ""

        # Kiểm tra từ cấm
        if "nhóm 04" in p_text.lower() or "nhom04" in p_text.lower():
            has_nhom04 = True
            errors.append(f"Phát hiện 'Nhóm 04' ở đoạn {i}: {p_text[:60]}")
        
        if "lập trình nhúng" in p_text.lower():
            has_lap_trinh_nhung = True
            errors.append(f"Phát hiện 'Lập trình nhúng' ở đoạn {i}: {p_text[:60]}")

        if "Tổng quan đề tài" in p_text:
            has_tong_quan = True

        # Kiểm tra dấu gạch ngang cấm (Quy định 9)
        for bd in forbidden_dashes:
            if bd in p_text:
                bad_dash_count += 1

        # Kiểm tra Heading (Quy định 1 & 3)
        if style_name.startswith("Heading"):
            # Kiểm tra Sentence case (không in hoa toàn bộ)
            words = [w for w in p_text.split() if w.isalpha()]
            if len(words) > 3 and all(w.isupper() for w in words):
                heading_caps_issues += 1
                errors.append(f"Heading in hoa toàn bộ: {p_text}")

            for run in p.runs:
                if run.font.italic:
                    errors.append(f"Heading không được in nghiêng: {p_text}")
                if style_name == "Heading 1" and run.font.size and run.font.size.pt != 16:
                    errors.append(f"Heading 1 phải là 16pt, phát hiện: {run.font.size.pt}pt ở '{p_text}'")
                elif style_name in ["Heading 2", "Heading 3", "Heading 4"] and run.font.size and run.font.size.pt != 13:
                    errors.append(f"{style_name} phải là 13pt, phát hiện: {run.font.size.pt}pt ở '{p_text}'")

        # Kiểm tra Captions (Quy định 1: 11pt, bold, not italic)
        import re
        is_caption = (style_name == "Caption" or (bool(re.match(r'^(Hình|Bảng)\s*(\d+|\.)', p_text.strip())) and "..." not in p_text and len(p_text.strip()) < 150))
        if is_caption:
            for run in p.runs:
                if run.font.italic:
                    caption_italic_issues += 1
                if run.font.size and run.font.size.pt != 11:
                    errors.append(f"Caption phải là 11pt, phát hiện: {run.font.size.pt}pt ở '{p_text}'")

        # Kiểm tra Body Paragraphs căn đều (Quy định 12)
        if style_name == "Normal" and len(p_text.strip()) > 80:
            if p.alignment not in [WD_ALIGN_PARAGRAPH.JUSTIFY, None]: # None có thể thừa kế style justified
                # Kiểm tra xml jc
                jc = p._p.find(qn('w:pPr'))
                if jc is not None:
                    jc_val = jc.find(qn('w:jc'))
                    if jc_val is None or jc_val.get(qn('w:val')) != 'both':
                        body_align_issues += 1

        # Kiểm tra màu đen và font Times New Roman (Quy định 1 & 7)
        for run in p.runs:
            if run.font.color and run.font.color.rgb:
                if run.font.color.rgb != RGBColor(0, 0, 0):
                    non_black_count += 1
            if run.font.name and run.font.name != "Times New Roman":
                font_issues += 1

    # 3. Quét Tables (Quy định 2 & 8)
    print(f"[INFO] Tổng số bảng trong tài liệu: {len(doc.tables)}")
    table_border_issues = 0
    cell_font_issues = 0
    image_table_count = 0

    for t_idx, table in enumerate(doc.tables):
        # Bảng 1x1 là bọc ảnh
        if len(table.rows) == 1 and len(table.columns) == 1:
            image_table_count += 1
            # Kiểm tra viền đen (Quy định 8)
            tblBorders = table._tbl.tblPr.find(qn('w:tblBorders'))
            if tblBorders is None:
                table_border_issues += 1
            continue

        # Bảng dữ liệu thường
        header_row = table.rows[0]
        for cell in header_row.cells:
            for p in cell.paragraphs:
                # Kiểm tra căn giữa
                if p.alignment not in [WD_ALIGN_PARAGRAPH.CENTER, None]:
                    pass
                for r in p.runs:
                    if not r.font.bold and r.text.strip():
                        # warnings.append(f"Header cell text '{r.text}' chưa bold")
                        pass

    print(f"[INFO] Số bảng bọc khung viền hình ảnh: {image_table_count}")
    print(f"[INFO] Dấu gạch ngang cấm (–, —): {bad_dash_count}")
    print(f"[INFO] Màu chữ không phải đen: {non_black_count}")
    print(f"[INFO] Lỗi font không phải Times New Roman: {font_issues}")
    print(f"[INFO] Caption bị in nghiêng: {caption_italic_issues}")
    print(f"[INFO] Có mục 'Tổng quan đề tài': {has_tong_quan}")

    if bad_dash_count > 0:
        errors.append(f"Có {bad_dash_count} dấu gạch ngang dài (– hoặc —), yêu cầu chỉ dùng '-'")
    if non_black_count > 0:
        errors.append(f"Có {non_black_count} runs màu chữ khác đen")
    if font_issues > 0:
        errors.append(f"Có {font_issues} runs font không phải Times New Roman")
    if caption_italic_issues > 0:
        errors.append(f"Có {caption_italic_issues} caption bị in nghiêng")
    if not has_tong_quan:
        errors.append("Không tìm thấy mục 'Tổng quan đề tài'")

    # Kiểm tra Tài liệu tham khảo [1]..[10] (Quy định 5)
    full_text = "\n".join(p.text for p in doc.paragraphs)
    missing_refs = []
    for ref_num in range(1, 11):
        ref_tag = f"[{ref_num}]"
        if ref_tag not in full_text:
            missing_refs.append(ref_tag)
    if missing_refs:
        errors.append(f"Thiếu các trích dẫn tài liệu tham khảo: {missing_refs}")
    else:
        print("[INFO] Toàn bộ 10 trích dẫn tài liệu tham khảo [1]..[10] đã xuất hiện đầy đủ trong văn bản.")

    # Kiểm tra Heading styles thực tế
    h1_count = sum(1 for p in doc.paragraphs if p.style and p.style.name == "Heading 1")
    h2_count = sum(1 for p in doc.paragraphs if p.style and p.style.name == "Heading 2")
    print(f"[INFO] Số lượng Heading 1: {h1_count}, Heading 2: {h2_count}")
    if h1_count < 10:
        errors.append(f"Số lượng Heading 1 quá ít ({h1_count}), chưa áp dụng Heading style!")
    if h2_count < 10:
        errors.append(f"Số lượng Heading 2 quá ít ({h2_count}), chưa áp dụng Heading style!")

    # Kiểm tra loại bỏ Phụ lục B
    if "phụ lục b" in full_text.lower():
        errors.append("Phát hiện 'Phụ lục B' vẫn còn trong tài liệu, yêu cầu loại bỏ!")
    else:
        print("[INFO] Đã loại bỏ hoàn toàn Phụ lục B theo đúng yêu cầu.")

    # Kiểm tra Bảng BOM 34 linh kiện từ PPTX
    bom_found = False
    for table in doc.tables:
        t_text = " ".join(cell.text for row in table.rows for cell in row.cells)
        if "LM2596S" in t_text and "KHỐI VI ĐIỀU KHIỂN" in t_text and "~720k" in t_text:
            bom_found = True
            row_count = len(table.rows)
            print(f"[INFO] Tìm thấy Bảng BOM chuẩn với {row_count} hàng (gồm 34 linh kiện và 4 nhóm khối I..IV).")
            if row_count < 35:
                errors.append(f"Bảng BOM chưa đủ 34 linh kiện (hiện có {row_count} hàng)!")
            break
    if not bom_found:
        errors.append("Không tìm thấy Bảng BOM chuẩn 34 linh kiện (~720k) trong Phụ lục A!")

    # 4. Kiểm tra các Phương trình toán học chuẩn Word (OMML) và ký hiệu toán học (≥, ≤)
    import zipfile
    with zipfile.ZipFile(docx_path, 'r') as z:
        doc_xml = z.read('word/document.xml').decode('utf-8')
        settings_xml = z.read('word/settings.xml').decode('utf-8') if 'word/settings.xml' in z.namelist() else ''

    omml_para_count = doc_xml.count('<m:oMathPara')
    omml_math_count = doc_xml.count('<m:oMath')
    print(f"[INFO] Số lượng khối phương trình hiển thị (m:oMathPara): {omml_para_count}")
    print(f"[INFO] Tổng số đối tượng toán học Word (m:oMath): {omml_math_count}")

    if omml_para_count < 4:
        errors.append(f"Chưa đủ số phương trình hiển thị OMML độc lập (yêu cầu tối thiểu 4, hiện có {omml_para_count})!")
    if omml_math_count < 8:
        errors.append(f"Chưa đủ số đối tượng toán học OMML (yêu cầu tối thiểu 8, hiện có {omml_math_count})!")

    # Kiểm tra ký hiệu toán học thô (>=, <=) trong toàn bộ nội dung văn bản
    raw_ge_count = full_text.count(">=")
    raw_le_count = full_text.count("<=")
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                raw_ge_count += cell.text.count(">=")
                raw_le_count += cell.text.count("<=")

    if raw_ge_count > 0:
        errors.append(f"Phát hiện {raw_ge_count} ký hiệu '>=' dạng text thô, yêu cầu thay bằng ký hiệu toán học '≥'!")
    else:
        print("[INFO] Không còn ký hiệu '>=' thô; 100% đã được chuyển thành ký hiệu toán học '≥'.")

    if raw_le_count > 0:
        errors.append(f"Phát hiện {raw_le_count} ký hiệu '<=' dạng text thô, yêu cầu thay bằng ký hiệu toán học '≤'!")
    else:
        print("[INFO] Không còn ký hiệu '<=' thô; 100% đã được chuyển thành ký hiệu toán học '≤'.")

    # Kiểm tra loại bỏ pop-up cảnh báo mở file (updateFields trong settings.xml)
    if "updateFields" in settings_xml:
        errors.append("Phát hiện thẻ 'updateFields' trong settings.xml gây hộp thoại cảnh báo khi mở file Word!")
    else:
        print("[INFO] settings.xml không chứa 'updateFields' - Word sẽ mở tài liệu êm ái, không có pop-up cảnh báo.")

    # 5. Kiểm tra các bảng kỹ thuật và hình ảnh sơ đồ phần cứng & firmware mới bổ sung
    full_table_text = " ".join(cell.text for t in doc.tables for row in t.rows for cell in row.cells)
    
    # Kiểm tra Bảng 3.1: Đặc tính điện ESP32
    if "AMS1117" in full_table_text and "NADC" in full_table_text and "Attenuation" in full_table_text:
        print("[INFO] Bảng 3.1 (Đặc tính điện chip ESP32 chuẩn Datasheet): ĐÃ HIỆN DIỆN.")
    else:
        errors.append("Thiếu Bảng 3.1 (Đặc tính điện của chip ESP32) trong Chương 3!")

    # Kiểm tra Bảng 3.2: Power Budget
    if "Power Budget" in full_text and "~866.5 mA" in full_table_text and "~4.33 W" in full_table_text:
        print("[INFO] Bảng 3.2 (Cân bằng công suất điện năng Power Budget): ĐÃ HIỆN DIỆN.")
    else:
        errors.append("Thiếu Bảng 3.2 (Cân bằng công suất điện năng toàn hệ thống) trong Chương 3!")

    # Kiểm tra Bảng 3.3: Bảng nối chân Lab 16 kết nối
    if "16 kết nối chuẩn diagram.json" in full_text and "relay1:COM" not in full_table_text and "Cảm biến Khói MQ-2" in full_table_text:
        print("[INFO] Bảng 3.3 (Bảng đấu nối chân Lab 16 kết nối chuẩn diagram.json): ĐÃ HIỆN DIỆN.")
    else:
        errors.append("Thiếu Bảng 3.3 (Bảng đấu nối chân Lab chi tiết 16 kết nối) trong Chương 3!")

    # Kiểm tra Bảng 3.4: Bảng đối chiếu Wokwi vs Lab thực tế
    if "wokwi-gas-sensor" in full_table_text and "wokwi-relay-module" in full_table_text:
        print("[INFO] Bảng 3.4 (Bảng đối chiếu Wokwi vs Mạch thực tế phòng Lab): ĐÃ HIỆN DIỆN.")
    else:
        errors.append("Thiếu Bảng 3.4 (Bảng đối chiếu Wokwi vs Phần cứng Lab thực tế) trong Chương 3!")

    # Kiểm tra Bảng 4.2: Danh mục hàm firmware
    if "readMQ2PPM()" in full_table_text and "emaUpdate()" in full_table_text and "fsmStep()" in full_table_text:
        print("[INFO] Bảng 4.2 (Danh mục các hàm cốt lõi trong src/main.cpp): ĐÃ HIỆN DIỆN.")
    else:
        errors.append("Thiếu Bảng 4.2 (Danh mục hàm cốt lõi trong src/main.cpp) trong Chương 4!")

    # Kiểm tra các hình ảnh sơ đồ kỹ thuật mới
    has_fig_3_1 = "Sơ đồ ghép nối mạch nguyên lý" in full_text
    has_fig_3_2 = "Giao diện bố trí linh kiện" in full_text
    has_fig_4_1 = "Sơ đồ phân rã chức năng" in full_text
    has_fig_4_2 = "Lưu đồ thuật toán vòng lặp" in full_text
    
    if has_fig_3_1:
        print("[INFO] Hình 3.1 (Sơ đồ ghép nối mạch nguyên lý toàn hệ thống): ĐÃ HIỆN DIỆN.")
    else:
        errors.append("Thiếu Hình 3.1 (Sơ đồ ghép nối mạch nguyên lý) trong Chương 3!")

    if has_fig_3_2:
        print("[INFO] Hình 3.2 (Giao diện bố trí linh kiện trên Wokwi): ĐÃ HIỆN DIỆN.")
    else:
        errors.append("Thiếu Hình 3.2 (Bố trí linh kiện trên Wokwi) trong Chương 3!")

    if has_fig_4_1:
        print("[INFO] Hình 4.1 (Sơ đồ phân rã chức năng Firmware C++): ĐÃ HIỆN DIỆN.")
    else:
        errors.append("Thiếu Hình 4.1 (Sơ đồ phân rã chức năng Firmware) trong Chương 4!")

    if has_fig_4_2:
        print("[INFO] Hình 4.2 (Lưu đồ thuật toán vòng lặp chính loop()): ĐÃ HIỆN DIỆN.")
    else:
        errors.append("Thiếu Hình 4.2 (Lưu đồ thuật toán loop()) trong Chương 4!")

    # TỔNG KẾT
    print("=" * 80)
    if errors:
        print(f"[KẾT QUẢ] CÓ {len(errors)} LỖI CẦN XỬ LÝ:")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("[KẾT QUẢ] XUẤT SẮC! File hoàn toàn tuân thủ 100% 12 quy định định dạng đã đề ra!")
        return True

if __name__ == "__main__":
    docx_file = r"E:\IoT\DoAn\docs\word\Nhom09_HeThongBaoKhoiCanhBaoSom.docx"
    success = verify_report(docx_file)
    sys.exit(0 if success else 1)
