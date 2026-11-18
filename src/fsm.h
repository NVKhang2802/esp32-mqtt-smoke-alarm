#ifndef FSM_H
#define FSM_H

#include <Arduino.h>
#include "config.h"

void initActuators();
void fanApply(bool on);
void buzzerTick(BuzzerMode mode, uint32_t now);
void buzzerTest(uint32_t now);
const char* getFsmStateString(SystemState state);

#endif // FSM_H
