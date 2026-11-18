// functions/scheduler_tick.js
const h = new Date().getHours();
const night = h >= 22 || h < 6;

if (flow.get('sched') === night) return null;

flow.set('sched', night);
return {
  topic: 'Nhom09/smoke/cmd/scheduler',
  payload: JSON.stringify({ mode: night ? 'NIGHT' : 'DAY', source: 'RULE_3_SCHEDULER' })
};
