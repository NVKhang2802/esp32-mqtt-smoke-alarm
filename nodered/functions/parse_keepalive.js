// nodered/functions/parse_keepalive.js
let d = msg.payload;
if (typeof d === 'string') {
  try {
    d = JSON.parse(d);
  } catch (e) {
    return null;
  }
}
if (!d || typeof d !== 'object') return null;

msg.eventType = 'KEEP_ALIVE';
msg.deviceId  = d.device_id || 'ESP32_SMOKE_N04_A01';
msg.uptime    = d.uptime_s !== undefined ? d.uptime_s : d.uptime_sec;
msg.freeHeap  = Number(d.free_heap_bytes || 0);
msg.wifiRssi  = Number(d.wifi_rssi_dbm || -60);
msg.status    = d.status || 'HEALTHY';
msg.fsmState  = d.fsm_state;

// Dedup cache TTL 5s
if (msg.uptime !== undefined) {
  const now = Date.now(), cache = flow.get('dedup') || {};
  for (const k in cache) {
    if (now - cache[k] > 5000) delete cache[k];
  }
  const key = msg.deviceId + '|' + msg.eventType + '|' + msg.uptime;
  if (cache[key]) return null;
  cache[key] = now;
  flow.set('dedup', cache);
}

return msg;
