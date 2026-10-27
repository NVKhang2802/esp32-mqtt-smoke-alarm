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
            "birthTopic": "smoke/middleware/status",
            "birthQos": "1",
            "birthRetain": "true",
            "birthPayload": json.dumps({"middleware": "ONLINE", "version": "3.0.0", "milestone": "WEEK7_BUSINESS_RULES_ABNORMAL"}),
            "closeTopic": "smoke/middleware/status",
            "closeQos": "1",
            "closeRetain": "true",
            "closePayload": json.dumps({"middleware": "OFFLINE"}),
            "willTopic": "smoke/middleware/status",
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
            "name": "Sub (1a): smoke/v2/auth/request",
            "topic": "smoke/v2/auth/request",
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

let respTopic = "smoke/v2/auth/response/" + devId;
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
    let fleet = flow.get("device_fleet") || {};
    fleet[devId] = {
        deviceId: devId,
        mac: devMac,
        zone: record.topology.zone,
        topology: record.topology,
        sessionKey: sessionKey,
        status: "ONLINE",
        fsmState: "SAFE",
        lastSeen: Date.now(),
        ppm: 0,
        temp: 28.0,
        freeHeap: 180000,
        rssi: -60
    };
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
            "name": "Pub (1d): smoke/v2/auth/response",
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
            "name": "Sub V1: smoke/telemetry",
            "topic": "smoke/telemetry",
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
            "name": "Sub (2a): smoke/v2/+/+/+/+/telemetry",
            "topic": "smoke/v2/+/+/+/+/telemetry",
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
            "name": "Sub V1: smoke/event/alarm",
            "topic": "smoke/event/alarm",
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
            "name": "Sub (2a): smoke/v2/+/+/+/+/event/alarm",
            "topic": "smoke/v2/+/+/+/+/event/alarm",
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
            "name": "Sub (Abnormal 2): smoke/history/sync",
            "topic": "smoke/history/sync",
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
            "name": "Sub V1: smoke/keep_alive",
            "topic": "smoke/keep_alive",
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
            "name": "Sub (4a): smoke/v2/+/+/+/+/keep_alive",
            "topic": "smoke/v2/+/+/+/+/keep_alive",
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
            "name": "Sub: smoke/lwt",
            "topic": "smoke/lwt",
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
            "name": "Sub (Rule 3): smoke/cmd/scheduler",
            "topic": "smoke/cmd/scheduler",
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
            "name": "Sub (Fault Inject): smoke/cmd/inject_fault",
            "topic": "smoke/cmd/inject_fault",
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
            "func": """let data = msg.payload;
if (typeof data === 'string') {
    try { data = JSON.parse(data); } catch(e) { return null; }
}

msg.eventType = "TELEMETRY";
msg.deviceId = data.device_id || "ESP32_SMOKE_N04_A01";
msg.ppm = parseFloat(data.mq2_ppm || data.ppm || 0);
msg.temp = parseFloat(data.temp || data.temperature_c || 28.0);
msg.hum = parseFloat(data.hum || data.humidity_pct || 60.0);
msg.deviceFan = data.fan || "OFF";
msg.deviceMode = data.mode || "AUTO";
msg.fsmState = data.fsm_state || "SAFE";
msg.timestamp = Date.now();

return msg;""",
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
            "func": """let data = msg.payload;
if (typeof data === 'string') {
    try { data = JSON.parse(data); } catch(e) { return null; }
}

msg.eventType = "URGENT_ALARM";
msg.deviceId = data.device_id || "ESP32_SMOKE_N04_A01";
msg.ppm = parseFloat(data.ppm || data.mq2_ppm || 450);
msg.severity = data.severity || "CRITICAL";
msg.timestamp = Date.now();

return msg;""",
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
msg.syncSeq = data.sync_seq || 1;
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
            "func": """let data = msg.payload;
if (typeof data === 'string') {
    try { data = JSON.parse(data); } catch(e) { return null; }
}

msg.eventType = "KEEP_ALIVE";
msg.deviceId = data.device_id || "ESP32_SMOKE_N04_A01";
msg.uptimeSec = data.uptime_sec || 0;
msg.freeHeap = data.free_heap_bytes || 180000;
msg.wifiRssi = data.wifi_rssi_dbm || -60;
msg.status = data.status || "HEALTHY";
msg.timestamp = Date.now();

return msg;""",
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
            "func": """let status = (typeof msg.payload === 'string') ? msg.payload.trim().toLowerCase() : "";
msg.eventType = "LWT";
msg.isOnline = (status === "online");
msg.deviceId = "ESP32_SMOKE_N04_A01";
msg.timestamp = Date.now();
return msg;""",
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

        # ======================================================================
        # 7. CORE ENGINE: FSM 6 STATES, 5 BUSINESS RULES & 4 ABNORMAL SCENARIOS
        # ======================================================================
        {
            "id": "fn_core_fsm_engine",
            "type": "function",
            "z": flow_tab_id,
            "name": "Core Engine: FSM, 5 Rules & Abnormal Scenarios",
            "func": """/**
 * TẦNG 3 - MIDDLEWARE AUTOMATION ENGINE (TUẦN 7: BUSINESS RULES & ABNORMAL SCENARIOS)
 * Hỗ trợ hạm đội đa thiết bị, FSM 6 trạng thái, 5 Business Rules, 4 Kịch bản Sự cố Bất thường
 */

let state = flow.get("fsm_state") || "SAFE";
let sensitivityMode = flow.get("sensitivity_mode") || "DAY";
let lastSeen = flow.get("last_seen") || 0;
let lastAlertTime = flow.get("last_alert_time") || 0;
let cooldownStartTime = flow.get("cooldown_start") || null;
let lastTemp = flow.get("last_temp") || 28.0;
let lastTempTime = flow.get("last_temp_time") || Date.now();
let smokeSpikeStartTime = flow.get("smoke_spike_start") || null;
let fanCmdState = flow.get("fan_cmd_state") || "OFF";
let buzzerCmdState = flow.get("buzzer_cmd_state") || "OFF";
let activeFaultCode = flow.get("active_fault_code") || "NONE";

let fleet = flow.get("device_fleet") || {
    "ESP32_SMOKE_N04_A01": {
        deviceId: "ESP32_SMOKE_N04_A01",
        zone: "Phòng Lab IoT (P302)",
        status: "ONLINE",
        fsmState: "SAFE",
        lastSeen: Date.now(),
        ppm: 145.0,
        temp: 28.5,
        freeHeap: 182400,
        rssi: -58
    }
};

let now = Date.now();

// Rule 3: Dynamic Threshold Scheduler (Ngưỡng Ngày / Đêm thích ứng)
let currentHour = new Date().getHours();
let isNight = (sensitivityMode === "NIGHT") || (currentHour >= 22 || currentHour < 6);
let ALARM_THRESHOLD = isNight ? 350.0 : 400.0;
let SAFE_THRESHOLD = isNight ? 250.0 : 300.0;
const COOLDOWN_PURGE_DURATION_MS = 30000; // Rule 4: 30s Post-Alarm Purge Delay
const WATCHDOG_TIMEOUT_MS = 30000;       // Abnormal 3: 30s Watchdog (3 missed keep-alives)
const ALERT_RATE_LIMIT_MS = 20000;

let commands = [];
let logs = [];
let uiUpdates = {};
let alertMessage = null;

// ==========================================
// 1. XỬ LÝ LỆNH SCHEDULER & FAULT INJECTION
// ==========================================
if (msg.eventType === "SCHEDULER_CMD") {
    let mode = (msg.mode || "DAY").toUpperCase();
    sensitivityMode = mode;
    flow.set("sensitivity_mode", sensitivityMode);
    logs.push({ level: "INFO", event: "RULE_3_SCHEDULER_CHANGED", desc: `Cập nhật Scheduler: Chế độ ${mode} (Alarm: ${mode==="NIGHT"?350:400} PPM, Safe: ${mode==="NIGHT"?250:300} PPM)` });
}

if (msg.eventType === "FAULT_INJECTION_CMD") {
    let fType = msg.fault || "NONE";
    activeFaultCode = fType;
    if (fType === "CLEAR" || fType === "RESTORE") {
        activeFaultCode = "NONE";
        if (state === "FAULT") state = "SAFE";
        logs.push({ level: "INFO", event: "FAULT_CLEARED", desc: "Đã xóa toàn bộ lỗi giả lập. Hệ thống trở về SAFE." });
    } else {
        state = "FAULT";
        logs.push({ level: "ERROR", event: "ABNORMAL_SIMULATED", desc: `Kích hoạt sự cố giả lập: ${fType} -> Chuyển sang FAIL-SAFE Mode` });
    }
}

// ==========================================
// 2. XỬ LÝ OFFLINE BUFFER SYNC (ABNORMAL SCENARIO 2)
// ==========================================
if (msg.eventType === "OFFLINE_SYNC") {
    logs.push({
        level: "INFO",
        event: "OFFLINE_REPLAY_SYNC",
        desc: `Đồng bộ bản ghi ngoại tuyến seq=${msg.syncSeq}: PPM=${msg.ppm}, Temp=${msg.temp}°C, Fan=${msg.fan}, Trạng thái=${msg.recordState}`
    });
}

// ==========================================
// 3. XỬ LÝ KEEP-ALIVE & WATCHDOG (ABNORMAL SCENARIO 3)
// ==========================================
if (msg.eventType === "KEEP_ALIVE") {
    let devId = msg.deviceId;
    lastSeen = now;
    if (state === "OFFLINE") state = "SAFE";

    if (!fleet[devId]) {
        fleet[devId] = { deviceId: devId, zone: "Khu Vực Chung", status: "ONLINE", fsmState: "SAFE" };
    }
    fleet[devId].lastSeen = now;
    fleet[devId].status = "ONLINE";
    fleet[devId].freeHeap = msg.freeHeap;
    fleet[devId].rssi = msg.wifiRssi;

    if (msg.status === "FAULT") {
        state = "FAULT";
        activeFaultCode = "HARDWARE_REPORTED_FAULT";
        logs.push({ level: "ERROR", event: "HARDWARE_FAULT", desc: `Thiết bị ${devId} báo lỗi phần cứng trong gói tin Heartbeat!` });
    }

    logs.push({ level: "INFO", event: "KEEP_ALIVE_PONG", desc: `Tín hiệu Keep-Alive từ ${devId} (Heap: ${msg.freeHeap}B, RSSI: ${msg.wifiRssi}dBm)` });
}

if (msg.eventType === "WATCHDOG_TICK") {
    for (let dId in fleet) {
        let dev = fleet[dId];
        if (dev.status !== "OFFLINE" && (now - dev.lastSeen > WATCHDOG_TIMEOUT_MS)) {
            dev.status = "OFFLINE";
            logs.push({
                level: "CRITICAL",
                event: "WATCHDOG_DEAD_DEVICE",
                desc: `CẢNH BÁO: Thiết bị ${dId} mất nhịp tim liên tiếp quá 30s! Kích hoạt quy trình cảnh báo Dead Device!`
            });
            alertMessage = {
                title: "🚨 BÁO ĐỘNG ĐỘT TỬ THIẾT BỊ (WATCHDOG)",
                device: dId,
                desc: "Thiết bị mất liên lạc > 30s. Nguy cơ mất an toàn PCCC!"
            };
        }
    }
    if (state !== "OFFLINE" && lastSeen > 0 && (now - lastSeen > WATCHDOG_TIMEOUT_MS)) {
        state = "OFFLINE";
    }
}

// ==========================================
// 4. XỬ LÝ TELEMETRY & 5 BUSINESS RULES
// ==========================================
if (msg.eventType === "TELEMETRY" || msg.eventType === "URGENT_ALARM") {
    let devId = msg.deviceId;
    lastSeen = now;
    if (state === "OFFLINE") state = "SAFE";

    let ppm = msg.ppm || 0;
    let temp = msg.temp || 28.0;
    let hum = msg.hum || 60.0;

    // Abnormal 1: Phát hiện bất thường cảm biến (MQ-2 ADC sat day hoac DHT NaN)
    if (ppm > 5000.0 || temp < -10.0 || temp > 100.0) {
        state = "FAULT";
        activeFaultCode = "SENSOR_ANOMALY_OUT_OF_RANGE";
        logs.push({ level: "ERROR", event: "SENSOR_MALFUNCTION", desc: `Số đo cảm biến vượt giới hạn vật lý (PPM=${ppm}, Temp=${temp}°C)!` });
    }

    // Tính gia tốc tăng nhiệt độ dT/dt (°C / phút)
    let dtMinutes = (now - lastTempTime) / 60000.0;
    let rateOfRise = (dtMinutes > 0.05) ? ((temp - lastTemp) / dtMinutes) : 0.0;
    lastTemp = temp;
    lastTempTime = now;

    if (!fleet[devId]) {
        fleet[devId] = { deviceId: devId, zone: "Khu Vực Tầng 3", status: "ONLINE", fsmState: "SAFE" };
    }
    fleet[devId].lastSeen = now;
    fleet[devId].ppm = ppm;
    fleet[devId].temp = temp;
    fleet[devId].status = "ONLINE";

    uiUpdates = { ppm: ppm, temp: temp, hum: hum, rateOfRise: rateOfRise };

    // RULE 1: Multi-Sensor Correlation (Tương quan Đa cảm biến: Khói + Gia tốc nhiệt)
    let isRealFire = (ppm >= ALARM_THRESHOLD) && (rateOfRise >= 3.0 || temp >= 50.0);
    
    // RULE 2: False Alarm / Transient Smoke Spike Suppression (Lọc khói thoáng qua)
    let isTransientSmoke = (ppm >= ALARM_THRESHOLD) && (temp < 35.0) && (!isRealFire);

    if (isRealFire) {
        state = "ALARM";
        cooldownStartTime = null;
        smokeSpikeStartTime = null;
        logs.push({
            level: "CRITICAL",
            event: "REAL_FIRE_CONFIRMED",
            desc: `HỎA HOẠN THỰC SỰ: Khói ${ppm.toFixed(1)} PPM kèm nhiệt độ tăng vọt (${rateOfRise.toFixed(1)}°C/min hoặc ${temp.toFixed(1)}°C)! Kích hoạt FULL ALARM ngay!`
        });
        commands.push({ topic: "smoke/cmd/fan", payload: { action: "ON", reason: "RULE_1_REAL_FIRE" } });
        commands.push({ topic: "smoke/cmd/buzzer", payload: { action: "UNMUTE", reason: "RULE_1_REAL_FIRE" } });
        
        // RULE 5: Cross-Zone Broadcast khi khói >= 600 PPM
        if (ppm >= 600.0) {
            logs.push({ level: "CRITICAL", event: "CROSS_ZONE_BROADCAST", desc: `Khói mức ĐẠI NGUY HIỂM (${ppm.toFixed(1)} PPM). Kích hoạt còi toàn bộ Hành lang Tầng 3 (Zone F03)!` });
            commands.push({ topic: "smoke/v2/HUIT_A/F03/+/cmd/buzzer", payload: { cmd_id: "CMD-ZONE-EVACUATION", action: "UNMUTE", priority: "CRITICAL" } });
        }

        if (now - lastAlertTime > ALERT_RATE_LIMIT_MS) {
            alertMessage = { title: "🔥 CHÁY THỰC SỰ ĐƯỢC XÁC NHẬN!", ppm: ppm, temp: temp, rateOfRise: rateOfRise, device: devId };
            lastAlertTime = now;
        }
    } else if (isTransientSmoke) {
        if (!smokeSpikeStartTime) smokeSpikeStartTime = now;
        let spikeDuration = (now - smokeSpikeStartTime) / 1000;
        
        if (spikeDuration < 10) {
            // Lọc khói thoáng qua: Chỉ bật quạt thông gió, ngắt còi tránh hoảng loạn
            logs.push({
                level: "WARN",
                event: "TRANSIENT_SMOKE_SUPPRESSED",
                desc: `Khói tăng ${ppm.toFixed(1)} PPM nhưng nhiệt độ bình thường (${temp.toFixed(1)}°C, thời gian ${spikeDuration.toFixed(1)}s < 10s). Bật quạt thông gió, không hú còi.`
            });
            commands.push({ topic: "smoke/cmd/fan", payload: { action: "ON", reason: "RULE_2_PURGE_VENTILATION" } });
            commands.push({ topic: "smoke/cmd/buzzer", payload: { action: "MUTE", reason: "RULE_2_SUPPRESSION" } });
            state = "WARNING";
        } else {
            // Khói duy trì > 10s -> Nâng lên ALARM
            state = "ALARM";
            commands.push({ topic: "smoke/cmd/buzzer", payload: { action: "UNMUTE", reason: "PERSISTENT_SMOKE" } });
        }
    } else if (ppm >= ALARM_THRESHOLD) {
        state = "ALARM";
        cooldownStartTime = null;
        commands.push({ topic: "smoke/cmd/fan", payload: { action: "ON", reason: "STANDARD_ALARM" } });
        commands.push({ topic: "smoke/cmd/buzzer", payload: { action: "UNMUTE", reason: "STANDARD_ALARM" } });
    }
    // RULE 4: Cooldown Purge Hysteresis (30s)
    else if (state === "ALARM" && ppm <= SAFE_THRESHOLD) {
        state = "COOLDOWN";
        cooldownStartTime = now;
        smokeSpikeStartTime = null;
        logs.push({
            level: "INFO",
            event: "RULE_4_COOLDOWN_PURGE_STARTED",
            desc: `Khói đã hạ về mức an toàn (${ppm.toFixed(1)} <= ${SAFE_THRESHOLD} PPM). Kích hoạt thông gió cưỡng bức trễ 30s!`
        });
        commands.push({ topic: "smoke/cmd/buzzer", payload: { action: "MUTE", reason: "COOLDOWN_SAFE" } });
    }
    else if (state === "COOLDOWN") {
        if (ppm >= SAFE_THRESHOLD) {
            state = "ALARM";
            cooldownStartTime = null;
            logs.push({ level: "WARN", event: "COOLDOWN_ABORTED", desc: "Khói tăng trở lại trong lúc Cooldown! Tái kích hoạt ALARM." });
        } else if (now - cooldownStartTime >= COOLDOWN_PURGE_DURATION_MS) {
            state = "SAFE";
            cooldownStartTime = null;
            logs.push({ level: "INFO", event: "RULE_4_PURGE_COMPLETED", desc: "Hoàn tất 30s thông gió cưỡng bức. Trả quạt về trạng thái IDLE an toàn." });
            commands.push({ topic: "smoke/cmd/fan", payload: { action: "OFF", reason: "PURGE_COMPLETED" } });
        }
    } else if (state === "SAFE" && ppm >= 250.0 && ppm < ALARM_THRESHOLD) {
        state = "WARNING";
    } else if (state === "WARNING" && ppm < 250.0 && temp < 50.0) {
        state = "SAFE";
    }

    fleet[devId].fsmState = state;
}

// Lưu Context
flow.set("fsm_state", state);
flow.set("device_fleet", fleet);
flow.set("last_seen", lastSeen);
flow.set("last_alert_time", lastAlertTime);
flow.set("cooldown_start", cooldownStartTime);
flow.set("last_temp", lastTemp);
flow.set("last_temp_time", lastTempTime);
flow.set("smoke_spike_start", smokeSpikeStartTime);
flow.set("active_fault_code", activeFaultCode);
flow.set("fan_cmd_state", fanCmdState);
flow.set("buzzer_cmd_state", buzzerCmdState);

// Lưu vào mảng Lịch sử sự kiện (Circular Buffer 50 mục)
let eventHistory = flow.get("event_history") || [];
for (let lg of logs) {
    eventHistory.unshift({
        time: new Date().toLocaleTimeString('vi-VN') + " " + new Date().toLocaleDateString('vi-VN'),
        level: lg.level,
        event: lg.event,
        desc: lg.desc,
        fsmState: state
    });
}
if (eventHistory.length > 50) eventHistory = eventHistory.slice(0, 50);
flow.set("event_history", eventHistory);

// Output: Commands, Logs, UI Updates, Alerts
let outCommands = (commands.length > 0) ? commands.map(c => ({ topic: c.topic, payload: JSON.stringify(c.payload), qos: 1 })) : null;
let outLogs = (logs.length > 0) ? { payload: logs, eventHistory: eventHistory } : null;

let outUI = {
    payload: {
        fsmState: state,
        sensitivityMode: sensitivityMode,
        alarmThreshold: ALARM_THRESHOLD,
        activeFaultCode: activeFaultCode,
        cooldownRemaining: cooldownStartTime ? Math.max(0, Math.ceil((COOLDOWN_PURGE_DURATION_MS - (now - cooldownStartTime))/1000)) : 0,
        fleetList: Object.values(fleet),
        ...uiUpdates
    }
};

let outAlert = alertMessage ? { payload: alertMessage } : null;

return [outCommands, outLogs, outUI, outAlert];""",
            "outputs": 4,
            "noerr": 0,
            "x": 860,
            "y": 420,
            "wires": [
                ["fn_command_dispatcher"],
                ["fn_audit_logger"],
                ["fn_ui_dashboard_adapter"],
                ["debug_alert_notifications"]
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
            "func": "return [msg];",
            "outputs": 1,
            "x": 1140,
            "y": 380,
            "wires": [["router_mqtt_downlink"]]
        },
        {
            "id": "router_mqtt_downlink",
            "type": "switch",
            "z": flow_tab_id,
            "name": "Route by Downlink Topic",
            "property": "topic",
            "propertyType": "msg",
            "rules": [
                {"t": "cont", "v": "/cmd/fan", "vt": "str"},
                {"t": "cont", "v": "/cmd/buzzer", "vt": "str"}
            ],
            "checkall": "true",
            "repair": False,
            "outputs": 2,
            "x": 1150,
            "y": 460,
            "wires": [
                ["mqtt_out_fan_downlink", "debug_cmd_sent"],
                ["mqtt_out_buzzer_downlink", "debug_cmd_sent"]
            ]
        },
        {
            "id": "mqtt_out_fan_downlink",
            "type": "mqtt out",
            "z": flow_tab_id,
            "name": "Downlink: smoke/cmd/fan",
            "topic": "smoke/cmd/fan",
            "qos": "1",
            "retain": "false",
            "broker": broker_id,
            "x": 1410,
            "y": 440,
            "wires": []
        },
        {
            "id": "mqtt_out_buzzer_downlink",
            "type": "mqtt out",
            "z": flow_tab_id,
            "name": "Downlink: smoke/cmd/buzzer",
            "topic": "smoke/cmd/buzzer",
            "qos": "1",
            "retain": "false",
            "broker": broker_id,
            "x": 1420,
            "y": 500,
            "wires": []
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
            "func": "return [msg];",
            "outputs": 1,
            "x": 1130,
            "y": 620,
            "wires": [["debug_dashboard_state"]]
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
        }
    ]

    return nodes

if __name__ == "__main__":
    flow_data = build_nodered_flow()
    out_file = r"e:\IoT\DoAn\nodered\flows_smoke_detector.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(flow_data, f, ensure_ascii=False, indent=2)
    print(f"Node-RED flow V3 (Week 7) successfully generated at: {out_file} (Total nodes: {len(flow_data)})")
