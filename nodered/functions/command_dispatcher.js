// functions/command_dispatcher.js
if (typeof msg.topic !== 'string' || /[+#]/.test(msg.topic)) {
  node.warn('Bo qua topic khong hop le: ' + msg.topic);
  return null;
}
return msg;
