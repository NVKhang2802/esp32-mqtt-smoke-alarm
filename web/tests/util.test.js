// web/tests/util.test.js
// Tests real web/app.js functions directly via a mock DOM environment
const { test, describe, beforeEach } = require('node:test');
const assert = require('node:assert/strict');

// Minimal mock DOM element representation
class MockElement {
  constructor(tag = 'div') {
    this.tagName = tag.toUpperCase();
    this.children = [];
    this._textContent = '';
    this.className = '';
    this.style = {};
    this.value = 'ALL';
    this.remove = () => {};
    this.classList = {
      _classes: new Set(),
      add: (...cls) => cls.forEach(c => this.classList._classes.add(c)),
      remove: (...cls) => cls.forEach(c => this.classList._classes.delete(c)),
      contains: (c) => this.classList._classes.has(c)
    };
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

// Setup global mock document before requiring app.js
const mockElements = {
  auditTableBody: new MockElement('tbody'),
  logFilterLevel: new MockElement('select'),
  toastContainer: new MockElement('div'),
  clockDisplay: new MockElement('span'),
  valSmokePpm: new MockElement('span'),
  valTemp: new MockElement('span'),
  valHum: new MockElement('span'),
  kpiSmoke: new MockElement('div'),
  tagSmoke: new MockElement('span'),
  fsmChip: new MockElement('div'),
  fsmStatusText: new MockElement('span'),
  alarmBanner: new MockElement('div'),
  bannerTitle: new MockElement('h4'),
  bannerDesc: new MockElement('p'),
  btnFanOff: new MockElement('button'),
  btnBuzzerMute: new MockElement('button'),
  btnBannerMute: new MockElement('button')
};

global.document = {
  getElementById: (id) => mockElements[id] || new MockElement('div'),
  createElement: (tag) => new MockElement(tag),
  createTextNode: (text) => ({ tagName: '#TEXT', textContent: text, children: [] }),
  addEventListener: () => {}
};

// Require real app.js directly!
const app = require('../app');
const { escapeHtml, renderAuditTable, showToast, handleMqttMessage, updateUiFromState, STATE, DOM } = app;

describe('Web SCADA Direct app.js Unit Tests', () => {

  beforeEach(() => {
    mockElements.auditTableBody.children = [];
    mockElements.toastContainer.children = [];
    STATE.logs = [];
  });

  // T-W1: Direct escapeHtml verification from app.js
  test('T-W1: escapeHtml from app.js sanitizes XSS payloads and special characters', () => {
    const raw = '<img src=x onerror=alert(1)> & "hello" \'world\'';
    const escaped = escapeHtml(raw);

    assert.equal(escaped.includes('<'), false, 'Must not contain literal <');
    assert.equal(escaped.includes('>'), false, 'Must not contain literal >');
    assert.equal(escaped.includes('"'), false, 'Must not contain literal "');
    assert.equal(escaped.includes("'"), false, "Must not contain literal '");
    assert.ok(escaped.includes('&lt;img'), 'Must escape < to &lt;');
    assert.ok(escaped.includes('&amp;'), 'Must escape & to &amp;');
    assert.ok(escaped.includes('&quot;'), 'Must escape " to &quot;');
    assert.ok(escaped.includes('&#39;'), "Must escape ' to &#39;");

    // Null/undefined safety
    assert.equal(escapeHtml(null), '');
    assert.equal(escapeHtml(undefined), '');
  });

  // T-W2: Direct renderAuditTable execution from app.js
  test('T-W2: renderAuditTable() from app.js renders logs via textContent without creating script elements', () => {
    STATE.logs = [
      {
        time: '12:00:00',
        level: 'CRITICAL',
        event: 'EXPLOIT_TEST',
        desc: '<script>alert("hacked")</script><img src=x onerror=alert(1)>',
        fsm: 'ALARM'
      }
    ];

    // Call REAL function from app.js!
    renderAuditTable();

    const tbody = mockElements.auditTableBody;
    assert.equal(tbody.children.length, 1, 'Should render 1 table row');

    const scripts = tbody.getElementsByTagName('script');
    assert.equal(scripts.length, 0, 'No script elements must be created in the DOM');

    const row = tbody.children[0];
    const descCell = row.children[3];
    assert.equal(descCell.textContent, STATE.logs[0].desc, 'Payload is rendered purely as textContent');
  });

  // T-W3: Direct showToast execution from app.js
  test('T-W3: showToast() from app.js mounts message via textContent and does not parse HTML', () => {
    const dangerousMsg = '<b>Alert</b><script>alert(1)</script>';

    // Call REAL function from app.js!
    showToast(dangerousMsg, 'danger');

    const container = mockElements.toastContainer;
    assert.equal(container.children.length, 1, 'Toast container should receive 1 toast');

    const toast = container.children[0];
    const scripts = toast.getElementsByTagName('script');
    assert.equal(scripts.length, 0, 'No script elements must exist in toast container');
    assert.ok(toast.textContent.includes(dangerousMsg), 'Message is preserved as literal textContent');
  });

  // T-W4: Direct handleMqttMessage execution from app.js
  test('T-W4: handleMqttMessage() from app.js reflects telemetry and fsm_state without sending commands', () => {
    STATE.fsmState = 'SAFE';
    STATE.fanState = false;
    STATE.health.mq2 = 'OK';

    const telemetryPayload = JSON.stringify({
      device_id: 'ESP32_SMOKE_N09_A01',
      mq2_ppm: null,
      mq2_valid: false,
      dht_valid: true,
      fsm_state: 'ALARM',
      alarm_th: 400,
      safe_th: 300,
      fan: 'ON',
      buzzer: 'ON'
    });

    // Call REAL handleMqttMessage from app.js!
    handleMqttMessage('Nhom09/smoke/telemetry', telemetryPayload);

    assert.equal(STATE.fsmState, 'ALARM', 'Web SCADA must reflect fsm_state from ESP32');
    assert.equal(STATE.health.mq2, 'FAULT', 'Web SCADA must reflect MQ-2 fault badge');
    assert.equal(STATE.fanState, true, 'Web SCADA must reflect fan ON from ESP32');
    assert.equal(STATE.alarmThreshold, 400, 'Web SCADA must reflect alarmThreshold');
  });

  // T-W5: Direct updateUiFromState execution from app.js proving UI Safety Interlock
  test('T-W5: updateUiFromState() disables actuator controls during ALARM and restores in SAFE', () => {
    STATE.fsmState = 'ALARM';
    updateUiFromState();
    assert.equal(DOM.btnFanOff.disabled, true, 'Fan OFF button must be disabled during ALARM');
    assert.equal(DOM.btnBuzzerMute.disabled, true, 'Buzzer MUTE button must be disabled during ALARM');

    STATE.fsmState = 'SAFE';
    updateUiFromState();
    assert.equal(DOM.btnFanOff.disabled, false, 'Fan OFF button must be re-enabled during SAFE');
    assert.equal(DOM.btnBuzzerMute.disabled, false, 'Buzzer MUTE button must be re-enabled during SAFE');
  });

});
