# -*- coding: utf-8 -*-
"""
TRÌNH THỰC THI KIỂM THỬ THỐNG NHẤT TOÀN HỆ THỐNG (UNIFIED TEST RUNNER)
Đề tài 04: Hệ thống Báo khói Cảnh báo sớm - Nhóm 09 (N09)
Cú pháp:
    python tests/run_all_tests.py --all       # Chạy toàn bộ 63 Test Cases (Tuần 6, 7, 8, 9)
    python tests/run_all_tests.py --week9     # Chạy 16 Test Cases Tuần 9 (System Test & Robustness)
    python tests/run_all_tests.py --week8     # Chạy 16 Test Cases Tuần 8 (End-to-End Integration)
    python tests/run_all_tests.py --week7     # Chạy 16 Test Cases Tuần 7 (Business Rules & Abnormal)
    python tests/run_all_tests.py --week6     # Chạy 15 Test Cases Tuần 6 (Tầng 4 Application E2E)
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

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))

def run_suite(script_name, label):
    script_path = os.path.join(TESTS_DIR, script_name)
    print("\r\n" + "#" * 80)
    print(f"  BẮT ĐẦU CHẠY BỘ KIỂM THỬ: {label.upper()}")
    print(f"  Kịch bản thực thi: {script_name}")
    print("#" * 80 + "\r\n")

    cmd = [sys.executable, script_path]
    ret = subprocess.run(cmd, env={**os.environ, "PYTHONIOENCODING": "utf-8"}, cwd=TESTS_DIR)
    return ret.returncode == 0

def main():
    configure_console()
    parser = argparse.ArgumentParser(description="Unified Test Runner cho Hệ thống Báo khói Nhóm 09")
    parser.add_argument("--week6", action="store_true", help="Chạy bộ kiểm thử E2E Tuần 6 (15 TCs)")
    parser.add_argument("--week7", action="store_true", help="Chạy bộ kiểm thử Business Rules & Abnormal Tuần 7 (16 TCs)")
    parser.add_argument("--week8", action="store_true", help="Chạy bộ kiểm thử End-to-End Integration Tuần 8 (16 TCs)")
    parser.add_argument("--week9", action="store_true", help="Chạy bộ kiểm thử System Test & Robustness Tuần 9 (16 TCs)")
    parser.add_argument("--audit", action="store_true", help="Chạy bộ xác thực 3-Tier Audit Claims")
    parser.add_argument("--all", action="store_true", help="Chạy toàn bộ các bộ kiểm thử (63 TCs + Audit Matrix)")
    args = parser.parse_args()

    run_w6 = args.week6 or args.all
    run_w7 = args.week7 or args.all
    run_w8 = args.week8 or args.all
    run_w9 = args.week9 or args.all or (not args.week6 and not args.week7 and not args.week8 and not args.week9 and not args.audit and not args.all)
    run_audit = args.audit or args.all

    overall_success = True

    if run_audit:
        print("\r\n" + "#" * 80)
        print("  BẮT ĐẦU CHẠY: 3-TIER AUDIT CLAIM VALIDATOR")
        print("#" * 80 + "\r\n")
        claim_script = os.path.join(os.path.dirname(TESTS_DIR), "scripts", "check_claims.py")
        ret = subprocess.run([sys.executable, claim_script], cwd=os.path.dirname(TESTS_DIR))
        if ret.returncode != 0:
            overall_success = False

    if run_w9:
        ok = run_suite("test_tuan9_system_robustness.py", "Tuần 9: System Test & Robustness Optimization")
        if not ok:
            overall_success = False

    if run_w8:
        ok = run_suite("test_tuan8_e2e_integration.py", "Tuần 8: End-to-End Integration (Milestone M4)")
        if not ok:
            overall_success = False

    if run_w7:
        ok = run_suite("test_tuan7_business_rules.py", "Tuần 7: Business Rules & Abnormal Scenarios")
        if not ok:
            overall_success = False

    if run_w6:
        ok = run_suite("test_tuan6_application.py", "Tuần 6: Tầng 4 Application & MQTT E2E")
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

