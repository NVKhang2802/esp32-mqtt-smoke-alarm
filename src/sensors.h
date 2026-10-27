#ifndef SENSORS_H
#define SENSORS_H

#include <Arduino.h>
#include "config.h"

/**
 * @file sensors.h
 * @brief Module truu tuong hoa cam bien MQ-2, DHT22 va chuan doan suc khoe phan cung
 */

void initSensors();
void calibrateMQ2(SensorConfig& config, float& r0Out);
float readMQ2PPM(const SensorConfig& config, float r0);
bool readDHT(float& tempOut, float& humOut);

struct SensorHealthStatus {
  bool mq2Fault;
  bool dhtFault;
  char faultCode[32];
};

void checkSensorHealth(
  float currentTemp,
  float currentHum,
  bool simFaultMQ2,
  bool simFaultDHT,
  SensorHealthStatus& healthStatus,
  SystemState& systemState
);

#endif // SENSORS_H
