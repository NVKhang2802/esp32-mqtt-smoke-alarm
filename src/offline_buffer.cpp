#include "offline_buffer.h"

static RingBuffer<OfflineRecord, OFFLINE_BUF_SIZE> s_ringBuffer;

void initOfflineBuffer() {
  s_ringBuffer.clear();
}

void pushOfflineRecord(float ppm, float temp, float hum, bool fan, bool buzzer, const char* stateStr, const char* eventType, bool mq2Valid, bool dhtValid) {
  OfflineRecord rec = {};
  rec.timestamp = millis() / 1000;
  rec.ppm = ppm;
  rec.temp = temp;
  rec.hum = hum;
  rec.fan = fan;
  rec.buzzer = buzzer;
  rec.mq2Valid = mq2Valid;
  rec.dhtValid = dhtValid;

  if (stateStr != nullptr) {
    strncpy(rec.state, stateStr, sizeof(rec.state) - 1);
  } else {
    strncpy(rec.state, "UNKNOWN", sizeof(rec.state) - 1);
  }
  rec.state[sizeof(rec.state) - 1] = '\0';

  if (eventType != nullptr) {
    strncpy(rec.eventType, eventType, sizeof(rec.eventType) - 1);
  } else {
    strncpy(rec.eventType, "TELEMETRY", sizeof(rec.eventType) - 1);
  }
  rec.eventType[sizeof(rec.eventType) - 1] = '\0';

  s_ringBuffer.push(rec);
}

void flushOfflineBuffer(PubSubClient& client, const char* topic, int maxBatch) {
  if (s_ringBuffer.empty() || !client.connected() || topic == nullptr) {
    return;
  }

  const size_t toSend = (s_ringBuffer.size() < (size_t)maxBatch) ? s_ringBuffer.size() : (size_t)maxBatch;
  char payload[256];
  size_t successfullySent = 0;

  for (size_t idx = 0; idx < toSend; idx++) {
    const OfflineRecord& rec = s_ringBuffer.getOldest(idx);
    snprintf(payload, sizeof(payload),
      "{\"sync_seq\":%zu,\"ts\":%lu,\"type\":\"%s\",\"mq2_ppm\":%.1f,\"temp\":%.1f,\"hum\":%.1f,\"fan\":\"%s\",\"buzzer\":\"%s\",\"state\":\"%s\",\"mq2_valid\":%s,\"dht_valid\":%s}",
      idx + 1,
      rec.timestamp,
      rec.eventType,
      rec.ppm,
      rec.temp,
      rec.hum,
      rec.fan ? "ON" : "OFF",
      rec.buzzer ? "ON" : "OFF",
      rec.state,
      rec.mq2Valid ? "true" : "false",
      rec.dhtValid ? "true" : "false"
    );

    if (!client.publish(topic, payload)) {
      // If publish failed, stop immediately and preserve remaining records
      break;
    }
    successfullySent++;
    delay(20);
  }

  s_ringBuffer.drop(successfullySent);
  if (successfullySent > 0) {
    Serial.printf("[OFFLINE BUFFER] Da dong bo %zu ban ghi. Con lai trong dem: %zu\r\n", successfullySent, s_ringBuffer.size());
  }
}

int getOfflineBufferCount() {
  return static_cast<int>(s_ringBuffer.size());
}
