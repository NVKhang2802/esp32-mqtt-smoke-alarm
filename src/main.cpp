/**
 * @file main.cpp
 * @brief Chuong trinh dieu khien chinh (Main Application Orchestrator)
 * @details De tai 04: He thong bao khoi canh bao som - Nhom 04 (N09)
 *          Kien truc Lean & Clean Code: JsonDocument cap phat heap tam theo RAII trong tung handler, giai phong khi thoat ham; gioi han boi buffer mang (512B) va payload (256B).
 */

#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

#include "config.h"
#include "offline_buffer.h"
#include "sensors.h"
#include "fsm.h"
#include "backoff.h"
#include "cmd_parse.h"

// ============================================================================
// GLOBAL STATE & SYSTEM CONTEXT
// ============================================================================
static SensorConfig g_cfg = {
  5.0f,     // vccSensor
  10.0f,    // rlKOhm
  1.0f,     // curveA
  1.0f,     // curveB
  200.0f,   // calibPoint1
  1000.0f   // calibPoint2
};

static Thresholds   g_th  = makeThresholds(DEFAULT_ALARM_PPM_DAY);
static FsmContext   g_fsm = {};
static FsmInput     g_in  = {};
static FsmOutput    g_out = {};
static EmaFilter    g_ema = {};
static Mq2Health    g_mq2h = {};
static DhtHealth    g_dhth = {};

static float        g_r0          = 10.0f;
static float        g_ppm         = 0.0f;
static float        g_temp        = 28.0f;
static float        g_hum         = 65.0f;
static uint32_t     g_cycleCount  = 0;

// Simulation flags for fault injection sandbox
static bool g_simMq2 = false;
static bool g_simDht = false;

// Session & Client Identity
static char g_sessionKey[40] = "SK_SESSION_DEFAULT_N09";
static char g_clientId[40]   = "";
static char g_macAddress[20] = "";

// Timers
static uint32_t g_lastSample    = 0;
static uint32_t g_lastDht       = 0;
static uint32_t g_lastHeartbeat = 0;

// Network backoff & non-blocking state
static ExponentialBackoff s_wifiBackoff;
static ExponentialBackoff s_mqttBackoff;
static uint32_t s_wifiEnd     = 0;
static uint32_t s_wifiBegin   = 0;
static uint32_t s_mqttTry     = 0;
static bool     s_wifiBusy    = false;

// Button debounce
static bool     g_lastButtonState   = HIGH;
static bool     g_stableButtonState = HIGH;
static uint32_t g_lastDebounceTime  = 0;

// Network clients
static WiFiClient   g_espClient;
static PubSubClient g_mqttClient(g_espClient);

// ============================================================================
// FORWARD DECLARATIONS
// ============================================================================
static void recompute();
static void publishTelemetry();
static void publishAlarmEvent(bool isCritical);
static void publishAuthRequest();
static void publishKeepAlive();
static void mqttCallback(char* topic, byte* payload, unsigned int length);
static bool mqttConnect();
static void netTick(uint32_t now);
static void buttonTick(uint32_t now);

// ============================================================================
// COMMAND & ACK HELPERS
// ============================================================================
enum CmdType : uint8_t {
  CMD_FAN,
  CMD_BUZZER,
  CMD_MODE,
  CMD_SCHEDULER,
  CMD_FAULT,
  CMD_BUTTON,
  CMD_SYSTEM
};

static const char* cmdName(CmdType c) {
  switch (c) {
    case CMD_FAN:       return "cmd_fan";
    case CMD_BUZZER:    return "cmd_buzzer";
    case CMD_MODE:      return "cmd_mode";
    case CMD_SCHEDULER: return "cmd_scheduler";
    case CMD_FAULT:     return "inject_fault";
    case CMD_BUTTON:    return "button_press";
    default:            return "system";
  }
}

static const char* ackResultStr(AckResult r) {
  switch (r) {
    case ACK_ACCEPTED:       return "ACCEPTED";
    case ACK_SAFETY_LOCK:    return "REJECTED_SAFETY_LOCK";
    case ACK_LOCAL_SILENCE:  return "LOCAL_SILENCE_60S";
    case ACK_BAD_PAYLOAD:    return "REJECTED_BAD_PAYLOAD";
    case ACK_UNKNOWN_ACTION: return "REJECTED_UNKNOWN_ACTION";
    default:                 return "UNKNOWN";
  }
}

static void publishAck(CmdType cmd, AckResult res, const char* detail = "") {
  if (!g_mqttClient.connected()) return;

  char payload[256];
  snprintf(payload, sizeof(payload),
    "{\"device_id\":\"%s\",\"cmd\":\"%s\",\"result\":\"%s\",\"detail\":\"%s\",\"fan\":\"%s\",\"buzzer\":\"%s\",\"mode\":\"%s\",\"fsm_state\":\"%s\"}",
    DEVICE_ID, cmdName(cmd), ackResultStr(res), detail,
    g_out.fanOn ? "ON" : "OFF",
    (g_out.buzzer != BUZZ_OFF) ? "ON" : "OFF",
    g_fsm.manualMode ? "MANUAL" : "AUTO",
    getFsmStateString(g_fsm.state)
  );

  g_mqttClient.publish(TOPIC_STATUS, payload);
  g_mqttClient.publish(TOPIC_V2_STATUS, payload);
  Serial.printf("  [MQTT STATUS] -> ACK %s: %s (%s)\r\n", cmdName(cmd), ackResultStr(res), detail);
}

static void recompute() {
  g_in.nowMs = millis();
  g_in.ppm = g_ppm;
  g_in.mq2Fault = g_mq2h.fault;
  g_in.dhtFault = g_dhth.fault;
  g_out = fsmStep(g_fsm, g_in, g_th);
  fanApply(g_out.fanOn);
  buzzerTick(g_out.buzzer, g_in.nowMs);
}

// ============================================================================
// UPLINK MESSAGING HELPERS
// ============================================================================
static void publishTelemetry() {
  char ppmStr[16];
  if (g_mq2h.fault) {
    strcpy(ppmStr, "null");
  } else {
    snprintf(ppmStr, sizeof(ppmStr), "%.1f", g_ppm);
  }

  char payload[384];
  snprintf(payload, sizeof(payload),
    "{\"device_id\":\"%s\",\"uptime_s\":%lu,\"mq2_ppm\":%s,\"mq2_valid\":%s,\"temp\":%.1f,\"hum\":%.1f,\"dht_valid\":%s,\"fan\":\"%s\",\"buzzer\":\"%s\",\"buzzer_muted\":%s,\"mode\":\"%s\",\"fsm_state\":\"%s\",\"alarm_th\":%.1f,\"safe_th\":%.1f}",
    DEVICE_ID,
    millis() / 1000,
    ppmStr,
    g_mq2h.fault ? "false" : "true",
    g_temp,
    g_hum,
    g_dhth.fault ? "false" : "true",
    g_out.fanOn ? "ON" : "OFF",
    (g_out.buzzer != BUZZ_OFF) ? "ON" : "OFF",
    g_out.buzzerMuted ? "true" : "false",
    g_fsm.manualMode ? "MANUAL" : "AUTO",
    getFsmStateString(g_fsm.state),
    g_th.alarm,
    g_th.safe
  );

  if (g_mqttClient.connected()) {
    g_mqttClient.publish(TOPIC_TELEMETRY, payload);
    g_mqttClient.publish(TOPIC_V2_TELEMETRY, payload);
  } else {
    pushOfflineRecord(g_mq2h.fault ? 0.0f : g_ppm, g_temp, g_hum, g_out.fanOn, (g_out.buzzer != BUZZ_OFF), getFsmStateString(g_fsm.state), "TELEMETRY", !g_mq2h.fault, !g_dhth.fault);
  }
}

static void publishAlarmEvent(bool isCritical) {
  char payload[256];
  if (isCritical) {
    snprintf(payload, sizeof(payload),
      "{\"device_id\":\"%s\",\"uptime_s\":%lu,\"event\":\"SMOKE_ALERT\",\"severity\":\"CRITICAL\",\"ppm\":%.1f,\"threshold\":%.1f,\"msg\":\"CANH BAO: Khoi vuot nguong! Coi va Quat da bat!\"}",
      DEVICE_ID, millis() / 1000, g_ppm, g_th.alarm
    );
  } else {
    snprintf(payload, sizeof(payload),
      "{\"device_id\":\"%s\",\"uptime_s\":%lu,\"event\":\"SMOKE_SAFE\",\"severity\":\"NORMAL\",\"ppm\":%.1f,\"threshold\":%.1f,\"msg\":\"AN TOAN: Nong do khoi da ve muc an toan. Bat dau Purge 30s.\"}",
      DEVICE_ID, millis() / 1000, g_ppm, g_th.safe
    );
  }

  if (g_mqttClient.connected()) {
    g_mqttClient.publish(TOPIC_EVENT_ALARM, payload);
    g_mqttClient.publish(TOPIC_V2_ALARM, payload);
  } else {
    pushOfflineRecord(g_ppm, g_temp, g_hum, g_out.fanOn, (g_out.buzzer != BUZZ_OFF), getFsmStateString(g_fsm.state), "ALARM_EVENT", !g_mq2h.fault, !g_dhth.fault);
  }
  Serial.printf("  [MQTT EVENT] -> ALARM %s (PPM: %.1f)\r\n", isCritical ? "CRITICAL" : "SAFE", g_ppm);
}

static void publishAuthRequest() {
  if (!g_mqttClient.connected()) return;

  char payload[256];
  snprintf(payload, sizeof(payload),
    "{\"msg_id\":\"REQ-AUTH-%04lu\",\"device_id\":\"%s\",\"mac_address\":\"%s\",\"secret_token\":\"HUIT_IOT_SECURE_TOKEN_N09\",\"timestamp\":%lu}",
    millis() / 1000,
    DEVICE_ID,
    g_macAddress,
    millis() / 1000
  );

  g_mqttClient.publish(TOPIC_V2_AUTH_REQ, payload, 1);
  Serial.println(F("  [MQTT AUTH REQ] -> Sent Auth Request"));
}

static void publishKeepAlive() {
  if (!g_mqttClient.connected()) return;

  const char* statusStr = (g_fsm.state == STATE_FAULT || g_mq2h.fault) ? "FAULT" : (g_dhth.fault ? "DEGRADED" : "HEALTHY");
  char payload[256];
  snprintf(payload, sizeof(payload),
    "{\"session_key\":\"%s\",\"device_id\":\"%s\",\"uptime_s\":%lu,\"uptime_sec\":%lu,\"free_heap_bytes\":%u,\"wifi_rssi_dbm\":%d,\"status\":\"%s\",\"fsm_state\":\"%s\"}",
    g_sessionKey,
    DEVICE_ID,
    millis() / 1000,
    millis() / 1000,
    ESP.getFreeHeap(),
    WiFi.RSSI(),
    statusStr,
    getFsmStateString(g_fsm.state)
  );

  g_mqttClient.publish(TOPIC_KEEP_ALIVE_V1, payload);
  g_mqttClient.publish(TOPIC_V2_KEEP_ALIVE, payload);
}

// ============================================================================
// DOWNLINK COMMAND HANDLERS
// ============================================================================
static bool is(const char* a, const char* v) { return a && strcasecmp(a, v) == 0; }

static void onAuthResponse(const char* topic, const char* message) {
  if (strstr(topic, DEVICE_ID) == nullptr) return;

  JsonDocument doc;
  if (deserializeJson(doc, message)) return;

  const char* status = doc["status"] | "REJECTED";
  if (is(status, "PASS")) {
    const char* sk = doc["session_key"] | "SK_AUTHORIZED_N09";
    strncpy(g_sessionKey, sk, sizeof(g_sessionKey) - 1);
    g_sessionKey[sizeof(g_sessionKey) - 1] = '\0';
    Serial.println(F("  [AUTH PASS] Server accepted device"));

    if (doc["config"]["alarm_threshold_ppm"].is<float>()) {
      float reqTh = doc["config"]["alarm_threshold_ppm"].as<float>();
      g_th = makeThresholds(reqTh);
      Serial.printf("  [AUTH CONFIG] Synced alarm threshold: %.1f PPM (Safe: %.1f PPM)\r\n", g_th.alarm, g_th.safe);
    }
    publishAck(CMD_SYSTEM, ACK_ACCEPTED, "AUTH_PASS");
  } else {
    Serial.println(F("  [AUTH REJECTED] Server rejected authentication"));
  }
}

static void onFan(const char* message) {
  JsonDocument doc;
  if (deserializeJson(doc, message)) {
    publishAck(CMD_FAN, ACK_BAD_PAYLOAD, "JSON_PARSE_ERROR");
    return;
  }

  const char* action = doc["action"] | doc["cmd"] | "";
  ActionAck ack = applyFanAction(g_fsm, action);
  if (ack == ACTION_ACCEPTED) {
    publishAck(CMD_FAN, ACK_ACCEPTED, is(action, "AUTO") ? "MODE_AUTO" : (g_fsm.manualFan ? "FAN_ON" : "FAN_OFF"));
  } else if (ack == ACTION_SAFETY_LOCK) {
    publishAck(CMD_FAN, ACK_SAFETY_LOCK, "PPM_ABOVE_THRESHOLD");
  } else {
    publishAck(CMD_FAN, ACK_UNKNOWN_ACTION, "UNKNOWN_ACTION");
  }
  recompute();
}

static void onBuzzer(const char* message) {
  JsonDocument doc;
  if (deserializeJson(doc, message)) {
    publishAck(CMD_BUZZER, ACK_BAD_PAYLOAD, "JSON_PARSE_ERROR");
    return;
  }

  const char* action = doc["action"] | doc["cmd"] | "";
  ActionAck ack = applyBuzzerAction(g_fsm, action, millis());
  if (ack == ACTION_ACCEPTED) {
    if (is(action, "TEST") || is(action, "ON")) {
      buzzerTest(millis());
      publishAck(CMD_BUZZER, ACK_ACCEPTED, "TEST_500MS");
    } else {
      publishAck(CMD_BUZZER, ACK_ACCEPTED, g_fsm.muted ? "MUTED_180S" : "UNMUTED");
    }
  } else if (ack == ACTION_SAFETY_LOCK) {
    publishAck(CMD_BUZZER, ACK_SAFETY_LOCK, "ALARM_LATCHED");
  } else {
    publishAck(CMD_BUZZER, ACK_UNKNOWN_ACTION, "UNKNOWN_ACTION");
  }
  recompute();
}

static void onMode(const char* message) {
  JsonDocument doc;
  if (deserializeJson(doc, message)) {
    publishAck(CMD_MODE, ACK_BAD_PAYLOAD, "JSON_PARSE_ERROR");
    return;
  }

  const char* modeStr = doc["mode"] | doc["action"] | "";
  if (is(modeStr, "MANUAL")) {
    g_fsm.manualMode = true;
    publishAck(CMD_MODE, ACK_ACCEPTED, "MANUAL_MODE");
  } else if (is(modeStr, "AUTO")) {
    g_fsm.manualMode = false;
    publishAck(CMD_MODE, ACK_ACCEPTED, "AUTO_MODE");
  } else {
    publishAck(CMD_MODE, ACK_UNKNOWN_ACTION, "UNKNOWN_MODE");
  }
  recompute();
}

static void onScheduler(const char* message) {
  JsonDocument doc;
  if (deserializeJson(doc, message)) {
    publishAck(CMD_SCHEDULER, ACK_BAD_PAYLOAD, "JSON_PARSE_ERROR");
    return;
  }

  const char* mode = doc["mode"] | "";
  if (is(mode, "NIGHT")) {
    g_th = makeThresholds(ALARM_PPM_NIGHT);
    publishAck(CMD_SCHEDULER, ACK_ACCEPTED, "NIGHT_MODE_350PPM");
  } else if (is(mode, "DAY")) {
    g_th = makeThresholds(DEFAULT_ALARM_PPM_DAY);
    publishAck(CMD_SCHEDULER, ACK_ACCEPTED, "DAY_MODE_400PPM");
  } else {
    publishAck(CMD_SCHEDULER, ACK_UNKNOWN_ACTION, "UNKNOWN_SCHEDULER_MODE");
  }
  recompute();
}

static void onFaultInjection(const char* message) {
  JsonDocument doc;
  if (deserializeJson(doc, message)) {
    publishAck(CMD_FAULT, ACK_BAD_PAYLOAD, "JSON_PARSE_ERROR");
    return;
  }

  const char* type = doc["type"] | doc["fault"] | "";
  if (is(type, "MQ2_DISCONNECT")) {
    g_simMq2 = true;
    mq2Update(g_mq2h, 0, g_simMq2, MQ2_ENTER_N, MQ2_EXIT_N);
    publishAck(CMD_FAULT, ACK_ACCEPTED, "MQ2_DISCONNECT_INJECTED");
  } else if (is(type, "DHT_NAN") || is(type, "DHT_TIMEOUT")) {
    g_simDht = true;
    dhtOnRead(g_dhth, false, g_temp, g_simDht);
    publishAck(CMD_FAULT, ACK_ACCEPTED, "DHT_FAULT_INJECTED");
  } else if (is(type, "CLEAR") || is(type, "RESTORE") || is(type, "NONE")) {
    g_simMq2 = false;
    g_simDht = false;
    g_mq2h = {};
    g_dhth = {};
    emaReset(g_ema, g_ppm > 0.0f ? g_ppm : 200.0f);
    publishAck(CMD_FAULT, ACK_ACCEPTED, "ALL_FAULTS_CLEARED");
  } else {
    publishAck(CMD_FAULT, ACK_UNKNOWN_ACTION, "REJECTED_UNKNOWN_FAULT");
  }
  recompute();
}

static void mqttCallback(char* topic, byte* payload, unsigned int length) {
  if (!topic || !payload || length == 0) return;

  char message[256];
  if (length >= sizeof(message)) length = sizeof(message) - 1;
  memcpy(message, payload, length);
  message[length] = '\0';

  Serial.println(F("\r\n====================== [DOWNLINK COMMAND] ======================"));
  Serial.print(F("Topic   : ")); Serial.println(topic);
  Serial.print(F("Payload : ")); Serial.println(message);

  if (strstr(topic, "/auth/response") != nullptr) {
    onAuthResponse(topic, message);
  } else if (strcmp(topic, TOPIC_CMD_FAN) == 0 || strstr(topic, "/cmd/fan") != nullptr) {
    onFan(message);
  } else if (strcmp(topic, TOPIC_CMD_BUZZER) == 0 || strstr(topic, "/cmd/buzzer") != nullptr) {
    onBuzzer(message);
  } else if (strcmp(topic, TOPIC_CMD_MODE) == 0 || strstr(topic, "/cmd/mode") != nullptr) {
    onMode(message);
  } else if (strcmp(topic, TOPIC_CMD_INJECT_FAULT) == 0 || strstr(topic, "/inject_fault") != nullptr) {
    onFaultInjection(message);
  } else if (strcmp(topic, TOPIC_CMD_SCHEDULER) == 0 || strstr(topic, "/scheduler") != nullptr) {
    onScheduler(message);
  }

  Serial.println(F("================================================================\r\n"));
}

// ============================================================================
// HARDWARE PERIPHERALS & NETWORK ORCHESTRATION
// ============================================================================
static void buttonTick(uint32_t now) {
  const bool reading = digitalRead(PIN_BUTTON);
  if (reading != g_lastButtonState) {
    g_lastDebounceTime = now;
  }

  if ((now - g_lastDebounceTime) > DEBOUNCE_DELAY_MS) {
    if (reading != g_stableButtonState) {
      g_stableButtonState = reading;
      if (g_stableButtonState == LOW) {
        bool silenced = cmdLocalButton(g_fsm, now);
        publishAck(CMD_BUTTON, silenced ? ACK_LOCAL_SILENCE : ACK_ACCEPTED, silenced ? "LOCAL_SILENCE_60S" : (g_fsm.manualFan ? "FAN_ON" : "FAN_OFF"));
        recompute();
      }
    }
  }
  g_lastButtonState = reading;
}

static bool mqttConnect() {
  Serial.print(F("[MQTT] Connecting to Broker "));
  Serial.println(MQTT_BROKER);

  g_mqttClient.setSocketTimeout(2);

  const char* lwtMsg = "{\"device_id\":\"ESP32_SMOKE_N09_A01\",\"status\":\"offline\",\"eventType\":\"LWT\"}";
  if (g_mqttClient.connect(g_clientId, TOPIC_LWT, 1, true, lwtMsg)) {
    Serial.println(F("[MQTT] >>> CONNECTED SUCCESSFULLY! <<<"));

    const char* onlineMsg = "{\"device_id\":\"ESP32_SMOKE_N09_A01\",\"status\":\"online\"}";
    g_mqttClient.publish(TOPIC_LWT, onlineMsg, true);

    g_mqttClient.subscribe("Nhom09/smoke/cmd/#", 1);
    g_mqttClient.subscribe(TOPIC_V2_AUTH_RESP, 1);
    g_mqttClient.subscribe("Nhom09/smoke/v2/+/+/+/+/cmd/#", 1);

    publishAck(CMD_SYSTEM, ACK_ACCEPTED, "ONLINE_READY");
    publishAuthRequest();
    flushOfflineBuffer(g_mqttClient, TOPIC_OFFLINE_SYNC, 5);
    return true;
  } else {
    Serial.printf("[MQTT] Connection failed, rc=%d\r\n", g_mqttClient.state());
    return false;
  }
}

static void netTick(uint32_t now) {
  if (WiFi.status() != WL_CONNECTED) {
    if (!s_wifiBusy) {
      if (now - s_wifiEnd >= s_wifiBackoff.currentMs) {
        WiFi.disconnect();
        WiFi.begin(WIFI_SSID, WIFI_PASS);
        s_wifiBusy = true;
        s_wifiBegin = now;
      }
    } else if (now - s_wifiBegin >= WIFI_ATTEMPT_TIMEOUT_MS) {
      s_wifiBusy = false;
      s_wifiEnd = now;
      s_wifiBackoff.fail();
    }
    return;
  }

  s_wifiBusy = false;
  s_wifiBackoff.reset();

  if (g_mqttClient.connected()) {
    g_mqttClient.loop();
    flushOfflineBuffer(g_mqttClient, TOPIC_OFFLINE_SYNC, 5);
    return;
  }

  if (now - s_mqttTry >= s_mqttBackoff.currentMs) {
    s_mqttTry = now;
    if (mqttConnect()) {
      s_mqttBackoff.reset();
    } else {
      s_mqttBackoff.fail();
    }
  }
}

// ============================================================================
// ARDUINO SETUP & MAIN LOOP
// ============================================================================
void setup() {
  Serial.begin(115200);
  delay(300);

  Serial.println(F("\r\n========================================================"));
  Serial.println(F("  HE THONG BAO KHOI CANH BAO SOM - FIRMWARE V5"));
  Serial.println(F("  Nhom 04 - Lop Lap trinh nhung IoT - GVHD: Vo Hoang Hai "));
  Serial.println(F("========================================================"));

  pinMode(PIN_BUTTON, INPUT_PULLUP);

  initActuators();
  initSensors();
  initOfflineBuffer();
  calibrateMQ2(g_cfg, g_r0);

  // Generate unique client ID with random hex suffix
  snprintf(g_clientId, sizeof(g_clientId), "%s%04X", MQTT_CLIENT_PREFIX, (uint16_t)random(0xffff));
  strncpy(g_macAddress, WiFi.macAddress().c_str(), sizeof(g_macAddress) - 1);
  g_macAddress[sizeof(g_macAddress) - 1] = '\0';
  Serial.printf("[SETUP] Client ID: %s | MAC: %s\r\n", g_clientId, g_macAddress);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  g_espClient.setTimeout(2);
  g_mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  g_mqttClient.setCallback(mqttCallback);
  g_mqttClient.setBufferSize(512);
  g_mqttClient.setSocketTimeout(2);

  recompute();
  Serial.println(F("[SETUP] Initialization complete. Starting non-blocking loop.\r\n"));
}

void loop() {
  const uint32_t loopStart = millis();
  const uint32_t now = loopStart;

  // 1. Maintain Network connectivity (Non-blocking decoupled backoff)
  netTick(now);

  // 2. Hardware push button
  buttonTick(now);

  // 3. Actuator updates (Edge-triggered LEDC tone)
  buzzerTick(g_out.buzzer, now);
  fanApply(g_out.fanOn);

  // 4. Sample MQ-2 & step FSM every SAMPLE_MS (2000ms)
  if (now - g_lastSample >= SAMPLE_MS) {
    g_lastSample = now;
    g_cycleCount++;

    const SystemState prev = g_fsm.state;
    const int adc = analogRead(PIN_MQ2);
    const float rawPpm = readMQ2PPM(g_cfg, g_r0);

    const HealthEvent ev = mq2Update(g_mq2h, adc, g_simMq2, MQ2_ENTER_N, MQ2_EXIT_N);
    if (ev == HE_RECOVERED) {
      emaReset(g_ema, rawPpm);
    }
    if (!g_mq2h.fault) {
      g_ppm = emaUpdate(g_ema, rawPpm);
    }

    g_in = { g_ppm, g_mq2h.fault, g_dhth.fault, now };
    g_out = fsmStep(g_fsm, g_in, g_th);

    Serial.printf("[#%04lu | T=%3lus] PPM: %5.1f (raw: %5.1f) | Nhiet: %4.1f*C | Am: %4.1f%% | Quat: %3s | Coi: %3s | State: %s\r\n",
      g_cycleCount,
      now / 1000,
      g_mq2h.fault ? 0.0f : g_ppm,
      rawPpm,
      g_temp,
      g_hum,
      g_out.fanOn ? "BAT" : "TAT",
      (g_out.buzzer != BUZZ_OFF) ? "BAT" : "TAT",
      getFsmStateString(g_fsm.state)
    );

    if (g_fsm.state == STATE_ALARM && prev != STATE_ALARM) {
      publishAlarmEvent(true);
    } else if (g_fsm.state == STATE_COOLDOWN && prev == STATE_ALARM) {
      publishAlarmEvent(false);
    }

    publishTelemetry();
  }

  // 5. Poll DHT22 temperature & humidity (5000ms)
  if (now - g_lastDht >= DHT_POLL_INTERVAL_MS) {
    g_lastDht = now;
    float t = 0.0f, h = 0.0f;
    const bool ok = readDHT(t, h);
    dhtOnRead(g_dhth, ok, t, g_simDht);
    if (ok && !g_dhth.fault) {
      g_temp = t;
      g_hum  = h;
    }
  }

  // 6. Periodic Keep-Alive heartbeat (10s)
  if (now - g_lastHeartbeat >= HEARTBEAT_INTERVAL_MS) {
    g_lastHeartbeat = now;
    publishKeepAlive();
  }

  // 7. Loop Latency Performance Guard
  const uint32_t loopDuration = millis() - loopStart;
  if (loopDuration > NET_MAX_BLOCK_MS) {
    Serial.printf("[PERF WARN] Loop duration %lu ms exceeded NET_MAX_BLOCK_MS (%lu ms)!\r\n", loopDuration, NET_MAX_BLOCK_MS);
  }
}
