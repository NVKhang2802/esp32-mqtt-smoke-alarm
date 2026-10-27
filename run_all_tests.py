# -*- coding: utf-8 -*-
"""
TRÌNH THỰC THI KIỂM THỬ THỐNG NHẤT TOÀN HỆ THỐNG (UNIFIED TEST RUNNER)
Đề tài 04: Hệ thống Báo khói Cảnh báo sớm - Nhóm 04 (N09)
Cú pháp:
    python run_all_tests.py --all       # Chạy toàn bộ 31 Test Cases (Tuần 6 & Tuần 7)
    python run_all_tests.py --week7     # Chạy 16 Test Cases Tuần 7 (Business Rules & Abnormal)
    python run_all_tests.py --week6     # Chạy 15 Test Cases Tuần 6 (Tầng 4 Application E2E)
"""

import sys
import os
import argparse
import subprocess

def configure_console():
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

def run_suite(script_name, label):
    print("\r\n" + "#" * 80)
    print(f"  BẮT ĐẦU CHẠY BỘ KIỂM THỬ: {label.upper()}")
    print(f"  Kịch bản thực thi: {script_name}")
    print("#" * 80 + "\r\n")

    cmd = [sys.executable, script_name]
    ret = subprocess.run(cmd, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    return ret.returncode == 0

def main():
    configure_console()
    parser = argparse.ArgumentParser(description="Unified Test Runner cho Hệ thống Báo khói Nhóm 04")
    parser.add_argument("--week6", action="store_true", help="Chạy bộ kiểm thử E2E Tuần 6 (15 TCs)")
    parser.add_argument("--week7", action="store_true", help="Chạy bộ kiểm thử Business Rules & Abnormal Tuần 7 (16 TCs)")
    parser.add_argument("--week8", action="store_true", help="Chạy bộ kiểm thử End-to-End Integration Tuần 8 (16 TCs)")
    parser.add_argument("--week9", action="store_true", help="Chạy bộ kiểm thử System Test & Robustness Tuần 9 (16 TCs)")
    parser.add_argument("--all", action="store_true", help="Chạy toàn bộ các bộ kiểm thử (63 TCs)")
    args = parser.parse_args()

    # Mặc định nếu không truyền tham số: chạy Tuần 9
    run_w6 = args.week6 or args.all
    run_w7 = args.week7 or args.all
    run_w8 = args.week8 or args.all
    run_w9 = args.week9 or args.all or (not args.week6 and not args.week7 and not args.week8 and not args.week9 and not args.all)

    overall_success = True

    if run_w9:
        ok = run_suite("test_system_robustness_tuan9.py", "Tuần 9: System Test & Robustness Optimization")
        if not ok:
            overall_success = False

    if run_w8:
        ok = run_suite("test_e2e_integration_tuan8.py", "Tuần 8: End-to-End Integration (Milestone M4)")
        if not ok:
            overall_success = False

    if run_w7:
        ok = run_suite("test_business_rules_abnormal_tuan7.py", "Tuần 7: Business Rules & Abnormal Scenarios")
        if not ok:
            overall_success = False

    if run_w6:
        ok = run_suite("test_application_e2e_tuan6.py", "Tuần 6: Tầng 4 Application & MQTT E2E")
        if not ok:
            overall_success = False

    print("\r\n" + "=" * 80)
    if overall_success:
        print("🏆 TẤT CẢ CÁC BỘ KIỂM THỬ ĐÃ HOÀN THÀNH VÀ ĐẠT 100% TIÊU CHUẨN!")
    else:
        print("❌ CÓ BÀI KIỂM THỬ THẤT BẠI. XIN VUI LÒNG KIỂM TRA LẠI LOGS!")
    print("=" * 80 + "\r\n")

    sys.exit(0 if overall_success else 1)

if __name__ == "__main__":
    main()
