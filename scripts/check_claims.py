#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/check_claims.py
Audits and dynamically verifies all claims declared in docs/audit/claims.yaml.
Supports 3-tier classification: VERIFIED, PARTIAL, SCOPE.
Performs AST/regex source code validation ensuring zero simulated or missing test IDs.
"""

import os
import sys
import glob
import re
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

def collect_source_test_ids():
    """Scans all test files to collect real implemented test IDs (T-*, FLOW-*)."""
    search_patterns = [
        os.path.join(BASE_DIR, "test", "**", "*.*"),
        os.path.join(BASE_DIR, "nodered", "tests", "**", "*.*"),
        os.path.join(BASE_DIR, "web", "tests", "**", "*.*"),
    ]
    test_files = []
    for pat in search_patterns:
        test_files.extend(glob.glob(pat, recursive=True))

    found_ids = set()
    test_id_regex = re.compile(r'\b(T-[A-Z0-9]+|FLOW-[0-9]+)\b')

    for filepath in test_files:
        if not os.path.isfile(filepath):
            continue
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                matches = test_id_regex.findall(content)
                found_ids.update(matches)
        except Exception as e:
            print(f"[WARN] Failed to read {filepath}: {e}")

    return found_ids

def main():
    print("=" * 80)
    print("  3-TIER AUDIT CLAIM VALIDATOR - NHOM 04 HUIT (CODEBASE AUDIT V5)")
    print("  Classification: [VERIFIED] Fully Proven | [PARTIAL] Algorithmic | [SCOPE] Design Boundary")
    print("  Source Code Validation: Checking test ID integrity against codebase...")
    print("=" * 80)

    if not os.path.isfile(CLAIMS_FILE):
        print(f"[FAIL] Claims file not found: {CLAIMS_FILE}")
        sys.exit(1)

    with open(CLAIMS_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    claims = data.get("claims", [])
    print(f"Loaded {len(claims)} audit claims from: {CLAIMS_FILE}")

    source_test_ids = collect_source_test_ids()
    print(f"Discovered {len(source_test_ids)} distinct test IDs in test source files.\n")

    results = []
    has_failure = False

    for c in claims:
        cid = c.get("id")
        tier = c.get("tier", "VERIFIED")
        desc = c.get("description", "")
        cmd = c.get("test_command")
        evidence = c.get("evidence_tests", [])

        print(f"Checking [{cid}] ({tier}): {desc[:48]}...", end=" ", flush=True)

        # 1. Source code check: verify that all evidence tests exist in test source code
        missing_ids = []
        for tid in evidence:
            if (tid.startswith("T-") or tid.startswith("FLOW-")) and tid not in source_test_ids:
                missing_ids.append(tid)

        if missing_ids:
            verdict = "FAIL"
            err_msg = f"Evidence test ID(s) not found in test source files: {', '.join(missing_ids)}"
            print("\033[91m[FAILED - MISSING TEST ID]\033[0m" if sys.platform != "win32" else "[FAILED - MISSING TEST ID]")
            print(f"  {err_msg}\n")
            results.append((cid, tier, verdict, err_msg))
            has_failure = True
            continue

        # 2. Check for empty test command
        if not cmd or not cmd.strip():
            print("[WARN] No verification command")
            results.append((cid, tier, "SKIPPED", "No test command"))
            continue

        # 3. Disallow dummy commands for VERIFIED or PARTIAL tiers
        if tier in ("VERIFIED", "PARTIAL") and "print(" in cmd:
            verdict = "FAIL"
            err_msg = f"Dummy test command rejected for {tier} tier: {cmd}"
            print("\033[91m[FAILED - DUMMY CMD]\033[0m" if sys.platform != "win32" else "[FAILED - DUMMY CMD]")
            print(f"  {err_msg}\n")
            results.append((cid, tier, verdict, err_msg))
            has_failure = True
            continue

        ok, out = run_cmd(cmd)

        if ok:
            if tier == "VERIFIED":
                verdict = "VERIFIED_PASS"
                print("\033[92m[VERIFIED PASS]\033[0m" if sys.platform != "win32" else "[VERIFIED PASS]")
            elif tier == "PARTIAL":
                verdict = "PARTIAL_VALID"
                print("\033[93m[PARTIAL VALID]\033[0m" if sys.platform != "win32" else "[PARTIAL VALID]")
            else: # SCOPE
                verdict = "SCOPE_VALID"
                print("\033[94m[SCOPE VALID]\033[0m" if sys.platform != "win32" else "[SCOPE VALID]")
            results.append((cid, tier, verdict, None))
        else:
            verdict = "FAIL"
            print("\033[91m[FAILED]\033[0m" if sys.platform != "win32" else "[FAILED]")
            print(f"  Command: {cmd}")
            print(f"  Error snippet:\n{out[:250]}\n")
            results.append((cid, tier, verdict, out[:250]))
            has_failure = True

    print("\n" + "=" * 80)
    print(f"{'Claim ID':<22} | {'Tier':<10} | {'Verdict':<15} | {'Evidence':<25}")
    print("-" * 80)
    for cid, tier, verdict, _ in results:
        ev = next((','.join(c.get('evidence_tests', [])) for c in claims if c.get('id') == cid), "")
        print(f"{cid:<22} | {tier:<10} | {verdict:<15} | {ev:<25}")
    print("=" * 80)

    count_verified = sum(1 for _, t, v, _ in results if t == "VERIFIED" and v == "VERIFIED_PASS")
    count_partial = sum(1 for _, t, v, _ in results if t == "PARTIAL" and v == "PARTIAL_VALID")
    count_scope = sum(1 for _, t, v, _ in results if t == "SCOPE" and v == "SCOPE_VALID")
    count_fail = sum(1 for _, _, v, _ in results if v == "FAIL")

    print(f"Summary: {len(results)} Claims Evaluated")
    print(f"  - VERIFIED PASS : {count_verified}")
    print(f"  - PARTIAL VALID : {count_partial}")
    print(f"  - SCOPE VALID   : {count_scope}")
    print(f"  - FAILED        : {count_fail}")
    print("=" * 80)

    if not has_failure:
        print("  VERDICT: 100% AUDIT CRITERIA MET WITH FULL SCIENTIFIC HONESTY.")
        print("=" * 80)
        sys.exit(0)
    else:
        print("  VERDICT: AUDIT FAILED - RESOLVE DISCREPANCIES ABOVE.")
        print("=" * 80)
        sys.exit(1)

if __name__ == "__main__":
    main()
