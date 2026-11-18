// nodered/functions/parse_alarm.js
let d = msg.payload;
if (typeof d === 'string') {
  try {
    d = JSON.parse(d);
  } catch (e) {
    return null;
  }
}
if (!d || typeof d !== 'object') return null;

msg.eventType = 'ALARM_EVENT';
msg.deviceId  = d.device_id || 'ESP32_SMOKE_N04_A01';
msg.eventName = d.event || 'SMOKE_ALERT';
msg.severity  = d.severity || 'CRITICAL';
msg.ppm       = Number(d.ppm !== undefined ? d.ppm : (d.mq2_ppm || 0));
msg.threshold = Number(d.threshold || 400);
msg.uptime    = d.uptime_s !== undefined ? d.uptime_s : d.uptime_sec;

// Dedup cache TTL 5s
if (msg.uptime !== undefined) {
  const now = Date.now(), cache = flow.get('dedup') || {};
  for (const k in cache) {
    if (now - cache[k] > 5000) delete cache[k];
  }
  const key = msg.deviceId + '|' + msg.eventType + '|' + (msg.eventName || '') + '|' + msg.uptime;
  if (cache[key]) return null;
  cache[key] = now;
  flow.set('dedup', cache);
}

return msg;
