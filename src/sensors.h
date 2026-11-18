#ifndef SENSORS_H
#define SENSORS_H

#include <Arduino.h>
#include "config.h"

void initSensors();
void calibrateMQ2(SensorConfig& config, float& r0Out);
float readMQ2PPM(const SensorConfig& config, float r0);
inline float readSmokePPM(const SensorConfig& config, float r0) { return readMQ2PPM(config, r0); }
bool readDHT(float& tempOut, float& humOut);

#endif // SENSORS_H
