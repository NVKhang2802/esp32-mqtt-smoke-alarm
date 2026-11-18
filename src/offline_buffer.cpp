#include "offline_buffer.h"

static OfflineRecord s_offlineBuffer[OFFLINE_BUF_SIZE];
static int s_offlineHead = 0;
static int s_offlineCount = 0;

void initOfflineBuffer() {
  s_offlineHead = 0;
  s_offlineCount = 0;
  memset(s_offlineBuffer, 0, sizeof(s_offlineBuffer));
}

void pushOfflineRecord(float ppm, float temp, float hum, bool fan, bool buzzer, const char* stateStr, const char* eventType) {
  s_offlineBuffer[s_offlineHead].timestamp = millis() / 1000;
  s_offlineBuffer[s_offlineHead].ppm = ppm;
  s_offlineBuffer[s_offlineHead].temp = temp;
  s_offlineBuffer[s_offlineHead].hum = hum;
  s_offlineBuffer[s_offlineHead].fan = fan;
  s_offlineBuffer[s_offlineHead].buzzer = buzzer;

  if (stateStr != nullptr) {
    strncpy(s_offlineBuffer[s_offlineHead].state, stateStr, sizeof(s_offlineBuffer[s_offlineHead].state) - 1);
    s_offlineBuffer[s_offlineHead].state[sizeof(s_offlineBuffer[s_offlineHead].state) - 1] = '\0';
  } else {
    strncpy(s_offlineBuffer[s_offlineHead].state, "UNKNOWN", sizeof(s_offlineBuffer[s_offlineHead].state) - 1);
  }

  if (eventType != nullptr) {
    strncpy(s_offlineBuffer[s_offlineHead].eventType, eventType, sizeof(s_offlineBuffer[s_offlineHead].eventType) - 1);
    s_offlineBuffer[s_offlineHead].eventType[sizeof(s_offlineBuffer[s_offlineHead].eventType) - 1] = '\0';
  } else {
    strncpy(s_offlineBuffer[s_offlineHead].eventType, "TELEMETRY", sizeof(s_offlineBuffer[s_offlineHead].eventType) - 1);
  }

  s_offlineHead = (s_offlineHead + 1) % OFFLINE_BUF_SIZE;
  if (s_offlineCount < (int)OFFLINE_BUF_SIZE) {
    s_offlineCount++;
  }
}

void flushOfflineBuffer(PubSubClient& client, const char* topic, int maxBatch) {
  if (s_offlineCount == 0 || !client.connected() || topic == nullptr) {
    return;
  }

  const int toSend = (s_offlineCount < maxBatch) ? s_offlineCount : maxBatch;
  const int startIdx = (s_offlineHead - s_offlineCount + OFFLINE_BUF_SIZE) % OFFLINE_BUF_SIZE;
  char payload[256];
  int successfullySent = 0;

  for (int idx = 0; idx < toSend; idx++) {
    const int cur = (startIdx + idx) % OFFLINE_BUF_SIZE;
    snprintf(payload, sizeof(payload),
      "{\"sync_seq\":%d,\"ts\":%lu,\"type\":\"%s\",\"mq2_ppm\":%.1f,\"temp\":%.1f,\"hum\":%.1f,\"fan\":\"%s\",\"buzzer\":\"%s\",\"state\":\"%s\"}",
      idx + 1,
      s_offlineBuffer[cur].timestamp,
      s_offlineBuffer[cur].eventType,
      s_offlineBuffer[cur].ppm,
      s_offlineBuffer[cur].temp,
      s_offlineBuffer[cur].hum,
      s_offlineBuffer[cur].fan ? "ON" : "OFF",
      s_offlineBuffer[cur].buzzer ? "ON" : "OFF",
      s_offlineBuffer[cur].state
    );

    if (!client.publish(topic, payload)) {
      // If publish failed, stop immediately and preserve remaining records
      break;
    }
    successfullySent++;
    delay(20);
  }

  s_offlineCount -= successfullySent;
  if (successfullySent > 0) {
    Serial.printf("[OFFLINE BUFFER] Da dong bo %d ban ghi. Con lai trong dem: %d\r\n", successfullySent, s_offlineCount);
  }
}

int getOfflineBufferCount() {
  return s_offlineCount;
}
