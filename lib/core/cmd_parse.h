#ifndef CMD_PARSE_H
#define CMD_PARSE_H

#include <string.h>
#include "fsm_core.h"

/**
 * @file cmd_parse.h
 * @brief Bo phan giai lenh chap hanh doc lap phan cung va khoa an toan PCCC
 * @details Dung chung cho Firmware ESP32 (src/main.cpp) va bo kiem thu Native Unity (test/test_core.cpp)
 */

enum ActionAck : uint8_t {
    ACTION_ACCEPTED,
    ACTION_SAFETY_LOCK,
    ACTION_UNKNOWN
};

inline ActionAck applyFanAction(FsmContext& ctx, const char* action) {
    if (!action) return ACTION_UNKNOWN;
    if (strcmp(action, "OFF") == 0) {
        CmdResult cr = cmdRemoteFanOff(ctx);
        return (cr == CMD_OK) ? ACTION_ACCEPTED : ACTION_SAFETY_LOCK;
    } else if (strcmp(action, "ON") == 0) {
        cmdRemoteFanOn(ctx);
        return ACTION_ACCEPTED;
    } else if (strcmp(action, "AUTO") == 0) {
        cmdFanAuto(ctx);
        return ACTION_ACCEPTED;
    }
    return ACTION_UNKNOWN;
}

inline ActionAck applyBuzzerAction(FsmContext& ctx, const char* action, uint32_t now) {
    if (!action) return ACTION_UNKNOWN;
    if (strcmp(action, "MUTE") == 0 || strcmp(action, "OFF") == 0) {
        CmdResult cr = cmdRemoteMute(ctx, now);
        return (cr == CMD_OK) ? ACTION_ACCEPTED : ACTION_SAFETY_LOCK;
    } else if (strcmp(action, "UNMUTE") == 0) {
        cmdRemoteUnmute(ctx);
        return ACTION_ACCEPTED;
    } else if (strcmp(action, "TEST") == 0 || strcmp(action, "ON") == 0) {
        CmdResult cr = cmdBuzzerTest(ctx);
        return (cr == CMD_OK) ? ACTION_ACCEPTED : ACTION_SAFETY_LOCK;
    }
    return ACTION_UNKNOWN;
}

#endif // CMD_PARSE_H
