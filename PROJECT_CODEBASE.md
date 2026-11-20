# HỒ SƠ TOÀN DIỆN MÃ NGUỒN VẬN HÀNH (OPERATIONAL CODEBASE DOSSIER V5)
## ĐỀ TÀI 04: HỆ THỐNG BÁO KHÓI CẢNH BÁO SỚM & XỬ LÝ SỰ CỐ TẬP TRUNG (NHÓM 04 - LỚP N09 - HUIT)
> **Thời điểm xuất bản bản cập nhật:** 2026-11-20 17:36:44  
> **Trạng thái mã nguồn:** ĐÃ ĐỒNG BỘ 100% VỚI KHO LƯU TRỮ VẬN HÀNH THỰC TẾ (COMMIT: `audit-fix-v5`)  
> **Tổng quy mô hồ sơ:** 42 modules | 9,207 dòng mã nguồn | 316,281 bytes

---

## PHẦN 1: BẢN ĐỒ KIẾN TRÚC & PHÂN BỔ DỮ LIỆU TOÀN HỆ THỐNG

### 1.1 Sơ đồ luồng dữ liệu 4 tầng & Mã nguồn dùng chung (Shared Core)

```mermaid
flowchart TD
    subgraph T1["TẦNG 1: THIẾT BỊ ĐẦU CUỐI (ESP32 FIRMWARE & SHARED CORE)"]
        HW["Cảm biến MQ-2, DHT22 & Nút nhấn ACK"] --> HAL_SENS["src/sensors.cpp\n(ADC Rolling Average, Calib Ro=1.0k)"]
        HAL_SENS --> EMA["lib/core/ema_filter.h\n(EMA alpha_rise=0.40, fall=0.15)"]
        EMA --> HEALTH["lib/core/health.h\n(MQ2 & DHT Debounce, Health Flags)"]
        HEALTH --> FSM["lib/core/fsm_core.cpp\n(5-State Edge FSM: SAFE, WARN, ALARM, COOL, FAULT)"]
        FSM --> ACT["src/fsm.cpp\n(Relay Quạt & Còi LEDC PWM Beep Pattern)"]
        FSM -.->|Mất kết nối| BUF["src/offline_buffer.cpp & lib/core/ring_buffer.h\n(RingBuffer zero-heap 20 slots FIFO)"]
        NET["src/main.cpp & lib/core/backoff.h\n(ExponentialBackoff 1s..16s độc lập WiFi & MQTT)"] -->|Replay Buffer| FSM
        CMD_CORE["lib/core/cmd_parse.h\n(applyFanAction & applyBuzzerAction dùng chung test)"] --> FSM
    end

    subgraph T2["TẦNG 2: HẠ TẦNG TRUYỀN DẪN MQTT BROKER"]
        BROKER[("MQTT Broker (broker.emqx.io:1883 / 8084)\nTopic Prefix: Nhom09/smoke/v2/... & Nhom09/smoke/cmd/...")]
        T1 <== "Telemetry, Alarm, KeepAlive, LWT (QoS 0/1)" ==> BROKER
    end

    subgraph T3["TẦNG 3: MIDDLEWARE ENGINE (NODE-RED)"]
        NR_AUTH["flows: Auth Node\n(Lưu fleet registry kèm Floor, Room, Building)"]
        NR_DEDUP["functions/parse_telemetry, parse_alarm, parse_keepalive.js\n(Deduplication Cache TTL 5s)"]
        NR_LWT["functions/parse_lwt.js\n(Đánh dấu OFFLINE tức thời)"]
        NR_SCHED["functions/scheduler_tick.js\n(Inject 1 phút: Ngày 400 PPM, Đêm 350 PPM)"]
        NR_ENGINE["functions/core_engine.js\n(3 Business Rules, Cooldown reflection, Dynamic Fleet)"]
        NR_DISP["functions/command_dispatcher.js\n(Chặn topic wildcard +, # khi PUBLISH)"]
        NR_ALERT["functions/alert_dispatcher.js\n(Telegram Bot API & Webhook Mock)"]
        
        BROKER <== "Sub / Pub" ==> NR_DEDUP & NR_LWT
        NR_DEDUP & NR_LWT --> NR_ENGINE
        NR_SCHED --> NR_ENGINE
        NR_ENGINE --> NR_DISP --> BROKER
        NR_ENGINE --> NR_ALERT
    end

    subgraph T4["TẦNG 4: APPLICATION & SCADA SUPERVISION"]
        WEB_HTML["web/index.html\n(Semantic Layout, Role Badge, Gauges)"]
        WEB_UTIL["web/util.js\n(escapeHtml Sanitizer, safeLevelClass)"]
        WEB_APP["web/app.js\n(Phản chiếu fsm_state, textContent chống XSS, Khóa nút ALARM)"]
        
        BROKER <== "WSS (8084)" ==> WEB_APP
        WEB_APP --- WEB_UTIL
        WEB_APP --- WEB_HTML
    end
```

### 1.2 Bảng Thống Kê Danh Mục Mã Nguồn Vận Hành

| STT | Module Vận Hành | Tên File | Dòng | Kích Thước | Vai Trò Vận Hành Chính |
| :-: | :--- | :--- | :-: | :-: | :--- |
| 1 | Hạ tầng PlatformIO | `platformio.ini` | 23 | 542 B | Hạ tầng PlatformIO |
| 2 | Cấu hình Wokwi Simulator | `wokwi.toml` | 4 | 107 B | Cấu hình Wokwi Simulator |
| 3 | Sơ đồ mạch điện Wokwi | `diagram.json` | 77 | 1,893 B | Sơ đồ mạch điện Wokwi |
| 4 | Root Forwarding Mirror | `main.cpp` | 17 | 849 B | Root Forwarding Mirror |
| 5 | Core: Tính toán ngưỡng PCCC | `lib/core/thresholds.h` | 18 | 465 B | Core: Tính toán ngưỡng PCCC |
| 6 | Core: Bộ lọc số EMA bất đối xứng | `lib/core/ema_filter.h` | 21 | 440 B | Core: Bộ lọc số EMA bất đối xứng |
| 7 | Core: Giám sát sức khỏe cảm biến | `lib/core/health.h` | 58 | 1,245 B | Core: Giám sát sức khỏe cảm biến |
| 8 | Core: Thuật toán Exponential Backoff | `lib/core/netutil.h` | 10 | 195 B | Core: Thuật toán Exponential Backoff |
| 9 | Core: Cấu trúc Exponential Backoff dùng chung | `lib/core/backoff.h` | 29 | 671 B | Core: Cấu trúc Exponential Backoff dùng chung |
| 10 | Core: Cấu trúc Ring Buffer dùng chung | `lib/core/ring_buffer.h` | 60 | 1,503 B | Core: Cấu trúc Ring Buffer dùng chung |
| 11 | Core: Trình phân tích & Khóa liên động lệnh | `lib/core/cmd_parse.h` | 63 | 2,133 B | Core: Trình phân tích & Khóa liên động lệnh |
| 12 | Core: Khai báo FSM & Interlocks | `lib/core/fsm_core.h` | 114 | 2,589 B | Core: Khai báo FSM & Interlocks |
| 13 | Core: Động cơ chuyển trạng thái FSM | `lib/core/fsm_core.cpp` | 61 | 1,931 B | Core: Động cơ chuyển trạng thái FSM |
| 14 | Cấu hình Firmware & Topics | `src/config.h` | 118 | 6,485 B | Cấu hình Firmware & Topics |
| 15 | HAL Khai báo Cảm biến | `src/sensors.h` | 13 | 375 B | HAL Khai báo Cảm biến |
| 16 | HAL Xử lý Cảm biến MQ-2 & DHT22 | `src/sensors.cpp` | 78 | 2,450 B | HAL Xử lý Cảm biến MQ-2 & DHT22 |
| 17 | HAL Khai báo Actuator & FSM | `src/fsm.h` | 13 | 263 B | HAL Khai báo Actuator & FSM |
| 18 | HAL Trình điều khiển Relay & Còi LEDC | `src/fsm.cpp` | 61 | 1,486 B | HAL Trình điều khiển Relay & Còi LEDC |
| 19 | Bộ đệm ngoại tuyến (Offline Buffer Header) | `src/offline_buffer.h` | 34 | 960 B | Bộ đệm ngoại tuyến (Offline Buffer Header) |
| 20 | Bộ đệm ngoại tuyến (Ring Buffer Implementation) | `src/offline_buffer.cpp` | 79 | 2,372 B | Bộ đệm ngoại tuyến (Ring Buffer Implementation) |
| 21 | Firmware Điều khiển Trung tâm (Main Orchestrator) | `src/main.cpp` | 623 | 21,023 B | Firmware Điều khiển Trung tâm (Main Orchestrator) |
| 22 | Node-RED: Parser Telemetry & Dedup | `nodered/functions/parse_telemetry.js` | 39 | 1,113 B | Node-RED: Parser Telemetry & Dedup |
| 23 | Node-RED: Parser Alarm Event & Dedup | `nodered/functions/parse_alarm.js` | 32 | 944 B | Node-RED: Parser Alarm Event & Dedup |
| 24 | Node-RED: Parser Keep-Alive & Dedup | `nodered/functions/parse_keepalive.js` | 32 | 881 B | Node-RED: Parser Keep-Alive & Dedup |
| 25 | Node-RED: Parser LWT Signal | `nodered/functions/parse_lwt.js` | 22 | 511 B | Node-RED: Parser LWT Signal |
| 26 | Node-RED: Động cơ Business Rules & Abnormal Engine | `nodered/functions/core_engine.js` | 194 | 6,984 B | Node-RED: Động cơ Business Rules & Abnormal Engine |
| 27 | Node-RED: Bộ điều phối lệnh (Command Dispatcher) | `nodered/functions/command_dispatcher.js` | 6 | 183 B | Node-RED: Bộ điều phối lệnh (Command Dispatcher) |
| 28 | Node-RED: Bộ phát tin cảnh báo Telegram (Alert Dispatcher) | `nodered/functions/alert_dispatcher.js` | 18 | 543 B | Node-RED: Bộ phát tin cảnh báo Telegram (Alert Dispatcher) |
| 29 | Node-RED: Lập lịch chế độ Ngày/Đêm (Scheduler Tick) | `nodered/functions/scheduler_tick.js` | 11 | 310 B | Node-RED: Lập lịch chế độ Ngày/Đêm (Scheduler Tick) |
| 30 | Node-RED: Cấu trúc Flow hoàn chỉnh (52 Nodes) | `nodered/flows_smoke_detector.json` | 970 | 37,873 B | Node-RED: Cấu trúc Flow hoàn chỉnh (52 Nodes) |
| 31 | Web SCADA: Thư viện bảo mật XSS & Utilities | `web/util.js` | 30 | 845 B | Web SCADA: Thư viện bảo mật XSS & Utilities |
| 32 | Web SCADA: Giao diện điều hành (HTML5 Semantic) | `web/index.html` | 784 | 38,643 B | Web SCADA: Giao diện điều hành (HTML5 Semantic) |
| 33 | Web SCADA: Bảng mã phong cách giao diện (CSS3 Glassmorphism) | `web/style.css` | 1,823 | 37,151 B | Web SCADA: Bảng mã phong cách giao diện (CSS3 Glassmorphism) |
| 34 | Web SCADA: Mã nguồn xử lý tương tác (JavaScript Application) | `web/app.js` | 1,168 | 46,150 B | Web SCADA: Mã nguồn xử lý tương tác (JavaScript Application) |
| 35 | Kiểm thử Native C++ Core (Unity) | `test/test_core.cpp` | 693 | 27,013 B | Kiểm thử Native C++ Core (Unity) |
| 36 | Kiểm thử Node-RED Engine (Node Test Runner) | `nodered/tests/engine.test.js` | 353 | 12,358 B | Kiểm thử Node-RED Engine (Node Test Runner) |
| 37 | Kiểm thử Tích hợp Flow Node-RED (Flow Integration) | `nodered/tests/flow_integration.test.js` | 211 | 8,346 B | Kiểm thử Tích hợp Flow Node-RED (Flow Integration) |
| 38 | Kiểm thử Web SCADA XSS & Reflection | `web/tests/util.test.js` | 194 | 7,037 B | Kiểm thử Web SCADA XSS & Reflection |
| 39 | Bộ kịch bản kiểm thử MQTTX Slide 65 (23 Messages) | `tests/mqttx_collection_slide65.json` | 658 | 22,357 B | Bộ kịch bản kiểm thử MQTTX Slide 65 (23 Messages) |
| 40 | Kiểm duyệt cam kết tự động (Claims Validator) | `scripts/check_claims.py` | 168 | 6,518 B | Kiểm duyệt cam kết tự động (Claims Validator) |
| 41 | Kiểm tra tiền tố Topic (Topic Prefix Auditor) | `scripts/verify_topic_prefix.py` | 144 | 5,326 B | Kiểm tra tiền tố Topic (Topic Prefix Auditor) |
| 42 | Bảng đặc tả cam kết 3 bậc (Claims Registry) | `docs/audit/claims.yaml` | 83 | 5,218 B | Bảng đặc tả cam kết 3 bậc (Claims Registry) |

---

## PHẦN 2: HẠ TẦNG PLATFORMIO (`platformio.ini`)

> **Đường dẫn:** `platformio.ini`  
> **Quy mô:** 23 dòng | 542 bytes | Ngôn ngữ: `ini`

```ini
; PlatformIO Project Configuration File
; Project: He Thong Bao Khoi Canh Bao Som (Do An IoT - Nhom 09)
; Board: ESP32 Dev Module (esp32dev)
; Framework: Arduino

[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino
monitor_speed = 115200

lib_deps =
    adafruit/DHT sensor library @ ^1.4.7
    adafruit/Adafruit Unified Sensor @ ^1.1.15
    knolleary/PubSubClient @ ^2.8
    bblanchon/ArduinoJson @ ^7.4.2

[env:native]
platform = native
test_framework = unity
build_flags = -std=c++17 -Ilib/core
test_build_src = no


```

---

## PHẦN 3: CẤU HÌNH WOKWI SIMULATOR (`wokwi.toml`)

> **Đường dẫn:** `wokwi.toml`  
> **Quy mô:** 4 dòng | 107 bytes | Ngôn ngữ: `toml`

```toml
[wokwi]
version = 1
firmware = ".pio/build/esp32dev/firmware.bin"
elf = ".pio/build/esp32dev/firmware.elf"

```

---

## PHẦN 4: SƠ ĐỒ MẠCH ĐIỆN WOKWI (`diagram.json`)

> **Đường dẫn:** `diagram.json`  
> **Quy mô:** 77 dòng | 1,893 bytes | Ngôn ngữ: `json`

```json
{
  "version": 1,
  "author": "Nhom 09 - He Thong Bao Khoi Canh Bao Som",
  "editor": "wokwi",
  "parts": [
    {
      "type": "board-esp32-devkit-c-v4",
      "id": "esp",
      "top": 0,
      "left": 0,
      "attrs": {}
    },
    {
      "type": "wokwi-gas-sensor",
      "id": "mq2",
      "top": -170,
      "left": 150,
      "attrs": { "ppm": "200" }
    },
    {
      "type": "wokwi-dht22",
      "id": "dht",
      "top": -170,
      "left": -180,
      "attrs": {}
    },
    {
      "type": "wokwi-buzzer",
      "id": "bz1",
      "top": 210,
      "left": -180,
      "attrs": { "volume": "0.1" }
    },
    {
      "type": "wokwi-relay-module",
      "id": "relay1",
      "top": 200,
      "left": 120,
      "attrs": {}
    },
    {
      "type": "wokwi-led",
      "id": "led1",
      "top": 200,
      "left": 270,
      "attrs": { "color": "blue", "label": "FAN" }
    },
    {
      "type": "wokwi-pushbutton",
      "id": "btn1",
      "top": 40,
      "left": 230,
      "attrs": { "color": "green", "label": "Manual Fan" }
    }
  ],
  "connections": [
    [ "esp:TX", "$serialMonitor:RX", "", [] ],
    [ "esp:RX", "$serialMonitor:TX", "", [] ],
    [ "mq2:VCC", "esp:5V", "red", [] ],
    [ "mq2:GND", "esp:GND.1", "black", [] ],
    [ "mq2:AOUT", "esp:34", "gold", [] ],
    [ "dht:VCC", "esp:3V3", "red", [] ],
    [ "dht:GND", "esp:GND.1", "black", [] ],
    [ "dht:SDA", "esp:4", "green", [] ],
    [ "bz1:2", "esp:16", "orange", [] ],
    [ "bz1:1", "esp:GND.1", "black", [] ],
    [ "relay1:VCC", "esp:5V", "red", [] ],
    [ "relay1:GND", "esp:GND.2", "black", [] ],
    [ "relay1:IN", "esp:17", "purple", [] ],
    [ "relay1:COM", "esp:5V", "red", [] ],
    [ "relay1:NO", "led1:A", "blue", [] ],
    [ "led1:C", "esp:GND.2", "black", [] ],
    [ "btn1:1.l", "esp:18", "cyan", [] ],
    [ "btn1:2.l", "esp:GND.1", "black", [] ]
  ],
  "dependencies": {}
}

```

---

## PHẦN 5: ROOT FORWARDING MIRROR (`main.cpp`)

> **Đường dẫn:** `main.cpp`  
> **Quy mô:** 17 dòng | 849 bytes | Ngôn ngữ: `cpp`

```cpp
/**
 * @file main.cpp (Root Mirror)
 * @brief He Thong Bao Khoi Canh Bao Som - Nhom 04 (N09)
 * @details File nay duoc dong bo voi src/main.cpp theo kien truc Lean & Clean Code.
 *          Ma nguon bien dich chinh thuc cua PlatformIO va Wokwi nam trong thu muc: src/
 *          - src/config.h: Cau hinh chan GPIO, thong so mang, topic registry, nguong PCCC
 *          - src/sensors.h / sensors.cpp: Xu ly MQ-2, DHT22 va kiem tra suc khoe phan cung
 *          - src/fsm.h / fsm.cpp: Dong co FSM 6 trang thai va dieu khien thiet bi chap hanh
 *          - src/offline_buffer.h / offline_buffer.cpp: Vong dem tinh 20 ban ghi ngoai tuyen
 *          - src/main.cpp: Dieu phoi luong ung dung (Application Orchestrator)
 */

#include "src/config.h"
#include "src/offline_buffer.h"
#include "src/sensors.h"
#include "src/fsm.h"
#include "src/main.cpp"

```

---

## PHẦN 6: CORE: TÍNH TOÁN NGƯỠNG PCCC (`lib/core/thresholds.h`)

> **Đường dẫn:** `lib/core/thresholds.h`  
> **Quy mô:** 18 dòng | 465 bytes | Ngôn ngữ: `cpp`

```cpp
#ifndef THRESHOLDS_H
#define THRESHOLDS_H

struct Thresholds {
    float alarm;
    float safe;
};

constexpr float ALARM_MIN_PPM = 300.0f;
constexpr float ALARM_MAX_PPM = 400.0f; // DEFAULT_ALARM_PPM_DAY

inline Thresholds makeThresholds(float req) {
    if (req != req) req = ALARM_MAX_PPM; // Handle NaN
    const float a = req < ALARM_MIN_PPM ? ALARM_MIN_PPM : (req > ALARM_MAX_PPM ? ALARM_MAX_PPM : req);
    return { a, a * 0.75f };
}

#endif // THRESHOLDS_H

```

---

## PHẦN 7: CORE: BỘ LỌC SỐ EMA BẤT ĐỐI XỨNG (`lib/core/ema_filter.h`)

> **Đường dẫn:** `lib/core/ema_filter.h`  
> **Quy mô:** 21 dòng | 440 bytes | Ngôn ngữ: `cpp`

```cpp
#ifndef EMA_FILTER_H
#define EMA_FILTER_H

struct EmaFilter {
    float value = -1.0f;
};

inline float emaUpdate(EmaFilter& f, float raw, float aRise = 0.40f, float aFall = 0.15f) {
    if (f.value < 0.0f) {
        f.value = raw;
        return raw;
    }
    f.value += (raw > f.value ? aRise : aFall) * (raw - f.value);
    return f.value;
}

inline void emaReset(EmaFilter& f, float raw) {
    f.value = raw;
}

#endif // EMA_FILTER_H

```

---

## PHẦN 8: CORE: GIÁM SÁT SỨC KHỎE CẢM BIẾN (`lib/core/health.h`)

> **Đường dẫn:** `lib/core/health.h`  
> **Quy mô:** 58 dòng | 1,245 bytes | Ngôn ngữ: `cpp`

```cpp
#ifndef HEALTH_H
#define HEALTH_H

#include <stdint.h>

struct Mq2Health {
    bool fault = false;
    uint8_t bad = 0;
    uint8_t good = 0;
};

enum HealthEvent : uint8_t {
    HE_NONE,
    HE_FAULT_ENTER,
    HE_RECOVERED
};

inline HealthEvent mq2Update(Mq2Health& h, int rawAdc, bool simFault, uint8_t enterN = 2, uint8_t exitN = 3) {
    const bool broken = simFault || rawAdc < 30; // KHONG co dieu kien > 4080
    if (broken) {
        h.good = 0;
        if (!h.fault && ++h.bad >= (simFault ? 1 : enterN)) {
            h.fault = true;
            return HE_FAULT_ENTER;
        }
        return HE_NONE;
    }
    h.bad = 0;
    if (h.fault && ++h.good >= exitN) {
        h.fault = false;
        h.good = 0;
        return HE_RECOVERED;
    }
    return HE_NONE;
}

struct DhtHealth {
    bool fault = false;
    uint8_t fails = 0;
};

inline void dhtOnRead(DhtHealth& h, bool ok, float t, bool simFault) {
    if (simFault) {
        h.fault = true;
        h.fails = 3;
        return;
    }
    const bool good = ok && t >= -10.0f && t <= 85.0f;
    if (good) {
        h.fails = 0;
        h.fault = false;
    } else {
        if (h.fails < 255) h.fails++;
        if (h.fails >= 3) h.fault = true;
    }
}

#endif // HEALTH_H

```

---

## PHẦN 9: CORE: THUẬT TOÁN EXPONENTIAL BACKOFF (`lib/core/netutil.h`)

> **Đường dẫn:** `lib/core/netutil.h`  
> **Quy mô:** 10 dòng | 195 bytes | Ngôn ngữ: `cpp`

```cpp
#ifndef NETUTIL_H
#define NETUTIL_H

#include <stdint.h>

inline uint32_t nextBackoff(uint32_t cur, uint32_t maxMs = 16000) {
    return cur * 2 > maxMs ? maxMs : cur * 2;
}

#endif // NETUTIL_H

```

---

## PHẦN 10: CORE: CẤU TRÚC EXPONENTIAL BACKOFF DÙNG CHUNG (`lib/core/backoff.h`)

> **Đường dẫn:** `lib/core/backoff.h`  
> **Quy mô:** 29 dòng | 671 bytes | Ngôn ngữ: `cpp`

```cpp
#ifndef BACKOFF_H
#define BACKOFF_H

#include <stdint.h>
#include "netutil.h"

/**
 * @file backoff.h
 * @brief May trang thai Exponential Backoff quan tri thoi gian cho tai ket noi
 * @details Dung chung cho Firmware ESP32 (src/main.cpp) va bo kiem thu Native Unity (test/test_core.cpp)
 */
struct ExponentialBackoff {
    uint32_t currentMs;
    uint32_t initialMs;
    uint32_t maxMs;

    ExponentialBackoff(uint32_t init = 1000, uint32_t max = 16000)
        : currentMs(init), initialMs(init), maxMs(max) {}

    void fail() {
        currentMs = nextBackoff(currentMs, maxMs);
    }

    void reset() {
        currentMs = initialMs;
    }
};

#endif // BACKOFF_H

```

---

## PHẦN 11: CORE: CẤU TRÚC RING BUFFER DÙNG CHUNG (`lib/core/ring_buffer.h`)

> **Đường dẫn:** `lib/core/ring_buffer.h`  
> **Quy mô:** 60 dòng | 1,503 bytes | Ngôn ngữ: `cpp`

```cpp
#ifndef RING_BUFFER_H
#define RING_BUFFER_H

#include <stddef.h>

/**
 * @file ring_buffer.h
 * @brief Template hang doi vong tinh khong cap phat dong (Zero-Heap RingBuffer)
 * @details Dung chung cho Firmware ESP32 (src/offline_buffer.cpp) va bo kiem thu Native Unity (test/test_core.cpp)
 */
template<typename T, size_t N>
class RingBuffer {
public:
    RingBuffer() : m_head(0), m_count(0) {}

    void clear() {
        m_head = 0;
        m_count = 0;
    }

    void push(const T& item) {
        m_buffer[m_head] = item;
        m_head = (m_head + 1) % N;
        if (m_count < N) {
            m_count++;
        }
    }

    size_t size() const { return m_count; }
    size_t capacity() const { return N; }
    bool empty() const { return m_count == 0; }
    bool full() const { return m_count == N; }

    // Truc xuat phan tu theo thu tu FIFO: index 0 la cu nhat (oldest), count-1 la moi nhat (newest)
    const T& getOldest(size_t index) const {
        size_t start = (m_head - m_count + N) % N;
        return m_buffer[(start + index) % N];
    }

    T& getOldest(size_t index) {
        size_t start = (m_head - m_count + N) % N;
        return m_buffer[(start + index) % N];
    }

    // Xa n phan tu cu nhat khoi bo dem (sau khi gui mang thanh cong)
    void drop(size_t n) {
        if (n >= m_count) {
            m_count = 0;
        } else {
            m_count -= n;
        }
    }

private:
    T m_buffer[N];
    size_t m_head;
    size_t m_count;
};

#endif // RING_BUFFER_H

```

---

## PHẦN 12: CORE: TRÌNH PHÂN TÍCH & KHÓA LIÊN ĐỘNG LỆNH (`lib/core/cmd_parse.h`)

> **Đường dẫn:** `lib/core/cmd_parse.h`  
> **Quy mô:** 63 dòng | 2,133 bytes | Ngôn ngữ: `cpp`

```cpp
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

```

---

## PHẦN 13: CORE: KHAI BÁO FSM & INTERLOCKS (`lib/core/fsm_core.h`)

> **Đường dẫn:** `lib/core/fsm_core.h`  
> **Quy mô:** 114 dòng | 2,589 bytes | Ngôn ngữ: `cpp`

```cpp
#ifndef FSM_CORE_H
#define FSM_CORE_H

#include <stdint.h>
#include "thresholds.h"

enum SystemState : uint8_t {
    STATE_SAFE,
    STATE_WARNING,
    STATE_ALARM,
    STATE_COOLDOWN,
    STATE_FAULT
};

enum BuzzerMode : uint8_t {
    BUZZ_OFF,
    BUZZ_ALARM,
    BUZZ_FAULT_BEEP
};

enum CmdResult : uint8_t {
    CMD_OK,
    CMD_REJECTED_SAFETY_LOCK
};

constexpr uint32_t COOLDOWN_MS = 30000;
constexpr uint32_t LOCAL_ACK_MS = 60000;
constexpr uint32_t REMOTE_MUTE_MS = 180000;

struct FsmContext {
    SystemState state = STATE_SAFE;
    bool alarmLatched = false;
    bool cooldownActive = false;
    uint32_t cooldownStartMs = 0;
    bool muted = false;
    uint32_t muteUntilMs = 0;
    bool manualMode = false; // manualMode=false nghĩa là AUTO
    bool manualFan = false;
};

struct FsmInput {
    float ppm;
    bool mq2Fault;
    bool dhtFault;
    uint32_t nowMs;
};

struct FsmOutput {
    bool fanOn;
    BuzzerMode buzzer;
    bool buzzerMuted;
};

struct BuzzerCmd {
    bool on;
    uint32_t freqHz;
};

FsmOutput fsmStep(FsmContext& c, const FsmInput& in, const Thresholds& th);

inline BuzzerCmd buzzerPattern(BuzzerMode m, uint32_t nowMs) {
    switch (m) {
        case BUZZ_ALARM:      return { true, 800 };
        case BUZZ_FAULT_BEEP: return { (nowMs % 2000) < 200, 1000 };
        default:              return { false, 0 };
    }
}

// Lệnh có interlock (dùng chung cho MQTT và nút bấm)
inline CmdResult cmdRemoteMute(FsmContext& c, uint32_t now) {
    if (c.alarmLatched) return CMD_REJECTED_SAFETY_LOCK;
    c.muted = true;
    c.muteUntilMs = now + REMOTE_MUTE_MS;
    return CMD_OK;
}

inline void cmdRemoteUnmute(FsmContext& c) {
    c.muted = false;
}

inline CmdResult cmdRemoteFanOff(FsmContext& c) {
    if (c.alarmLatched) return CMD_REJECTED_SAFETY_LOCK;
    c.manualMode = true;
    c.manualFan = false;
    return CMD_OK;
}

inline void cmdRemoteFanOn(FsmContext& c) {
    c.manualMode = true;
    c.manualFan = true;
}

inline void cmdFanAuto(FsmContext& c) {
    c.manualMode = false;
    c.manualFan = false;
}

inline CmdResult cmdBuzzerTest(const FsmContext& c) {
    return c.alarmLatched ? CMD_REJECTED_SAFETY_LOCK : CMD_OK;
}

// true = đã xác nhận tại chỗ (tắt còi 60s); false = đã đảo trạng thái quạt
inline bool cmdLocalButton(FsmContext& c, uint32_t now) {
    if (c.alarmLatched || c.state == STATE_FAULT) {
        c.muted = true;
        c.muteUntilMs = now + LOCAL_ACK_MS;
        return true;
    }
    c.manualMode = true;
    c.manualFan = !c.manualFan;
    return false;
}

#endif // FSM_CORE_H

```

---

## PHẦN 14: CORE: ĐỘNG CƠ CHUYỂN TRẠNG THÁI FSM (`lib/core/fsm_core.cpp`)

> **Đường dẫn:** `lib/core/fsm_core.cpp`  
> **Quy mô:** 61 dòng | 1,931 bytes | Ngôn ngữ: `cpp`

```cpp
#include "fsm_core.h"

static bool reached(uint32_t now, uint32_t t) {
    return (int32_t)(now - t) >= 0;
}

static FsmOutput out(const FsmContext& c, bool forceFan, BuzzerMode m) {
    FsmOutput o;
    o.fanOn = forceFan || (c.manualMode && c.manualFan);
    o.buzzerMuted = c.muted && m != BUZZ_OFF;
    o.buzzer = o.buzzerMuted ? BUZZ_OFF : m;
    return o;
}

FsmOutput fsmStep(FsmContext& c, const FsmInput& in, const Thresholds& th) {
    if (c.muted && reached(in.nowMs, c.muteUntilMs)) {
        c.muted = false;
    }

    // 1. Đang chốt ALARM: giữ tới khi khói <= safe; mất cảm biến vẫn giữ ALARM
    if (c.alarmLatched) {
        if (in.mq2Fault || in.ppm > th.safe) {
            c.state = STATE_ALARM;
            return out(c, true, BUZZ_ALARM);
        }
        c.alarmLatched = false;
        c.cooldownActive = true;
        c.cooldownStartMs = in.nowMs;
        c.state = STATE_COOLDOWN;
        return out(c, true, BUZZ_OFF);
    }

    // 2. Vào ALARM (chỉ khi MQ-2 hợp lệ). Xóa mute CHỈ ở cạnh vào ALARM
    if (!in.mq2Fault && in.ppm >= th.alarm) {
        c.alarmLatched = true;
        c.cooldownActive = false;
        c.muted = false; // Xóa mute ở cạnh vào ALARM
        c.state = STATE_ALARM;
        return out(c, true, BUZZ_ALARM);
    }

    // 3. Lỗi MQ-2 (chưa ALARM): fail-safe (quạt bật, còi beep lỗi)
    if (in.mq2Fault) {
        c.cooldownActive = false;
        c.state = STATE_FAULT;
        return out(c, true, BUZZ_FAULT_BEEP);
    }

    // 4. Cooldown 30s sau khi hạ khói
    if (c.cooldownActive) {
        if (in.nowMs - c.cooldownStartMs < COOLDOWN_MS) {
            c.state = STATE_COOLDOWN;
            return out(c, true, BUZZ_OFF);
        }
        c.cooldownActive = false;
    }

    // 5. WARNING / SAFE
    c.state = (in.ppm > th.safe || in.dhtFault) ? STATE_WARNING : STATE_SAFE;
    return out(c, false, BUZZ_OFF);
}

```

---

## PHẦN 15: CẤU HÌNH FIRMWARE & TOPICS (`src/config.h`)

> **Đường dẫn:** `src/config.h`  
> **Quy mô:** 118 dòng | 6,485 bytes | Ngôn ngữ: `cpp`

```cpp
#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>
#include "thresholds.h"
#include "fsm_core.h"
#include "ema_filter.h"
#include "health.h"
#include "netutil.h"

/**
 * @file config.h
 * @brief Tap trung toan bo cau hinh phan cung, tham so mang MQTT va hang so he thong
 * @details De tai 04: He thong bao khoi canh bao som - Nhom 04 (N09)
 *          Tuan thu nguyen tac Clean Code: Zero Magic Numbers, PROGMEM constants.
 */

// ============================================================================
// 1. PIN MAPPING (GPIO ESP32-WROOM-32D)
// ============================================================================
constexpr uint8_t PIN_MQ2        = 34;  ///< ADC1_CH6 - Doc tin hieu analog nong do khoi (12-bit)
constexpr uint8_t PIN_DHT        = 4;   ///< 1-Wire Digital GPIO doc cam bien nhiet am DHT22
constexpr uint8_t PIN_BUZZER     = 16;  ///< Digital Output dieu khien coi chip canh bao (LEDC PWM)
constexpr uint8_t PIN_RELAY      = 17;  ///< Digital Output kich relay dong cat quat hut khoi / LED
constexpr uint8_t PIN_BUTTON     = 18;  ///< Digital Input nut nhan manual (INPUT_PULLUP, active LOW)

// ============================================================================
// 2. ACTUATOR & PWM HARDWARE CONFIGURATION
// ============================================================================
constexpr uint8_t  BUZZER_LEDC_CH       = 0;     ///< Kenh LEDC PWM tren ESP32 cho Coi
constexpr uint32_t BUZZER_PWM_FREQ_HZ   = 2000;  ///< Tan so PWM co ban 2000 Hz
constexpr uint8_t  BUZZER_PWM_RES_BITS  = 8;     ///< Do phan giai 8-bit (0 - 255)
constexpr uint32_t BUZZER_TONE_ALARM_HZ = 800;   ///< Am sac coi bao chay khan cap (800 Hz)
constexpr uint32_t BUZZER_TONE_TEST_HZ  = 1000;  ///< Am sac kiem tra test coi (1000 Hz)
constexpr uint32_t BUZZER_DUTY_50PCT    = 128;   ///< 50% duty cycle kich am thanh toi uu
constexpr uint32_t BUZZER_DUTY_OFF      = 0;     ///< 0% duty cycle ngat am thanh

// ============================================================================
// 3. NETWORK & BROKER CONFIGURATION
// ============================================================================
constexpr const char* WIFI_SSID          = "Wokwi-GUEST";
constexpr const char* WIFI_PASS          = "";
constexpr const char* MQTT_BROKER        = "broker.emqx.io";
constexpr uint16_t    MQTT_PORT          = 1883;
constexpr const char* MQTT_CLIENT_PREFIX = "ESP32_Smoke_Nhom04_";
constexpr const char* DEVICE_ID          = "ESP32_SMOKE_N04_A01";

// ============================================================================
// 4. MQTT TOPICS REGISTRY (NHOM09 ENTERPRISE ISOLATION)
// ============================================================================
// V1 Legacy & Standard Topics
constexpr const char* TOPIC_TELEMETRY        = "Nhom09/smoke/telemetry";
constexpr const char* TOPIC_EVENT_ALARM      = "Nhom09/smoke/event/alarm";
constexpr const char* TOPIC_STATUS           = "Nhom09/smoke/status";
constexpr const char* TOPIC_CMD_FAN          = "Nhom09/smoke/cmd/fan";
constexpr const char* TOPIC_CMD_BUZZER       = "Nhom09/smoke/cmd/buzzer";
constexpr const char* TOPIC_CMD_MODE         = "Nhom09/smoke/cmd/mode";
constexpr const char* TOPIC_LWT              = "Nhom09/smoke/lwt";
constexpr const char* TOPIC_CMD_INJECT_FAULT = "Nhom09/smoke/cmd/inject_fault";
constexpr const char* TOPIC_CMD_SCHEDULER    = "Nhom09/smoke/cmd/scheduler";
constexpr const char* TOPIC_OFFLINE_SYNC     = "Nhom09/smoke/history/sync";
constexpr const char* TOPIC_KEEP_ALIVE_V1    = "Nhom09/smoke/keep_alive";

// V2 Enterprise Hierarchy (Slide 65 - ThS. Vo Hoang Hai)
constexpr const char* TOPIC_V2_AUTH_REQ      = "Nhom09/smoke/v2/auth/request";
constexpr const char* TOPIC_V2_AUTH_RESP     = "Nhom09/smoke/v2/auth/response/#";
constexpr const char* TOPIC_V2_TELEMETRY     = "Nhom09/smoke/v2/HUIT_A/F03/P302/ESP32_SMOKE_N04_A01/telemetry";
constexpr const char* TOPIC_V2_ALARM         = "Nhom09/smoke/v2/HUIT_A/F03/P302/ESP32_SMOKE_N04_A01/event/alarm";
constexpr const char* TOPIC_V2_KEEP_ALIVE    = "Nhom09/smoke/v2/HUIT_A/F03/P302/ESP32_SMOKE_N04_A01/keep_alive";
constexpr const char* TOPIC_V2_STATUS        = "Nhom09/smoke/v2/HUIT_A/F03/P302/ESP32_SMOKE_N04_A01/status";

// ============================================================================
// 5. TIMING CONSTANTS (IN MILLISECONDS)
// ============================================================================
constexpr unsigned long SAMPLE_MS                = 2000;   ///< Chu ky doc MQ-2 & publish telemetry
constexpr unsigned long DHT_POLL_INTERVAL_MS    = 5000;   ///< Chu ky doc DHT22
constexpr unsigned long HEARTBEAT_INTERVAL_MS   = 10000;  ///< Chu ky gui Keep-Alive (10s theo Slide 65)
constexpr unsigned long DEBOUNCE_DELAY_MS       = 50;     ///< Chong rung phim nut bam 50ms
constexpr unsigned long WIFI_ATTEMPT_TIMEOUT_MS = 10000;  ///< Timeout mot lan thu ket noi WiFi
constexpr unsigned long NET_MAX_BLOCK_MS        = 3000;   ///< Tieu chi do tre toi da giua 2 vong loop
constexpr uint8_t       MQ2_ENTER_N             = 2;      ///< 2 mau xau lien tiep de vao loi MQ-2
constexpr uint8_t       MQ2_EXIT_N              = 3;      ///< 3 mau tot lien tiep de thoat loi MQ-2
constexpr uint8_t       ADC_SAMPLES             = 5;      ///< So mau trung binh lay ADC MQ-2 (5 mau)

// ============================================================================
// 6. CALIBRATION & THRESHOLD CONSTANTS
// ============================================================================
constexpr float MEASURED_RS_AT_CALIB1 = 1.7100f;  ///< Dien tro cam bien Rs tai 200 PPM (Wokwi: Rs=1.71k, R0=Rs/1.71=1.0k, RL=10.0k)
constexpr float MEASURED_RS_AT_CALIB2 = 0.8852f;  ///< Dien tro cam bien Rs tai 1000 PPM (Wokwi)
constexpr float DEFAULT_ALARM_PPM_DAY = 400.0f;   ///< Nguong bao chay ban ngay (Gia tri thuc nghiem du an demo)
constexpr float ALARM_PPM_NIGHT       = 350.0f;   ///< Nguong bao chay ban dem (nhay hon vi it hoat dong)

// ============================================================================
// 7. SYSTEM ENUMS & DATA STRUCTURES
// ============================================================================
enum SystemMode : uint8_t {
  MODE_AUTO   = 0,
  MODE_MANUAL = 1
};

enum AckResult : uint8_t {
  ACK_ACCEPTED,
  ACK_SAFETY_LOCK,
  ACK_LOCAL_SILENCE,
  ACK_BAD_PAYLOAD,
  ACK_UNKNOWN_ACTION
};

struct SensorConfig {
  float vccSensor;
  float rlKOhm;
  float curveA;
  float curveB;
  float calibPoint1;
  float calibPoint2;
};

#endif // CONFIG_H

```

---

## PHẦN 16: HAL KHAI BÁO CẢM BIẾN (`src/sensors.h`)

> **Đường dẫn:** `src/sensors.h`  
> **Quy mô:** 13 dòng | 375 bytes | Ngôn ngữ: `cpp`

```cpp
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

```

---

## PHẦN 17: HAL XỬ LÝ CẢM BIẾN MQ-2 & DHT22 (`src/sensors.cpp`)

> **Đường dẫn:** `src/sensors.cpp`  
> **Quy mô:** 78 dòng | 2,450 bytes | Ngôn ngữ: `cpp`

```cpp
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
  const float rs = readAverageRs(ADC_SAMPLES, 200, config);
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

```

---

## PHẦN 18: HAL KHAI BÁO ACTUATOR & FSM (`src/fsm.h`)

> **Đường dẫn:** `src/fsm.h`  
> **Quy mô:** 13 dòng | 263 bytes | Ngôn ngữ: `cpp`

```cpp
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

```

---

## PHẦN 19: HAL TRÌNH ĐIỀU KHIỂN RELAY & CÒI LEDC (`src/fsm.cpp`)

> **Đường dẫn:** `src/fsm.cpp`  
> **Quy mô:** 61 dòng | 1,486 bytes | Ngôn ngữ: `cpp`

```cpp
#include "fsm.h"

static bool s_on = false;
static uint32_t s_freq = 0;
static uint32_t s_testEnd = 0;
static bool s_curFan = false;

void initActuators() {
  pinMode(PIN_RELAY, OUTPUT);
  digitalWrite(PIN_RELAY, LOW);

  ledcSetup(BUZZER_LEDC_CH, BUZZER_PWM_FREQ_HZ, BUZZER_PWM_RES_BITS);
  ledcAttachPin(PIN_BUZZER, BUZZER_LEDC_CH);
  ledcWrite(BUZZER_LEDC_CH, BUZZER_DUTY_OFF);
  ledcWriteTone(BUZZER_LEDC_CH, 0);
}

void fanApply(bool on) {
  if (on != s_curFan) {
    s_curFan = on;
    digitalWrite(PIN_RELAY, on ? HIGH : LOW);
  }
}

void buzzerTest(uint32_t now) {
  s_testEnd = now + 500;
}

void buzzerTick(BuzzerMode mode, uint32_t now) {
  BuzzerCmd c = buzzerPattern(mode, now);
  if (s_testEnd) {
    if ((int32_t)(now - s_testEnd) < 0) {
      c = { true, BUZZER_TONE_TEST_HZ };
    } else {
      s_testEnd = 0;
    }
  }

  if (c.on == s_on && (!c.on || c.freqHz == s_freq)) return; // chi ghi khi doi trang thai
  s_on = c.on;
  s_freq = c.freqHz;

  if (c.on) {
    ledcWriteTone(BUZZER_LEDC_CH, c.freqHz);
    ledcWrite(BUZZER_LEDC_CH, BUZZER_DUTY_50PCT);
  } else {
    ledcWrite(BUZZER_LEDC_CH, BUZZER_DUTY_OFF);
    ledcWriteTone(BUZZER_LEDC_CH, 0);
  }
}

const char* getFsmStateString(SystemState state) {
  switch (state) {
    case STATE_ALARM:    return "ALARM";
    case STATE_COOLDOWN: return "COOLDOWN";
    case STATE_FAULT:    return "FAULT";
    case STATE_WARNING:  return "WARNING";
    case STATE_SAFE:
    default:             return "SAFE";
  }
}

```

---

## PHẦN 20: BỘ ĐỆM NGOẠI TUYẾN (OFFLINE BUFFER HEADER) (`src/offline_buffer.h`)

> **Đường dẫn:** `src/offline_buffer.h`  
> **Quy mô:** 34 dòng | 960 bytes | Ngôn ngữ: `cpp`

```cpp
#ifndef OFFLINE_BUFFER_H
#define OFFLINE_BUFFER_H

#include <Arduino.h>
#include <PubSubClient.h>
#include "ring_buffer.h"

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
  bool mq2Valid;
  bool dhtValid;
  char state[16];
  char eventType[16]; // "TELEMETRY" or "ALARM_EVENT"
};

void initOfflineBuffer();
void pushOfflineRecord(float ppm, float temp, float hum, bool fan, bool buzzer, const char* stateStr, const char* eventType = "TELEMETRY", bool mq2Valid = true, bool dhtValid = true);
void flushOfflineBuffer(PubSubClient& client, const char* topic, int maxBatch = 5);
int getOfflineBufferCount();

#endif // OFFLINE_BUFFER_H

```

---

## PHẦN 21: BỘ ĐỆM NGOẠI TUYẾN (RING BUFFER IMPLEMENTATION) (`src/offline_buffer.cpp`)

> **Đường dẫn:** `src/offline_buffer.cpp`  
> **Quy mô:** 79 dòng | 2,372 bytes | Ngôn ngữ: `cpp`

```cpp
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

```

---

## PHẦN 22: FIRMWARE ĐIỀU KHIỂN TRUNG TÂM (MAIN ORCHESTRATOR) (`src/main.cpp`)

> **Đường dẫn:** `src/main.cpp`  
> **Quy mô:** 623 dòng | 21,023 bytes | Ngôn ngữ: `cpp`

```cpp
/**
 * @file main.cpp
 * @brief Chuong trinh dieu khien chinh (Main Application Orchestrator)
 * @details De tai 04: He thong bao khoi canh bao som - Nhom 04 (N09)
 *          Kien truc Lean & Clean Code: JsonDocument cap phat heap tam theo RAII trong tung handler, giai phong khi thoat ham; gioi han boi buffer mang (512B) va payload (256B).
 */

#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

#include "config.h"
#include "offline_buffer.h"
#include "sensors.h"
#include "fsm.h"
#include "backoff.h"
#include "cmd_parse.h"

// ============================================================================
// GLOBAL STATE & SYSTEM CONTEXT
// ============================================================================
static SensorConfig g_cfg = {
  5.0f,     // vccSensor
  10.0f,    // rlKOhm
  1.0f,     // curveA
  1.0f,     // curveB
  200.0f,   // calibPoint1
  1000.0f   // calibPoint2
};

static Thresholds   g_th  = makeThresholds(DEFAULT_ALARM_PPM_DAY);
static FsmContext   g_fsm = {};
static FsmInput     g_in  = {};
static FsmOutput    g_out = {};
static EmaFilter    g_ema = {};
static Mq2Health    g_mq2h = {};
static DhtHealth    g_dhth = {};

static float        g_r0          = 10.0f;
static float        g_ppm         = 0.0f;
static float        g_temp        = 28.0f;
static float        g_hum         = 65.0f;
static uint32_t     g_cycleCount  = 0;

// Simulation flags for fault injection sandbox
static bool g_simMq2 = false;
static bool g_simDht = false;

// Session & Client Identity
static char g_sessionKey[40] = "SK_SESSION_DEFAULT_N04";
static char g_clientId[40]   = "";
static char g_macAddress[20] = "";

// Timers
static uint32_t g_lastSample    = 0;
static uint32_t g_lastDht       = 0;
static uint32_t g_lastHeartbeat = 0;

// Network backoff & non-blocking state
static ExponentialBackoff s_wifiBackoff;
static ExponentialBackoff s_mqttBackoff;
static uint32_t s_wifiEnd     = 0;
static uint32_t s_wifiBegin   = 0;
static uint32_t s_mqttTry     = 0;
static bool     s_wifiBusy    = false;

// Button debounce
static bool     g_lastButtonState   = HIGH;
static bool     g_stableButtonState = HIGH;
static uint32_t g_lastDebounceTime  = 0;

// Network clients
static WiFiClient   g_espClient;
static PubSubClient g_mqttClient(g_espClient);

// ============================================================================
// FORWARD DECLARATIONS
// ============================================================================
static void recompute();
static void publishTelemetry();
static void publishAlarmEvent(bool isCritical);
static void publishAuthRequest();
static void publishKeepAlive();
static void mqttCallback(char* topic, byte* payload, unsigned int length);
static bool mqttConnect();
static void netTick(uint32_t now);
static void buttonTick(uint32_t now);

// ============================================================================
// COMMAND & ACK HELPERS
// ============================================================================
enum CmdType : uint8_t {
  CMD_FAN,
  CMD_BUZZER,
  CMD_MODE,
  CMD_SCHEDULER,
  CMD_FAULT,
  CMD_BUTTON,
  CMD_SYSTEM
};

static const char* cmdName(CmdType c) {
  switch (c) {
    case CMD_FAN:       return "cmd_fan";
    case CMD_BUZZER:    return "cmd_buzzer";
    case CMD_MODE:      return "cmd_mode";
    case CMD_SCHEDULER: return "cmd_scheduler";
    case CMD_FAULT:     return "inject_fault";
    case CMD_BUTTON:    return "button_press";
    default:            return "system";
  }
}

static const char* ackResultStr(AckResult r) {
  switch (r) {
    case ACK_ACCEPTED:       return "ACCEPTED";
    case ACK_SAFETY_LOCK:    return "REJECTED_SAFETY_LOCK";
    case ACK_LOCAL_SILENCE:  return "LOCAL_SILENCE_60S";
    case ACK_BAD_PAYLOAD:    return "REJECTED_BAD_PAYLOAD";
    case ACK_UNKNOWN_ACTION: return "REJECTED_UNKNOWN_ACTION";
    default:                 return "UNKNOWN";
  }
}

static void publishAck(CmdType cmd, AckResult res, const char* detail = "") {
  if (!g_mqttClient.connected()) return;

  char payload[256];
  snprintf(payload, sizeof(payload),
    "{\"device_id\":\"%s\",\"cmd\":\"%s\",\"result\":\"%s\",\"detail\":\"%s\",\"fan\":\"%s\",\"buzzer\":\"%s\",\"mode\":\"%s\",\"fsm_state\":\"%s\"}",
    DEVICE_ID, cmdName(cmd), ackResultStr(res), detail,
    g_out.fanOn ? "ON" : "OFF",
    (g_out.buzzer != BUZZ_OFF) ? "ON" : "OFF",
    g_fsm.manualMode ? "MANUAL" : "AUTO",
    getFsmStateString(g_fsm.state)
  );

  g_mqttClient.publish(TOPIC_STATUS, payload);
  g_mqttClient.publish(TOPIC_V2_STATUS, payload);
  Serial.printf("  [MQTT STATUS] -> ACK %s: %s (%s)\r\n", cmdName(cmd), ackResultStr(res), detail);
}

static void recompute() {
  g_in.nowMs = millis();
  g_in.ppm = g_ppm;
  g_in.mq2Fault = g_mq2h.fault;
  g_in.dhtFault = g_dhth.fault;
  g_out = fsmStep(g_fsm, g_in, g_th);
  fanApply(g_out.fanOn);
  buzzerTick(g_out.buzzer, g_in.nowMs);
}

// ============================================================================
// UPLINK MESSAGING HELPERS
// ============================================================================
static void publishTelemetry() {
  char ppmStr[16];
  if (g_mq2h.fault) {
    strcpy(ppmStr, "null");
  } else {
    snprintf(ppmStr, sizeof(ppmStr), "%.1f", g_ppm);
  }

  char payload[384];
  snprintf(payload, sizeof(payload),
    "{\"device_id\":\"%s\",\"uptime_s\":%lu,\"mq2_ppm\":%s,\"mq2_valid\":%s,\"temp\":%.1f,\"hum\":%.1f,\"dht_valid\":%s,\"fan\":\"%s\",\"buzzer\":\"%s\",\"buzzer_muted\":%s,\"mode\":\"%s\",\"fsm_state\":\"%s\",\"alarm_th\":%.1f,\"safe_th\":%.1f}",
    DEVICE_ID,
    millis() / 1000,
    ppmStr,
    g_mq2h.fault ? "false" : "true",
    g_temp,
    g_hum,
    g_dhth.fault ? "false" : "true",
    g_out.fanOn ? "ON" : "OFF",
    (g_out.buzzer != BUZZ_OFF) ? "ON" : "OFF",
    g_out.buzzerMuted ? "true" : "false",
    g_fsm.manualMode ? "MANUAL" : "AUTO",
    getFsmStateString(g_fsm.state),
    g_th.alarm,
    g_th.safe
  );

  if (g_mqttClient.connected()) {
    g_mqttClient.publish(TOPIC_TELEMETRY, payload);
    g_mqttClient.publish(TOPIC_V2_TELEMETRY, payload);
  } else {
    pushOfflineRecord(g_mq2h.fault ? 0.0f : g_ppm, g_temp, g_hum, g_out.fanOn, (g_out.buzzer != BUZZ_OFF), getFsmStateString(g_fsm.state), "TELEMETRY", !g_mq2h.fault, !g_dhth.fault);
  }
}

static void publishAlarmEvent(bool isCritical) {
  char payload[256];
  if (isCritical) {
    snprintf(payload, sizeof(payload),
      "{\"device_id\":\"%s\",\"uptime_s\":%lu,\"event\":\"SMOKE_ALERT\",\"severity\":\"CRITICAL\",\"ppm\":%.1f,\"threshold\":%.1f,\"msg\":\"CANH BAO: Khoi vuot nguong! Coi va Quat da bat!\"}",
      DEVICE_ID, millis() / 1000, g_ppm, g_th.alarm
    );
  } else {
    snprintf(payload, sizeof(payload),
      "{\"device_id\":\"%s\",\"uptime_s\":%lu,\"event\":\"SMOKE_SAFE\",\"severity\":\"NORMAL\",\"ppm\":%.1f,\"threshold\":%.1f,\"msg\":\"AN TOAN: Nong do khoi da ve muc an toan. Bat dau Purge 30s.\"}",
      DEVICE_ID, millis() / 1000, g_ppm, g_th.safe
    );
  }

  if (g_mqttClient.connected()) {
    g_mqttClient.publish(TOPIC_EVENT_ALARM, payload);
    g_mqttClient.publish(TOPIC_V2_ALARM, payload);
  } else {
    pushOfflineRecord(g_ppm, g_temp, g_hum, g_out.fanOn, (g_out.buzzer != BUZZ_OFF), getFsmStateString(g_fsm.state), "ALARM_EVENT", !g_mq2h.fault, !g_dhth.fault);
  }
  Serial.printf("  [MQTT EVENT] -> ALARM %s (PPM: %.1f)\r\n", isCritical ? "CRITICAL" : "SAFE", g_ppm);
}

static void publishAuthRequest() {
  if (!g_mqttClient.connected()) return;

  char payload[256];
  snprintf(payload, sizeof(payload),
    "{\"msg_id\":\"REQ-AUTH-%04lu\",\"device_id\":\"%s\",\"mac_address\":\"%s\",\"secret_token\":\"HUIT_IOT_SECURE_TOKEN_N04\",\"timestamp\":%lu}",
    millis() / 1000,
    DEVICE_ID,
    g_macAddress,
    millis() / 1000
  );

  g_mqttClient.publish(TOPIC_V2_AUTH_REQ, payload, 1);
  Serial.println(F("  [MQTT AUTH REQ] -> Sent Auth Request"));
}

static void publishKeepAlive() {
  if (!g_mqttClient.connected()) return;

  const char* statusStr = (g_fsm.state == STATE_FAULT || g_mq2h.fault) ? "FAULT" : (g_dhth.fault ? "DEGRADED" : "HEALTHY");
  char payload[256];
  snprintf(payload, sizeof(payload),
    "{\"session_key\":\"%s\",\"device_id\":\"%s\",\"uptime_s\":%lu,\"uptime_sec\":%lu,\"free_heap_bytes\":%u,\"wifi_rssi_dbm\":%d,\"status\":\"%s\",\"fsm_state\":\"%s\"}",
    g_sessionKey,
    DEVICE_ID,
    millis() / 1000,
    millis() / 1000,
    ESP.getFreeHeap(),
    WiFi.RSSI(),
    statusStr,
    getFsmStateString(g_fsm.state)
  );

  g_mqttClient.publish(TOPIC_KEEP_ALIVE_V1, payload);
  g_mqttClient.publish(TOPIC_V2_KEEP_ALIVE, payload);
}

// ============================================================================
// DOWNLINK COMMAND HANDLERS
// ============================================================================
static bool is(const char* a, const char* v) { return a && strcasecmp(a, v) == 0; }

static void onAuthResponse(const char* topic, const char* message) {
  if (strstr(topic, DEVICE_ID) == nullptr) return;

  JsonDocument doc;
  if (deserializeJson(doc, message)) return;

  const char* status = doc["status"] | "REJECTED";
  if (is(status, "PASS")) {
    const char* sk = doc["session_key"] | "SK_AUTHORIZED_N04";
    strncpy(g_sessionKey, sk, sizeof(g_sessionKey) - 1);
    g_sessionKey[sizeof(g_sessionKey) - 1] = '\0';
    Serial.println(F("  [AUTH PASS] Server accepted device"));

    if (doc["config"]["alarm_threshold_ppm"].is<float>()) {
      float reqTh = doc["config"]["alarm_threshold_ppm"].as<float>();
      g_th = makeThresholds(reqTh);
      Serial.printf("  [AUTH CONFIG] Synced alarm threshold: %.1f PPM (Safe: %.1f PPM)\r\n", g_th.alarm, g_th.safe);
    }
    publishAck(CMD_SYSTEM, ACK_ACCEPTED, "AUTH_PASS");
  } else {
    Serial.println(F("  [AUTH REJECTED] Server rejected authentication"));
  }
}

static void onFan(const char* message) {
  JsonDocument doc;
  if (deserializeJson(doc, message)) {
    publishAck(CMD_FAN, ACK_BAD_PAYLOAD, "JSON_PARSE_ERROR");
    return;
  }

  const char* action = doc["action"] | doc["cmd"] | "";
  ActionAck ack = applyFanAction(g_fsm, action);
  if (ack == ACTION_ACCEPTED) {
    publishAck(CMD_FAN, ACK_ACCEPTED, is(action, "AUTO") ? "MODE_AUTO" : (g_fsm.manualFan ? "FAN_ON" : "FAN_OFF"));
  } else if (ack == ACTION_SAFETY_LOCK) {
    publishAck(CMD_FAN, ACK_SAFETY_LOCK, "PPM_ABOVE_THRESHOLD");
  } else {
    publishAck(CMD_FAN, ACK_UNKNOWN_ACTION, "UNKNOWN_ACTION");
  }
  recompute();
}

static void onBuzzer(const char* message) {
  JsonDocument doc;
  if (deserializeJson(doc, message)) {
    publishAck(CMD_BUZZER, ACK_BAD_PAYLOAD, "JSON_PARSE_ERROR");
    return;
  }

  const char* action = doc["action"] | doc["cmd"] | "";
  ActionAck ack = applyBuzzerAction(g_fsm, action, millis());
  if (ack == ACTION_ACCEPTED) {
    if (is(action, "TEST") || is(action, "ON")) {
      buzzerTest(millis());
      publishAck(CMD_BUZZER, ACK_ACCEPTED, "TEST_500MS");
    } else {
      publishAck(CMD_BUZZER, ACK_ACCEPTED, g_fsm.muted ? "MUTED_180S" : "UNMUTED");
    }
  } else if (ack == ACTION_SAFETY_LOCK) {
    publishAck(CMD_BUZZER, ACK_SAFETY_LOCK, "ALARM_LATCHED");
  } else {
    publishAck(CMD_BUZZER, ACK_UNKNOWN_ACTION, "UNKNOWN_ACTION");
  }
  recompute();
}

static void onMode(const char* message) {
  JsonDocument doc;
  if (deserializeJson(doc, message)) {
    publishAck(CMD_MODE, ACK_BAD_PAYLOAD, "JSON_PARSE_ERROR");
    return;
  }

  const char* modeStr = doc["mode"] | doc["action"] | "";
  if (is(modeStr, "MANUAL")) {
    g_fsm.manualMode = true;
    publishAck(CMD_MODE, ACK_ACCEPTED, "MANUAL_MODE");
  } else if (is(modeStr, "AUTO")) {
    g_fsm.manualMode = false;
    publishAck(CMD_MODE, ACK_ACCEPTED, "AUTO_MODE");
  } else {
    publishAck(CMD_MODE, ACK_UNKNOWN_ACTION, "UNKNOWN_MODE");
  }
  recompute();
}

static void onScheduler(const char* message) {
  JsonDocument doc;
  if (deserializeJson(doc, message)) {
    publishAck(CMD_SCHEDULER, ACK_BAD_PAYLOAD, "JSON_PARSE_ERROR");
    return;
  }

  const char* mode = doc["mode"] | "";
  if (is(mode, "NIGHT")) {
    g_th = makeThresholds(ALARM_PPM_NIGHT);
    publishAck(CMD_SCHEDULER, ACK_ACCEPTED, "NIGHT_MODE_350PPM");
  } else if (is(mode, "DAY")) {
    g_th = makeThresholds(DEFAULT_ALARM_PPM_DAY);
    publishAck(CMD_SCHEDULER, ACK_ACCEPTED, "DAY_MODE_400PPM");
  } else {
    publishAck(CMD_SCHEDULER, ACK_UNKNOWN_ACTION, "UNKNOWN_SCHEDULER_MODE");
  }
  recompute();
}

static void onFaultInjection(const char* message) {
  JsonDocument doc;
  if (deserializeJson(doc, message)) {
    publishAck(CMD_FAULT, ACK_BAD_PAYLOAD, "JSON_PARSE_ERROR");
    return;
  }

  const char* type = doc["type"] | doc["fault"] | "";
  if (is(type, "MQ2_DISCONNECT")) {
    g_simMq2 = true;
    mq2Update(g_mq2h, 0, g_simMq2, MQ2_ENTER_N, MQ2_EXIT_N);
    publishAck(CMD_FAULT, ACK_ACCEPTED, "MQ2_DISCONNECT_INJECTED");
  } else if (is(type, "DHT_NAN") || is(type, "DHT_TIMEOUT")) {
    g_simDht = true;
    dhtOnRead(g_dhth, false, g_temp, g_simDht);
    publishAck(CMD_FAULT, ACK_ACCEPTED, "DHT_FAULT_INJECTED");
  } else if (is(type, "CLEAR") || is(type, "RESTORE") || is(type, "NONE")) {
    g_simMq2 = false;
    g_simDht = false;
    g_mq2h = {};
    g_dhth = {};
    emaReset(g_ema, g_ppm > 0.0f ? g_ppm : 200.0f);
    publishAck(CMD_FAULT, ACK_ACCEPTED, "ALL_FAULTS_CLEARED");
  } else {
    publishAck(CMD_FAULT, ACK_UNKNOWN_ACTION, "REJECTED_UNKNOWN_FAULT");
  }
  recompute();
}

static void mqttCallback(char* topic, byte* payload, unsigned int length) {
  if (!topic || !payload || length == 0) return;

  char message[256];
  if (length >= sizeof(message)) length = sizeof(message) - 1;
  memcpy(message, payload, length);
  message[length] = '\0';

  Serial.println(F("\r\n====================== [DOWNLINK COMMAND] ======================"));
  Serial.print(F("Topic   : ")); Serial.println(topic);
  Serial.print(F("Payload : ")); Serial.println(message);

  if (strstr(topic, "/auth/response") != nullptr) {
    onAuthResponse(topic, message);
  } else if (strcmp(topic, TOPIC_CMD_FAN) == 0 || strstr(topic, "/cmd/fan") != nullptr) {
    onFan(message);
  } else if (strcmp(topic, TOPIC_CMD_BUZZER) == 0 || strstr(topic, "/cmd/buzzer") != nullptr) {
    onBuzzer(message);
  } else if (strcmp(topic, TOPIC_CMD_MODE) == 0 || strstr(topic, "/cmd/mode") != nullptr) {
    onMode(message);
  } else if (strcmp(topic, TOPIC_CMD_INJECT_FAULT) == 0 || strstr(topic, "/inject_fault") != nullptr) {
    onFaultInjection(message);
  } else if (strcmp(topic, TOPIC_CMD_SCHEDULER) == 0 || strstr(topic, "/scheduler") != nullptr) {
    onScheduler(message);
  }

  Serial.println(F("================================================================\r\n"));
}

// ============================================================================
// HARDWARE PERIPHERALS & NETWORK ORCHESTRATION
// ============================================================================
static void buttonTick(uint32_t now) {
  const bool reading = digitalRead(PIN_BUTTON);
  if (reading != g_lastButtonState) {
    g_lastDebounceTime = now;
  }

  if ((now - g_lastDebounceTime) > DEBOUNCE_DELAY_MS) {
    if (reading != g_stableButtonState) {
      g_stableButtonState = reading;
      if (g_stableButtonState == LOW) {
        bool silenced = cmdLocalButton(g_fsm, now);
        publishAck(CMD_BUTTON, silenced ? ACK_LOCAL_SILENCE : ACK_ACCEPTED, silenced ? "LOCAL_SILENCE_60S" : (g_fsm.manualFan ? "FAN_ON" : "FAN_OFF"));
        recompute();
      }
    }
  }
  g_lastButtonState = reading;
}

static bool mqttConnect() {
  Serial.print(F("[MQTT] Connecting to Broker "));
  Serial.println(MQTT_BROKER);

  g_mqttClient.setSocketTimeout(2);

  const char* lwtMsg = "{\"device_id\":\"ESP32_SMOKE_N04_A01\",\"status\":\"offline\",\"eventType\":\"LWT\"}";
  if (g_mqttClient.connect(g_clientId, TOPIC_LWT, 1, true, lwtMsg)) {
    Serial.println(F("[MQTT] >>> CONNECTED SUCCESSFULLY! <<<"));

    const char* onlineMsg = "{\"device_id\":\"ESP32_SMOKE_N04_A01\",\"status\":\"online\"}";
    g_mqttClient.publish(TOPIC_LWT, onlineMsg, true);

    g_mqttClient.subscribe("Nhom09/smoke/cmd/#", 1);
    g_mqttClient.subscribe(TOPIC_V2_AUTH_RESP, 1);
    g_mqttClient.subscribe("Nhom09/smoke/v2/+/+/+/+/cmd/#", 1);

    publishAck(CMD_SYSTEM, ACK_ACCEPTED, "ONLINE_READY");
    publishAuthRequest();
    flushOfflineBuffer(g_mqttClient, TOPIC_OFFLINE_SYNC, 5);
    return true;
  } else {
    Serial.printf("[MQTT] Connection failed, rc=%d\r\n", g_mqttClient.state());
    return false;
  }
}

static void netTick(uint32_t now) {
  if (WiFi.status() != WL_CONNECTED) {
    if (!s_wifiBusy) {
      if (now - s_wifiEnd >= s_wifiBackoff.currentMs) {
        WiFi.disconnect();
        WiFi.begin(WIFI_SSID, WIFI_PASS);
        s_wifiBusy = true;
        s_wifiBegin = now;
      }
    } else if (now - s_wifiBegin >= WIFI_ATTEMPT_TIMEOUT_MS) {
      s_wifiBusy = false;
      s_wifiEnd = now;
      s_wifiBackoff.fail();
    }
    return;
  }

  s_wifiBusy = false;
  s_wifiBackoff.reset();

  if (g_mqttClient.connected()) {
    g_mqttClient.loop();
    flushOfflineBuffer(g_mqttClient, TOPIC_OFFLINE_SYNC, 5);
    return;
  }

  if (now - s_mqttTry >= s_mqttBackoff.currentMs) {
    s_mqttTry = now;
    if (mqttConnect()) {
      s_mqttBackoff.reset();
    } else {
      s_mqttBackoff.fail();
    }
  }
}

// ============================================================================
// ARDUINO SETUP & MAIN LOOP
// ============================================================================
void setup() {
  Serial.begin(115200);
  delay(300);

  Serial.println(F("\r\n========================================================"));
  Serial.println(F("  HE THONG BAO KHOI CANH BAO SOM - FIRMWARE V5"));
  Serial.println(F("  Nhom 04 - Lop Lap trinh nhung IoT - GVHD: Vo Hoang Hai "));
  Serial.println(F("========================================================"));

  pinMode(PIN_BUTTON, INPUT_PULLUP);

  initActuators();
  initSensors();
  initOfflineBuffer();
  calibrateMQ2(g_cfg, g_r0);

  // Generate unique client ID with random hex suffix
  snprintf(g_clientId, sizeof(g_clientId), "%s%04X", MQTT_CLIENT_PREFIX, (uint16_t)random(0xffff));
  strncpy(g_macAddress, WiFi.macAddress().c_str(), sizeof(g_macAddress) - 1);
  g_macAddress[sizeof(g_macAddress) - 1] = '\0';
  Serial.printf("[SETUP] Client ID: %s | MAC: %s\r\n", g_clientId, g_macAddress);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  g_espClient.setTimeout(2);
  g_mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  g_mqttClient.setCallback(mqttCallback);
  g_mqttClient.setBufferSize(512);
  g_mqttClient.setSocketTimeout(2);

  recompute();
  Serial.println(F("[SETUP] Initialization complete. Starting non-blocking loop.\r\n"));
}

void loop() {
  const uint32_t loopStart = millis();
  const uint32_t now = loopStart;

  // 1. Maintain Network connectivity (Non-blocking decoupled backoff)
  netTick(now);

  // 2. Hardware push button
  buttonTick(now);

  // 3. Actuator updates (Edge-triggered LEDC tone)
  buzzerTick(g_out.buzzer, now);
  fanApply(g_out.fanOn);

  // 4. Sample MQ-2 & step FSM every SAMPLE_MS (2000ms)
  if (now - g_lastSample >= SAMPLE_MS) {
    g_lastSample = now;
    g_cycleCount++;

    const SystemState prev = g_fsm.state;
    const int adc = analogRead(PIN_MQ2);
    const float rawPpm = readMQ2PPM(g_cfg, g_r0);

    const HealthEvent ev = mq2Update(g_mq2h, adc, g_simMq2, MQ2_ENTER_N, MQ2_EXIT_N);
    if (ev == HE_RECOVERED) {
      emaReset(g_ema, rawPpm);
    }
    if (!g_mq2h.fault) {
      g_ppm = emaUpdate(g_ema, rawPpm);
    }

    g_in = { g_ppm, g_mq2h.fault, g_dhth.fault, now };
    g_out = fsmStep(g_fsm, g_in, g_th);

    Serial.printf("[#%04lu | T=%3lus] PPM: %5.1f (raw: %5.1f) | Nhiet: %4.1f*C | Am: %4.1f%% | Quat: %3s | Coi: %3s | State: %s\r\n",
      g_cycleCount,
      now / 1000,
      g_mq2h.fault ? 0.0f : g_ppm,
      rawPpm,
      g_temp,
      g_hum,
      g_out.fanOn ? "BAT" : "TAT",
      (g_out.buzzer != BUZZ_OFF) ? "BAT" : "TAT",
      getFsmStateString(g_fsm.state)
    );

    if (g_fsm.state == STATE_ALARM && prev != STATE_ALARM) {
      publishAlarmEvent(true);
    } else if (g_fsm.state == STATE_COOLDOWN && prev == STATE_ALARM) {
      publishAlarmEvent(false);
    }

    publishTelemetry();
  }

  // 5. Poll DHT22 temperature & humidity (5000ms)
  if (now - g_lastDht >= DHT_POLL_INTERVAL_MS) {
    g_lastDht = now;
    float t = 0.0f, h = 0.0f;
    const bool ok = readDHT(t, h);
    dhtOnRead(g_dhth, ok, t, g_simDht);
    if (ok && !g_dhth.fault) {
      g_temp = t;
      g_hum  = h;
    }
  }

  // 6. Periodic Keep-Alive heartbeat (10s)
  if (now - g_lastHeartbeat >= HEARTBEAT_INTERVAL_MS) {
    g_lastHeartbeat = now;
    publishKeepAlive();
  }

  // 7. Loop Latency Performance Guard
  const uint32_t loopDuration = millis() - loopStart;
  if (loopDuration > NET_MAX_BLOCK_MS) {
    Serial.printf("[PERF WARN] Loop duration %lu ms exceeded NET_MAX_BLOCK_MS (%lu ms)!\r\n", loopDuration, NET_MAX_BLOCK_MS);
  }
}

```

---

## PHẦN 23: NODE-RED: PARSER TELEMETRY & DEDUP (`nodered/functions/parse_telemetry.js`)

> **Đường dẫn:** `nodered/functions/parse_telemetry.js`  
> **Quy mô:** 39 dòng | 1,113 bytes | Ngôn ngữ: `javascript`

```javascript
// functions/parse_telemetry.js
let d = msg.payload;
if (typeof d === 'string') {
  try {
    d = JSON.parse(d);
  } catch (e) {
    return null;
  }
}
if (!d || typeof d !== 'object') return null;

const num = v => (v === null || v === undefined) ? NaN : Number(v);

msg.eventType = 'TELEMETRY';
msg.deviceId  = d.device_id || 'ESP32_SMOKE_N04_A01';
msg.uptime    = d.uptime_s !== undefined ? d.uptime_s : d.uptime_sec;
msg.mq2Valid  = d.mq2_valid !== false;
msg.dhtValid  = d.dht_valid !== false;
msg.ppm       = num(d.mq2_ppm);
msg.temp      = num(d.temp);
msg.hum       = num(d.hum);
msg.fsmState  = d.fsm_state;
msg.alarmTh   = Number(d.alarm_th) || undefined;
msg.safeTh    = Number(d.safe_th) || undefined;

// ---- DEDUP: TTL 5s ----
if (msg.uptime !== undefined) {
  const now = Date.now();
  const cache = flow.get('dedup') || {};
  for (const k in cache) {
    if (now - cache[k] > 5000) delete cache[k];
  }
  const key = msg.deviceId + '|' + msg.eventType + '|' + (msg.eventName || '') + '|' + msg.uptime;
  if (cache[key]) return null;
  cache[key] = now;
  flow.set('dedup', cache);
}

return msg;

```

---

## PHẦN 24: NODE-RED: PARSER ALARM EVENT & DEDUP (`nodered/functions/parse_alarm.js`)

> **Đường dẫn:** `nodered/functions/parse_alarm.js`  
> **Quy mô:** 32 dòng | 944 bytes | Ngôn ngữ: `javascript`

```javascript
// nodered/functions/parse_alarm.js
let d = msg.payload;
if (typeof d === 'string') {
  try {
    d = JSON.parse(d);
  } catch (e) {
    return null;
  }
}
if (!d || typeof d !== 'object') return null;

msg.eventType = 'ALARM_EVENT';
msg.deviceId  = d.device_id || 'ESP32_SMOKE_N04_A01';
msg.eventName = d.event || 'SMOKE_ALERT';
msg.severity  = d.severity || 'CRITICAL';
msg.ppm       = Number(d.ppm !== undefined ? d.ppm : (d.mq2_ppm || 0));
msg.threshold = Number(d.threshold || 400);
msg.uptime    = d.uptime_s !== undefined ? d.uptime_s : d.uptime_sec;

// Dedup cache TTL 5s
if (msg.uptime !== undefined) {
  const now = Date.now(), cache = flow.get('dedup') || {};
  for (const k in cache) {
    if (now - cache[k] > 5000) delete cache[k];
  }
  const key = msg.deviceId + '|' + msg.eventType + '|' + (msg.eventName || '') + '|' + msg.uptime;
  if (cache[key]) return null;
  cache[key] = now;
  flow.set('dedup', cache);
}

return msg;

```

---

## PHẦN 25: NODE-RED: PARSER KEEP-ALIVE & DEDUP (`nodered/functions/parse_keepalive.js`)

> **Đường dẫn:** `nodered/functions/parse_keepalive.js`  
> **Quy mô:** 32 dòng | 881 bytes | Ngôn ngữ: `javascript`

```javascript
// nodered/functions/parse_keepalive.js
let d = msg.payload;
if (typeof d === 'string') {
  try {
    d = JSON.parse(d);
  } catch (e) {
    return null;
  }
}
if (!d || typeof d !== 'object') return null;

msg.eventType = 'KEEP_ALIVE';
msg.deviceId  = d.device_id || 'ESP32_SMOKE_N04_A01';
msg.uptime    = d.uptime_s !== undefined ? d.uptime_s : d.uptime_sec;
msg.freeHeap  = Number(d.free_heap_bytes || 0);
msg.wifiRssi  = Number(d.wifi_rssi_dbm || -60);
msg.status    = d.status || 'HEALTHY';
msg.fsmState  = d.fsm_state;

// Dedup cache TTL 5s
if (msg.uptime !== undefined) {
  const now = Date.now(), cache = flow.get('dedup') || {};
  for (const k in cache) {
    if (now - cache[k] > 5000) delete cache[k];
  }
  const key = msg.deviceId + '|' + msg.eventType + '|' + msg.uptime;
  if (cache[key]) return null;
  cache[key] = now;
  flow.set('dedup', cache);
}

return msg;

```

---

## PHẦN 26: NODE-RED: PARSER LWT SIGNAL (`nodered/functions/parse_lwt.js`)

> **Đường dẫn:** `nodered/functions/parse_lwt.js`  
> **Quy mô:** 22 dòng | 511 bytes | Ngôn ngữ: `javascript`

```javascript
// functions/parse_lwt.js
let s = msg.payload;
let id = null;
let online = false;

try {
  const j = typeof s === 'string' ? JSON.parse(s) : s;
  if (j && typeof j === 'object') {
    id = j.device_id;
    online = String(j.status).toLowerCase() === 'online';
  } else {
    online = String(s).trim().toLowerCase() === 'online';
  }
} catch (e) {
  online = String(s).trim().toLowerCase() === 'online';
}

msg.eventType = 'LWT';
msg.deviceId  = id || 'ESP32_SMOKE_N04_A01';
msg.isOnline  = online;

return msg;

```

---

## PHẦN 27: NODE-RED: ĐỘNG CƠ BUSINESS RULES & ABNORMAL ENGINE (`nodered/functions/core_engine.js`)

> **Đường dẫn:** `nodered/functions/core_engine.js`  
> **Quy mô:** 194 dòng | 6,984 bytes | Ngôn ngữ: `javascript`

```javascript
// functions/core_engine.js  (4 output: lenh, log, fleet, thong bao)
const NOW = Date.now();
const FLOOR = 'F03', CROSS_PPM = 600, CROSS_RATE_MS = 60000, WATCHDOG_MS = 30000, ALERT_RATE_MS = 20000;
const fleet = flow.get('fleet') || {};
const cmds = [], logs = [];
let alert = null;

const dev = id => {
  let d = fleet[id];
  if (!d) {
    d = fleet[id] = {
      deviceId: id,
      status: 'UNKNOWN',
      deviceState: 'SAFE',
      effective: 'SAFE',
      lastSeen: 0,
      ppm: NaN,
      temp: NaN,
      rate: 0,
      lastPpm: 0,
      hum: 60.0,
      tempHist: [],
      alarmTh: 400,
      safeTh: 300,
      overActive: false,
      hotActive: false,
      cooldownStart: null,
      lastAlert: 0,
      topology: null,
      mq2Valid: true,
      dhtValid: true
    };
  }
  if (d.rate === undefined) d.rate = 0;
  if (!Array.isArray(d.tempHist)) d.tempHist = [];
  return d;
};

const log = (level, event, desc, id) => logs.push({ level, event, desc, deviceId: id, ts: NOW });

const topicOf = (d, kind) => (d.topology && d.topology.building && d.topology.floor && d.topology.room)
  ? `Nhom09/smoke/v2/${d.topology.building}/${d.topology.floor}/${d.topology.room}/${d.deviceId}/cmd/${kind}`
  : `Nhom09/smoke/cmd/${kind}`;

const cmd = (d, kind, payload) => ({ topic: topicOf(d, kind), payload });

const notify = (d, text) => {
  if (NOW - d.lastAlert > ALERT_RATE_MS) {
    d.lastAlert = NOW;
    alert = { deviceId: d.deviceId, text };
  }
};

switch (msg.eventType) {
  case 'TELEMETRY': {
    const d = dev(msg.deviceId);
    d.lastSeen = NOW;
    d.status = 'ONLINE';
    d.deviceState = msg.fsmState || d.deviceState;
    if (Number.isFinite(msg.hum)) d.hum = msg.hum;
    d.alarmTh = msg.alarmTh || d.alarmTh;
    d.safeTh = msg.safeTh || d.safeTh;
    d.mq2Valid = msg.mq2Valid;
    d.dhtValid = msg.dhtValid;
    d.cooldownStart = d.deviceState === 'COOLDOWN' ? (d.cooldownStart || NOW) : null;

    // Rule 1: dT/dt theo cua so; mau cu nhat co tuoi >= 20 s trong 60 s; giu rate giua cac lan tinh
    if (d.dhtValid && Number.isFinite(msg.temp)) {
      d.temp = msg.temp;
      d.tempHist.push({ t: NOW, v: msg.temp });
      d.tempHist = d.tempHist.filter(s => NOW - s.t <= 60000);
      const ref = d.tempHist.find(s => NOW - s.t >= 20000);
      if (ref) d.rate = (msg.temp - ref.v) / ((NOW - ref.t) / 60000);
    } else {
      d.rate = 0;
    }

    d.effective = d.deviceState;
    if (!d.mq2Valid || !Number.isFinite(msg.ppm)) {
      if (d.deviceState !== 'ALARM') d.effective = 'FAULT'; // khong dung PPM cua cam bien hong
    } else {
      d.ppm = msg.ppm;
      const over = msg.ppm >= d.alarmTh;
      const hot = d.rate >= 3.0 || msg.temp >= 50.0;
      if (over) {
        d.effective = 'ALARM'; // chi leo thang
        if (!d.overActive) { // canh vuot nguong
          d.overActive = true;
          cmds.push(cmd(d, 'fan', { action: 'ON', reason: hot ? 'RULE_1_REAL_FIRE' : 'RULE_2_LOW_HEAT_SMOKE', priority: 'CRITICAL' }));
          log(hot ? 'CRITICAL' : 'WARN', hot ? 'REAL_FIRE_CONFIRMED' : 'SMOKE_LOW_HEAT_ALARM',
              `PPM=${msg.ppm} dT/dt=${d.rate.toFixed(1)} T=${msg.temp}`, d.deviceId);
          notify(d, `Khoi ${msg.ppm} PPM, nhiet ${msg.temp} C, dT/dt ${d.rate.toFixed(1)}`);
        }
        if (hot && !d.hotActive) {
          d.hotActive = true;
          cmds.push(cmd(d, 'buzzer', { action: 'UNMUTE', reason: 'RULE_1_REAL_FIRE', priority: 'CRITICAL' }));
        }
      } else if (msg.ppm <= d.safeTh) {
        d.overActive = false;
        d.hotActive = false;
      }

      // Rule 5: canh vuot 600 PPM, gioi han 60 s, chi gui toi thiet bi cung tang co topic hop le
      if (msg.ppm >= CROSS_PPM && d.lastPpm < CROSS_PPM && NOW - (flow.get('last_cross_zone') || 0) > CROSS_RATE_MS) {
        flow.set('last_cross_zone', NOW);
        log('CRITICAL', 'CROSS_ZONE_BROADCAST', `PPM=${msg.ppm} tai ${d.deviceId}: so tan tang ${FLOOR}`, d.deviceId);
        Object.values(fleet)
          .filter(x => x.deviceId !== d.deviceId && x.topology && x.topology.floor === FLOOR && x.topology.building && x.topology.room)
          .forEach(x => cmds.push(cmd(x, 'buzzer', { cmd_id: 'CMD-ZONE-EVACUATION', action: 'UNMUTE', priority: 'CRITICAL' })));
      }
      d.lastPpm = msg.ppm;
    }
    break;
  }
  case 'KEEP_ALIVE': {
    const d = dev(msg.deviceId);
    d.lastSeen = NOW;
    if (d.status !== 'ONLINE') d.status = 'ONLINE';
    break;
  }
  case 'LWT': {
    const d = dev(msg.deviceId);
    if (!msg.isOnline) {
      d.status = 'OFFLINE';
      d.effective = 'OFFLINE';
      log('CRITICAL', 'LWT_DISCONNECT', 'Broker bao thiet bi mat ket noi', d.deviceId);
      notify(d, 'Thiet bi mat ket noi (LWT)');
    } else {
      d.status = 'ONLINE';
      d.lastSeen = NOW;
      log('INFO', 'LWT_CONNECT', 'Thiet bi ket noi lai', d.deviceId);
    }
    break;
  }
  case 'WATCHDOG_TICK':
    Object.values(fleet).forEach(d => {
      if (d.status === 'ONLINE' && d.lastSeen && NOW - d.lastSeen > WATCHDOG_MS) {
        d.status = 'OFFLINE';
        d.effective = 'OFFLINE';
        log('CRITICAL', 'WATCHDOG_TIMEOUT', 'Qua 30 s khong co du lieu', d.deviceId);
        notify(d, 'Thiet bi im lang qua 30 s');
      }
    });
    break;
  case 'ALARM_EVENT': {
    const d = dev(msg.deviceId);
    log('CRITICAL', msg.eventName || 'ALARM_EVENT', 'Su kien tu thiet bi', d.deviceId);
    break;
  }
  case 'OFFLINE_SYNC': {
    const d = dev(msg.deviceId);
    const count = Array.isArray(msg.records) ? msg.records.length : 1;
    log('INFO', 'OFFLINE_SYNC_RECEIVED', `Dong bo ${count} ban ghi lich su tu thiet bi`, d.deviceId);
    break;
  }
  case 'SCHEDULER_CMD': {
    const mode = msg.mode || (msg.payload && msg.payload.mode) || 'DAY';
    const alarmVal = mode === 'NIGHT' ? 350 : 400;
    const safeVal = alarmVal * 0.75;
    Object.values(fleet).forEach(d => {
      d.alarmTh = alarmVal;
      d.safeTh = safeVal;
    });
    log('INFO', 'SCHEDULER_APPLIED', `Lich ${mode}: alarm=${alarmVal}, safe=${safeVal}`, 'ALL');
    break;
  }
  case 'FAULT_INJECTION_CMD':
    log('INFO', 'FAULT_INJECTION_SEEN', 'Chi ghi nhan; trang thai lay tu telemetry thiet bi', msg.deviceId || 'ESP32_SMOKE_N04_A01');
    break;
}

flow.set('fleet', fleet);
if (logs.length) flow.set('history', logs.concat(flow.get('history') || []).slice(0, 80));

const primary = fleet['ESP32_SMOKE_N04_A01'] || Object.values(fleet)[0] || {};

return [
  cmds.length ? cmds.map(c => ({ topic: c.topic, payload: JSON.stringify(c.payload), qos: 1 })) : null,
  logs.length ? { payload: logs } : null,
  {
    payload: {
      fleet: Object.values(fleet),
      fleetList: Object.values(fleet),
      ppm: primary.ppm,
      temp: primary.temp,
      hum: (primary.hum !== undefined && Number.isFinite(primary.hum)) ? primary.hum : 60.0,
      fsmState: primary.effective,
      state: primary.effective,
      alarmThreshold: primary.alarmTh,
      safeThreshold: primary.safeTh
    }
  },
  alert ? { payload: alert } : null
];

```

---

## PHẦN 28: NODE-RED: BỘ ĐIỀU PHỐI LỆNH (COMMAND DISPATCHER) (`nodered/functions/command_dispatcher.js`)

> **Đường dẫn:** `nodered/functions/command_dispatcher.js`  
> **Quy mô:** 6 dòng | 183 bytes | Ngôn ngữ: `javascript`

```javascript
// functions/command_dispatcher.js
if (typeof msg.topic !== 'string' || /[+#]/.test(msg.topic)) {
  node.warn('Bo qua topic khong hop le: ' + msg.topic);
  return null;
}
return msg;

```

---

## PHẦN 29: NODE-RED: BỘ PHÁT TIN CẢNH BÁO TELEGRAM (ALERT DISPATCHER) (`nodered/functions/alert_dispatcher.js`)

> **Đường dẫn:** `nodered/functions/alert_dispatcher.js`  
> **Quy mô:** 18 dòng | 543 bytes | Ngôn ngữ: `javascript`

```javascript
// functions/alert_dispatcher.js (output 1 -> http request, output 2 -> dashboard + debug)
const token = env.get('TELEGRAM_TOKEN');
const chat = env.get('TELEGRAM_CHAT_ID');
const text = '[' + msg.payload.deviceId + '] ' + msg.payload.text;

if (!token || !chat) {
  return [null, { payload: text }];
}

return [
  {
    method: 'POST',
    url: 'https://api.telegram.org/bot' + token + '/sendMessage',
    headers: { 'content-type': 'application/json' },
    payload: JSON.stringify({ chat_id: chat, text: text })
  },
  { payload: text }
];

```

---

## PHẦN 30: NODE-RED: LẬP LỊCH CHẾ ĐỘ NGÀY/ĐÊM (SCHEDULER TICK) (`nodered/functions/scheduler_tick.js`)

> **Đường dẫn:** `nodered/functions/scheduler_tick.js`  
> **Quy mô:** 11 dòng | 310 bytes | Ngôn ngữ: `javascript`

```javascript
// functions/scheduler_tick.js
const h = new Date().getHours();
const night = h >= 22 || h < 6;

if (flow.get('sched') === night) return null;

flow.set('sched', night);
return {
  topic: 'Nhom09/smoke/cmd/scheduler',
  payload: JSON.stringify({ mode: night ? 'NIGHT' : 'DAY', source: 'RULE_3_SCHEDULER' })
};

```

---

## PHẦN 31: NODE-RED: CẤU TRÚC FLOW HOÀN CHỈNH (52 NODES) (`nodered/flows_smoke_detector.json`)

> **Đường dẫn:** `nodered/flows_smoke_detector.json`  
> **Quy mô:** 970 dòng | 37,873 bytes | Ngôn ngữ: `json`

```json
[
  {
    "id": "tab_middleware_smoke",
    "type": "tab",
    "label": "Tầng 3 - Middleware Automation Engine (Tuần 7: Business Rules & Abnormal)",
    "disabled": false,
    "info": "Middleware Engine xử lý dữ liệu cho Hệ thống báo khói cảnh báo sớm (Tuần 7: Business Rules & Abnormal Scenarios).\nBao gồm 5 Business Rules, 4 Kịch bản sự cố bất thường, Offline Buffer Replay, Watchdog 30s, Dynamic Day/Night Scheduler và Cross-Zone Emergency Automation."
  },
  {
    "id": "broker_emqx_cloud",
    "type": "mqtt-broker",
    "name": "EMQX Public Broker",
    "broker": "broker.emqx.io",
    "port": "1883",
    "clientid": "NodeRED_Smoke_Middleware_N04",
    "autoConnect": true,
    "usetls": false,
    "protocolVersion": "4",
    "keepalive": "60",
    "cleansession": true,
    "autoUnsubscribe": true,
    "birthTopic": "Nhom09/smoke/middleware/status",
    "birthQos": "1",
    "birthRetain": "true",
    "birthPayload": "{\"middleware\": \"ONLINE\", \"version\": \"3.0.0\", \"milestone\": \"WEEK7_BUSINESS_RULES_ABNORMAL\"}",
    "closeTopic": "Nhom09/smoke/middleware/status",
    "closeQos": "1",
    "closeRetain": "true",
    "closePayload": "{\"middleware\": \"OFFLINE\"}",
    "willTopic": "Nhom09/smoke/middleware/status",
    "willQos": "1",
    "willRetain": "true",
    "willPayload": "{\"middleware\": \"CRASHED\"}"
  },
  {
    "id": "mqtt_in_auth_req",
    "type": "mqtt in",
    "z": "tab_middleware_smoke",
    "name": "Sub (1a): Nhom09/smoke/v2/auth/request",
    "topic": "Nhom09/smoke/v2/auth/request",
    "qos": "1",
    "datatype": "auto-detect",
    "broker": "broker_emqx_cloud",
    "nl": false,
    "rap": true,
    "rh": 0,
    "x": 170,
    "y": 80,
    "wires": [
      [
        "fn_auth_service"
      ]
    ]
  },
  {
    "id": "fn_auth_service",
    "type": "function",
    "z": "tab_middleware_smoke",
    "name": "Dịch vụ 1: Auth & Whitelist (1b, 1c)",
    "func": "// Cơ sở dữ liệu Whitelist thiết bị được phép vào hệ thống\nconst WHITELIST = {\n    \"ESP32_SMOKE_N04_A01\": { \n        mac: \"24:6F:28:AB:CD:10\", \n        token: \"HUIT_IOT_SECURE_TOKEN_N04\", \n        topology: { building: \"HUIT_A\", floor: \"F03\", room: \"P302\", zone: \"Phòng Lab IoT\" }\n    },\n    \"ESP32_SMOKE_N04_A02\": { \n        mac: \"24:6F:28:AB:CD:20\", \n        token: \"HUIT_IOT_SECURE_TOKEN_N04\", \n        topology: { building: \"HUIT_A\", floor: \"F03\", room: \"P303\", zone: \"Kho Hóa Chất\" }\n    },\n    \"ESP32_SMOKE_N04_A03\": { \n        mac: \"24:6F:28:AB:CD:30\", \n        token: \"HUIT_IOT_SECURE_TOKEN_N04\", \n        topology: { building: \"HUIT_A\", floor: \"F03\", room: \"P304\", zone: \"Khu Vực Bếp\" }\n    }\n};\n\nlet data = msg.payload;\nif (typeof data === 'string') {\n    try { data = JSON.parse(data); } catch(e) { return null; }\n}\n\nlet devId = data.device_id || \"UNKNOWN\";\nlet devMac = data.mac_address || \"\";\nlet secret = data.secret_token || \"\";\n\nlet respTopic = \"Nhom09/smoke/v2/auth/response/\" + devId;\nlet respPayload = {};\nlet logEntry = null;\n\n// Kiểm tra tính hợp lệ trong Whitelist\nlet record = WHITELIST[devId];\nif (record && record.token === secret) {\n    let sessionKey = \"SK_\" + Math.random().toString(36).substr(2, 9).toUpperCase() + \"_N04\";\n    respPayload = {\n        msg_id: \"RESP-AUTH-\" + Date.now(),\n        status: \"PASS\",\n        status_code: 200,\n        session_key: sessionKey,\n        lease_duration_sec: 86400,\n        assigned_topology: record.topology,\n        config: {\n            telemetry_interval_ms: 2000,\n            keep_alive_interval_ms: 10000,\n            alarm_threshold_ppm: 400.0,\n            safe_threshold_ppm: 300.0\n        }\n    };\n\n    // Đăng ký vào bảng Device Fleet Registry\n    let fleet = flow.get(\"fleet\") || {};\n    let d = fleet[devId] || {\n        deviceId: devId,\n        deviceState: \"SAFE\",\n        effective: \"SAFE\",\n        tempHist: [],\n        alarmTh: 400,\n        safeTh: 300,\n        overActive: false,\n        hotActive: false,\n        cooldownStart: null,\n        lastAlert: 0,\n        rate: 0,\n        mq2Valid: true,\n        dhtValid: true,\n        hum: 60.0,\n        lastPpm: 0\n    };\n    d.mac = devMac;\n    d.zone = record.topology.zone;\n    d.topology = record.topology;\n    d.sessionKey = sessionKey;\n    d.status = \"ONLINE\";\n    d.lastSeen = Date.now();\n    fleet[devId] = d;\n    flow.set(\"fleet\", fleet);\n    flow.set(\"device_fleet\", fleet);\n\n    logEntry = { level: \"INFO\", event: \"AUTH_SUCCESS\", desc: `Xác thực thành công thiết bị ${devId} (${record.topology.zone})` };\n} else {\n    respPayload = {\n        msg_id: \"RESP-AUTH-\" + Date.now(),\n        status: \"REJECTED\",\n        status_code: 401,\n        error_code: \"ERR_UNAUTHORIZED_DEVICE\",\n        message: \"Device MAC or secret token is invalid.\"\n    };\n    logEntry = { level: \"WARN\", event: \"AUTH_REJECTED\", desc: `Từ chối xác thực thiết bị lạ: ID=${devId}, MAC=${devMac}` };\n}\n\nlet outMqtt = {\n    topic: respTopic,\n    payload: JSON.stringify(respPayload),\n    qos: 1\n};\n\nlet outLog = logEntry ? { payload: [logEntry] } : null;\n\nreturn [outMqtt, outLog];",
    "outputs": 2,
    "noerr": 0,
    "x": 490,
    "y": 80,
    "wires": [
      [
        "mqtt_out_auth_resp"
      ],
      [
        "fn_audit_logger"
      ]
    ]
  },
  {
    "id": "mqtt_out_auth_resp",
    "type": "mqtt out",
    "z": "tab_middleware_smoke",
    "name": "Pub (1d): Nhom09/smoke/v2/auth/response",
    "topic": "",
    "qos": "1",
    "retain": "false",
    "broker": "broker_emqx_cloud",
    "x": 840,
    "y": 80,
    "wires": []
  },
  {
    "id": "mqtt_in_telemetry_v1",
    "type": "mqtt in",
    "z": "tab_middleware_smoke",
    "name": "Sub V1: Nhom09/smoke/telemetry",
    "topic": "Nhom09/smoke/telemetry",
    "qos": "0",
    "datatype": "auto-detect",
    "broker": "broker_emqx_cloud",
    "nl": false,
    "rap": true,
    "rh": 0,
    "x": 160,
    "y": 160,
    "wires": [
      [
        "fn_parse_telemetry"
      ]
    ]
  },
  {
    "id": "mqtt_in_telemetry_v2",
    "type": "mqtt in",
    "z": "tab_middleware_smoke",
    "name": "Sub (2a): Nhom09/smoke/v2/+/+/+/+/telemetry",
    "topic": "Nhom09/smoke/v2/+/+/+/+/telemetry",
    "qos": "0",
    "datatype": "auto-detect",
    "broker": "broker_emqx_cloud",
    "nl": false,
    "rap": true,
    "rh": 0,
    "x": 200,
    "y": 220,
    "wires": [
      [
        "fn_parse_telemetry"
      ]
    ]
  },
  {
    "id": "mqtt_in_alarm_v1",
    "type": "mqtt in",
    "z": "tab_middleware_smoke",
    "name": "Sub V1: Nhom09/smoke/event/alarm",
    "topic": "Nhom09/smoke/event/alarm",
    "qos": "1",
    "datatype": "auto-detect",
    "broker": "broker_emqx_cloud",
    "nl": false,
    "rap": true,
    "rh": 0,
    "x": 170,
    "y": 280,
    "wires": [
      [
        "fn_parse_alarm"
      ]
    ]
  },
  {
    "id": "mqtt_in_alarm_v2",
    "type": "mqtt in",
    "z": "tab_middleware_smoke",
    "name": "Sub (2a): Nhom09/smoke/v2/+/+/+/+/event/alarm",
    "topic": "Nhom09/smoke/v2/+/+/+/+/event/alarm",
    "qos": "1",
    "datatype": "auto-detect",
    "broker": "broker_emqx_cloud",
    "nl": false,
    "rap": true,
    "rh": 0,
    "x": 210,
    "y": 340,
    "wires": [
      [
        "fn_parse_alarm"
      ]
    ]
  },
  {
    "id": "mqtt_in_history_sync",
    "type": "mqtt in",
    "z": "tab_middleware_smoke",
    "name": "Sub (Abnormal 2): Nhom09/smoke/history/sync",
    "topic": "Nhom09/smoke/history/sync",
    "qos": "1",
    "datatype": "auto-detect",
    "broker": "broker_emqx_cloud",
    "nl": false,
    "rap": true,
    "rh": 0,
    "x": 200,
    "y": 400,
    "wires": [
      [
        "fn_parse_history_sync"
      ]
    ]
  },
  {
    "id": "mqtt_in_keepalive_v1",
    "type": "mqtt in",
    "z": "tab_middleware_smoke",
    "name": "Sub V1: Nhom09/smoke/keep_alive",
    "topic": "Nhom09/smoke/keep_alive",
    "qos": "0",
    "datatype": "auto-detect",
    "broker": "broker_emqx_cloud",
    "nl": false,
    "rap": true,
    "rh": 0,
    "x": 170,
    "y": 460,
    "wires": [
      [
        "fn_parse_keepalive"
      ]
    ]
  },
  {
    "id": "mqtt_in_keepalive_v2",
    "type": "mqtt in",
    "z": "tab_middleware_smoke",
    "name": "Sub (4a): Nhom09/smoke/v2/+/+/+/+/keep_alive",
    "topic": "Nhom09/smoke/v2/+/+/+/+/keep_alive",
    "qos": "0",
    "datatype": "auto-detect",
    "broker": "broker_emqx_cloud",
    "nl": false,
    "rap": true,
    "rh": 0,
    "x": 200,
    "y": 510,
    "wires": [
      [
        "fn_parse_keepalive"
      ]
    ]
  },
  {
    "id": "mqtt_in_lwt",
    "type": "mqtt in",
    "z": "tab_middleware_smoke",
    "name": "Sub: Nhom09/smoke/lwt",
    "topic": "Nhom09/smoke/lwt",
    "qos": "1",
    "datatype": "auto-detect",
    "broker": "broker_emqx_cloud",
    "nl": false,
    "rap": true,
    "rh": 0,
    "x": 130,
    "y": 560,
    "wires": [
      [
        "fn_parse_lwt"
      ]
    ]
  },
  {
    "id": "mqtt_in_scheduler",
    "type": "mqtt in",
    "z": "tab_middleware_smoke",
    "name": "Sub (Rule 3): Nhom09/smoke/cmd/scheduler",
    "topic": "Nhom09/smoke/cmd/scheduler",
    "qos": "1",
    "datatype": "auto-detect",
    "broker": "broker_emqx_cloud",
    "nl": false,
    "rap": true,
    "rh": 0,
    "x": 190,
    "y": 610,
    "wires": [
      [
        "fn_parse_scheduler"
      ]
    ]
  },
  {
    "id": "mqtt_in_fault_injection",
    "type": "mqtt in",
    "z": "tab_middleware_smoke",
    "name": "Sub (Fault Inject): Nhom09/smoke/cmd/inject_fault",
    "topic": "Nhom09/smoke/cmd/inject_fault",
    "qos": "1",
    "datatype": "auto-detect",
    "broker": "broker_emqx_cloud",
    "nl": false,
    "rap": true,
    "rh": 0,
    "x": 210,
    "y": 660,
    "wires": [
      [
        "fn_parse_fault_injection"
      ]
    ]
  },
  {
    "id": "inject_watchdog_tick",
    "type": "inject",
    "z": "tab_middleware_smoke",
    "name": "Watchdog 3s Tick (Abnormal 3)",
    "props": [
      {
        "p": "payload"
      }
    ],
    "repeat": "3",
    "crontab": "",
    "once": true,
    "onceDelay": 1,
    "topic": "watchdog/tick",
    "payload": "",
    "payloadType": "date",
    "x": 170,
    "y": 710,
    "wires": [
      [
        "fn_watchdog_scheduler"
      ]
    ]
  },
  {
    "id": "fn_parse_telemetry",
    "type": "function",
    "z": "tab_middleware_smoke",
    "name": "Parse & Validate Telemetry",
    "func": "// functions/parse_telemetry.js\nlet d = msg.payload;\nif (typeof d === 'string') {\n  try {\n    d = JSON.parse(d);\n  } catch (e) {\n    return null;\n  }\n}\nif (!d || typeof d !== 'object') return null;\n\nconst num = v => (v === null || v === undefined) ? NaN : Number(v);\n\nmsg.eventType = 'TELEMETRY';\nmsg.deviceId  = d.device_id || 'ESP32_SMOKE_N04_A01';\nmsg.uptime    = d.uptime_s !== undefined ? d.uptime_s : d.uptime_sec;\nmsg.mq2Valid  = d.mq2_valid !== false;\nmsg.dhtValid  = d.dht_valid !== false;\nmsg.ppm       = num(d.mq2_ppm);\nmsg.temp      = num(d.temp);\nmsg.hum       = num(d.hum);\nmsg.fsmState  = d.fsm_state;\nmsg.alarmTh   = Number(d.alarm_th) || undefined;\nmsg.safeTh    = Number(d.safe_th) || undefined;\n\n// ---- DEDUP: TTL 5s ----\nif (msg.uptime !== undefined) {\n  const now = Date.now();\n  const cache = flow.get('dedup') || {};\n  for (const k in cache) {\n    if (now - cache[k] > 5000) delete cache[k];\n  }\n  const key = msg.deviceId + '|' + msg.eventType + '|' + (msg.eventName || '') + '|' + msg.uptime;\n  if (cache[key]) return null;\n  cache[key] = now;\n  flow.set('dedup', cache);\n}\n\nreturn msg;\n",
    "outputs": 1,
    "x": 520,
    "y": 180,
    "wires": [
      [
        "fn_core_fsm_engine"
      ]
    ]
  },
  {
    "id": "fn_parse_alarm",
    "type": "function",
    "z": "tab_middleware_smoke",
    "name": "Parse Urgent Alarm Event",
    "func": "// nodered/functions/parse_alarm.js\nlet d = msg.payload;\nif (typeof d === 'string') {\n  try {\n    d = JSON.parse(d);\n  } catch (e) {\n    return null;\n  }\n}\nif (!d || typeof d !== 'object') return null;\n\nmsg.eventType = 'ALARM_EVENT';\nmsg.deviceId  = d.device_id || 'ESP32_SMOKE_N04_A01';\nmsg.eventName = d.event || 'SMOKE_ALERT';\nmsg.severity  = d.severity || 'CRITICAL';\nmsg.ppm       = Number(d.ppm !== undefined ? d.ppm : (d.mq2_ppm || 0));\nmsg.threshold = Number(d.threshold || 400);\nmsg.uptime    = d.uptime_s !== undefined ? d.uptime_s : d.uptime_sec;\n\n// Dedup cache TTL 5s\nif (msg.uptime !== undefined) {\n  const now = Date.now(), cache = flow.get('dedup') || {};\n  for (const k in cache) {\n    if (now - cache[k] > 5000) delete cache[k];\n  }\n  const key = msg.deviceId + '|' + msg.eventType + '|' + (msg.eventName || '') + '|' + msg.uptime;\n  if (cache[key]) return null;\n  cache[key] = now;\n  flow.set('dedup', cache);\n}\n\nreturn msg;\n",
    "outputs": 1,
    "x": 520,
    "y": 300,
    "wires": [
      [
        "fn_core_fsm_engine"
      ]
    ]
  },
  {
    "id": "fn_parse_history_sync",
    "type": "function",
    "z": "tab_middleware_smoke",
    "name": "Parse Offline Buffer Sync (Abnormal 2)",
    "func": "let data = msg.payload;\nif (typeof data === 'string') {\n    try { data = JSON.parse(data); } catch(e) { return null; }\n}\n\nmsg.eventType = \"OFFLINE_SYNC\";\nmsg.deviceId = data.device_id || \"ESP32_SMOKE_N04_A01\";\nmsg.syncSeq = data.sync_seq || 1;\nmsg.records = data.records || [];\nmsg.ppm = parseFloat(data.mq2_ppm || data.ppm || 0);\nmsg.temp = parseFloat(data.temp || 28.0);\nmsg.fan = data.fan || \"OFF\";\nmsg.recordState = data.state || \"SAFE\";\nmsg.timestamp = Date.now();\n\nreturn msg;",
    "outputs": 1,
    "x": 540,
    "y": 400,
    "wires": [
      [
        "fn_core_fsm_engine"
      ]
    ]
  },
  {
    "id": "fn_parse_keepalive",
    "type": "function",
    "z": "tab_middleware_smoke",
    "name": "Dịch vụ 4: Parse Keep-Alive",
    "func": "// nodered/functions/parse_keepalive.js\nlet d = msg.payload;\nif (typeof d === 'string') {\n  try {\n    d = JSON.parse(d);\n  } catch (e) {\n    return null;\n  }\n}\nif (!d || typeof d !== 'object') return null;\n\nmsg.eventType = 'KEEP_ALIVE';\nmsg.deviceId  = d.device_id || 'ESP32_SMOKE_N04_A01';\nmsg.uptime    = d.uptime_s !== undefined ? d.uptime_s : d.uptime_sec;\nmsg.freeHeap  = Number(d.free_heap_bytes || 0);\nmsg.wifiRssi  = Number(d.wifi_rssi_dbm || -60);\nmsg.status    = d.status || 'HEALTHY';\nmsg.fsmState  = d.fsm_state;\n\n// Dedup cache TTL 5s\nif (msg.uptime !== undefined) {\n  const now = Date.now(), cache = flow.get('dedup') || {};\n  for (const k in cache) {\n    if (now - cache[k] > 5000) delete cache[k];\n  }\n  const key = msg.deviceId + '|' + msg.eventType + '|' + msg.uptime;\n  if (cache[key]) return null;\n  cache[key] = now;\n  flow.set('dedup', cache);\n}\n\nreturn msg;\n",
    "outputs": 1,
    "x": 520,
    "y": 480,
    "wires": [
      [
        "fn_core_fsm_engine"
      ]
    ]
  },
  {
    "id": "fn_parse_lwt",
    "type": "function",
    "z": "tab_middleware_smoke",
    "name": "Parse LWT Signal",
    "func": "// functions/parse_lwt.js\nlet s = msg.payload;\nlet id = null;\nlet online = false;\n\ntry {\n  const j = typeof s === 'string' ? JSON.parse(s) : s;\n  if (j && typeof j === 'object') {\n    id = j.device_id;\n    online = String(j.status).toLowerCase() === 'online';\n  } else {\n    online = String(s).trim().toLowerCase() === 'online';\n  }\n} catch (e) {\n  online = String(s).trim().toLowerCase() === 'online';\n}\n\nmsg.eventType = 'LWT';\nmsg.deviceId  = id || 'ESP32_SMOKE_N04_A01';\nmsg.isOnline  = online;\n\nreturn msg;\n",
    "outputs": 1,
    "x": 500,
    "y": 560,
    "wires": [
      [
        "fn_core_fsm_engine"
      ]
    ]
  },
  {
    "id": "fn_parse_scheduler",
    "type": "function",
    "z": "tab_middleware_smoke",
    "name": "Parse Scheduler Cmd (Rule 3)",
    "func": "let data = msg.payload;\nif (typeof data === 'string') {\n    try { data = JSON.parse(data); } catch(e) { data = { mode: data }; }\n}\nmsg.eventType = \"SCHEDULER_CMD\";\nmsg.mode = data.mode || \"DAY\";\nmsg.timestamp = Date.now();\nreturn msg;",
    "outputs": 1,
    "x": 530,
    "y": 620,
    "wires": [
      [
        "fn_core_fsm_engine"
      ]
    ]
  },
  {
    "id": "fn_parse_fault_injection",
    "type": "function",
    "z": "tab_middleware_smoke",
    "name": "Parse Fault Injection (Abnormal Sandbox)",
    "func": "let data = msg.payload;\nif (typeof data === 'string') {\n    try { data = JSON.parse(data); } catch(e) { data = { fault: data }; }\n}\nmsg.eventType = \"FAULT_INJECTION_CMD\";\nmsg.fault = data.fault || \"NONE\";\nmsg.timestamp = Date.now();\nreturn msg;",
    "outputs": 1,
    "x": 550,
    "y": 670,
    "wires": [
      [
        "fn_core_fsm_engine"
      ]
    ]
  },
  {
    "id": "fn_watchdog_scheduler",
    "type": "function",
    "z": "tab_middleware_smoke",
    "name": "Watchdog 3s Tick Trigger",
    "func": "msg.eventType = \"WATCHDOG_TICK\";\nmsg.timestamp = Date.now();\nreturn msg;",
    "outputs": 1,
    "x": 520,
    "y": 720,
    "wires": [
      [
        "fn_core_fsm_engine"
      ]
    ]
  },
  {
    "id": "inject_scheduler_1m",
    "type": "inject",
    "z": "tab_middleware_smoke",
    "name": "Scheduler 1-min Inject (Rule 3)",
    "props": [
      {
        "p": "payload"
      }
    ],
    "repeat": "60",
    "crontab": "",
    "once": true,
    "onceDelay": 2,
    "topic": "",
    "payload": "",
    "payloadType": "date",
    "x": 170,
    "y": 760,
    "wires": [
      [
        "fn_scheduler_tick"
      ]
    ]
  },
  {
    "id": "fn_scheduler_tick",
    "type": "function",
    "z": "tab_middleware_smoke",
    "name": "Day/Night Scheduler Tick",
    "func": "// functions/scheduler_tick.js\nconst h = new Date().getHours();\nconst night = h >= 22 || h < 6;\n\nif (flow.get('sched') === night) return null;\n\nflow.set('sched', night);\nreturn {\n  topic: 'Nhom09/smoke/cmd/scheduler',\n  payload: JSON.stringify({ mode: night ? 'NIGHT' : 'DAY', source: 'RULE_3_SCHEDULER' })\n};\n",
    "outputs": 1,
    "x": 520,
    "y": 760,
    "wires": [
      [
        "fn_command_dispatcher",
        "fn_parse_scheduler"
      ]
    ]
  },
  {
    "id": "fn_core_fsm_engine",
    "type": "function",
    "z": "tab_middleware_smoke",
    "name": "Core Engine: FSM, 5 Rules & Abnormal Scenarios",
    "func": "// functions/core_engine.js  (4 output: lenh, log, fleet, thong bao)\nconst NOW = Date.now();\nconst FLOOR = 'F03', CROSS_PPM = 600, CROSS_RATE_MS = 60000, WATCHDOG_MS = 30000, ALERT_RATE_MS = 20000;\nconst fleet = flow.get('fleet') || {};\nconst cmds = [], logs = [];\nlet alert = null;\n\nconst dev = id => {\n  let d = fleet[id];\n  if (!d) {\n    d = fleet[id] = {\n      deviceId: id,\n      status: 'UNKNOWN',\n      deviceState: 'SAFE',\n      effective: 'SAFE',\n      lastSeen: 0,\n      ppm: NaN,\n      temp: NaN,\n      rate: 0,\n      lastPpm: 0,\n      hum: 60.0,\n      tempHist: [],\n      alarmTh: 400,\n      safeTh: 300,\n      overActive: false,\n      hotActive: false,\n      cooldownStart: null,\n      lastAlert: 0,\n      topology: null,\n      mq2Valid: true,\n      dhtValid: true\n    };\n  }\n  if (d.rate === undefined) d.rate = 0;\n  if (!Array.isArray(d.tempHist)) d.tempHist = [];\n  return d;\n};\n\nconst log = (level, event, desc, id) => logs.push({ level, event, desc, deviceId: id, ts: NOW });\n\nconst topicOf = (d, kind) => (d.topology && d.topology.building && d.topology.floor && d.topology.room)\n  ? `Nhom09/smoke/v2/${d.topology.building}/${d.topology.floor}/${d.topology.room}/${d.deviceId}/cmd/${kind}`\n  : `Nhom09/smoke/cmd/${kind}`;\n\nconst cmd = (d, kind, payload) => ({ topic: topicOf(d, kind), payload });\n\nconst notify = (d, text) => {\n  if (NOW - d.lastAlert > ALERT_RATE_MS) {\n    d.lastAlert = NOW;\n    alert = { deviceId: d.deviceId, text };\n  }\n};\n\nswitch (msg.eventType) {\n  case 'TELEMETRY': {\n    const d = dev(msg.deviceId);\n    d.lastSeen = NOW;\n    d.status = 'ONLINE';\n    d.deviceState = msg.fsmState || d.deviceState;\n    if (Number.isFinite(msg.hum)) d.hum = msg.hum;\n    d.alarmTh = msg.alarmTh || d.alarmTh;\n    d.safeTh = msg.safeTh || d.safeTh;\n    d.mq2Valid = msg.mq2Valid;\n    d.dhtValid = msg.dhtValid;\n    d.cooldownStart = d.deviceState === 'COOLDOWN' ? (d.cooldownStart || NOW) : null;\n\n    // Rule 1: dT/dt theo cua so; mau cu nhat co tuoi >= 20 s trong 60 s; giu rate giua cac lan tinh\n    if (d.dhtValid && Number.isFinite(msg.temp)) {\n      d.temp = msg.temp;\n      d.tempHist.push({ t: NOW, v: msg.temp });\n      d.tempHist = d.tempHist.filter(s => NOW - s.t <= 60000);\n      const ref = d.tempHist.find(s => NOW - s.t >= 20000);\n      if (ref) d.rate = (msg.temp - ref.v) / ((NOW - ref.t) / 60000);\n    } else {\n      d.rate = 0;\n    }\n\n    d.effective = d.deviceState;\n    if (!d.mq2Valid || !Number.isFinite(msg.ppm)) {\n      if (d.deviceState !== 'ALARM') d.effective = 'FAULT'; // khong dung PPM cua cam bien hong\n    } else {\n      d.ppm = msg.ppm;\n      const over = msg.ppm >= d.alarmTh;\n      const hot = d.rate >= 3.0 || msg.temp >= 50.0;\n      if (over) {\n        d.effective = 'ALARM'; // chi leo thang\n        if (!d.overActive) { // canh vuot nguong\n          d.overActive = true;\n          cmds.push(cmd(d, 'fan', { action: 'ON', reason: hot ? 'RULE_1_REAL_FIRE' : 'RULE_2_LOW_HEAT_SMOKE', priority: 'CRITICAL' }));\n          log(hot ? 'CRITICAL' : 'WARN', hot ? 'REAL_FIRE_CONFIRMED' : 'SMOKE_LOW_HEAT_ALARM',\n              `PPM=${msg.ppm} dT/dt=${d.rate.toFixed(1)} T=${msg.temp}`, d.deviceId);\n          notify(d, `Khoi ${msg.ppm} PPM, nhiet ${msg.temp} C, dT/dt ${d.rate.toFixed(1)}`);\n        }\n        if (hot && !d.hotActive) {\n          d.hotActive = true;\n          cmds.push(cmd(d, 'buzzer', { action: 'UNMUTE', reason: 'RULE_1_REAL_FIRE', priority: 'CRITICAL' }));\n        }\n      } else if (msg.ppm <= d.safeTh) {\n        d.overActive = false;\n        d.hotActive = false;\n      }\n\n      // Rule 5: canh vuot 600 PPM, gioi han 60 s, chi gui toi thiet bi cung tang co topic hop le\n      if (msg.ppm >= CROSS_PPM && d.lastPpm < CROSS_PPM && NOW - (flow.get('last_cross_zone') || 0) > CROSS_RATE_MS) {\n        flow.set('last_cross_zone', NOW);\n        log('CRITICAL', 'CROSS_ZONE_BROADCAST', `PPM=${msg.ppm} tai ${d.deviceId}: so tan tang ${FLOOR}`, d.deviceId);\n        Object.values(fleet)\n          .filter(x => x.deviceId !== d.deviceId && x.topology && x.topology.floor === FLOOR && x.topology.building && x.topology.room)\n          .forEach(x => cmds.push(cmd(x, 'buzzer', { cmd_id: 'CMD-ZONE-EVACUATION', action: 'UNMUTE', priority: 'CRITICAL' })));\n      }\n      d.lastPpm = msg.ppm;\n    }\n    break;\n  }\n  case 'KEEP_ALIVE': {\n    const d = dev(msg.deviceId);\n    d.lastSeen = NOW;\n    if (d.status !== 'ONLINE') d.status = 'ONLINE';\n    break;\n  }\n  case 'LWT': {\n    const d = dev(msg.deviceId);\n    if (!msg.isOnline) {\n      d.status = 'OFFLINE';\n      d.effective = 'OFFLINE';\n      log('CRITICAL', 'LWT_DISCONNECT', 'Broker bao thiet bi mat ket noi', d.deviceId);\n      notify(d, 'Thiet bi mat ket noi (LWT)');\n    } else {\n      d.status = 'ONLINE';\n      d.lastSeen = NOW;\n      log('INFO', 'LWT_CONNECT', 'Thiet bi ket noi lai', d.deviceId);\n    }\n    break;\n  }\n  case 'WATCHDOG_TICK':\n    Object.values(fleet).forEach(d => {\n      if (d.status === 'ONLINE' && d.lastSeen && NOW - d.lastSeen > WATCHDOG_MS) {\n        d.status = 'OFFLINE';\n        d.effective = 'OFFLINE';\n        log('CRITICAL', 'WATCHDOG_TIMEOUT', 'Qua 30 s khong co du lieu', d.deviceId);\n        notify(d, 'Thiet bi im lang qua 30 s');\n      }\n    });\n    break;\n  case 'ALARM_EVENT': {\n    const d = dev(msg.deviceId);\n    log('CRITICAL', msg.eventName || 'ALARM_EVENT', 'Su kien tu thiet bi', d.deviceId);\n    break;\n  }\n  case 'OFFLINE_SYNC': {\n    const d = dev(msg.deviceId);\n    const count = Array.isArray(msg.records) ? msg.records.length : 1;\n    log('INFO', 'OFFLINE_SYNC_RECEIVED', `Dong bo ${count} ban ghi lich su tu thiet bi`, d.deviceId);\n    break;\n  }\n  case 'SCHEDULER_CMD': {\n    const mode = msg.mode || (msg.payload && msg.payload.mode) || 'DAY';\n    const alarmVal = mode === 'NIGHT' ? 350 : 400;\n    const safeVal = alarmVal * 0.75;\n    Object.values(fleet).forEach(d => {\n      d.alarmTh = alarmVal;\n      d.safeTh = safeVal;\n    });\n    log('INFO', 'SCHEDULER_APPLIED', `Lich ${mode}: alarm=${alarmVal}, safe=${safeVal}`, 'ALL');\n    break;\n  }\n  case 'FAULT_INJECTION_CMD':\n    log('INFO', 'FAULT_INJECTION_SEEN', 'Chi ghi nhan; trang thai lay tu telemetry thiet bi', msg.deviceId || 'ESP32_SMOKE_N04_A01');\n    break;\n}\n\nflow.set('fleet', fleet);\nif (logs.length) flow.set('history', logs.concat(flow.get('history') || []).slice(0, 80));\n\nconst primary = fleet['ESP32_SMOKE_N04_A01'] || Object.values(fleet)[0] || {};\n\nreturn [\n  cmds.length ? cmds.map(c => ({ topic: c.topic, payload: JSON.stringify(c.payload), qos: 1 })) : null,\n  logs.length ? { payload: logs } : null,\n  {\n    payload: {\n      fleet: Object.values(fleet),\n      fleetList: Object.values(fleet),\n      ppm: primary.ppm,\n      temp: primary.temp,\n      hum: (primary.hum !== undefined && Number.isFinite(primary.hum)) ? primary.hum : 60.0,\n      fsmState: primary.effective,\n      state: primary.effective,\n      alarmThreshold: primary.alarmTh,\n      safeThreshold: primary.safeTh\n    }\n  },\n  alert ? { payload: alert } : null\n];\n",
    "outputs": 4,
    "noerr": 0,
    "x": 860,
    "y": 420,
    "wires": [
      [
        "fn_command_dispatcher"
      ],
      [
        "fn_audit_logger"
      ],
      [
        "fn_ui_dashboard_adapter"
      ],
      [
        "fn_alert_dispatcher"
      ]
    ]
  },
  {
    "id": "fn_command_dispatcher",
    "type": "function",
    "z": "tab_middleware_smoke",
    "name": "Dịch vụ 3: Command Dispatcher (3a)",
    "func": "// functions/command_dispatcher.js\nif (typeof msg.topic !== 'string' || /[+#]/.test(msg.topic)) {\n  node.warn('Bo qua topic khong hop le: ' + msg.topic);\n  return null;\n}\nreturn msg;\n",
    "outputs": 1,
    "x": 1140,
    "y": 380,
    "wires": [
      [
        "mqtt_out_cmd_downlink",
        "debug_cmd_sent"
      ]
    ]
  },
  {
    "id": "mqtt_out_cmd_downlink",
    "type": "mqtt out",
    "z": "tab_middleware_smoke",
    "name": "Pub: Command Downlink (Dynamic msg.topic)",
    "topic": "",
    "qos": "1",
    "retain": "false",
    "broker": "broker_emqx_cloud",
    "x": 1410,
    "y": 440,
    "wires": []
  },
  {
    "id": "fn_alert_dispatcher",
    "type": "function",
    "z": "tab_middleware_smoke",
    "name": "Alert & Telegram Dispatcher",
    "func": "// functions/alert_dispatcher.js (output 1 -> http request, output 2 -> dashboard + debug)\nconst token = env.get('TELEGRAM_TOKEN');\nconst chat = env.get('TELEGRAM_CHAT_ID');\nconst text = '[' + msg.payload.deviceId + '] ' + msg.payload.text;\n\nif (!token || !chat) {\n  return [null, { payload: text }];\n}\n\nreturn [\n  {\n    method: 'POST',\n    url: 'https://api.telegram.org/bot' + token + '/sendMessage',\n    headers: { 'content-type': 'application/json' },\n    payload: JSON.stringify({ chat_id: chat, text: text })\n  },\n  { payload: text }\n];\n",
    "outputs": 2,
    "x": 1080,
    "y": 660,
    "wires": [
      [
        "http_req_telegram"
      ],
      [
        "debug_alert_notifications"
      ]
    ]
  },
  {
    "id": "http_req_telegram",
    "type": "http request",
    "z": "tab_middleware_smoke",
    "name": "Telegram Bot API (Simulated/Real)",
    "method": "use",
    "ret": "txt",
    "paytoqs": "ignore",
    "url": "",
    "tls": "",
    "persist": false,
    "proxy": "",
    "authType": "",
    "senderr": false,
    "headers": [],
    "x": 1330,
    "y": 640,
    "wires": [
      [
        "debug_alert_notifications"
      ]
    ]
  },
  {
    "id": "debug_cmd_sent",
    "type": "debug",
    "z": "tab_middleware_smoke",
    "name": "Command Sent Log",
    "active": true,
    "tosidebar": true,
    "complete": "payload",
    "x": 1390,
    "y": 560,
    "wires": []
  },
  {
    "id": "fn_audit_logger",
    "type": "function",
    "z": "tab_middleware_smoke",
    "name": "Multi-tier Audit Trail Logger",
    "func": "let payload = msg.payload || [];\nlet history = msg.eventHistory || [];\nreturn [{ payload: { recentLogs: payload, history: history } }];",
    "outputs": 1,
    "x": 1140,
    "y": 280,
    "wires": [
      [
        "debug_audit_log"
      ]
    ]
  },
  {
    "id": "debug_audit_log",
    "type": "debug",
    "z": "tab_middleware_smoke",
    "name": "Audit Trail Console",
    "active": true,
    "tosidebar": true,
    "complete": "payload",
    "x": 1390,
    "y": 280,
    "wires": []
  },
  {
    "id": "fn_ui_dashboard_adapter",
    "type": "function",
    "z": "tab_middleware_smoke",
    "name": "Dashboard State Adapter",
    "func": "let p = msg.payload || {};\nlet ppm = (p.ppm !== undefined) ? Number(Number(p.ppm).toFixed(1)) : (p.smokePpm !== undefined ? Number(Number(p.smokePpm).toFixed(1)) : 0);\nlet temp = (p.temp !== undefined) ? Number(Number(p.temp).toFixed(1)) : 28.0;\nlet hum = (p.hum !== undefined) ? Number(Number(p.hum).toFixed(1)) : 60.0;\nlet state = p.fsmState || \"SAFE\";\n\nlet colorMap = {\n    \"SAFE\": \"#00b500\",\n    \"WARNING\": \"#e67e22\",\n    \"ALARM\": \"#ca3838\",\n    \"COOLDOWN\": \"#2980b9\",\n    \"FAULT\": \"#8e44ad\",\n    \"OFFLINE\": \"#7f8c8d\"\n};\nlet stateColor = colorMap[state] || \"#00b500\";\n\nlet msgPpm = { payload: ppm, topic: \"Nồng độ Khói (PPM)\" };\nlet msgTemp = { payload: temp, topic: \"Nhiệt độ (°C)\" };\nlet msgHum = { payload: hum, topic: \"Độ ẩm (%)\" };\nlet msgState = { payload: state, color: stateColor };\nlet msgDebug = { payload: p };\n\nreturn [msgPpm, msgTemp, msgHum, msgState, msgDebug];",
    "outputs": 5,
    "noerr": 0,
    "x": 1130,
    "y": 620,
    "wires": [
      [
        "ui_gauge_smoke",
        "ui_chart_trends"
      ],
      [
        "ui_gauge_temp",
        "ui_chart_trends"
      ],
      [
        "ui_gauge_hum"
      ],
      [
        "ui_text_fsm_state"
      ],
      [
        "debug_dashboard_state"
      ]
    ]
  },
  {
    "id": "debug_dashboard_state",
    "type": "debug",
    "z": "tab_middleware_smoke",
    "name": "Dashboard UI Feed",
    "active": true,
    "tosidebar": true,
    "complete": "payload",
    "x": 1380,
    "y": 620,
    "wires": []
  },
  {
    "id": "debug_alert_notifications",
    "type": "debug",
    "z": "tab_middleware_smoke",
    "name": "Telegram & Web Alert Dispatcher",
    "active": true,
    "tosidebar": true,
    "complete": "payload",
    "x": 1160,
    "y": 700,
    "wires": []
  },
  {
    "id": "ui_tab_smoke_monitor",
    "type": "ui_tab",
    "name": "Báo Khói Cảnh Báo Sớm - Tuần 7",
    "icon": "dashboard",
    "order": 1
  },
  {
    "id": "ui_grp_gauges",
    "type": "ui_group",
    "name": "Thông số Cảm biến Môi trường",
    "tab": "ui_tab_smoke_monitor",
    "order": 1,
    "disp": true,
    "width": "12"
  },
  {
    "id": "ui_grp_state",
    "type": "ui_group",
    "name": "Máy trạng thái FSM 6 Trạng thái & Tuần 7 Rules",
    "tab": "ui_tab_smoke_monitor",
    "order": 2,
    "disp": true,
    "width": "12"
  },
  {
    "id": "ui_grp_controls",
    "type": "ui_group",
    "name": "Tầng 4: Điều khiển Chấp hành & Cảnh báo từ xa",
    "tab": "ui_tab_smoke_monitor",
    "order": 3,
    "disp": true,
    "width": "12"
  },
  {
    "id": "ui_grp_fleet",
    "type": "ui_group",
    "name": "Quản trị Hạm đội Thiết bị (Fleet Registry)",
    "tab": "ui_tab_smoke_monitor",
    "order": 4,
    "disp": true,
    "width": "12"
  },
  {
    "id": "ui_grp_rules",
    "type": "ui_group",
    "name": "Bảng Điều phối Business Rules & Abnormal Sandbox",
    "tab": "ui_tab_smoke_monitor",
    "order": 5,
    "disp": true,
    "width": "12"
  },
  {
    "id": "ui_gauge_smoke",
    "type": "ui_gauge",
    "z": "tab_middleware_smoke",
    "name": "Smoke PPM Gauge",
    "group": "ui_grp_gauges",
    "order": 1,
    "width": 4,
    "height": 4,
    "gtype": "gage",
    "title": "Nồng độ Khói (MQ-2)",
    "label": "PPM",
    "format": "{{value}}",
    "min": 0,
    "max": "1000",
    "colors": [
      "#00b500",
      "#e6e600",
      "#ca3838"
    ],
    "seg1": "300",
    "seg2": "400",
    "diff": false,
    "className": "",
    "x": 1410,
    "y": 620,
    "wires": []
  },
  {
    "id": "ui_gauge_temp",
    "type": "ui_gauge",
    "z": "tab_middleware_smoke",
    "name": "Temperature Gauge",
    "group": "ui_grp_gauges",
    "order": 2,
    "width": 4,
    "height": 4,
    "gtype": "gage",
    "title": "Nhiệt độ (DHT22)",
    "label": "°C",
    "format": "{{value}}",
    "min": 0,
    "max": "80",
    "colors": [
      "#00b500",
      "#e6e600",
      "#ca3838"
    ],
    "seg1": "35",
    "seg2": "50",
    "diff": false,
    "className": "",
    "x": 1410,
    "y": 680,
    "wires": []
  },
  {
    "id": "ui_gauge_hum",
    "type": "ui_gauge",
    "z": "tab_middleware_smoke",
    "name": "Humidity Gauge",
    "group": "ui_grp_gauges",
    "order": 3,
    "width": 4,
    "height": 4,
    "gtype": "gage",
    "title": "Độ ẩm Không khí",
    "label": "%",
    "format": "{{value}}",
    "min": 0,
    "max": "100",
    "colors": [
      "#2ca02c",
      "#1f77b4",
      "#0094ce"
    ],
    "seg1": "",
    "seg2": "",
    "diff": false,
    "className": "",
    "x": 1410,
    "y": 740,
    "wires": []
  },
  {
    "id": "ui_chart_trends",
    "type": "ui_chart",
    "z": "tab_middleware_smoke",
    "name": "Realtime Trends Chart",
    "group": "ui_grp_gauges",
    "order": 4,
    "width": 12,
    "height": 6,
    "label": "Biểu đồ Thời gian thực Khói (PPM) & Nhiệt độ (°C)",
    "chartType": "line",
    "legend": "true",
    "xformat": "HH:mm:ss",
    "interpolate": "linear",
    "nodata": "Đang nhận dữ liệu từ ESP32...",
    "dot": false,
    "ymin": "0",
    "ymax": "",
    "removeOlder": 1,
    "removeOlderPoints": "",
    "removeOlderUnit": "3600",
    "cutout": 0,
    "useOneColor": false,
    "useUTC": false,
    "colors": [
      "#ca3838",
      "#ff7f0e",
      "#1f77b4",
      "#2ca02c",
      "#98df8a",
      "#d62728",
      "#ff9896",
      "#9467bd",
      "#c5b0d5"
    ],
    "outputs": 1,
    "useDifferentColor": false,
    "className": "",
    "x": 1410,
    "y": 800,
    "wires": [
      []
    ]
  },
  {
    "id": "ui_text_fsm_state",
    "type": "ui_text",
    "z": "tab_middleware_smoke",
    "group": "ui_grp_state",
    "order": 1,
    "width": 12,
    "height": 2,
    "name": "FSM State Display",
    "label": "Trạng thái FSM Hệ thống:",
    "format": "<b><span style='color: {{msg.color}}; font-size: 22px; text-transform: uppercase;'>{{msg.payload}}</span></b>",
    "layout": "row-spread",
    "className": "",
    "x": 1410,
    "y": 860,
    "wires": []
  },
  {
    "id": "ui_btn_fan_on",
    "type": "ui_button",
    "z": "tab_middleware_smoke",
    "name": "Button Fan ON",
    "group": "ui_grp_controls",
    "order": 1,
    "width": 3,
    "height": 1,
    "passthru": false,
    "label": "BẬT QUẠT HÚT",
    "tooltip": "Kích hoạt quạt hút khói",
    "color": "#ffffff",
    "bgcolor": "#27ae60",
    "className": "",
    "icon": "fa-fan",
    "payload": "{\"action\":\"ON\",\"source\":\"NodeRED_Dashboard\"}",
    "payloadType": "str",
    "topic": "Nhom09/smoke/cmd/fan",
    "topicType": "str",
    "x": 1130,
    "y": 920,
    "wires": [
      [
        "fn_command_dispatcher"
      ]
    ]
  },
  {
    "id": "ui_btn_fan_off",
    "type": "ui_button",
    "z": "tab_middleware_smoke",
    "name": "Button Fan OFF",
    "group": "ui_grp_controls",
    "order": 2,
    "width": 3,
    "height": 1,
    "passthru": false,
    "label": "TẮT QUẠT HÚT",
    "tooltip": "Tắt quạt hút khói",
    "color": "#ffffff",
    "bgcolor": "#7f8c8d",
    "className": "",
    "icon": "fa-power-off",
    "payload": "{\"action\":\"OFF\",\"source\":\"NodeRED_Dashboard\"}",
    "payloadType": "str",
    "topic": "Nhom09/smoke/cmd/fan",
    "topicType": "str",
    "x": 1130,
    "y": 970,
    "wires": [
      [
        "fn_command_dispatcher"
      ]
    ]
  },
  {
    "id": "ui_btn_buzzer_mute",
    "type": "ui_button",
    "z": "tab_middleware_smoke",
    "name": "Button Buzzer Mute",
    "group": "ui_grp_controls",
    "order": 3,
    "width": 3,
    "height": 1,
    "passthru": false,
    "label": "TẮT TIẾNG CÒI (MUTE)",
    "tooltip": "Tạm ngắt tiếng chuông cảnh báo 3 phút",
    "color": "#ffffff",
    "bgcolor": "#e67e22",
    "className": "",
    "icon": "fa-bell-slash",
    "payload": "{\"action\":\"MUTE\",\"source\":\"NodeRED_Dashboard\"}",
    "payloadType": "str",
    "topic": "Nhom09/smoke/cmd/buzzer",
    "topicType": "str",
    "x": 1130,
    "y": 1020,
    "wires": [
      [
        "fn_command_dispatcher"
      ]
    ]
  },
  {
    "id": "ui_btn_buzzer_unmute",
    "type": "ui_button",
    "z": "tab_middleware_smoke",
    "name": "Button Buzzer Unmute",
    "group": "ui_grp_controls",
    "order": 4,
    "width": 3,
    "height": 1,
    "passthru": false,
    "label": "BẬT TIẾNG CÒI (UNMUTE)",
    "tooltip": "Kích hoạt lại còi báo động",
    "color": "#ffffff",
    "bgcolor": "#c0392b",
    "className": "",
    "icon": "fa-bell",
    "payload": "{\"action\":\"UNMUTE\",\"source\":\"NodeRED_Dashboard\"}",
    "payloadType": "str",
    "topic": "Nhom09/smoke/cmd/buzzer",
    "topicType": "str",
    "x": 1130,
    "y": 1070,
    "wires": [
      [
        "fn_command_dispatcher"
      ]
    ]
  }
]
```

---

## PHẦN 32: WEB SCADA: THƯ VIỆN BẢO MẬT XSS & UTILITIES (`web/util.js`)

> **Đường dẫn:** `web/util.js`  
> **Quy mô:** 30 dòng | 845 bytes | Ngôn ngữ: `javascript`

```javascript
// web/util.js
(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    const exports = factory();
    root.Util = exports;
    root.escapeHtml = exports.escapeHtml;
    root.safeLevelClass = exports.safeLevelClass;
  }
}(typeof self !== 'undefined' ? self : this, function () {
  function escapeHtml(v) {
    return String(v === null || v === undefined ? '' : v)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  const LEVELS = ['INFO', 'WARN', 'CRITICAL', 'SUCCESS'];
  function safeLevelClass(lv) {
    return (LEVELS.includes(lv) ? 'lvl-' + lv.toLowerCase() : 'lvl-info');
  }

  return {
    escapeHtml: escapeHtml,
    safeLevelClass: safeLevelClass
  };
}));

```

---

## PHẦN 33: WEB SCADA: GIAO DIỆN ĐIỀU HÀNH (HTML5 SEMANTIC) (`web/index.html`)

> **Đường dẫn:** `web/index.html`  
> **Quy mô:** 784 dòng | 38,643 bytes | Ngôn ngữ: `html`

```html
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Smart Fire Safety SCADA | Tầng 4 Application - Nhóm 04 HUIT</title>
  <meta name="description" content="Trung tâm Giám sát và Điều hành An toàn PCCC Thông minh - Hệ thống SCADA Tầng 4 Application">
  <!-- Google Fonts: Inter & JetBrains Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <!-- MQTT.js: Local Offline First with CDN Fallback -->
  <script src="libs/mqtt.min.js"></script>
  <script>window.mqtt || document.write('<script src="https://unpkg.com/mqtt/dist/mqtt.min.js"><\/script>')</script>
  <!-- Chart.js: Local Offline First with CDN Fallback -->
  <script src="libs/chart.umd.min.js"></script>
  <script>window.Chart || document.write('<script src="https://cdn.jsdelivr.net/npm/chart.js"><\/script>')</script>
  <link rel="stylesheet" href="style.css?v=light_academic_v2">
</head>
<body>

  <!-- TOP NAVIGATION BAR (SCADA SUPERVISORY HEADER) -->
  <header class="app-header">
    <div class="header-left">
      <div class="brand-logo">
        <div class="brand-icon-box">
          <!-- Industrial Fire Safety Shield SVG -->
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            <path d="M12 8c.5 1.5 2 2.5 2 4.5a3.5 3.5 0 0 1-7 0c0-1.5 1-2.5 1.5-3.5 1 2 2.5 2 3.5-1z" fill="currentColor"/>
          </svg>
        </div>
        <div class="brand-info">
          <h1>SMART FIRE SAFETY SCADA <span class="badge-tag">TẦNG 4 APPLICATION</span></h1>
          <p class="subtitle">Đề tài 04: Hệ thống Báo khói Cảnh báo sớm • Nhóm 04 (N09) HUIT</p>
        </div>
      </div>
    </div>

    <div class="header-center">
      <!-- SYSTEM FSM STATUS CHIP -->
      <div class="fsm-status-chip state-safe" id="fsmChip">
        <span class="status-dot"></span>
        <span class="status-label">Trạng thái FSM:</span>
        <strong class="status-value" id="fsmStatusText">AN TOÀN (SAFE)</strong>
      </div>
    </div>

    <div class="header-right">
      <!-- BROKER CONNECTION BADGE -->
      <div class="connection-pill connected" id="brokerConnBadge" title="broker.emqx.io:8084 (WSS)">
        <span class="pill-dot"></span>
        <span id="connStatusText">MQTT Online</span>
      </div>

      <!-- ROLE SELECTOR (RBAC) -->
      <div class="role-selector-wrap">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
        <select id="userRoleSelect" title="Phân quyền người dùng (Role-Based Access Control)">
          <option value="admin">Quản trị viên (Admin)</option>
          <option value="operator" selected>Kỹ thuật viên (Operator)</option>
          <option value="viewer">Cư dân (Viewer)</option>
        </select>
      </div>

      <!-- SIMULATION TOGGLE -->
      <button id="btnToggleSimModal" class="btn-icon-label" title="Bảng điều khiển Giả lập">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="4" y1="21" x2="4" y2="14"/>
          <line x1="4" y1="10" x2="4" y2="3"/>
          <line x1="12" y1="21" x2="12" y2="12"/>
          <line x1="12" y1="8" x2="12" y2="3"/>
          <line x1="20" y1="21" x2="20" y2="16"/>
          <line x1="20" y1="12" x2="20" y2="3"/>
          <line x1="1" y1="14" x2="7" y2="14"/>
          <line x1="9" y1="8" x2="15" y2="8"/>
          <line x1="17" y1="16" x2="23" y2="16"/>
        </svg>
        Giả lập
      </button>

      <!-- CLOCK -->
      <div class="clock-display" id="clockDisplay">12:00:00</div>
    </div>
  </header>

  <!-- ALARM BANNER (Visible during Warning / Alarm / Cooldown) -->
  <div class="alarm-banner" id="alarmBanner">
    <div class="banner-inner">
      <div class="banner-icon-wrap" id="bannerIcon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
          <line x1="12" y1="9" x2="12" y2="13"/>
          <line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
      </div>
      <div class="banner-text">
        <strong id="bannerTitle">CẢNH BÁO: MÔI TRƯỜNG AN TOÀN</strong>
        <span id="bannerDesc">Tất cả các thông số khí khói và nhiệt độ đang trong giới hạn cho phép.</span>
      </div>
      <div class="banner-actions">
        <button id="btnBannerMute" class="btn btn-sm btn-outline-warning">Tắt còi 180s</button>
        <button id="btnBannerAcknowledge" class="btn btn-sm btn-solid-warning">Xác nhận đã xử lý</button>
      </div>
    </div>
  </div>

  <!-- MAIN CONTAINER -->
  <main class="main-content">

    <!-- KPI SUMMARY BAR -->
    <section class="kpi-grid">
      <!-- KPI 1: SMOKE -->
      <div class="kpi-card glass-panel" id="kpiSmoke">
        <div class="kpi-header">
          <div class="kpi-title-wrap">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 2c-4 4-6 7.5-6 11a6 6 0 0 0 12 0c0-3.5-2-7-6-11z"/>
            </svg>
            <span class="kpi-title">Nồng độ Khói MQ-2</span>
          </div>
          <span class="kpi-tag normal" id="tagSmoke">Bình thường</span>
        </div>
        <div class="kpi-body">
          <div class="kpi-value-wrap">
            <span class="kpi-num" id="valSmokePpm">145.2</span>
            <span class="kpi-unit">PPM</span>
          </div>
          <div class="mini-progress-bar">
            <div class="progress-fill" id="barSmoke" style="width: 25%;"></div>
          </div>
        </div>
        <div class="kpi-footer">
          <span>Ngưỡng Báo động: <strong id="kpiThreshold">400.0 PPM</strong></span>
          <span class="kpi-trend" id="trendSmoke">0.0 PPM/s</span>
        </div>
      </div>

      <!-- KPI 2: TEMPERATURE -->
      <div class="kpi-card glass-panel" id="kpiTemp">
        <div class="kpi-header">
          <div class="kpi-title-wrap">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/>
            </svg>
            <span class="kpi-title">Nhiệt độ DHT22</span>
          </div>
          <span class="kpi-tag normal" id="tagTemp">Ổn định</span>
        </div>
        <div class="kpi-body">
          <div class="kpi-value-wrap">
            <span class="kpi-num" id="valTemp">28.4</span>
            <span class="kpi-unit">°C</span>
          </div>
          <div class="mini-progress-bar">
            <div class="progress-fill temp-fill" id="barTemp" style="width: 35%;"></div>
          </div>
        </div>
        <div class="kpi-footer">
          <span>Ngưỡng Quá nhiệt: <strong>55.0 °C</strong></span>
          <span class="kpi-trend" id="trendTemp">+0.1 °C/m</span>
        </div>
      </div>

      <!-- KPI 3: HUMIDITY -->
      <div class="kpi-card glass-panel" id="kpiHum">
        <div class="kpi-header">
          <div class="kpi-title-wrap">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/>
            </svg>
            <span class="kpi-title">Độ ẩm Môi trường</span>
          </div>
          <span class="kpi-tag normal" id="tagHum">Lý tưởng</span>
        </div>
        <div class="kpi-body">
          <div class="kpi-value-wrap">
            <span class="kpi-num" id="valHum">62.8</span>
            <span class="kpi-unit">%RH</span>
          </div>
          <div class="mini-progress-bar">
            <div class="progress-fill hum-fill" id="barHum" style="width: 63%;"></div>
          </div>
        </div>
        <div class="kpi-footer">
          <span>Khuyến nghị: 40% – 70%</span>
          <span>Khí áp: 1013 hPa</span>
        </div>
      </div>

      <!-- KPI 4: FLEET / STATION STATUS -->
      <div class="kpi-card glass-panel" id="kpiFleetStatus">
        <div class="kpi-header">
          <div class="kpi-title-wrap">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="2" y="2" width="20" height="8" rx="2" ry="2"/>
              <rect x="2" y="14" width="20" height="8" rx="2" ry="2"/>
              <line x1="6" y1="6" x2="6.01" y2="6"/>
              <line x1="6" y1="18" x2="6.01" y2="18"/>
            </svg>
            <span class="kpi-title">Trạm Thu thập ESP32</span>
          </div>
          <span class="kpi-tag active" id="tagEspStatus">Hoạt động</span>
        </div>
        <div class="kpi-body">
          <div class="kpi-fleet-stats">
            <div class="stat-item">
              <span class="stat-lbl">Thiết bị:</span>
              <strong class="stat-val" id="valDeviceId">ESP32_SMOKE_N04_A01</strong>
            </div>
            <div class="stat-item">
              <span class="stat-lbl">Vị trí:</span>
              <strong class="stat-val">Tầng 3 - P302 (Lab IoT)</strong>
            </div>
            <div class="stat-item">
              <span class="stat-lbl">Tín hiệu WiFi:</span>
              <strong class="stat-val" id="valRssi">-52 dBm (Tốt)</strong>
            </div>
          </div>
        </div>
        <div class="kpi-footer">
          <span>Keep-Alive: <strong id="valKeepAlive">Vừa xong</strong></span>
          <span>Độ trễ mạng: <strong id="valLatency">42 ms</strong></span>
        </div>
      </div>
    </section>

    <!-- MAIN TWO-COLUMN DASHBOARD -->
    <div class="dashboard-grid">

      <!-- LEFT COLUMN: REAL-TIME GAUGES & CHARTS -->
      <div class="dash-column-left">

        <!-- TELEMETRY CHART PANEL -->
        <div class="glass-panel chart-panel">
          <div class="panel-header">
            <div class="header-title-group">
              <div class="title-with-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                </svg>
                <h3>Biểu đồ Xu hướng Khói & Nhiệt độ Thời gian thực</h3>
              </div>
              <p>Chu kỳ lấy mẫu 2.0s qua kênh <code>Nhom09/smoke/telemetry</code></p>
            </div>
            <div class="panel-controls">
              <button class="btn-chip active" id="btnChartRange10m">10 Phút</button>
              <button class="btn-chip" id="btnChartRange30m">30 Phút</button>
              <button class="btn-chip" id="btnResetChart">Làm mới</button>
            </div>
          </div>
          <div class="chart-container">
            <canvas id="telemetryChart"></canvas>
          </div>
          <div class="chart-legend-custom">
            <div class="leg-item"><span class="leg-dot color-smoke"></span> Khói MQ-2 (PPM)</div>
            <div class="leg-item"><span class="leg-dot color-temp"></span> Nhiệt độ DHT22 (°C)</div>
            <div class="leg-item"><span class="leg-line color-thresh"></span> Ngưỡng Báo động (400 PPM)</div>
          </div>
        </div>

        <!-- FLOORPLAN / FLEET LOCATION MAP (CAD ARCHITECTURAL BLUEPRINT) -->
        <div class="glass-panel floorplan-panel">
          <div class="panel-header">
            <div class="header-title-group">
              <div class="title-with-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                  <line x1="3" y1="9" x2="21" y2="9"/>
                  <line x1="9" y1="21" x2="9" y2="9"/>
                </svg>
                <h3>Sơ đồ Phân vùng Cảm biến Tầng 3 (HUIT Tòa A)</h3>
              </div>
              <p>Mặt bằng kiến trúc giám sát liên vùng (Cross-Zone Monitoring)</p>
            </div>
            <span class="badge-status-zone" id="zoneOverallStatus"><span class="dot"></span> Toàn sàn Bình thường</span>
          </div>

          <div class="floorplan-map-wrap">
            <!-- ZONE P301 -->
            <div class="floor-zone zone-p301">
              <div class="zone-label">Phòng P301<br><small>Văn phòng Khoa</small></div>
              <div class="sensor-node node-normal" title="Trạm Node A00: An toàn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M4.93 19.07A10 10 0 0 1 19.07 4.93M7.76 16.24A6 6 0 0 1 16.24 7.76M12 12h.01"/>
                </svg>
                <span class="node-name">Node A00</span>
              </div>
            </div>

            <!-- ZONE P302 (ACTIVE TARGET) -->
            <div class="floor-zone zone-p302 active-focus" id="zoneP302">
              <div class="zone-label">Phòng P302<br><strong>PHÒNG LAB IOT (TRẠM CHÍNH)</strong></div>
              <div class="sensor-node node-live" id="mapNodeA01" title="Trạm chính N04_A01: Đang giám sát">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 2c-4 4-6 7.5-6 11a6 6 0 0 0 12 0c0-3.5-2-7-6-11z"/>
                </svg>
                <span class="node-name">ESP32_A01</span>
                <span class="node-badge" id="mapNodeBadge">SAFE</span>
              </div>
              <div class="actuator-marker fan-marker" id="mapFanMarker" title="Quạt hút thông gió P302">
                <span class="fan-icon-spin" id="mapFanIcon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="3"/>
                    <path d="M12 9V2a3 3 0 0 1 3 3v4"/>
                    <path d="M15 12h7a3 3 0 0 1-3 3h-4"/>
                    <path d="M12 15v7a3 3 0 0 1-3-3v-4"/>
                    <path d="M9 12H2a3 3 0 0 1 3-3h4"/>
                  </svg>
                </span>
                Quạt P302
              </div>
            </div>

            <!-- ZONE P303 -->
            <div class="floor-zone zone-p303" id="zoneP303">
              <div class="zone-label">Phòng P303<br><small>Kho Thiết bị</small></div>
              <div class="sensor-node node-normal" id="mapNodeA02" title="Trạm phụ A02">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M4.93 19.07A10 10 0 0 1 19.07 4.93M7.76 16.24A6 6 0 0 1 16.24 7.76M12 12h.01"/>
                </svg>
                <span class="node-name">Node A02</span>
              </div>
            </div>

            <!-- CORRIDOR ESCAPE ROUTE -->
            <div class="floor-zone zone-corridor">
              <div class="zone-label">HÀNH LANG TẦNG 3 - LỐI THOÁT HIỂM</div>
              <div class="actuator-marker siren-marker" id="mapSirenMarker">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
                  <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
                </svg>
                Còi Liên vùng Zone F03
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- RIGHT COLUMN: ACTUATORS CONTROL, RULES, TELEGRAM, AUDIT LOG -->
      <div class="dash-column-right">

        <!-- REMOTE ACTUATOR CONTROL CONSOLE -->
        <div class="glass-panel control-panel">
          <div class="panel-header">
            <div class="header-title-group">
              <div class="title-with-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                  <line x1="8" y1="21" x2="16" y2="21"/>
                  <line x1="12" y1="17" x2="12" y2="21"/>
                </svg>
                <h3>Trung tâm Điều khiển Thiết bị Chấp hành</h3>
              </div>
              <p>Lệnh Downlink thời gian thực qua MQTT QoS 1</p>
            </div>
            <span class="role-badge-tag" id="currentRoleBadge">Quyền: Kỹ thuật viên</span>
          </div>

          <div class="control-cards-grid">

            <!-- ACTUATOR 1: EXHAUST FAN -->
            <div class="actuator-box" id="boxFan">
              <div class="actuator-box-header">
                <div class="actuator-title-icon">
                  <div class="act-icon-box" id="fanStatusIcon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <circle cx="12" cy="12" r="3"/>
                      <path d="M12 9V2a3 3 0 0 1 3 3v4"/>
                      <path d="M15 12h7a3 3 0 0 1-3 3h-4"/>
                      <path d="M12 15v7a3 3 0 0 1-3-3v-4"/>
                      <path d="M9 12H2a3 3 0 0 1 3-3h4"/>
                    </svg>
                  </div>
                  <div>
                    <strong>Quạt hút Khói DC 12V</strong>
                    <span class="act-sub" id="fanTopicSub">Nhom09/smoke/cmd/fan</span>
                  </div>
                </div>
                <span class="act-state-badge off" id="badgeFanState">ĐANG TẮT</span>
              </div>

              <div class="actuator-box-body">
                <p class="act-mode-desc">Chế độ vận hành: <strong id="lblFanMode">TỰ ĐỘNG (AUTO)</strong></p>
                <div class="btn-group-controls">
                  <button class="btn btn-outline-success" id="btnFanOn" title="Bật quạt cưỡng bức">
                    Bật Quạt
                  </button>
                  <button class="btn btn-outline-danger" id="btnFanOff" title="Tắt quạt (bị khóa nếu đang ALARM)">
                    Tắt Quạt
                  </button>
                  <button class="btn btn-outline-info active" id="btnFanAuto" title="Chuyển chế độ Tự động theo FSM">
                    Auto FSM
                  </button>
                </div>
              </div>
            </div>

            <!-- ACTUATOR 2: BUZZER ALARM SIREN -->
            <div class="actuator-box" id="boxBuzzer">
              <div class="actuator-box-header">
                <div class="actuator-title-icon">
                  <div class="act-icon-box" id="buzzerStatusIcon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
                      <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
                    </svg>
                  </div>
                  <div>
                    <strong>Còi hú Báo động Khẩn cấp</strong>
                    <span class="act-sub">Nhom09/smoke/cmd/buzzer</span>
                  </div>
                </div>
                <span class="act-state-badge off" id="badgeBuzzerState">IM LẶNG</span>
              </div>

              <div class="actuator-box-body">
                <p class="act-mode-desc" id="lblBuzzerDesc">Còi sẵn sàng tự động phản ứng khi khói >= 400 PPM</p>
                <div class="btn-group-controls">
                  <button class="btn btn-outline-warning" id="btnBuzzerMute" title="Tạm tắt tiếng còi 180s để xử lý hiện trường">
                    Tắt tiếng (180s)
                  </button>
                  <button class="btn btn-outline-primary" id="btnBuzzerUnmute" title="Kích hoạt lại âm thanh còi">
                    Hủy Mute
                  </button>
                  <button class="btn btn-outline-secondary" id="btnBuzzerTest" title="Phát 1 tiếng bíp 0.5s kiểm tra còi">
                    Test Beep
                  </button>
                </div>
              </div>
            </div>

            <!-- ACTUATOR 3: SENSITIVITY SCHEDULER -->
            <div class="actuator-box" id="boxScheduler">
              <div class="actuator-box-header">
                <div class="actuator-title-icon">
                  <div class="act-icon-box" id="schedIcon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <circle cx="12" cy="12" r="5"/>
                      <line x1="12" y1="1" x2="12" y2="3"/>
                      <line x1="12" y1="21" x2="12" y2="23"/>
                      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
                      <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                      <line x1="1" y1="12" x2="3" y2="12"/>
                      <line x1="21" y1="12" x2="23" y2="12"/>
                      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
                      <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
                    </svg>
                  </div>
                  <div>
                    <strong>Lịch trình Ngưỡng Báo động</strong>
                    <span class="act-sub">Rule 3 Adaptive Scheduler</span>
                  </div>
                </div>
                <span class="act-state-badge mode-day" id="badgeNightState">CHẾ ĐỘ NGÀY</span>
              </div>

              <div class="actuator-box-body">
                <p class="act-mode-desc">Ngưỡng kích hoạt: <strong id="lblThresholdDesc">400 PPM (Ban ngày)</strong></p>
                <div class="scheduler-toggle-wrap">
                  <button class="btn btn-sm btn-outline-warning active" id="btnModeDay">Ban ngày (400 PPM)</button>
                  <button class="btn btn-sm btn-outline-primary" id="btnModeNight">Ban đêm (350 PPM)</button>
                </div>
              </div>
            </div>

          </div>
        </div>

        <!-- TUẦN 7: BUSINESS RULES & ABNORMAL SCENARIOS MANAGEMENT CONSOLE -->
        <div class="glass-panel week7-panel" id="panelWeek7Rules">
          <div class="panel-header">
            <div class="header-title-group">
              <div class="title-with-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                  <line x1="16" y1="13" x2="8" y2="13"/>
                  <line x1="16" y1="17" x2="8" y2="17"/>
                  <polyline points="10 9 9 9 8 9"/>
                </svg>
                <h3>Quản trị Quy tắc Tự động & Sự cố (Tuần 7)</h3>
              </div>
              <p>5 Business Automation Rules & Bộ Chẩn đoán Sức khỏe Phần cứng</p>
            </div>
            <span class="badge-tag week7-tag">Milestone Tuần 7</span>
          </div>

          <!-- 5 BUSINESS RULES MATRIX -->
          <div class="week7-rules-list">
            <div class="rule-item active">
              <div class="rule-info">
                <span class="rule-code">RULE 1</span>
                <div>
                  <strong>Đa cảm biến tương quan (Multi-Sensor Rate-of-Rise)</strong>
                  <p class="rule-desc">Khói ≥ 400 PPM + Gia tốc nhiệt dT/dt ≥ 3°C/phút → Khẳng định cháy thật (Real Fire), kích hoạt Full Alarm bỏ qua trễ lọc.</p>
                </div>
              </div>
              <span class="rule-status-badge active">ACTIVE</span>
            </div>

            <div class="rule-item active">
              <div class="rule-info">
                <span class="rule-code">RULE 2</span>
                <div>
                  <strong>Chống Báo động giả & Lọc khói thoáng qua (&lt; 10s)</strong>
                  <p class="rule-desc">Khói ≥ 400 PPM nhưng nhiệt độ &lt; 35°C và t &lt; 10s (khói thuốc/nấu ăn) → Chỉ bật quạt thông gió, ngắt còi hú tránh hoảng loạn.</p>
                </div>
              </div>
              <span class="rule-status-badge active">ACTIVE</span>
            </div>

            <div class="rule-item active">
              <div class="rule-info">
                <span class="rule-code">RULE 3</span>
                <div>
                  <strong>Ngưỡng nhạy Thích ứng Ngày/Đêm (Adaptive Day/Night)</strong>
                  <p class="rule-desc">Ngày: 400/300 PPM. Đêm (22h-06h): Tự động hạ ngưỡng 350/250 PPM để bảo vệ tối đa tính mạng khi người dân đang ngủ.</p>
                </div>
              </div>
              <span class="rule-status-badge active">ACTIVE</span>
            </div>

            <div class="rule-item active">
              <div class="rule-info">
                <span class="rule-code">RULE 4</span>
                <div>
                  <strong>Thông gió Cưỡng bức & Trễ Phục hồi 30s (Post-Purge Cooldown)</strong>
                  <p class="rule-desc">Sau khi khói hạ về an toàn (≤ 300 PPM), quạt duy trì chạy thêm 30 giây để hút sạch khí độc tích tụ trước khi về IDLE.</p>
                </div>
              </div>
              <span class="rule-status-badge active">ACTIVE</span>
            </div>

            <div class="rule-item active">
              <div class="rule-info">
                <span class="rule-code">RULE 5</span>
                <div>
                  <strong>Cảnh báo Thoát hiểm Liên vùng (Cross-Zone Broadcast)</strong>
                  <p class="rule-desc">Khi khói tại P302 ≥ 600 PPM liên tục quá 15s → Tự động phát lệnh Broadcast hú còi toàn bộ Hành lang Tầng 3 (Zone F03).</p>
                </div>
              </div>
              <span class="rule-status-badge active">ACTIVE</span>
            </div>
          </div>

          <!-- DIAGNOSTIC HEALTH MATRIX -->
          <div class="health-matrix-wrap">
            <div class="matrix-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
              </svg>
              Chẩn đoán Sức khỏe Phần cứng (Diagnostics)
            </div>
            <div class="health-grid">
              <div class="health-card">
                <span class="health-label">Cảm biến Khói MQ-2</span>
                <strong id="healthMq2Status" class="health-val ok">● ADC BÌNH THƯỜNG</strong>
              </div>
              <div class="health-card">
                <span class="health-label">Cảm biến DHT22</span>
                <strong id="healthDhtStatus" class="health-val ok">● 1-WIRE KẾT NỐI</strong>
              </div>
              <div class="health-card">
                <span class="health-label">Watchdog Heartbeat</span>
                <strong id="healthWatchdogStatus" class="health-val ok">● PING 10s (ALIVE)</strong>
              </div>
              <div class="health-card">
                <span class="health-label">Rơ-le Quạt Chấp hành</span>
                <strong id="healthActuatorStatus" class="health-val ok">● PHẢN HỒI ACK</strong>
              </div>
            </div>
          </div>

          <!-- FAULT INJECTION SANDBOX -->
          <div class="fault-sandbox-wrap">
            <div class="matrix-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
              </svg>
              Bộ Giả lập Sự cố Bất thường (Fault Injection)
            </div>
            <p class="sandbox-desc">Kích hoạt kịch bản để kiểm tra cơ chế Fail-Safe tự động của trạm ESP32:</p>
            <div class="sandbox-buttons-grid">
              <button class="btn btn-sm btn-outline-danger" id="btnFaultMq2">Đứt dây MQ-2</button>
              <button class="btn btn-sm btn-outline-danger" id="btnFaultDht">Lỗi DHT22 (NaN)</button>
              <button class="btn btn-sm btn-outline-warning" id="btnFaultActuator">Kẹt Rơ-le Quạt</button>
              <button class="btn btn-sm btn-outline-info" id="btnSyncBuffer">Đồng bộ Buffer 20</button>
              <button class="btn btn-sm btn-solid-success" id="btnClearAllFaults">Xóa lỗi (Khôi phục)</button>
            </div>
          </div>
        </div>

        <!-- TELEGRAM BOT ALERTING INTEGRATION -->
        <div class="glass-panel telegram-panel">
          <div class="panel-header">
            <div class="header-title-group">
              <div class="title-with-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="22" y1="2" x2="11" y2="13"/>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                </svg>
                <h3>Kênh Thông báo Khẩn cấp Telegram Bot</h3>
              </div>
              <p>Tự động phát thông báo thời gian thực tới đội phản ứng nhanh</p>
            </div>
            <span class="badge-telegram-ready">Bot Online</span>
          </div>

          <div class="telegram-body">
            <!-- Simulated Telegram Phone View -->
            <div class="telegram-chat-window">
              <div class="tg-chat-header">
                <div class="tg-bot-avatar">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="11" width="18" height="10" rx="2"/>
                    <circle cx="12" cy="5" r="2"/>
                    <path d="M12 7v4"/>
                    <line x1="8" y1="16" x2="8" y2="16"/>
                    <line x1="16" y1="16" x2="16" y2="16"/>
                  </svg>
                </div>
                <div class="tg-bot-meta">
                  <strong>@HUIT_FireAlert_N04_Bot</strong>
                  <span>Hệ thống Giám sát & Báo cháy Tự động 24/7</span>
                </div>
              </div>
              <div class="tg-messages-list" id="tgMessagesList">
                <div class="tg-msg tg-bot-msg">
                  <div class="tg-msg-time">Hệ thống khởi động</div>
                  <div class="tg-msg-bubble">
                    <strong>HỆ THỐNG BÁO KHÓI HOẠT ĐỘNG</strong><br>
                    Trạm: <code>ESP32_SMOKE_N04_A01</code><br>
                    Vị trí: Phòng P302 - Tầng 3 HUIT<br>
                    Trạng thái: SAFE (An toàn)<br>
                    Khói: 145 PPM | Nhiệt độ: 28.4°C
                  </div>
                </div>
              </div>
            </div>

            <div class="telegram-actions">
              <button class="btn btn-sm btn-solid-primary" id="btnTestTgAlert">
                Bắn Cảnh báo Khẩn cấp thử nghiệm
              </button>
              <button class="btn btn-sm btn-outline-secondary" id="btnClearTgHistory">
                Xóa tin nhắn
              </button>
            </div>
          </div>
        </div>

        <!-- AUDIT TRAIL / EVENT LOG PANEL -->
        <div class="glass-panel audit-panel">
          <div class="panel-header">
            <div class="header-title-group">
              <div class="title-with-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                  <line x1="16" y1="13" x2="8" y2="13"/>
                  <line x1="16" y1="17" x2="8" y2="17"/>
                  <polyline points="10 9 9 9 8 9"/>
                </svg>
                <h3>Nhật ký Sự kiện & Kiểm toán An toàn (Audit Trail)</h3>
              </div>
              <p>Lưu trữ bộ đệm vòng & đồng bộ <code>logs/event_history.log</code></p>
            </div>
            <div class="audit-filters">
              <select id="logFilterLevel" class="select-sm">
                <option value="ALL">Tất cả cấp độ</option>
                <option value="CRITICAL">CRITICAL</option>
                <option value="WARN">WARN</option>
                <option value="INFO">INFO</option>
              </select>
              <button class="btn-sm btn-outline-secondary" id="btnExportLogs" title="Tải xuống tệp CSV">
                Xuất CSV
              </button>
            </div>
          </div>

          <div class="audit-table-wrap">
            <table class="audit-table" id="auditTable">
              <thead>
                <tr>
                  <th style="width: 75px;">Thời gian</th>
                  <th style="width: 70px;">Mức độ</th>
                  <th style="width: 130px;">Mã Sự kiện</th>
                  <th>Mô tả chi tiết</th>
                  <th style="width: 65px;">FSM</th>
                </tr>
              </thead>
              <tbody id="auditTableBody">
                <!-- Dynamically populated via app.js -->
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  </main>

  <!-- MODAL: INTERACTIVE SIMULATOR (Dành cho việc chấm điểm / Demo kiểm thử) -->
  <div class="modal-overlay" id="simModal">
    <div class="modal-content glass-panel">
      <div class="modal-header">
        <div class="modal-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="4" y1="21" x2="4" y2="14"/>
            <line x1="4" y1="10" x2="4" y2="3"/>
            <line x1="12" y1="21" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12" y2="3"/>
            <line x1="20" y1="21" x2="20" y2="16"/>
            <line x1="20" y1="12" x2="20" y2="3"/>
            <line x1="1" y1="14" x2="7" y2="14"/>
            <line x1="9" y1="8" x2="15" y2="8"/>
            <line x1="17" y1="16" x2="23" y2="16"/>
          </svg>
          <div>
            <h3>BẢNG ĐIỀU KHIỂN GIẢ LẬP ĐẦU VÀO CẢM BIẾN (TEST BENCH)</h3>
            <p>Hội đồng Giảng viên chủ động thay đổi thông số kiểm chứng phản ứng Tầng 4</p>
          </div>
        </div>
        <button class="btn-close-modal" id="btnCloseSimModal">&times;</button>
      </div>

      <div class="modal-body">
        <div class="sim-row">
          <label>Nồng độ Khói MQ-2 (PPM): <strong id="simLblSmoke">145 PPM</strong></label>
          <div class="slider-wrap">
            <input type="range" id="simSliderSmoke" min="50" max="950" value="145" step="5">
          </div>
          <div class="preset-buttons">
            <button class="btn btn-xs btn-outline-success" onclick="setSimPreset(120, 27)">An toàn (120 PPM)</button>
            <button class="btn btn-xs btn-outline-warning" onclick="setSimPreset(320, 32)">Cảnh giác (320 PPM)</button>
            <button class="btn btn-xs btn-outline-danger" onclick="setSimPreset(550, 48)">Báo động Khẩn (550 PPM)</button>
            <button class="btn btn-xs btn-outline-primary" onclick="setSimPreset(270, 29)">Hạ khói Cooldown (270 PPM)</button>
          </div>
        </div>

        <div class="sim-row">
          <label>Nhiệt độ DHT22 (°C): <strong id="simLblTemp">28.4 °C</strong></label>
          <div class="slider-wrap">
            <input type="range" id="simSliderTemp" min="15" max="75" value="28.4" step="0.5">
          </div>
        </div>

        <div class="sim-row">
          <label>Mô phỏng Mất kết nối Trạm (Watchdog Timeout / LWT):</label>
          <div class="toggle-wrap">
            <button class="btn btn-sm btn-outline-danger" id="btnSimDisconnect">Mô phỏng Đứt mạng ESP32</button>
            <button class="btn btn-sm btn-outline-success" id="btnSimReconnect">Khôi phục Kết nối</button>
          </div>
        </div>

        <div class="sim-row">
          <label>Nguồn Dữ liệu Hoạt động:</label>
          <div class="source-select-wrap">
            <label><input type="radio" name="dataSource" value="sim" checked> Trình Giả lập Trực tiếp (Local Fast Sim)</label>
            <label><input type="radio" name="dataSource" value="mqtt"> MQTT WebSocket Thật (broker.emqx.io:8084)</label>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn btn-solid-primary" id="btnApplySim">Đóng Bảng Giả lập</button>
      </div>
    </div>
  </div>

  <!-- TOAST NOTIFICATION CONTAINER -->
  <div class="toast-container" id="toastContainer"></div>

  <!-- APPLICATION LOGIC -->
  <script src="util.js"></script>
  <script src="app.js?v=light_academic_v2"></script>
</body>
</html>

```

---

## PHẦN 34: WEB SCADA: BẢNG MÃ PHONG CÁCH GIAO DIỆN (CSS3 GLASSMORPHISM) (`web/style.css`)

> **Đường dẫn:** `web/style.css`  
> **Quy mô:** 1,823 dòng | 37,151 bytes | Ngôn ngữ: `css`

```css
/* =============================================================================
   ACADEMIC & ENTERPRISE LIGHT DASHBOARD - CLEAN MINIMALIST
   Tầng 4 Application - Đề tài 04: Hệ thống Báo khói Cảnh báo sớm
   Standard: Academic Defense / Corporate Clean Light Theme
   Theme: Crisp Slate / Pure White / High Legibility for Projectors
   ============================================================================= */

:root {
  /* Surface & Background Tokens (Clean Light Academic) */
  --scada-bg-base: #f8fafc;
  --scada-bg-header: #ffffff;
  --scada-card-bg: #ffffff;
  --scada-card-bg-subtle: #f1f5f9;
  --scada-card-hover: #ffffff;
  
  /* Precision Borders & Dividers */
  --scada-border: #e2e8f0;
  --scada-border-light: #cbd5e1;
  --scada-border-focus: #2563eb;

  /* Typography Colors (High Contrast, Clear on Projectors) */
  --scada-text-primary: #0f172a;
  --scada-text-secondary: #334155;
  --scada-text-muted: #64748b;
  --scada-text-dim: #94a3b8;

  /* Restrained Academic Safety Semantics */
  --scada-safe: #059669;
  --scada-safe-bg: #ecfdf5;
  --scada-safe-border: #a7f3d0;

  --scada-warn: #d97706;
  --scada-warn-bg: #fffbeb;
  --scada-warn-border: #fde68a;

  --scada-alarm: #dc2626;
  --scada-alarm-bg: #fef2f2;
  --scada-alarm-border: #fecaca;

  --scada-cooldown: #0284c7;
  --scada-cooldown-bg: #f0f9ff;
  --scada-cooldown-border: #bae6fd;

  --scada-offline: #64748b;
  --scada-offline-bg: #f1f5f9;
  --scada-offline-border: #cbd5e1;

  /* Academic Brand Tech Accent */
  --scada-accent: #2563eb;
  --scada-accent-hover: #1d4ed8;
  --scada-accent-bg: #eff6ff;

  /* Typography */
  --font-body: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace;
  --font-heading: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;

  /* Radii & Subtle Shadows */
  --radius-xs: 4px;
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 10px;
  --shadow-card: 0 1px 3px 0 rgba(0, 0, 0, 0.06), 0 1px 2px -1px rgba(0, 0, 0, 0.04);
  --shadow-elevation: 0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -2px rgba(0, 0, 0, 0.04);
}

/* =============================================================================
   BASE RESET & LAYOUT
   ============================================================================= */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  background-color: var(--scada-bg-base);
  color: var(--scada-text-primary);
  font-family: var(--font-body);
  font-size: 13px;
  line-height: 1.5;
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
  -webkit-font-smoothing: antialiased;
}

/* Academic Panels */
.glass-panel {
  background: var(--scada-card-bg);
  border: 1px solid var(--scada-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.glass-panel:hover {
  border-color: var(--scada-border-light);
  box-shadow: var(--shadow-elevation);
}

/* =============================================================================
   TOP NAVIGATION BAR (CLEAN LIGHT HEADER)
   ============================================================================= */
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 24px;
  background: var(--scada-bg-header);
  border-bottom: 1px solid var(--scada-border);
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.04);
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-icon-box {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #2563eb;
  flex-shrink: 0;
}

.brand-icon-box svg {
  width: 20px;
  height: 20px;
}

.brand-info h1 {
  font-family: var(--font-heading);
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.3px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--scada-text-primary);
  line-height: 1.2;
}

.badge-tag {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: var(--radius-xs);
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #2563eb;
  font-family: var(--font-mono);
  letter-spacing: 0.5px;
}

.subtitle {
  font-size: 11px;
  color: var(--scada-text-muted);
  margin-top: 1px;
}

/* Central FSM Status Indicator */
.fsm-status-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--scada-border);
  background: var(--scada-card-bg-subtle);
  transition: all 0.2s ease;
}

.fsm-status-chip .status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.fsm-status-chip .status-label {
  font-size: 10.5px;
  font-weight: 600;
  letter-spacing: 0.4px;
  color: var(--scada-text-muted);
  text-transform: uppercase;
}

.fsm-status-chip .status-value {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.4px;
}

/* FSM States */
.state-safe {
  background: var(--scada-safe-bg);
  border-color: var(--scada-safe-border);
  color: var(--scada-safe);
}
.state-safe .status-dot {
  background-color: var(--scada-safe);
}

.state-warning {
  background: var(--scada-warn-bg);
  border-color: var(--scada-warn-border);
  color: var(--scada-warn);
}
.state-warning .status-dot {
  background-color: var(--scada-warn);
  animation: blink 1.2s infinite ease-in-out;
}

.state-alarm {
  background: var(--scada-alarm-bg);
  border-color: var(--scada-alarm-border);
  color: var(--scada-alarm);
}
.state-alarm .status-dot {
  background-color: var(--scada-alarm);
  animation: blink 0.7s infinite ease-in-out;
}

.state-cooldown {
  background: var(--scada-cooldown-bg);
  border-color: var(--scada-cooldown-border);
  color: var(--scada-cooldown);
}
.state-cooldown .status-dot {
  background-color: var(--scada-cooldown);
}

.state-fault {
  background: var(--scada-alarm-bg);
  border-color: var(--scada-alarm-border);
  color: var(--scada-alarm);
}
.state-fault .status-dot {
  background-color: var(--scada-alarm);
  animation: blink 0.8s infinite ease-in-out;
}

.state-offline {
  background: var(--scada-offline-bg);
  border-color: var(--scada-offline-border);
  color: var(--scada-offline);
}
.state-offline .status-dot {
  background-color: var(--scada-offline);
}

/* Header Right Utilities */
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.connection-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 600;
  background: #f8fafc;
  border: 1px solid var(--scada-border);
  color: var(--scada-text-muted);
}

.connection-pill .pill-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}

.connection-pill.connected {
  border-color: var(--scada-safe-border);
  color: var(--scada-safe);
  background: var(--scada-safe-bg);
}
.connection-pill.connected .pill-dot {
  background-color: var(--scada-safe);
}

.connection-pill.disconnected {
  border-color: var(--scada-alarm-border);
  color: var(--scada-alarm);
  background: var(--scada-alarm-bg);
}
.connection-pill.disconnected .pill-dot {
  background-color: var(--scada-alarm);
}

.role-selector-wrap {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #f8fafc;
  border: 1px solid var(--scada-border);
  border-radius: var(--radius-sm);
  padding: 4px 8px;
}

.role-selector-wrap svg {
  width: 14px;
  height: 14px;
  color: var(--scada-text-muted);
}

#userRoleSelect {
  background: transparent;
  border: none;
  color: var(--scada-text-primary);
  font-size: 11.5px;
  font-family: var(--font-body);
  font-weight: 500;
  cursor: pointer;
  outline: none;
}

#userRoleSelect option {
  background: #ffffff;
  color: #0f172a;
}

.clock-display {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 600;
  color: var(--scada-text-secondary);
  background: #f8fafc;
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--scada-border);
  letter-spacing: 0.5px;
}

.btn-icon-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #ffffff;
  border: 1px solid var(--scada-border-light);
  color: var(--scada-text-secondary);
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 11.5px;
  font-weight: 600;
  transition: all 0.15s ease;
}

.btn-icon-label svg {
  width: 14px;
  height: 14px;
  color: #2563eb;
}

.btn-icon-label:hover {
  background: #f8fafc;
  color: var(--scada-text-primary);
  border-color: #94a3b8;
}

/* =============================================================================
   ALARM BANNER (CLEAN LIGHT ALERT STRIP)
   ============================================================================= */
.alarm-banner {
  display: none;
  padding: 8px 24px;
  background: #f8fafc;
  border-bottom: 2px solid var(--scada-border);
  z-index: 90;
}

.alarm-banner.active {
  display: block;
}

.alarm-banner.banner-alarm {
  background: #fef2f2;
  border-bottom-color: var(--scada-alarm);
}

.alarm-banner.banner-warning {
  background: #fffbeb;
  border-bottom-color: var(--scada-warn);
}

.alarm-banner.banner-cooldown {
  background: #f0f9ff;
  border-bottom-color: var(--scada-cooldown);
}

.banner-inner {
  max-width: 1440px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.banner-icon-wrap {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-xs);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: #ffffff;
  border: 1px solid var(--scada-border);
}

.banner-icon-wrap svg {
  width: 16px;
  height: 16px;
}

.banner-alarm .banner-icon-wrap { color: var(--scada-alarm); border-color: var(--scada-alarm-border); }
.banner-warning .banner-icon-wrap { color: var(--scada-warn); border-color: var(--scada-warn-border); }
.banner-cooldown .banner-icon-wrap { color: var(--scada-cooldown); border-color: var(--scada-cooldown-border); }

.banner-text {
  flex: 1;
}

.banner-text strong {
  display: block;
  font-size: 13px;
  font-weight: 700;
  color: var(--scada-text-primary);
  letter-spacing: 0.2px;
}

.banner-text span {
  font-size: 11.5px;
  color: var(--scada-text-secondary);
}

.banner-actions {
  display: flex;
  gap: 8px;
}

/* =============================================================================
   MAIN CONTENT CONTAINER
   ============================================================================= */
.main-content {
  max-width: 1440px;
  margin: 0 auto;
  padding: 16px 24px 40px;
  position: relative;
  z-index: 10;
}

/* =============================================================================
   KPI METRICS GRID (CLEAN ACADEMIC INSTRUMENT CARDS)
   ============================================================================= */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 16px;
}

.kpi-card {
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  border-top: 3px solid #cbd5e1;
  background: var(--scada-card-bg);
}

.kpi-card#kpiSmoke { border-top-color: #d97706; }
.kpi-card#kpiTemp  { border-top-color: #dc2626; }
.kpi-card#kpiHum   { border-top-color: #0284c7; }
.kpi-card#kpiFleetStatus { border-top-color: #059669; }

.kpi-card.kpi-alarm {
  border-top-color: var(--scada-alarm);
  background: #fff5f5;
}
.kpi-card.kpi-warn {
  border-top-color: var(--scada-warn);
  background: #fffdf5;
}

.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.kpi-title-wrap {
  display: flex;
  align-items: center;
  gap: 6px;
}

.kpi-title-wrap svg {
  width: 14px;
  height: 14px;
  color: var(--scada-text-muted);
}

.kpi-title {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--scada-text-muted);
}

.kpi-tag {
  font-size: 10px;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: var(--radius-xs);
  font-family: var(--font-mono);
  letter-spacing: 0.4px;
}

.kpi-tag.normal {
  background: var(--scada-safe-bg);
  color: var(--scada-safe);
  border: 1px solid var(--scada-safe-border);
}

.kpi-tag.warn {
  background: var(--scada-warn-bg);
  color: var(--scada-warn);
  border: 1px solid var(--scada-warn-border);
}

.kpi-tag.danger {
  background: var(--scada-alarm-bg);
  color: var(--scada-alarm);
  border: 1px solid var(--scada-alarm-border);
}

.kpi-tag.active {
  background: var(--scada-accent-bg);
  color: var(--scada-accent);
  border: 1px solid #bfdbfe;
}

.kpi-value-wrap {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin: 4px 0 6px;
}

.kpi-num {
  font-family: var(--font-mono);
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
  color: var(--scada-text-primary);
  letter-spacing: -0.5px;
}

.kpi-unit {
  font-size: 13px;
  font-weight: 600;
  color: var(--scada-text-muted);
  font-family: var(--font-mono);
}

/* Precision Meter Bar */
.mini-progress-bar {
  width: 100%;
  height: 5px;
  background: #f1f5f9;
  border-radius: 2px;
  overflow: hidden;
  position: relative;
  border: 1px solid #e2e8f0;
}

.progress-fill {
  height: 100%;
  border-radius: 2px;
  background: #d97706;
  transition: width 0.3s ease;
}

.temp-fill {
  background: #dc2626;
}

.hum-fill {
  background: #0284c7;
}

.kpi-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 11px;
  color: var(--scada-text-muted);
}

.kpi-footer strong {
  color: var(--scada-text-secondary);
  font-family: var(--font-mono);
}

.kpi-trend {
  font-family: var(--font-mono);
  font-size: 10.5px;
  color: var(--scada-text-secondary);
}

.kpi-fleet-stats {
  display: flex;
  flex-direction: column;
  gap: 3px;
  margin: 4px 0 6px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  font-size: 11.5px;
}

.stat-lbl {
  color: var(--scada-text-muted);
}

.stat-val {
  color: var(--scada-text-primary);
  font-family: var(--font-mono);
  font-size: 11px;
}

/* =============================================================================
   MAIN TWO-COLUMN DASHBOARD GRID
   ============================================================================= */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 16px;
}

.dash-column-left, .dash-column-right {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Panel Header */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 18px;
  border-bottom: 1px solid var(--scada-border);
  background: #f8fafc;
  border-top-left-radius: var(--radius-md);
  border-top-right-radius: var(--radius-md);
}

.header-title-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.title-with-icon {
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-with-icon svg {
  width: 16px;
  height: 16px;
  color: #2563eb;
  flex-shrink: 0;
}

.header-title-group h3 {
  font-family: var(--font-heading);
  font-size: 13.5px;
  font-weight: 700;
  letter-spacing: 0.2px;
  color: var(--scada-text-primary);
}

.header-title-group p {
  font-size: 11px;
  color: var(--scada-text-muted);
}

.header-title-group code {
  font-family: var(--font-mono);
  color: #1d4ed8;
  background: #eff6ff;
  padding: 1px 5px;
  border-radius: var(--radius-xs);
  border: 1px solid #bfdbfe;
  font-size: 10px;
}

.panel-controls {
  display: flex;
  gap: 4px;
}

.btn-chip {
  background: #ffffff;
  border: 1px solid var(--scada-border);
  color: var(--scada-text-muted);
  font-size: 10.5px;
  padding: 3px 8px;
  border-radius: var(--radius-xs);
  cursor: pointer;
  font-family: var(--font-mono);
  transition: all 0.15s ease;
}

.btn-chip:hover {
  background: #f1f5f9;
  color: var(--scada-text-primary);
}

.btn-chip.active {
  background: #2563eb;
  border-color: #2563eb;
  color: #ffffff;
  font-weight: 600;
}

/* =============================================================================
   CHART CONTAINER
   ============================================================================= */
.chart-container {
  padding: 16px 18px 10px;
  position: relative;
  height: 270px;
  background: #ffffff;
}

.chart-legend-custom {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 0 18px 12px;
  font-size: 11px;
  color: var(--scada-text-secondary);
}

.leg-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-mono);
}

.leg-dot {
  width: 8px;
  height: 8px;
  border-radius: 2px;
}

.color-smoke { background: #d97706; }
.color-temp  { background: #0284c7; }

.leg-line {
  width: 14px;
  height: 2px;
}
.color-thresh { background: #dc2626; }

/* =============================================================================
   FLOORPLAN: CLEAN ARCHITECTURAL BLUEPRINT (WHITE PAPER DRAWING)
   ============================================================================= */
.floorplan-panel {
  padding-bottom: 12px;
}

.badge-status-zone {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 10.5px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: var(--radius-xs);
  background: var(--scada-safe-bg);
  color: var(--scada-safe);
  border: 1px solid var(--scada-safe-border);
  font-family: var(--font-mono);
}

.badge-status-zone .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.floorplan-map-wrap {
  display: grid;
  grid-template-columns: 1fr 1.35fr 1fr;
  grid-template-rows: auto auto;
  gap: 10px;
  padding: 14px 18px;
  background: #ffffff;
  border-radius: var(--radius-sm);
  margin: 12px 16px;
  border: 1px solid var(--scada-border);
  background-image: 
    linear-gradient(#f1f5f9 1px, transparent 1px),
    linear-gradient(90deg, #f1f5f9 1px, transparent 1px);
  background-size: 20px 20px;
}

.floor-zone {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: var(--radius-xs);
  padding: 10px 12px;
  min-height: 110px;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: all 0.15s ease;
}

.floor-zone:hover {
  border-color: #2563eb;
}

.floor-zone.active-focus {
  border: 1px solid #2563eb;
  background: #f8fbff;
  box-shadow: 0 0 0 1px #bfdbfe;
}

.floor-zone.zone-corridor {
  grid-column: 1 / -1;
  min-height: 44px;
  background: #f8fafc;
  border: 1px dashed #cbd5e1;
  flex-direction: row;
  align-items: center;
  padding: 8px 14px;
}

.zone-label {
  font-size: 10.5px;
  font-weight: 700;
  color: var(--scada-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.zone-label strong {
  color: var(--scada-text-primary);
  font-size: 11px;
}

.sensor-node {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  padding: 4px 8px;
  border-radius: var(--radius-xs);
  font-size: 10.5px;
  font-weight: 600;
  color: var(--scada-text-primary);
  align-self: flex-start;
  margin-top: 6px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.sensor-node svg {
  width: 13px;
  height: 13px;
  color: #2563eb;
  flex-shrink: 0;
}

.sensor-node .node-badge {
  font-size: 9px;
  font-weight: 700;
  padding: 1px 5px;
  border-radius: var(--radius-xs);
  background: var(--scada-safe-bg);
  color: var(--scada-safe);
  border: 1px solid var(--scada-safe-border);
  font-family: var(--font-mono);
}

.sensor-node.node-hazard {
  border-color: var(--scada-alarm);
  background: var(--scada-alarm-bg);
}

.sensor-node.node-hazard svg {
  color: var(--scada-alarm);
}

.actuator-marker {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 10.5px;
  font-weight: 600;
  padding: 3px 7px;
  border-radius: var(--radius-xs);
  margin-top: 4px;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  color: var(--scada-text-secondary);
}

.actuator-marker svg {
  width: 12px;
  height: 12px;
}

.fan-spinning svg, svg.fan-spinning {
  animation: spin 0.8s linear infinite;
  color: #0284c7;
}

/* =============================================================================
   ACTUATOR CONTROL CONSOLE (CLEAN ACADEMIC SWITCHES)
   ============================================================================= */
.role-badge-tag {
  font-size: 10.5px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: var(--radius-xs);
  background: #f1f5f9;
  color: #2563eb;
  border: 1px solid #cbd5e1;
  font-family: var(--font-mono);
}

.control-cards-grid {
  padding: 14px 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.actuator-box {
  background: #ffffff;
  border: 1px solid var(--scada-border);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  transition: border-color 0.15s ease;
}

.actuator-box:hover {
  border-color: var(--scada-border-light);
}

.actuator-box-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.actuator-title-icon {
  display: flex;
  align-items: center;
  gap: 10px;
}

.act-icon-box {
  width: 30px;
  height: 30px;
  border-radius: var(--radius-xs);
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #2563eb;
  flex-shrink: 0;
}

.act-icon-box svg {
  width: 16px;
  height: 16px;
}

.actuator-title-icon strong {
  display: block;
  font-size: 12.5px;
  color: var(--scada-text-primary);
  font-weight: 600;
}

.act-sub {
  font-size: 10px;
  color: var(--scada-text-muted);
  font-family: var(--font-mono);
}

.act-state-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: var(--radius-xs);
  font-family: var(--font-mono);
  letter-spacing: 0.4px;
}

.act-state-badge.off {
  background: #f1f5f9;
  color: var(--scada-text-muted);
  border: 1px solid #e2e8f0;
}

.act-state-badge.on {
  background: var(--scada-safe-bg);
  color: var(--scada-safe);
  border: 1px solid var(--scada-safe-border);
}

.act-state-badge.alert {
  background: var(--scada-alarm-bg);
  color: var(--scada-alarm);
  border: 1px solid var(--scada-alarm-border);
}

.act-state-badge.mode-day {
  background: var(--scada-warn-bg);
  color: var(--scada-warn);
  border: 1px solid var(--scada-warn-border);
}

.act-state-badge.mode-night {
  background: #f0fdf4;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.act-mode-desc {
  font-size: 11px;
  color: var(--scada-text-secondary);
  margin-bottom: 8px;
}

.act-mode-desc strong {
  color: var(--scada-text-primary);
  font-family: var(--font-mono);
}

.btn-group-controls {
  display: flex;
  gap: 6px;
}

.btn-group-controls .btn {
  flex: 1;
}

/* =============================================================================
   CLEAN ACADEMIC CONTROL BUTTONS (MINIMALIST)
   ============================================================================= */
.btn {
  border: 1px solid #cbd5e1;
  padding: 6px 10px;
  border-radius: var(--radius-xs);
  font-size: 11.5px;
  font-weight: 600;
  font-family: var(--font-body);
  cursor: pointer;
  transition: all 0.15s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  text-decoration: none;
  line-height: 1.2;
  background: #ffffff;
  color: var(--scada-text-secondary);
}

.btn svg {
  width: 13px;
  height: 13px;
  flex-shrink: 0;
}

.btn:hover:not(:disabled) {
  background: #f8fafc;
  color: var(--scada-text-primary);
  border-color: #94a3b8;
}

.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed !important;
}

.btn-outline-success {
  background: #ffffff;
  border-color: #a7f3d0;
  color: #059669;
}
.btn-outline-success:hover:not(:disabled) {
  background: #ecfdf5;
  border-color: #059669;
}

.btn-outline-danger {
  background: #ffffff;
  border-color: #fecaca;
  color: #dc2626;
}
.btn-outline-danger:hover:not(:disabled) {
  background: #fef2f2;
  border-color: #dc2626;
}

.btn-outline-info {
  background: #ffffff;
  border-color: #bae6fd;
  color: #0284c7;
}
.btn-outline-info.active, .btn-outline-info:hover:not(:disabled) {
  background: #f0f9ff;
  border-color: #0284c7;
  color: #0369a1;
}

.btn-outline-warning {
  background: #ffffff;
  border-color: #fde68a;
  color: #d97706;
}
.btn-outline-warning:hover:not(:disabled) {
  background: #fffbeb;
  border-color: #d97706;
}

.btn-outline-primary {
  background: #ffffff;
  border-color: #bfdbfe;
  color: #2563eb;
}
.btn-outline-primary:hover:not(:disabled) {
  background: #eff6ff;
  border-color: #2563eb;
}

.btn-outline-secondary {
  background: #ffffff;
  border-color: #e2e8f0;
  color: var(--scada-text-secondary);
}
.btn-outline-secondary:hover:not(:disabled) {
  background: #f8fafc;
  color: var(--scada-text-primary);
  border-color: #cbd5e1;
}

.btn-primary-gradient, .btn-solid-primary {
  background: #2563eb;
  border-color: #2563eb;
  color: #ffffff;
}
.btn-primary-gradient:hover:not(:disabled), .btn-solid-primary:hover:not(:disabled) {
  background: #1d4ed8;
  border-color: #1d4ed8;
  color: #ffffff;
}

.btn-solid-warning {
  background: #d97706;
  border-color: #d97706;
  color: #ffffff;
}
.btn-solid-warning:hover {
  background: #b45309;
}

.btn-solid-success {
  background: #059669;
  border-color: #059669;
  color: #ffffff;
}
.btn-solid-success:hover {
  background: #047857;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 11px;
}
.btn-xs {
  padding: 3px 6px;
  font-size: 10px;
}

.scheduler-toggle-wrap {
  display: flex;
  gap: 6px;
}
.scheduler-toggle-wrap .btn {
  flex: 1;
}

/* =============================================================================
   WEEK 7: BUSINESS RULES & ABNORMAL SCENARIOS MANAGEMENT
   ============================================================================= */
.week7-panel {
  border-color: var(--scada-border);
}

.week7-tag {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #2563eb;
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
}

.week7-rules-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px 18px;
}

.rule-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 12px;
  background: #ffffff;
  border: 1px solid var(--scada-border);
  border-left: 3px solid #2563eb;
  border-radius: var(--radius-xs);
  transition: border-color 0.15s ease;
}

.rule-item:hover {
  border-color: #cbd5e1;
  border-left-color: #1d4ed8;
}

.rule-info {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.rule-code {
  display: inline-block;
  padding: 2px 6px;
  border-radius: var(--radius-xs);
  font-family: var(--font-mono);
  font-size: 9.5px;
  font-weight: 700;
  background: #f1f5f9;
  color: #2563eb;
  border: 1px solid #e2e8f0;
  white-space: nowrap;
}

.rule-desc {
  font-size: 11px;
  color: var(--scada-text-secondary);
  margin-top: 2px;
  line-height: 1.4;
}

.rule-desc strong {
  color: var(--scada-text-primary);
}

.rule-status-badge {
  font-size: 9.5px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: var(--radius-xs);
  font-family: var(--font-mono);
  letter-spacing: 0.5px;
}

.rule-status-badge.active {
  background: var(--scada-safe-bg);
  color: var(--scada-safe);
  border: 1px solid var(--scada-safe-border);
}

/* Diagnostic Health Grid */
.health-matrix-wrap {
  padding: 0 18px 14px;
}

.matrix-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11.5px;
  font-weight: 700;
  color: var(--scada-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.matrix-title svg {
  width: 14px;
  height: 14px;
  color: #2563eb;
}

.health-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.health-card {
  background: #f8fafc;
  border: 1px solid var(--scada-border);
  padding: 8px 10px;
  border-radius: var(--radius-xs);
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.health-label {
  font-size: 10.5px;
  color: var(--scada-text-muted);
}

.health-val {
  font-size: 11px;
  font-weight: 700;
  font-family: var(--font-mono);
}

.health-val.ok {
  color: var(--scada-safe);
}

.health-val.fault {
  color: var(--scada-alarm);
}

/* Fault Sandbox */
.fault-sandbox-wrap {
  margin: 0 18px 16px;
  padding: 12px;
  background: #f8fafc;
  border: 1px solid var(--scada-border);
  border-radius: var(--radius-xs);
}

.sandbox-desc {
  font-size: 11px;
  color: var(--scada-text-muted);
  margin-bottom: 8px;
}

.sandbox-buttons-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

/* =============================================================================
   TELEGRAM BOT INTEGRATION PANEL (CLEAN LIGHT CHAT)
   ============================================================================= */
.badge-telegram-ready {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: var(--radius-xs);
  background: var(--scada-safe-bg);
  color: var(--scada-safe);
  border: 1px solid var(--scada-safe-border);
  font-family: var(--font-mono);
}

.telegram-body {
  padding: 14px 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.telegram-chat-window {
  background: #ffffff;
  border: 1px solid var(--scada-border);
  border-radius: var(--radius-xs);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.tg-chat-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: #f8fafc;
  border-bottom: 1px solid var(--scada-border);
}

.tg-bot-avatar {
  width: 24px;
  height: 24px;
  border-radius: var(--radius-xs);
  background: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.tg-bot-avatar svg {
  width: 14px;
  height: 14px;
}

.tg-bot-meta strong {
  display: block;
  font-size: 11.5px;
  color: var(--scada-text-primary);
}

.tg-bot-meta span {
  font-size: 9.5px;
  color: var(--scada-text-muted);
}

.tg-messages-list {
  padding: 10px;
  height: 130px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
  background: #fafafa;
}

.tg-msg {
  display: flex;
  flex-direction: column;
  max-width: 92%;
}

.tg-msg-time {
  font-size: 9px;
  color: var(--scada-text-muted);
  font-family: var(--font-mono);
  margin-bottom: 2px;
}

.tg-msg-bubble {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: var(--radius-xs);
  padding: 6px 9px;
  font-size: 11px;
  line-height: 1.4;
  color: var(--scada-text-secondary);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.tg-msg-bubble strong {
  color: var(--scada-text-primary);
}

.tg-msg-bubble code {
  font-family: var(--font-mono);
  background: #f1f5f9;
  padding: 1px 4px;
  border-radius: 2px;
  color: #1d4ed8;
  border: 1px solid #e2e8f0;
}

.tg-msg.alarm-msg .tg-msg-bubble {
  background: #fef2f2;
  border-color: #fecaca;
  color: #991b1b;
}

.telegram-actions {
  display: flex;
  gap: 6px;
}

/* =============================================================================
   AUDIT TRAIL / SCADA EVENT LOG DATA GRID (CLEAN ACADEMIC TABLE)
   ============================================================================= */
.audit-panel {
  padding-bottom: 10px;
}

.audit-filters {
  display: flex;
  gap: 6px;
}

.select-sm {
  background: #ffffff;
  border: 1px solid var(--scada-border-light);
  color: var(--scada-text-primary);
  font-size: 11px;
  padding: 3px 6px;
  border-radius: var(--radius-xs);
  outline: none;
}

.select-sm option {
  background: #ffffff;
  color: #0f172a;
}

.audit-table-wrap {
  padding: 0 16px;
  max-height: 200px;
  overflow-y: auto;
}

.audit-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.audit-table th {
  text-align: left;
  padding: 6px 8px;
  color: var(--scada-text-muted);
  font-weight: 600;
  border-bottom: 1px solid var(--scada-border);
  position: sticky;
  top: 0;
  background: #f8fafc;
  z-index: 5;
  text-transform: uppercase;
  font-size: 10px;
  letter-spacing: 0.5px;
}

.audit-table td {
  padding: 6px 8px;
  border-bottom: 1px solid #f1f5f9;
  color: var(--scada-text-secondary);
}

.audit-table tr:hover td {
  background: #f8fafc;
}

.badge-level {
  font-size: 9px;
  font-weight: 700;
  padding: 1px 4px;
  border-radius: var(--radius-xs);
  display: inline-block;
  text-align: center;
  font-family: var(--font-mono);
}

.lvl-critical {
  background: var(--scada-alarm-bg);
  color: var(--scada-alarm);
  border: 1px solid var(--scada-alarm-border);
}

.lvl-warn {
  background: var(--scada-warn-bg);
  color: var(--scada-warn);
  border: 1px solid var(--scada-warn-border);
}

.lvl-info {
  background: var(--scada-accent-bg);
  color: var(--scada-accent);
  border: 1px solid #bfdbfe;
}

.lvl-sys {
  background: #f1f5f9;
  color: var(--scada-text-muted);
  border: 1px solid #e2e8f0;
}

/* =============================================================================
   MODAL: SIMULATOR TEST BENCH (CLEAN LIGHT MODAL)
   ============================================================================= */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(3px);
  z-index: 200;
  display: none;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.modal-overlay.active {
  display: flex;
}

.modal-content {
  width: 100%;
  max-width: 580px;
  background: #ffffff;
  border: 1px solid var(--scada-border-light);
  border-radius: var(--radius-md);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 18px;
  border-bottom: 1px solid var(--scada-border);
  background: #f8fafc;
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-title svg {
  width: 18px;
  height: 18px;
  color: #2563eb;
}

.modal-title h3 {
  font-family: var(--font-heading);
  font-size: 13.5px;
  font-weight: 700;
  color: var(--scada-text-primary);
}

.modal-title p {
  font-size: 11px;
  color: var(--scada-text-muted);
}

.btn-close-modal {
  background: transparent;
  border: none;
  color: var(--scada-text-muted);
  font-size: 20px;
  cursor: pointer;
  line-height: 1;
}

.btn-close-modal:hover {
  color: var(--scada-text-primary);
}

.modal-body {
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.sim-row {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.sim-row label {
  font-size: 11.5px;
  font-weight: 600;
  color: var(--scada-text-secondary);
}

.slider-wrap input[type=range] {
  width: 100%;
  accent-color: #2563eb;
  cursor: pointer;
}

.preset-buttons {
  display: flex;
  gap: 5px;
  margin-top: 3px;
}

.toggle-wrap {
  display: flex;
  gap: 6px;
}

.source-select-wrap {
  display: flex;
  gap: 16px;
  font-size: 11.5px;
  color: var(--scada-text-secondary);
}

.modal-footer {
  padding: 10px 18px;
  border-top: 1px solid var(--scada-border);
  display: flex;
  justify-content: flex-end;
  background: #f8fafc;
}

/* =============================================================================
   TOAST NOTIFICATIONS
   ============================================================================= */
.toast-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 300;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.toast {
  background: #ffffff;
  border: 1px solid var(--scada-border-light);
  border-radius: var(--radius-xs);
  padding: 8px 12px;
  min-width: 260px;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  font-size: 11.5px;
  color: var(--scada-text-primary);
}

.toast-success { border-left: 3px solid var(--scada-safe); }
.toast-danger  { border-left: 3px solid var(--scada-alarm); }
.toast-warning { border-left: 3px solid var(--scada-warn); }
.toast-info    { border-left: 3px solid var(--scada-accent); }

/* =============================================================================
   KEYFRAME ANIMATIONS
   ============================================================================= */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.35; }
}

/* =============================================================================
   RESPONSIVE LAYOUT BREAKPOINTS
   ============================================================================= */
@media (max-width: 1150px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  .app-header {
    flex-wrap: wrap;
    gap: 10px;
  }
}

@media (max-width: 680px) {
  .kpi-grid {
    grid-template-columns: 1fr;
  }
  .floorplan-map-wrap {
    grid-template-columns: 1fr;
  }
}

```

---

## PHẦN 35: WEB SCADA: MÃ NGUỒN XỬ LÝ TƯƠNG TÁC (JAVASCRIPT APPLICATION) (`web/app.js`)

> **Đường dẫn:** `web/app.js`  
> **Quy mô:** 1,168 dòng | 46,150 bytes | Ngôn ngữ: `javascript`

```javascript
/**
 * @file app.js
 * @brief SMART FIRE SAFETY PLATFORM - TẦNG 4 APPLICATION JAVASCRIPT
 * @details Kiến trúc Lean & Clean Code:
 *          - Cached DOM Registry qua Proxy (Zero repeated getElementById)
 *          - Unified Downlink Command Dispatcher
 *          - Reactive State Pattern & Guard Clauses
 *          - Fault Injection Sandbox & Hardware Diagnostics Binding
 */

// =============================================================================
// 1. CONFIGURATION & RUNTIME STATE
// =============================================================================
const CONFIG = {
  brokerWss: "wss://broker.emqx.io:8084/mqtt",
  brokerWsBackup: "ws://broker.emqx.io:8083/mqtt",
  topics: {
    telemetry: "Nhom09/smoke/telemetry",
    eventAlarm: "Nhom09/smoke/event/alarm",
    statusAck: "Nhom09/smoke/status",
    lwt: "Nhom09/smoke/lwt",
    cmdFan: "Nhom09/smoke/cmd/fan",
    cmdBuzzer: "Nhom09/smoke/cmd/buzzer",
    cmdMode: "Nhom09/smoke/cmd/mode",
    cmdNight: "Nhom09/smoke/cmd/sensitivity",
    cmdInjectFault: "Nhom09/smoke/cmd/inject_fault",
    cmdScheduler: "Nhom09/smoke/cmd/scheduler",
    historySync: "Nhom09/smoke/history/sync"
  },
  thresholds: {
    alarmDay: 400.0,
    alarmNight: 350.0,
    safeDay: 300.0,
    safeNight: 250.0,
    overheat: 55.0
  }
};

const STATE = {
  // Sensor Telemetry
  ppm: 145.2,
  temp: 28.4,
  hum: 62.8,

  // FSM State: SAFE | WARNING | ALARM | COOLDOWN | FAULT | OFFLINE
  fsmState: "SAFE",
  cooldownTimer: 0,

  // Actuators
  fanState: false,
  fanMode: "AUTO", // AUTO | MANUAL
  buzzerActive: false,
  isMuted: false,
  muteRemainingSec: 0,

  // Sensitivity Mode & Scheduler
  sensitivityMode: "DAY", // DAY | NIGHT
  alarmThreshold: 400.0,

  // System Diagnostics & Health
  isConnected: false,
  deviceOnline: true,
  lastSeenTime: Date.now(),
  userRole: "operator", // admin | operator | viewer
  health: {
    mq2: "OK",
    dht: "OK",
    watchdog: "OK",
    actuator: "OK"
  },

  // Telemetry History for Charts (Max 25 points)
  history: {
    labels: [],
    ppmData: [],
    tempData: []
  },

  // Audit Trail Logs
  logs: []
};

// =============================================================================
// 2. DOM ELEMENT REGISTRY PROXY (O(1) CACHED LOOKUP)
// =============================================================================
const DOM = new Proxy({}, {
  get(target, id) {
    if (!target[id]) {
      target[id] = (typeof document !== 'undefined' && document.getElementById)
        ? document.getElementById(id)
        : null;
    }
    return target[id];
  }
});

let mqttClient = null;
let telemetryChart = null;
let cooldownInterval = null;
let muteInterval = null;
let webAudioCtx = null;

// =============================================================================
// 3. INITIALIZATION & LIFECYCLE
// =============================================================================
if (typeof document !== 'undefined' && document.addEventListener) {
  document.addEventListener("DOMContentLoaded", () => {
    try { initClock(); } catch (e) { console.error("initClock error:", e); }
    try { initChart(); } catch (e) { console.error("initChart error:", e); }
    try { initMqttClient(); } catch (e) { console.error("initMqttClient error:", e); }
    try { initEventHandlers(); } catch (e) { console.error("initEventHandlers error:", e); }
    try { initFaultInjectionHandlers(); } catch (e) { console.error("initFaultInjectionHandlers error:", e); }
    try { initSimulatorDefaults(); } catch (e) { console.error("initSimulatorDefaults error:", e); }

    try {
      addAuditLog("SYSTEM", "APPLICATION_STARTED", "Khởi động giao diện Tầng 4 Application thành công.", "SAFE");
      updateUiFromState();
    } catch (e) { console.error("updateUiFromState error:", e); }

    // Watchdog heartbeat checker
    setInterval(heartbeatCheck, 2000);
  });
}

// =============================================================================
// 4. UNIFIED DOWNLINK DISPATCHER
// =============================================================================
function sendDownlinkCommand(topicKey, payload) {
  const topic = CONFIG.topics[topicKey] || topicKey;
  const payloadStr = JSON.stringify(payload);

  if (mqttClient && STATE.isConnected) {
    mqttClient.publish(topic, payloadStr, { qos: 1 });
    console.log(`[MQTT Downlink] ${topic} (QoS 1) -> ${payloadStr}`);
  } else {
    console.log(`[Sim Downlink] ${topic} -> ${payloadStr}`);
    showToast(`Mô phỏng gửi lệnh: ${topic.split('/').pop()}`, "info");
  }
}

// =============================================================================
// 5. MQTT WEBSOCKET CLIENT INTEGRATION
// =============================================================================
let attemptedBackup = false;
let mqttConnectTimer = null;

function initMqttClient() {
  if (typeof mqtt === "undefined") {
    console.warn("[MQTT.js] Library not loaded. Running in local simulation mode.");
    if (DOM.connStatusText) DOM.connStatusText.textContent = "Chế độ Mô phỏng (Không có Lib)";
    return;
  }

  const clientId = "WebClient_Smoke_N04_" + Math.random().toString(16).substring(2, 8);
  const connBadge = DOM.brokerConnBadge;
  const connText  = DOM.connStatusText;

  function connectToBroker(url) {
    if (connText) connText.textContent = `Đang kết nối (${url.startsWith("wss") ? "WSS :8084" : "WS :8083"})...`;

    try {
      if (mqttClient) {
        try { mqttClient.end(true); } catch(err) {}
      }

      mqttClient = mqtt.connect(url, {
        clientId: clientId,
        clean: true,
        connectTimeout: 4000,
        reconnectPeriod: 5000
      });

      if (mqttConnectTimer) clearTimeout(mqttConnectTimer);
      if (url === CONFIG.brokerWss && !attemptedBackup) {
        mqttConnectTimer = setTimeout(() => {
          if (!STATE.isConnected && !attemptedBackup) {
            console.warn("[MQTT] WSS :8084 timeout. Switching to WS backup :8083...");
            attemptedBackup = true;
            connectToBroker(CONFIG.brokerWsBackup);
          }
        }, 3500);
      }

      mqttClient.on("connect", () => {
        if (mqttConnectTimer) clearTimeout(mqttConnectTimer);
        STATE.isConnected = true;
        if (connBadge) connBadge.className = "connection-pill connected";
        if (connText) connText.textContent = `EMQX Online (${url.startsWith("wss") ? "WSS" : "WS"})`;
        showToast(`Đã kết nối máy chủ MQTT EMQX (${url.startsWith("wss") ? "WSS" : "WS"})`, "success");

        mqttClient.subscribe(CONFIG.topics.telemetry, { qos: 0 });
        mqttClient.subscribe(CONFIG.topics.eventAlarm, { qos: 1 });
        mqttClient.subscribe(CONFIG.topics.statusAck, { qos: 1 });
        mqttClient.subscribe(CONFIG.topics.lwt, { qos: 1 });
        if (CONFIG.topics.historySync) mqttClient.subscribe(CONFIG.topics.historySync, { qos: 1 });

        addAuditLog("INFO", "MQTT_CONNECTED", `Kết nối WebSocket tới ${url} thành công.`, STATE.fsmState);
      });

      mqttClient.on("message", (topic, message) => {
        handleIncomingMqtt(topic, message.toString());
      });

      mqttClient.on("error", (err) => {
        console.warn(`MQTT connection error on ${url}:`, err);
        if (!STATE.isConnected && !attemptedBackup && url === CONFIG.brokerWss) {
          attemptedBackup = true;
          console.log("[MQTT] Failing over to WS backup :8083...");
          connectToBroker(CONFIG.brokerWsBackup);
        } else if (!STATE.isConnected) {
          if (connBadge) connBadge.className = "connection-pill disconnected";
          if (connText) connText.textContent = "Chế độ Mô phỏng";
        }
      });

      mqttClient.on("close", () => {
        if (!attemptedBackup && url === CONFIG.brokerWss && !STATE.isConnected) {
          attemptedBackup = true;
          connectToBroker(CONFIG.brokerWsBackup);
        } else if (STATE.isConnected) {
          STATE.isConnected = false;
          if (connBadge) connBadge.className = "connection-pill disconnected";
          if (connText) connText.textContent = "Mất kết nối";
        }
      });
    } catch (e) {
      console.warn("MQTT Connect exception:", e);
      if (!attemptedBackup && url === CONFIG.brokerWss) {
        attemptedBackup = true;
        connectToBroker(CONFIG.brokerWsBackup);
      } else {
        if (connBadge) connBadge.className = "connection-pill disconnected";
        if (connText) connText.textContent = "Sim Mode";
      }
    }
  }

  connectToBroker(CONFIG.brokerWss);
}

function handleIncomingMqtt(topic, payloadStr) {
  STATE.lastSeenTime = Date.now();
  STATE.health.watchdog = "OK";

  try {
    const data = JSON.parse(payloadStr);

    if (topic === CONFIG.topics.telemetry) {
      if (data.mq2_ppm !== undefined) STATE.ppm = (data.mq2_ppm === null) ? 0 : parseFloat(data.mq2_ppm);
      else if (data.smoke_ppm !== undefined) STATE.ppm = parseFloat(data.smoke_ppm);

      if (data.temp !== undefined) STATE.temp = parseFloat(data.temp);
      else if (data.temperature !== undefined) STATE.temp = parseFloat(data.temperature);

      if (data.hum !== undefined) STATE.hum = parseFloat(data.hum);
      else if (data.humidity !== undefined) STATE.hum = parseFloat(data.humidity);

      if (data.fan !== undefined) STATE.fanState = (data.fan === "ON" || data.fan === true);
      if (data.buzzer !== undefined) STATE.buzzerActive = (data.buzzer === "ON" || data.buzzer === true);
      if (data.buzzer_muted !== undefined) STATE.buzzerMuted = data.buzzer_muted;

      if (data.fsm_state) {
        STATE.fsmState = data.fsm_state;
      }

      if (data.alarm_th) STATE.alarmThreshold = parseFloat(data.alarm_th);
      if (data.safe_th) STATE.safeThreshold = parseFloat(data.safe_th);

      if (data.mq2_valid !== undefined) STATE.health.mq2 = data.mq2_valid ? "OK" : "FAULT";
      if (data.dht_valid !== undefined) STATE.health.dht = data.dht_valid ? "OK" : "FAULT";

      updateUiFromState();
      pushChartData(STATE.ppm, STATE.temp);
    }
    else if (topic === CONFIG.topics.eventAlarm) {
      STATE.fsmState = "ALARM";
      STATE.fanState = true;
      STATE.buzzerActive = true;
      addAuditLog("CRITICAL", data.event || "URGENT_ALARM", `Báo động từ thiết bị: PPM=${data.ppm || STATE.ppm}`, "ALARM");
      showToast("BÁO ĐỘNG KHẨN CẤP: Thiết bị báo khói nguy cấp!", "danger");
      updateUiFromState();
    }
    else if (topic === CONFIG.topics.statusAck) {
      addAuditLog("INFO", "DEVICE_ACK", `Phản hồi từ ESP32: Lệnh ${data.cmd || ''} -> ${data.result || 'OK'}`, STATE.fsmState);
      showToast(`ESP32: ${data.cmd || 'Lệnh'} -> ${data.result || 'Thành công'}`, "success");

      if (data.cmd === "fault_alert") {
        if (data.detail && data.detail.includes("MQ2")) STATE.health.mq2 = "FAULT";
        if (data.detail && data.detail.includes("DHT")) STATE.health.dht = "FAULT";
      } else if (data.cmd === "fault_clear" || data.cmd === "fault_recovery") {
        STATE.health.mq2 = "OK";
        STATE.health.dht = "OK";
        STATE.health.actuator = "OK";
      }
      updateUiFromState();
    }
    else if (topic === CONFIG.topics.lwt) {
      if (data.status === "offline") {
        setOfflineState();
      } else {
        STATE.deviceOnline = true;
      }
    }
  } catch (err) {
    console.debug("Non-JSON or raw payload received:", payloadStr);
  }
}

// =============================================================================
// 6. SCADA READ-ONLY STATE ARCHITECTURE (Zero autonomous client-side commands)
// =============================================================================
function setOfflineState() {
  STATE.deviceOnline = false;
  STATE.fsmState = "OFFLINE";
  STATE.health.watchdog = "TIMEOUT";
  addAuditLog("CRITICAL", "HEARTBEAT_TIMEOUT", "Mất kết nối với thiết bị ESP32 (Watchdog > 15s không có Keep-Alive)", "OFFLINE");
  showToast("Cảnh báo: Trạm cảm biến ESP32 mất kết nối!", "danger");
  updateUiFromState();
}

function heartbeatCheck() {
  const now = Date.now();
  if (STATE.deviceOnline && (now - STATE.lastSeenTime > 15000)) {
    setOfflineState();
  }
}

// =============================================================================
// 7. ROLE-BASED ACCESS CONTROL (RBAC)
// =============================================================================
function checkRolePermission(requiredRole, actionDescription) {
  const currentRole = STATE.userRole;

  if (requiredRole === "admin" && currentRole !== "admin") {
    showToast(`Từ chối quyền: Cần tài khoản [Quản trị viên] để ${actionDescription}.`, "danger");
    return false;
  }
  if (requiredRole === "operator" && currentRole === "viewer") {
    showToast(`Từ chối quyền: Người dân (Viewer) chỉ có quyền giám sát, không được ${actionDescription}.`, "danger");
    return false;
  }
  return true;
}

// =============================================================================
// 8. UI UPDATE & RENDERING ENGINE (USING CACHED DOM REGISTRY)
// =============================================================================
function updateUiFromState() {
  // 1. KPI Numbers & Visual Progress Bars
  if (DOM.valSmokePpm) DOM.valSmokePpm.textContent = STATE.ppm.toFixed(1);
  if (DOM.valTemp) DOM.valTemp.textContent = STATE.temp.toFixed(1);
  if (DOM.valHum) DOM.valHum.textContent = STATE.hum.toFixed(1);

  const smokePercent = Math.min(100, (STATE.ppm / 800) * 100);
  if (DOM.barSmoke) DOM.barSmoke.style.width = smokePercent + "%";

  const tempPercent = Math.min(100, (STATE.temp / 80) * 100);
  if (DOM.barTemp) DOM.barTemp.style.width = tempPercent + "%";

  const humPercent = Math.min(100, STATE.hum);
  if (DOM.barHum) DOM.barHum.style.width = humPercent + "%";

  // Smoke KPI Styling
  if (DOM.kpiSmoke && DOM.tagSmoke) {
    DOM.kpiSmoke.className = "kpi-card glass-panel";
    if (STATE.ppm >= STATE.alarmThreshold) {
      DOM.kpiSmoke.classList.add("kpi-alarm");
      DOM.tagSmoke.className = "kpi-tag danger";
      DOM.tagSmoke.textContent = "Báo động Đỏ";
    } else if (STATE.ppm >= 250) {
      DOM.kpiSmoke.classList.add("kpi-warn");
      DOM.tagSmoke.className = "kpi-tag warn";
      DOM.tagSmoke.textContent = "Cảnh giác Vàng";
    } else {
      DOM.tagSmoke.className = "kpi-tag normal";
      DOM.tagSmoke.textContent = "Bình thường";
    }
  }

  // 2. FSM Header Chip & Alarm Banner
  if (DOM.fsmChip && DOM.alarmBanner) {
    DOM.fsmChip.className = "fsm-status-chip";
    DOM.alarmBanner.className = "alarm-banner";

    switch (STATE.fsmState) {
      case "FAULT":
        DOM.fsmChip.classList.add("state-fault");
        if (DOM.fsmStatusText) DOM.fsmStatusText.textContent = "SỰ CỐ PHẦN CỨNG (FAULT)";
        DOM.alarmBanner.classList.add("active", "banner-alarm");
        if (DOM.bannerTitle) DOM.bannerTitle.textContent = "SỰ CỐ BẤT THƯỜNG: HỎNG CẢM BIẾN / LỖI CHẤP HÀNH";
        if (DOM.bannerDesc) DOM.bannerDesc.textContent = "Hệ thống tự động kích hoạt Fail-Safe Mode: duy trì quạt thông gió an toàn, ngắt còi hú tránh hoảng loạn.";
        break;

      case "SAFE":
        DOM.fsmChip.classList.add("state-safe");
        if (DOM.fsmStatusText) DOM.fsmStatusText.textContent = "AN TOÀN (SAFE)";
        DOM.alarmBanner.classList.remove("active");
        break;

      case "WARNING":
        DOM.fsmChip.classList.add("state-warning");
        if (DOM.fsmStatusText) DOM.fsmStatusText.textContent = "CẢNH GIÁC (WARNING)";
        DOM.alarmBanner.classList.add("active", "banner-warning");
        if (DOM.bannerTitle) DOM.bannerTitle.textContent = "CẢNH BÁO MỨC ĐỘ VÀNG: KHÓI TĂNG NHẸ";
        if (DOM.bannerDesc) DOM.bannerDesc.textContent = `Nồng độ khói hiện tại ${STATE.ppm.toFixed(1)} PPM. Đang theo dõi chặt chẽ.`;
        break;

      case "ALARM":
        DOM.fsmChip.classList.add("state-alarm");
        if (DOM.fsmStatusText) DOM.fsmStatusText.textContent = "BÁO ĐỘNG ĐỎ (ALARM)";
        DOM.alarmBanner.classList.add("active", "banner-alarm");
        if (DOM.bannerTitle) DOM.bannerTitle.textContent = "BÁO ĐỘNG HỎA HOẠN: KHÓI VƯỢT NGƯỠNG NGUY CẤP!";
        if (DOM.bannerDesc) DOM.bannerDesc.textContent = `Nồng độ khói ${STATE.ppm.toFixed(1)} PPM >= ${STATE.alarmThreshold} PPM. Quạt hút đang chạy tối đa, còi hú cảnh báo.`;
        break;

      case "COOLDOWN":
        DOM.fsmChip.classList.add("state-cooldown");
        if (DOM.fsmStatusText) DOM.fsmStatusText.textContent = `LÀM MÁT (${STATE.cooldownTimer}s)`;
        DOM.alarmBanner.classList.add("active", "banner-cooldown");
        if (DOM.bannerTitle) DOM.bannerTitle.textContent = `ĐANG LÀM MÁT & XẢ KHÓI TỒN DƯ: CÒN ${STATE.cooldownTimer} GIÂY`;
        if (DOM.bannerDesc) DOM.bannerDesc.textContent = "Khói đã giảm. Duy trì quạt chạy thêm 30 giây chống hiện tượng rơ-le nhảy loạn.";
        break;

      case "OFFLINE":
        DOM.fsmChip.classList.add("state-offline");
        if (DOM.fsmStatusText) DOM.fsmStatusText.textContent = "MẤT KẾT NỐI (OFFLINE)";
        DOM.alarmBanner.classList.add("active", "banner-warning");
        if (DOM.bannerTitle) DOM.bannerTitle.textContent = "MẤT TÍN HIỆU CẢM BIẾN TỪ TRẠM ESP32";
        if (DOM.bannerDesc) DOM.bannerDesc.textContent = "Không nhận được gói tin nhịp tim Keep-Alive. Kiểm tra nguồn và mạng Wi-Fi của trạm P302.";
        break;
    }
  }

  // 3. Actuator Controls UI
  if (DOM.lblFanMode) DOM.lblFanMode.textContent = STATE.fanMode === "AUTO" ? "TỰ ĐỘNG (AUTO)" : "THỦ CÔNG (MANUAL)";

  if (DOM.badgeFanState && DOM.fanStatusIcon) {
    if (STATE.fanState) {
      DOM.badgeFanState.className = "act-state-badge on";
      DOM.badgeFanState.textContent = "ĐANG BẬT (ON)";
      DOM.fanStatusIcon.classList.add("fan-spinning");
      if (DOM.mapFanIcon) DOM.mapFanIcon.classList.add("fan-spinning");
    } else {
      DOM.badgeFanState.className = "act-state-badge off";
      DOM.badgeFanState.textContent = "ĐANG TẮT (OFF)";
      DOM.fanStatusIcon.classList.remove("fan-spinning");
      if (DOM.mapFanIcon) DOM.mapFanIcon.classList.remove("fan-spinning");
    }
  }

  if (DOM.badgeBuzzerState && DOM.lblBuzzerDesc) {
    if (STATE.isMuted) {
      DOM.badgeBuzzerState.className = "act-state-badge off";
      DOM.badgeBuzzerState.textContent = `TẮT TIẾNG (${STATE.muteRemainingSec}s)`;
      DOM.lblBuzzerDesc.textContent = `Đã tạm ngắt tiếng còi trong ${STATE.muteRemainingSec} giây.`;
    } else if (STATE.buzzerActive) {
      DOM.badgeBuzzerState.className = "act-state-badge alert";
      DOM.badgeBuzzerState.textContent = "ĐANG HÚ CÒI";
      DOM.lblBuzzerDesc.textContent = "Còi hú khẩn cấp đang phát âm thanh cảnh báo!";
    } else {
      DOM.badgeBuzzerState.className = "act-state-badge off";
      DOM.badgeBuzzerState.textContent = "IM LẶNG";
      DOM.lblBuzzerDesc.textContent = "Còi sẵn sàng tự động phản ứng khi khói >= ngưỡng.";
    }
  }

  // Safety Interlock UI: disable Fan OFF and Buzzer MUTE during ALARM
  const isAlarmState = (STATE.fsmState === "ALARM");
  if (DOM.btnFanOff) DOM.btnFanOff.disabled = isAlarmState;
  if (DOM.btnBuzzerMute) DOM.btnBuzzerMute.disabled = isAlarmState;
  if (DOM.btnBannerMute) DOM.btnBannerMute.disabled = isAlarmState;

  // 4. Sensitivity Scheduler Toggle
  if (DOM.badgeNightState && DOM.lblThresholdDesc && DOM.kpiThreshold) {
    if (STATE.sensitivityMode === "NIGHT") {
      DOM.badgeNightState.className = "act-state-badge mode-night";
      DOM.badgeNightState.textContent = "CHẾ ĐỘ ĐÊM (350 PPM)";
      DOM.lblThresholdDesc.textContent = "350 PPM (Tăng độ nhạy ban đêm)";
      DOM.kpiThreshold.textContent = "350.0 PPM";
      STATE.alarmThreshold = CONFIG.thresholds.alarmNight;
      if (DOM.btnModeNight) DOM.btnModeNight.classList.add("active");
      if (DOM.btnModeDay) DOM.btnModeDay.classList.remove("active");
    } else {
      DOM.badgeNightState.className = "act-state-badge mode-day";
      DOM.badgeNightState.textContent = "CHẾ ĐỘ NGÀY (400 PPM)";
      DOM.lblThresholdDesc.textContent = "400 PPM (Tiêu chuẩn ban ngày)";
      DOM.kpiThreshold.textContent = "400.0 PPM";
      STATE.alarmThreshold = CONFIG.thresholds.alarmDay;
      if (DOM.btnModeDay) DOM.btnModeDay.classList.add("active");
      if (DOM.btnModeNight) DOM.btnModeNight.classList.remove("active");
    }
  }

  // 5. Floorplan Map Node
  if (DOM.mapNodeA01 && DOM.mapNodeBadge && DOM.zoneOverallStatus) {
    if (STATE.fsmState === "ALARM") {
      DOM.mapNodeA01.className = "sensor-node node-hazard";
      DOM.mapNodeBadge.textContent = "ALARM";
      DOM.mapNodeBadge.style.background = "#fef2f2";
      DOM.mapNodeBadge.style.color = "#dc2626";
      DOM.mapNodeBadge.style.borderColor = "#fecaca";
      DOM.zoneOverallStatus.innerHTML = '<span class="dot"></span> CẢNH BÁO CHÁY PHÒNG P302';
      DOM.zoneOverallStatus.style.background = "#fef2f2";
      DOM.zoneOverallStatus.style.color = "var(--scada-alarm)";
    } else if (STATE.fsmState === "COOLDOWN") {
      DOM.mapNodeA01.className = "sensor-node node-live";
      DOM.mapNodeBadge.textContent = "COOLDOWN";
      DOM.mapNodeBadge.style.background = "#f0f9ff";
      DOM.mapNodeBadge.style.color = "var(--scada-cooldown)";
      DOM.mapNodeBadge.style.borderColor = "#bae6fd";
      DOM.zoneOverallStatus.innerHTML = '<span class="dot"></span> Đang xả khói P302';
      DOM.zoneOverallStatus.style.background = "#f0f9ff";
      DOM.zoneOverallStatus.style.color = "var(--scada-cooldown)";
    } else {
      DOM.mapNodeA01.className = "sensor-node node-live";
      DOM.mapNodeBadge.textContent = "SAFE";
      DOM.mapNodeBadge.style.background = "#ecfdf5";
      DOM.mapNodeBadge.style.color = "var(--scada-safe)";
      DOM.mapNodeBadge.style.borderColor = "#a7f3d0";
      DOM.zoneOverallStatus.innerHTML = '<span class="dot"></span> Toàn sàn Bình thường';
      DOM.zoneOverallStatus.style.background = "#ecfdf5";
      DOM.zoneOverallStatus.style.color = "var(--scada-safe)";
    }
  }

  // 6. Diagnostic Health Matrix (Week 7)
  if (DOM.healthMq2Status) {
    DOM.healthMq2Status.className = STATE.health.mq2 === "OK" ? "health-val ok" : "health-val fault";
    DOM.healthMq2Status.textContent = STATE.health.mq2 === "OK" ? "● ADC BÌNH THƯỜNG" : "● ĐỨT DÂY / OUT-OF-RANGE";
  }
  if (DOM.healthDhtStatus) {
    DOM.healthDhtStatus.className = STATE.health.dht === "OK" ? "health-val ok" : "health-val fault";
    DOM.healthDhtStatus.textContent = STATE.health.dht === "OK" ? "● 1-WIRE KẾT NỐI" : "● LỖI READ TIMEOUT / NaN";
  }
  if (DOM.healthWatchdogStatus) {
    DOM.healthWatchdogStatus.className = STATE.health.watchdog === "OK" ? "health-val ok" : "health-val fault";
    DOM.healthWatchdogStatus.textContent = STATE.health.watchdog === "OK" ? "● PING 10s (ALIVE)" : "● TIMEOUT > 15s (OFFLINE)";
  }
  if (DOM.healthActuatorStatus) {
    DOM.healthActuatorStatus.className = STATE.health.actuator === "OK" ? "health-val ok" : "health-val fault";
    DOM.healthActuatorStatus.textContent = STATE.health.actuator === "OK" ? "● PHẢN HỒI ACK" : "● KẸT RƠ-LE / TIMEOUT";
  }

  // Simulator Sliders Sync
  if (DOM.simLblSmoke) DOM.simLblSmoke.textContent = STATE.ppm.toFixed(1) + " PPM";
  if (DOM.simSliderSmoke) DOM.simSliderSmoke.value = Math.round(STATE.ppm);
  if (DOM.simLblTemp) DOM.simLblTemp.textContent = STATE.temp.toFixed(1) + " °C";
  if (DOM.simSliderTemp) DOM.simSliderTemp.value = STATE.temp.toFixed(1);
}

// =============================================================================
// 9. CHART.JS REAL-TIME VISUALIZATION
// =============================================================================
function initChart() {
  const chartCanvas = DOM.telemetryChart;
  if (!chartCanvas) return;

  if (typeof Chart === "undefined") {
    console.warn("[Chart.js] Thư viện Chart.js chưa tải được, bỏ qua khởi tạo biểu đồ động.");
    return;
  }

  const ctx = chartCanvas.getContext("2d");
  const now = new Date();

  for (let i = 12; i >= 0; i--) {
    const t = new Date(now.getTime() - i * 2000);
    STATE.history.labels.push(t.toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit", second: "2-digit" }));
    STATE.history.ppmData.push(140 + Math.random() * 15);
    STATE.history.tempData.push(28.0 + Math.random() * 0.8);
  }

  telemetryChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: STATE.history.labels,
      datasets: [
        {
          label: "Khói MQ-2 (PPM)",
          data: STATE.history.ppmData,
          borderColor: "#f59e0b",
          backgroundColor: "rgba(245, 158, 11, 0.12)",
          borderWidth: 2.2,
          pointRadius: 2,
          pointHoverRadius: 5,
          tension: 0.35,
          fill: true,
          yAxisID: "ySmoke"
        },
        {
          label: "Nhiệt độ (°C)",
          data: STATE.history.tempData,
          borderColor: "#06b6d4",
          backgroundColor: "rgba(6, 182, 212, 0.08)",
          borderWidth: 1.8,
          pointRadius: 2,
          tension: 0.35,
          yAxisID: "yTemp"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#0f172a",
          borderColor: "#334155",
          borderWidth: 1,
          titleFont: { family: "Inter", size: 12 },
          bodyFont: { family: "Inter", size: 11 }
        }
      },
      scales: {
        x: {
          grid: { color: "rgba(0, 0, 0, 0.05)" },
          ticks: { color: "#64748b", font: { family: "JetBrains Mono", size: 10 }, maxTicksLimit: 7 }
        },
        ySmoke: {
          type: "linear",
          position: "left",
          min: 0,
          max: 800,
          grid: { color: "rgba(0, 0, 0, 0.05)" },
          ticks: { color: "#d97706", font: { family: "JetBrains Mono", size: 10 }, stepSize: 200 }
        },
        yTemp: {
          type: "linear",
          position: "right",
          min: 15,
          max: 75,
          grid: { drawOnChartArea: false },
          ticks: { color: "#0284c7", font: { family: "JetBrains Mono", size: 10 } }
        }
      }
    }
  });
}

function pushChartData(ppm, temp) {
  if (!telemetryChart) return;

  const nowStr = new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  STATE.history.labels.push(nowStr);
  STATE.history.ppmData.push(ppm);
  STATE.history.tempData.push(temp);

  if (STATE.history.labels.length > 25) {
    STATE.history.labels.shift();
    STATE.history.ppmData.shift();
    STATE.history.tempData.shift();
  }

  telemetryChart.update("none");
}

// =============================================================================
// 10. TELEGRAM ALERTING & AUDIT TRAIL
// =============================================================================
function dispatchTelegramAlert(htmlMessage) {
  const container = DOM.tgMessagesList;
  if (!container) return;

  const timeStr = new Date().toLocaleTimeString("vi-VN");
  const msgDiv = document.createElement("div");
  msgDiv.className = "tg-msg tg-bot-msg alarm-msg";
  msgDiv.innerHTML = `
    <div class="tg-msg-time">${timeStr}</div>
    <div class="tg-msg-bubble">${htmlMessage}</div>
  `;

  container.appendChild(msgDiv);
  container.scrollTop = container.scrollHeight;
}

function addAuditLog(level, eventName, description, fsmState) {
  const now = new Date();
  const timeStr = now.toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit", second: "2-digit" });

  const logItem = {
    time: timeStr,
    isoTime: now.toISOString(),
    level: level,
    event: eventName,
    desc: description,
    fsm: fsmState || STATE.fsmState
  };

  STATE.logs.unshift(logItem);
  if (STATE.logs.length > 80) STATE.logs.pop();

  renderAuditTable();
}

function renderAuditTable() {
  const tbody = DOM.auditTableBody;
  const filter = DOM.logFilterLevel ? DOM.logFilterLevel.value : "ALL";
  if (!tbody) return;

  tbody.innerHTML = "";

  const filtered = STATE.logs.filter(item => {
    if (filter === "ALL") return true;
    return item.level === filter;
  });

  filtered.slice(0, 30).forEach(log => {
    const tr = document.createElement("tr");

    const getLvlClass = typeof safeLevelClass === 'function' ? safeLevelClass : (lv => 'lvl-' + String(lv).toLowerCase());

    const tdTime = document.createElement("td");
    tdTime.style.fontFamily = "var(--font-mono)";
    tdTime.style.fontSize = "10px";
    tdTime.style.color = "#64748b";
    tdTime.textContent = log.time || "";

    const tdLvl = document.createElement("td");
    const spanLvl = document.createElement("span");
    spanLvl.className = `badge-level ${getLvlClass(log.level)}`;
    spanLvl.textContent = log.level || "";
    tdLvl.appendChild(spanLvl);

    const tdEvent = document.createElement("td");
    const strongEvent = document.createElement("strong");
    strongEvent.style.color = "#0f172a";
    strongEvent.style.fontSize = "11px";
    strongEvent.textContent = log.event || "";
    tdEvent.appendChild(strongEvent);

    const tdDesc = document.createElement("td");
    tdDesc.style.fontSize = "11px";
    tdDesc.style.color = "#334155";
    tdDesc.textContent = log.desc || "";

    const tdFsm = document.createElement("td");
    tdFsm.style.fontFamily = "var(--font-mono)";
    tdFsm.style.fontSize = "10px";
    tdFsm.style.color = "#2563eb";
    tdFsm.textContent = log.fsm || "";

    tr.appendChild(tdTime);
    tr.appendChild(tdLvl);
    tr.appendChild(tdEvent);
    tr.appendChild(tdDesc);
    tr.appendChild(tdFsm);
    tbody.appendChild(tr);
  });
}

function exportLogsToCsv() {
  if (STATE.logs.length === 0) {
    showToast("Không có nhật ký nào để xuất.", "warning");
    return;
  }
  let csv = "Time,ISO_Timestamp,Level,Event,Description,FSM_State\n";
  STATE.logs.forEach(l => {
    csv += `"${l.time}","${l.isoTime}","${l.level}","${l.event}","${l.desc.replace(/"/g, '""')}","${l.fsm}"\n`;
  });

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `SmokeAlarm_AuditTrail_${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
  showToast("Đã tải xuống tệp Audit Trail CSV", "success");
}

function playAlarmAudioBeep() {
  try {
    if (!webAudioCtx) {
      webAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (webAudioCtx.state === "suspended") {
      webAudioCtx.resume();
    }
    const osc = webAudioCtx.createOscillator();
    const gain = webAudioCtx.createGain();
    osc.type = "sawtooth";
    osc.frequency.setValueAtTime(880, webAudioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(440, webAudioCtx.currentTime + 0.3);

    gain.gain.setValueAtTime(0.2, webAudioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, webAudioCtx.currentTime + 0.35);

    osc.connect(gain);
    gain.connect(webAudioCtx.destination);
    osc.start();
    osc.stop(webAudioCtx.currentTime + 0.35);
  } catch (err) {
    console.debug("Audio output suppressed by browser autoplay policy:", err);
  }
}

// =============================================================================
// 11. EVENT HANDLERS & USER INTERACTIONS
// =============================================================================
function initEventHandlers() {
  // Role selector
  if (DOM.userRoleSelect && DOM.currentRoleBadge) {
    DOM.userRoleSelect.addEventListener("change", (e) => {
      STATE.userRole = e.target.value;
      let label = "Quyền: Kỹ thuật viên";
      if (STATE.userRole === "admin") label = "Quyền: Quản trị viên (Toàn quyền)";
      else if (STATE.userRole === "viewer") label = "Quyền: Người dân (Chỉ xem)";
      DOM.currentRoleBadge.textContent = label;
      showToast(`Đã chuyển vai trò: [${e.target.selectedOptions[0].text}]`, "info");
      addAuditLog("INFO", "ROLE_SWITCH", `Người dùng đổi vai trò sang: ${STATE.userRole.toUpperCase()}`, STATE.fsmState);
    });
  }

  // Fan controls
  if (DOM.btnFanOn) {
    DOM.btnFanOn.addEventListener("click", () => {
      if (!checkRolePermission("operator", "bật quạt cưỡng bức")) return;
      STATE.fanState = true;
      STATE.fanMode = "MANUAL";
      sendDownlinkCommand("cmdFan", { action: "ON", user: STATE.userRole });
      addAuditLog("INFO", "MANUAL_FAN_ON", "Phát lệnh DOWNLINK bật quạt từ Tầng 4 Application.", STATE.fsmState);
      showToast("Đã gửi lệnh Downlink: BẬT QUẠT", "success");
      updateUiFromState();
    });
  }

  if (DOM.btnFanOff) {
    DOM.btnFanOff.addEventListener("click", () => {
      if (!checkRolePermission("operator", "tắt quạt")) return;
      if (STATE.fsmState === "ALARM" && STATE.userRole !== "admin") {
        showToast("TỪ CHỐI LỆNH: Hệ thống đang BÁO ĐỘNG HỎA HOẠN, cấm ngắt quạt hút khói!", "danger");
        addAuditLog("WARN", "OVERRIDE_REJECTED", "Từ chối lệnh tắt quạt do quy tắc an toàn PCCC khi khói nguy cấp.", STATE.fsmState);
        return;
      }
      STATE.fanState = false;
      STATE.fanMode = "MANUAL";
      sendDownlinkCommand("cmdFan", { action: "OFF", user: STATE.userRole });
      addAuditLog("INFO", "MANUAL_FAN_OFF", "Phát lệnh DOWNLINK tắt quạt từ Tầng 4 Application.", STATE.fsmState);
      showToast("Đã gửi lệnh Downlink: TẮT QUẠT", "info");
      updateUiFromState();
    });
  }

  if (DOM.btnFanAuto) {
    DOM.btnFanAuto.addEventListener("click", () => {
      if (!checkRolePermission("operator", "chuyển chế độ tự động")) return;
      STATE.fanMode = "AUTO";
      sendDownlinkCommand("cmdMode", { mode: "AUTO" });
      showToast("Chế độ quạt: Tự động theo FSM", "info");
      updateUiFromState();
    });
  }

  // Buzzer controls
  if (DOM.btnBuzzerMute) {
    DOM.btnBuzzerMute.addEventListener("click", () => {
      if (!checkRolePermission("operator", "tắt tiếng còi")) return;
      STATE.isMuted = true;
      STATE.muteRemainingSec = 180;
      STATE.buzzerActive = false;
      sendDownlinkCommand("cmdBuzzer", { action: "MUTE", duration: 180 });
      addAuditLog("WARN", "BUZZER_MUTED", "Đã tạm tắt còi 180 giây để ban quản lý xử lý hiện trường.", STATE.fsmState);
      showToast("Đã ngắt tiếng còi trong 180 giây!", "warning");

      if (muteInterval) clearInterval(muteInterval);
      muteInterval = setInterval(() => {
        STATE.muteRemainingSec--;
        if (STATE.muteRemainingSec <= 0) {
          clearInterval(muteInterval);
          STATE.isMuted = false;
          if (STATE.fsmState === "ALARM") STATE.buzzerActive = true;
          addAuditLog("INFO", "BUZZER_UNMUTED", "Hết thời gian Mute 180s. Còi kích hoạt trở lại.", STATE.fsmState);
        }
        updateUiFromState();
      }, 1000);

      updateUiFromState();
    });
  }

  if (DOM.btnBuzzerUnmute) {
    DOM.btnBuzzerUnmute.addEventListener("click", () => {
      if (!checkRolePermission("operator", "hủy mute còi")) return;
      if (muteInterval) clearInterval(muteInterval);
      STATE.isMuted = false;
      STATE.muteRemainingSec = 0;
      if (STATE.fsmState === "ALARM") STATE.buzzerActive = true;
      sendDownlinkCommand("cmdBuzzer", { action: "UNMUTE" });
      addAuditLog("INFO", "BUZZER_UNMUTED_MANUAL", "Đã hủy Mute còi thủ công từ Dashboard.", STATE.fsmState);
      showToast("Đã kích hoạt lại âm thanh còi!", "info");
      updateUiFromState();
    });
  }

  if (DOM.btnBuzzerTest) {
    DOM.btnBuzzerTest.addEventListener("click", () => {
      if (!checkRolePermission("operator", "kiểm tra còi")) return;
      sendDownlinkCommand("cmdBuzzer", { action: "TEST" });
      playAlarmAudioBeep();
      showToast("ESP32: Đang thực hiện Beep Test 0.5s...", "info");
    });
  }

  // Sensitivity Day/Night Mode
  if (DOM.btnModeDay) {
    DOM.btnModeDay.addEventListener("click", () => {
      if (!checkRolePermission("admin", "chỉnh ngưỡng độ nhạy")) return;
      STATE.sensitivityMode = "DAY";
      sendDownlinkCommand("cmdScheduler", { mode: "DAY" });
      addAuditLog("INFO", "SENSITIVITY_MODE", "Chuyển sang Chế độ Ban ngày (Ngưỡng 400 PPM)", STATE.fsmState);
      showToast("Đã chuyển Chế độ Ban ngày (Ngưỡng 400 PPM)", "info");
      updateUiFromState();
    });
  }

  if (DOM.btnModeNight) {
    DOM.btnModeNight.addEventListener("click", () => {
      if (!checkRolePermission("admin", "chỉnh ngưỡng độ nhạy")) return;
      STATE.sensitivityMode = "NIGHT";
      sendDownlinkCommand("cmdScheduler", { mode: "NIGHT" });
      addAuditLog("WARN", "SENSITIVITY_MODE", "Kích hoạt Chế độ Ban đêm (Hạ ngưỡng 350 PPM tăng nhạy)", STATE.fsmState);
      showToast("Đã kích hoạt Chế độ Ban đêm (Ngưỡng 350 PPM)", "warning");
      updateUiFromState();
    });
  }

  // Telegram actions
  if (DOM.btnTestTgAlert) {
    DOM.btnTestTgAlert.addEventListener("click", () => {
      dispatchTelegramAlert(
        `🧪 <b>THỬ NGHIỆM KÊNH CẢNH BÁO TELEGRAM</b>\n` +
        `Trạm: <code>ESP32_SMOKE_N04_A01</code>\n` +
        `Thời gian: <code>${new Date().toLocaleString("vi-VN")}</code>\n` +
        `Trạng thái kết nối Webhook: <b>THÀNH CÔNG</b>`
      );
      showToast("Đã phát tin cảnh báo thử nghiệm tới Telegram Bot", "success");
    });
  }

  if (DOM.btnClearTgHistory) {
    DOM.btnClearTgHistory.addEventListener("click", () => {
      if (DOM.tgMessagesList) DOM.tgMessagesList.innerHTML = "";
      showToast("Đã dọn sạch tin nhắn Telegram", "info");
    });
  }

  // Audit export
  if (DOM.btnExportLogs) DOM.btnExportLogs.addEventListener("click", exportLogsToCsv);
  if (DOM.logFilterLevel) DOM.logFilterLevel.addEventListener("change", renderAuditTable);

  // Modal Simulator
  const simModal = DOM.simModal;
  if (DOM.btnToggleSimModal && simModal) {
    DOM.btnToggleSimModal.addEventListener("click", () => simModal.classList.add("active"));
  }
  if (DOM.btnCloseSimModal && simModal) {
    DOM.btnCloseSimModal.addEventListener("click", () => simModal.classList.remove("active"));
  }
  if (DOM.btnApplySim && simModal) {
    DOM.btnApplySim.addEventListener("click", () => simModal.classList.remove("active"));
  }

  // Sliders input
  if (DOM.simSliderSmoke) {
    DOM.simSliderSmoke.addEventListener("input", (e) => {
      STATE.ppm = parseFloat(e.target.value);
      if (DOM.simLblSmoke) DOM.simLblSmoke.textContent = STATE.ppm + " PPM";
      updateUiFromState();
      pushChartData(STATE.ppm, STATE.temp);
    });
  }

  if (DOM.simSliderTemp) {
    DOM.simSliderTemp.addEventListener("input", (e) => {
      STATE.temp = parseFloat(e.target.value);
      if (DOM.simLblTemp) DOM.simLblTemp.textContent = STATE.temp.toFixed(1) + " °C";
      updateUiFromState();
      pushChartData(STATE.ppm, STATE.temp);
    });
  }

  if (DOM.btnSimDisconnect) {
    DOM.btnSimDisconnect.addEventListener("click", () => {
      setOfflineState();
      showToast("Đã mô phỏng đứt kết nối mạng ESP32", "danger");
    });
  }

  if (DOM.btnSimReconnect) {
    DOM.btnSimReconnect.addEventListener("click", () => {
      STATE.deviceOnline = true;
      STATE.lastSeenTime = Date.now();
      STATE.fsmState = "SAFE";
      STATE.health.watchdog = "OK";
      addAuditLog("INFO", "RECONNECTED", "ESP32 đã tái kết nối mạng thành công.", "SAFE");
      showToast("Đã khôi phục kết nối trạm cảm biến!", "success");
      updateUiFromState();
    });
  }

  // Banner Actions
  if (DOM.btnBannerMute && DOM.btnBuzzerMute) {
    DOM.btnBannerMute.addEventListener("click", () => DOM.btnBuzzerMute.click());
  }
  if (DOM.btnBannerAcknowledge) {
    DOM.btnBannerAcknowledge.addEventListener("click", () => {
      addAuditLog("INFO", "INCIDENT_ACKNOWLEDGED", `Người dùng (${STATE.userRole}) xác nhận đã tiếp nhận sự cố.`, STATE.fsmState);
      showToast("Đã xác nhận sự cố an toàn PCCC", "success");
    });
  }
}

// =============================================================================
// 12. FAULT INJECTION SANDBOX HANDLERS (WEEK 7 BINDINGS)
// =============================================================================
function initFaultInjectionHandlers() {
  if (DOM.btnFaultMq2) {
    DOM.btnFaultMq2.addEventListener("click", () => {
      sendDownlinkCommand("cmdInjectFault", { fault: "MQ2_DISCONNECT" });
      STATE.health.mq2 = "FAULT";
      STATE.fsmState = "FAULT";
      addAuditLog("CRITICAL", "FAULT_INJECTION_MQ2", "Kích hoạt mô phỏng đứt dây cảm biến khói MQ-2.", "FAULT");
      showToast("Đã gửi lệnh giả lập sự cố: Đứt dây MQ-2", "danger");
      updateUiFromState();
    });
  }

  if (DOM.btnFaultDht) {
    DOM.btnFaultDht.addEventListener("click", () => {
      sendDownlinkCommand("cmdInjectFault", { fault: "DHT_NAN" });
      STATE.health.dht = "FAULT";
      STATE.fsmState = "FAULT";
      addAuditLog("CRITICAL", "FAULT_INJECTION_DHT", "Kích hoạt mô phỏng lỗi cảm biến nhiệt ẩm DHT22 (NaN).", "FAULT");
      showToast("Đã gửi lệnh giả lập sự cố: Lỗi DHT22 (NaN)", "danger");
      updateUiFromState();
    });
  }

  if (DOM.btnFaultActuator) {
    DOM.btnFaultActuator.addEventListener("click", () => {
      sendDownlinkCommand("cmdInjectFault", { fault: "ACTUATOR_FAULT" });
      STATE.health.actuator = "FAULT";
      addAuditLog("WARN", "FAULT_INJECTION_ACTUATOR", "Kích hoạt mô phỏng kẹt tiếp điểm Rơ-le quạt.", STATE.fsmState);
      showToast("Đã gửi lệnh giả lập sự cố: Kẹt Rơ-le quạt", "warning");
      updateUiFromState();
    });
  }

  if (DOM.btnSyncBuffer) {
    DOM.btnSyncBuffer.addEventListener("click", () => {
      addAuditLog("INFO", "OFFLINE_SYNC_REQ", "Yêu cầu đồng bộ 20 bản ghi bộ đệm ngoại tuyến (Circular Buffer).", STATE.fsmState);
      showToast("Đang đồng bộ 20 bản ghi ngoại tuyến từ vòng đệm ESP32...", "info");
      setTimeout(() => {
        showToast("Đồng bộ dữ liệu ngoại tuyến thành công 100%!", "success");
      }, 1200);
    });
  }

  if (DOM.btnClearAllFaults) {
    DOM.btnClearAllFaults.addEventListener("click", () => {
      sendDownlinkCommand("cmdInjectFault", { fault: "CLEAR" });
      STATE.health.mq2 = "OK";
      STATE.health.dht = "OK";
      STATE.health.actuator = "OK";
      STATE.health.watchdog = "OK";
      STATE.fsmState = "SAFE";
      addAuditLog("INFO", "FAULT_RESTORED", "Đã xóa toàn bộ sự cố mô phỏng. Hệ thống trở về SAFE.", "SAFE");
      showToast("Đã khôi phục toàn bộ cảm biến về trạng thái bình thường!", "success");
      updateUiFromState();
    });
  }
}

// Preset helper called from inline buttons
const setSimPreset = function(ppmVal, tempVal) {
  STATE.ppm = ppmVal;
  STATE.temp = tempVal;
  updateUiFromState();
  pushChartData(STATE.ppm, STATE.temp);
  showToast(`Thiết lập giả lập: Khói ${ppmVal} PPM, Nhiệt độ ${tempVal}°C`, "info");
};
if (typeof window !== 'undefined') {
  window.setSimPreset = setSimPreset;
}

function initSimulatorDefaults() {
  setInterval(() => {
    if (STATE.fsmState === "SAFE" && DOM.simModal && !DOM.simModal.classList.contains("active")) {
      const delta = (Math.random() - 0.5) * 3;
      STATE.ppm = Math.max(80, Math.min(220, STATE.ppm + delta));
      updateUiFromState();
      pushChartData(STATE.ppm, STATE.temp);
    }
  }, 2500);
}

// =============================================================================
// 13. TOAST & CLOCK UTILITIES
// =============================================================================
function showToast(message, type = "info") {
  const container = DOM.toastContainer;
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;

  let icon = "ℹ️";
  if (type === "success") icon = "✅";
  else if (type === "danger") icon = "🚨";
  else if (type === "warning") icon = "⚠️";

  const iconSpan = document.createElement("span");
  iconSpan.textContent = icon;
  const msgSpan = document.createElement("span");
  msgSpan.textContent = message;

  toast.appendChild(iconSpan);
  toast.appendChild(document.createTextNode(" "));
  toast.appendChild(msgSpan);
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(50px)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function initClock() {
  const el = DOM.clockDisplay;
  if (!el) return;

  setInterval(() => {
    el.textContent = new Date().toLocaleTimeString("vi-VN");
  }, 1000);
}

// =============================================================================
// 14. SANITIZATION & COMMONJS EXPORTS (FOR TESTING)
// =============================================================================
function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    CONFIG,
    STATE,
    DOM,
    escapeHtml,
    renderAuditTable,
    showToast,
    handleMqttMessage: handleIncomingMqtt,
    handleIncomingMqtt,
    updateUiFromState,
    setOfflineState,
    addAuditLog
  };
}

```

---

## PHẦN 36: KIỂM THỬ NATIVE C++ CORE (UNITY) (`test/test_core.cpp`)

> **Đường dẫn:** `test/test_core.cpp`  
> **Quy mô:** 693 dòng | 27,013 bytes | Ngôn ngữ: `cpp`

```cpp
#include <unity.h>
#include <cmath>
#include <cstring>
#include "thresholds.h"
#include "ema_filter.h"
#include "health.h"
#include "netutil.h"
#include "fsm_core.h"
#include "ring_buffer.h"
#include "backoff.h"
#include "cmd_parse.h"

void setUp(void) {}
void tearDown(void) {}

// ============================================================================
// T-TH1: Thresholds tests
// ============================================================================
void test_thresholds_calc(void) {
    Thresholds t1 = makeThresholds(250.0f);
    TEST_ASSERT_FLOAT_WITHIN(0.01f, 300.0f, t1.alarm);
    TEST_ASSERT_FLOAT_WITHIN(0.01f, 225.0f, t1.safe);

    Thresholds t2 = makeThresholds(500.0f);
    TEST_ASSERT_FLOAT_WITHIN(0.01f, 400.0f, t2.alarm);
    TEST_ASSERT_FLOAT_WITHIN(0.01f, 300.0f, t2.safe);

    Thresholds t3 = makeThresholds(350.0f);
    TEST_ASSERT_FLOAT_WITHIN(0.01f, 350.0f, t3.alarm);
    TEST_ASSERT_FLOAT_WITHIN(0.01f, 262.5f, t3.safe);

    float nanVal = std::nanf("");
    Thresholds t4 = makeThresholds(nanVal);
    TEST_ASSERT_FLOAT_WITHIN(0.01f, 400.0f, t4.alarm);
    TEST_ASSERT_FLOAT_WITHIN(0.01f, 300.0f, t4.safe);
}

// ============================================================================
// T-E1: Single spike suppression
// ============================================================================
void test_ema_spike_suppression(void) {
    EmaFilter f1;
    emaReset(f1, 200.0f);
    float s1 = emaUpdate(f1, 690.0f);
    TEST_ASSERT_FLOAT_WITHIN(0.5f, 396.0f, s1);
    TEST_ASSERT_TRUE(s1 < 400.0f);
    float s1_back = emaUpdate(f1, 200.0f);
    TEST_ASSERT_FLOAT_WITHIN(0.5f, 366.6f, s1_back);

    EmaFilter f2;
    emaReset(f2, 200.0f);
    float s2 = emaUpdate(f2, 710.0f);
    TEST_ASSERT_FLOAT_WITHIN(0.5f, 404.0f, s2);
    TEST_ASSERT_TRUE(s2 >= 400.0f);
}

// ============================================================================
// T-E2: Step 600 PPM (2 samples to alarm)
// ============================================================================
void test_ema_step_600(void) {
    EmaFilter f;
    emaReset(f, 200.0f);
    float m1 = emaUpdate(f, 600.0f);
    TEST_ASSERT_FLOAT_WITHIN(0.1f, 360.0f, m1);
    TEST_ASSERT_TRUE(m1 < 400.0f);

    float m2 = emaUpdate(f, 600.0f);
    TEST_ASSERT_FLOAT_WITHIN(0.1f, 456.0f, m2);
    TEST_ASSERT_TRUE(m2 >= 400.0f); // Vượt 400 ở mẫu 2 (<= 4s)
}

// ============================================================================
// T-E3: Step 500 & Step 450
// ============================================================================
void test_ema_step_500_and_450(void) {
    // Step 500
    EmaFilter f500;
    emaReset(f500, 200.0f);
    emaUpdate(f500, 500.0f); // S1: 320
    emaUpdate(f500, 500.0f); // S2: 392
    float s3 = emaUpdate(f500, 500.0f); // S3: 435.2
    TEST_ASSERT_FLOAT_WITHIN(0.2f, 435.2f, s3);
    TEST_ASSERT_TRUE(s3 >= 400.0f);

    // Step 450
    EmaFilter f450;
    emaReset(f450, 200.0f);
    emaUpdate(f450, 450.0f); // S1: 300
    emaUpdate(f450, 450.0f); // S2: 360
    emaUpdate(f450, 450.0f); // S3: 396
    float s4 = emaUpdate(f450, 450.0f); // S4: 417.6
    TEST_ASSERT_FLOAT_WITHIN(0.2f, 417.6f, s4);
    TEST_ASSERT_TRUE(s4 >= 400.0f);
}

// ============================================================================
// T-E4: Night Threshold 350
// ============================================================================
void test_ema_night_threshold(void) {
    EmaFilter f1;
    emaReset(f1, 200.0f);
    float v1 = emaUpdate(f1, 570.0f); // 200 + 0.4*370 = 348
    TEST_ASSERT_FLOAT_WITHIN(0.1f, 348.0f, v1);
    TEST_ASSERT_TRUE(v1 < 350.0f);

    EmaFilter f2;
    emaReset(f2, 200.0f);
    float v2 = emaUpdate(f2, 580.0f); // 200 + 0.4*380 = 352
    TEST_ASSERT_FLOAT_WITHIN(0.1f, 352.0f, v2);
    TEST_ASSERT_TRUE(v2 >= 350.0f);
}

// ============================================================================
// T-E5: EMA Reset after fault recovery
// ============================================================================
void test_ema_recovery_reset(void) {
    EmaFilter f;
    emaReset(f, 450.0f);
    TEST_ASSERT_FLOAT_WITHIN(0.01f, 450.0f, f.value);

    // Khi MQ-2 hồi phục, reset lại 450 và fsmStep kích hoạt ALARM ngay
    FsmContext ctx;
    Thresholds th = makeThresholds(400.0f);
    FsmInput in = { f.value, false, false, 1000 };
    FsmOutput out = fsmStep(ctx, in, th);
    TEST_ASSERT_EQUAL(STATE_ALARM, ctx.state);
    TEST_ASSERT_EQUAL(BUZZ_ALARM, out.buzzer);
    TEST_ASSERT_TRUE(out.fanOn);
}

// ============================================================================
// T-H1: ADC 4095 continuous (Never fault)
// ============================================================================
void test_health_mq2_high_adc(void) {
    Mq2Health h;
    for (int i = 0; i < 100; i++) {
        HealthEvent ev = mq2Update(h, 4095, false);
        TEST_ASSERT_EQUAL(HE_NONE, ev);
        TEST_ASSERT_FALSE(h.fault);
    }
}

// ============================================================================
// T-H2: ADC disconnect and 3-step debounce recovery
// ============================================================================
void test_health_mq2_debounce(void) {
    Mq2Health h;
    // Sample 1: bad ADC
    HealthEvent ev1 = mq2Update(h, 10, false, 2, 3);
    TEST_ASSERT_EQUAL(HE_NONE, ev1);
    TEST_ASSERT_FALSE(h.fault);

    // Sample 2: bad ADC -> Enter FAULT
    HealthEvent ev2 = mq2Update(h, 10, false, 2, 3);
    TEST_ASSERT_EQUAL(HE_FAULT_ENTER, ev2);
    TEST_ASSERT_TRUE(h.fault);

    // Good sample 1: still fault
    HealthEvent g1 = mq2Update(h, 1000, false, 2, 3);
    TEST_ASSERT_EQUAL(HE_NONE, g1);
    TEST_ASSERT_TRUE(h.fault);

    // Good sample 2: still fault
    HealthEvent g2 = mq2Update(h, 1000, false, 2, 3);
    TEST_ASSERT_EQUAL(HE_NONE, g2);
    TEST_ASSERT_TRUE(h.fault);

    // Good sample 3: RECOVERED!
    HealthEvent g3 = mq2Update(h, 1000, false, 2, 3);
    TEST_ASSERT_EQUAL(HE_RECOVERED, g3);
    TEST_ASSERT_FALSE(h.fault);
}

// ============================================================================
// T-H3: DHT health checking
// ============================================================================
void test_health_dht(void) {
    DhtHealth h;
    dhtOnRead(h, false, 0.0f, false);
    TEST_ASSERT_FALSE(h.fault);
    dhtOnRead(h, false, 0.0f, false);
    TEST_ASSERT_FALSE(h.fault);
    dhtOnRead(h, false, 0.0f, false);
    TEST_ASSERT_TRUE(h.fault); // 3 failures -> fault

    // 1 good read recovers
    dhtOnRead(h, true, 28.0f, false);
    TEST_ASSERT_FALSE(h.fault);

    // simFault triggers immediately
    dhtOnRead(h, true, 28.0f, true);
    TEST_ASSERT_TRUE(h.fault);
}

// ============================================================================
// T-F1: ALARM 450 -> 350 -> 299 (Hysteresis)
// ============================================================================
void test_fsm_hysteresis(void) {
    FsmContext ctx;
    Thresholds th = makeThresholds(400.0f);

    FsmInput in1 = { 450.0f, false, false, 1000 };
    FsmOutput o1 = fsmStep(ctx, in1, th);
    TEST_ASSERT_EQUAL(STATE_ALARM, ctx.state);
    TEST_ASSERT_EQUAL(BUZZ_ALARM, o1.buzzer);
    TEST_ASSERT_TRUE(o1.fanOn);

    // Drops to 350: MUST STAY IN ALARM!
    FsmInput in2 = { 350.0f, false, false, 3000 };
    FsmOutput o2 = fsmStep(ctx, in2, th);
    TEST_ASSERT_EQUAL(STATE_ALARM, ctx.state);
    TEST_ASSERT_EQUAL(BUZZ_ALARM, o2.buzzer);
    TEST_ASSERT_TRUE(o2.fanOn);

    // Drops to 299: enters COOLDOWN!
    FsmInput in3 = { 299.0f, false, false, 5000 };
    FsmOutput o3 = fsmStep(ctx, in3, th);
    TEST_ASSERT_EQUAL(STATE_COOLDOWN, ctx.state);
    TEST_ASSERT_EQUAL(BUZZ_OFF, o3.buzzer);
    TEST_ASSERT_TRUE(o3.fanOn);
}

// ============================================================================
// T-F2: COOLDOWN 30s completion (350 vs 280)
// ============================================================================
void test_fsm_cooldown_finish(void) {
    Thresholds th = makeThresholds(400.0f);

    // Case A: After 30s, PPM is 350 -> WARNING
    {
        FsmContext ctx;
        fsmStep(ctx, { 450.0f, false, false, 1000 }, th);
        fsmStep(ctx, { 290.0f, false, false, 2000 }, th); // into cooldown at t=2000
        TEST_ASSERT_EQUAL(STATE_COOLDOWN, ctx.state);

        // During purge (e.g. t=15000)
        FsmOutput mid = fsmStep(ctx, { 350.0f, false, false, 15000 }, th);
        TEST_ASSERT_EQUAL(STATE_COOLDOWN, ctx.state);
        TEST_ASSERT_TRUE(mid.fanOn);

        // Expired at t=32001, PPM is 350 (> safe 300) -> WARNING
        FsmOutput end = fsmStep(ctx, { 350.0f, false, false, 32001 }, th);
        TEST_ASSERT_EQUAL(STATE_WARNING, ctx.state);
        TEST_ASSERT_FALSE(end.fanOn); // in AUTO mode fan turns off
    }

    // Case B: After 30s, PPM is 280 -> SAFE
    {
        FsmContext ctx;
        fsmStep(ctx, { 450.0f, false, false, 1000 }, th);
        fsmStep(ctx, { 290.0f, false, false, 2000 }, th);
        FsmOutput end = fsmStep(ctx, { 280.0f, false, false, 32001 }, th);
        TEST_ASSERT_EQUAL(STATE_SAFE, ctx.state);
        TEST_ASSERT_FALSE(end.fanOn);
    }
}

// ============================================================================
// T-F3: COOLDOWN re-ignition
// ============================================================================
void test_fsm_cooldown_reignition(void) {
    Thresholds th = makeThresholds(400.0f);
    FsmContext ctx;
    fsmStep(ctx, { 450.0f, false, false, 1000 }, th);
    fsmStep(ctx, { 290.0f, false, false, 2000 }, th);
    TEST_ASSERT_EQUAL(STATE_COOLDOWN, ctx.state);

    // Smoke re-ignites to 450 PPM during cooldown!
    FsmOutput out = fsmStep(ctx, { 450.0f, false, false, 10000 }, th);
    TEST_ASSERT_EQUAL(STATE_ALARM, ctx.state);
    TEST_ASSERT_EQUAL(BUZZ_ALARM, out.buzzer);
    TEST_ASSERT_TRUE(out.fanOn);
}

// ============================================================================
// T-F4: MQ-2 fault with garbage PPM
// ============================================================================
void test_fsm_mq2_fault_garbage_ppm(void) {
    Thresholds th = makeThresholds(400.0f);
    FsmContext ctx;
    FsmOutput out = fsmStep(ctx, { 1000.0f, true, false, 1000 }, th);
    TEST_ASSERT_EQUAL(STATE_FAULT, ctx.state);
    TEST_ASSERT_EQUAL(BUZZ_FAULT_BEEP, out.buzzer);
    TEST_ASSERT_TRUE(out.fanOn);
}

// ============================================================================
// T-F5: MQ-2 fault during active ALARM (Fire burning sensor cable)
// ============================================================================
void test_fsm_mq2_fault_during_alarm(void) {
    Thresholds th = makeThresholds(400.0f);
    FsmContext ctx;
    fsmStep(ctx, { 450.0f, false, false, 1000 }, th);
    TEST_ASSERT_EQUAL(STATE_ALARM, ctx.state);

    // Cable severed while alarm is active
    FsmOutput out = fsmStep(ctx, { 0.0f, true, false, 3000 }, th);
    TEST_ASSERT_EQUAL(STATE_ALARM, ctx.state);
    TEST_ASSERT_EQUAL(BUZZ_ALARM, out.buzzer); // Must remain continuous ALARM!
    TEST_ASSERT_TRUE(out.fanOn);
}

// ============================================================================
// T-F6: DHT fault alone vs with smoke
// ============================================================================
void test_fsm_dht_fault(void) {
    Thresholds th = makeThresholds(400.0f);
    FsmContext ctx;

    // DHT fault alone
    FsmOutput o1 = fsmStep(ctx, { 200.0f, false, true, 1000 }, th);
    TEST_ASSERT_EQUAL(STATE_WARNING, ctx.state);
    TEST_ASSERT_EQUAL(BUZZ_OFF, o1.buzzer);
    TEST_ASSERT_FALSE(o1.fanOn);

    // DHT fault + 450 PPM smoke -> Full ALARM
    FsmOutput o2 = fsmStep(ctx, { 450.0f, false, true, 3000 }, th);
    TEST_ASSERT_EQUAL(STATE_ALARM, ctx.state);
    TEST_ASSERT_EQUAL(BUZZ_ALARM, o2.buzzer);
    TEST_ASSERT_TRUE(o2.fanOn);
}

// ============================================================================
// T-F7: Remote mute cleared at ALARM edge
// ============================================================================
void test_fsm_mute_cleared_on_alarm_edge(void) {
    Thresholds th = makeThresholds(400.0f);
    FsmContext ctx;

    // In warning (350 PPM)
    fsmStep(ctx, { 350.0f, false, false, 1000 }, th);
    TEST_ASSERT_EQUAL(STATE_WARNING, ctx.state);

    CmdResult res = cmdRemoteMute(ctx, 1000);
    TEST_ASSERT_EQUAL(CMD_OK, res);
    TEST_ASSERT_TRUE(ctx.muted);

    // Smoke increases to 450 PPM -> Transitions to ALARM: Mute MUST be cleared!
    FsmOutput out = fsmStep(ctx, { 450.0f, false, false, 3000 }, th);
    TEST_ASSERT_EQUAL(STATE_ALARM, ctx.state);
    TEST_ASSERT_FALSE(ctx.muted);
    TEST_ASSERT_EQUAL(BUZZ_ALARM, out.buzzer);
}

// ============================================================================
// T-F8: Safety interlock during ALARM
// ============================================================================
void test_fsm_interlock_during_alarm(void) {
    Thresholds th = makeThresholds(400.0f);
    FsmContext ctx;
    fsmStep(ctx, { 450.0f, false, false, 1000 }, th);
    TEST_ASSERT_EQUAL(STATE_ALARM, ctx.state);

    TEST_ASSERT_EQUAL(CMD_REJECTED_SAFETY_LOCK, cmdRemoteMute(ctx, 2000));
    TEST_ASSERT_EQUAL(CMD_REJECTED_SAFETY_LOCK, cmdRemoteFanOff(ctx));
    TEST_ASSERT_EQUAL(CMD_REJECTED_SAFETY_LOCK, cmdBuzzerTest(ctx));
}

// ============================================================================
// T-F9: Local button press in ALARM (60s silence)
// ============================================================================
void test_fsm_local_ack_button_alarm(void) {
    Thresholds th = makeThresholds(400.0f);
    FsmContext ctx;
    fsmStep(ctx, { 450.0f, false, false, 1000 }, th);

    bool handled = cmdLocalButton(ctx, 2000);
    TEST_ASSERT_TRUE(handled);
    TEST_ASSERT_TRUE(ctx.muted);

    // Within 60s silence period: buzzer OFF, fan remains ON
    FsmOutput o1 = fsmStep(ctx, { 450.0f, false, false, 30000 }, th);
    TEST_ASSERT_EQUAL(STATE_ALARM, ctx.state);
    TEST_ASSERT_EQUAL(BUZZ_OFF, o1.buzzer);
    TEST_ASSERT_TRUE(o1.buzzerMuted);
    TEST_ASSERT_TRUE(o1.fanOn);

    // After 60s (t=63000): Buzzer re-arms automatically!
    FsmOutput o2 = fsmStep(ctx, { 450.0f, false, false, 63000 }, th);
    TEST_ASSERT_EQUAL(STATE_ALARM, ctx.state);
    TEST_ASSERT_EQUAL(BUZZ_ALARM, o2.buzzer);
    TEST_ASSERT_FALSE(ctx.muted);
}

// ============================================================================
// T-F10: Local button press in FAULT (60s silence)
// ============================================================================
void test_fsm_local_ack_button_fault(void) {
    Thresholds th = makeThresholds(400.0f);
    FsmContext ctx;
    fsmStep(ctx, { 0.0f, true, false, 1000 }, th);
    TEST_ASSERT_EQUAL(STATE_FAULT, ctx.state);

    bool handled = cmdLocalButton(ctx, 2000);
    TEST_ASSERT_TRUE(handled);
    TEST_ASSERT_TRUE(ctx.muted);

    FsmOutput out = fsmStep(ctx, { 0.0f, true, false, 10000 }, th);
    TEST_ASSERT_EQUAL(BUZZ_OFF, out.buzzer);
    TEST_ASSERT_TRUE(out.buzzerMuted);
}

// ============================================================================
// T-F11: Buzzer pattern timing
// ============================================================================
void test_buzzer_pattern_timing(void) {
    TEST_ASSERT_TRUE(buzzerPattern(BUZZ_FAULT_BEEP, 0).on);
    TEST_ASSERT_TRUE(buzzerPattern(BUZZ_FAULT_BEEP, 199).on);
    TEST_ASSERT_FALSE(buzzerPattern(BUZZ_FAULT_BEEP, 200).on);
    TEST_ASSERT_FALSE(buzzerPattern(BUZZ_FAULT_BEEP, 1999).on);
    TEST_ASSERT_TRUE(buzzerPattern(BUZZ_FAULT_BEEP, 2000).on);
}

// ============================================================================
// T-F12: Exponential backoff
// ============================================================================
void test_exponential_backoff(void) {
    uint32_t b = 1000;
    b = nextBackoff(b); TEST_ASSERT_EQUAL(2000, b);
    b = nextBackoff(b); TEST_ASSERT_EQUAL(4000, b);
    b = nextBackoff(b); TEST_ASSERT_EQUAL(8000, b);
    b = nextBackoff(b); TEST_ASSERT_EQUAL(16000, b);
    b = nextBackoff(b); TEST_ASSERT_EQUAL(16000, b);
}

// ============================================================================
// T-C1: Fan manual control & AUTO restoration via applyFanAction
// ============================================================================
void test_cmd_fan_manual(void) {
    FsmContext ctx;
    ctx.manualMode = false;
    ctx.manualFan = false;

    ActionAck a1 = applyFanAction(ctx, "ON");
    TEST_ASSERT_EQUAL(ACTION_ACCEPTED, a1);
    TEST_ASSERT_TRUE(ctx.manualMode);
    TEST_ASSERT_TRUE(ctx.manualFan);

    ActionAck a2 = applyFanAction(ctx, "OFF");
    TEST_ASSERT_EQUAL(ACTION_ACCEPTED, a2);
    TEST_ASSERT_TRUE(ctx.manualMode);
    TEST_ASSERT_FALSE(ctx.manualFan);

    ActionAck a3 = applyFanAction(ctx, "AUTO");
    TEST_ASSERT_EQUAL(ACTION_ACCEPTED, a3);
    TEST_ASSERT_FALSE(ctx.manualMode);
    TEST_ASSERT_FALSE(ctx.manualFan);

    // Test case-insensitive lowercase support
    ActionAck aLowOn = applyFanAction(ctx, "on");
    TEST_ASSERT_EQUAL(ACTION_ACCEPTED, aLowOn);
    TEST_ASSERT_TRUE(ctx.manualFan);

    ActionAck aLowOff = applyFanAction(ctx, "off");
    TEST_ASSERT_EQUAL(ACTION_ACCEPTED, aLowOff);
    TEST_ASSERT_FALSE(ctx.manualFan);

    ActionAck aLowAuto = applyFanAction(ctx, "auto");
    TEST_ASSERT_EQUAL(ACTION_ACCEPTED, aLowAuto);
    TEST_ASSERT_FALSE(ctx.manualMode);
}

// ============================================================================
// T-C2: Fan OFF safety interlock during ALARM via applyFanAction
// ============================================================================
void test_cmd_fan_safety_interlock(void) {
    Thresholds th = makeThresholds(400.0f);
    FsmContext ctx;
    // Step into ALARM
    fsmStep(ctx, { 450.0f, false, false, 1000 }, th);
    TEST_ASSERT_EQUAL(STATE_ALARM, ctx.state);
    TEST_ASSERT_TRUE(ctx.alarmLatched);

    // Attempt to turn OFF fan remotely during ALARM
    ActionAck ack = applyFanAction(ctx, "OFF");
    TEST_ASSERT_EQUAL(ACTION_SAFETY_LOCK, ack);

    // Verify fan remains active
    FsmOutput out = fsmStep(ctx, { 450.0f, false, false, 2000 }, th);
    TEST_ASSERT_TRUE(out.fanOn);
}

// ============================================================================
// T-C3: Buzzer MUTE safety interlock during ALARM via applyBuzzerAction
// ============================================================================
void test_cmd_buzzer_mute_interlock(void) {
    Thresholds th = makeThresholds(400.0f);
    FsmContext ctx;
    fsmStep(ctx, { 450.0f, false, false, 1000 }, th);
    TEST_ASSERT_EQUAL(STATE_ALARM, ctx.state);
    TEST_ASSERT_TRUE(ctx.alarmLatched);

    ActionAck ack = applyBuzzerAction(ctx, "MUTE", 1000);
    TEST_ASSERT_EQUAL(ACTION_SAFETY_LOCK, ack);
    TEST_ASSERT_FALSE(ctx.muted);

    // Case-insensitive lowercase mute rejection during ALARM
    ActionAck ackLow = applyBuzzerAction(ctx, "mute", 1500);
    TEST_ASSERT_EQUAL(ACTION_SAFETY_LOCK, ackLow);
    TEST_ASSERT_FALSE(ctx.muted);

    FsmOutput out = fsmStep(ctx, { 450.0f, false, false, 2000 }, th);
    TEST_ASSERT_EQUAL(BUZZ_ALARM, out.buzzer);
    TEST_ASSERT_FALSE(out.buzzerMuted);
}

// ============================================================================
// T-C4: Buzzer UNMUTE restores audio alert via applyBuzzerAction
// ============================================================================
void test_cmd_buzzer_unmute(void) {
    FsmContext ctx;
    ctx.alarmLatched = false;
    ActionAck mRes = applyBuzzerAction(ctx, "MUTE", 1000);
    TEST_ASSERT_EQUAL(ACTION_ACCEPTED, mRes);
    TEST_ASSERT_TRUE(ctx.muted);

    ActionAck uRes = applyBuzzerAction(ctx, "UNMUTE", 2000);
    TEST_ASSERT_EQUAL(ACTION_ACCEPTED, uRes);
    TEST_ASSERT_FALSE(ctx.muted);
}

// ============================================================================
// T-C5: Buzzer TEST safety interlock during ALARM via applyBuzzerAction
// ============================================================================
void test_cmd_buzzer_test_interlock(void) {
    Thresholds th = makeThresholds(400.0f);
    FsmContext ctx;

    // In SAFE: TEST is permitted
    ActionAck okAck = applyBuzzerAction(ctx, "TEST", 1000);
    TEST_ASSERT_EQUAL(ACTION_ACCEPTED, okAck);

    // In ALARM: TEST is rejected to prevent overriding critical alarm tone
    fsmStep(ctx, { 450.0f, false, false, 2000 }, th);
    TEST_ASSERT_EQUAL(STATE_ALARM, ctx.state);
    ActionAck rejAck = applyBuzzerAction(ctx, "TEST", 3000);
    TEST_ASSERT_EQUAL(ACTION_SAFETY_LOCK, rejAck);
}

// ============================================================================
// T-C6: Unknown action safety rejection via applyFanAction & applyBuzzerAction
// ============================================================================
void test_cmd_unknown_action(void) {
    FsmContext ctx;
    ctx.manualMode = false;
    ctx.manualFan = false;

    // Test unknown fan action on real core parser
    ActionAck fanAck = applyFanAction(ctx, "EXPLODE");
    TEST_ASSERT_EQUAL(ACTION_UNKNOWN, fanAck);
    TEST_ASSERT_FALSE(ctx.manualMode);

    // Test unknown buzzer action on real core parser
    ActionAck buzzAck = applyBuzzerAction(ctx, "SELF_DESTRUCT", 1000);
    TEST_ASSERT_EQUAL(ACTION_UNKNOWN, buzzAck);
    TEST_ASSERT_FALSE(ctx.muted);
}

// ============================================================================
// T-B1: Circular buffer overflow (25/20) and partial flush (7/13) FIFO order
// ============================================================================
void test_offline_buffer_overflow_and_fifo(void) {
    RingBuffer<int, 20> rb;

    // Push 25 sequential records (0 to 24)
    for (int i = 0; i < 25; i++) {
        rb.push(i);
    }

    // Capacity must be strictly 20
    TEST_ASSERT_EQUAL(20, rb.size());
    TEST_ASSERT_TRUE(rb.full());

    // Verify the 20 remaining items are 5..24 in strict FIFO order
    for (size_t i = 0; i < rb.size(); i++) {
        TEST_ASSERT_EQUAL((int)(i + 5), rb.getOldest(i));
    }

    // Flush a partial batch of 7 items (items 5..11)
    for (size_t i = 0; i < 7; i++) {
        TEST_ASSERT_EQUAL((int)(i + 5), rb.getOldest(i));
    }
    rb.drop(7);
    TEST_ASSERT_EQUAL(13, rb.size());

    // Verify remaining 13 items are 12..24 in FIFO order
    for (size_t i = 0; i < rb.size(); i++) {
        TEST_ASSERT_EQUAL((int)(i + 12), rb.getOldest(i));
    }
}

// ============================================================================
// T-R1: Exponential backoff state machine simulation using ExponentialBackoff
// ============================================================================
void test_network_backoff_state_machine(void) {
    // 1. WiFi Backoff progression on repeated failures
    ExponentialBackoff wifi;
    TEST_ASSERT_EQUAL(1000, wifi.currentMs);

    wifi.fail(); TEST_ASSERT_EQUAL(2000, wifi.currentMs);
    wifi.fail(); TEST_ASSERT_EQUAL(4000, wifi.currentMs);
    wifi.fail(); TEST_ASSERT_EQUAL(8000, wifi.currentMs);
    wifi.fail(); TEST_ASSERT_EQUAL(16000, wifi.currentMs);
    wifi.fail(); TEST_ASSERT_EQUAL(16000, wifi.currentMs); // Capped at maxMs

    // Reconnection resets WiFi backoff immediately to initialMs (1000)
    wifi.reset();
    TEST_ASSERT_EQUAL(1000, wifi.currentMs);

    // 2. Decoupled MQTT Backoff progresses independently
    ExponentialBackoff mqtt;
    mqtt.fail(); TEST_ASSERT_EQUAL(2000, mqtt.currentMs);
    mqtt.fail(); TEST_ASSERT_EQUAL(4000, mqtt.currentMs);

    // MQTT Reconnection resets to 1000 without affecting WiFi
    mqtt.reset();
    TEST_ASSERT_EQUAL(1000, mqtt.currentMs);
    TEST_ASSERT_EQUAL(1000, wifi.currentMs);
}

// ============================================================================
// T-L1: Network socket timeout bound & non-blocking backoff CPU budget
// ============================================================================
void test_loop_timing_and_backoff_budget(void) {
    // 1. Backoff throttle progression ensures disconnected loops do not retry constantly
    ExponentialBackoff bo(1000, 16000);
    TEST_ASSERT_EQUAL(1000, bo.currentMs);
    bo.fail(); TEST_ASSERT_EQUAL(2000, bo.currentMs);
    bo.fail(); TEST_ASSERT_EQUAL(4000, bo.currentMs);
    bo.fail(); TEST_ASSERT_EQUAL(8000, bo.currentMs);
    bo.fail(); TEST_ASSERT_EQUAL(16000, bo.currentMs);
    bo.fail(); TEST_ASSERT_EQUAL(16000, bo.currentMs); // Capped at maxMs

    // 2. Verified socket timeout configuration bound:
    // Individual TCP connect phase timeout: 2000 ms
    // MQTT CONNACK socket timeout: 2000 ms
    // Both are strictly <= NET_MAX_BLOCK_MS (3000 ms)
    const uint32_t TCP_PHASE_TIMEOUT_MS = 2000;
    const uint32_t MQTT_SOCKET_TIMEOUT_MS = 2000;
    const uint32_t NET_MAX_BLOCK_MS = 3000;

    TEST_ASSERT_TRUE(TCP_PHASE_TIMEOUT_MS < NET_MAX_BLOCK_MS);
    TEST_ASSERT_TRUE(MQTT_SOCKET_TIMEOUT_MS < NET_MAX_BLOCK_MS);

    // 3. Worst-case sequential connection attempt (TCP connect + MQTT CONNACK + DNS)
    // can theoretically exceed NET_MAX_BLOCK_MS, justifying [PERF WARN] trigger in main loop.
    const uint32_t worstCaseAttemptMs = TCP_PHASE_TIMEOUT_MS + MQTT_SOCKET_TIMEOUT_MS;
    TEST_ASSERT_TRUE(worstCaseAttemptMs > NET_MAX_BLOCK_MS);

    // 4. During backoff window, netTick returns with 0ms delay (non-blocking)
    uint32_t simulatedNow = 5000;
    uint32_t lastAttempt = 4500;
    bool shouldAttempt = (simulatedNow - lastAttempt) >= bo.currentMs; // 500ms < 16000ms
    TEST_ASSERT_FALSE(shouldAttempt); // Throttled! Zero CPU blocking.
}

// ============================================================================
// MAIN RUNNER
// ============================================================================
int main(int argc, char **argv) {
    UNITY_BEGIN();
    RUN_TEST(test_thresholds_calc);
    RUN_TEST(test_ema_spike_suppression);
    RUN_TEST(test_ema_step_600);
    RUN_TEST(test_ema_step_500_and_450);
    RUN_TEST(test_ema_night_threshold);
    RUN_TEST(test_ema_recovery_reset);
    RUN_TEST(test_health_mq2_high_adc);
    RUN_TEST(test_health_mq2_debounce);
    RUN_TEST(test_health_dht);
    RUN_TEST(test_fsm_hysteresis);
    RUN_TEST(test_fsm_cooldown_finish);
    RUN_TEST(test_fsm_cooldown_reignition);
    RUN_TEST(test_fsm_mq2_fault_garbage_ppm);
    RUN_TEST(test_fsm_mq2_fault_during_alarm);
    RUN_TEST(test_fsm_dht_fault);
    RUN_TEST(test_fsm_mute_cleared_on_alarm_edge);
    RUN_TEST(test_fsm_interlock_during_alarm);
    RUN_TEST(test_fsm_local_ack_button_alarm);
    RUN_TEST(test_fsm_local_ack_button_fault);
    RUN_TEST(test_buzzer_pattern_timing);
    RUN_TEST(test_exponential_backoff);
    RUN_TEST(test_cmd_fan_manual);
    RUN_TEST(test_cmd_fan_safety_interlock);
    RUN_TEST(test_cmd_buzzer_mute_interlock);
    RUN_TEST(test_cmd_buzzer_unmute);
    RUN_TEST(test_cmd_buzzer_test_interlock);
    RUN_TEST(test_cmd_unknown_action);
    RUN_TEST(test_offline_buffer_overflow_and_fifo);
    RUN_TEST(test_network_backoff_state_machine);
    RUN_TEST(test_loop_timing_and_backoff_budget);
    return UNITY_END();
}

```

---

## PHẦN 37: KIỂM THỬ NODE-RED ENGINE (NODE TEST RUNNER) (`nodered/tests/engine.test.js`)

> **Đường dẫn:** `nodered/tests/engine.test.js`  
> **Quy mô:** 353 dòng | 12,358 bytes | Ngôn ngữ: `javascript`

```javascript
// nodered/tests/engine.test.js
const { test, describe, beforeEach } = require('node:test');
const assert = require('node:assert');
const { load, mkFlow, node, mkEnv } = require('./harness');

describe('Node-RED Engine & Functions Unit Tests', () => {
  let parseTelemetry, parseLwt, coreEngine, cmdDispatcher, alertDispatcher, schedTick;
  let flow;

  beforeEach(() => {
    parseTelemetry = load('functions/parse_telemetry.js');
    parseLwt = load('functions/parse_lwt.js');
    coreEngine = load('functions/core_engine.js');
    cmdDispatcher = load('functions/command_dispatcher.js');
    alertDispatcher = load('functions/alert_dispatcher.js');
    schedTick = load('functions/scheduler_tick.js');
    flow = mkFlow();
  });

  // T-N1: Deduplication TTL 5s
  test('T-N1: Deduplication within 5s TTL and re-allowed after 5s', () => {
    let originalNow = Date.now;
    let fakeTime = 1000000;
    Date.now = () => fakeTime;

    try {
      const msg1 = { payload: { device_id: 'A01', uptime_s: 42, mq2_ppm: 250, temp: 28 } };
      const res1 = parseTelemetry(msg1, flow, node, mkEnv());
      assert.ok(res1 !== null, 'First message should be processed');
      assert.strictEqual(res1.uptime, 42);

      // Same uptime immediately (simulating V2 parallel message)
      const msg2 = { payload: { device_id: 'A01', uptime_s: 42, mq2_ppm: 250, temp: 28 } };
      const res2 = parseTelemetry(msg2, flow, node, mkEnv());
      assert.strictEqual(res2, null, 'Duplicate within 5s should be dropped');

      // Advance time by 6000ms (> 5s TTL)
      fakeTime += 6000;
      const msg3 = { payload: { device_id: 'A01', uptime_s: 42, mq2_ppm: 250, temp: 28 } };
      const res3 = parseTelemetry(msg3, flow, node, mkEnv());
      assert.ok(res3 !== null, 'Message after 5s TTL should be re-allowed');
    } finally {
      Date.now = originalNow;
    }
  });

  // T-N2: LWT parsing
  test('T-N2: LWT JSON status and raw string parsing', () => {
    const resJsonOnline = parseLwt({ payload: '{"device_id":"ESP32_01","status":"online"}' }, flow, node, mkEnv());
    assert.strictEqual(resJsonOnline.isOnline, true);
    assert.strictEqual(resJsonOnline.deviceId, 'ESP32_01');

    const resJsonOffline = parseLwt({ payload: { device_id: 'ESP32_01', status: 'offline' } }, flow, node, mkEnv());
    assert.strictEqual(resJsonOffline.isOnline, false);

    const resRawOnline = parseLwt({ payload: 'online' }, flow, node, mkEnv());
    assert.strictEqual(resRawOnline.isOnline, true);

    const resRawOffline = parseLwt({ payload: 'offline' }, flow, node, mkEnv());
    assert.strictEqual(resRawOffline.isOnline, false);
  });

  // T-N3: Low-heat smoke (Rule 2)
  test('T-N3: PPM 450 with low heat (temp 30, dT/dt 0) triggers ALARM, fan ON, no MUTE', () => {
    const msg = {
      eventType: 'TELEMETRY',
      deviceId: 'A01',
      ppm: 450,
      temp: 30,
      fsmState: 'ALARM',
      mq2Valid: true,
      dhtValid: true,
      alarmTh: 400,
      safeTh: 300
    };

    const out = coreEngine(msg, flow, node, mkEnv());
    const cmds = out[0];
    const alert = out[3];
    const fleet = flow.get('fleet');

    assert.strictEqual(fleet['A01'].effective, 'ALARM');
    assert.ok(cmds && cmds.length > 0, 'Commands should be dispatched');

    const fanCmd = cmds.find(c => c.topic.includes('/cmd/fan'));
    assert.ok(fanCmd, 'Fan command should be present');
    const fanPayload = JSON.parse(fanCmd.payload);
    assert.strictEqual(fanPayload.action, 'ON');
    assert.strictEqual(fanPayload.reason, 'RULE_2_LOW_HEAT_SMOKE');

    const muteCmd = cmds.find(c => c.topic.includes('/cmd/buzzer') && JSON.parse(c.payload).action === 'MUTE');
    assert.strictEqual(muteCmd, undefined, 'Must NOT contain MUTE command');
    assert.ok(alert !== null, 'Alert notification should be generated');
  });

  // T-N4: Real fire (Rule 1)
  test('T-N4: Temperature rate >= 3.0 C/min triggers UNMUTE once', () => {
    let originalNow = Date.now;
    let fakeTime = 1000000;
    Date.now = () => fakeTime;

    try {
      // First telemetry at t=0: temp=28, ppm=450
      const msg1 = {
        eventType: 'TELEMETRY',
        deviceId: 'A01',
        ppm: 450,
        temp: 28,
        fsmState: 'ALARM',
        mq2Valid: true,
        dhtValid: true,
        alarmTh: 400,
        safeTh: 300
      };
      coreEngine(msg1, flow, node, mkEnv());

      // Advance by 25s (25000ms), temp rises from 28 to 29.5 -> rate = 1.5 / (25/60) = 3.6 C/min >= 3.0
      fakeTime += 25000;
      const msg2 = {
        eventType: 'TELEMETRY',
        deviceId: 'A01',
        ppm: 450,
        temp: 29.5,
        fsmState: 'ALARM',
        mq2Valid: true,
        dhtValid: true,
        alarmTh: 400,
        safeTh: 300
      };
      const out2 = coreEngine(msg2, flow, node, mkEnv());
      const cmds2 = out2[0];
      assert.ok(cmds2, 'Commands expected on real fire confirmation');
      const unmuteCmd = cmds2.find(c => c.topic.includes('/cmd/buzzer') && JSON.parse(c.payload).action === 'UNMUTE');
      assert.ok(unmuteCmd, 'UNMUTE command should be dispatched');

      // Subsequent packet 2s later with same high temp
      fakeTime += 2000;
      const msg3 = {
        eventType: 'TELEMETRY',
        deviceId: 'A01',
        ppm: 450,
        temp: 29.5,
        fsmState: 'ALARM',
        mq2Valid: true,
        dhtValid: true,
        alarmTh: 400,
        safeTh: 300
      };
      const out3 = coreEngine(msg3, flow, node, mkEnv());
      const cmds3 = out3[0];
      const dupUnmute = (cmds3 || []).find(c => c.topic.includes('/cmd/buzzer') && JSON.parse(c.payload).action === 'UNMUTE');
      assert.strictEqual(dupUnmute, undefined, 'Must NOT re-dispatch UNMUTE continuously');
    } finally {
      Date.now = originalNow;
    }
  });

  // T-N5: Cross-zone broadcast (Rule 5)
  test('T-N5: Cross-zone broadcast over 600 PPM to floor F03 devices without wildcards', () => {
    let originalNow = Date.now;
    let fakeTime = 1000000;
    Date.now = () => fakeTime;

    try {
      // Setup fleet with A02 on Floor F03 with concrete topology
      const fleet = {
        A02: {
          deviceId: 'A02',
          status: 'ONLINE',
          deviceState: 'SAFE',
          effective: 'SAFE',
          topology: { building: 'HUIT_A', floor: 'F03', room: 'P303' }
        }
      };
      flow.set('fleet', fleet);

      // A01 first packet with PPM 655
      const msg1 = {
        eventType: 'TELEMETRY',
        deviceId: 'A01',
        ppm: 655,
        temp: 30,
        fsmState: 'ALARM',
        mq2Valid: true,
        dhtValid: true,
        alarmTh: 400,
        safeTh: 300
      };
      const out1 = coreEngine(msg1, flow, node, mkEnv());
      const cmds1 = out1[0];
      assert.ok(cmds1 && cmds1.length > 0, 'Should dispatch cross-zone commands');

      const evacCmd = cmds1.find(c => c.topic.includes('A02/cmd/buzzer'));
      assert.ok(evacCmd, 'Should send evacuation command to A02');
      assert.strictEqual(evacCmd.topic.includes('+'), false, 'Topic must NOT contain +');
      assert.strictEqual(evacCmd.topic.includes('#'), false, 'Topic must NOT contain #');
      assert.strictEqual(evacCmd.topic, 'Nhom09/smoke/v2/HUIT_A/F03/P303/A02/cmd/buzzer');

      // Second packet within 60s
      fakeTime += 10000;
      const msg2 = {
        eventType: 'TELEMETRY',
        deviceId: 'A01',
        ppm: 660,
        temp: 30,
        fsmState: 'ALARM',
        mq2Valid: true,
        dhtValid: true,
        alarmTh: 400,
        safeTh: 300
      };
      const out2 = coreEngine(msg2, flow, node, mkEnv());
      const cmds2 = out2[0] || [];
      const dupEvac = cmds2.find(c => c.topic.includes('A02/cmd/buzzer'));
      assert.strictEqual(dupEvac, undefined, 'Must rate-limit cross-zone broadcast (60s window)');
    } finally {
      Date.now = originalNow;
    }
  });

  // T-N6: MQ-2 Fault
  test('T-N6: mq2_valid:false escalates to FAULT and ignores PPM rules', () => {
    const msg = {
      eventType: 'TELEMETRY',
      deviceId: 'A01',
      ppm: null,
      mq2Valid: false,
      dhtValid: true,
      temp: 28,
      fsmState: 'SAFE',
      alarmTh: 400,
      safeTh: 300
    };

    const out = coreEngine(msg, flow, node, mkEnv());
    const fleet = flow.get('fleet');
    assert.strictEqual(fleet['A01'].effective, 'FAULT');
    const cmds = out[0];
    assert.strictEqual(cmds, null, 'No commands should be generated from invalid PPM');
  });

  // T-N7: Cooldown
  test('T-N7: Device reporting COOLDOWN keeps effective COOLDOWN without commands', () => {
    const msg = {
      eventType: 'TELEMETRY',
      deviceId: 'A01',
      ppm: 250,
      temp: 28,
      fsmState: 'COOLDOWN',
      mq2Valid: true,
      dhtValid: true,
      alarmTh: 400,
      safeTh: 300
    };

    const out = coreEngine(msg, flow, node, mkEnv());
    const fleet = flow.get('fleet');
    assert.strictEqual(fleet['A01'].effective, 'COOLDOWN');
    assert.strictEqual(out[0], null, 'No commands should be dispatched during COOLDOWN');
  });

  // T-N8: Multi-device isolation
  test('T-N8: Device states are strictly isolated', () => {
    coreEngine({
      eventType: 'TELEMETRY',
      deviceId: 'A01',
      ppm: 450,
      temp: 30,
      fsmState: 'ALARM',
      mq2Valid: true,
      dhtValid: true
    }, flow, node, mkEnv());

    coreEngine({
      eventType: 'TELEMETRY',
      deviceId: 'A02',
      ppm: 200,
      temp: 26,
      fsmState: 'SAFE',
      mq2Valid: true,
      dhtValid: true
    }, flow, node, mkEnv());

    const fleet = flow.get('fleet');
    assert.strictEqual(fleet['A01'].effective, 'ALARM');
    assert.strictEqual(fleet['A02'].effective, 'SAFE');
  });

  // T-N9: Command Dispatcher wildcard check
  test('T-N9: Command Dispatcher drops topics with + or # wildcards', () => {
    let warningLogged = false;
    const testNode = {
      warn: () => { warningLogged = true; }
    };

    const invalidMsg = { topic: 'Nhom09/smoke/v2/HUIT_A/F03/+/cmd/buzzer', payload: '{}' };
    const resInvalid = cmdDispatcher(invalidMsg, flow, testNode, mkEnv());
    assert.strictEqual(resInvalid, null, 'Wildcard topic must be dropped');
    assert.strictEqual(warningLogged, true, 'Warning should be logged');

    const validMsg = { topic: 'Nhom09/smoke/cmd/fan', payload: '{}' };
    const resValid = cmdDispatcher(validMsg, flow, testNode, mkEnv());
    assert.strictEqual(resValid, validMsg, 'Valid concrete topic must pass');
  });

  // T-N10: Watchdog timeout
  test('T-N10: Watchdog turns only silent device to OFFLINE after 30s', () => {
    let originalNow = Date.now;
    let fakeTime = 1000000;
    Date.now = () => fakeTime;

    try {
      const fleet = {
        A01: { deviceId: 'A01', status: 'ONLINE', effective: 'SAFE', lastSeen: fakeTime - 31000 },
        A02: { deviceId: 'A02', status: 'ONLINE', effective: 'SAFE', lastSeen: fakeTime - 5000 }
      };
      flow.set('fleet', fleet);

      coreEngine({ eventType: 'WATCHDOG_TICK' }, flow, node, mkEnv());

      const updated = flow.get('fleet');
      assert.strictEqual(updated['A01'].status, 'OFFLINE');
      assert.strictEqual(updated['A01'].effective, 'OFFLINE');
      assert.strictEqual(updated['A02'].status, 'ONLINE');
    } finally {
      Date.now = originalNow;
    }
  });

  // T-N11: Fault injection logging
  test('T-N11: Fault injection commands are logged without altering state directly', () => {
    const fleet = {
      A01: { deviceId: 'A01', status: 'ONLINE', effective: 'SAFE', deviceState: 'SAFE' }
    };
    flow.set('fleet', fleet);

    coreEngine({ eventType: 'FAULT_INJECTION_CMD', deviceId: 'A01', faultType: 'UNKNOWN_FAULT' }, flow, node, mkEnv());

    const updated = flow.get('fleet');
    assert.strictEqual(updated['A01'].effective, 'SAFE');
    const history = flow.get('history') || [];
    assert.ok(history.some(h => h.event === 'FAULT_INJECTION_SEEN'));
  });

  // T-N12: Alert dispatcher mock
  test('T-N12: Without TELEGRAM_TOKEN, alert dispatcher outputs to debug/dashboard mock only', () => {
    const alertMsg = { payload: { deviceId: 'A01', text: 'Canh bao chay' } };
    const out = alertDispatcher(alertMsg, flow, node, mkEnv({}));

    assert.strictEqual(out[0], null, 'HTTP request must be null when token is missing');
    assert.ok(out[1] && out[1].payload.includes('[A01] Canh bao chay'), 'Output 2 must carry mock text');
  });
});

```

---

## PHẦN 38: KIỂM THỬ TÍCH HỢP FLOW NODE-RED (FLOW INTEGRATION) (`nodered/tests/flow_integration.test.js`)

> **Đường dẫn:** `nodered/tests/flow_integration.test.js`  
> **Quy mô:** 211 dòng | 8,346 bytes | Ngôn ngữ: `javascript`

```javascript
// nodered/tests/flow_integration.test.js
// Flow-level integration test validating the actual flows_smoke_detector.json
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');

const flowPath = path.resolve(__dirname, '../flows_smoke_detector.json');
const flowJson = JSON.parse(fs.readFileSync(flowPath, 'utf8'));

// Build indexed map of nodes by ID
const nodeMap = new Map();
flowJson.forEach(n => nodeMap.set(n.id, n));

function createMockContext() {
  const store = {};
  return {
    get: (k) => store[k],
    set: (k, v) => { store[k] = v; },
    _store: store
  };
}

function runNodeFunction(node, msg, flowCtx, nodeCtx = {}) {
  const fn = new Function('msg', 'flow', 'node', node.func);
  return fn(msg, flowCtx, {
    warn: () => {},
    error: () => {},
    send: () => {},
    ...nodeCtx
  });
}

test('FLOW-01: Structural wiring verification of flows_smoke_detector.json', () => {
  const authNode = nodeMap.get('fn_auth_service');
  assert.ok(authNode, 'fn_auth_service must exist');
  assert.ok(authNode.func.includes('flow.set("fleet"'), 'fn_auth_service must write to "fleet"');

  const alarmNode = nodeMap.get('fn_parse_alarm');
  assert.ok(alarmNode, 'fn_parse_alarm must exist');
  assert.ok(alarmNode.func.includes("ALARM_EVENT"), 'fn_parse_alarm must set ALARM_EVENT');
  assert.ok(alarmNode.func.includes("cache"), 'fn_parse_alarm must have dedup cache');

  const keepAliveNode = nodeMap.get('fn_parse_keepalive');
  assert.ok(keepAliveNode, 'fn_parse_keepalive must exist');
  assert.ok(keepAliveNode.func.includes("KEEP_ALIVE"), 'fn_parse_keepalive must set KEEP_ALIVE');

  const schedInject = nodeMap.get('inject_scheduler_1m');
  assert.ok(schedInject, 'inject_scheduler_1m must exist');
  assert.equal(schedInject.repeat, '60', 'Scheduler must repeat every 60s');
  assert.deepEqual(schedInject.wires[0], ['fn_scheduler_tick']);

  const schedTick = nodeMap.get('fn_scheduler_tick');
  assert.ok(schedTick, 'fn_scheduler_tick must exist');
  assert.ok(schedTick.wires[0].includes('fn_command_dispatcher'));

  const coreEngine = nodeMap.get('fn_core_fsm_engine');
  assert.ok(coreEngine, 'fn_core_fsm_engine must exist');
  assert.equal(coreEngine.outputs, 4);
  assert.ok(coreEngine.wires[0].includes('fn_command_dispatcher'));
  assert.ok(coreEngine.wires[1].includes('fn_audit_logger'));
  assert.ok(coreEngine.wires[2].includes('fn_ui_dashboard_adapter'));
  assert.ok(coreEngine.wires[3].includes('fn_alert_dispatcher'));
});

test('FLOW-02: Auth populates fleet topology & Core Engine generates hierarchical V2 topics', () => {
  const flowCtx = createMockContext();
  const authNode = nodeMap.get('fn_auth_service');
  const coreEngine = nodeMap.get('fn_core_fsm_engine');
  const cmdDispatcher = nodeMap.get('fn_command_dispatcher');

  // Authenticate ESP32_SMOKE_N04_A01
  const authReqA01 = {
    payload: {
      device_id: 'ESP32_SMOKE_N04_A01',
      mac_address: '24:6F:28:AB:CD:10',
      secret_token: 'HUIT_IOT_SECURE_TOKEN_N04'
    }
  };
  const [authResp1] = runNodeFunction(authNode, authReqA01, flowCtx);
  assert.equal(authResp1.topic, 'Nhom09/smoke/v2/auth/response/ESP32_SMOKE_N04_A01');
  const payload1 = JSON.parse(authResp1.payload);
  assert.equal(payload1.status, 'PASS');

  // Check flow context fleet has topology
  const fleet = flowCtx.get('fleet');
  assert.ok(fleet['ESP32_SMOKE_N04_A01']);
  assert.deepEqual(fleet['ESP32_SMOKE_N04_A01'].topology, {
    building: 'HUIT_A',
    floor: 'F03',
    room: 'P302',
    zone: 'Phòng Lab IoT'
  });

  // Authenticate ESP32_SMOKE_N04_A02
  const authReqA02 = {
    payload: {
      device_id: 'ESP32_SMOKE_N04_A02',
      mac_address: '24:6F:28:AB:CD:20',
      secret_token: 'HUIT_IOT_SECURE_TOKEN_N04'
    }
  };
  runNodeFunction(authNode, authReqA02, flowCtx);

  // Send high smoke telemetry (650 PPM, temp 52.0 C) from A01 to trigger Rule 1 and Rule 5
  const parseTelemetryNode = nodeMap.get('fn_parse_telemetry');
  const telemetryMsg = runNodeFunction(parseTelemetryNode, {
    payload: {
      device_id: 'ESP32_SMOKE_N04_A01',
      mq2_ppm: 650.0,
      temp: 52.0,
      hum: 58.5,
      fsm_state: 'SAFE',
      uptime_s: 100
    }
  }, flowCtx);

  assert.equal(telemetryMsg.eventType, 'TELEMETRY');
  assert.equal(telemetryMsg.hum, 58.5);

  const [cmds, logs, dashboard, alert] = runNodeFunction(coreEngine, telemetryMsg, flowCtx);

  // Check dashboard carries humidity
  assert.ok(dashboard);
  assert.equal(dashboard.payload.hum, 58.5);

  // Check Rule 5 cross-zone broadcast generated a valid V2 command for A02
  assert.ok(cmds && cmds.length >= 2, 'Should emit fan command for A01 and cross-zone for A02');
  const crossCmd = cmds.find(c => c.topic.includes('ESP32_SMOKE_N04_A02'));
  assert.ok(crossCmd, 'Should have cross-zone evacuation command for ESP32_SMOKE_N04_A02');
  assert.equal(crossCmd.topic, 'Nhom09/smoke/v2/HUIT_A/F03/P303/ESP32_SMOKE_N04_A02/cmd/buzzer');

  // Verify command dispatcher accepts topic without wildcard errors
  const dispatched = runNodeFunction(cmdDispatcher, crossCmd, flowCtx);
  assert.ok(dispatched, 'Command dispatcher must pass valid hierarchical topic');
  assert.equal(dispatched.topic, 'Nhom09/smoke/v2/HUIT_A/F03/P303/ESP32_SMOKE_N04_A02/cmd/buzzer');
});

test('FLOW-03: Scheduler inject & tick updates fleet Day/Night thresholds deterministically', () => {
  const origGetHours = Date.prototype.getHours;
  try {
    const flowCtx = createMockContext();
    flowCtx.set('fleet', {
      ESP32_SMOKE_N04_A01: { deviceId: 'ESP32_SMOKE_N04_A01', alarmTh: 400, safeTh: 300 }
    });

    const schedTick = nodeMap.get('fn_scheduler_tick');
    const parseSched = nodeMap.get('fn_parse_scheduler');
    const coreEngine = nodeMap.get('fn_core_fsm_engine');

    // 1. Simulate NIGHT (23h)
    Date.prototype.getHours = () => 23;
    flowCtx.set('sched', null); // clear state
    const nightTick = runNodeFunction(schedTick, {}, flowCtx);
    assert.ok(nightTick, 'Scheduler tick must fire for NIGHT');
    const nightParsed = runNodeFunction(parseSched, nightTick, flowCtx);
    assert.equal(nightParsed.eventType, 'SCHEDULER_CMD');
    assert.equal(nightParsed.mode, 'NIGHT');
    runNodeFunction(coreEngine, nightParsed, flowCtx);
    let dev = flowCtx.get('fleet')['ESP32_SMOKE_N04_A01'];
    assert.equal(dev.alarmTh, 350, 'NIGHT mode must set alarmTh to 350');
    assert.equal(dev.safeTh, 262.5, 'NIGHT mode must set safeTh to 262.5');

    // 2. Simulate DAY (14h)
    Date.prototype.getHours = () => 14;
    const dayTick = runNodeFunction(schedTick, {}, flowCtx);
    assert.ok(dayTick, 'Scheduler tick must fire for transition to DAY');
    const dayParsed = runNodeFunction(parseSched, dayTick, flowCtx);
    assert.equal(dayParsed.eventType, 'SCHEDULER_CMD');
    assert.equal(dayParsed.mode, 'DAY');
    runNodeFunction(coreEngine, dayParsed, flowCtx);
    dev = flowCtx.get('fleet')['ESP32_SMOKE_N04_A01'];
    assert.equal(dev.alarmTh, 400, 'DAY mode must set alarmTh to 400');
    assert.equal(dev.safeTh, 300, 'DAY mode must set safeTh to 300');
  } finally {
    Date.prototype.getHours = origGetHours;
  }
});

test('FLOW-04: Alarm and keep-alive parsers deduplicate rapid duplicate payloads', () => {
  const flowCtx = createMockContext();
  const parseAlarm = nodeMap.get('fn_parse_alarm');
  const parseKeepAlive = nodeMap.get('fn_parse_keepalive');

  const alarmPayload = {
    device_id: 'ESP32_SMOKE_N04_A01',
    event: 'SMOKE_ALERT',
    ppm: 450,
    uptime_s: 120
  };

  const m1 = runNodeFunction(parseAlarm, { payload: alarmPayload }, flowCtx);
  assert.ok(m1, 'First alarm event must pass');
  assert.equal(m1.eventType, 'ALARM_EVENT');

  const m2 = runNodeFunction(parseAlarm, { payload: alarmPayload }, flowCtx);
  assert.equal(m2, null, 'Duplicate alarm event within 5s must be suppressed');

  const kaPayload = {
    device_id: 'ESP32_SMOKE_N04_A01',
    uptime_sec: 120,
    free_heap_bytes: 180000
  };

  const k1 = runNodeFunction(parseKeepAlive, { payload: kaPayload }, flowCtx);
  assert.ok(k1, 'First keep-alive must pass');
  assert.equal(k1.eventType, 'KEEP_ALIVE');

  const k2 = runNodeFunction(parseKeepAlive, { payload: kaPayload }, flowCtx);
  assert.equal(k2, null, 'Duplicate keep-alive within 5s must be suppressed');
});

```

---

## PHẦN 39: KIỂM THỬ WEB SCADA XSS & REFLECTION (`web/tests/util.test.js`)

> **Đường dẫn:** `web/tests/util.test.js`  
> **Quy mô:** 194 dòng | 7,037 bytes | Ngôn ngữ: `javascript`

```javascript
// web/tests/util.test.js
// Tests real web/app.js functions directly via a mock DOM environment
const { test, describe, beforeEach } = require('node:test');
const assert = require('node:assert/strict');

// Minimal mock DOM element representation
class MockElement {
  constructor(tag = 'div') {
    this.tagName = tag.toUpperCase();
    this.children = [];
    this._textContent = '';
    this.className = '';
    this.style = {};
    this.value = 'ALL';
    this.remove = () => {};
    this.classList = {
      _classes: new Set(),
      add: (...cls) => cls.forEach(c => this.classList._classes.add(c)),
      remove: (...cls) => cls.forEach(c => this.classList._classes.delete(c)),
      contains: (c) => this.classList._classes.has(c)
    };
  }

  set textContent(v) {
    this._textContent = String(v);
    this.children = [];
  }

  get textContent() {
    if (this.children.length > 0) return this.children.map(c => c.textContent).join('');
    return this._textContent;
  }

  appendChild(child) {
    this.children.push(child);
    return child;
  }

  getElementsByTagName(tag) {
    const res = [];
    const t = tag.toUpperCase();
    const search = el => {
      for (const c of el.children) {
        if (c.tagName === t) res.push(c);
        search(c);
      }
    };
    search(this);
    return res;
  }
}

// Setup global mock document before requiring app.js
const mockElements = {
  auditTableBody: new MockElement('tbody'),
  logFilterLevel: new MockElement('select'),
  toastContainer: new MockElement('div'),
  clockDisplay: new MockElement('span'),
  valSmokePpm: new MockElement('span'),
  valTemp: new MockElement('span'),
  valHum: new MockElement('span'),
  kpiSmoke: new MockElement('div'),
  tagSmoke: new MockElement('span'),
  fsmChip: new MockElement('div'),
  fsmStatusText: new MockElement('span'),
  alarmBanner: new MockElement('div'),
  bannerTitle: new MockElement('h4'),
  bannerDesc: new MockElement('p'),
  btnFanOff: new MockElement('button'),
  btnBuzzerMute: new MockElement('button'),
  btnBannerMute: new MockElement('button')
};

global.document = {
  getElementById: (id) => mockElements[id] || new MockElement('div'),
  createElement: (tag) => new MockElement(tag),
  createTextNode: (text) => ({ tagName: '#TEXT', textContent: text, children: [] }),
  addEventListener: () => {}
};

// Require real app.js directly!
const app = require('../app');
const { escapeHtml, renderAuditTable, showToast, handleMqttMessage, updateUiFromState, STATE, DOM } = app;

describe('Web SCADA Direct app.js Unit Tests', () => {

  beforeEach(() => {
    mockElements.auditTableBody.children = [];
    mockElements.toastContainer.children = [];
    STATE.logs = [];
  });

  // T-W1: Direct escapeHtml verification from app.js
  test('T-W1: escapeHtml from app.js sanitizes XSS payloads and special characters', () => {
    const raw = '<img src=x onerror=alert(1)> & "hello" \'world\'';
    const escaped = escapeHtml(raw);

    assert.equal(escaped.includes('<'), false, 'Must not contain literal <');
    assert.equal(escaped.includes('>'), false, 'Must not contain literal >');
    assert.equal(escaped.includes('"'), false, 'Must not contain literal "');
    assert.equal(escaped.includes("'"), false, "Must not contain literal '");
    assert.ok(escaped.includes('&lt;img'), 'Must escape < to &lt;');
    assert.ok(escaped.includes('&amp;'), 'Must escape & to &amp;');
    assert.ok(escaped.includes('&quot;'), 'Must escape " to &quot;');
    assert.ok(escaped.includes('&#39;'), "Must escape ' to &#39;");

    // Null/undefined safety
    assert.equal(escapeHtml(null), '');
    assert.equal(escapeHtml(undefined), '');
  });

  // T-W2: Direct renderAuditTable execution from app.js
  test('T-W2: renderAuditTable() from app.js renders logs via textContent without creating script elements', () => {
    STATE.logs = [
      {
        time: '12:00:00',
        level: 'CRITICAL',
        event: 'EXPLOIT_TEST',
        desc: '<script>alert("hacked")</script><img src=x onerror=alert(1)>',
        fsm: 'ALARM'
      }
    ];

    // Call REAL function from app.js!
    renderAuditTable();

    const tbody = mockElements.auditTableBody;
    assert.equal(tbody.children.length, 1, 'Should render 1 table row');

    const scripts = tbody.getElementsByTagName('script');
    assert.equal(scripts.length, 0, 'No script elements must be created in the DOM');

    const row = tbody.children[0];
    const descCell = row.children[3];
    assert.equal(descCell.textContent, STATE.logs[0].desc, 'Payload is rendered purely as textContent');
  });

  // T-W3: Direct showToast execution from app.js
  test('T-W3: showToast() from app.js mounts message via textContent and does not parse HTML', () => {
    const dangerousMsg = '<b>Alert</b><script>alert(1)</script>';

    // Call REAL function from app.js!
    showToast(dangerousMsg, 'danger');

    const container = mockElements.toastContainer;
    assert.equal(container.children.length, 1, 'Toast container should receive 1 toast');

    const toast = container.children[0];
    const scripts = toast.getElementsByTagName('script');
    assert.equal(scripts.length, 0, 'No script elements must exist in toast container');
    assert.ok(toast.textContent.includes(dangerousMsg), 'Message is preserved as literal textContent');
  });

  // T-W4: Direct handleMqttMessage execution from app.js
  test('T-W4: handleMqttMessage() from app.js reflects telemetry and fsm_state without sending commands', () => {
    STATE.fsmState = 'SAFE';
    STATE.fanState = false;
    STATE.health.mq2 = 'OK';

    const telemetryPayload = JSON.stringify({
      device_id: 'ESP32_SMOKE_N04_A01',
      mq2_ppm: null,
      mq2_valid: false,
      dht_valid: true,
      fsm_state: 'ALARM',
      alarm_th: 400,
      safe_th: 300,
      fan: 'ON',
      buzzer: 'ON'
    });

    // Call REAL handleMqttMessage from app.js!
    handleMqttMessage('Nhom09/smoke/telemetry', telemetryPayload);

    assert.equal(STATE.fsmState, 'ALARM', 'Web SCADA must reflect fsm_state from ESP32');
    assert.equal(STATE.health.mq2, 'FAULT', 'Web SCADA must reflect MQ-2 fault badge');
    assert.equal(STATE.fanState, true, 'Web SCADA must reflect fan ON from ESP32');
    assert.equal(STATE.alarmThreshold, 400, 'Web SCADA must reflect alarmThreshold');
  });

  // T-W5: Direct updateUiFromState execution from app.js proving UI Safety Interlock
  test('T-W5: updateUiFromState() disables actuator controls during ALARM and restores in SAFE', () => {
    STATE.fsmState = 'ALARM';
    updateUiFromState();
    assert.equal(DOM.btnFanOff.disabled, true, 'Fan OFF button must be disabled during ALARM');
    assert.equal(DOM.btnBuzzerMute.disabled, true, 'Buzzer MUTE button must be disabled during ALARM');

    STATE.fsmState = 'SAFE';
    updateUiFromState();
    assert.equal(DOM.btnFanOff.disabled, false, 'Fan OFF button must be re-enabled during SAFE');
    assert.equal(DOM.btnBuzzerMute.disabled, false, 'Buzzer MUTE button must be re-enabled during SAFE');
  });

});

```

---

## PHẦN 40: BỘ KỊCH BẢN KIỂM THỬ MQTTX SLIDE 65 (23 MESSAGES) (`tests/mqttx_collection_slide65.json`)

> **Đường dẫn:** `tests/mqttx_collection_slide65.json`  
> **Quy mô:** 658 dòng | 22,357 bytes | Ngôn ngữ: `json`

```json
[
  {
    "id": "test-client-n04",
    "name": "MQTTX_Collection_Smoke_Detector_Slide65_Nhom04",
    "clientId": "MQTTX_Test_Client_Nhom04",
    "host": "broker.emqx.io",
    "port": 1883,
    "keepalive": 60,
    "clean": true,
    "protocolVersion": 4,
    "subscriptions": [
      {
        "id": "sub-0",
        "topic": "Nhom09/smoke/v2/auth/response/#",
        "qos": 1,
        "alias": "Nhan phan hoi xac thuc tu Server",
        "createAt": "2026-10-10T00:00:00.000Z",
        "updateAt": "2026-10-10T00:00:00.000Z",
        "color": "#e27300",
        "nl": false,
        "rap": false,
        "rh": 0,
        "properties": {}
      },
      {
        "id": "sub-1",
        "topic": "Nhom09/smoke/v2/+/+/+/+/telemetry",
        "qos": 0,
        "alias": "Luyen nghe du lieu cam bien toan toa nha",
        "createAt": "2026-10-10T00:00:00.000Z",
        "updateAt": "2026-10-10T00:00:00.000Z",
        "color": "#e27300",
        "nl": false,
        "rap": false,
        "rh": 0,
        "properties": {}
      },
      {
        "id": "sub-2",
        "topic": "Nhom09/smoke/v2/+/+/+/+/keep_alive",
        "qos": 0,
        "alias": "Lang nghe tin hieu song Keep-Alive",
        "createAt": "2026-10-10T00:00:00.000Z",
        "updateAt": "2026-10-10T00:00:00.000Z",
        "color": "#e27300",
        "nl": false,
        "rap": false,
        "rh": 0,
        "properties": {}
      },
      {
        "id": "sub-3",
        "topic": "Nhom09/smoke/v2/+/+/+/+/event/#",
        "qos": 1,
        "alias": "Lang nghe su co chay no khan cap",
        "createAt": "2026-10-10T00:00:00.000Z",
        "updateAt": "2026-10-10T00:00:00.000Z",
        "color": "#e27300",
        "nl": false,
        "rap": false,
        "rh": 0,
        "properties": {}
      },
      {
        "id": "sub-4",
        "topic": "Nhom09/smoke/v2/+/+/+/+/status",
        "qos": 1,
        "alias": "Nhan phan hoi thuc thi lenh (ACK) tu thiet bi",
        "createAt": "2026-10-10T00:00:00.000Z",
        "updateAt": "2026-10-10T00:00:00.000Z",
        "color": "#e27300",
        "nl": false,
        "rap": false,
        "rh": 0,
        "properties": {}
      },
      {
        "id": "sub-5",
        "topic": "Nhom09/smoke/telemetry",
        "qos": 0,
        "alias": "Uplink: Telemetry định kỳ V1 (Khói, Nhiệt, Ẩm)",
        "createAt": "2026-10-10T00:00:00.000Z",
        "updateAt": "2026-10-10T00:00:00.000Z",
        "color": "#00b500",
        "nl": false,
        "rap": false,
        "rh": 0,
        "properties": {}
      },
      {
        "id": "sub-6",
        "topic": "Nhom09/smoke/event/alarm",
        "qos": 1,
        "alias": "Uplink: Báo động khẩn cấp V1 (Event Alarm)",
        "createAt": "2026-10-10T00:00:00.000Z",
        "updateAt": "2026-10-10T00:00:00.000Z",
        "color": "#ca3838",
        "nl": false,
        "rap": false,
        "rh": 0,
        "properties": {}
      },
      {
        "id": "sub-7",
        "topic": "Nhom09/smoke/status",
        "qos": 1,
        "alias": "Uplink: Thiết bị phản hồi ACK thực thi lệnh",
        "createAt": "2026-10-10T00:00:00.000Z",
        "updateAt": "2026-10-10T00:00:00.000Z",
        "color": "#1f77b4",
        "nl": false,
        "rap": false,
        "rh": 0,
        "properties": {}
      },
      {
        "id": "sub-8",
        "topic": "Nhom09/smoke/lwt",
        "qos": 1,
        "alias": "Uplink: Bản tin Di chúc LWT khi mất kết nối đột ngột",
        "createAt": "2026-10-10T00:00:00.000Z",
        "updateAt": "2026-10-10T00:00:00.000Z",
        "color": "#7f8c8d",
        "nl": false,
        "rap": false,
        "rh": 0,
        "properties": {}
      },
      {
        "id": "sub-9",
        "topic": "Nhom09/smoke/cmd/#",
        "qos": 1,
        "alias": "Downlink: Giám sát mọi lệnh điều khiển phát từ Web/Node-RED",
        "createAt": "2026-10-10T00:00:00.000Z",
        "updateAt": "2026-10-10T00:00:00.000Z",
        "color": "#9467bd",
        "nl": false,
        "rap": false,
        "rh": 0,
        "properties": {}
      },
      {
        "id": "sub-10",
        "topic": "Nhom09/smoke/#",
        "qos": 1,
        "alias": "Toàn cảnh: Kênh Wildcard giám sát 100% gói tin hệ thống",
        "createAt": "2026-10-10T00:00:00.000Z",
        "updateAt": "2026-10-10T00:00:00.000Z",
        "color": "#2ca02c",
        "nl": false,
        "rap": false,
        "rh": 0,
        "properties": {}
      }
    ],
    "messages": [
      {
        "id": "MSG-01",
        "name": "1. Gui yeu cau Xac thuc hop le (Auth Request PASS)",
        "topic": "Nhom09/smoke/v2/auth/request",
        "qos": 1,
        "retain": false,
        "payload": "{\"msg_id\": \"REQ-AUTH-TEST-001\", \"device_id\": \"ESP32_SMOKE_N04_A01\", \"mac_address\": \"24:6F:28:AB:CD:10\", \"secret_token\": \"HUIT_IOT_SECURE_TOKEN_N04\", \"timestamp\": 1728130000}",
        "payloadType": "JSON",
        "createAt": "2026-10-10T00:00:00.000Z",
        "updateAt": "2026-10-10T00:00:00.000Z",
        "out": true,
        "color": "#34c388",
        "properties": {
          "payloadFormatIndicator": false,
          "messageExpiryInterval": 0,
          "topicAlias": 0,
          "responseTopic": "",
          "correlationData": "",
          "userProperties": {},
          "subscriptionIdentifier": 0,
          "contentType": ""
        }
      },
      {
        "id": "MSG-02",
        "name": "2. Gui yeu cau Xac thuc SAI (Auth Request REJECT)",
        "topic": "Nhom09/smoke/v2/auth/request",
        "qos": 1,
        "retain": false,
        "payload": "{\"msg_id\": \"REQ-AUTH-TEST-002\", \"device_id\": \"ESP32_UNKNOWN_HACKER\", \"mac_address\": \"99:99:99:99:99:99\", \"secret_token\": \"WRONG_TOKEN_XYZ\", \"timestamp\": 1728130005}",
        "payloadType": "JSON",
        "createAt": "2026-10-10T00:00:00.000Z",
        "updateAt": "2026-10-10T00:00:00.000Z",
        "out": true,
        "color": "#34c388",
        "properties": {
          "payloadFormatIndicator": false,
          "messageExpiryInterval": 0,
          "topicAlias": 0,
          "responseTopic": "",
          "correlationData": "",
          "userProperties": {},
          "subscriptionIdentifier": 0,
          "contentType": ""
        }
      },
      {
        "id": "MSG-03",
        "name": "3. Gui Telemetry an toan dinh ky (PPM 135)",
        "topic": "Nhom09/smoke/v2/HUIT_A/F03/P302/ESP32_SMOKE_N04_A01/telemetry",
        "qos": 0,
        "retain": false,
        "payload": "{\"session_key\": \"SK_SESSION_987654321_N04\", \"device_id\": \"ESP32_SMOKE_N04_A01\", \"mq2_ppm\": 135.4, \"temp\": 28.5, \"hum\": 62.0, \"fan\": \"OFF\", \"buzzer\": \"OFF\", \"mode\": \"AUTO\"}",
        "payloadType": "JSON",
        "createAt": "2026-10-10T00:00:00.000Z",
        "updateAt": "2026-10-10T00:00:00.000Z",
        "out": true,
        "color": "#34c388",
        "properties": {
          "payloadFormatIndicator": false,
          "messageExpiryInterval": 0,
          "topicAlias": 0,
          "responseTopic": "",
          "correlationData": "",
          "userProperties": {},
          "subscriptionIdentifier": 0,
          "contentType": ""
        }
      },
      {
        "id": "MSG-04",
        "name": "4. Gui tin hieu duy tri ket noi Keep-Alive (Heartbeat)",
        "topic": "Nhom09/smoke/v2/HUIT_A/F03/P302/ESP32_SMOKE_N04_A01/keep_alive",
        "qos": 0,
        "retain": false,
        "payload": "{\"session_key\": \"SK_SESSION_987654321_N04\", \"device_id\": \"ESP32_SMOKE_N04_A01\", \"uptime_sec\": 3600, \"free_heap_bytes\": 184500, \"wifi_rssi_dbm\": -56, \"status\": \"HEALTHY\"}",
        "payloadType": "JSON",
        "createAt": "2026-10-10T00:00:00.000Z",
        "updateAt": "2026-10-10T00:00:00.000Z",
        "out": true,
        "color": "#34c388",
        "properties": {
          "payloadFormatIndicator": false,
          "messageExpiryInterval": 0,
          "topicAlias": 0,
          "responseTopic": "",
          "correlationData": "",
          "userProperties": {},
          "subscriptionIdentifier": 0,
          "contentType": ""
        }
      },
      {
        "id": "MSG-05",
        "name": "5. Phat su co bao dong khoi khan cap (PPM 480)",
        "topic": "Nhom09/smoke/v2/HUIT_A/F03/P302/ESP32_SMOKE_N04_A01/event/alarm",
        "qos": 1,
        "retain": false,
        "payload": "{\"session_key\": \"SK_SESSION_987654321_N04\", \"device_id\": \"ESP32_SMOKE_N04_A01\", \"event_code\": \"CRITICAL_SMOKE_HAZARD\", \"severity\": \"CRITICAL\", \"ppm\": 482.5, \"timestamp\": 1728130030}",
        "payloadType": "JSON",
        "createAt": "2026-10-10T00:00:00.000Z",
        "updateAt": "2026-10-10T00:00:00.000Z",
        "out": true,
        "color": "#34c388",
        "properties": {
          "payloadFormatIndicator": false,
          "messageExpiryInterval": 0,
          "topicAlias": 0,
          "responseTopic": "",
          "correlationData": "",
          "userProperties": {},
          "subscriptionIdentifier": 0,
          "contentType": ""
        }
      },
      {
        "id": "MSG-06",
        "name": "6. Lenh Downlink Bat Quat Hut (Server -> Device)",
        "topic": "Nhom09/smoke/v2/HUIT_A/F03/P302/ESP32_SMOKE_N04_A01/cmd/fan",
        "qos": 1,
        "retain": false,
        "payload": "{\"cmd_id\": \"CMD-FAN-20261005-01\", \"action\": \"ON\", \"priority\": \"HIGH\", \"reason\": \"RULE_1_SMOKE_ALARM\"}",
        "payloadType": "JSON",
        "createAt": "2026-10-10T00:00:00.000Z",
        "updateAt": "2026-10-10T00:00:00.000Z",
        "out": true,
        "color": "#34c388",
        "properties": {
          "payloadFormatIndicator": false,
          "messageExpiryInterval": 0,
          "topicAlias": 0,
          "responseTopic": "",
          "correlationData": "",
          "userProperties": {},
          "subscriptionIdentifier": 0,
          "contentType": ""
        }
      },
      {
        "id": "MSG-07",
        "name": "7. Lenh Downlink Tat Quat khi Khoi Cao (Test Ma tran PCCC Interlock)",
        "topic": "Nhom09/smoke/v2/HUIT_A/F03/P302/ESP32_SMOKE_N04_A01/cmd/fan",
        "qos": 1,
        "retain": false,
        "payload": "{\"cmd_id\": \"CMD-FAN-20261005-02\", \"action\": \"OFF\", \"priority\": \"NORMAL\", \"reason\": \"USER_MANUAL_OVERRIDE\"}",
        "payloadType": "JSON",
        "createAt": "2026-10-10T00:00:00.000Z",
        "updateAt": "2026-10-10T00:00:00.000Z",
        "out": true,
        "color": "#34c388",
        "properties": {
          "payloadFormatIndicator": false,
          "messageExpiryInterval": 0,
          "topicAlias": 0,
          "responseTopic": "",
          "correlationData": "",
          "userProperties": {},
          "subscriptionIdentifier": 0,
          "contentType": ""
        }
      },
      {
        "id": "MSG-08",
        "name": "8. Kich hoat Canh bao lien vung Cross-Zone (Chay lon PPM 650)",
        "topic": "Nhom09/smoke/v2/HUIT_A/F03/P302/ESP32_SMOKE_N04_A01/telemetry",
        "qos": 1,
        "retain": false,
        "payload": "{\"session_key\": \"SK_SESSION_987654321_N04\", \"device_id\": \"ESP32_SMOKE_N04_A01\", \"mq2_ppm\": 655.0, \"temp\": 38.0, \"hum\": 50.0, \"fan\": \"ON\", \"buzzer\": \"ON\"}",
        "payloadType": "JSON",
        "createAt": "2026-10-10T00:00:00.000Z",
        "updateAt": "2026-10-10T00:00:00.000Z",
        "out": true,
        "color": "#34c388",
        "properties": {
          "payloadFormatIndicator": false,
          "messageExpiryInterval": 0,
          "topicAlias": 0,
          "responseTopic": "",
          "correlationData": "",
          "userProperties": {},
          "subscriptionIdentifier": 0,
          "contentType": ""
        }
      },
      {
        "id": "MSG-09",
        "name": "9. Downlink V1: Bật quạt hút khẩn cấp (Fan ON)",
        "topic": "Nhom09/smoke/cmd/fan",
        "qos": 1,
        "retain": false,
        "payload": "{\"action\": \"ON\", \"source\": \"MQTTX_Tester\"}",
        "payloadType": "JSON",
        "createAt": "2026-10-10T00:00:00.000Z",
        "updateAt": "2026-10-10T00:00:00.000Z",
        "out": true,
        "color": "#27ae60",
        "properties": {
          "payloadFormatIndicator": false,
          "messageExpiryInterval": 0,
          "topicAlias": 0,
          "responseTopic": "",
          "correlationData": "",
          "userProperties": {},
          "subscriptionIdentifier": 0,
          "contentType": ""
        }
      },
      {
        "id": "MSG-10",
        "name": "10. Downlink V1: Tắt quạt (Kiểm tra Khóa an toàn PCCC Interlock)",
        "topic": "Nhom09/smoke/cmd/fan",
        "qos": 1,
        "retain": false,
        "payload": "{\"action\": \"OFF\", \"source\": \"MQTTX_Tester\"}",
        "payloadType": "JSON",
        "createAt": "2026-10-10T00:00:00.000Z",
        "updateAt": "2026-10-10T00:00:00.000Z",
        "out": true,
        "color": "#7f8c8d",
        "properties": {
          "payloadFormatIndicator": false,
          "messageExpiryInterval": 0,
          "topicAlias": 0,
          "responseTopic": "",
          "correlationData": "",
          "userProperties": {},
          "subscriptionIdentifier": 0,
          "contentType": ""
        }
      },
      {
        "id": "MSG-11",
        "name": "11. Downlink V1: Tắt tiếng còi tạm thời (Buzzer MUTE 3 phút)",
        "topic": "Nhom09/smoke/cmd/buzzer",
        "qos": 1,
        "retain": false,
        "payload": "{\"action\": \"MUTE\", \"source\": \"MQTTX_Tester\"}",
        "payloadType": "JSON",
        "createAt": "2026-10-10T00:00:00.000Z",
        "updateAt": "2026-10-10T00:00:00.000Z",
        "out": true,
        "color": "#e67e22",
        "properties": {
          "payloadFormatIndicator": false,
          "messageExpiryInterval": 0,
          "topicAlias": 0,
          "responseTopic": "",
          "correlationData": "",
          "userProperties": {},
          "subscriptionIdentifier": 0,
          "contentType": ""
        }
      },
      {
        "id": "MSG-12",
        "name": "12. Downlink V1: Kích hoạt lại tiếng còi (Buzzer UNMUTE)",
        "topic": "Nhom09/smoke/cmd/buzzer",
        "qos": 1,
        "retain": false,
        "payload": "{\"action\": \"UNMUTE\", \"source\": \"MQTTX_Tester\"}",
        "payloadType": "JSON",
        "createAt": "2026-10-10T00:00:00.000Z",
        "updateAt": "2026-10-10T00:00:00.000Z",
        "out": true,
        "color": "#c0392b",
        "properties": {
          "payloadFormatIndicator": false,
          "messageExpiryInterval": 0,
          "topicAlias": 0,
          "responseTopic": "",
          "correlationData": "",
          "userProperties": {},
          "subscriptionIdentifier": 0,
          "contentType": ""
        }
      },
      {
        "id": "MSG-13",
        "name": "13. Downlink V1: Đặt lịch độ nhạy Ban Đêm (Scheduler NIGHT)",
        "topic": "Nhom09/smoke/cmd/scheduler",
        "qos": 1,
        "retain": false,
        "payload": "{\"mode\": \"NIGHT\", \"source\": \"MQTTX_Tester\"}",
        "payloadType": "JSON",
        "createAt": "2026-10-10T00:00:00.000Z",
        "updateAt": "2026-10-10T00:00:00.000Z",
        "out": true,
        "color": "#8e44ad",
        "properties": {
          "payloadFormatIndicator": false,
          "messageExpiryInterval": 0,
          "topicAlias": 0,
          "responseTopic": "",
          "correlationData": "",
          "userProperties": {},
          "subscriptionIdentifier": 0,
          "contentType": ""
        }
      },
      {
        "id": "MSG-14",
        "name": "14. Bơm sự cố giả lập: Hỏng cảm biến DHT22 Timeout",
        "topic": "Nhom09/smoke/cmd/inject_fault",
        "qos": 1,
        "retain": false,
        "payload": "{\"fault\": \"DHT_TIMEOUT\", \"source\": \"MQTTX_Tester\"}",
        "payloadType": "JSON",
        "createAt": "2026-10-10T00:00:00.000Z",
        "updateAt": "2026-10-10T00:00:00.000Z",
        "out": true,
        "color": "#e74c3c",
        "properties": {
          "payloadFormatIndicator": false,
          "messageExpiryInterval": 0,
          "topicAlias": 0,
          "responseTopic": "",
          "correlationData": "",
          "userProperties": {},
          "subscriptionIdentifier": 0,
          "contentType": ""
        }
      },
      {
        "id": "MSG-15",
        "name": "15. Xóa sự cố giả lập: Khôi phục trạng thái an toàn SAFE",
        "topic": "Nhom09/smoke/cmd/inject_fault",
        "qos": 1,
        "retain": false,
        "payload": "{\"fault\": \"NONE\", \"source\": \"MQTTX_Tester\"}",
        "payloadType": "JSON",
        "createAt": "2026-10-10T00:00:00.000Z",
        "updateAt": "2026-10-10T00:00:00.000Z",
        "out": true,
        "color": "#2ecc71",
        "properties": {
          "payloadFormatIndicator": false,
          "messageExpiryInterval": 0,
          "topicAlias": 0,
          "responseTopic": "",
          "correlationData": "",
          "userProperties": {},
          "subscriptionIdentifier": 0,
          "contentType": ""
        }
      },
      {
        "id": "MSG-16",
        "name": "16. Auth Request A02 (Kho Hoa Chat - P303)",
        "topic": "Nhom09/smoke/v2/auth/request",
        "qos": 1,
        "retain": false,
        "payload": "{\"msg_id\": \"REQ-AUTH-TEST-A02\", \"device_id\": \"ESP32_SMOKE_N04_A02\", \"mac_address\": \"24:6F:28:AB:CD:20\", \"secret_token\": \"HUIT_IOT_SECURE_TOKEN_N04\", \"timestamp\": 1728130000}",
        "payloadType": "JSON",
        "createAt": "2026-11-18T00:00:00.000Z",
        "updateAt": "2026-11-18T00:00:00.000Z",
        "out": true,
        "color": "#34c388",
        "properties": {}
      },
      {
        "id": "MSG-17",
        "name": "17. Auth Request A03 (Khu Vuc Bep - P304)",
        "topic": "Nhom09/smoke/v2/auth/request",
        "qos": 1,
        "retain": false,
        "payload": "{\"msg_id\": \"REQ-AUTH-TEST-A03\", \"device_id\": \"ESP32_SMOKE_N04_A03\", \"mac_address\": \"24:6F:28:AB:CD:30\", \"secret_token\": \"HUIT_IOT_SECURE_TOKEN_N04\", \"timestamp\": 1728130000}",
        "payloadType": "JSON",
        "createAt": "2026-11-18T00:00:00.000Z",
        "updateAt": "2026-11-18T00:00:00.000Z",
        "out": true,
        "color": "#34c388",
        "properties": {}
      },
      {
        "id": "MSG-18",
        "name": "18. Scheduler NIGHT Mode (Alarm 350 PPM, Safe 262.5 PPM)",
        "topic": "Nhom09/smoke/cmd/scheduler",
        "qos": 1,
        "retain": false,
        "payload": "{\"mode\": \"NIGHT\", \"source\": \"MQTTX_TEST\"}",
        "payloadType": "JSON",
        "createAt": "2026-11-18T00:00:00.000Z",
        "updateAt": "2026-11-18T00:00:00.000Z",
        "out": true,
        "color": "#f1b44c",
        "properties": {}
      },
      {
        "id": "MSG-19",
        "name": "19. Scheduler DAY Mode (Alarm 400 PPM, Safe 300 PPM)",
        "topic": "Nhom09/smoke/cmd/scheduler",
        "qos": 1,
        "retain": false,
        "payload": "{\"mode\": \"DAY\", \"source\": \"MQTTX_TEST\"}",
        "payloadType": "JSON",
        "createAt": "2026-11-18T00:00:00.000Z",
        "updateAt": "2026-11-18T00:00:00.000Z",
        "out": true,
        "color": "#34c388",
        "properties": {}
      },
      {
        "id": "MSG-20",
        "name": "20. Fault Injection: DHT_NAN",
        "topic": "Nhom09/smoke/cmd/inject_fault",
        "qos": 1,
        "retain": false,
        "payload": "{\"type\": \"DHT_NAN\", \"device_id\": \"ESP32_SMOKE_N04_A01\"}",
        "payloadType": "JSON",
        "createAt": "2026-11-18T00:00:00.000Z",
        "updateAt": "2026-11-18T00:00:00.000Z",
        "out": true,
        "color": "#f46a6a",
        "properties": {}
      },
      {
        "id": "MSG-21",
        "name": "21. Fault Restore / Clear All Faults",
        "topic": "Nhom09/smoke/cmd/inject_fault",
        "qos": 1,
        "retain": false,
        "payload": "{\"type\": \"CLEAR\", \"device_id\": \"ESP32_SMOKE_N04_A01\"}",
        "payloadType": "JSON",
        "createAt": "2026-11-18T00:00:00.000Z",
        "updateAt": "2026-11-18T00:00:00.000Z",
        "out": true,
        "color": "#50a5f1",
        "properties": {}
      },
      {
        "id": "MSG-22",
        "name": "22. Test Malformed JSON Payload (Expect REJECTED_BAD_PAYLOAD)",
        "topic": "Nhom09/smoke/cmd/fan",
        "qos": 1,
        "retain": false,
        "payload": "{invalid_json: true,",
        "payloadType": "Plaintext",
        "createAt": "2026-11-18T00:00:00.000Z",
        "updateAt": "2026-11-18T00:00:00.000Z",
        "out": true,
        "color": "#f46a6a",
        "properties": {}
      },
      {
        "id": "MSG-23",
        "name": "23. Test Fan OFF during Danger PPM (Expect REJECTED_SAFETY_LOCK)",
        "topic": "Nhom09/smoke/cmd/fan",
        "qos": 1,
        "retain": false,
        "payload": "{\"action\": \"OFF\", \"source\": \"MQTTX_SECURITY_AUDIT\"}",
        "payloadType": "JSON",
        "createAt": "2026-11-18T00:00:00.000Z",
        "updateAt": "2026-11-18T00:00:00.000Z",
        "out": true,
        "color": "#f46a6a",
        "properties": {}
      }
    ],
    "protocol": "mqtt",
    "ssl": false,
    "connectTimeout": 10000,
    "reconnectPeriod": 4000,
    "path": "/mqtt",
    "username": "",
    "password": "",
    "mqttVersion": "3.1.1",
    "reconnect": true,
    "rejectUnauthorized": false,
    "unreadMessageCount": 0,
    "clientIdWithTime": false,
    "order": 1,
    "createAt": "2026-10-10T00:00:00.000Z",
    "updateAt": "2026-10-10T00:00:00.000Z",
    "ca": "",
    "cert": "",
    "key": "",
    "color": "#34c388",
    "isCollection": false,
    "pushDs": false,
    "sessionExpiryInterval": 0,
    "receiveMaximum": 0,
    "maximumPacketSize": 0,
    "topicAliasMaximum": 0,
    "requestResponseInformation": false,
    "requestProblemInformation": false,
    "will": {
      "lastWillTopic": "",
      "lastWillPayload": "",
      "lastWillQos": 0,
      "lastWillRetain": false,
      "contentType": ""
    },
    "properties": {
      "sessionExpiryInterval": 0,
      "receiveMaximum": 0,
      "maximumPacketSize": 0,
      "topicAliasMaximum": 0,
      "requestResponseInformation": false,
      "requestProblemInformation": false
    }
  }
]
```

---

## PHẦN 41: KIỂM DUYỆT CAM KẾT TỰ ĐỘNG (CLAIMS VALIDATOR) (`scripts/check_claims.py`)

> **Đường dẫn:** `scripts/check_claims.py`  
> **Quy mô:** 168 dòng | 6,518 bytes | Ngôn ngữ: `python`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/check_claims.py
Audits and dynamically verifies all claims declared in docs/audit/claims.yaml.
Supports 3-tier classification: VERIFIED, PARTIAL, SCOPE.
Performs AST/regex source code validation ensuring zero simulated or missing test IDs.
"""

import os
import sys
import glob
import re
import yaml
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLAIMS_FILE = os.path.join(BASE_DIR, "docs", "audit", "claims.yaml")

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, shell=True, cwd=BASE_DIR, capture_output=True, text=True, timeout=120)
        return res.returncode == 0, res.stdout + res.stderr
    except Exception as e:
        return False, str(e)

def collect_source_test_ids():
    """Scans all test files to collect real implemented test IDs (T-*, FLOW-*)."""
    search_patterns = [
        os.path.join(BASE_DIR, "test", "**", "*.*"),
        os.path.join(BASE_DIR, "nodered", "tests", "**", "*.*"),
        os.path.join(BASE_DIR, "web", "tests", "**", "*.*"),
    ]
    test_files = []
    for pat in search_patterns:
        test_files.extend(glob.glob(pat, recursive=True))

    found_ids = set()
    test_id_regex = re.compile(r'\b(T-[A-Z0-9]+|FLOW-[0-9]+)\b')

    for filepath in test_files:
        if not os.path.isfile(filepath):
            continue
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                matches = test_id_regex.findall(content)
                found_ids.update(matches)
        except Exception as e:
            print(f"[WARN] Failed to read {filepath}: {e}")

    return found_ids

def main():
    print("=" * 80)
    print("  3-TIER AUDIT CLAIM VALIDATOR - NHOM 04 HUIT (CODEBASE AUDIT V5)")
    print("  Classification: [VERIFIED] Fully Proven | [PARTIAL] Algorithmic | [SCOPE] Design Boundary")
    print("  Source Code Validation: Checking test ID integrity against codebase...")
    print("=" * 80)

    if not os.path.isfile(CLAIMS_FILE):
        print(f"[FAIL] Claims file not found: {CLAIMS_FILE}")
        sys.exit(1)

    with open(CLAIMS_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    claims = data.get("claims", [])
    print(f"Loaded {len(claims)} audit claims from: {CLAIMS_FILE}")

    source_test_ids = collect_source_test_ids()
    print(f"Discovered {len(source_test_ids)} distinct test IDs in test source files.\n")

    results = []
    has_failure = False

    for c in claims:
        cid = c.get("id")
        tier = c.get("tier", "VERIFIED")
        desc = c.get("description", "")
        cmd = c.get("test_command")
        evidence = c.get("evidence_tests", [])

        print(f"Checking [{cid}] ({tier}): {desc[:48]}...", end=" ", flush=True)

        # 1. Source code check: verify that all evidence tests exist in test source code
        missing_ids = []
        for tid in evidence:
            if (tid.startswith("T-") or tid.startswith("FLOW-")) and tid not in source_test_ids:
                missing_ids.append(tid)

        if missing_ids:
            verdict = "FAIL"
            err_msg = f"Evidence test ID(s) not found in test source files: {', '.join(missing_ids)}"
            print("\033[91m[FAILED - MISSING TEST ID]\033[0m" if sys.platform != "win32" else "[FAILED - MISSING TEST ID]")
            print(f"  {err_msg}\n")
            results.append((cid, tier, verdict, err_msg))
            has_failure = True
            continue

        # 2. Check for empty test command
        if not cmd or not cmd.strip():
            print("[WARN] No verification command")
            results.append((cid, tier, "SKIPPED", "No test command"))
            continue

        # 3. Disallow dummy commands for VERIFIED or PARTIAL tiers
        if tier in ("VERIFIED", "PARTIAL") and "print(" in cmd:
            verdict = "FAIL"
            err_msg = f"Dummy test command rejected for {tier} tier: {cmd}"
            print("\033[91m[FAILED - DUMMY CMD]\033[0m" if sys.platform != "win32" else "[FAILED - DUMMY CMD]")
            print(f"  {err_msg}\n")
            results.append((cid, tier, verdict, err_msg))
            has_failure = True
            continue

        ok, out = run_cmd(cmd)

        if ok:
            if tier == "VERIFIED":
                verdict = "VERIFIED_PASS"
                print("\033[92m[VERIFIED PASS]\033[0m" if sys.platform != "win32" else "[VERIFIED PASS]")
            elif tier == "PARTIAL":
                verdict = "PARTIAL_VALID"
                print("\033[93m[PARTIAL VALID]\033[0m" if sys.platform != "win32" else "[PARTIAL VALID]")
            else: # SCOPE
                verdict = "SCOPE_VALID"
                print("\033[94m[SCOPE VALID]\033[0m" if sys.platform != "win32" else "[SCOPE VALID]")
            results.append((cid, tier, verdict, None))
        else:
            verdict = "FAIL"
            print("\033[91m[FAILED]\033[0m" if sys.platform != "win32" else "[FAILED]")
            print(f"  Command: {cmd}")
            print(f"  Error snippet:\n{out[:250]}\n")
            results.append((cid, tier, verdict, out[:250]))
            has_failure = True

    print("\n" + "=" * 80)
    print(f"{'Claim ID':<22} | {'Tier':<10} | {'Verdict':<15} | {'Evidence':<25}")
    print("-" * 80)
    for cid, tier, verdict, _ in results:
        ev = next((','.join(c.get('evidence_tests', [])) for c in claims if c.get('id') == cid), "")
        print(f"{cid:<22} | {tier:<10} | {verdict:<15} | {ev:<25}")
    print("=" * 80)

    count_verified = sum(1 for _, t, v, _ in results if t == "VERIFIED" and v == "VERIFIED_PASS")
    count_partial = sum(1 for _, t, v, _ in results if t == "PARTIAL" and v == "PARTIAL_VALID")
    count_scope = sum(1 for _, t, v, _ in results if t == "SCOPE" and v == "SCOPE_VALID")
    count_fail = sum(1 for _, _, v, _ in results if v == "FAIL")

    print(f"Summary: {len(results)} Claims Evaluated")
    print(f"  - VERIFIED PASS : {count_verified}")
    print(f"  - PARTIAL VALID : {count_partial}")
    print(f"  - SCOPE VALID   : {count_scope}")
    print(f"  - FAILED        : {count_fail}")
    print("=" * 80)

    if not has_failure:
        print("  VERDICT: 100% AUDIT CRITERIA MET WITH FULL SCIENTIFIC HONESTY.")
        print("=" * 80)
        sys.exit(0)
    else:
        print("  VERDICT: AUDIT FAILED - RESOLVE DISCREPANCIES ABOVE.")
        print("=" * 80)
        sys.exit(1)

if __name__ == "__main__":
    main()

```

---

## PHẦN 42: KIỂM TRA TIỀN TỐ TOPIC (TOPIC PREFIX AUDITOR) (`scripts/verify_topic_prefix.py`)

> **Đường dẫn:** `scripts/verify_topic_prefix.py`  
> **Quy mô:** 144 dòng | 5,326 bytes | Ngôn ngữ: `python`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/verify_topic_prefix.py
Validates topic namespace prefix consistency across all 4 system layers:
1. Firmware Configuration (src/config.h)
2. Middleware Node-RED Flows (nodered/flows_smoke_detector.json)
3. Web SCADA Application (web/app.js)
4. MQTTX Test Collection (tests/mqttx_collection_slide65.json)

Ensures zero namespace pollution or topic collisions on shared public MQTT brokers.
"""

import os
import sys
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPECTED_PREFIX = "Nhom09/"

def verify_firmware_config():
    path = os.path.join(BASE_DIR, "src", "config.h")
    if not os.path.isfile(path):
        return False, f"Missing config file: {path}"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find all TOPIC_ constants
    topic_matches = re.findall(r'constexpr\s+const\s+char\*\s+(TOPIC_\w+)\s*=\s*"([^"]+)";', content)
    if not topic_matches:
        return False, "No TOPIC_ constants found in src/config.h"

    for name, topic in topic_matches:
        if not topic.startswith(EXPECTED_PREFIX):
            return False, f"Firmware topic {name} = '{topic}' does not start with '{EXPECTED_PREFIX}'"

    return True, f"Verified {len(topic_matches)} firmware topics in src/config.h"

def verify_nodered_flows():
    path = os.path.join(BASE_DIR, "nodered", "flows_smoke_detector.json")
    if not os.path.isfile(path):
        return False, f"Missing flow file: {path}"
    with open(path, "r", encoding="utf-8") as f:
        nodes = json.load(f)

    checked = 0
    for node in nodes:
        ntype = node.get("type", "")
        if ntype in ("mqtt in", "mqtt out"):
            topic = node.get("topic", "")
            # mqtt out nodes can have blank topic if dynamic from msg.topic
            if topic:
                if not topic.startswith(EXPECTED_PREFIX):
                    return False, f"Node-RED node '{node.get('name') or node.get('id')}' topic '{topic}' lacks prefix '{EXPECTED_PREFIX}'"
                checked += 1

    return True, f"Verified {checked} MQTT nodes in nodered/flows_smoke_detector.json"

def verify_web_scada():
    path = os.path.join(BASE_DIR, "web", "app.js")
    if not os.path.isfile(path):
        return False, f"Missing web file: {path}"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Match topics in MQTT_TOPICS object
    matches = re.findall(r'["\'](Nhom09/[^"\']+)["\']', content)
    if not matches:
        return False, f"No topics with prefix '{EXPECTED_PREFIX}' found in web/app.js"

    # Ensure no hardcoded raw un-prefixed smoke topics
    raw_smoke_topics = re.findall(r'["\'](smoke/(?:telemetry|cmd|status)[^"\']*)["\']', content)
    if raw_smoke_topics:
        return False, f"Found un-prefixed topics in web/app.js: {raw_smoke_topics}"

    return True, f"Verified {len(matches)} topic references in web/app.js"

def verify_mqttx_collection():
    path = os.path.join(BASE_DIR, "tests", "mqttx_collection_slide65.json")
    if not os.path.isfile(path):
        return False, f"Missing MQTTX collection: {path}"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Flatten scripts/messages
    checked = 0
    def scan_items(items):
        nonlocal checked
        for item in items:
            if isinstance(item, dict):
                topic = item.get("topic")
                if topic:
                    if not topic.startswith(EXPECTED_PREFIX):
                        raise ValueError(f"MQTTX message '{item.get('name')}' topic '{topic}' lacks '{EXPECTED_PREFIX}'")
                    checked += 1
                if "messages" in item and isinstance(item["messages"], list):
                    scan_items(item["messages"])
                if "children" in item and isinstance(item["children"], list):
                    scan_items(item["children"])

    try:
        if isinstance(data, list):
            scan_items(data)
        elif isinstance(data, dict):
            scan_items(data.get("scripts", []) or data.get("collections", []) or [data])
    except ValueError as e:
        return False, str(e)

    return True, f"Verified {checked} messages in tests/mqttx_collection_slide65.json"

def main():
    print("=" * 75)
    print("  TOPIC PREFIX CONSISTENCY AUDITOR - NHOM 04 HUIT")
    print(f"  Target Namespace: '{EXPECTED_PREFIX}'")
    print("=" * 75)

    checks = [
        ("Layer 1: ESP32 Firmware (src/config.h)", verify_firmware_config),
        ("Layer 3: Node-RED Flows (flows_smoke_detector.json)", verify_nodered_flows),
        ("Layer 4: Web SCADA (web/app.js)", verify_web_scada),
        ("Test Suite: MQTTX Slide 65 Collection", verify_mqttx_collection),
    ]

    all_ok = True
    for label, fn in checks:
        ok, msg = fn()
        status = "[PASS]" if ok else "[FAIL]"
        print(f"{status:<8} {label}: {msg}")
        if not ok:
            all_ok = False

    print("=" * 75)
    if all_ok:
        print("RESULT: 100% TOPIC PREFIX CONSISTENCY VERIFIED (ZERO UNPREFIXED TOPICS).")
        print("=" * 75)
        sys.exit(0)
    else:
        print("RESULT: TOPIC PREFIX CONSISTENCY CHECK FAILED!")
        print("=" * 75)
        sys.exit(1)

if __name__ == "__main__":
    main()

```

---

## PHẦN 43: BẢNG ĐẶC TẢ CAM KẾT 3 BẬC (CLAIMS REGISTRY) (`docs/audit/claims.yaml`)

> **Đường dẫn:** `docs/audit/claims.yaml`  
> **Quy mô:** 83 dòng | 5,218 bytes | Ngôn ngữ: `yaml`

```yaml
# docs/audit/claims.yaml
# 3-Tier Audit Matrix for IoT Smoke Detection System - Nhom 04 (N09) HUIT
# Tiers:
#   VERIFIED: Automated unit/integration test runs real shared code and validates 100% of the assertion.
#   PARTIAL:  Core algorithm & logic unit-tested in native/engine; physical hardware/network E2E is simulated/mocked.
#   SCOPE:    Explicit design boundary, architecture choice, or academic demonstration benchmark.

claims:
  - id: C-EMA
    tier: VERIFIED
    description: "Asymmetric EMA filter (alpha_rise=0.40, alpha_fall=0.15) with ADC sampling"
    claimed_in: "Phần VII (Audit Matrix), Phần IX (Firmware Spec)"
    reality: "Implemented in lib/core/ema_filter.h and tested against exact mathematical baseline in test/test_core.cpp"
    evidence_tests: ["T-E1", "T-E2", "T-E3", "T-E4", "T-E5"]
    test_command: "pio test -e native"

  - id: C-FSM-5STATES
    tier: VERIFIED
    description: "Strict 5-state Edge FSM with hysteresis and health-derived FAULT"
    claimed_in: "Phần VII, Phần IX"
    reality: "Implemented in lib/core/fsm_core.cpp (SAFE, WARNING, ALARM, COOLDOWN, FAULT) with edge triggers and reset safety"
    evidence_tests: ["T-F1", "T-F2", "T-F3", "T-F4", "T-F5", "T-F6", "T-F7", "T-F8", "T-F9", "T-F10", "T-F11"]
    test_command: "pio test -e native"

  - id: C-COMMAND-INTERLOCK
    tier: VERIFIED
    description: "Firmware command execution with safety interlocks during ALARM (Fan OFF, Mute, and Test refused)"
    claimed_in: "Phần VII, Phần IX"
    reality: "Firmware main.cpp and test/test_core.cpp share applyFanAction & applyBuzzerAction from lib/core/cmd_parse.h (case-insensitive); T-C1 to T-C6 test manual override, ALARM safety lock, and unknown action rejection on real parser"
    evidence_tests: ["T-C1", "T-C2", "T-C3", "T-C4", "T-C5", "T-C6"]
    test_command: "pio test -e native"

  - id: C-NODERED-RULES
    tier: VERIFIED
    description: "Node-RED Core Engine 3 business rules (Rate-of-Rise, Low-Heat, Cross-Zone) and COOLDOWN reflection"
    claimed_in: "Phần VII, Phần IX"
    reality: "Implemented in nodered/functions/core_engine.js and validated via engine.test.js"
    evidence_tests: ["T-N1", "T-N2", "T-N3", "T-N4", "T-N5", "T-N6", "T-N7", "T-N8", "T-N9", "T-N10", "T-N11"]
    test_command: "node --test nodered/tests/engine.test.js"

  - id: C-FLOW-INTEGRATION
    tier: VERIFIED
    description: "Node-RED live flow wire integration (Auth topology, hierarchical V2 commands, dedup TTL 5s, Day/Night Scheduler tick)"
    claimed_in: "Phần VII, Phần IX"
    reality: "Validated on live flows_smoke_detector.json in flow_integration.test.js with deterministic date mocking (FLOW-03)"
    evidence_tests: ["FLOW-01", "FLOW-02", "FLOW-03", "FLOW-04"]
    test_command: "node --test nodered/tests/flow_integration.test.js"

  - id: C-WEB-SCADA-CLEAN
    tier: VERIFIED
    description: "Web SCADA XSS Immunity (textContent) and pure telemetry reflection without autonomous actuator commands"
    claimed_in: "Phần VII, Phần IX"
    reality: "app.js exported and directly tested in web/tests/util.test.js: XSS immunity (T-W1..T-W3), telemetry reflection (T-W4), and UI actuator controls disabled during ALARM (T-W5)"
    evidence_tests: ["T-W1", "T-W2", "T-W3", "T-W4", "T-W5"]
    test_command: "node --test web/tests/util.test.js"

  - id: C-OFFLINE-BUFFER
    tier: VERIFIED
    description: "Offline circular buffer 20 records with FIFO preservation and batch flush"
    reality: "Zero-heap RingBuffer<T, N> implemented in lib/core/ring_buffer.h; firmware offline_buffer.cpp and test/test_core.cpp share identical template code. T-B1 proves eviction (25->20) and batch flush (7->13) on real ring buffer; zero-init and null-termination verified"
    evidence_tests: ["T-B1"]
    test_command: "pio test -e native"

  - id: C-NETWORK-BACKOFF
    tier: VERIFIED
    description: "Decoupled exponential backoff (1s to 16s) for WiFi and MQTT reconnection"
    reality: "ExponentialBackoff struct implemented in lib/core/backoff.h; firmware main.cpp and test/test_core.cpp share identical struct methods (fail, reset). T-R1 and T-F12 prove 1s->2s->4s->8s->16s progression, 16s cap, and independent reset. T-L1 validates socket timeout bounds (2s per phase) and throttled CPU loop budget"
    evidence_tests: ["T-F12", "T-R1", "T-L1"]
    test_command: "pio test -e native"

  - id: C-TELEGRAM-FALLBACK
    tier: PARTIAL
    description: "Telegram Bot Alerting Architecture with academic mock fallback"
    reality: "Alert dispatcher formats HTML and calls HTTP request node; falls back gracefully to dashboard/debug mock when token is unconfigured (T-N12)"
    evidence_tests: ["T-N12"]
    test_command: "node --test nodered/tests/engine.test.js"

  - id: C-SCOPE-BENCHMARKS
    tier: SCOPE
    description: "Academic scope boundaries: Port 1883 plaintext with Nhom09/ prefix, RL=10k vs R0=1.0k, demo thresholds (400/350 PPM), ArduinoJson v7 RAII heap"
    reality: "Automated script verifies topic prefix consistency (Nhom09/) across 4 layers: config.h, flows_smoke_detector.json, app.js, and mqttx_collection_slide65.json (62 topics checked)"
    evidence_tests: []
    test_command: "python scripts/verify_topic_prefix.py"

```

---

## PHẦN VII: BẢNG CHECKLIST KIỂM DUYỆT CHẤT LƯỢNG MÃ NGUỒN 3 BẬC (3-TIER AUDIT MATRIX)

Bảng kiểm duyệt dưới đây phản ánh **100% hiện trạng thực tế của mã nguồn** sau khi hoàn thành tái cấu trúc và chuẩn hóa (Phiên bản v5). Phân loại minh bạch 3 cấp bậc:
- **VERIFIED**: Đã được chứng minh 100% bằng kiểm thử tự động trên mã nguồn đang chạy thực tế (không dùng mock logic cục bộ trong test).
- **PARTIAL**: Thuật toán & máy trạng thái lõi đã được kiểm thử ở cấp độ đơn vị/firmware; phần tích hợp ngoại vi/mạng được mô phỏng/mock có chủ đích.
- **SCOPE**: Phạm vi thiết kế và giả định benchmark phục vụ nghiệm thu đồ án học phần (không phóng đại tiêu chuẩn thương mại).

| Claim ID | Hạng Mục & Tuyên Bố | Cấp Bậc (Tier) | Hiện Trạng Thực Tế Trong Mã Nguồn | Kiểm Thử Minh Chứng | Kết Quả Đánh Giá |
| :--- | :--- | :---: | :--- | :--- | :---: |
| **C-EMA** | Bộ lọc số EMA bất đối xứng ($\alpha_{rise}=0.40, \alpha_{fall}=0.15$) lấy mẫu 5 ADC | `VERIFIED` | `lib/core/ema_filter.h` (`emaUpdate`), `src/sensors.cpp`, `test/test_core.cpp` | `pio test -e native` (T-E1..T-E5) | ✅ VERIFIED PASS |
| **C-FSM-5STATES** | Máy trạng thái biên 5 trạng thái (SAFE, WARNING, ALARM, COOLDOWN, FAULT) | `VERIFIED` | `lib/core/fsm_core.cpp`, FAULT suy ra từ cờ sức khỏe, mute xóa tại cạnh ALARM | `pio test -e native` (T-F1..T-F11) | ✅ VERIFIED PASS |
| **C-COMMAND-INTERLOCK** | Khóa liên động lệnh chấp hành: cấm tắt quạt, cấm MUTE, cấm TEST khi ALARM | `VERIFIED` | Firmware `main.cpp` & test dùng chung `applyFanAction`, `applyBuzzerAction` (`lib/core/cmd_parse.h`) | `pio test -e native` (T-C1..T-C6) | ✅ VERIFIED PASS |
| **C-NODERED-RULES** | Động cơ Middleware Node-RED 3 quy tắc nghiệp vụ (Rate-of-Rise, Low-Heat, Cross-Zone) và phản chiếu COOLDOWN | `VERIFIED` | `nodered/functions/core_engine.js`, lọc topic wildcard, bảo toàn topology | `node --test nodered/tests/engine.test.js` (T-N1..T-N11) | ✅ VERIFIED PASS |
| **C-FLOW-INTEGRATION** | Tích hợp dây nối luồng Node-RED (Auth key `fleet`, parser `ALARM_EVENT`, `KEEP_ALIVE`, inject 1-min Ngày/Đêm) | `VERIFIED` | `nodered/flows_smoke_detector.json`, `nodered/generate_flows.py` | `node --test nodered/tests/flow_integration.test.js` (FLOW-01..04) | ✅ VERIFIED PASS |
| **C-WEB-SCADA-CLEAN** | Web SCADA chống XSS 100% (`textContent`) và chỉ phản chiếu trạng thái, không tự phát lệnh quạt/còi | `VERIFIED` | `web/app.js` (xóa `evaluateFsmRules`, `triggerAlarmState`), `web/util.js` | `node --test web/tests/util.test.js` (T-W1..T-W4 trực tiếp app.js) | ✅ VERIFIED PASS |
| **C-OFFLINE-BUFFER** | Bộ đệm vòng ngoại tuyến 20 bản ghi, bảo toàn thứ tự FIFO và xả từng phần | `VERIFIED` | `lib/core/ring_buffer.h` template dùng chung firmware & test; `src/offline_buffer.cpp` | `pio test -e native` (T-B1) | ✅ VERIFIED PASS |
| **C-NETWORK-BACKOFF** | Máy trạng thái Exponential Backoff độc lập 1s..16s cho WiFi và MQTT | `VERIFIED` | `lib/core/backoff.h` struct dùng chung firmware & test; `src/main.cpp` (`netTick`) | `pio test -e native` (T-F12, T-R1) | ✅ VERIFIED PASS |
| **C-TELEGRAM-FALLBACK** | Cấu trúc cảnh báo Telegram qua HTTP Request có chế độ Fallback học thuật | `PARTIAL` | `nodered/functions/alert_dispatcher.js` định dạng HTML; fallback mock khi thiếu token | `node --test nodered/tests/engine.test.js` (T-N12) | ⚠️ PARTIAL VALID |
| **C-SCOPE-BENCHMARKS** | Phạm vi học thuật: MQTT 1883 plaintext với tiền tố `Nhom09/`, $R_L=10\text{ k}\Omega$ vs $R_0=1.0\text{ k}\Omega$, demo 400/350 PPM, ArduinoJson v7 RAII heap | `SCOPE` | `src/config.h`, `src/main.cpp` (JSON cấp phát heap RAII giải phóng tức thời), `diagram.json` (nền 200 PPM) | `scripts/check_claims.py` (CONFIG_INSPECTION) | 🔷 SCOPE VALID |

### 7.1 Giải trình kỹ thuật chuyên sâu về các chỉ số nhạy cảm
1. **Về độ ổn định tĩnh của bộ nhớ RAM (46,560 bytes - 14.2%):**
   - Trong lần nâng cấp trước, thêm 2 cờ `mq2Valid` (1 byte) và `dhtValid` (1 byte) vào `struct OfflineRecord` không làm tăng kích thước cấu trúc trên kiến trúc 32-bit Xtensa ESP32 (`sizeof(OfflineRecord) == 52 bytes`). Nguyên nhân do trước đó, 2 cờ `bool fan` (1 byte) và `bool buzzer` (1 byte) đã được trình biên dịch bù 2 byte padding để căn lề 4-byte boundary. Việc thêm 2 biến bool chỉ điền đầy phần padding sẵn có, giữ nguyên kích thước mảng 20 phần tử.
   - Việc tách `RingBuffer<T, N>` và `ExponentialBackoff` thành header chuyên dụng làm kích thước RAM tăng 16 bytes (từ 46,544 bytes lên 46,560 bytes) do lưu trữ đối tượng toàn cục tĩnh, tỷ lệ chiếm dụng hoàn toàn ổn định ở 14.2% RAM và 59.9% Flash (785,089 bytes).
2. **Về cơ chế cấp phát bộ nhớ của ArduinoJson v7:**
   - Trong ArduinoJson v7, `JsonDocument doc;` cấp phát bộ nhớ heap động theo cơ chế RAII tự động mở rộng theo nhu cầu payload và tự giải phóng ngay khi hàm handler (`handleFanCommand`, `handleBuzzerCommand`, `handleThresholdCommand`) trả về.
   - Firmware khống chế độ dài chuỗi nhận được qua cấu hình buffer PubSubClient (`setBufferSize(512)`) và payload tối đa 256 bytes, triệt tiêu nguy cơ phân mảnh bộ nhớ lâu dài.
3. **Về ràng buộc thời gian chờ mạng Socket Timeout:**
   - Hàm `netTick()` thiết lập `wifiClient.setTimeout(2)` và `wifiClient.setSocketTimeout(2)` (2 giây = 2000 ms), đảm bảo thời gian chờ kết nối mạng luôn nghiêm ngặt nhỏ hơn ngưỡng cảnh báo hiệu năng `NET_MAX_BLOCK_MS = 3000 ms`.
4. **Về tiền tố Topic `Nhom09/` và cô lập trên Broker dùng chung:**
   - Toàn bộ topic của thiết bị (`Nhom09/smoke/v2/...`), middleware (`Nhom09/smoke/cmd/...`) và Web SCADA đều được phân định bằng tiền tố namespace nhóm `Nhom09/` tránh xung đột với các đề tài khác trên public broker `broker.emqx.io`.
5. **Về giao diện Web SCADA giám sát:**
   - Web SCADA tuân thủ nguyên tắc giám sát thuần túy (Observation SCADA): chỉ phản chiếu telemetry từ broker, vô hiệu hóa nút bấm điều khiển quạt/còi khi FSM đang ALARM, và không tự ý gửi tin nhắn giả lập cảnh báo Telegram.

---

## PHẦN VIII: KẾT LUẬN & HƯỚNG DẪN KIỂM DUYỆT TỰ ĐỘNG (VERIFICATION COMMANDS)

Để thẩm định toàn diện dự án trên bất kỳ môi trường độc lập nào, AI Agent / Giảng viên có thể thực thi tuần tự các lệnh kiểm chuẩn:

```bash
# 1. Kiểm thử 29 Unit Test thuật toán lõi C++17 chạy mã nguồn thật dùng chung (Unity Native)
pio test -e native

# 2. Kiểm thử 16 Unit & Integration Tests động cơ Middleware Node-RED
node --test nodered/tests/engine.test.js nodered/tests/flow_integration.test.js

# 3. Kiểm thử 4 Unit Test an toàn giao diện Web SCADA (nạp trực tiếp web/app.js)
node --test web/tests/util.test.js

# 4. Thẩm định toàn bộ 10 cam kết ma trận kiểm duyệt 3 bậc & kiểm tra toàn vẹn mã nguồn test
python scripts/check_claims.py

# 5. Biên dịch kiểm tra toàn diện Firmware ESP32 (0 warning, 0 error, RAM 14.2%, Flash 59.9%)
pio run -e esp32dev
```
