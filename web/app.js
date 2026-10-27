/**
 * @file app.js
 * @brief SMART FIRE SAFETY PLATFORM - TẦNG 4 APPLICATION JAVASCRIPT
 * @details Kiến trúc Lean & Clean Code:
 *          - Cached DOM Registry qua Proxy (Zero repeated getElementById)
 *          - Unified Downlink Command Dispatcher
 *          - Reactive State Pattern & Guard Clauses
 *          - Fault Injection Sandbox & Hardware Diagnostics Binding
 */

// =============================================================================
// 1. CONFIGURATION & RUNTIME STATE
// =============================================================================
const CONFIG = {
  brokerWss: "wss://broker.emqx.io:8084/mqtt",
  brokerWsBackup: "ws://broker.emqx.io:8083/mqtt",
  topics: {
    telemetry: "Nhom09/smoke/telemetry",
    eventAlarm: "Nhom09/smoke/event/alarm",
    statusAck: "Nhom09/smoke/status",
    lwt: "Nhom09/smoke/lwt",
    cmdFan: "Nhom09/smoke/cmd/fan",
    cmdBuzzer: "Nhom09/smoke/cmd/buzzer",
    cmdMode: "Nhom09/smoke/cmd/mode",
    cmdNight: "Nhom09/smoke/cmd/sensitivity",
    cmdInjectFault: "Nhom09/smoke/cmd/inject_fault",
    cmdScheduler: "Nhom09/smoke/cmd/scheduler",
    historySync: "Nhom09/smoke/history/sync"
  },
  thresholds: {
    alarmDay: 400.0,
    alarmNight: 350.0,
    safeDay: 300.0,
    safeNight: 250.0,
    overheat: 55.0
  }
};

const STATE = {
  // Sensor Telemetry
  ppm: 145.2,
  temp: 28.4,
  hum: 62.8,

  // FSM State: SAFE | WARNING | ALARM | COOLDOWN | FAULT | OFFLINE
  fsmState: "SAFE",
  cooldownTimer: 0,

  // Actuators
  fanState: false,
  fanMode: "AUTO", // AUTO | MANUAL
  buzzerActive: false,
  isMuted: false,
  muteRemainingSec: 0,

  // Sensitivity Mode & Scheduler
  sensitivityMode: "DAY", // DAY | NIGHT
  alarmThreshold: 400.0,

  // System Diagnostics & Health
  isConnected: false,
  deviceOnline: true,
  lastSeenTime: Date.now(),
  userRole: "operator", // admin | operator | viewer
  health: {
    mq2: "OK",
    dht: "OK",
    watchdog: "OK",
    actuator: "OK"
  },

  // Telemetry History for Charts (Max 25 points)
  history: {
    labels: [],
    ppmData: [],
    tempData: []
  },

  // Audit Trail Logs
  logs: []
};

// =============================================================================
// 2. DOM ELEMENT REGISTRY PROXY (O(1) CACHED LOOKUP)
// =============================================================================
const DOM = new Proxy({}, {
  get(target, id) {
    if (!target[id]) {
      target[id] = document.getElementById(id);
    }
    return target[id];
  }
});

let mqttClient = null;
let telemetryChart = null;
let cooldownInterval = null;
let muteInterval = null;
let webAudioCtx = null;

// =============================================================================
// 3. INITIALIZATION & LIFECYCLE
// =============================================================================
document.addEventListener("DOMContentLoaded", () => {
  initClock();
  initChart();
  initMqttClient();
  initEventHandlers();
  initFaultInjectionHandlers();
  initSimulatorDefaults();

  addAuditLog("SYSTEM", "APPLICATION_STARTED", "Khởi động giao diện Tầng 4 Application thành công.", "SAFE");
  updateUiFromState();

  // Watchdog heartbeat checker
  setInterval(heartbeatCheck, 2000);
});

// =============================================================================
// 4. UNIFIED DOWNLINK DISPATCHER
// =============================================================================
function sendDownlinkCommand(topicKey, payload) {
  const topic = CONFIG.topics[topicKey] || topicKey;
  const payloadStr = JSON.stringify(payload);

  if (mqttClient && STATE.isConnected) {
    mqttClient.publish(topic, payloadStr, { qos: 1 });
    console.log(`[MQTT Downlink] ${topic} (QoS 1) -> ${payloadStr}`);
  } else {
    console.log(`[Sim Downlink] ${topic} -> ${payloadStr}`);
    showToast(`Mô phỏng gửi lệnh: ${topic.split('/').pop()}`, "info");
  }
}

// =============================================================================
// 5. MQTT WEBSOCKET CLIENT INTEGRATION
// =============================================================================
function initMqttClient() {
  const clientId = "WebClient_Smoke_N04_" + Math.random().toString(16).substring(2, 8);
  const connBadge = DOM.brokerConnBadge;
  const connText  = DOM.connStatusText;

  if (connText) connText.textContent = "Đang kết nối...";

  try {
    mqttClient = mqtt.connect(CONFIG.brokerWss, {
      clientId: clientId,
      clean: true,
      connectTimeout: 5000,
      reconnectPeriod: 4000
    });

    mqttClient.on("connect", () => {
      STATE.isConnected = true;
      if (connBadge) connBadge.className = "connection-pill connected";
      if (connText) connText.textContent = "EMQX Online";
      showToast("Đã kết nối máy chủ MQTT EMQX (WSS)", "success");

      mqttClient.subscribe(CONFIG.topics.telemetry, { qos: 0 });
      mqttClient.subscribe(CONFIG.topics.eventAlarm, { qos: 1 });
      mqttClient.subscribe(CONFIG.topics.statusAck, { qos: 1 });
      mqttClient.subscribe(CONFIG.topics.lwt, { qos: 1 });

      addAuditLog("INFO", "MQTT_CONNECTED", `Kết nối WebSocket tới ${CONFIG.brokerWss} thành công.`, STATE.fsmState);
    });

    mqttClient.on("message", (topic, message) => {
      handleIncomingMqtt(topic, message.toString());
    });

    mqttClient.on("error", (err) => {
      console.warn("MQTT WSS Error, falling back to simulator:", err);
      STATE.isConnected = false;
      if (connBadge) connBadge.className = "connection-pill disconnected";
      if (connText) connText.textContent = "Chế độ Mô phỏng";
    });

    mqttClient.on("close", () => {
      STATE.isConnected = false;
      if (connBadge) connBadge.className = "connection-pill disconnected";
      if (connText) connText.textContent = "Mất kết nối";
    });
  } catch (e) {
    console.warn("MQTT Connect exception, operating in demo simulation:", e);
    if (connBadge) connBadge.className = "connection-pill disconnected";
    if (connText) connText.textContent = "Sim Mode";
  }
}

function handleIncomingMqtt(topic, payloadStr) {
  STATE.lastSeenTime = Date.now();
  STATE.health.watchdog = "OK";

  try {
    const data = JSON.parse(payloadStr);

    if (topic === CONFIG.topics.telemetry) {
      if (data.mq2_ppm !== undefined) STATE.ppm = parseFloat(data.mq2_ppm);
      else if (data.smoke_ppm !== undefined) STATE.ppm = parseFloat(data.smoke_ppm);

      if (data.temp !== undefined) STATE.temp = parseFloat(data.temp);
      else if (data.temperature !== undefined) STATE.temp = parseFloat(data.temperature);

      if (data.hum !== undefined) STATE.hum = parseFloat(data.hum);
      else if (data.humidity !== undefined) STATE.hum = parseFloat(data.humidity);

      if (data.fan !== undefined) STATE.fanState = (data.fan === "ON" || data.fan === true);
      if (data.buzzer !== undefined) STATE.buzzerActive = (data.buzzer === "ON" || data.buzzer === true);
      if (data.fsm_state) STATE.fsmState = data.fsm_state;

      evaluateFsmRules();
      updateUiFromState();
      pushChartData(STATE.ppm, STATE.temp);
    }
    else if (topic === CONFIG.topics.eventAlarm) {
      triggerAlarmState(data.ppm || STATE.ppm, data.event || "URGENT_ALARM");
    }
    else if (topic === CONFIG.topics.statusAck) {
      addAuditLog("INFO", "DEVICE_ACK", `Phản hồi từ ESP32: Lệnh ${data.cmd || ''} -> ${data.result || 'OK'}`, STATE.fsmState);
      showToast(`ESP32: ${data.cmd || 'Lệnh'} -> ${data.result || 'Thành công'}`, "success");

      if (data.cmd === "fault_alert") {
        if (data.detail && data.detail.includes("MQ2")) STATE.health.mq2 = "FAULT";
        if (data.detail && data.detail.includes("DHT")) STATE.health.dht = "FAULT";
      } else if (data.cmd === "fault_clear" || data.cmd === "fault_recovery") {
        STATE.health.mq2 = "OK";
        STATE.health.dht = "OK";
        STATE.health.actuator = "OK";
      }
      updateUiFromState();
    }
    else if (topic === CONFIG.topics.lwt) {
      if (data.status === "offline") {
        setOfflineState();
      } else {
        STATE.deviceOnline = true;
      }
    }
  } catch (err) {
    console.debug("Non-JSON or raw payload received:", payloadStr);
  }
}

// =============================================================================
// 6. FINITE STATE MACHINE (FSM) & BUSINESS RULES EVALUATION
// =============================================================================
function evaluateFsmRules() {
  if (!STATE.deviceOnline) return;

  const currentThresh = (STATE.sensitivityMode === "NIGHT")
    ? CONFIG.thresholds.alarmNight
    : CONFIG.thresholds.alarmDay;

  const safeThresh = (STATE.sensitivityMode === "NIGHT")
    ? CONFIG.thresholds.safeNight
    : CONFIG.thresholds.safeDay;

  // RULE 1: Smoke Hazard (>= 400 PPM or 350 PPM)
  if (STATE.ppm >= currentThresh) {
    if (STATE.fsmState !== "ALARM") {
      triggerAlarmState(STATE.ppm, "SMOKE_HAZARD_DETECTED");
    }
    return;
  }

  // RULE 3: Cooldown Logic (< 300 PPM when in ALARM)
  if (STATE.fsmState === "ALARM" && STATE.ppm < safeThresh) {
    triggerCooldownState();
    return;
  }

  // In Cooldown: Re-escalation Guard (if smoke rises back >= safeThresh)
  if (STATE.fsmState === "COOLDOWN") {
    if (STATE.ppm >= safeThresh) {
      if (cooldownInterval) clearInterval(cooldownInterval);
      triggerAlarmState(STATE.ppm, "COOLDOWN_ABORTED_SMOKE_REBOUND");
    }
    return;
  }

  // RULE 2: Overheat Hazard (Temp >= 55.0°C)
  if (STATE.temp >= CONFIG.thresholds.overheat) {
    if (STATE.fsmState === "SAFE") {
      STATE.fsmState = "WARNING";
      addAuditLog("WARN", "OVERHEAT_DETECTED", `Nhiệt độ môi trường cực cao (${STATE.temp.toFixed(1)}°C >= 55.0°C)`, "WARNING");
      showToast("Cảnh báo: Phát hiện quá nhiệt môi trường!", "warning");
    }
    return;
  }

  // Normal Safe Return
  if (STATE.fsmState === "WARNING" && STATE.ppm < (currentThresh - 100) && STATE.temp < 50.0) {
    STATE.fsmState = "SAFE";
    addAuditLog("INFO", "RETURN_TO_SAFE", "Nhiệt độ và khói đã ổn định trở lại vùng an toàn.", "SAFE");
  }
}

function triggerAlarmState(ppmVal, reason) {
  STATE.fsmState = "ALARM";
  STATE.fanState = true;
  STATE.buzzerActive = true;

  playAlarmAudioBeep();

  addAuditLog("CRITICAL", "SMOKE_ALARM_TRIGGERED", `Khói vượt ngưỡng (${ppmVal.toFixed(1)} PPM >= ${STATE.alarmThreshold} PPM). Quạt BẬT, Còi HÚ!`, "ALARM");
  showToast("BÁO ĐỘNG KHẨN CẤP: Nồng độ khói vượt ngưỡng an toàn!", "danger");

  dispatchTelegramAlert(
    `🚨 <b>BÁO ĐỘNG HỎA HOẠN KHẨN CẤP!</b>\n` +
    `📍 <b>Vị trí:</b> Phòng P302 - Khoa CNTT HUIT\n` +
    `💨 <b>Nồng độ khói MQ-2:</b> <code>${ppmVal.toFixed(1)} PPM</code>\n` +
    `🌡️ <b>Nhiệt độ DHT22:</b> <code>${STATE.temp.toFixed(1)} °C</code>\n` +
    `🌀 <b>Quạt hút DC:</b> ĐÃ TỰ ĐỘNG BẬT CƯỠNG BỨC\n` +
    `🔔 <b>Còi báo động:</b> ĐANG PHÁT TÍN HIỆU HÚ KHẨN`
  );
}

function triggerCooldownState() {
  STATE.fsmState = "COOLDOWN";
  STATE.cooldownTimer = 30; // 30s Post-alarm purge delay
  STATE.fanState = true;    // Fan stays active during cooldown
  STATE.buzzerActive = false;

  addAuditLog("INFO", "COOLDOWN_STARTED", `Khói hạ dưới ${CONFIG.thresholds.safeDay} PPM. Kích hoạt đếm lùi 30s xả khói tồn dư.`, "COOLDOWN");
  showToast("Bắt đầu quá trình 30s làm mát & thông gió cưỡng bức (Cooldown Purge)", "warning");

  if (cooldownInterval) clearInterval(cooldownInterval);

  cooldownInterval = setInterval(() => {
    STATE.cooldownTimer--;
    updateUiFromState();

    if (STATE.cooldownTimer <= 0) {
      clearInterval(cooldownInterval);
      STATE.fsmState = "SAFE";
      if (STATE.fanMode === "AUTO") {
        STATE.fanState = false;
        sendDownlinkCommand("cmdFan", { action: "OFF", reason: "COOLDOWN_FINISHED" });
      }
      addAuditLog("INFO", "COOLDOWN_COMPLETED", "Hoàn tất 30s xả khói tồn dư. Quạt tự động trở về SAFE IDLE.", "SAFE");
      showToast("Quá trình xả khói hoàn tất. Hệ thống trở về trạng thái An toàn.", "success");
      updateUiFromState();
    }
  }, 1000);
}

function setOfflineState() {
  STATE.deviceOnline = false;
  STATE.fsmState = "OFFLINE";
  STATE.health.watchdog = "TIMEOUT";
  addAuditLog("CRITICAL", "HEARTBEAT_TIMEOUT", "Mất kết nối với thiết bị ESP32 (Watchdog > 15s không có Keep-Alive)", "OFFLINE");
  showToast("Cảnh báo: Trạm cảm biến ESP32 mất kết nối!", "danger");
  updateUiFromState();
}

function heartbeatCheck() {
  const now = Date.now();
  if (STATE.deviceOnline && (now - STATE.lastSeenTime > 15000)) {
    setOfflineState();
  }
}

// =============================================================================
// 7. ROLE-BASED ACCESS CONTROL (RBAC)
// =============================================================================
function checkRolePermission(requiredRole, actionDescription) {
  const currentRole = STATE.userRole;

  if (requiredRole === "admin" && currentRole !== "admin") {
    showToast(`Từ chối quyền: Cần tài khoản [Quản trị viên] để ${actionDescription}.`, "danger");
    return false;
  }
  if (requiredRole === "operator" && currentRole === "viewer") {
    showToast(`Từ chối quyền: Người dân (Viewer) chỉ có quyền giám sát, không được ${actionDescription}.`, "danger");
    return false;
  }
  return true;
}

// =============================================================================
// 8. UI UPDATE & RENDERING ENGINE (USING CACHED DOM REGISTRY)
// =============================================================================
function updateUiFromState() {
  // 1. KPI Numbers & Visual Progress Bars
  if (DOM.valSmokePpm) DOM.valSmokePpm.textContent = STATE.ppm.toFixed(1);
  if (DOM.valTemp) DOM.valTemp.textContent = STATE.temp.toFixed(1);
  if (DOM.valHum) DOM.valHum.textContent = STATE.hum.toFixed(1);

  const smokePercent = Math.min(100, (STATE.ppm / 800) * 100);
  if (DOM.barSmoke) DOM.barSmoke.style.width = smokePercent + "%";

  const tempPercent = Math.min(100, (STATE.temp / 80) * 100);
  if (DOM.barTemp) DOM.barTemp.style.width = tempPercent + "%";

  const humPercent = Math.min(100, STATE.hum);
  if (DOM.barHum) DOM.barHum.style.width = humPercent + "%";

  // Smoke KPI Styling
  if (DOM.kpiSmoke && DOM.tagSmoke) {
    DOM.kpiSmoke.className = "kpi-card glass-panel";
    if (STATE.ppm >= STATE.alarmThreshold) {
      DOM.kpiSmoke.classList.add("kpi-alarm");
      DOM.tagSmoke.className = "kpi-tag danger";
      DOM.tagSmoke.textContent = "Báo động Đỏ";
    } else if (STATE.ppm >= 250) {
      DOM.kpiSmoke.classList.add("kpi-warn");
      DOM.tagSmoke.className = "kpi-tag warn";
      DOM.tagSmoke.textContent = "Cảnh giác Vàng";
    } else {
      DOM.tagSmoke.className = "kpi-tag normal";
      DOM.tagSmoke.textContent = "Bình thường";
    }
  }

  // 2. FSM Header Chip & Alarm Banner
  if (DOM.fsmChip && DOM.alarmBanner) {
    DOM.fsmChip.className = "fsm-status-chip";
    DOM.alarmBanner.className = "alarm-banner";

    switch (STATE.fsmState) {
      case "FAULT":
        DOM.fsmChip.classList.add("state-fault");
        if (DOM.fsmStatusText) DOM.fsmStatusText.textContent = "SỰ CỐ PHẦN CỨNG (FAULT)";
        DOM.alarmBanner.classList.add("active", "banner-alarm");
        if (DOM.bannerTitle) DOM.bannerTitle.textContent = "SỰ CỐ BẤT THƯỜNG: HỎNG CẢM BIẾN / LỖI CHẤP HÀNH";
        if (DOM.bannerDesc) DOM.bannerDesc.textContent = "Hệ thống tự động kích hoạt Fail-Safe Mode: duy trì quạt thông gió an toàn, ngắt còi hú tránh hoảng loạn.";
        break;

      case "SAFE":
        DOM.fsmChip.classList.add("state-safe");
        if (DOM.fsmStatusText) DOM.fsmStatusText.textContent = "AN TOÀN (SAFE)";
        DOM.alarmBanner.classList.remove("active");
        break;

      case "WARNING":
        DOM.fsmChip.classList.add("state-warning");
        if (DOM.fsmStatusText) DOM.fsmStatusText.textContent = "CẢNH GIÁC (WARNING)";
        DOM.alarmBanner.classList.add("active", "banner-warning");
        if (DOM.bannerTitle) DOM.bannerTitle.textContent = "CẢNH BÁO MỨC ĐỘ VÀNG: KHÓI TĂNG NHẸ";
        if (DOM.bannerDesc) DOM.bannerDesc.textContent = `Nồng độ khói hiện tại ${STATE.ppm.toFixed(1)} PPM. Đang theo dõi chặt chẽ.`;
        break;

      case "ALARM":
        DOM.fsmChip.classList.add("state-alarm");
        if (DOM.fsmStatusText) DOM.fsmStatusText.textContent = "BÁO ĐỘNG ĐỎ (ALARM)";
        DOM.alarmBanner.classList.add("active", "banner-alarm");
        if (DOM.bannerTitle) DOM.bannerTitle.textContent = "BÁO ĐỘNG HỎA HOẠN: KHÓI VƯỢT NGƯỠNG NGUY CẤP!";
        if (DOM.bannerDesc) DOM.bannerDesc.textContent = `Nồng độ khói ${STATE.ppm.toFixed(1)} PPM >= ${STATE.alarmThreshold} PPM. Quạt hút đang chạy tối đa, còi hú cảnh báo.`;
        break;

      case "COOLDOWN":
        DOM.fsmChip.classList.add("state-cooldown");
        if (DOM.fsmStatusText) DOM.fsmStatusText.textContent = `LÀM MÁT (${STATE.cooldownTimer}s)`;
        DOM.alarmBanner.classList.add("active", "banner-cooldown");
        if (DOM.bannerTitle) DOM.bannerTitle.textContent = `ĐANG LÀM MÁT & XẢ KHÓI TỒN DƯ: CÒN ${STATE.cooldownTimer} GIÂY`;
        if (DOM.bannerDesc) DOM.bannerDesc.textContent = "Khói đã giảm. Duy trì quạt chạy thêm 30 giây chống hiện tượng rơ-le nhảy loạn.";
        break;

      case "OFFLINE":
        DOM.fsmChip.classList.add("state-offline");
        if (DOM.fsmStatusText) DOM.fsmStatusText.textContent = "MẤT KẾT NỐI (OFFLINE)";
        DOM.alarmBanner.classList.add("active", "banner-warning");
        if (DOM.bannerTitle) DOM.bannerTitle.textContent = "MẤT TÍN HIỆU CẢM BIẾN TỪ TRẠM ESP32";
        if (DOM.bannerDesc) DOM.bannerDesc.textContent = "Không nhận được gói tin nhịp tim Keep-Alive. Kiểm tra nguồn và mạng Wi-Fi của trạm P302.";
        break;
    }
  }

  // 3. Actuator Controls UI
  if (DOM.lblFanMode) DOM.lblFanMode.textContent = STATE.fanMode === "AUTO" ? "TỰ ĐỘNG (AUTO)" : "THỦ CÔNG (MANUAL)";

  if (DOM.badgeFanState && DOM.fanStatusIcon) {
    if (STATE.fanState) {
      DOM.badgeFanState.className = "act-state-badge on";
      DOM.badgeFanState.textContent = "ĐANG BẬT (ON)";
      DOM.fanStatusIcon.classList.add("fan-spinning");
      if (DOM.mapFanIcon) DOM.mapFanIcon.classList.add("fan-spinning");
    } else {
      DOM.badgeFanState.className = "act-state-badge off";
      DOM.badgeFanState.textContent = "ĐANG TẮT (OFF)";
      DOM.fanStatusIcon.classList.remove("fan-spinning");
      if (DOM.mapFanIcon) DOM.mapFanIcon.classList.remove("fan-spinning");
    }
  }

  if (DOM.badgeBuzzerState && DOM.lblBuzzerDesc) {
    if (STATE.isMuted) {
      DOM.badgeBuzzerState.className = "act-state-badge off";
      DOM.badgeBuzzerState.textContent = `TẮT TIẾNG (${STATE.muteRemainingSec}s)`;
      DOM.lblBuzzerDesc.textContent = `Đã tạm ngắt tiếng còi trong ${STATE.muteRemainingSec} giây.`;
    } else if (STATE.buzzerActive) {
      DOM.badgeBuzzerState.className = "act-state-badge alert";
      DOM.badgeBuzzerState.textContent = "ĐANG HÚ CÒI";
      DOM.lblBuzzerDesc.textContent = "Còi hú khẩn cấp đang phát âm thanh cảnh báo!";
    } else {
      DOM.badgeBuzzerState.className = "act-state-badge off";
      DOM.badgeBuzzerState.textContent = "IM LẶNG";
      DOM.lblBuzzerDesc.textContent = "Còi sẵn sàng tự động phản ứng khi khói >= ngưỡng.";
    }
  }

  // 4. Sensitivity Scheduler Toggle
  if (DOM.badgeNightState && DOM.lblThresholdDesc && DOM.kpiThreshold) {
    if (STATE.sensitivityMode === "NIGHT") {
      DOM.badgeNightState.className = "act-state-badge mode-night";
      DOM.badgeNightState.textContent = "CHẾ ĐỘ ĐÊM (350 PPM)";
      DOM.lblThresholdDesc.textContent = "350 PPM (Tăng độ nhạy ban đêm)";
      DOM.kpiThreshold.textContent = "350.0 PPM";
      STATE.alarmThreshold = CONFIG.thresholds.alarmNight;
      if (DOM.btnModeNight) DOM.btnModeNight.classList.add("active");
      if (DOM.btnModeDay) DOM.btnModeDay.classList.remove("active");
    } else {
      DOM.badgeNightState.className = "act-state-badge mode-day";
      DOM.badgeNightState.textContent = "CHẾ ĐỘ NGÀY (400 PPM)";
      DOM.lblThresholdDesc.textContent = "400 PPM (Tiêu chuẩn ban ngày)";
      DOM.kpiThreshold.textContent = "400.0 PPM";
      STATE.alarmThreshold = CONFIG.thresholds.alarmDay;
      if (DOM.btnModeDay) DOM.btnModeDay.classList.add("active");
      if (DOM.btnModeNight) DOM.btnModeNight.classList.remove("active");
    }
  }

  // 5. Floorplan Map Node
  if (DOM.mapNodeA01 && DOM.mapNodeBadge && DOM.zoneOverallStatus) {
    if (STATE.fsmState === "ALARM") {
      DOM.mapNodeA01.className = "sensor-node node-hazard";
      DOM.mapNodeBadge.textContent = "ALARM";
      DOM.mapNodeBadge.style.background = "#fef2f2";
      DOM.mapNodeBadge.style.color = "#dc2626";
      DOM.mapNodeBadge.style.borderColor = "#fecaca";
      DOM.zoneOverallStatus.innerHTML = '<span class="dot"></span> CẢNH BÁO CHÁY PHÒNG P302';
      DOM.zoneOverallStatus.style.background = "#fef2f2";
      DOM.zoneOverallStatus.style.color = "var(--scada-alarm)";
    } else if (STATE.fsmState === "COOLDOWN") {
      DOM.mapNodeA01.className = "sensor-node node-live";
      DOM.mapNodeBadge.textContent = "COOLDOWN";
      DOM.mapNodeBadge.style.background = "#f0f9ff";
      DOM.mapNodeBadge.style.color = "var(--scada-cooldown)";
      DOM.mapNodeBadge.style.borderColor = "#bae6fd";
      DOM.zoneOverallStatus.innerHTML = '<span class="dot"></span> Đang xả khói P302';
      DOM.zoneOverallStatus.style.background = "#f0f9ff";
      DOM.zoneOverallStatus.style.color = "var(--scada-cooldown)";
    } else {
      DOM.mapNodeA01.className = "sensor-node node-live";
      DOM.mapNodeBadge.textContent = "SAFE";
      DOM.mapNodeBadge.style.background = "#ecfdf5";
      DOM.mapNodeBadge.style.color = "var(--scada-safe)";
      DOM.mapNodeBadge.style.borderColor = "#a7f3d0";
      DOM.zoneOverallStatus.innerHTML = '<span class="dot"></span> Toàn sàn Bình thường';
      DOM.zoneOverallStatus.style.background = "#ecfdf5";
      DOM.zoneOverallStatus.style.color = "var(--scada-safe)";
    }
  }

  // 6. Diagnostic Health Matrix (Week 7)
  if (DOM.healthMq2Status) {
    DOM.healthMq2Status.className = STATE.health.mq2 === "OK" ? "health-val ok" : "health-val fault";
    DOM.healthMq2Status.textContent = STATE.health.mq2 === "OK" ? "● ADC BÌNH THƯỜNG" : "● ĐỨT DÂY / OUT-OF-RANGE";
  }
  if (DOM.healthDhtStatus) {
    DOM.healthDhtStatus.className = STATE.health.dht === "OK" ? "health-val ok" : "health-val fault";
    DOM.healthDhtStatus.textContent = STATE.health.dht === "OK" ? "● 1-WIRE KẾT NỐI" : "● LỖI READ TIMEOUT / NaN";
  }
  if (DOM.healthWatchdogStatus) {
    DOM.healthWatchdogStatus.className = STATE.health.watchdog === "OK" ? "health-val ok" : "health-val fault";
    DOM.healthWatchdogStatus.textContent = STATE.health.watchdog === "OK" ? "● PING 10s (ALIVE)" : "● TIMEOUT > 15s (OFFLINE)";
  }
  if (DOM.healthActuatorStatus) {
    DOM.healthActuatorStatus.className = STATE.health.actuator === "OK" ? "health-val ok" : "health-val fault";
    DOM.healthActuatorStatus.textContent = STATE.health.actuator === "OK" ? "● PHẢN HỒI ACK" : "● KẸT RƠ-LE / TIMEOUT";
  }

  // Simulator Sliders Sync
  if (DOM.simLblSmoke) DOM.simLblSmoke.textContent = STATE.ppm.toFixed(1) + " PPM";
  if (DOM.simSliderSmoke) DOM.simSliderSmoke.value = Math.round(STATE.ppm);
  if (DOM.simLblTemp) DOM.simLblTemp.textContent = STATE.temp.toFixed(1) + " °C";
  if (DOM.simSliderTemp) DOM.simSliderTemp.value = STATE.temp.toFixed(1);
}

// =============================================================================
// 9. CHART.JS REAL-TIME VISUALIZATION
// =============================================================================
function initChart() {
  const chartCanvas = DOM.telemetryChart;
  if (!chartCanvas) return;

  const ctx = chartCanvas.getContext("2d");
  const now = new Date();

  for (let i = 12; i >= 0; i--) {
    const t = new Date(now.getTime() - i * 2000);
    STATE.history.labels.push(t.toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit", second: "2-digit" }));
    STATE.history.ppmData.push(140 + Math.random() * 15);
    STATE.history.tempData.push(28.0 + Math.random() * 0.8);
  }

  telemetryChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: STATE.history.labels,
      datasets: [
        {
          label: "Khói MQ-2 (PPM)",
          data: STATE.history.ppmData,
          borderColor: "#f59e0b",
          backgroundColor: "rgba(245, 158, 11, 0.12)",
          borderWidth: 2.2,
          pointRadius: 2,
          pointHoverRadius: 5,
          tension: 0.35,
          fill: true,
          yAxisID: "ySmoke"
        },
        {
          label: "Nhiệt độ (°C)",
          data: STATE.history.tempData,
          borderColor: "#06b6d4",
          backgroundColor: "rgba(6, 182, 212, 0.08)",
          borderWidth: 1.8,
          pointRadius: 2,
          tension: 0.35,
          yAxisID: "yTemp"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#0f172a",
          borderColor: "#334155",
          borderWidth: 1,
          titleFont: { family: "Inter", size: 12 },
          bodyFont: { family: "Inter", size: 11 }
        }
      },
      scales: {
        x: {
          grid: { color: "rgba(0, 0, 0, 0.05)" },
          ticks: { color: "#64748b", font: { family: "JetBrains Mono", size: 10 }, maxTicksLimit: 7 }
        },
        ySmoke: {
          type: "linear",
          position: "left",
          min: 0,
          max: 800,
          grid: { color: "rgba(0, 0, 0, 0.05)" },
          ticks: { color: "#d97706", font: { family: "JetBrains Mono", size: 10 }, stepSize: 200 }
        },
        yTemp: {
          type: "linear",
          position: "right",
          min: 15,
          max: 75,
          grid: { drawOnChartArea: false },
          ticks: { color: "#0284c7", font: { family: "JetBrains Mono", size: 10 } }
        }
      }
    }
  });
}

function pushChartData(ppm, temp) {
  if (!telemetryChart) return;

  const nowStr = new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  STATE.history.labels.push(nowStr);
  STATE.history.ppmData.push(ppm);
  STATE.history.tempData.push(temp);

  if (STATE.history.labels.length > 25) {
    STATE.history.labels.shift();
    STATE.history.ppmData.shift();
    STATE.history.tempData.shift();
  }

  telemetryChart.update("none");
}

// =============================================================================
// 10. TELEGRAM ALERTING & AUDIT TRAIL
// =============================================================================
function dispatchTelegramAlert(htmlMessage) {
  const container = DOM.tgMessagesList;
  if (!container) return;

  const timeStr = new Date().toLocaleTimeString("vi-VN");
  const msgDiv = document.createElement("div");
  msgDiv.className = "tg-msg tg-bot-msg alarm-msg";
  msgDiv.innerHTML = `
    <div class="tg-msg-time">${timeStr}</div>
    <div class="tg-msg-bubble">${htmlMessage}</div>
  `;

  container.appendChild(msgDiv);
  container.scrollTop = container.scrollHeight;
}

function addAuditLog(level, eventName, description, fsmState) {
  const now = new Date();
  const timeStr = now.toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit", second: "2-digit" });

  const logItem = {
    time: timeStr,
    isoTime: now.toISOString(),
    level: level,
    event: eventName,
    desc: description,
    fsm: fsmState || STATE.fsmState
  };

  STATE.logs.unshift(logItem);
  if (STATE.logs.length > 80) STATE.logs.pop();

  renderAuditTable();
}

function renderAuditTable() {
  const tbody = DOM.auditTableBody;
  const filter = DOM.logFilterLevel ? DOM.logFilterLevel.value : "ALL";
  if (!tbody) return;

  tbody.innerHTML = "";

  const filtered = STATE.logs.filter(item => {
    if (filter === "ALL") return true;
    return item.level === filter;
  });

  filtered.slice(0, 30).forEach(log => {
    const tr = document.createElement("tr");

    let lvlClass = "lvl-sys";
    if (log.level === "CRITICAL") lvlClass = "lvl-critical";
    else if (log.level === "WARN") lvlClass = "lvl-warn";
    else if (log.level === "INFO") lvlClass = "lvl-info";

    tr.innerHTML = `
      <td style="font-family: var(--font-mono); font-size: 10px; color: #64748b;">${log.time}</td>
      <td><span class="badge-level ${lvlClass}">${log.level}</span></td>
      <td><strong style="color: #0f172a; font-size: 11px;">${log.event}</strong></td>
      <td style="font-size: 11px; color: #334155;">${log.desc}</td>
      <td style="font-family: var(--font-mono); font-size: 10px; color: #2563eb;">${log.fsm}</td>
    `;
    tbody.appendChild(tr);
  });
}

function exportLogsToCsv() {
  if (STATE.logs.length === 0) {
    showToast("Không có nhật ký nào để xuất.", "warning");
    return;
  }
  let csv = "Time,ISO_Timestamp,Level,Event,Description,FSM_State\n";
  STATE.logs.forEach(l => {
    csv += `"${l.time}","${l.isoTime}","${l.level}","${l.event}","${l.desc.replace(/"/g, '""')}","${l.fsm}"\n`;
  });

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `SmokeAlarm_AuditTrail_${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
  showToast("Đã tải xuống tệp Audit Trail CSV", "success");
}

function playAlarmAudioBeep() {
  try {
    if (!webAudioCtx) {
      webAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (webAudioCtx.state === "suspended") {
      webAudioCtx.resume();
    }
    const osc = webAudioCtx.createOscillator();
    const gain = webAudioCtx.createGain();
    osc.type = "sawtooth";
    osc.frequency.setValueAtTime(880, webAudioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(440, webAudioCtx.currentTime + 0.3);

    gain.gain.setValueAtTime(0.2, webAudioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, webAudioCtx.currentTime + 0.35);

    osc.connect(gain);
    gain.connect(webAudioCtx.destination);
    osc.start();
    osc.stop(webAudioCtx.currentTime + 0.35);
  } catch (err) {
    console.debug("Audio output suppressed by browser autoplay policy:", err);
  }
}

// =============================================================================
// 11. EVENT HANDLERS & USER INTERACTIONS
// =============================================================================
function initEventHandlers() {
  // Role selector
  if (DOM.userRoleSelect && DOM.currentRoleBadge) {
    DOM.userRoleSelect.addEventListener("change", (e) => {
      STATE.userRole = e.target.value;
      let label = "Quyền: Kỹ thuật viên";
      if (STATE.userRole === "admin") label = "Quyền: Quản trị viên (Toàn quyền)";
      else if (STATE.userRole === "viewer") label = "Quyền: Người dân (Chỉ xem)";
      DOM.currentRoleBadge.textContent = label;
      showToast(`Đã chuyển vai trò: [${e.target.selectedOptions[0].text}]`, "info");
      addAuditLog("INFO", "ROLE_SWITCH", `Người dùng đổi vai trò sang: ${STATE.userRole.toUpperCase()}`, STATE.fsmState);
    });
  }

  // Fan controls
  if (DOM.btnFanOn) {
    DOM.btnFanOn.addEventListener("click", () => {
      if (!checkRolePermission("operator", "bật quạt cưỡng bức")) return;
      STATE.fanState = true;
      STATE.fanMode = "MANUAL";
      sendDownlinkCommand("cmdFan", { action: "ON", user: STATE.userRole });
      addAuditLog("INFO", "MANUAL_FAN_ON", "Phát lệnh DOWNLINK bật quạt từ Tầng 4 Application.", STATE.fsmState);
      showToast("Đã gửi lệnh Downlink: BẬT QUẠT", "success");
      updateUiFromState();
    });
  }

  if (DOM.btnFanOff) {
    DOM.btnFanOff.addEventListener("click", () => {
      if (!checkRolePermission("operator", "tắt quạt")) return;
      if (STATE.fsmState === "ALARM" && STATE.userRole !== "admin") {
        showToast("TỪ CHỐI LỆNH: Hệ thống đang BÁO ĐỘNG HỎA HOẠN, cấm ngắt quạt hút khói!", "danger");
        addAuditLog("WARN", "OVERRIDE_REJECTED", "Từ chối lệnh tắt quạt do quy tắc an toàn PCCC khi khói nguy cấp.", STATE.fsmState);
        return;
      }
      STATE.fanState = false;
      STATE.fanMode = "MANUAL";
      sendDownlinkCommand("cmdFan", { action: "OFF", user: STATE.userRole });
      addAuditLog("INFO", "MANUAL_FAN_OFF", "Phát lệnh DOWNLINK tắt quạt từ Tầng 4 Application.", STATE.fsmState);
      showToast("Đã gửi lệnh Downlink: TẮT QUẠT", "info");
      updateUiFromState();
    });
  }

  if (DOM.btnFanAuto) {
    DOM.btnFanAuto.addEventListener("click", () => {
      if (!checkRolePermission("operator", "chuyển chế độ tự động")) return;
      STATE.fanMode = "AUTO";
      sendDownlinkCommand("cmdMode", { mode: "AUTO" });
      showToast("Chế độ quạt: Tự động theo FSM", "info");
      evaluateFsmRules();
      updateUiFromState();
    });
  }

  // Buzzer controls
  if (DOM.btnBuzzerMute) {
    DOM.btnBuzzerMute.addEventListener("click", () => {
      if (!checkRolePermission("operator", "tắt tiếng còi")) return;
      STATE.isMuted = true;
      STATE.muteRemainingSec = 180;
      STATE.buzzerActive = false;
      sendDownlinkCommand("cmdBuzzer", { action: "MUTE", duration: 180 });
      addAuditLog("WARN", "BUZZER_MUTED", "Đã tạm tắt còi 180 giây để ban quản lý xử lý hiện trường.", STATE.fsmState);
      showToast("Đã ngắt tiếng còi trong 180 giây!", "warning");

      if (muteInterval) clearInterval(muteInterval);
      muteInterval = setInterval(() => {
        STATE.muteRemainingSec--;
        if (STATE.muteRemainingSec <= 0) {
          clearInterval(muteInterval);
          STATE.isMuted = false;
          if (STATE.fsmState === "ALARM") STATE.buzzerActive = true;
          addAuditLog("INFO", "BUZZER_UNMUTED", "Hết thời gian Mute 180s. Còi kích hoạt trở lại.", STATE.fsmState);
        }
        updateUiFromState();
      }, 1000);

      updateUiFromState();
    });
  }

  if (DOM.btnBuzzerUnmute) {
    DOM.btnBuzzerUnmute.addEventListener("click", () => {
      if (!checkRolePermission("operator", "hủy mute còi")) return;
      if (muteInterval) clearInterval(muteInterval);
      STATE.isMuted = false;
      STATE.muteRemainingSec = 0;
      if (STATE.fsmState === "ALARM") STATE.buzzerActive = true;
      sendDownlinkCommand("cmdBuzzer", { action: "UNMUTE" });
      addAuditLog("INFO", "BUZZER_UNMUTED_MANUAL", "Đã hủy Mute còi thủ công từ Dashboard.", STATE.fsmState);
      showToast("Đã kích hoạt lại âm thanh còi!", "info");
      updateUiFromState();
    });
  }

  if (DOM.btnBuzzerTest) {
    DOM.btnBuzzerTest.addEventListener("click", () => {
      if (!checkRolePermission("operator", "kiểm tra còi")) return;
      sendDownlinkCommand("cmdBuzzer", { action: "TEST" });
      playAlarmAudioBeep();
      showToast("ESP32: Đang thực hiện Beep Test 0.5s...", "info");
    });
  }

  // Sensitivity Day/Night Mode
  if (DOM.btnModeDay) {
    DOM.btnModeDay.addEventListener("click", () => {
      if (!checkRolePermission("admin", "chỉnh ngưỡng độ nhạy")) return;
      STATE.sensitivityMode = "DAY";
      sendDownlinkCommand("cmdScheduler", { mode: "DAY" });
      addAuditLog("INFO", "SENSITIVITY_MODE", "Chuyển sang Chế độ Ban ngày (Ngưỡng 400 PPM)", STATE.fsmState);
      showToast("Đã chuyển Chế độ Ban ngày (Ngưỡng 400 PPM)", "info");
      evaluateFsmRules();
      updateUiFromState();
    });
  }

  if (DOM.btnModeNight) {
    DOM.btnModeNight.addEventListener("click", () => {
      if (!checkRolePermission("admin", "chỉnh ngưỡng độ nhạy")) return;
      STATE.sensitivityMode = "NIGHT";
      sendDownlinkCommand("cmdScheduler", { mode: "NIGHT" });
      addAuditLog("WARN", "SENSITIVITY_MODE", "Kích hoạt Chế độ Ban đêm (Hạ ngưỡng 350 PPM tăng nhạy)", STATE.fsmState);
      showToast("Đã kích hoạt Chế độ Ban đêm (Ngưỡng 350 PPM)", "warning");
      evaluateFsmRules();
      updateUiFromState();
    });
  }

  // Telegram actions
  if (DOM.btnTestTgAlert) {
    DOM.btnTestTgAlert.addEventListener("click", () => {
      dispatchTelegramAlert(
        `🧪 <b>THỬ NGHIỆM KÊNH CẢNH BÁO TELEGRAM</b>\n` +
        `Trạm: <code>ESP32_SMOKE_N04_A01</code>\n` +
        `Thời gian: <code>${new Date().toLocaleString("vi-VN")}</code>\n` +
        `Trạng thái kết nối Webhook: <b>THÀNH CÔNG</b>`
      );
      showToast("Đã phát tin cảnh báo thử nghiệm tới Telegram Bot", "success");
    });
  }

  if (DOM.btnClearTgHistory) {
    DOM.btnClearTgHistory.addEventListener("click", () => {
      if (DOM.tgMessagesList) DOM.tgMessagesList.innerHTML = "";
      showToast("Đã dọn sạch tin nhắn Telegram", "info");
    });
  }

  // Audit export
  if (DOM.btnExportLogs) DOM.btnExportLogs.addEventListener("click", exportLogsToCsv);
  if (DOM.logFilterLevel) DOM.logFilterLevel.addEventListener("change", renderAuditTable);

  // Modal Simulator
  const simModal = DOM.simModal;
  if (DOM.btnToggleSimModal && simModal) {
    DOM.btnToggleSimModal.addEventListener("click", () => simModal.classList.add("active"));
  }
  if (DOM.btnCloseSimModal && simModal) {
    DOM.btnCloseSimModal.addEventListener("click", () => simModal.classList.remove("active"));
  }
  if (DOM.btnApplySim && simModal) {
    DOM.btnApplySim.addEventListener("click", () => simModal.classList.remove("active"));
  }

  // Sliders input
  if (DOM.simSliderSmoke) {
    DOM.simSliderSmoke.addEventListener("input", (e) => {
      STATE.ppm = parseFloat(e.target.value);
      if (DOM.simLblSmoke) DOM.simLblSmoke.textContent = STATE.ppm + " PPM";
      evaluateFsmRules();
      updateUiFromState();
      pushChartData(STATE.ppm, STATE.temp);
    });
  }

  if (DOM.simSliderTemp) {
    DOM.simSliderTemp.addEventListener("input", (e) => {
      STATE.temp = parseFloat(e.target.value);
      if (DOM.simLblTemp) DOM.simLblTemp.textContent = STATE.temp.toFixed(1) + " °C";
      evaluateFsmRules();
      updateUiFromState();
      pushChartData(STATE.ppm, STATE.temp);
    });
  }

  if (DOM.btnSimDisconnect) {
    DOM.btnSimDisconnect.addEventListener("click", () => {
      setOfflineState();
      showToast("Đã mô phỏng đứt kết nối mạng ESP32", "danger");
    });
  }

  if (DOM.btnSimReconnect) {
    DOM.btnSimReconnect.addEventListener("click", () => {
      STATE.deviceOnline = true;
      STATE.lastSeenTime = Date.now();
      STATE.fsmState = "SAFE";
      STATE.health.watchdog = "OK";
      addAuditLog("INFO", "RECONNECTED", "ESP32 đã tái kết nối mạng thành công.", "SAFE");
      showToast("Đã khôi phục kết nối trạm cảm biến!", "success");
      updateUiFromState();
    });
  }

  // Banner Actions
  if (DOM.btnBannerMute && DOM.btnBuzzerMute) {
    DOM.btnBannerMute.addEventListener("click", () => DOM.btnBuzzerMute.click());
  }
  if (DOM.btnBannerAcknowledge) {
    DOM.btnBannerAcknowledge.addEventListener("click", () => {
      addAuditLog("INFO", "INCIDENT_ACKNOWLEDGED", `Người dùng (${STATE.userRole}) xác nhận đã tiếp nhận sự cố.`, STATE.fsmState);
      showToast("Đã xác nhận sự cố an toàn PCCC", "success");
    });
  }
}

// =============================================================================
// 12. FAULT INJECTION SANDBOX HANDLERS (WEEK 7 BINDINGS)
// =============================================================================
function initFaultInjectionHandlers() {
  if (DOM.btnFaultMq2) {
    DOM.btnFaultMq2.addEventListener("click", () => {
      sendDownlinkCommand("cmdInjectFault", { fault: "MQ2_DISCONNECT" });
      STATE.health.mq2 = "FAULT";
      STATE.fsmState = "FAULT";
      addAuditLog("CRITICAL", "FAULT_INJECTION_MQ2", "Kích hoạt mô phỏng đứt dây cảm biến khói MQ-2.", "FAULT");
      showToast("Đã gửi lệnh giả lập sự cố: Đứt dây MQ-2", "danger");
      updateUiFromState();
    });
  }

  if (DOM.btnFaultDht) {
    DOM.btnFaultDht.addEventListener("click", () => {
      sendDownlinkCommand("cmdInjectFault", { fault: "DHT_NAN" });
      STATE.health.dht = "FAULT";
      STATE.fsmState = "FAULT";
      addAuditLog("CRITICAL", "FAULT_INJECTION_DHT", "Kích hoạt mô phỏng lỗi cảm biến nhiệt ẩm DHT22 (NaN).", "FAULT");
      showToast("Đã gửi lệnh giả lập sự cố: Lỗi DHT22 (NaN)", "danger");
      updateUiFromState();
    });
  }

  if (DOM.btnFaultActuator) {
    DOM.btnFaultActuator.addEventListener("click", () => {
      sendDownlinkCommand("cmdInjectFault", { fault: "ACTUATOR_FAULT" });
      STATE.health.actuator = "FAULT";
      addAuditLog("WARN", "FAULT_INJECTION_ACTUATOR", "Kích hoạt mô phỏng kẹt tiếp điểm Rơ-le quạt.", STATE.fsmState);
      showToast("Đã gửi lệnh giả lập sự cố: Kẹt Rơ-le quạt", "warning");
      updateUiFromState();
    });
  }

  if (DOM.btnSyncBuffer) {
    DOM.btnSyncBuffer.addEventListener("click", () => {
      addAuditLog("INFO", "OFFLINE_SYNC_REQ", "Yêu cầu đồng bộ 20 bản ghi bộ đệm ngoại tuyến (Circular Buffer).", STATE.fsmState);
      showToast("Đang đồng bộ 20 bản ghi ngoại tuyến từ vòng đệm ESP32...", "info");
      setTimeout(() => {
        showToast("Đồng bộ dữ liệu ngoại tuyến thành công 100%!", "success");
      }, 1200);
    });
  }

  if (DOM.btnClearAllFaults) {
    DOM.btnClearAllFaults.addEventListener("click", () => {
      sendDownlinkCommand("cmdInjectFault", { fault: "CLEAR" });
      STATE.health.mq2 = "OK";
      STATE.health.dht = "OK";
      STATE.health.actuator = "OK";
      STATE.health.watchdog = "OK";
      STATE.fsmState = "SAFE";
      addAuditLog("INFO", "FAULT_RESTORED", "Đã xóa toàn bộ sự cố mô phỏng. Hệ thống trở về SAFE.", "SAFE");
      showToast("Đã khôi phục toàn bộ cảm biến về trạng thái bình thường!", "success");
      updateUiFromState();
    });
  }
}

// Preset helper called from inline buttons
window.setSimPreset = function(ppmVal, tempVal) {
  STATE.ppm = ppmVal;
  STATE.temp = tempVal;
  evaluateFsmRules();
  updateUiFromState();
  pushChartData(STATE.ppm, STATE.temp);
  showToast(`Thiết lập giả lập: Khói ${ppmVal} PPM, Nhiệt độ ${tempVal}°C`, "info");
};

function initSimulatorDefaults() {
  setInterval(() => {
    if (STATE.fsmState === "SAFE" && DOM.simModal && !DOM.simModal.classList.contains("active")) {
      const delta = (Math.random() - 0.5) * 3;
      STATE.ppm = Math.max(80, Math.min(220, STATE.ppm + delta));
      updateUiFromState();
      pushChartData(STATE.ppm, STATE.temp);
    }
  }, 2500);
}

// =============================================================================
// 13. TOAST & CLOCK UTILITIES
// =============================================================================
function showToast(message, type = "info") {
  const container = DOM.toastContainer;
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;

  let icon = "ℹ️";
  if (type === "success") icon = "✅";
  else if (type === "danger") icon = "🚨";
  else if (type === "warning") icon = "⚠️";

  toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(50px)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function initClock() {
  const el = DOM.clockDisplay;
  if (!el) return;

  setInterval(() => {
    el.textContent = new Date().toLocaleTimeString("vi-VN");
  }, 1000);
}
