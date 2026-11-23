# -*- coding: utf-8 -*-
"""
Tự động sinh cấu trúc Flow Node-RED chuẩn cho Đề tài 04 - Hệ thống báo khói cảnh báo sớm.
Đạt đầy đủ các tiêu chuẩn nghiệm thu Tuần 5, Tuần 6 và TIẾN ĐỘ TUẦN 7 (Business Rules & Abnormal Scenarios):
- 5 Business Rules:
  1. Multi-Sensor Rate-of-Rise Correlation (Khói >= 400 + dT/dt >= 3.0°C/min hoặc Temp >= 50°C -> Real Fire Emergency)
  2. Transient Smoke Suppression Filter (Khói vượt ngưỡng nhưng Temp < 35°C và < 10s -> Purge fan only, Mute buzzer)
  3. Adaptive Day/Night Dynamic Threshold Scheduler (Day: 400/300 PPM, Night: 350/250 PPM)
  4. Post-Alarm Purge Delay Cooldown (Thông gió cưỡng bức 30s sau khi khói an toàn)
  5. Cross-Zone Emergency Corridor Broadcast (Khói >= 600 PPM -> Bật còi toàn sàn F03)
- 4 Abnormal Scenarios:
  1. Sensor Malfunction Detection (MQ-2 ADC out-of-range, DHT22 NaN/Timeout -> Fail-Safe Mode)
  2. Network Outage & Offline Circular Buffer Sync (Ingestion topic smoke/history/sync)
  3. Watchdog Sudden Death Detection (> 30s missing keep-alives -> Telegram & Dashboard Alert)
  4. Actuator Feedback Fault & Command Timeout Alert
- Quản trị Hạm đội đa thiết bị (Dynamic Fleet Registry & Whitelist Validation)
- Ghi nhật ký đa tầng (Audit Trail) & Dashboard UI Gauges / State Matrices
"""

import json
import uuid
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def read_func(rel_path):
    path = os.path.join(BASE_DIR, rel_path)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_nodered_flow():
    flow_tab_id = "tab_middleware_smoke"
    broker_id = "broker_emqx_cloud"
    
    # UI Group / Tab IDs for Dashboard
    ui_tab_id = "ui_tab_smoke_monitor"
    ui_grp_gauges = "ui_grp_gauges"
    ui_grp_state = "ui_grp_state"
    ui_grp_fleet = "ui_grp_fleet"
    ui_grp_controls = "ui_grp_controls"
    ui_grp_rules = "ui_grp_rules"

    nodes = [
        # 1. Flow Tab Definition
        {
            "id": flow_tab_id,
            "type": "tab",
            "label": "Tầng 3 - Middleware Automation Engine (Tuần 7: Business Rules & Abnormal)",
            "disabled": False,
            "info": "Middleware Engine xử lý dữ liệu cho Hệ thống báo khói cảnh báo sớm (Tuần 7: Business Rules & Abnormal Scenarios).\nBao gồm 5 Business Rules, 4 Kịch bản sự cố bất thường, Offline Buffer Replay, Watchdog 30s, Dynamic Day/Night Scheduler và Cross-Zone Emergency Automation."
        },
        
        # 2. MQTT Broker Configuration Node
        {
            "id": broker_id,
            "type": "mqtt-broker",
            "name": "EMQX Public Broker",
            "broker": "broker.emqx.io",
            "port": "1883",
            "clientid": "NodeRED_Smoke_Middleware_N04",
            "autoConnect": True,
            "usetls": False,
            "protocolVersion": "4",
            "keepalive": "60",
            "cleansession": True,
            "autoUnsubscribe": True,
            "birthTopic": "Nhom09/smoke/middleware/status",
            "birthQos": "1",
            "birthRetain": "true",
            "birthPayload": json.dumps({"middleware": "ONLINE", "version": "3.0.0", "milestone": "WEEK7_BUSINESS_RULES_ABNORMAL"}),
            "closeTopic": "Nhom09/smoke/middleware/status",
            "closeQos": "1",
            "closeRetain": "true",
            "closePayload": json.dumps({"middleware": "OFFLINE"}),
            "willTopic": "Nhom09/smoke/middleware/status",
            "willQos": "1",
            "willRetain": "true",
            "willPayload": json.dumps({"middleware": "CRASHED"})
        },

        # ======================================================================
        # 3. DỊCH VỤ 1: AUTHENTICATION SERVICE (Slide 65: 1a - 1d)
        # ======================================================================
        {
            "id": "mqtt_in_auth_req",
            "type": "mqtt in",
            "z": flow_tab_id,
            "name": "Sub (1a): Nhom09/smoke/v2/auth/request",
            "topic": "Nhom09/smoke/v2/auth/request",
            "qos": "1",
            "datatype": "auto-detect",
            "broker": broker_id,
            "nl": False,
            "rap": True,
            "rh": 0,
            "x": 170,
            "y": 80,
            "wires": [["fn_auth_service"]]
        },
        {
            "id": "fn_auth_service",
            "type": "function",
            "z": flow_tab_id,
            "name": "Dịch vụ 1: Auth & Whitelist (1b, 1c)",
            "func": """// Cơ sở dữ liệu Whitelist thiết bị được phép vào hệ thống
const WHITELIST = {
    "ESP32_SMOKE_N04_A01": { 
        mac: "24:6F:28:AB:CD:10", 
        token: "HUIT_IOT_SECURE_TOKEN_N04", 
        topology: { building: "HUIT_A", floor: "F03", room: "P302", zone: "Phòng Lab IoT" }
    },
    "ESP32_SMOKE_N04_A02": { 
        mac: "24:6F:28:AB:CD:20", 
        token: "HUIT_IOT_SECURE_TOKEN_N04", 
        topology: { building: "HUIT_A", floor: "F03", room: "P303", zone: "Kho Hóa Chất" }
    },
    "ESP32_SMOKE_N04_A03": { 
        mac: "24:6F:28:AB:CD:30", 
        token: "HUIT_IOT_SECURE_TOKEN_N04", 
        topology: { building: "HUIT_A", floor: "F03", room: "P304", zone: "Khu Vực Bếp" }
    }
};

let data = msg.payload;
if (typeof data === 'string') {
    try { data = JSON.parse(data); } catch(e) { return null; }
}

let devId = data.device_id || "UNKNOWN";
let devMac = data.mac_address || "";
let secret = data.secret_token || "";

let respTopic = "Nhom09/smoke/v2/auth/response/" + devId;
let respPayload = {};
let logEntry = null;

// Kiểm tra tính hợp lệ trong Whitelist
let record = WHITELIST[devId];
if (record && record.token === secret) {
    let sessionKey = "SK_" + Math.random().toString(36).substr(2, 9).toUpperCase() + "_N04";
    respPayload = {
        msg_id: "RESP-AUTH-" + Date.now(),
        status: "PASS",
        status_code: 200,
        session_key: sessionKey,
        lease_duration_sec: 86400,
        assigned_topology: record.topology,
        config: {
            telemetry_interval_ms: 2000,
            keep_alive_interval_ms: 10000,
            alarm_threshold_ppm: 400.0,
            safe_threshold_ppm: 300.0
        }
    };

    // Đăng ký vào bảng Device Fleet Registry
    let fleet = flow.get("fleet") || {};
    let d = fleet[devId] || {
        deviceId: devId,
        deviceState: "SAFE",
        effective: "SAFE",
        tempHist: [],
        alarmTh: 400,
        safeTh: 300,
        overActive: false,
        hotActive: false,
        cooldownStart: null,
        lastAlert: 0,
        rate: 0,
        mq2Valid: true,
        dhtValid: true,
        hum: 60.0,
        lastPpm: 0
    };
    d.mac = devMac;
    d.zone = record.topology.zone;
    d.topology = record.topology;
    d.sessionKey = sessionKey;
    d.status = "ONLINE";
    d.lastSeen = Date.now();
    fleet[devId] = d;
    flow.set("fleet", fleet);
    flow.set("device_fleet", fleet);

    logEntry = { level: "INFO", event: "AUTH_SUCCESS", desc: `Xác thực thành công thiết bị ${devId} (${record.topology.zone})` };
} else {
    respPayload = {
        msg_id: "RESP-AUTH-" + Date.now(),
        status: "REJECTED",
        status_code: 401,
        error_code: "ERR_UNAUTHORIZED_DEVICE",
        message: "Device MAC or secret token is invalid."
    };
    logEntry = { level: "WARN", event: "AUTH_REJECTED", desc: `Từ chối xác thực thiết bị lạ: ID=${devId}, MAC=${devMac}` };
}

let outMqtt = {
    topic: respTopic,
    payload: JSON.stringify(respPayload),
    qos: 1
};

let outLog = logEntry ? { payload: [logEntry] } : null;

return [outMqtt, outLog];""",
            "outputs": 2,
            "noerr": 0,
            "x": 490,
            "y": 80,
            "wires": [["mqtt_out_auth_resp"], ["fn_audit_logger"]]
        },
        {
            "id": "mqtt_out_auth_resp",
            "type": "mqtt out",
            "z": flow_tab_id,
            "name": "Pub (1d): Nhom09/smoke/v2/auth/response",
            "topic": "",
            "qos": "1",
            "retain": "false",
            "broker": broker_id,
            "x": 840,
            "y": 80,
            "wires": []
        },

        # ======================================================================
        # 4. DỊCH VỤ 2: COLLECT SENSORS DATA (Slide 65: 2a - 2b) & TUẦN 7 INPUTS
        # ======================================================================
        {
            "id": "mqtt_in_telemetry_v1",
            "type": "mqtt in",
            "z": flow_tab_id,
            "name": "Sub V1: Nhom09/smoke/telemetry",
            "topic": "Nhom09/smoke/telemetry",
            "qos": "0",
            "datatype": "auto-detect",
            "broker": broker_id,
            "nl": False,
            "rap": True,
            "rh": 0,
            "x": 160,
            "y": 160,
            "wires": [["fn_parse_telemetry"]]
        },
        {
            "id": "mqtt_in_telemetry_v2",
            "type": "mqtt in",
            "z": flow_tab_id,
            "name": "Sub (2a): Nhom09/smoke/v2/+/+/+/+/telemetry",
            "topic": "Nhom09/smoke/v2/+/+/+/+/telemetry",
            "qos": "0",
            "datatype": "auto-detect",
            "broker": broker_id,
            "nl": False,
            "rap": True,
            "rh": 0,
            "x": 200,
            "y": 220,
            "wires": [["fn_parse_telemetry"]]
        },
        {
            "id": "mqtt_in_alarm_v1",
            "type": "mqtt in",
            "z": flow_tab_id,
            "name": "Sub V1: Nhom09/smoke/event/alarm",
            "topic": "Nhom09/smoke/event/alarm",
            "qos": "1",
            "datatype": "auto-detect",
            "broker": broker_id,
            "nl": False,
            "rap": True,
            "rh": 0,
            "x": 170,
            "y": 280,
            "wires": [["fn_parse_alarm"]]
        },
        {
            "id": "mqtt_in_alarm_v2",
            "type": "mqtt in",
            "z": flow_tab_id,
            "name": "Sub (2a): Nhom09/smoke/v2/+/+/+/+/event/alarm",
            "topic": "Nhom09/smoke/v2/+/+/+/+/event/alarm",
            "qos": "1",
            "datatype": "auto-detect",
            "broker": broker_id,
            "nl": False,
            "rap": True,
            "rh": 0,
            "x": 210,
            "y": 340,
            "wires": [["fn_parse_alarm"]]
        },
        # Tuần 7: Ingestion Offline Buffer Replay
        {
            "id": "mqtt_in_history_sync",
            "type": "mqtt in",
            "z": flow_tab_id,
            "name": "Sub (Abnormal 2): Nhom09/smoke/history/sync",
            "topic": "Nhom09/smoke/history/sync",
            "qos": "1",
            "datatype": "auto-detect",
            "broker": broker_id,
            "nl": False,
            "rap": True,
            "rh": 0,
            "x": 200,
            "y": 400,
            "wires": [["fn_parse_history_sync"]]
        },

        # ======================================================================
        # 5. DỊCH VỤ 4: KEEP-ALIVE, WATCHDOG & TUẦN 7 SCHEDULER INPUTS
        # ======================================================================
        {
            "id": "mqtt_in_keepalive_v1",
            "type": "mqtt in",
            "z": flow_tab_id,
            "name": "Sub V1: Nhom09/smoke/keep_alive",
            "topic": "Nhom09/smoke/keep_alive",
            "qos": "0",
            "datatype": "auto-detect",
            "broker": broker_id,
            "nl": False,
            "rap": True,
            "rh": 0,
            "x": 170,
            "y": 460,
            "wires": [["fn_parse_keepalive"]]
        },
        {
            "id": "mqtt_in_keepalive_v2",
            "type": "mqtt in",
            "z": flow_tab_id,
            "name": "Sub (4a): Nhom09/smoke/v2/+/+/+/+/keep_alive",
            "topic": "Nhom09/smoke/v2/+/+/+/+/keep_alive",
            "qos": "0",
            "datatype": "auto-detect",
            "broker": broker_id,
            "nl": False,
            "rap": True,
            "rh": 0,
            "x": 200,
            "y": 510,
            "wires": [["fn_parse_keepalive"]]
        },
        {
            "id": "mqtt_in_lwt",
            "type": "mqtt in",
            "z": flow_tab_id,
            "name": "Sub: Nhom09/smoke/lwt",
            "topic": "Nhom09/smoke/lwt",
            "qos": "1",
            "datatype": "auto-detect",
            "broker": broker_id,
            "nl": False,
            "rap": True,
            "rh": 0,
            "x": 130,
            "y": 560,
            "wires": [["fn_parse_lwt"]]
        },
        # Tuần 7: Sub Scheduler Command
        {
            "id": "mqtt_in_scheduler",
            "type": "mqtt in",
            "z": flow_tab_id,
            "name": "Sub (Rule 3): Nhom09/smoke/cmd/scheduler",
            "topic": "Nhom09/smoke/cmd/scheduler",
            "qos": "1",
            "datatype": "auto-detect",
            "broker": broker_id,
            "nl": False,
            "rap": True,
            "rh": 0,
            "x": 190,
            "y": 610,
            "wires": [["fn_parse_scheduler"]]
        },
        # Tuần 7: Sub Fault Injection Command
        {
            "id": "mqtt_in_fault_injection",
            "type": "mqtt in",
            "z": flow_tab_id,
            "name": "Sub (Fault Inject): Nhom09/smoke/cmd/inject_fault",
            "topic": "Nhom09/smoke/cmd/inject_fault",
            "qos": "1",
            "datatype": "auto-detect",
            "broker": broker_id,
            "nl": False,
            "rap": True,
            "rh": 0,
            "x": 210,
            "y": 660,
            "wires": [["fn_parse_fault_injection"]]
        },
        {
            "id": "inject_watchdog_tick",
            "type": "inject",
            "z": flow_tab_id,
            "name": "Watchdog 3s Tick (Abnormal 3)",
            "props": [{"p": "payload"}],
            "repeat": "3",
            "crontab": "",
            "once": True,
            "onceDelay": 1,
            "topic": "watchdog/tick",
            "payload": "",
            "payloadType": "date",
            "x": 170,
            "y": 710,
            "wires": [["fn_watchdog_scheduler"]]
        },

        # ======================================================================
        # 6. PARSER & STANDARDIZATION FUNCTIONS
        # ======================================================================
        {
            "id": "fn_parse_telemetry",
            "type": "function",
            "z": flow_tab_id,
            "name": "Parse & Validate Telemetry",
            "func": read_func("functions/parse_telemetry.js"),
            "outputs": 1,
            "x": 520,
            "y": 180,
            "wires": [["fn_core_fsm_engine"]]
        },
        {
            "id": "fn_parse_alarm",
            "type": "function",
            "z": flow_tab_id,
            "name": "Parse Urgent Alarm Event",
            "func": read_func("functions/parse_alarm.js"),
            "outputs": 1,
            "x": 520,
            "y": 300,
            "wires": [["fn_core_fsm_engine"]]
        },
        {
            "id": "fn_parse_history_sync",
            "type": "function",
            "z": flow_tab_id,
            "name": "Parse Offline Buffer Sync (Abnormal 2)",
            "func": """let data = msg.payload;
if (typeof data === 'string') {
    try { data = JSON.parse(data); } catch(e) { return null; }
}

msg.eventType = "OFFLINE_SYNC";
msg.deviceId = data.device_id || "ESP32_SMOKE_N04_A01";
msg.syncSeq = data.sync_seq || 1;
msg.records = data.records || [];
msg.ppm = parseFloat(data.mq2_ppm || data.ppm || 0);
msg.temp = parseFloat(data.temp || 28.0);
msg.fan = data.fan || "OFF";
msg.recordState = data.state || "SAFE";
msg.timestamp = Date.now();

return msg;""",
            "outputs": 1,
            "x": 540,
            "y": 400,
            "wires": [["fn_core_fsm_engine"]]
        },
        {
            "id": "fn_parse_keepalive",
            "type": "function",
            "z": flow_tab_id,
            "name": "Dịch vụ 4: Parse Keep-Alive",
            "func": read_func("functions/parse_keepalive.js"),
            "outputs": 1,
            "x": 520,
            "y": 480,
            "wires": [["fn_core_fsm_engine"]]
        },
        {
            "id": "fn_parse_lwt",
            "type": "function",
            "z": flow_tab_id,
            "name": "Parse LWT Signal",
            "func": read_func("functions/parse_lwt.js"),
            "outputs": 1,
            "x": 500,
            "y": 560,
            "wires": [["fn_core_fsm_engine"]]
        },
        {
            "id": "fn_parse_scheduler",
            "type": "function",
            "z": flow_tab_id,
            "name": "Parse Scheduler Cmd (Rule 3)",
            "func": """let data = msg.payload;
if (typeof data === 'string') {
    try { data = JSON.parse(data); } catch(e) { data = { mode: data }; }
}
msg.eventType = "SCHEDULER_CMD";
msg.mode = data.mode || "DAY";
msg.timestamp = Date.now();
return msg;""",
            "outputs": 1,
            "x": 530,
            "y": 620,
            "wires": [["fn_core_fsm_engine"]]
        },
        {
            "id": "fn_parse_fault_injection",
            "type": "function",
            "z": flow_tab_id,
            "name": "Parse Fault Injection (Abnormal Sandbox)",
            "func": """let data = msg.payload;
if (typeof data === 'string') {
    try { data = JSON.parse(data); } catch(e) { data = { fault: data }; }
}
msg.eventType = "FAULT_INJECTION_CMD";
msg.fault = data.fault || "NONE";
msg.timestamp = Date.now();
return msg;""",
            "outputs": 1,
            "x": 550,
            "y": 670,
            "wires": [["fn_core_fsm_engine"]]
        },
        {
            "id": "fn_watchdog_scheduler",
            "type": "function",
            "z": flow_tab_id,
            "name": "Watchdog 3s Tick Trigger",
            "func": """msg.eventType = "WATCHDOG_TICK";
msg.timestamp = Date.now();
return msg;""",
            "outputs": 1,
            "x": 520,
            "y": 720,
            "wires": [["fn_core_fsm_engine"]]
        },
        {
            "id": "inject_scheduler_1m",
            "type": "inject",
            "z": flow_tab_id,
            "name": "Scheduler 1-min Inject (Rule 3)",
            "props": [{"p": "payload"}],
            "repeat": "60",
            "crontab": "",
            "once": True,
            "onceDelay": 2,
            "topic": "",
            "payload": "",
            "payloadType": "date",
            "x": 170,
            "y": 760,
            "wires": [["fn_scheduler_tick"]]
        },
        {
            "id": "fn_scheduler_tick",
            "type": "function",
            "z": flow_tab_id,
            "name": "Day/Night Scheduler Tick",
            "func": read_func("functions/scheduler_tick.js"),
            "outputs": 1,
            "x": 520,
            "y": 760,
            "wires": [["fn_command_dispatcher", "fn_parse_scheduler"]]
        },

        # ======================================================================
        # 7. CORE ENGINE: FSM 6 STATES, 5 BUSINESS RULES & 4 ABNORMAL SCENARIOS
        # ======================================================================
        {
            "id": "fn_core_fsm_engine",
            "type": "function",
            "z": flow_tab_id,
            "name": "Core Engine: FSM, 5 Rules & Abnormal Scenarios",
            "func": read_func("functions/core_engine.js"),
            "outputs": 4,
            "noerr": 0,
            "x": 860,
            "y": 420,
            "wires": [
                ["fn_command_dispatcher"],
                ["fn_audit_logger"],
                ["fn_ui_dashboard_adapter"],
                ["fn_alert_dispatcher"]
            ]
        },

        # ======================================================================
        # 8. COMMAND DISPATCHER & MQTT OUT
        # ======================================================================
        {
            "id": "fn_command_dispatcher",
            "type": "function",
            "z": flow_tab_id,
            "name": "Dịch vụ 3: Command Dispatcher (3a)",
            "func": read_func("functions/command_dispatcher.js"),
            "outputs": 1,
            "x": 1140,
            "y": 380,
            "wires": [["mqtt_out_cmd_downlink", "debug_cmd_sent"]]
        },
        {
            "id": "mqtt_out_cmd_downlink",
            "type": "mqtt out",
            "z": flow_tab_id,
            "name": "Pub: Command Downlink (Dynamic msg.topic)",
            "topic": "",
            "qos": "1",
            "retain": "false",
            "broker": broker_id,
            "x": 1410,
            "y": 440,
            "wires": []
        },
        {
            "id": "fn_alert_dispatcher",
            "type": "function",
            "z": flow_tab_id,
            "name": "Alert & Telegram Dispatcher",
            "func": read_func("functions/alert_dispatcher.js"),
            "outputs": 2,
            "x": 1080,
            "y": 660,
            "wires": [
                ["http_req_telegram"],
                ["debug_alert_notifications"]
            ]
        },
        {
            "id": "http_req_telegram",
            "type": "http request",
            "z": flow_tab_id,
            "name": "Telegram Bot API (Simulated/Real)",
            "method": "use",
            "ret": "txt",
            "paytoqs": "ignore",
            "url": "",
            "tls": "",
            "persist": False,
            "proxy": "",
            "authType": "",
            "senderr": False,
            "headers": [],
            "x": 1330,
            "y": 640,
            "wires": [["debug_alert_notifications"]]
        },
        {
            "id": "debug_cmd_sent",
            "type": "debug",
            "z": flow_tab_id,
            "name": "Command Sent Log",
            "active": True,
            "tosidebar": True,
            "complete": "payload",
            "x": 1390,
            "y": 560,
            "wires": []
        },

        # ======================================================================
        # 9. AUDIT LOGGER & UI ADAPTERS
        # ======================================================================
        {
            "id": "fn_audit_logger",
            "type": "function",
            "z": flow_tab_id,
            "name": "Multi-tier Audit Trail Logger",
            "func": """let payload = msg.payload || [];
let history = msg.eventHistory || [];
return [{ payload: { recentLogs: payload, history: history } }];""",
            "outputs": 1,
            "x": 1140,
            "y": 280,
            "wires": [["debug_audit_log"]]
        },
        {
            "id": "debug_audit_log",
            "type": "debug",
            "z": flow_tab_id,
            "name": "Audit Trail Console",
            "active": True,
            "tosidebar": True,
            "complete": "payload",
            "x": 1390,
            "y": 280,
            "wires": []
        },
        {
            "id": "fn_ui_dashboard_adapter",
            "type": "function",
            "z": flow_tab_id,
            "name": "Dashboard State Adapter",
            "func": """let p = msg.payload || {};
let ppm = (p.ppm !== undefined) ? Number(Number(p.ppm).toFixed(1)) : (p.smokePpm !== undefined ? Number(Number(p.smokePpm).toFixed(1)) : 0);
let temp = (p.temp !== undefined) ? Number(Number(p.temp).toFixed(1)) : 28.0;
let hum = (p.hum !== undefined) ? Number(Number(p.hum).toFixed(1)) : 60.0;
let state = p.fsmState || "SAFE";

let colorMap = {
    "SAFE": "#00b500",
    "WARNING": "#e67e22",
    "ALARM": "#ca3838",
    "COOLDOWN": "#2980b9",
    "FAULT": "#8e44ad",
    "OFFLINE": "#7f8c8d"
};
let stateColor = colorMap[state] || "#00b500";

let msgPpm = { payload: ppm, topic: "Nồng độ Khói (PPM)" };
let msgTemp = { payload: temp, topic: "Nhiệt độ (°C)" };
let msgHum = { payload: hum, topic: "Độ ẩm (%)" };
let msgState = { payload: state, color: stateColor };
let msgDebug = { payload: p };

return [msgPpm, msgTemp, msgHum, msgState, msgDebug];""",
            "outputs": 5,
            "noerr": 0,
            "x": 1130,
            "y": 620,
            "wires": [
                ["ui_gauge_smoke", "ui_chart_trends"],
                ["ui_gauge_temp", "ui_chart_trends"],
                ["ui_gauge_hum"],
                ["ui_text_fsm_state"],
                ["debug_dashboard_state"]
            ]
        },
        {
            "id": "debug_dashboard_state",
            "type": "debug",
            "z": flow_tab_id,
            "name": "Dashboard UI Feed",
            "active": True,
            "tosidebar": True,
            "complete": "payload",
            "x": 1380,
            "y": 620,
            "wires": []
        },
        {
            "id": "debug_alert_notifications",
            "type": "debug",
            "z": flow_tab_id,
            "name": "Telegram & Web Alert Dispatcher",
            "active": True,
            "tosidebar": True,
            "complete": "payload",
            "x": 1160,
            "y": 700,
            "wires": []
        },

        # Dashboard Config UI Tabs
        {
            "id": ui_tab_id,
            "type": "ui_tab",
            "name": "Báo Khói Cảnh Báo Sớm - Tuần 7",
            "icon": "dashboard",
            "order": 1
        },
        {
            "id": ui_grp_gauges,
            "type": "ui_group",
            "name": "Thông số Cảm biến Môi trường",
            "tab": ui_tab_id,
            "order": 1,
            "disp": True,
            "width": "12"
        },
        {
            "id": ui_grp_state,
            "type": "ui_group",
            "name": "Máy trạng thái FSM 6 Trạng thái & Tuần 7 Rules",
            "tab": ui_tab_id,
            "order": 2,
            "disp": True,
            "width": "12"
        },
        {
            "id": ui_grp_controls,
            "type": "ui_group",
            "name": "Tầng 4: Điều khiển Chấp hành & Cảnh báo từ xa",
            "tab": ui_tab_id,
            "order": 3,
            "disp": True,
            "width": "12"
        },
        {
            "id": ui_grp_fleet,
            "type": "ui_group",
            "name": "Quản trị Hạm đội Thiết bị (Fleet Registry)",
            "tab": ui_tab_id,
            "order": 4,
            "disp": True,
            "width": "12"
        },
        {
            "id": ui_grp_rules,
            "type": "ui_group",
            "name": "Bảng Điều phối Business Rules & Abnormal Sandbox",
            "tab": ui_tab_id,
            "order": 5,
            "disp": True,
            "width": "12"
        },

        # ======================================================================
        # 10. DASHBOARD UI WIDGETS & CONTROLS (TẦNG 4 MONITOR & CONTROL)
        # ======================================================================
        {
            "id": "ui_gauge_smoke",
            "type": "ui_gauge",
            "z": flow_tab_id,
            "name": "Smoke PPM Gauge",
            "group": ui_grp_gauges,
            "order": 1,
            "width": 4,
            "height": 4,
            "gtype": "gage",
            "title": "Nồng độ Khói (MQ-2)",
            "label": "PPM",
            "format": "{{value}}",
            "min": 0,
            "max": "1000",
            "colors": ["#00b500", "#e6e600", "#ca3838"],
            "seg1": "300",
            "seg2": "400",
            "diff": False,
            "className": "",
            "x": 1410,
            "y": 620,
            "wires": []
        },
        {
            "id": "ui_gauge_temp",
            "type": "ui_gauge",
            "z": flow_tab_id,
            "name": "Temperature Gauge",
            "group": ui_grp_gauges,
            "order": 2,
            "width": 4,
            "height": 4,
            "gtype": "gage",
            "title": "Nhiệt độ (DHT22)",
            "label": "°C",
            "format": "{{value}}",
            "min": 0,
            "max": "80",
            "colors": ["#00b500", "#e6e600", "#ca3838"],
            "seg1": "35",
            "seg2": "50",
            "diff": False,
            "className": "",
            "x": 1410,
            "y": 680,
            "wires": []
        },
        {
            "id": "ui_gauge_hum",
            "type": "ui_gauge",
            "z": flow_tab_id,
            "name": "Humidity Gauge",
            "group": ui_grp_gauges,
            "order": 3,
            "width": 4,
            "height": 4,
            "gtype": "gage",
            "title": "Độ ẩm Không khí",
            "label": "%",
            "format": "{{value}}",
            "min": 0,
            "max": "100",
            "colors": ["#2ca02c", "#1f77b4", "#0094ce"],
            "seg1": "",
            "seg2": "",
            "diff": False,
            "className": "",
            "x": 1410,
            "y": 740,
            "wires": []
        },
        {
            "id": "ui_chart_trends",
            "type": "ui_chart",
            "z": flow_tab_id,
            "name": "Realtime Trends Chart",
            "group": ui_grp_gauges,
            "order": 4,
            "width": 12,
            "height": 6,
            "label": "Biểu đồ Thời gian thực Khói (PPM) & Nhiệt độ (°C)",
            "chartType": "line",
            "legend": "true",
            "xformat": "HH:mm:ss",
            "interpolate": "linear",
            "nodata": "Đang nhận dữ liệu từ ESP32...",
            "dot": False,
            "ymin": "0",
            "ymax": "",
            "removeOlder": 1,
            "removeOlderPoints": "",
            "removeOlderUnit": "3600",
            "cutout": 0,
            "useOneColor": False,
            "useUTC": False,
            "colors": ["#ca3838", "#ff7f0e", "#1f77b4", "#2ca02c", "#98df8a", "#d62728", "#ff9896", "#9467bd", "#c5b0d5"],
            "outputs": 1,
            "useDifferentColor": False,
            "className": "",
            "x": 1410,
            "y": 800,
            "wires": [[]]
        },
        {
            "id": "ui_text_fsm_state",
            "type": "ui_text",
            "z": flow_tab_id,
            "group": ui_grp_state,
            "order": 1,
            "width": 12,
            "height": 2,
            "name": "FSM State Display",
            "label": "Trạng thái FSM Hệ thống:",
            "format": "<b><span style='color: {{msg.color}}; font-size: 22px; text-transform: uppercase;'>{{msg.payload}}</span></b>",
            "layout": "row-spread",
            "className": "",
            "x": 1410,
            "y": 860,
            "wires": []
        },
        {
            "id": "ui_btn_fan_on",
            "type": "ui_button",
            "z": flow_tab_id,
            "name": "Button Fan ON",
            "group": ui_grp_controls,
            "order": 1,
            "width": 3,
            "height": 1,
            "passthru": False,
            "label": "BẬT QUẠT HÚT",
            "tooltip": "Kích hoạt quạt hút khói",
            "color": "#ffffff",
            "bgcolor": "#27ae60",
            "className": "",
            "icon": "fa-fan",
            "payload": "{\"action\":\"ON\",\"source\":\"NodeRED_Dashboard\"}",
            "payloadType": "str",
            "topic": "Nhom09/smoke/cmd/fan",
            "topicType": "str",
            "x": 1130,
            "y": 920,
            "wires": [["fn_command_dispatcher"]]
        },
        {
            "id": "ui_btn_fan_off",
            "type": "ui_button",
            "z": flow_tab_id,
            "name": "Button Fan OFF",
            "group": ui_grp_controls,
            "order": 2,
            "width": 3,
            "height": 1,
            "passthru": False,
            "label": "TẮT QUẠT HÚT",
            "tooltip": "Tắt quạt hút khói",
            "color": "#ffffff",
            "bgcolor": "#7f8c8d",
            "className": "",
            "icon": "fa-power-off",
            "payload": "{\"action\":\"OFF\",\"source\":\"NodeRED_Dashboard\"}",
            "payloadType": "str",
            "topic": "Nhom09/smoke/cmd/fan",
            "topicType": "str",
            "x": 1130,
            "y": 970,
            "wires": [["fn_command_dispatcher"]]
        },
        {
            "id": "ui_btn_buzzer_mute",
            "type": "ui_button",
            "z": flow_tab_id,
            "name": "Button Buzzer Mute",
            "group": ui_grp_controls,
            "order": 3,
            "width": 3,
            "height": 1,
            "passthru": False,
            "label": "TẮT TIẾNG CÒI (MUTE)",
            "tooltip": "Tạm ngắt tiếng chuông cảnh báo 3 phút",
            "color": "#ffffff",
            "bgcolor": "#e67e22",
            "className": "",
            "icon": "fa-bell-slash",
            "payload": "{\"action\":\"MUTE\",\"source\":\"NodeRED_Dashboard\"}",
            "payloadType": "str",
            "topic": "Nhom09/smoke/cmd/buzzer",
            "topicType": "str",
            "x": 1130,
            "y": 1020,
            "wires": [["fn_command_dispatcher"]]
        },
        {
            "id": "ui_btn_buzzer_unmute",
            "type": "ui_button",
            "z": flow_tab_id,
            "name": "Button Buzzer Unmute",
            "group": ui_grp_controls,
            "order": 4,
            "width": 3,
            "height": 1,
            "passthru": False,
            "label": "BẬT TIẾNG CÒI (UNMUTE)",
            "tooltip": "Kích hoạt lại còi báo động",
            "color": "#ffffff",
            "bgcolor": "#c0392b",
            "className": "",
            "icon": "fa-bell",
            "payload": "{\"action\":\"UNMUTE\",\"source\":\"NodeRED_Dashboard\"}",
            "payloadType": "str",
            "topic": "Nhom09/smoke/cmd/buzzer",
            "topicType": "str",
            "x": 1130,
            "y": 1070,
            "wires": [["fn_command_dispatcher"]]
        }
    ]

    return nodes

if __name__ == "__main__":
    flow_data = build_nodered_flow()
    out_file = os.path.join(BASE_DIR, "flows_smoke_detector.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(flow_data, f, ensure_ascii=False, indent=2)
    print(f"Node-RED flow successfully generated at: {out_file} (Total nodes: {len(flow_data)})")

    # Sync to live Node-RED user directory if present
    nodered_user_dir = os.path.expanduser("~/.node-red")
    if os.path.isdir(nodered_user_dir):
        live_flows = os.path.join(nodered_user_dir, "flows.json")
        shutil.copyfile(out_file, live_flows)
        print(f"Deployed to active Node-RED: {live_flows}")
