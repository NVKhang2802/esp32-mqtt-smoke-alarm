#include "fsm.h"

void initFsm(FsmContext& ctx) {
  ctx.currentState        = STATE_SAFE;
  ctx.mode                = MODE_AUTO;
  ctx.autoOverrideActive  = false;
  ctx.inCooldownPurge     = false;
  ctx.cooldownStartTime   = 0;
  ctx.isBuzzerActive      = false;
  ctx.isMuted             = false;
  ctx.muteStartTime       = 0;
  ctx.muteDurationMs      = MUTE_DURATION_MS;
  ctx.fanState            = false;
  ctx.manualFanState      = false;

  pinMode(PIN_RELAY, OUTPUT);
  digitalWrite(PIN_RELAY, LOW);

  ledcSetup(BUZZER_LEDC_CH, BUZZER_PWM_FREQ_HZ, BUZZER_PWM_RES_BITS);
  ledcAttachPin(PIN_BUZZER, BUZZER_LEDC_CH);
  ledcWrite(BUZZER_LEDC_CH, BUZZER_DUTY_OFF);
  ledcWriteTone(BUZZER_LEDC_CH, 0);
}

void setActuatorBuzzer(FsmContext& ctx, bool state) {
  if (state && !ctx.isMuted) {
    if (!ctx.isBuzzerActive) {
      ledcWriteTone(BUZZER_LEDC_CH, BUZZER_TONE_ALARM_HZ);
      ledcWrite(BUZZER_LEDC_CH, BUZZER_DUTY_50PCT);
      ctx.isBuzzerActive = true;
    }
  } else {
    ledcWrite(BUZZER_LEDC_CH, BUZZER_DUTY_OFF);
    ledcWriteTone(BUZZER_LEDC_CH, 0);
    ctx.isBuzzerActive = false;
  }
}

void setActuatorFan(FsmContext& ctx, bool state) {
  ctx.fanState = state;
  digitalWrite(PIN_RELAY, state ? HIGH : LOW);
}

void checkMuteTimer(FsmContext& ctx) {
  if (!ctx.isMuted) return;

  if (millis() - ctx.muteStartTime >= ctx.muteDurationMs) {
    ctx.isMuted = false;
    Serial.println(F("\r\n[TIMER] Het thoi gian Mute. Kich hoat lai coi neu van con khoi."));
    if (ctx.autoOverrideActive) {
      setActuatorBuzzer(ctx, true);
    }
  }
}

void updateFsmLogic(FsmContext& ctx, float currentPPM, const SensorConfig& cfg) {
  // 1. Truong hop Su co Phan cung (Fail-Safe: Quat chay bao ve, coi tat)
  if (ctx.currentState == STATE_FAULT) {
    setActuatorFan(ctx, true);
    setActuatorBuzzer(ctx, false);
    Serial.println(F("  >>> [FAIL-SAFE MODE] Phat hien su co phan cung -> Duy tri quat thong gio an toan! <<<"));
    return;
  }

  // 2. Truong hop Khoi vuot nguong Bao dong (Alarm State)
  if (currentPPM >= cfg.alarmThreshold) {
    ctx.inCooldownPurge = false;
    ctx.currentState = STATE_ALARM;

    if (!ctx.autoOverrideActive) {
      ctx.autoOverrideActive = true;
      Serial.println(F("  >>> [CANH BAO PCCC] PPM >= Nguong -> COI & QUAT BAT CUONG BUC! <<<"));
    }
    setActuatorBuzzer(ctx, true);
    setActuatorFan(ctx, true);
    return;
  }

  // 3. Truong hop Khoi an toan (PPM <= Safe Threshold)
  if (currentPPM <= cfg.safeThreshold) {
    if (ctx.autoOverrideActive) {
      // Chuyen tu ALARM sang COOLDOWN PURGE (Thong gio cuong buc 30s)
      ctx.autoOverrideActive = false;
      ctx.inCooldownPurge = true;
      ctx.cooldownStartTime = millis();
      ctx.currentState = STATE_COOLDOWN;
      setActuatorBuzzer(ctx, false); // Ngat coi ngay khi nong do ha
      setActuatorFan(ctx, true);     // Quat tiep tuc chay 30s
      Serial.println(F("  --- [COOLDOWN PURGE] Khoi da giam ve an toan. Bat dau chay thong gio cuong buc 30s! ---"));
      return;
    }

    if (ctx.inCooldownPurge) {
      if (millis() - ctx.cooldownStartTime >= COOLDOWN_PURGE_MS) {
        ctx.inCooldownPurge = false;
        ctx.currentState = STATE_SAFE;
        const bool fanTarget = (ctx.mode == MODE_AUTO) ? false : ctx.manualFanState;
        setActuatorFan(ctx, fanTarget);
        Serial.println(F("  --- [PURGE HOAN TAT] Het 30s thong gio cuong buc. He thong tro ve SAFE IDLE ---"));
      } else {
        ctx.currentState = STATE_COOLDOWN;
        setActuatorFan(ctx, true);
      }
      return;
    }

    // Trang thai binh thuong (SAFE)
    ctx.currentState = STATE_SAFE;
    setActuatorBuzzer(ctx, false);
    const bool normalFan = (ctx.mode == MODE_AUTO) ? false : ctx.manualFanState;
    setActuatorFan(ctx, normalFan);
  }
}

const char* getFsmStateString(SystemState state) {
  switch (state) {
    case STATE_ALARM:    return "ALARM";
    case STATE_COOLDOWN: return "COOLDOWN";
    case STATE_FAULT:    return "FAULT";
    case STATE_WARNING:  return "WARNING";
    case STATE_OFFLINE:  return "OFFLINE";
    case STATE_SAFE:
    default:             return "SAFE";
  }
}
