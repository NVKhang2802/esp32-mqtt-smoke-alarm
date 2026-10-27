# -*- coding: utf-8 -*-
"""
THƯ VIỆN KIỂM THỬ DÙNG CHUNG (TEST HARNESS & REPORTING FRAMEWORK)
Đề tài 04: Hệ thống Báo khói Cảnh báo sớm - Nhóm 04 (N09)
Cung cấp các hàm chuẩn hóa:
- Ghi nhận kết quả test case (record_test)
- In báo cáo tổng hợp chuẩn Bộ môn (print_test_summary)
- Cấu hình Unicode console trên Windows chống lỗi CP1258
"""

import sys
import io
import time
import json

def configure_utf8_output():
    """Bảo đảm in tiếng Việt có dấu trên console Windows không bị lỗi cp1258"""
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

def record_test(results_list, test_id, name, expected, actual, passed, notes="", latency_ms=0.0):
    """Ghi nhận 1 test case và in định dạng trực quan"""
    record = {
        "id": test_id,
        "name": name,
        "expected": str(expected),
        "actual": str(actual),
        "status": "PASS" if passed else "FAIL",
        "notes": notes,
        "latency_ms": round(latency_ms, 2)
    }
    results_list.append(record)
    
    icon = "✅ PASS" if passed else "❌ FAIL"
    print(f"[{icon}] Test {test_id:02d}: {name}")
    print(f"       Kỳ vọng : {expected}")
    print(f"       Thực tế : {actual}")
    if latency_ms > 0:
        print(f"       Độ trễ  : {latency_ms:.2f} ms")
    if notes:
        print(f"       Ghi chú : {notes}")
    print("-" * 75)
    return passed

def print_test_summary(results_list, title="BẢNG TỔNG HỢP KẾT QUẢ KIỂM THỬ"):
    """In bảng tổng hợp kết quả kiểm thử chuẩn báo cáo đồ án"""
    total = len(results_list)
    passed = sum(1 for r in results_list if r["status"] == "PASS")
    failed = total - passed
    pass_rate = (passed / total * 100.0) if total > 0 else 0.0

    print("\r\n" + "=" * 80)
    print(f"       {title.upper()}")
    print("=" * 80)
    print(f"  Tổng số Test Cases : {total}")
    print(f"  Thành công (PASS)  : {passed} ({pass_rate:.1f}%)")
    print(f"  Thất bại  (FAIL)  : {failed}")
    print("=" * 80)

    print(f"{'TC':<4} | {'Tên Kịch Bản Kiểm Thử':<42} | {'Kết Quả':<8} | {'Ghi Chú'}")
    print("-" * 80)
    for r in results_list:
        icon = "PASS" if r["status"] == "PASS" else "FAIL"
        note = (r["notes"][:24] + "...") if len(r["notes"]) > 24 else r["notes"]
        print(f"#{r['id']:02d} | {r['name'][:42]:<42} | {icon:<8} | {note}")
    print("=" * 80)

    if failed == 0:
        print(f"🎉 KẾT LUẬN: TOÀN BỘ {total}/{total} BÀI TEST ĐẠT CHUẨN (100% PASS)!\r\n")
    else:
        print(f"⚠️ CẢNH BÁO: CÓ {failed} BÀI TEST CHƯA ĐẠT CHUẨN!\r\n")

    return failed == 0
