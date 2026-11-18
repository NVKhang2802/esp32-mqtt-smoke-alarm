// functions/parse_telemetry.js
let d = msg.payload;
if (typeof d === 'string') {
  try {
    d = JSON.parse(d);
  } catch (e) {
    return null;
  }
}
if (!d || typeof d !== 'object') return null;

const num = v => (v === null || v === undefined) ? NaN : Number(v);

msg.eventType = 'TELEMETRY';
msg.deviceId  = d.device_id || 'ESP32_SMOKE_N04_A01';
msg.uptime    = d.uptime_s !== undefined ? d.uptime_s : d.uptime_sec;
msg.mq2Valid  = d.mq2_valid !== false;
msg.dhtValid  = d.dht_valid !== false;
msg.ppm       = num(d.mq2_ppm);
msg.temp      = num(d.temp);
msg.hum       = num(d.hum);
msg.fsmState  = d.fsm_state;
msg.alarmTh   = Number(d.alarm_th) || undefined;
msg.safeTh    = Number(d.safe_th) || undefined;

// ---- DEDUP: TTL 5s ----
if (msg.uptime !== undefined) {
  const now = Date.now();
  const cache = flow.get('dedup') || {};
  for (const k in cache) {
    if (now - cache[k] > 5000) delete cache[k];
  }
  const key = msg.deviceId + '|' + msg.eventType + '|' + (msg.eventName || '') + '|' + msg.uptime;
  if (cache[key]) return null;
  cache[key] = now;
  flow.set('dedup', cache);
}

return msg;
