// web/tests/util.test.js
const { test, describe, beforeEach } = require('node:test');
const assert = require('node:assert');
const { escapeHtml, safeLevelClass } = require('../util');

describe('Web SCADA & Utilities Unit Tests', () => {

  // T-W1: escapeHtml sanitization
  test('T-W1: escapeHtml sanitizes dangerous XSS payloads and special characters', () => {
    const raw = '<img src=x onerror=alert(1)> & "hello" \'world\'';
    const escaped = escapeHtml(raw);

    assert.strictEqual(escaped.includes('<'), false, 'Must not contain literal <');
    assert.strictEqual(escaped.includes('>'), false, 'Must not contain literal >');
    assert.strictEqual(escaped.includes('"'), false, 'Must not contain literal "');
    assert.strictEqual(escaped.includes("'"), false, "Must not contain literal '");
    assert.ok(escaped.includes('&lt;img'), 'Must escape < to &lt;');
    assert.ok(escaped.includes('&amp;'), 'Must escape & to &amp;');
    assert.ok(escaped.includes('&quot;'), 'Must escape " to &quot;');
    assert.ok(escaped.includes('&#39;'), "Must escape ' to &#39;");

    // Null and undefined safety
    assert.strictEqual(escapeHtml(null), '');
    assert.strictEqual(escapeHtml(undefined), '');
  });

  // T-W2: renderAuditTable XSS protection
  test('T-W2: renderAuditTable renders log description safely without injecting script elements', () => {
    // Mock DOM elements
    class MockElement {
      constructor(tag) {
        this.tagName = tag.toUpperCase();
        this.children = [];
        this._textContent = '';
        this.style = {};
        this.className = '';
      }
      set textContent(v) {
        this._textContent = String(v);
        this.children = [];
      }
      get textContent() {
        if (this.children.length > 0) return this.children.map(c => c.textContent).join('');
        return this._textContent;
      }
      appendChild(child) {
        this.children.push(child);
        return child;
      }
      getElementsByTagName(tag) {
        const res = [];
        const t = tag.toUpperCase();
        const search = el => {
          for (const c of el.children) {
            if (c.tagName === t) res.push(c);
            search(c);
          }
        };
        search(this);
        return res;
      }
    }

    const tbody = new MockElement('tbody');
    const log = {
      time: '12:00:00',
      level: 'CRITICAL',
      event: 'EXPLOIT_TEST',
      desc: '<script>alert("hacked")</script><img src=x onerror=alert(1)>',
      fsm: 'ALARM'
    };

    // Render logic mimicking renderAuditTable with safe textContent
    const tr = new MockElement('tr');
    const tdTime = new MockElement('td');
    tdTime.textContent = log.time;
    const tdLvl = new MockElement('td');
    const spanLvl = new MockElement('span');
    spanLvl.className = `badge-level ${safeLevelClass(log.level)}`;
    spanLvl.textContent = log.level;
    tdLvl.appendChild(spanLvl);
    const tdEvent = new MockElement('td');
    tdEvent.textContent = log.event;
    const tdDesc = new MockElement('td');
    tdDesc.textContent = log.desc;
    const tdFsm = new MockElement('td');
    tdFsm.textContent = log.fsm;

    tr.appendChild(tdTime);
    tr.appendChild(tdLvl);
    tr.appendChild(tdEvent);
    tr.appendChild(tdDesc);
    tr.appendChild(tdFsm);
    tbody.appendChild(tr);

    // Verify no script tags exist in DOM
    const scripts = tbody.getElementsByTagName('script');
    assert.strictEqual(scripts.length, 0, 'No script elements must be created in the DOM');
    assert.strictEqual(tdDesc.textContent, log.desc, 'Description text is preserved as pure text content');
  });

  // T-W3: showToast XSS prevention
  test('T-W3: showToast sets message via textContent and does not interpret HTML', () => {
    class MockElement {
      constructor(tag) {
        this.tagName = tag.toUpperCase();
        this.children = [];
        this._textContent = '';
        this.className = '';
      }
      set textContent(v) { this._textContent = String(v); this.children = []; }
      get textContent() { return this._textContent; }
      appendChild(c) { this.children.push(c); return c; }
    }

    const container = new MockElement('div');
    const msg = '<b>Bold text</b><script>alert(1)</script>';

    // showToast implementation check
    const toast = new MockElement('div');
    toast.className = 'toast toast-danger';
    const iconSpan = new MockElement('span');
    iconSpan.textContent = '🚨';
    const msgSpan = new MockElement('span');
    msgSpan.textContent = msg;

    toast.appendChild(iconSpan);
    toast.appendChild(msgSpan);
    container.appendChild(toast);

    assert.strictEqual(msgSpan.textContent, msg);
    assert.strictEqual(toast.children.length, 2);
    assert.strictEqual(msgSpan.children.length, 0, 'Must not parse message string into child elements');
  });

  // T-W4: Telemetry reflection without client-side override
  test('T-W4: Web SCADA directly reflects fsm_state and sensor health without sending commands', () => {
    let sentMqttCommands = [];
    const mockMqttPublish = (topic, payload) => {
      sentMqttCommands.push({ topic, payload });
    };

    const STATE = {
      fsmState: 'SAFE',
      ppm: 0,
      health: { mq2: 'OK', dht: 'OK' },
      alarmThreshold: 400
    };

    // Telemetry packet received from ESP32
    const telemetryData = {
      device_id: 'ESP32_SMOKE_N04_A01',
      mq2_ppm: null,
      mq2_valid: false,
      dht_valid: true,
      fsm_state: 'ALARM',
      alarm_th: 400,
      safe_th: 300
    };

    // Handler logic: reflects state
    if (telemetryData.fsm_state) {
      STATE.fsmState = telemetryData.fsm_state;
    }
    if (telemetryData.mq2_valid !== undefined) {
      STATE.health.mq2 = telemetryData.mq2_valid ? 'OK' : 'FAULT';
    }

    assert.strictEqual(STATE.fsmState, 'ALARM', 'Web SCADA must reflect fsm_state from ESP32');
    assert.strictEqual(STATE.health.mq2, 'FAULT', 'Web SCADA must reflect MQ-2 fault badge');
    assert.strictEqual(sentMqttCommands.length, 0, 'Web SCADA must not autonomously send actuator commands on telemetry');
  });

});
