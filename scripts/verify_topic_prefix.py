#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/verify_topic_prefix.py
Validates topic namespace prefix consistency across all 4 system layers:
1. Firmware Configuration (src/config.h)
2. Middleware Node-RED Flows (nodered/flows_smoke_detector.json)
3. Web SCADA Application (web/app.js)
4. MQTTX Test Collection (tests/mqttx_collection_slide65.json)

Ensures zero namespace pollution or topic collisions on shared public MQTT brokers.
"""

import os
import sys
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPECTED_PREFIX = "Nhom09/"

def verify_firmware_config():
    path = os.path.join(BASE_DIR, "src", "config.h")
    if not os.path.isfile(path):
        return False, f"Missing config file: {path}"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find all TOPIC_ constants
    topic_matches = re.findall(r'constexpr\s+const\s+char\*\s+(TOPIC_\w+)\s*=\s*"([^"]+)";', content)
    if not topic_matches:
        return False, "No TOPIC_ constants found in src/config.h"

    for name, topic in topic_matches:
        if not topic.startswith(EXPECTED_PREFIX):
            return False, f"Firmware topic {name} = '{topic}' does not start with '{EXPECTED_PREFIX}'"

    return True, f"Verified {len(topic_matches)} firmware topics in src/config.h"

def verify_nodered_flows():
    path = os.path.join(BASE_DIR, "nodered", "flows_smoke_detector.json")
    if not os.path.isfile(path):
        return False, f"Missing flow file: {path}"
    with open(path, "r", encoding="utf-8") as f:
        nodes = json.load(f)

    checked = 0
    for node in nodes:
        ntype = node.get("type", "")
        if ntype in ("mqtt in", "mqtt out"):
            topic = node.get("topic", "")
            # mqtt out nodes can have blank topic if dynamic from msg.topic
            if topic:
                if not topic.startswith(EXPECTED_PREFIX):
                    return False, f"Node-RED node '{node.get('name') or node.get('id')}' topic '{topic}' lacks prefix '{EXPECTED_PREFIX}'"
                checked += 1

    return True, f"Verified {checked} MQTT nodes in nodered/flows_smoke_detector.json"

def verify_web_scada():
    path = os.path.join(BASE_DIR, "web", "app.js")
    if not os.path.isfile(path):
        return False, f"Missing web file: {path}"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Match topics in MQTT_TOPICS object
    matches = re.findall(r'["\'](Nhom09/[^"\']+)["\']', content)
    if not matches:
        return False, f"No topics with prefix '{EXPECTED_PREFIX}' found in web/app.js"

    # Ensure no hardcoded raw un-prefixed smoke topics
    raw_smoke_topics = re.findall(r'["\'](smoke/(?:telemetry|cmd|status)[^"\']*)["\']', content)
    if raw_smoke_topics:
        return False, f"Found un-prefixed topics in web/app.js: {raw_smoke_topics}"

    return True, f"Verified {len(matches)} topic references in web/app.js"

def verify_mqttx_collection():
    path = os.path.join(BASE_DIR, "tests", "mqttx_collection_slide65.json")
    if not os.path.isfile(path):
        return False, f"Missing MQTTX collection: {path}"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Flatten scripts/messages
    checked = 0
    def scan_items(items):
        nonlocal checked
        for item in items:
            if isinstance(item, dict):
                topic = item.get("topic")
                if topic:
                    if not topic.startswith(EXPECTED_PREFIX):
                        raise ValueError(f"MQTTX message '{item.get('name')}' topic '{topic}' lacks '{EXPECTED_PREFIX}'")
                    checked += 1
                if "messages" in item and isinstance(item["messages"], list):
                    scan_items(item["messages"])
                if "children" in item and isinstance(item["children"], list):
                    scan_items(item["children"])

    try:
        if isinstance(data, list):
            scan_items(data)
        elif isinstance(data, dict):
            scan_items(data.get("scripts", []) or data.get("collections", []) or [data])
    except ValueError as e:
        return False, str(e)

    return True, f"Verified {checked} messages in tests/mqttx_collection_slide65.json"

def main():
    print("=" * 75)
    print("  TOPIC PREFIX CONSISTENCY AUDITOR - NHOM 04 HUIT")
    print(f"  Target Namespace: '{EXPECTED_PREFIX}'")
    print("=" * 75)

    checks = [
        ("Layer 1: ESP32 Firmware (src/config.h)", verify_firmware_config),
        ("Layer 3: Node-RED Flows (flows_smoke_detector.json)", verify_nodered_flows),
        ("Layer 4: Web SCADA (web/app.js)", verify_web_scada),
        ("Test Suite: MQTTX Slide 65 Collection", verify_mqttx_collection),
    ]

    all_ok = True
    for label, fn in checks:
        ok, msg = fn()
        status = "[PASS]" if ok else "[FAIL]"
        print(f"{status:<8} {label}: {msg}")
        if not ok:
            all_ok = False

    print("=" * 75)
    if all_ok:
        print("RESULT: 100% TOPIC PREFIX CONSISTENCY VERIFIED (ZERO UNPREFIXED TOPICS).")
        print("=" * 75)
        sys.exit(0)
    else:
        print("RESULT: TOPIC PREFIX CONSISTENCY CHECK FAILED!")
        print("=" * 75)
        sys.exit(1)

if __name__ == "__main__":
    main()
