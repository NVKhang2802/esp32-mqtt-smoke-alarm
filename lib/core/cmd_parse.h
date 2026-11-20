#ifndef CMD_PARSE_H
#define CMD_PARSE_H

#include <string.h>
#include <stdint.h>
#include "fsm_core.h"

/**
 * @file cmd_parse.h
 * @brief Bo phan giai lenh chap hanh doc lap phan cung va khoa an toan PCCC
 * @details Dung chung cho Firmware ESP32 (src/main.cpp) va bo kiem thu Native Unity (test/test_core.cpp)
 *          Ho tro so sanh khong phan biet hoa thuong (Case-Insensitive) cho moi lenh chap hanh.
 */

enum ActionAck : uint8_t {
    ACTION_ACCEPTED,
    ACTION_SAFETY_LOCK,
    ACTION_UNKNOWN
};

inline bool strEqualsIgnoreCase(const char* s1, const char* s2) {
    if (!s1 || !s2) return false;
    while (*s1 && *s2) {
        char c1 = (*s1 >= 'a' && *s1 <= 'z') ? (char)(*s1 - 32) : *s1;
        char c2 = (*s2 >= 'a' && *s2 <= 'z') ? (char)(*s2 - 32) : *s2;
        if (c1 != c2) return false;
        s1++;
        s2++;
    }
    return (*s1 == '\0' && *s2 == '\0');
}

inline ActionAck applyFanAction(FsmContext& ctx, const char* action) {
    if (!action) return ACTION_UNKNOWN;
    if (strEqualsIgnoreCase(action, "OFF")) {
        CmdResult cr = cmdRemoteFanOff(ctx);
        return (cr == CMD_OK) ? ACTION_ACCEPTED : ACTION_SAFETY_LOCK;
    } else if (strEqualsIgnoreCase(action, "ON")) {
        cmdRemoteFanOn(ctx);
        return ACTION_ACCEPTED;
    } else if (strEqualsIgnoreCase(action, "AUTO")) {
        cmdFanAuto(ctx);
        return ACTION_ACCEPTED;
    }
    return ACTION_UNKNOWN;
}

inline ActionAck applyBuzzerAction(FsmContext& ctx, const char* action, uint32_t now) {
    if (!action) return ACTION_UNKNOWN;
    if (strEqualsIgnoreCase(action, "MUTE") || strEqualsIgnoreCase(action, "OFF")) {
        CmdResult cr = cmdRemoteMute(ctx, now);
        return (cr == CMD_OK) ? ACTION_ACCEPTED : ACTION_SAFETY_LOCK;
    } else if (strEqualsIgnoreCase(action, "UNMUTE")) {
        cmdRemoteUnmute(ctx);
        return ACTION_ACCEPTED;
    } else if (strEqualsIgnoreCase(action, "TEST") || strEqualsIgnoreCase(action, "ON")) {
        CmdResult cr = cmdBuzzerTest(ctx);
        return (cr == CMD_OK) ? ACTION_ACCEPTED : ACTION_SAFETY_LOCK;
    }
    return ACTION_UNKNOWN;
}

#endif // CMD_PARSE_H
