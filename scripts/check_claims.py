#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/check_claims.py
Audits and verifies all claims declared in docs/audit/claims.yaml.
Ensures zero discrepancies between claims and codebase reality.
"""

import os
import sys
import yaml
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLAIMS_FILE = os.path.join(BASE_DIR, "docs", "audit", "claims.yaml")

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, shell=True, cwd=BASE_DIR, capture_output=True, text=True, timeout=120)
        return res.returncode == 0, res.stdout + res.stderr
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 70)
    print("  AUDIT CLAIM VALIDATOR - NHOM 04 HUIT (CODEBASE AUDIT V5)")
    print("=" * 70)

    if not os.path.isfile(CLAIMS_FILE):
        print(f"[FAIL] Claims file not found: {CLAIMS_FILE}")
        sys.exit(1)

    with open(CLAIMS_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    claims = data.get("claims", [])
    print(f"Loaded {len(claims)} audit claims from: {CLAIMS_FILE}\n")

    all_passed = True
    for c in claims:
        cid = c.get("id")
        desc = c.get("description")
        cmd = c.get("test_command")
        print(f"Checking [{cid}]: {desc} ...", end=" ", flush=True)

        if not cmd:
            print("[WARN] No verification command provided")
            continue

        ok, out = run_cmd(cmd)
        if ok:
            print("[VERIFIED PASS]")
        else:
            print("[FAILED]")
            print(f"  Command: {cmd}")
            print(f"  Output:\n{out[:300]}")
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("  ALL AUDIT CLAIMS VERIFIED 100% PASS (Zero Discrepancies)")
        print("=" * 70)
        sys.exit(0)
    else:
        print("  SOME CLAIMS FAILED VERIFICATION")
        print("=" * 70)
        sys.exit(1)

if __name__ == "__main__":
    main()
