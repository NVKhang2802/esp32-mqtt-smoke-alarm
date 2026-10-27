#ifndef FSM_H
#define FSM_H

#include <Arduino.h>
#include "config.h"

/**
 * @file fsm.h
 * @brief Finite State Machine quan ly 6 trang thai he thong & logic dieu khien chap hanh
 */

struct FsmContext {
  SystemState currentState;
  SystemMode  mode;
  bool        autoOverrideActive;
  bool        inCooldownPurge;
  unsigned long cooldownStartTime;
  bool        isBuzzerActive;
  bool        isMuted;
  unsigned long muteStartTime;
  unsigned long muteDurationMs;
  bool        fanState;
  bool        manualFanState;
};

void initFsm(FsmContext& ctx);
void setActuatorBuzzer(FsmContext& ctx, bool state);
void setActuatorFan(FsmContext& ctx, bool state);
void updateFsmLogic(FsmContext& ctx, float currentPPM, const SensorConfig& cfg);
void checkMuteTimer(FsmContext& ctx);
const char* getFsmStateString(SystemState state);

#endif // FSM_H
