// nodered/tests/engine.test.js
const { test, describe, beforeEach } = require('node:test');
const assert = require('node:assert');
const { load, mkFlow, node, mkEnv } = require('./harness');

describe('Node-RED Engine & Functions Unit Tests', () => {
  let parseTelemetry, parseLwt, coreEngine, cmdDispatcher, alertDispatcher, schedTick;
  let flow;

  beforeEach(() => {
    parseTelemetry = load('functions/parse_telemetry.js');
    parseLwt = load('functions/parse_lwt.js');
    coreEngine = load('functions/core_engine.js');
    cmdDispatcher = load('functions/command_dispatcher.js');
    alertDispatcher = load('functions/alert_dispatcher.js');
    schedTick = load('functions/scheduler_tick.js');
    flow = mkFlow();
  });

  // T-N1: Deduplication TTL 5s
  test('T-N1: Deduplication within 5s TTL and re-allowed after 5s', () => {
    let originalNow = Date.now;
    let fakeTime = 1000000;
    Date.now = () => fakeTime;

    try {
      const msg1 = { payload: { device_id: 'A01', uptime_s: 42, mq2_ppm: 250, temp: 28 } };
      const res1 = parseTelemetry(msg1, flow, node, mkEnv());
      assert.ok(res1 !== null, 'First message should be processed');
      assert.strictEqual(res1.uptime, 42);

      // Same uptime immediately (simulating V2 parallel message)
      const msg2 = { payload: { device_id: 'A01', uptime_s: 42, mq2_ppm: 250, temp: 28 } };
      const res2 = parseTelemetry(msg2, flow, node, mkEnv());
      assert.strictEqual(res2, null, 'Duplicate within 5s should be dropped');

      // Advance time by 6000ms (> 5s TTL)
      fakeTime += 6000;
      const msg3 = { payload: { device_id: 'A01', uptime_s: 42, mq2_ppm: 250, temp: 28 } };
      const res3 = parseTelemetry(msg3, flow, node, mkEnv());
      assert.ok(res3 !== null, 'Message after 5s TTL should be re-allowed');
    } finally {
      Date.now = originalNow;
    }
  });

  // T-N2: LWT parsing
  test('T-N2: LWT JSON status and raw string parsing', () => {
    const resJsonOnline = parseLwt({ payload: '{"device_id":"ESP32_01","status":"online"}' }, flow, node, mkEnv());
    assert.strictEqual(resJsonOnline.isOnline, true);
    assert.strictEqual(resJsonOnline.deviceId, 'ESP32_01');

    const resJsonOffline = parseLwt({ payload: { device_id: 'ESP32_01', status: 'offline' } }, flow, node, mkEnv());
    assert.strictEqual(resJsonOffline.isOnline, false);

    const resRawOnline = parseLwt({ payload: 'online' }, flow, node, mkEnv());
    assert.strictEqual(resRawOnline.isOnline, true);

    const resRawOffline = parseLwt({ payload: 'offline' }, flow, node, mkEnv());
    assert.strictEqual(resRawOffline.isOnline, false);
  });

  // T-N3: Low-heat smoke (Rule 2)
  test('T-N3: PPM 450 with low heat (temp 30, dT/dt 0) triggers ALARM, fan ON, no MUTE', () => {
    const msg = {
      eventType: 'TELEMETRY',
      deviceId: 'A01',
      ppm: 450,
      temp: 30,
      fsmState: 'ALARM',
      mq2Valid: true,
      dhtValid: true,
      alarmTh: 400,
      safeTh: 300
    };

    const out = coreEngine(msg, flow, node, mkEnv());
    const cmds = out[0];
    const alert = out[3];
    const fleet = flow.get('fleet');

    assert.strictEqual(fleet['A01'].effective, 'ALARM');
    assert.ok(cmds && cmds.length > 0, 'Commands should be dispatched');

    const fanCmd = cmds.find(c => c.topic.includes('/cmd/fan'));
    assert.ok(fanCmd, 'Fan command should be present');
    const fanPayload = JSON.parse(fanCmd.payload);
    assert.strictEqual(fanPayload.action, 'ON');
    assert.strictEqual(fanPayload.reason, 'RULE_2_LOW_HEAT_SMOKE');

    const muteCmd = cmds.find(c => c.topic.includes('/cmd/buzzer') && JSON.parse(c.payload).action === 'MUTE');
    assert.strictEqual(muteCmd, undefined, 'Must NOT contain MUTE command');
    assert.ok(alert !== null, 'Alert notification should be generated');
  });

  // T-N4: Real fire (Rule 1)
  test('T-N4: Temperature rate >= 3.0 C/min triggers UNMUTE once', () => {
    let originalNow = Date.now;
    let fakeTime = 1000000;
    Date.now = () => fakeTime;

    try {
      // First telemetry at t=0: temp=28, ppm=450
      const msg1 = {
        eventType: 'TELEMETRY',
        deviceId: 'A01',
        ppm: 450,
        temp: 28,
        fsmState: 'ALARM',
        mq2Valid: true,
        dhtValid: true,
        alarmTh: 400,
        safeTh: 300
      };
      coreEngine(msg1, flow, node, mkEnv());

      // Advance by 25s (25000ms), temp rises from 28 to 29.5 -> rate = 1.5 / (25/60) = 3.6 C/min >= 3.0
      fakeTime += 25000;
      const msg2 = {
        eventType: 'TELEMETRY',
        deviceId: 'A01',
        ppm: 450,
        temp: 29.5,
        fsmState: 'ALARM',
        mq2Valid: true,
        dhtValid: true,
        alarmTh: 400,
        safeTh: 300
      };
      const out2 = coreEngine(msg2, flow, node, mkEnv());
      const cmds2 = out2[0];
      assert.ok(cmds2, 'Commands expected on real fire confirmation');
      const unmuteCmd = cmds2.find(c => c.topic.includes('/cmd/buzzer') && JSON.parse(c.payload).action === 'UNMUTE');
      assert.ok(unmuteCmd, 'UNMUTE command should be dispatched');

      // Subsequent packet 2s later with same high temp
      fakeTime += 2000;
      const msg3 = {
        eventType: 'TELEMETRY',
        deviceId: 'A01',
        ppm: 450,
        temp: 29.5,
        fsmState: 'ALARM',
        mq2Valid: true,
        dhtValid: true,
        alarmTh: 400,
        safeTh: 300
      };
      const out3 = coreEngine(msg3, flow, node, mkEnv());
      const cmds3 = out3[0];
      const dupUnmute = (cmds3 || []).find(c => c.topic.includes('/cmd/buzzer') && JSON.parse(c.payload).action === 'UNMUTE');
      assert.strictEqual(dupUnmute, undefined, 'Must NOT re-dispatch UNMUTE continuously');
    } finally {
      Date.now = originalNow;
    }
  });

  // T-N5: Cross-zone broadcast (Rule 5)
  test('T-N5: Cross-zone broadcast over 600 PPM to floor F03 devices without wildcards', () => {
    let originalNow = Date.now;
    let fakeTime = 1000000;
    Date.now = () => fakeTime;

    try {
      // Setup fleet with A02 on Floor F03 with concrete topology
      const fleet = {
        A02: {
          deviceId: 'A02',
          status: 'ONLINE',
          deviceState: 'SAFE',
          effective: 'SAFE',
          topology: { building: 'HUIT_A', floor: 'F03', room: 'P303' }
        }
      };
      flow.set('fleet', fleet);

      // A01 first packet with PPM 655
      const msg1 = {
        eventType: 'TELEMETRY',
        deviceId: 'A01',
        ppm: 655,
        temp: 30,
        fsmState: 'ALARM',
        mq2Valid: true,
        dhtValid: true,
        alarmTh: 400,
        safeTh: 300
      };
      const out1 = coreEngine(msg1, flow, node, mkEnv());
      const cmds1 = out1[0];
      assert.ok(cmds1 && cmds1.length > 0, 'Should dispatch cross-zone commands');

      const evacCmd = cmds1.find(c => c.topic.includes('A02/cmd/buzzer'));
      assert.ok(evacCmd, 'Should send evacuation command to A02');
      assert.strictEqual(evacCmd.topic.includes('+'), false, 'Topic must NOT contain +');
      assert.strictEqual(evacCmd.topic.includes('#'), false, 'Topic must NOT contain #');
      assert.strictEqual(evacCmd.topic, 'Nhom09/smoke/v2/HUIT_A/F03/P303/A02/cmd/buzzer');

      // Second packet within 60s
      fakeTime += 10000;
      const msg2 = {
        eventType: 'TELEMETRY',
        deviceId: 'A01',
        ppm: 660,
        temp: 30,
        fsmState: 'ALARM',
        mq2Valid: true,
        dhtValid: true,
        alarmTh: 400,
        safeTh: 300
      };
      const out2 = coreEngine(msg2, flow, node, mkEnv());
      const cmds2 = out2[0] || [];
      const dupEvac = cmds2.find(c => c.topic.includes('A02/cmd/buzzer'));
      assert.strictEqual(dupEvac, undefined, 'Must rate-limit cross-zone broadcast (60s window)');
    } finally {
      Date.now = originalNow;
    }
  });

  // T-N6: MQ-2 Fault
  test('T-N6: mq2_valid:false escalates to FAULT and ignores PPM rules', () => {
    const msg = {
      eventType: 'TELEMETRY',
      deviceId: 'A01',
      ppm: null,
      mq2Valid: false,
      dhtValid: true,
      temp: 28,
      fsmState: 'SAFE',
      alarmTh: 400,
      safeTh: 300
    };

    const out = coreEngine(msg, flow, node, mkEnv());
    const fleet = flow.get('fleet');
    assert.strictEqual(fleet['A01'].effective, 'FAULT');
    const cmds = out[0];
    assert.strictEqual(cmds, null, 'No commands should be generated from invalid PPM');
  });

  // T-N7: Cooldown
  test('T-N7: Device reporting COOLDOWN keeps effective COOLDOWN without commands', () => {
    const msg = {
      eventType: 'TELEMETRY',
      deviceId: 'A01',
      ppm: 250,
      temp: 28,
      fsmState: 'COOLDOWN',
      mq2Valid: true,
      dhtValid: true,
      alarmTh: 400,
      safeTh: 300
    };

    const out = coreEngine(msg, flow, node, mkEnv());
    const fleet = flow.get('fleet');
    assert.strictEqual(fleet['A01'].effective, 'COOLDOWN');
    assert.strictEqual(out[0], null, 'No commands should be dispatched during COOLDOWN');
  });

  // T-N8: Multi-device isolation
  test('T-N8: Device states are strictly isolated', () => {
    coreEngine({
      eventType: 'TELEMETRY',
      deviceId: 'A01',
      ppm: 450,
      temp: 30,
      fsmState: 'ALARM',
      mq2Valid: true,
      dhtValid: true
    }, flow, node, mkEnv());

    coreEngine({
      eventType: 'TELEMETRY',
      deviceId: 'A02',
      ppm: 200,
      temp: 26,
      fsmState: 'SAFE',
      mq2Valid: true,
      dhtValid: true
    }, flow, node, mkEnv());

    const fleet = flow.get('fleet');
    assert.strictEqual(fleet['A01'].effective, 'ALARM');
    assert.strictEqual(fleet['A02'].effective, 'SAFE');
  });

  // T-N9: Command Dispatcher wildcard check
  test('T-N9: Command Dispatcher drops topics with + or # wildcards', () => {
    let warningLogged = false;
    const testNode = {
      warn: () => { warningLogged = true; }
    };

    const invalidMsg = { topic: 'Nhom09/smoke/v2/HUIT_A/F03/+/cmd/buzzer', payload: '{}' };
    const resInvalid = cmdDispatcher(invalidMsg, flow, testNode, mkEnv());
    assert.strictEqual(resInvalid, null, 'Wildcard topic must be dropped');
    assert.strictEqual(warningLogged, true, 'Warning should be logged');

    const validMsg = { topic: 'Nhom09/smoke/cmd/fan', payload: '{}' };
    const resValid = cmdDispatcher(validMsg, flow, testNode, mkEnv());
    assert.strictEqual(resValid, validMsg, 'Valid concrete topic must pass');
  });

  // T-N10: Watchdog timeout
  test('T-N10: Watchdog turns only silent device to OFFLINE after 30s', () => {
    let originalNow = Date.now;
    let fakeTime = 1000000;
    Date.now = () => fakeTime;

    try {
      const fleet = {
        A01: { deviceId: 'A01', status: 'ONLINE', effective: 'SAFE', lastSeen: fakeTime - 31000 },
        A02: { deviceId: 'A02', status: 'ONLINE', effective: 'SAFE', lastSeen: fakeTime - 5000 }
      };
      flow.set('fleet', fleet);

      coreEngine({ eventType: 'WATCHDOG_TICK' }, flow, node, mkEnv());

      const updated = flow.get('fleet');
      assert.strictEqual(updated['A01'].status, 'OFFLINE');
      assert.strictEqual(updated['A01'].effective, 'OFFLINE');
      assert.strictEqual(updated['A02'].status, 'ONLINE');
    } finally {
      Date.now = originalNow;
    }
  });

  // T-N11: Fault injection logging
  test('T-N11: Fault injection commands are logged without altering state directly', () => {
    const fleet = {
      A01: { deviceId: 'A01', status: 'ONLINE', effective: 'SAFE', deviceState: 'SAFE' }
    };
    flow.set('fleet', fleet);

    coreEngine({ eventType: 'FAULT_INJECTION_CMD', deviceId: 'A01', faultType: 'UNKNOWN_FAULT' }, flow, node, mkEnv());

    const updated = flow.get('fleet');
    assert.strictEqual(updated['A01'].effective, 'SAFE');
    const history = flow.get('history') || [];
    assert.ok(history.some(h => h.event === 'FAULT_INJECTION_SEEN'));
  });

  // T-N12: Alert dispatcher mock
  test('T-N12: Without TELEGRAM_TOKEN, alert dispatcher outputs to debug/dashboard mock only', () => {
    const alertMsg = { payload: { deviceId: 'A01', text: 'Canh bao chay' } };
    const out = alertDispatcher(alertMsg, flow, node, mkEnv({}));

    assert.strictEqual(out[0], null, 'HTTP request must be null when token is missing');
    assert.ok(out[1] && out[1].payload.includes('[A01] Canh bao chay'), 'Output 2 must carry mock text');
  });
});
