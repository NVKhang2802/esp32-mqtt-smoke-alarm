# -*- coding: utf-8 -*-
"""
Proxy Runner chuyển tiếp tới tests/run_all_tests.py
Giữ tương thích tuyệt đối cho các lệnh gọi: python run_all_tests.py [args]
"""
import os
import sys

if __name__ == "__main__":
    tests_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests")
    sys.path.insert(0, tests_dir)
    import run_all_tests
    run_all_tests.main()
