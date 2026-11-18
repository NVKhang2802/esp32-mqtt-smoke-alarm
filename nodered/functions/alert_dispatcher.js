// functions/alert_dispatcher.js (output 1 -> http request, output 2 -> dashboard + debug)
const token = env.get('TELEGRAM_TOKEN');
const chat = env.get('TELEGRAM_CHAT_ID');
const text = '[' + msg.payload.deviceId + '] ' + msg.payload.text;

if (!token || !chat) {
  return [null, { payload: text }];
}

return [
  {
    method: 'POST',
    url: 'https://api.telegram.org/bot' + token + '/sendMessage',
    headers: { 'content-type': 'application/json' },
    payload: JSON.stringify({ chat_id: chat, text: text })
  },
  { payload: text }
];
