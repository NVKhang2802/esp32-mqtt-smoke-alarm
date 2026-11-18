// functions/core_engine.js  (4 output: lenh, log, fleet, thong bao)
const NOW = Date.now();
const FLOOR = 'F03', CROSS_PPM = 600, CROSS_RATE_MS = 60000, WATCHDOG_MS = 30000, ALERT_RATE_MS = 20000;
const fleet = flow.get('fleet') || {};
const cmds = [], logs = [];
let alert = null;

const dev = id => {
  let d = fleet[id];
  if (!d) {
    d = fleet[id] = {
      deviceId: id,
      status: 'UNKNOWN',
      deviceState: 'SAFE',
      effective: 'SAFE',
      lastSeen: 0,
      ppm: NaN,
      temp: NaN,
      rate: 0,
      lastPpm: 0,
      hum: 60.0,
      tempHist: [],
      alarmTh: 400,
      safeTh: 300,
      overActive: false,
      hotActive: false,
      cooldownStart: null,
      lastAlert: 0,
      topology: null,
      mq2Valid: true,
      dhtValid: true
    };
  }
  if (d.rate === undefined) d.rate = 0;
  if (!Array.isArray(d.tempHist)) d.tempHist = [];
  return d;
};

const log = (level, event, desc, id) => logs.push({ level, event, desc, deviceId: id, ts: NOW });

const topicOf = (d, kind) => (d.topology && d.topology.building && d.topology.floor && d.topology.room)
  ? `Nhom09/smoke/v2/${d.topology.building}/${d.topology.floor}/${d.topology.room}/${d.deviceId}/cmd/${kind}`
  : `Nhom09/smoke/cmd/${kind}`;

const cmd = (d, kind, payload) => ({ topic: topicOf(d, kind), payload });

const notify = (d, text) => {
  if (NOW - d.lastAlert > ALERT_RATE_MS) {
    d.lastAlert = NOW;
    alert = { deviceId: d.deviceId, text };
  }
};

switch (msg.eventType) {
  case 'TELEMETRY': {
    const d = dev(msg.deviceId);
    d.lastSeen = NOW;
    d.status = 'ONLINE';
    d.deviceState = msg.fsmState || d.deviceState;
    if (Number.isFinite(msg.hum)) d.hum = msg.hum;
    d.alarmTh = msg.alarmTh || d.alarmTh;
    d.safeTh = msg.safeTh || d.safeTh;
    d.mq2Valid = msg.mq2Valid;
    d.dhtValid = msg.dhtValid;
    d.cooldownStart = d.deviceState === 'COOLDOWN' ? (d.cooldownStart || NOW) : null;

    // Rule 1: dT/dt theo cua so; mau cu nhat co tuoi >= 20 s trong 60 s; giu rate giua cac lan tinh
    if (d.dhtValid && Number.isFinite(msg.temp)) {
      d.temp = msg.temp;
      d.tempHist.push({ t: NOW, v: msg.temp });
      d.tempHist = d.tempHist.filter(s => NOW - s.t <= 60000);
      const ref = d.tempHist.find(s => NOW - s.t >= 20000);
      if (ref) d.rate = (msg.temp - ref.v) / ((NOW - ref.t) / 60000);
    } else {
      d.rate = 0;
    }

    d.effective = d.deviceState;
    if (!d.mq2Valid || !Number.isFinite(msg.ppm)) {
      if (d.deviceState !== 'ALARM') d.effective = 'FAULT'; // khong dung PPM cua cam bien hong
    } else {
      d.ppm = msg.ppm;
      const over = msg.ppm >= d.alarmTh;
      const hot = d.rate >= 3.0 || msg.temp >= 50.0;
      if (over) {
        d.effective = 'ALARM'; // chi leo thang
        if (!d.overActive) { // canh vuot nguong
          d.overActive = true;
          cmds.push(cmd(d, 'fan', { action: 'ON', reason: hot ? 'RULE_1_REAL_FIRE' : 'RULE_2_LOW_HEAT_SMOKE', priority: 'CRITICAL' }));
          log(hot ? 'CRITICAL' : 'WARN', hot ? 'REAL_FIRE_CONFIRMED' : 'SMOKE_LOW_HEAT_ALARM',
              `PPM=${msg.ppm} dT/dt=${d.rate.toFixed(1)} T=${msg.temp}`, d.deviceId);
          notify(d, `Khoi ${msg.ppm} PPM, nhiet ${msg.temp} C, dT/dt ${d.rate.toFixed(1)}`);
        }
        if (hot && !d.hotActive) {
          d.hotActive = true;
          cmds.push(cmd(d, 'buzzer', { action: 'UNMUTE', reason: 'RULE_1_REAL_FIRE', priority: 'CRITICAL' }));
        }
      } else if (msg.ppm <= d.safeTh) {
        d.overActive = false;
        d.hotActive = false;
      }

      // Rule 5: canh vuot 600 PPM, gioi han 60 s, chi gui toi thiet bi cung tang co topic hop le
      if (msg.ppm >= CROSS_PPM && d.lastPpm < CROSS_PPM && NOW - (flow.get('last_cross_zone') || 0) > CROSS_RATE_MS) {
        flow.set('last_cross_zone', NOW);
        log('CRITICAL', 'CROSS_ZONE_BROADCAST', `PPM=${msg.ppm} tai ${d.deviceId}: so tan tang ${FLOOR}`, d.deviceId);
        Object.values(fleet)
          .filter(x => x.deviceId !== d.deviceId && x.topology && x.topology.floor === FLOOR && x.topology.building && x.topology.room)
          .forEach(x => cmds.push(cmd(x, 'buzzer', { cmd_id: 'CMD-ZONE-EVACUATION', action: 'UNMUTE', priority: 'CRITICAL' })));
      }
      d.lastPpm = msg.ppm;
    }
    break;
  }
  case 'KEEP_ALIVE': {
    const d = dev(msg.deviceId);
    d.lastSeen = NOW;
    if (d.status !== 'ONLINE') d.status = 'ONLINE';
    break;
  }
  case 'LWT': {
    const d = dev(msg.deviceId);
    if (!msg.isOnline) {
      d.status = 'OFFLINE';
      d.effective = 'OFFLINE';
      log('CRITICAL', 'LWT_DISCONNECT', 'Broker bao thiet bi mat ket noi', d.deviceId);
      notify(d, 'Thiet bi mat ket noi (LWT)');
    } else {
      d.status = 'ONLINE';
      d.lastSeen = NOW;
      log('INFO', 'LWT_CONNECT', 'Thiet bi ket noi lai', d.deviceId);
    }
    break;
  }
  case 'WATCHDOG_TICK':
    Object.values(fleet).forEach(d => {
      if (d.status === 'ONLINE' && d.lastSeen && NOW - d.lastSeen > WATCHDOG_MS) {
        d.status = 'OFFLINE';
        d.effective = 'OFFLINE';
        log('CRITICAL', 'WATCHDOG_TIMEOUT', 'Qua 30 s khong co du lieu', d.deviceId);
        notify(d, 'Thiet bi im lang qua 30 s');
      }
    });
    break;
  case 'ALARM_EVENT': {
    const d = dev(msg.deviceId);
    log('CRITICAL', msg.eventName || 'ALARM_EVENT', 'Su kien tu thiet bi', d.deviceId);
    break;
  }
  case 'OFFLINE_SYNC': {
    const d = dev(msg.deviceId);
    const count = Array.isArray(msg.records) ? msg.records.length : 1;
    log('INFO', 'OFFLINE_SYNC_RECEIVED', `Dong bo ${count} ban ghi lich su tu thiet bi`, d.deviceId);
    break;
  }
  case 'SCHEDULER_CMD': {
    const mode = msg.mode || (msg.payload && msg.payload.mode) || 'DAY';
    const alarmVal = mode === 'NIGHT' ? 350 : 400;
    const safeVal = alarmVal * 0.75;
    Object.values(fleet).forEach(d => {
      d.alarmTh = alarmVal;
      d.safeTh = safeVal;
    });
    log('INFO', 'SCHEDULER_APPLIED', `Lich ${mode}: alarm=${alarmVal}, safe=${safeVal}`, 'ALL');
    break;
  }
  case 'FAULT_INJECTION_CMD':
    log('INFO', 'FAULT_INJECTION_SEEN', 'Chi ghi nhan; trang thai lay tu telemetry thiet bi', msg.deviceId || 'ESP32_SMOKE_N04_A01');
    break;
}

flow.set('fleet', fleet);
if (logs.length) flow.set('history', logs.concat(flow.get('history') || []).slice(0, 80));

const primary = fleet['ESP32_SMOKE_N04_A01'] || Object.values(fleet)[0] || {};

return [
  cmds.length ? cmds.map(c => ({ topic: c.topic, payload: JSON.stringify(c.payload), qos: 1 })) : null,
  logs.length ? { payload: logs } : null,
  {
    payload: {
      fleet: Object.values(fleet),
      fleetList: Object.values(fleet),
      ppm: primary.ppm,
      temp: primary.temp,
      hum: (primary.hum !== undefined && Number.isFinite(primary.hum)) ? primary.hum : 60.0,
      fsmState: primary.effective,
      state: primary.effective,
      alarmThreshold: primary.alarmTh,
      safeThreshold: primary.safeTh
    }
  },
  alert ? { payload: alert } : null
];
