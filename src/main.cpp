/**
 * @file main.cpp
 * @brief Chuong trinh dieu khien chinh (Main Application Orchestrator)
 * @details De tai 04: He thong bao khoi canh bao som - Nhom 04 (N09)
 *          Kien truc Lean & Clean Code: Zero Heap Fragmentation, Modular SRP.
 */

#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

#include "config.h"
#include "offline_buffer.h"
#include "sensors.h"
#include "fsm.h"

// ============================================================================
// GLOBAL STATE & SYSTEM CONTEXT
// ============================================================================
static SensorConfig       g_cfg = {
  .vccSensor      = 5.0f,
  .rlKOhm         = 10.0f,
  .curveA         = 1.0f,
  .curveB         = 1.0f,
  .alarmThreshold = DEFAULT_ALARM_PPM_DAY,
  .safeThreshold  = DEFAULT_SAFE_PPM_DAY,
  .calibPoint1    = 200.0f,
  .calibPoint2    = 1000.0f,
  .intervalMQ2    = SENSOR_POLL_INTERVAL_MS,
  .intervalDHT    = DHT_POLL_INTERVAL_MS
};

static FsmContext          g_fsm;
static SensorHealthStatus  g_health = { false, false, "NONE" };

static float         g_r0          = 10.0f;
static float         g_currentPPM  = 0.0f;
static float         g_currentTemp = 28.0f;
static float         g_currentHum  = 65.0f;
static unsigned long g_cycleCount  = 0;

// Simulation flags for fault injection sandbox
static bool g_simFaultMQ2      = false;
static bool g_simFaultDHT      = false;
static bool g_simFaultActuator = false;

// Session & Client Identity
static char g_sessionKey[36] = "SK_SESSION_DEFAULT_N04";
static char g_clientId[40]   = "";
static char g_macAddress[20] = "";

// Timers
static unsigned long g_lastMQ2Time       = 0;
static unsigned long g_lastDHTTime       = 0;
static unsigned long g_lastKeepAliveTime = 0;
static unsigned long g_lastWifiRetry     = 0;
static unsigned long g_lastMqttRetry     = 0;

// Button debounce
static bool          g_lastButtonState   = HIGH;
static bool          g_stableButtonState = HIGH;
static unsigned long g_lastDebounceTime  = 0;

// Network clients
static WiFiClient   g_espClient;
static PubSubClient g_mqttClient(g_espClient);

// ============================================================================
// FORWARD DECLARATIONS
// ============================================================================
static void publishTelemetry();
static void publishAlarmEvent(float ppm, bool isCritical);
static void publishStatusAck(const char* cmd, const char* result, const char* detail);
static void publishAuthRequest();
static void publishKeepAlive();
static void mqttCallback(char* topic, byte* payload, unsigned int length);

// ============================================================================
// UPLINK MESSAGING HELPERS
// ============================================================================
static void publishTelemetry() {
  if (!g_mqttClient.connected()) return;

  char payload[256];
  snprintf(payload, sizeof(payload),
    "{\"device_id\":\"ESP32_Smoke_Nhom04\",\"uptime_s\":%lu,\"mq2_ppm\":%.1f,\"temp\":%.1f,\"hum\":%.1f,\"fan\":\"%s\",\"buzzer\":\"%s\",\"mode\":\"%s\",\"fsm_state\":\"%s\"}",
    millis() / 1000,
    g_currentPPM,
    g_currentTemp,
    g_currentHum,
    g_fsm.fanState ? "ON" : "OFF",
    g_fsm.isBuzzerActive ? "ON" : "OFF",
    (g_fsm.mode == MODE_AUTO) ? "AUTO" : "MANUAL",
    getFsmStateString(g_fsm.currentState)
  );

  g_mqttClient.publish(TOPIC_TELEMETRY, payload);
  g_mqttClient.publish(TOPIC_V2_TELEMETRY, payload);
  Serial.println(F("  [MQTT UPLINK] -> smoke/telemetry (QoS 0) [OK]"));
}

static void publishAlarmEvent(float ppm, bool isCritical) {
  if (!g_mqttClient.connected()) return;

  char payload[256];
  if (isCritical) {
    snprintf(payload, sizeof(payload),
      "{\"device_id\":\"ESP32_Smoke_Nhom04\",\"event\":\"SMOKE_ALERT\",\"severity\":\"CRITICAL\",\"ppm\":%.1f,\"threshold\":%.1f,\"msg\":\"CANH BAO: Khoi vuot nguong! Coi va Quat da bat!\"}",
      ppm, g_cfg.alarmThreshold
    );
  } else {
    snprintf(payload, sizeof(payload),
      "{\"device_id\":\"ESP32_Smoke_Nhom04\",\"event\":\"SMOKE_SAFE\",\"severity\":\"NORMAL\",\"ppm\":%.1f,\"msg\":\"AN TOAN: Nong do khoi da ve muc an toan. Bat dau Purge 30s.\"}",
      ppm
    );
  }

  g_mqttClient.publish(TOPIC_EVENT_ALARM, payload);
  g_mqttClient.publish(TOPIC_V2_ALARM, payload);
  Serial.println(F("  [MQTT EVENT]  -> smoke/event/alarm (CRITICAL ALARM) [SENT]"));
}

static void publishStatusAck(const char* cmd, const char* result, const char* detail) {
  if (!g_mqttClient.connected()) return;

  char payload[256];
  snprintf(payload, sizeof(payload),
    "{\"device_id\":\"ESP32_Smoke_Nhom04\",\"cmd\":\"%s\",\"result\":\"%s\",\"detail\":\"%s\",\"fan\":\"%s\",\"mode\":\"%s\"}",
    cmd, result, detail,
    g_fsm.fanState ? "ON" : "OFF",
    (g_fsm.mode == MODE_AUTO) ? "AUTO" : "MANUAL"
  );

  g_mqttClient.publish(TOPIC_STATUS, payload);
  g_mqttClient.publish(TOPIC_V2_STATUS, payload);
  Serial.print(F("  [MQTT STATUS] -> smoke/status (ACK: "));
  Serial.print(result);
  Serial.println(F(") [SENT]"));
}

static void publishAuthRequest() {
  if (!g_mqttClient.connected()) return;

  char payload[256];
  snprintf(payload, sizeof(payload),
    "{\"msg_id\":\"REQ-AUTH-%04lu\",\"device_id\":\"%s\",\"mac_address\":\"%s\",\"secret_token\":\"HUIT_IOT_SECURE_TOKEN_N04\",\"timestamp\":%lu}",
    millis() / 1000,
    g_clientId,
    g_macAddress,
    millis() / 1000
  );

  g_mqttClient.publish(TOPIC_V2_AUTH_REQ, payload, 1);
  Serial.print(F("  [MQTT AUTH REQ] -> "));
  Serial.print(TOPIC_V2_AUTH_REQ);
  Serial.println(F(" [SENT]"));
}

static void publishKeepAlive() {
  if (!g_mqttClient.connected()) return;

  char payload[256];
  snprintf(payload, sizeof(payload),
    "{\"session_key\":\"%s\",\"device_id\":\"%s\",\"uptime_sec\":%lu,\"free_heap_bytes\":%u,\"wifi_rssi_dbm\":%d,\"status\":\"%s\",\"fsm_state\":\"%s\"}",
    g_sessionKey,
    g_clientId,
    millis() / 1000,
    ESP.getFreeHeap(),
    WiFi.RSSI(),
    (g_fsm.currentState == STATE_FAULT) ? "FAULT" : "HEALTHY",
    getFsmStateString(g_fsm.currentState)
  );

  g_mqttClient.publish(TOPIC_KEEP_ALIVE_V1, payload);
  g_mqttClient.publish(TOPIC_V2_KEEP_ALIVE, payload);
  Serial.print(F("  [MQTT HEARTBEAT] -> Alive (Heap: "));
  Serial.print(ESP.getFreeHeap());
  Serial.println(F(" bytes) [SENT]"));
}

// ============================================================================
// DOWNLINK COMMAND HANDLERS (CLEAN SRP)
// ============================================================================
static void handleAuthResponse(const char* message) {
  JsonDocument doc;
  if (deserializeJson(doc, message)) return;

  const char* status = doc["status"] | "REJECTED";
  if (strcmp(status, "PASS") == 0) {
    const char* sk = doc["session_key"] | "SK_AUTHORIZED_N04";
    strncpy(g_sessionKey, sk, sizeof(g_sessionKey) - 1);
    g_sessionKey[sizeof(g_sessionKey) - 1] = '\0';
    Serial.println(F("Ket qua : [AUTH PASS] Server chap thuan thiet bi!"));

    if (doc["config"]["alarm_threshold_ppm"]) {
      g_cfg.alarmThreshold = doc["config"]["alarm_threshold_ppm"];
      Serial.print(F("Dong bo : Nguong bao dong tu Server = "));
      Serial.print(g_cfg.alarmThreshold, 1);
      Serial.println(F(" PPM"));
    }
  } else {
    Serial.println(F("Ket qua : [AUTH REJECTED] Server tu choi xac thuc thiet bi!"));
  }
}

static void handleFanCommand(const char* message) {
  if (strstr(message, "OFF") != nullptr) {
    if (g_currentPPM >= g_cfg.alarmThreshold) {
      Serial.println(F("Ket qua : TU CHOI! [PCCC Interlock] Khoi dang nguy hiem, duy tri quat!"));
      publishStatusAck("cmd_fan_off", "REJECTED_SAFETY_LOCK", "PPM >= Threshold");
      return;
    }
    g_fsm.manualFanState = false;
    g_fsm.mode = MODE_MANUAL;
    setActuatorFan(g_fsm, false);
    Serial.println(F("Ket qua : CHAP NHAN -> TAT QUAT (MODE_MANUAL)"));
    publishStatusAck("cmd_fan_off", "ACCEPTED", "FAN_IS_OFF");
    return;
  }

  if (strstr(message, "ON") != nullptr) {
    g_fsm.manualFanState = true;
    g_fsm.mode = MODE_MANUAL;
    setActuatorFan(g_fsm, true);
    Serial.println(F("Ket qua : CHAP NHAN -> BAT QUAT (MODE_MANUAL)"));
    publishStatusAck("cmd_fan_on", "ACCEPTED", "FAN_IS_ON");
    return;
  }

  if (strstr(message, "AUTO") != nullptr) {
    g_fsm.mode = MODE_AUTO;
    Serial.println(F("Ket qua : CHAP NHAN -> Chuyen ve TU DONG (MODE_AUTO)"));
    if (g_currentPPM >= g_cfg.alarmThreshold) setActuatorFan(g_fsm, true);
    else if (g_currentPPM <= g_cfg.safeThreshold) setActuatorFan(g_fsm, false);
    publishStatusAck("cmd_fan_auto", "ACCEPTED", "MODE_AUTO_ACTIVE");
  }
}

static void handleBuzzerCommand(const char* message) {
  if (strstr(message, "UNMUTE") != nullptr) {
    g_fsm.isMuted = false;
    if (g_fsm.autoOverrideActive) setActuatorBuzzer(g_fsm, true);
    Serial.println(F("Ket qua : CHAP NHAN -> Da huy Mute coi"));
    publishStatusAck("cmd_buzzer_unmute", "ACCEPTED", "UNMUTED");
    return;
  }

  if (strstr(message, "MUTE") != nullptr || strstr(message, "OFF") != nullptr) {
    g_fsm.isMuted = true;
    g_fsm.muteStartTime = millis();
    g_fsm.muteDurationMs = MUTE_DURATION_MS;
    setActuatorBuzzer(g_fsm, false);
    Serial.println(F("Ket qua : CHAP NHAN -> Da MUTE/TAT coi trong 180s"));
    publishStatusAck("cmd_buzzer_mute", "ACCEPTED", "MUTED_FOR_180S");
    return;
  }

  if (strstr(message, "TEST") != nullptr || strstr(message, "ON") != nullptr) {
    Serial.println(F("Ket qua : CHAP NHAN -> Kiem tra coi bao (Test Beep 0.5s)"));
    ledcWriteTone(BUZZER_LEDC_CH, BUZZER_TONE_TEST_HZ);
    ledcWrite(BUZZER_LEDC_CH, BUZZER_DUTY_50PCT);
    delay(500);
    ledcWrite(BUZZER_LEDC_CH, BUZZER_DUTY_OFF);
    ledcWriteTone(BUZZER_LEDC_CH, 0);
    publishStatusAck("cmd_buzzer_test", "ACCEPTED", "BEEP_TESTED");
  }
}

static void handleModeCommand(const char* message) {
  if (strstr(message, "MANUAL") != nullptr) {
    g_fsm.mode = MODE_MANUAL;
    Serial.println(F("Ket qua : CHAP NHAN -> MODE_MANUAL"));
    publishStatusAck("cmd_mode", "ACCEPTED", "MANUAL");
  } else {
    g_fsm.mode = MODE_AUTO;
    Serial.println(F("Ket qua : CHAP NHAN -> MODE_AUTO"));
    publishStatusAck("cmd_mode", "ACCEPTED", "AUTO");
  }
}

static void handleFaultInjection(const char* message) {
  JsonDocument doc;
  if (deserializeJson(doc, message)) return;

  const char* faultType = doc["fault"] | "";
  Serial.print(F("Ket qua : [FAULT INJECTION] Kich hoat kieu: "));
  Serial.println(faultType);

  if (strcasecmp(faultType, "MQ2_DISCONNECT") == 0) {
    g_simFaultMQ2 = true;
    checkSensorHealth(g_currentTemp, g_currentHum, g_simFaultMQ2, g_simFaultDHT, g_health, g_fsm.currentState);
  } else if (strcasecmp(faultType, "DHT_NAN") == 0) {
    g_simFaultDHT = true;
    checkSensorHealth(g_currentTemp, g_currentHum, g_simFaultMQ2, g_simFaultDHT, g_health, g_fsm.currentState);
  } else if (strcasecmp(faultType, "ACTUATOR_FAULT") == 0) {
    g_simFaultActuator = true;
    publishStatusAck("actuator_check", "ACTUATOR_FAULT", "RELAY_RESPONSE_TIMEOUT");
  } else if (strcasecmp(faultType, "CLEAR") == 0 || strcasecmp(faultType, "RESTORE") == 0) {
    g_simFaultMQ2 = false;
    g_simFaultDHT = false;
    g_simFaultActuator = false;
    g_health.mq2Fault = false;
    g_health.dhtFault = false;
    strncpy(g_health.faultCode, "NONE", sizeof(g_health.faultCode));
    g_fsm.currentState = STATE_SAFE;
    Serial.println(F("Ket qua : [FAULT CLEAR] Da xoa moi su co mo phong, he thong ve SAFE"));
    publishStatusAck("fault_clear", "ACCEPTED", "SYSTEM_HEALTHY");
  }
}

static void handleSchedulerCommand(const char* message) {
  JsonDocument doc;
  if (deserializeJson(doc, message)) return;

  const char* schedMode = doc["mode"] | "DAY";
  if (strcasecmp(schedMode, "NIGHT") == 0) {
    g_cfg.alarmThreshold = ALARM_PPM_NIGHT;
    g_cfg.safeThreshold  = SAFE_PPM_NIGHT;
    Serial.println(F("Ket qua : [SCHEDULER] Kich hoat CHE DO BAN DEM (Alarm: 350, Safe: 250 PPM)"));
    publishStatusAck("cmd_scheduler", "ACCEPTED", "NIGHT_MODE_ACTIVE_350PPM");
  } else {
    g_cfg.alarmThreshold = DEFAULT_ALARM_PPM_DAY;
    g_cfg.safeThreshold  = DEFAULT_SAFE_PPM_DAY;
    Serial.println(F("Ket qua : [SCHEDULER] Kich hoat CHE DO BAN NGAY (Alarm: 400, Safe: 300 PPM)"));
    publishStatusAck("cmd_scheduler", "ACCEPTED", "DAY_MODE_ACTIVE_400PPM");
  }
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
    handleAuthResponse(message);
  } else if (strcmp(topic, TOPIC_CMD_FAN) == 0 || strstr(topic, "/cmd/fan") != nullptr) {
    handleFanCommand(message);
  } else if (strcmp(topic, TOPIC_CMD_BUZZER) == 0 || strstr(topic, "/cmd/buzzer") != nullptr) {
    handleBuzzerCommand(message);
  } else if (strcmp(topic, TOPIC_CMD_MODE) == 0 || strstr(topic, "/cmd/mode") != nullptr) {
    handleModeCommand(message);
  } else if (strcmp(topic, TOPIC_CMD_INJECT_FAULT) == 0 || strstr(topic, "/inject_fault") != nullptr) {
    handleFaultInjection(message);
  } else if (strcmp(topic, TOPIC_CMD_SCHEDULER) == 0 || strstr(topic, "/scheduler") != nullptr) {
    handleSchedulerCommand(message);
  }

  Serial.println(F("================================================================\r\n"));
}

// ============================================================================
// HARDWARE PERIPHERALS & NETWORK ORCHESTRATION
// ============================================================================
static void handleManualButton() {
  const bool reading = digitalRead(PIN_BUTTON);
  if (reading != g_lastButtonState) {
    g_lastDebounceTime = millis();
  }

  if ((millis() - g_lastDebounceTime) > DEBOUNCE_DELAY_MS) {
    if (reading != g_stableButtonState) {
      g_stableButtonState = reading;
      if (g_stableButtonState == LOW) {
        if (g_fsm.autoOverrideActive) {
          Serial.println(F("\r\n[BUTTON] >>> BI KHOA! Dang bao dong khoi (PPM >= Nguong), khong the tat quat!"));
          publishStatusAck("button_press", "REJECTED_SAFETY_LOCK", "Danger PPM");
        } else {
          g_fsm.manualFanState = !g_fsm.manualFanState;
          g_fsm.mode = MODE_MANUAL;
          setActuatorFan(g_fsm, g_fsm.manualFanState);
          Serial.print(F("\r\n[BUTTON] >>> Cong tac thu cong: Quat "));
          Serial.println(g_fsm.manualFanState ? F("BAT") : F("TAT"));
          publishStatusAck("button_press", "ACCEPTED", g_fsm.manualFanState ? "FAN_ON" : "FAN_OFF");
        }
      }
    }
  }
  g_lastButtonState = reading;
}

static void maintainNetworkConnection() {
  const unsigned long now = millis();

  // 1. Maintain WiFi
  if (WiFi.status() != WL_CONNECTED) {
    if (now - g_lastWifiRetry >= RECONNECT_INTERVAL_MS) {
      g_lastWifiRetry = now;
      Serial.println(F("[WIFI] Dang ket noi lai WiFi Wokwi-GUEST..."));
      WiFi.begin(WIFI_SSID, WIFI_PASS);
    }
    return;
  }

  // 2. Maintain MQTT
  if (!g_mqttClient.connected()) {
    if (now - g_lastMqttRetry >= RECONNECT_INTERVAL_MS) {
      g_lastMqttRetry = now;
      Serial.print(F("[MQTT] Dang ket noi Broker "));
      Serial.println(MQTT_BROKER);

      const char* lwtMsg = "{\"device_id\":\"ESP32_Smoke_Nhom04\",\"status\":\"offline\"}";
      if (g_mqttClient.connect(g_clientId, TOPIC_LWT, 1, true, lwtMsg)) {
        Serial.println(F("[MQTT] >>> KET NOI BROKER THANH CONG! <<<"));

        const char* onlineMsg = "{\"device_id\":\"ESP32_Smoke_Nhom04\",\"status\":\"online\"}";
        g_mqttClient.publish(TOPIC_LWT, onlineMsg, true);

        g_mqttClient.subscribe("Nhom09/smoke/cmd/#", 1);
        g_mqttClient.subscribe(TOPIC_V2_AUTH_RESP, 1);
        g_mqttClient.subscribe("Nhom09/smoke/v2/+/+/+/+/cmd/#", 1);
        Serial.println(F("[MQTT] Da dang ky LWT va Subscribe topics (QoS 1)\r\n"));

        publishStatusAck("system_online", "READY", "IP_ACQUIRED");
        publishAuthRequest();
        flushOfflineBuffer(g_mqttClient, TOPIC_OFFLINE_SYNC);
      } else {
        Serial.print(F("[MQTT] Ket noi that bai, rc="));
        Serial.print(g_mqttClient.state());
        Serial.println(F(". Thu lai sau 5s..."));
      }
    }
  } else {
    g_mqttClient.loop();
  }
}

// ============================================================================
// ARDUINO SETUP & MAIN LOOP
// ============================================================================
void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println(F("\r\n========================================================"));
  Serial.println(F("  HE THONG BAO KHOI CANH BAO SOM - LEAN & CLEAN FIRMWARE"));
  Serial.println(F("  Nhom 04 - Lop Lap trinh nhung IoT - GVHD: Vo Hoang Hai "));
  Serial.println(F("========================================================"));

  pinMode(PIN_BUTTON, INPUT_PULLUP);

  initFsm(g_fsm);
  initSensors();
  initOfflineBuffer();
  calibrateMQ2(g_cfg, g_r0);

  // Generate unique client ID & MAC string
  snprintf(g_clientId, sizeof(g_clientId), "%s%04X", MQTT_CLIENT_PREFIX, (uint16_t)random(0xffff));
  strncpy(g_macAddress, WiFi.macAddress().c_str(), sizeof(g_macAddress) - 1);
  g_macAddress[sizeof(g_macAddress) - 1] = '\0';
  Serial.print(F("[SETUP] Client ID: ")); Serial.println(g_clientId);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  g_mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  g_mqttClient.setCallback(mqttCallback);
  g_mqttClient.setBufferSize(512);

  Serial.println(F("[SETUP] Khoi tao hoan tat. Bat dau giam sat & truyen thong.\r\n"));
}

void loop() {
  const unsigned long now = millis();

  // 1. Maintain Network connectivity (Non-blocking)
  maintainNetworkConnection();

  // 2. Handle manual push button
  handleManualButton();

  // 3. Process mute buzzer timeout
  checkMuteTimer(g_fsm);

  // 4. Poll MQ-2 and evaluate FSM logic
  if (now - g_lastMQ2Time >= g_cfg.intervalMQ2) {
    g_lastMQ2Time = now;
    g_cycleCount++;
    g_currentPPM = readMQ2PPM(g_cfg, g_r0);

    Serial.printf("[#%04lu | T=%3lus] PPM: %5.1f | Nhiet: %4.1f*C | Am: %4.1f%% | Quat: %3s | Coi: %3s | State: %s\r\n",
      g_cycleCount,
      now / 1000,
      g_currentPPM,
      g_currentTemp,
      g_currentHum,
      g_fsm.fanState ? "BAT" : "TAT",
      g_fsm.isBuzzerActive ? "BAT" : "TAT",
      getFsmStateString(g_fsm.currentState)
    );

    // Diagnostics & Health Verification
    checkSensorHealth(g_currentTemp, g_currentHum, g_simFaultMQ2, g_simFaultDHT, g_health, g_fsm.currentState);

    // FSM State transitions & actuator actions
    const SystemState prevState = g_fsm.currentState;
    updateFsmLogic(g_fsm, g_currentPPM, g_cfg);

    if (g_fsm.currentState == STATE_ALARM && prevState != STATE_ALARM) {
      publishAlarmEvent(g_currentPPM, true);
    } else if (g_fsm.currentState == STATE_COOLDOWN && prevState == STATE_ALARM) {
      publishAlarmEvent(g_currentPPM, false);
    }

    // Offline buffer recording if disconnected
    if (!g_mqttClient.connected()) {
      pushOfflineRecord(g_currentPPM, g_currentTemp, g_currentHum, g_fsm.fanState, g_fsm.isBuzzerActive, getFsmStateString(g_fsm.currentState));
    }

    // Publish periodic telemetry
    publishTelemetry();
  }

  // 5. Poll DHT22 temperature & humidity
  if (now - g_lastDHTTime >= g_cfg.intervalDHT) {
    g_lastDHTTime = now;
    float t = 0.0f, h = 0.0f;
    if (readDHT(t, h)) {
      g_currentTemp = t;
      g_currentHum  = h;
    }
  }

  // 6. Dispatch periodic Keep-Alive heartbeat (10s)
  if (now - g_lastKeepAliveTime >= HEARTBEAT_INTERVAL_MS) {
    g_lastKeepAliveTime = now;
    publishKeepAlive();
  }
}
