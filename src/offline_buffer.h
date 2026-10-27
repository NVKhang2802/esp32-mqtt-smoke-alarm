#ifndef OFFLINE_BUFFER_H
#define OFFLINE_BUFFER_H

#include <Arduino.h>
#include <PubSubClient.h>

/**
 * @file offline_buffer.h
 * @brief Vong dem tinh luu tru ngoai tuyen (Zero-Heap Allocation Circular Buffer)
 * @details Tuan 7: Ghi nho 20 ban ghi telemetry gan nhat khi mat mang va dong bo tu dong len MQTT
 */

constexpr size_t OFFLINE_BUF_SIZE = 20;

struct OfflineRecord {
  unsigned long timestamp;
  float ppm;
  float temp;
  float hum;
  bool fan;
  bool buzzer;
  char state[16];
};

void initOfflineBuffer();
void pushOfflineRecord(float ppm, float temp, float hum, bool fan, bool buzzer, const char* stateStr);
void flushOfflineBuffer(PubSubClient& client, const char* topic);
int getOfflineBufferCount();

#endif // OFFLINE_BUFFER_H
