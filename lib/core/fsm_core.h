#ifndef FSM_CORE_H
#define FSM_CORE_H

#include <stdint.h>
#include "thresholds.h"

enum SystemState : uint8_t {
    STATE_SAFE,
    STATE_WARNING,
    STATE_ALARM,
    STATE_COOLDOWN,
    STATE_FAULT
};

enum BuzzerMode : uint8_t {
    BUZZ_OFF,
    BUZZ_ALARM,
    BUZZ_FAULT_BEEP
};

enum CmdResult : uint8_t {
    CMD_OK,
    CMD_REJECTED_SAFETY_LOCK
};

constexpr uint32_t COOLDOWN_MS = 30000;
constexpr uint32_t LOCAL_ACK_MS = 60000;
constexpr uint32_t REMOTE_MUTE_MS = 180000;

struct FsmContext {
    SystemState state = STATE_SAFE;
    bool alarmLatched = false;
    bool cooldownActive = false;
    uint32_t cooldownStartMs = 0;
    bool muted = false;
    uint32_t muteUntilMs = 0;
    bool manualMode = false; // manualMode=false nghĩa là AUTO
    bool manualFan = false;
};

struct FsmInput {
    float ppm;
    bool mq2Fault;
    bool dhtFault;
    uint32_t nowMs;
};

struct FsmOutput {
    bool fanOn;
    BuzzerMode buzzer;
    bool buzzerMuted;
};

struct BuzzerCmd {
    bool on;
    uint32_t freqHz;
};

FsmOutput fsmStep(FsmContext& c, const FsmInput& in, const Thresholds& th);

inline BuzzerCmd buzzerPattern(BuzzerMode m, uint32_t nowMs) {
    switch (m) {
        case BUZZ_ALARM:      return { true, 800 };
        case BUZZ_FAULT_BEEP: return { (nowMs % 2000) < 200, 1000 };
        default:              return { false, 0 };
    }
}

// Lệnh có interlock (dùng chung cho MQTT và nút bấm)
inline CmdResult cmdRemoteMute(FsmContext& c, uint32_t now) {
    if (c.alarmLatched) return CMD_REJECTED_SAFETY_LOCK;
    c.muted = true;
    c.muteUntilMs = now + REMOTE_MUTE_MS;
    return CMD_OK;
}

inline void cmdRemoteUnmute(FsmContext& c) {
    c.muted = false;
}

inline CmdResult cmdRemoteFanOff(FsmContext& c) {
    if (c.alarmLatched) return CMD_REJECTED_SAFETY_LOCK;
    c.manualMode = true;
    c.manualFan = false;
    return CMD_OK;
}

inline void cmdRemoteFanOn(FsmContext& c) {
    c.manualMode = true;
    c.manualFan = true;
}

inline void cmdFanAuto(FsmContext& c) {
    c.manualMode = false;
    c.manualFan = false;
}

inline CmdResult cmdBuzzerTest(const FsmContext& c) {
    return c.alarmLatched ? CMD_REJECTED_SAFETY_LOCK : CMD_OK;
}

// true = đã xác nhận tại chỗ (tắt còi 60s); false = đã đảo trạng thái quạt
inline bool cmdLocalButton(FsmContext& c, uint32_t now) {
    if (c.alarmLatched || c.state == STATE_FAULT) {
        c.muted = true;
        c.muteUntilMs = now + LOCAL_ACK_MS;
        return true;
    }
    c.manualMode = true;
    c.manualFan = !c.manualFan;
    return false;
}

#endif // FSM_CORE_H
