#include "sensors.h"
#include <DHT.h>
#include <math.h>

static DHT s_dht(PIN_DHT, DHT22);

void initSensors() {
  pinMode(PIN_MQ2, INPUT);
  s_dht.begin();
}

static float getRsFromVoltage(float v_out, float vcc, float rl) {
  if (v_out < 0.05f) v_out = 0.05f;
  if (v_out >= (vcc - 0.02f)) v_out = vcc - 0.03f;
  return rl * (vcc - v_out) / v_out;
}

static float readAverageRs(int numSamples, int delayUs, const SensorConfig& config) {
  long sum = 0;
  for (int i = 0; i < numSamples; i++) {
    sum += analogRead(PIN_MQ2);
    if (delayUs > 1000) delay(delayUs / 1000);
    else delayMicroseconds(delayUs);
  }
  const float avgADC = (float)sum / (float)numSamples;
  const float v_out = (avgADC / 4095.0f) * config.vccSensor;
  return getRsFromVoltage(v_out, config.vccSensor, config.rlKOhm);
}

void calibrateMQ2(SensorConfig& config, float& r0Out) {
  Serial.println(F("\r\n=================================================="));
  Serial.println(F("     HIEU CHUAN 2 DIEM THUC NGHIEM (Wokwi)        "));
  Serial.println(F("=================================================="));

  const float rs1 = MEASURED_RS_AT_CALIB1;
  const float rs2 = MEASURED_RS_AT_CALIB2;

  const float logPPM1 = log10(config.calibPoint1);
  const float logPPM2 = log10(config.calibPoint2);
  const float logRs1  = log10(rs1);
  const float logRs2  = log10(rs2);

  config.curveB = (logPPM2 - logPPM1) / (logRs2 - logRs1);
  config.curveA = config.calibPoint1 / pow(rs1, config.curveB);

  const float targetRatio = pow(config.calibPoint1 / config.curveA, 1.0f / config.curveB);
  r0Out = (targetRatio > 0.001f) ? rs1 / targetRatio : rs1;

  Serial.print(F("[CAL] Curve A = "));
  Serial.print(config.curveA, 6);
  Serial.print(F(" | Curve B = "));
  Serial.print(config.curveB, 6);
  Serial.print(F(" | R0 = "));
  Serial.print(r0Out, 4);
  Serial.println(F(" kOhm"));
  Serial.println(F("==================================================\r\n"));
}

float readMQ2PPM(const SensorConfig& config, float r0) {
  const float rs = readAverageRs(10, 200, config);
  float ratio = rs / r0;
  if (ratio <= 0.001f) ratio = 0.001f;
  const float ppm = config.curveA * pow(ratio, config.curveB);
  return (ppm < 0.0f) ? 0.0f : ppm;
}

bool readDHT(float& tempOut, float& humOut) {
  const float t = s_dht.readTemperature();
  const float h = s_dht.readHumidity();

  if (isnan(t) || isnan(h)) {
    return false;
  }

  tempOut = t;
  humOut = h;
  return true;
}

void checkSensorHealth(
  float currentTemp,
  float currentHum,
  bool simFaultMQ2,
  bool simFaultDHT,
  SensorHealthStatus& healthStatus,
  SystemState& systemState
) {
  // 1. Kiem tra tinh trang cam bien MQ-2 (ADC Out-of-Range)
  const int rawADC = analogRead(PIN_MQ2);
  if (simFaultMQ2 || rawADC < 30 || rawADC > 4080) {
    if (!healthStatus.mq2Fault) {
      healthStatus.mq2Fault = true;
      strncpy(healthStatus.faultCode, "SENSOR_FAULT_MQ2_DISCONNECT", sizeof(healthStatus.faultCode) - 1);
      healthStatus.faultCode[sizeof(healthStatus.faultCode) - 1] = '\0';
      systemState = STATE_FAULT;
      Serial.println(F("\r\n[FAULT] >>> PHAT HIEN SU CO: Cam bien MQ-2 dut day hoac ADC out-of-range! <<<"));
    }
  } else {
    if (healthStatus.mq2Fault && !simFaultDHT) {
      healthStatus.mq2Fault = false;
      strncpy(healthStatus.faultCode, "NONE", sizeof(healthStatus.faultCode) - 1);
      systemState = STATE_SAFE;
      Serial.println(F("\r\n[RECOVERY] >>> Cam bien MQ-2 da ket noi lai binh thuong! <<<"));
    }
  }

  // 2. Kiem tra tinh trang cam bien DHT22 (NaN hoac vuot dai vat ly)
  if (simFaultDHT || isnan(currentTemp) || isnan(currentHum) || currentTemp < -10.0f || currentTemp > 85.0f) {
    if (!healthStatus.dhtFault) {
      healthStatus.dhtFault = true;
      strncpy(healthStatus.faultCode, "SENSOR_FAULT_DHT_NAN", sizeof(healthStatus.faultCode) - 1);
      healthStatus.faultCode[sizeof(healthStatus.faultCode) - 1] = '\0';
      systemState = STATE_FAULT;
      Serial.println(F("\r\n[FAULT] >>> PHAT HIEN SU CO: Cam bien DHT22 bao NaN / Timeout! <<<"));
    }
  } else {
    if (healthStatus.dhtFault && !simFaultMQ2) {
      healthStatus.dhtFault = false;
      if (!healthStatus.mq2Fault) {
        strncpy(healthStatus.faultCode, "NONE", sizeof(healthStatus.faultCode) - 1);
        systemState = STATE_SAFE;
      }
      Serial.println(F("\r\n[RECOVERY] >>> Cam bien DHT22 da khoi phuc doc du lieu! <<<"));
    }
  }
}
