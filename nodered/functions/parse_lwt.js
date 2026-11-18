// functions/parse_lwt.js
let s = msg.payload;
let id = null;
let online = false;

try {
  const j = typeof s === 'string' ? JSON.parse(s) : s;
  if (j && typeof j === 'object') {
    id = j.device_id;
    online = String(j.status).toLowerCase() === 'online';
  } else {
    online = String(s).trim().toLowerCase() === 'online';
  }
} catch (e) {
  online = String(s).trim().toLowerCase() === 'online';
}

msg.eventType = 'LWT';
msg.deviceId  = id || 'ESP32_SMOKE_N04_A01';
msg.isOnline  = online;

return msg;
