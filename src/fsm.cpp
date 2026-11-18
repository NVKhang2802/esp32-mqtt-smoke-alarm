#include "fsm.h"

static bool s_on = false;
static uint32_t s_freq = 0;
static uint32_t s_testEnd = 0;
static bool s_curFan = false;

void initActuators() {
  pinMode(PIN_RELAY, OUTPUT);
  digitalWrite(PIN_RELAY, LOW);

  ledcSetup(BUZZER_LEDC_CH, BUZZER_PWM_FREQ_HZ, BUZZER_PWM_RES_BITS);
  ledcAttachPin(PIN_BUZZER, BUZZER_LEDC_CH);
  ledcWrite(BUZZER_LEDC_CH, BUZZER_DUTY_OFF);
  ledcWriteTone(BUZZER_LEDC_CH, 0);
}

void fanApply(bool on) {
  if (on != s_curFan) {
    s_curFan = on;
    digitalWrite(PIN_RELAY, on ? HIGH : LOW);
  }
}

void buzzerTest(uint32_t now) {
  s_testEnd = now + 500;
}

void buzzerTick(BuzzerMode mode, uint32_t now) {
  BuzzerCmd c = buzzerPattern(mode, now);
  if (s_testEnd) {
    if ((int32_t)(now - s_testEnd) < 0) {
      c = { true, BUZZER_TONE_TEST_HZ };
    } else {
      s_testEnd = 0;
    }
  }

  if (c.on == s_on && (!c.on || c.freqHz == s_freq)) return; // chi ghi khi doi trang thai
  s_on = c.on;
  s_freq = c.freqHz;

  if (c.on) {
    ledcWriteTone(BUZZER_LEDC_CH, c.freqHz);
    ledcWrite(BUZZER_LEDC_CH, BUZZER_DUTY_50PCT);
  } else {
    ledcWrite(BUZZER_LEDC_CH, BUZZER_DUTY_OFF);
    ledcWriteTone(BUZZER_LEDC_CH, 0);
  }
}

const char* getFsmStateString(SystemState state) {
  switch (state) {
    case STATE_ALARM:    return "ALARM";
    case STATE_COOLDOWN: return "COOLDOWN";
    case STATE_FAULT:    return "FAULT";
    case STATE_WARNING:  return "WARNING";
    case STATE_SAFE:
    default:             return "SAFE";
  }
}
