// nodered/tests/flow_integration.test.js
// Flow-level integration test validating the actual flows_smoke_detector.json
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');

const flowPath = path.resolve(__dirname, '../flows_smoke_detector.json');
const flowJson = JSON.parse(fs.readFileSync(flowPath, 'utf8'));

// Build indexed map of nodes by ID
const nodeMap = new Map();
flowJson.forEach(n => nodeMap.set(n.id, n));

function createMockContext() {
  const store = {};
  return {
    get: (k) => store[k],
    set: (k, v) => { store[k] = v; },
    _store: store
  };
}

function runNodeFunction(node, msg, flowCtx, nodeCtx = {}) {
  const fn = new Function('msg', 'flow', 'node', node.func);
  return fn(msg, flowCtx, {
    warn: () => {},
    error: () => {},
    send: () => {},
    ...nodeCtx
  });
}

test('FLOW-01: Structural wiring verification of flows_smoke_detector.json', () => {
  const authNode = nodeMap.get('fn_auth_service');
  assert.ok(authNode, 'fn_auth_service must exist');
  assert.ok(authNode.func.includes('flow.set("fleet"'), 'fn_auth_service must write to "fleet"');

  const alarmNode = nodeMap.get('fn_parse_alarm');
  assert.ok(alarmNode, 'fn_parse_alarm must exist');
  assert.ok(alarmNode.func.includes("ALARM_EVENT"), 'fn_parse_alarm must set ALARM_EVENT');
  assert.ok(alarmNode.func.includes("cache"), 'fn_parse_alarm must have dedup cache');

  const keepAliveNode = nodeMap.get('fn_parse_keepalive');
  assert.ok(keepAliveNode, 'fn_parse_keepalive must exist');
  assert.ok(keepAliveNode.func.includes("KEEP_ALIVE"), 'fn_parse_keepalive must set KEEP_ALIVE');

  const schedInject = nodeMap.get('inject_scheduler_1m');
  assert.ok(schedInject, 'inject_scheduler_1m must exist');
  assert.equal(schedInject.repeat, '60', 'Scheduler must repeat every 60s');
  assert.deepEqual(schedInject.wires[0], ['fn_scheduler_tick']);

  const schedTick = nodeMap.get('fn_scheduler_tick');
  assert.ok(schedTick, 'fn_scheduler_tick must exist');
  assert.ok(schedTick.wires[0].includes('fn_command_dispatcher'));

  const coreEngine = nodeMap.get('fn_core_fsm_engine');
  assert.ok(coreEngine, 'fn_core_fsm_engine must exist');
  assert.equal(coreEngine.outputs, 4);
  assert.ok(coreEngine.wires[0].includes('fn_command_dispatcher'));
  assert.ok(coreEngine.wires[1].includes('fn_audit_logger'));
  assert.ok(coreEngine.wires[2].includes('fn_ui_dashboard_adapter'));
  assert.ok(coreEngine.wires[3].includes('fn_alert_dispatcher'));
});

test('FLOW-02: Auth populates fleet topology & Core Engine generates hierarchical V2 topics', () => {
  const flowCtx = createMockContext();
  const authNode = nodeMap.get('fn_auth_service');
  const coreEngine = nodeMap.get('fn_core_fsm_engine');
  const cmdDispatcher = nodeMap.get('fn_command_dispatcher');

  // Authenticate ESP32_SMOKE_N09_A01
  const authReqA01 = {
    payload: {
      device_id: 'ESP32_SMOKE_N09_A01',
      mac_address: '24:6F:28:AB:CD:10',
      secret_token: 'HUIT_IOT_SECURE_TOKEN_N09'
    }
  };
  const [authResp1] = runNodeFunction(authNode, authReqA01, flowCtx);
  assert.equal(authResp1.topic, 'Nhom09/smoke/v2/auth/response/ESP32_SMOKE_N09_A01');
  const payload1 = JSON.parse(authResp1.payload);
  assert.equal(payload1.status, 'PASS');

  // Check flow context fleet has topology
  const fleet = flowCtx.get('fleet');
  assert.ok(fleet['ESP32_SMOKE_N09_A01']);
  assert.deepEqual(fleet['ESP32_SMOKE_N09_A01'].topology, {
    building: 'HUIT_A',
    floor: 'F03',
    room: 'P302',
    zone: 'Phòng Lab IoT'
  });

  // Authenticate ESP32_SMOKE_N09_A02
  const authReqA02 = {
    payload: {
      device_id: 'ESP32_SMOKE_N09_A02',
      mac_address: '24:6F:28:AB:CD:20',
      secret_token: 'HUIT_IOT_SECURE_TOKEN_N09'
    }
  };
  runNodeFunction(authNode, authReqA02, flowCtx);

  // Send high smoke telemetry (650 PPM, temp 52.0 C) from A01 to trigger Rule 1 and Rule 5
  const parseTelemetryNode = nodeMap.get('fn_parse_telemetry');
  const telemetryMsg = runNodeFunction(parseTelemetryNode, {
    payload: {
      device_id: 'ESP32_SMOKE_N09_A01',
      mq2_ppm: 650.0,
      temp: 52.0,
      hum: 58.5,
      fsm_state: 'SAFE',
      uptime_s: 100
    }
  }, flowCtx);

  assert.equal(telemetryMsg.eventType, 'TELEMETRY');
  assert.equal(telemetryMsg.hum, 58.5);

  const [cmds, logs, dashboard, alert] = runNodeFunction(coreEngine, telemetryMsg, flowCtx);

  // Check dashboard carries humidity
  assert.ok(dashboard);
  assert.equal(dashboard.payload.hum, 58.5);

  // Check Rule 5 cross-zone broadcast generated a valid V2 command for A02
  assert.ok(cmds && cmds.length >= 2, 'Should emit fan command for A01 and cross-zone for A02');
  const crossCmd = cmds.find(c => c.topic.includes('ESP32_SMOKE_N09_A02'));
  assert.ok(crossCmd, 'Should have cross-zone evacuation command for ESP32_SMOKE_N09_A02');
  assert.equal(crossCmd.topic, 'Nhom09/smoke/v2/HUIT_A/F03/P303/ESP32_SMOKE_N09_A02/cmd/buzzer');

  // Verify command dispatcher accepts topic without wildcard errors
  const dispatched = runNodeFunction(cmdDispatcher, crossCmd, flowCtx);
  assert.ok(dispatched, 'Command dispatcher must pass valid hierarchical topic');
  assert.equal(dispatched.topic, 'Nhom09/smoke/v2/HUIT_A/F03/P303/ESP32_SMOKE_N09_A02/cmd/buzzer');
});

test('FLOW-03: Scheduler inject & tick updates fleet Day/Night thresholds deterministically', () => {
  const origGetHours = Date.prototype.getHours;
  try {
    const flowCtx = createMockContext();
    flowCtx.set('fleet', {
      ESP32_SMOKE_N09_A01: { deviceId: 'ESP32_SMOKE_N09_A01', alarmTh: 400, safeTh: 300 }
    });

    const schedTick = nodeMap.get('fn_scheduler_tick');
    const parseSched = nodeMap.get('fn_parse_scheduler');
    const coreEngine = nodeMap.get('fn_core_fsm_engine');

    // 1. Simulate NIGHT (23h)
    Date.prototype.getHours = () => 23;
    flowCtx.set('sched', null); // clear state
    const nightTick = runNodeFunction(schedTick, {}, flowCtx);
    assert.ok(nightTick, 'Scheduler tick must fire for NIGHT');
    const nightParsed = runNodeFunction(parseSched, nightTick, flowCtx);
    assert.equal(nightParsed.eventType, 'SCHEDULER_CMD');
    assert.equal(nightParsed.mode, 'NIGHT');
    runNodeFunction(coreEngine, nightParsed, flowCtx);
    let dev = flowCtx.get('fleet')['ESP32_SMOKE_N09_A01'];
    assert.equal(dev.alarmTh, 350, 'NIGHT mode must set alarmTh to 350');
    assert.equal(dev.safeTh, 262.5, 'NIGHT mode must set safeTh to 262.5');

    // 2. Simulate DAY (14h)
    Date.prototype.getHours = () => 14;
    const dayTick = runNodeFunction(schedTick, {}, flowCtx);
    assert.ok(dayTick, 'Scheduler tick must fire for transition to DAY');
    const dayParsed = runNodeFunction(parseSched, dayTick, flowCtx);
    assert.equal(dayParsed.eventType, 'SCHEDULER_CMD');
    assert.equal(dayParsed.mode, 'DAY');
    runNodeFunction(coreEngine, dayParsed, flowCtx);
    dev = flowCtx.get('fleet')['ESP32_SMOKE_N09_A01'];
    assert.equal(dev.alarmTh, 400, 'DAY mode must set alarmTh to 400');
    assert.equal(dev.safeTh, 300, 'DAY mode must set safeTh to 300');
  } finally {
    Date.prototype.getHours = origGetHours;
  }
});

test('FLOW-04: Alarm and keep-alive parsers deduplicate rapid duplicate payloads', () => {
  const flowCtx = createMockContext();
  const parseAlarm = nodeMap.get('fn_parse_alarm');
  const parseKeepAlive = nodeMap.get('fn_parse_keepalive');

  const alarmPayload = {
    device_id: 'ESP32_SMOKE_N09_A01',
    event: 'SMOKE_ALERT',
    ppm: 450,
    uptime_s: 120
  };

  const m1 = runNodeFunction(parseAlarm, { payload: alarmPayload }, flowCtx);
  assert.ok(m1, 'First alarm event must pass');
  assert.equal(m1.eventType, 'ALARM_EVENT');

  const m2 = runNodeFunction(parseAlarm, { payload: alarmPayload }, flowCtx);
  assert.equal(m2, null, 'Duplicate alarm event within 5s must be suppressed');

  const kaPayload = {
    device_id: 'ESP32_SMOKE_N09_A01',
    uptime_sec: 120,
    free_heap_bytes: 180000
  };

  const k1 = runNodeFunction(parseKeepAlive, { payload: kaPayload }, flowCtx);
  assert.ok(k1, 'First keep-alive must pass');
  assert.equal(k1.eventType, 'KEEP_ALIVE');

  const k2 = runNodeFunction(parseKeepAlive, { payload: kaPayload }, flowCtx);
  assert.equal(k2, null, 'Duplicate keep-alive within 5s must be suppressed');
});
