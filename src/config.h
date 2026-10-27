#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

/**
 * @file config.h
 * @brief Tap trung toan bo cau hinh phan cung, tham so mang MQTT va hang so he thong
 * @details De tai 04: He thong bao khoi canh bao som - Nhom 04 (N09)
 *          Tuan thu nguyen tac Clean Code: Zero Magic Numbers, PROGMEM constants.
 */

// ============================================================================
// 1. PIN MAPPING (GPIO ESP32-WROOM-32D)
// ============================================================================
constexpr uint8_t PIN_MQ2        = 34;  ///< ADC1_CH6 - Doc tin hieu analog nong do khoi (12-bit)
constexpr uint8_t PIN_DHT        = 4;   ///< 1-Wire Digital GPIO doc cam bien nhiet am DHT22
constexpr uint8_t PIN_BUZZER     = 16;  ///< Digital Output dieu khien coi chip canh bao (LEDC PWM)
constexpr uint8_t PIN_RELAY      = 17;  ///< Digital Output kich relay dong cat quat hut khoi / LED
constexpr uint8_t PIN_BUTTON     = 18;  ///< Digital Input nut nhan manual (INPUT_PULLUP, active LOW)

// ============================================================================
// 2. ACTUATOR & PWM HARDWARE CONFIGURATION
// ============================================================================
constexpr uint8_t  BUZZER_LEDC_CH       = 0;     ///< Kenh LEDC PWM tren ESP32 cho Coi
constexpr uint32_t BUZZER_PWM_FREQ_HZ   = 2000;  ///< Tan so PWM co ban 2000 Hz
constexpr uint8_t  BUZZER_PWM_RES_BITS  = 8;     ///< Do phan giai 8-bit (0 - 255)
constexpr uint32_t BUZZER_TONE_ALARM_HZ = 800;   ///< Am sac coi bao chay khan cap (800 Hz)
constexpr uint32_t BUZZER_TONE_TEST_HZ  = 1000;  ///< Am sac kiem tra test coi (1000 Hz)
constexpr uint32_t BUZZER_DUTY_50PCT    = 128;   ///< 50% duty cycle kich am thanh toi uu
constexpr uint32_t BUZZER_DUTY_OFF      = 0;     ///< 0% duty cycle ngat am thanh

// ============================================================================
// 3. NETWORK & BROKER CONFIGURATION
// ============================================================================
constexpr const char* WIFI_SSID          = "Wokwi-GUEST";
constexpr const char* WIFI_PASS          = "";
constexpr const char* MQTT_BROKER        = "broker.emqx.io";
constexpr uint16_t    MQTT_PORT          = 1883;
constexpr const char* MQTT_CLIENT_PREFIX = "ESP32_Smoke_Nhom04_";

// ============================================================================
// 4. MQTT TOPICS REGISTRY (NHOM09 ENTERPRISE ISOLATION)
// ============================================================================
// V1 Legacy & Standard Topics
constexpr const char* TOPIC_TELEMETRY        = "Nhom09/smoke/telemetry";
constexpr const char* TOPIC_EVENT_ALARM      = "Nhom09/smoke/event/alarm";
constexpr const char* TOPIC_STATUS           = "Nhom09/smoke/status";
constexpr const char* TOPIC_CMD_FAN          = "Nhom09/smoke/cmd/fan";
constexpr const char* TOPIC_CMD_BUZZER       = "Nhom09/smoke/cmd/buzzer";
constexpr const char* TOPIC_CMD_MODE         = "Nhom09/smoke/cmd/mode";
constexpr const char* TOPIC_LWT              = "Nhom09/smoke/lwt";
constexpr const char* TOPIC_CMD_INJECT_FAULT = "Nhom09/smoke/cmd/inject_fault";
constexpr const char* TOPIC_CMD_SCHEDULER    = "Nhom09/smoke/cmd/scheduler";
constexpr const char* TOPIC_OFFLINE_SYNC     = "Nhom09/smoke/history/sync";
constexpr const char* TOPIC_KEEP_ALIVE_V1    = "Nhom09/smoke/keep_alive";

// V2 Enterprise Hierarchy (Slide 65 - ThS. Vo Hoang Hai)
constexpr const char* TOPIC_V2_AUTH_REQ      = "Nhom09/smoke/v2/auth/request";
constexpr const char* TOPIC_V2_AUTH_RESP     = "Nhom09/smoke/v2/auth/response/#";
constexpr const char* TOPIC_V2_TELEMETRY     = "Nhom09/smoke/v2/HUIT_A/F03/P302/ESP32_SMOKE_N04_A01/telemetry";
constexpr const char* TOPIC_V2_ALARM         = "Nhom09/smoke/v2/HUIT_A/F03/P302/ESP32_SMOKE_N04_A01/event/alarm";
constexpr const char* TOPIC_V2_KEEP_ALIVE    = "Nhom09/smoke/v2/HUIT_A/F03/P302/ESP32_SMOKE_N04_A01/keep_alive";
constexpr const char* TOPIC_V2_STATUS        = "Nhom09/smoke/v2/HUIT_A/F03/P302/ESP32_SMOKE_N04_A01/status";

// ============================================================================
// 5. TIMING CONSTANTS (IN MILLISECONDS)
// ============================================================================
constexpr unsigned long SENSOR_POLL_INTERVAL_MS = 2000;   ///< Chu ky doc MQ-2 & publish telemetry
constexpr unsigned long DHT_POLL_INTERVAL_MS    = 5000;   ///< Chu ky doc DHT22
constexpr unsigned long HEARTBEAT_INTERVAL_MS   = 10000;  ///< Chu ky gui Keep-Alive (10s theo Slide 65)
constexpr unsigned long COOLDOWN_PURGE_MS       = 30000;  ///< Chu ky thong gio cuong buc 30s sau bao dong
constexpr unsigned long DEBOUNCE_DELAY_MS       = 50;     ///< Chong rung phim nut bam 50ms
constexpr unsigned long RECONNECT_INTERVAL_MS   = 5000;   ///< Khoang thoi gian thu lai ket noi non-blocking
constexpr unsigned long MUTE_DURATION_MS        = 180000; ///< Thoi gian tam ngat chuong khi co lenh mute (3 phut)

// ============================================================================
// 6. CALIBRATION & THRESHOLD CONSTANTS
// ============================================================================
constexpr float MEASURED_RS_AT_CALIB1 = 1.7100f;  ///< Dien tro cam bien kOhm tai 200 PPM (Wokwi)
constexpr float MEASURED_RS_AT_CALIB2 = 0.8852f;  ///< Dien tro cam bien kOhm tai 1000 PPM (Wokwi)
constexpr float DEFAULT_ALARM_PPM_DAY = 400.0f;   ///< Nguong bao chay ban ngay (PCCC quy chuan)
constexpr float DEFAULT_SAFE_PPM_DAY  = 300.0f;   ///< Nguong an toan khoi ban ngay
constexpr float ALARM_PPM_NIGHT       = 350.0f;   ///< Nguong bao chay ban dem (nhay hon vi it hoat dong)
constexpr float SAFE_PPM_NIGHT        = 250.0f;   ///< Nguong an toan ban dem

// ============================================================================
// 7. SYSTEM ENUMS & DATA STRUCTURES
// ============================================================================
enum SystemMode : uint8_t {
  MODE_AUTO   = 0,
  MODE_MANUAL = 1
};

enum SystemState : uint8_t {
  STATE_SAFE     = 0,
  STATE_WARNING  = 1,
  STATE_ALARM    = 2,
  STATE_COOLDOWN = 3,
  STATE_FAULT    = 4,
  STATE_OFFLINE  = 5
};

struct SensorConfig {
  float vccSensor;
  float rlKOhm;
  float curveA;
  float curveB;
  float alarmThreshold;
  float safeThreshold;
  float calibPoint1;
  float calibPoint2;
  unsigned long intervalMQ2;
  unsigned long intervalDHT;
};

#endif // CONFIG_H
