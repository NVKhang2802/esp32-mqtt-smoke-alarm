#include "fsm_core.h"

static bool reached(uint32_t now, uint32_t t) {
    return (int32_t)(now - t) >= 0;
}

static FsmOutput out(const FsmContext& c, bool forceFan, BuzzerMode m) {
    FsmOutput o;
    o.fanOn = forceFan || (c.manualMode && c.manualFan);
    o.buzzerMuted = c.muted && m != BUZZ_OFF;
    o.buzzer = o.buzzerMuted ? BUZZ_OFF : m;
    return o;
}

FsmOutput fsmStep(FsmContext& c, const FsmInput& in, const Thresholds& th) {
    if (c.muted && reached(in.nowMs, c.muteUntilMs)) {
        c.muted = false;
    }

    // 1. Đang chốt ALARM: giữ tới khi khói <= safe; mất cảm biến vẫn giữ ALARM
    if (c.alarmLatched) {
        if (in.mq2Fault || in.ppm > th.safe) {
            c.state = STATE_ALARM;
            return out(c, true, BUZZ_ALARM);
        }
        c.alarmLatched = false;
        c.cooldownActive = true;
        c.cooldownStartMs = in.nowMs;
        c.state = STATE_COOLDOWN;
        return out(c, true, BUZZ_OFF);
    }

    // 2. Vào ALARM (chỉ khi MQ-2 hợp lệ). Xóa mute CHỈ ở cạnh vào ALARM
    if (!in.mq2Fault && in.ppm >= th.alarm) {
        c.alarmLatched = true;
        c.cooldownActive = false;
        c.muted = false; // Xóa mute ở cạnh vào ALARM
        c.state = STATE_ALARM;
        return out(c, true, BUZZ_ALARM);
    }

    // 3. Lỗi MQ-2 (chưa ALARM): fail-safe (quạt bật, còi beep lỗi)
    if (in.mq2Fault) {
        c.cooldownActive = false;
        c.state = STATE_FAULT;
        return out(c, true, BUZZ_FAULT_BEEP);
    }

    // 4. Cooldown 30s sau khi hạ khói
    if (c.cooldownActive) {
        if (in.nowMs - c.cooldownStartMs < COOLDOWN_MS) {
            c.state = STATE_COOLDOWN;
            return out(c, true, BUZZ_OFF);
        }
        c.cooldownActive = false;
    }

    // 5. WARNING / SAFE
    c.state = (in.ppm > th.safe || in.dhtFault) ? STATE_WARNING : STATE_SAFE;
    return out(c, false, BUZZ_OFF);
}
