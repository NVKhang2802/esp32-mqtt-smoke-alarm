# Kế hoạch khắc phục và chuẩn hóa dự án Báo khói IoT (v5)

Đề tài 04 · Nhóm 09 (N09) · HUIT. Bản thiết kế lại, hợp nhất plan v1–v4 và các vòng đánh giá; thay thế hoàn toàn các bản trước. Cập nhật 17/11/2026.

## 0. Cách dùng tài liệu

- Đây là bản hợp nhất đầy đủ, không phải bản thay đổi so với v4. Agent chỉ cần làm theo tài liệu này.
- Mỗi lỗi có mã F-xx, mỗi test có mã T-xx; bảng truy vết ở mục 13.
- Số liệu hiện trạng lấy từ snapshot cũ của repo. Phase 0 bắt buộc đối chiếu lại repo thật; chỗ nào khác snapshot thì ghi chú và điều chỉnh, không đoán.
- Code mẫu là đặc tả hành vi, phải biên dịch được và qua test; không dán máy móc.
- Không ghi PASS vào Audit Matrix cho mục nào chưa có test chạy qua.

## 1. Nguyên tắc thiết kế (bất biến)

| # | Nguyên tắc | Hệ quả khi thiết kế |
| :-: | :-- | :-- |
| P1 | Thiết bị biên tự chủ | Khói vượt ngưỡng thì còi và quạt bắt buộc bật; không lệnh từ xa nào tắt được |
| P2 | Cloud chỉ leo thang | Node-RED/Web được bật quạt, UNMUTE, thông báo, phát sơ tán; không MUTE, không tắt quạt |
| P3 | An toàn không phụ thuộc mạng | Vòng an toàn không bị chặn quá 3 giây khi broker hoặc WiFi hỏng |
| P4 | Một nguồn sự thật | Firmware quyết định trạng thái và ngưỡng; Node-RED và Web phản chiếu, không tự dựng lại FSM |
| P5 | Tài liệu chỉ nói điều code làm và test chứng minh | Audit Matrix sinh từ bảng claim có kiểm tra tự động (mục 11) |
| P6 | Logic thuần tách khỏi phần cứng | FSM, EMA, ngưỡng, health nằm trong lib/core và test native; phần cứng chỉ là lớp mỏng |

## 2. Bảng ưu tiên điều khiển

Giải quyết xung đột giữa luật an toàn cục bộ và lệnh ghi đè từ xa. Đưa nguyên bảng này vào báo cáo.

| Ưu tiên | Nguồn | Được làm | Không được làm |
| :-: | :-- | :-- | :-- |
| 1 | Khói ≥ ngưỡng báo động (MQ-2 hợp lệ) | Ép còi và quạt, chốt ALARM | — |
| 2 | Lỗi MQ-2 | Quạt bật, còi beep 200ms/1800ms; đang ALARM thì giữ ALARM liên tục | Dùng PPM của cảm biến hỏng để quyết định |
| 3 | Nút bấm tại chỗ | Xác nhận (tắt còi 60s, quạt giữ ON) khi ALARM hoặc FAULT; bật/tắt quạt khi bình thường | Tắt quạt khi ALARM |
| 4 | Lệnh MQTT từ xa | Quạt ON/AUTO; OFF, mute, test còi khi chưa ALARM; scheduler | Mute, tắt quạt, test còi khi đang ALARM; đặt ngưỡng ngoài 300–400 |
| 5 | Luật Node-RED | Bật quạt, UNMUTE, thông báo, sơ tán liên vùng | MUTE, tắt quạt, hạ trạng thái do thiết bị báo |

## 3. Quyết định kỹ thuật đã chốt

| # | Quyết định | Lý do |
| :-: | :-- | :-- |
| D1 | FSM firmware có 5 trạng thái: SAFE, WARNING, ALARM, COOLDOWN, FAULT. OFFLINE do Node-RED/Web suy ra từ LWT và watchdog | Firmware không tự biết mình offline |
| D2 | Ngưỡng qua một hàm duy nhất `makeThresholds(alarm)`: alarm kẹp \[300..400\], safe = 0.75 × alarm. Ngày 400/300, đêm 350/262.5; bỏ hằng `SAFE_PPM_NIGHT` | Nền Wokwi 200 PPM nên safe ≥ 225 không bị kẹt; chỉ cho hạ ngưỡng |
| D3 | EMA bất đối xứng α\_rise 0.40, α\_fall 0.15; đóng băng khi MQ-2 lỗi; reset bằng mẫu thật khi hồi phục | Số liệu công bố theo công thức, nêu rõ nền |
| D4 | Lỗi MQ-2: vào lỗi khi ADC < 30 hai mẫu liên tiếp (giả lập: ngay), thoát sau 3 mẫu tốt; bỏ điều kiện ADC > 4080 | Khói đặc làm ADC chạm trần, không phải đứt dây |
| D5 | Lỗi DHT22: ≥ 3 lần đọc hỏng liên tiếp (NaN hoặc ngoài −10..85°C) thì `dhtFault` và vào WARNING; không ép quạt, không chặn báo khói | Nhiệt độ không quyết định báo khói; giữ giá trị cũ sẽ không bao giờ phát hiện lỗi |
| D6 | ALARM chốt: vào khi ≥ alarm (MQ-2 hợp lệ), giữ tới ≤ safe, rồi COOLDOWN 30s; hết cooldown: PPM > safe thì WARNING (không ALARM), ngược lại SAFE | ALARM chỉ khi vượt ngưỡng báo động |
| D7 | Mute chỉ bị xóa ở cạnh vào ALARM. Mute từ xa 180s chỉ nhận khi chưa chốt ALARM. Nút tại chỗ xác nhận 60s (ALARM hoặc FAULT), quạt giữ ON, hết hạn còi tự kêu lại | Bản v4 xóa mute mỗi chu kỳ nên nút bấm vô hiệu |
| D8 | Hai backoff độc lập 1→16s; WiFi chỉ thử lại sau timeout 10s; MQTT connect timeout ≤ 2s; đo độ trễ vòng lặp, nếu > 3s thì tách FreeRTOS task | `PubSubClient.connect` là hàm chặn |
| D9 | Node-RED giữ trạng thái theo từng thiết bị, phản chiếu `fsm_state` và ngưỡng do thiết bị báo, chỉ leo thang. Code function nằm trong `nodered/functions/*.js`, `generate_flows.py` nhúng vào | Test chạy đúng code thật |
| D10 | Telegram: mặc định mock (khung chat Web + debug); gửi thật khi có biến môi trường `TELEGRAM_TOKEN` và `TELEGRAM_CHAT_ID`. Tài liệu ghi đúng như vậy | Không phụ thuộc token khi chấm |
| D11 | Phạm vi bảo mật học thuật: broker công cộng cổng 1883, token là demo. Khuyến nghị đổi tiền tố topic thành `Nhom09-N09-<hậu tố riêng>`; chỉ chấp nhận auth response gửi tới đúng `DEVICE_ID` | Không tuyên bố TLS hay RBAC thật |
| D12 | Công thức ADC `adc/4095 × 5.0` tương đương hệ số 1.515, xấp xỉ cầu phân áp 10k/20k (1.5) với ADC 0–3.3V, nên đúng cho mạch thật có cầu. `diagram.json` không có cầu: ghi chú khác biệt mô phỏng/thực tế; ADC ESP32 phi tuyến gần đỉnh. Đính chính: nhận xét trước đây cho rằng công thức này sai khi có cầu phân áp là không chính xác | Tài liệu trung thực |

## 4. Cấu trúc mã nguồn mục tiêu

```
lib/core/               thuần C++, không include Arduino.h
  thresholds.h  ema_filter.h  health.h  netutil.h  fsm_core.h  fsm_core.cpp
src/
  config.h  hal_sensors.*  hal_buzzer.*  commands.*  net.*  offline_buffer.*  main.cpp
test/native/              Unity: thresholds, ema, health, fsm, commands
nodered/functions/*.js    nguồn duy nhất của function node
nodered/generate_flows.py nhúng các file .js vào flow
nodered/tests/*.test.js   node --test, nạp đúng file .js
web/util.js               escapeHtml và các hàm thuần
scripts/check_claims.py   kiểm tra claim trong Audit Matrix
```

Thêm vào `platformio.ini`:

```ini
[env:native]
platform = native
test_framework = unity
build_flags = -std=c++17 -Ilib/core
test_build_src = no
```

## 5. Phase 0 — Chuẩn bị (≈ 2h)

1. Tạo nhánh `audit-fix-v5`, gắn tag `before-audit`.
2. Đối chiếu repo thật với snapshot: `fsm.cpp`, `sensors.cpp`, `main.cpp`, `generate_flows.py`, `app.js`. Ghi khác biệt vào `docs/audit/snapshot_diff.md`.
3. Chạy `python run_all_tests.py --all`, lưu kết quả gốc (63 test). Đánh dấu test nào đang mô tả hành vi cũ (Rule 2 MUTE, EMA < 196, backoff).
4. Thêm `[env:native]`, chạy một test mẫu.
5. Đo baseline: khi broker không tới được, ghi độ trễ lớn nhất giữa hai vòng `loop()` trong 60 giây. Số này quyết định D8.

Điều kiện xong: có tag, `snapshot_diff.md`, kết quả baseline, và `pio test -e native` chạy được.

## 6. Phase 1 — Lõi logic thuần (≈ 6h, viết test trước)

### 6.1 Ngưỡng, EMA, health, tiện ích

```cpp
// lib/core/thresholds.h
struct Thresholds { float alarm; float safe; };
constexpr float ALARM_MIN_PPM = 300.0f;
constexpr float ALARM_MAX_PPM = 400.0f;          // = DEFAULT_ALARM_PPM_DAY
inline Thresholds makeThresholds(float req) {
  if (req != req) req = ALARM_MAX_PPM;           // NaN
  const float a = req < ALARM_MIN_PPM ? ALARM_MIN_PPM : (req > ALARM_MAX_PPM ? ALARM_MAX_PPM : req);
  return { a, a * 0.75f };
}

// lib/core/ema_filter.h
struct EmaFilter { float value = -1.0f; };
inline float emaUpdate(EmaFilter& f, float raw, float aRise = 0.40f, float aFall = 0.15f) {
  if (f.value < 0.0f) { f.value = raw; return raw; }
  f.value += (raw > f.value ? aRise : aFall) * (raw - f.value);
  return f.value;
}
inline void emaReset(EmaFilter& f, float raw) { f.value = raw; }

// lib/core/health.h
struct Mq2Health { bool fault = false; uint8_t bad = 0, good = 0; };
enum HealthEvent : uint8_t { HE_NONE, HE_FAULT_ENTER, HE_RECOVERED };
inline HealthEvent mq2Update(Mq2Health& h, int rawAdc, bool simFault, uint8_t enterN, uint8_t exitN) {
  const bool broken = simFault || rawAdc < 30;    // KHONG co dieu kien > 4080
  if (broken) {
    h.good = 0;
    if (!h.fault && ++h.bad >= (simFault ? 1 : enterN)) { h.fault = true; return HE_FAULT_ENTER; }
    return HE_NONE;
  }
  h.bad = 0;
  if (h.fault && ++h.good >= exitN) { h.fault = false; h.good = 0; return HE_RECOVERED; }
  return HE_NONE;
}
struct DhtHealth { bool fault = false; uint8_t fails = 0; };
inline void dhtOnRead(DhtHealth& h, bool ok, float t, bool simFault) {
  const bool good = ok && !simFault && t >= -10.0f && t <= 85.0f;
  if (good) { h.fails = 0; h.fault = false; }
  else { if (h.fails < 255) h.fails++; if (h.fails >= 3) h.fault = true; }
}

// lib/core/netutil.h
inline uint32_t nextBackoff(uint32_t cur, uint32_t maxMs = 16000) { return cur * 2 > maxMs ? maxMs : cur * 2; }
```

### 6.2 FSM thuần và lệnh có interlock

FSM không gọi phần cứng: nhận đầu vào, trả về đầu ra mong muốn (quạt, kiểu còi). Mute được áp dụng trong FSM.

```cpp
// lib/core/fsm_core.h
#include <stdint.h>
#include <thresholds.h>
enum SystemState : uint8_t { STATE_SAFE, STATE_WARNING, STATE_ALARM, STATE_COOLDOWN, STATE_FAULT };
enum BuzzerMode  : uint8_t { BUZZ_OFF, BUZZ_ALARM, BUZZ_FAULT_BEEP };
enum CmdResult   : uint8_t { CMD_OK, CMD_REJECTED_SAFETY_LOCK };
constexpr uint32_t COOLDOWN_MS = 30000, LOCAL_ACK_MS = 60000, REMOTE_MUTE_MS = 180000;

struct FsmContext {
  SystemState state = STATE_SAFE;
  bool alarmLatched = false, cooldownActive = false;
  uint32_t cooldownStartMs = 0;
  bool muted = false;  uint32_t muteUntilMs = 0;
  bool manualMode = false, manualFan = false;     // manualMode=false nghia la AUTO
};
struct FsmInput  { float ppm; bool mq2Fault; bool dhtFault; uint32_t nowMs; };
struct FsmOutput { bool fanOn; BuzzerMode buzzer; bool buzzerMuted; };
struct BuzzerCmd { bool on; uint32_t freqHz; };

FsmOutput fsmStep(FsmContext& c, const FsmInput& in, const Thresholds& th);
inline BuzzerCmd buzzerPattern(BuzzerMode m, uint32_t nowMs) {
  switch (m) {
    case BUZZ_ALARM:      return { true, 800 };
    case BUZZ_FAULT_BEEP: return { (nowMs % 2000) < 200, 1000 };
    default:              return { false, 0 };
  }
}

// Lenh co interlock (dung chung cho MQTT va nut bam)
inline CmdResult cmdRemoteMute(FsmContext& c, uint32_t now) {
  if (c.alarmLatched) return CMD_REJECTED_SAFETY_LOCK;
  c.muted = true; c.muteUntilMs = now + REMOTE_MUTE_MS; return CMD_OK;
}
inline void cmdRemoteUnmute(FsmContext& c) { c.muted = false; }
inline CmdResult cmdRemoteFanOff(FsmContext& c) {
  if (c.alarmLatched) return CMD_REJECTED_SAFETY_LOCK;
  c.manualMode = true; c.manualFan = false; return CMD_OK;
}
inline void cmdRemoteFanOn(FsmContext& c) { c.manualMode = true; c.manualFan = true; }
inline void cmdFanAuto(FsmContext& c) { c.manualMode = false; c.manualFan = false; }
inline CmdResult cmdBuzzerTest(const FsmContext& c) { return c.alarmLatched ? CMD_REJECTED_SAFETY_LOCK : CMD_OK; }
// true = da xac nhan tai cho (tat coi 60s); false = da dao trang thai quat
inline bool cmdLocalButton(FsmContext& c, uint32_t now) {
  if (c.alarmLatched || c.state == STATE_FAULT) { c.muted = true; c.muteUntilMs = now + LOCAL_ACK_MS; return true; }
  c.manualMode = true; c.manualFan = !c.manualFan; return false;
}
```

```cpp
// lib/core/fsm_core.cpp
#include <fsm_core.h>
static bool reached(uint32_t now, uint32_t t) { return (int32_t)(now - t) >= 0; }
static FsmOutput out(const FsmContext& c, bool forceFan, BuzzerMode m) {
  FsmOutput o;
  o.fanOn = forceFan || (c.manualMode && c.manualFan);
  o.buzzerMuted = c.muted && m != BUZZ_OFF;
  o.buzzer = o.buzzerMuted ? BUZZ_OFF : m;
  return o;
}
FsmOutput fsmStep(FsmContext& c, const FsmInput& in, const Thresholds& th) {
  if (c.muted && reached(in.nowMs, c.muteUntilMs)) c.muted = false;

  // 1. Dang chot ALARM: giu toi khi khoi <= safe; mat cam bien van giu
  if (c.alarmLatched) {
    if (in.mq2Fault || in.ppm > th.safe) { c.state = STATE_ALARM; return out(c, true, BUZZ_ALARM); }
    c.alarmLatched = false; c.cooldownActive = true; c.cooldownStartMs = in.nowMs;
    c.state = STATE_COOLDOWN;
    return out(c, true, BUZZ_OFF);
  }
  // 2. Vao ALARM (chi khi MQ-2 hop le). Xoa mute CHI o canh vao
  if (!in.mq2Fault && in.ppm >= th.alarm) {
    c.alarmLatched = true; c.cooldownActive = false; c.muted = false;
    c.state = STATE_ALARM;
    return out(c, true, BUZZ_ALARM);
  }
  // 3. Loi MQ-2 (chua ALARM): fail-safe
  if (in.mq2Fault) { c.cooldownActive = false; c.state = STATE_FAULT; return out(c, true, BUZZ_FAULT_BEEP); }
  // 4. Cooldown
  if (c.cooldownActive) {
    if (in.nowMs - c.cooldownStartMs < COOLDOWN_MS) { c.state = STATE_COOLDOWN; return out(c, true, BUZZ_OFF); }
    c.cooldownActive = false;
  }
  // 5. WARNING / SAFE
  c.state = (in.ppm > th.safe || in.dhtFault) ? STATE_WARNING : STATE_SAFE;
  return out(c, false, BUZZ_OFF);
}
```

## 7. Test lõi native (Unity)

Nền 200 PPM, ngưỡng ngày 400 trừ khi ghi khác. Viết test trước rồi mới sửa tới khi qua.

| Mã | Kịch bản | Kết quả mong đợi |
| :-: | :-- | :-- |
| T-TH1 | `makeThresholds` với 250, 500, 350, NaN | 300/225; 400/300; 350/262.5; 400/300 |
| T-E1 | Xung 1 mẫu 690 rồi về 200; xung 710 | EMA tối đa 396 (< 400); 404 (≥ 400) |
| T-E2 | Bước 600 PPM giữ nguyên | 360 rồi 456: vượt 400 ở mẫu 2 (≤ 4s) |
| T-E3 | Bước 500; bước 450 | Vượt ở mẫu 3 (435.2); mẫu 4 (417.6) |
| T-E4 | Ngưỡng đêm 350: xung 570; 580 | 348 (không báo); 352 (báo) |
| T-E5 | EMA 450, lỗi 5 chu kỳ không cập nhật, hồi phục `emaReset(450)` | `fsmStep` vào ALARM ngay chu kỳ đó |
| T-H1 | ADC 4095 liên tục | Không bao giờ lỗi MQ-2 |
| T-H2 | ADC 10 hai mẫu liên tiếp; rồi 3 mẫu tốt | `HE_FAULT_ENTER` ở mẫu 2; `HE_RECOVERED` ở mẫu tốt thứ 3; mẫu lẻ không đổi trạng thái |
| T-H3 | DHT: 3 lần hỏng liên tiếp; 1 lần tốt | `fault` bật; rồi tắt ngay |
| T-F1 | ALARM ở 450, xuống 350, rồi 299 | Giữ ALARM ở 350; vào COOLDOWN ở 299 |
| T-F2 | COOLDOWN, PPM 350 suốt 30s; một lần khác PPM 280 | Hết 30s: WARNING; lần sau: SAFE. Trong lúc purge không đổi trạng thái |
| T-F3 | COOLDOWN rồi PPM 450 | Vào ALARM, còi bật |
| T-F4 | `mq2Fault`, PPM rác 1000 | STATE\_FAULT, còi BUZZ\_FAULT\_BEEP, không ALARM |
| T-F5 | Đang ALARM rồi `mq2Fault` | Giữ ALARM, còi BUZZ\_ALARM liên tục |
| T-F6 | `dhtFault` + 450 PPM; `dhtFault` một mình | ALARM; WARNING |
| T-F7 | Mute từ xa ở 350 (WARNING) rồi PPM lên 450 | Mute được nhận; vào ALARM thì còi kêu (mute đã bị xóa) |
| T-F8 | Đang ALARM: `cmdRemoteMute`, `cmdRemoteFanOff`, `cmdBuzzerTest` | Cả ba CMD\_REJECTED\_SAFETY\_LOCK |
| T-F9 | `cmdLocalButton` trong ALARM, PPM ≥ 400 qua nhiều chu kỳ | Còi tắt suốt 60s dù PPM cao, quạt ON; sau 60s còi kêu lại; ghi nhận ở cả khi `millis()` tràn số |
| T-F10 | `cmdLocalButton` trong FAULT | Beep tắt 60s |
| T-F11 | `buzzerPattern(BUZZ_FAULT_BEEP, t)` với t = 0, 199, 200, 1999, 2000 | on, on, off, off, on |
| T-F12 | `nextBackoff` từ 1000 | 2000, 4000, 8000, 16000, 16000 |

## 8. Phase 2 — Tích hợp firmware (≈ 7h)

Điều chỉnh mục 6.1: trong `dhtOnRead`, nếu `simFault` thì bật `fault` ngay (giống nhánh MQ-2) và thêm ca này vào T-H3.

### 8.1 Thay đổi `config.h`

| Mục | Giá trị / quy tắc |
| :-- | :-- |
| `DEVICE_ID` | Định danh ứng dụng, dùng trong payload, auth, LWT. Không dùng làm MQTT client id: client id giữ hậu tố ngẫu nhiên để hai phiên (ví dụ hai thành viên cùng chạy Wokwi) không đá nhau |
| `SAMPLE_MS` | 2000 |
| `MQ2_ENTER_N`, `MQ2_EXIT_N` | 2 và 3 |
| `WIFI_ATTEMPT_TIMEOUT_MS` | 10000 |
| `NET_MAX_BLOCK_MS` | 3000 (tiêu chí nghiệm thu T-L1) |
| Giữ | `ALARM_PPM_NIGHT = 350`; `DEFAULT_ALARM_PPM_DAY = 400` |
| Bỏ | `SAFE_PPM_NIGHT`, điều kiện `rawADC > 4080`, mọi nơi gán `STATE_OFFLINE` trong firmware |

### 8.2 Vòng lặp chính

```cpp
void loop() {
  const uint32_t now = millis();
  netTick(now);                       // khong chan qua NET_MAX_BLOCK_MS
  buttonTick(now);                    // debounce -> cmdLocalButton -> ack -> recompute()
  buzzerTick(g_out.buzzer, now);      // moi vong; chi ghi LEDC khi doi trang thai
  fanApply(g_out.fanOn);

  if (now - g_lastSample >= SAMPLE_MS) {
    g_lastSample = now;
    const SystemState prev = g_fsm.state;            // lay TRUOC khi chan doan
    const int   adc = analogRead(MQ2_PIN);
    const float raw = readMQ2PPM(g_cfg, g_r0);
    const HealthEvent ev = mq2Update(g_mq2h, adc, g_simMq2, MQ2_ENTER_N, MQ2_EXIT_N);
    if (ev == HE_RECOVERED) emaReset(g_ema, raw);
    if (!g_mq2h.fault) g_ppm = emaUpdate(g_ema, raw);   // dong bang EMA khi loi
    if (dhtDue(now)) {
      float t, h; const bool ok = readDHT(t, h);
      dhtOnRead(g_dhth, ok, t, g_simDht);
      if (ok) { g_temp = t; g_hum = h; }
    }
    g_in  = { g_ppm, g_mq2h.fault, g_dhth.fault, now };
    g_out = fsmStep(g_fsm, g_in, g_th);

    if (g_fsm.state == STATE_ALARM && prev != STATE_ALARM) publishAlarmEvent(true);
    else if (g_fsm.state == STATE_COOLDOWN && prev == STATE_ALARM) publishAlarmEvent(false);
    publishTelemetry();
  }
}
static void recompute() { g_in.nowMs = millis(); g_out = fsmStep(g_fsm, g_in, g_th); }
```

`recompute()` được gọi sau mỗi lệnh để quạt và còi đổi ngay, không chờ chu kỳ 2 giây. Khi MQ-2 hỏng từ lúc khởi động, `g_ppm` giữ 0 và telemetry gửi `mq2_valid:false`.

### 8.3 Driver còi — chủ sở hữu duy nhất của LEDC

```cpp
static bool s_on = false; static uint32_t s_freq = 0, s_testEnd = 0;
void buzzerTest(uint32_t now) { s_testEnd = now + 500; }             // thay delay(500)
void buzzerTick(BuzzerMode mode, uint32_t now) {
  BuzzerCmd c = buzzerPattern(mode, now);
  if (s_testEnd) { if ((int32_t)(now - s_testEnd) < 0) c = { true, BUZZER_TONE_TEST_HZ }; else s_testEnd = 0; }
  if (c.on == s_on && (!c.on || c.freqHz == s_freq)) return;            // chi ghi khi doi
  s_on = c.on; s_freq = c.freqHz;
  if (c.on) { ledcWriteTone(BUZZER_LEDC_CH, c.freqHz); ledcWrite(BUZZER_LEDC_CH, BUZZER_DUTY_50PCT); }
  else      { ledcWrite(BUZZER_LEDC_CH, BUZZER_DUTY_OFF); ledcWriteTone(BUZZER_LEDC_CH, 0); }
}
```

Quy tắc: không đoạn code nào khác ghi LEDC (cấm `ledcWrite*` trong handler lệnh). Tone TEST bị từ chối khi ALARM nên không bao giờ làm tắt còi báo động.

### 8.4 Lệnh MQTT và nút bấm

Mọi handler dùng ArduinoJson, không dùng `strstr`. Payload sai cú pháp phải trả ACK, không bỏ im lặng. Mã ACK là enum, chuỗi chỉ nằm ở một bảng.

| Topic | Trường | Giá trị | Ghi chú |
| :-- | :-- | :-- | :-- |
| `cmd/fan` | `action` | ON, OFF, AUTO | OFF khi ALARM trả `REJECTED_SAFETY_LOCK` |
| `cmd/buzzer` | `action` | MUTE (bí danh OFF), UNMUTE, TEST (bí danh ON) | MUTE và TEST khi ALARM trả `REJECTED_SAFETY_LOCK`; TEST dùng `buzzerTest`, không `delay` |
| `cmd/mode` | `mode` hoặc `action` | MANUAL, AUTO |  |
| `cmd/scheduler` | `mode` | DAY, NIGHT | `g_th = makeThresholds(NIGHT ? ALARM_PPM_NIGHT : DEFAULT_ALARM_PPM_DAY)` |
| `cmd/inject_fault` | `type` | MQ2\_DISCONNECT, DHT\_NAN, DHT\_TIMEOUT, CLEAR, RESTORE, NONE | Tên lạ trả `REJECTED_UNKNOWN_FAULT`; CLEAR/RESTORE/NONE tắt cờ giả lập, reset health và `emaReset` |
| `auth/response/<DEVICE_ID>` | `status`, `config.alarm_threshold_ppm` |  | Chỉ nhận khi topic đúng `DEVICE_ID`; ngưỡng đi qua `makeThresholds` |

```cpp
static bool is(const char* a, const char* v) { return a && strcasecmp(a, v) == 0; }
static void onFan(const char* msg) {
  JsonDocument d;
  if (deserializeJson(d, msg)) { ack(CMD_FAN, ACK_BAD_PAYLOAD); return; }
  const char* a = d["action"] | "";
  if      (is(a, "OFF"))  ack(CMD_FAN, cmdRemoteFanOff(g_fsm) == CMD_OK ? ACK_ACCEPTED : ACK_SAFETY_LOCK);
  else if (is(a, "ON"))   { cmdRemoteFanOn(g_fsm); ack(CMD_FAN, ACK_ACCEPTED); }
  else if (is(a, "AUTO")) { cmdFanAuto(g_fsm);     ack(CMD_FAN, ACK_ACCEPTED); }
  else ack(CMD_FAN, ACK_UNKNOWN_ACTION);
  recompute();
}
// Nut bam: sau debounce, o canh nhan
static void onButtonPress(uint32_t now) {
  ack(CMD_BUTTON, cmdLocalButton(g_fsm, now) ? ACK_LOCAL_SILENCE : ACK_ACCEPTED);
  recompute();
}
```

Ghi chú: chuỗi `ACTION` chứa `ON`, vì vậy so khớp bằng `strstr` làm `AUTO` bị hiểu thành ON; so khớp bắt buộc là so sánh nguyên chuỗi như trên.

### 8.5 Mạng không được chặn vòng an toàn

```cpp
static uint32_t s_wifiBackoff = 1000, s_mqttBackoff = 1000, s_wifiEnd = 0, s_wifiBegin = 0, s_mqttTry = 0;
static bool s_wifiBusy = false;

void netTick(uint32_t now) {
  if (WiFi.status() != WL_CONNECTED) {
    if (!s_wifiBusy) {
      if (now - s_wifiEnd >= s_wifiBackoff) { WiFi.disconnect(); WiFi.begin(WIFI_SSID, WIFI_PASS); s_wifiBusy = true; s_wifiBegin = now; }
    } else if (now - s_wifiBegin >= WIFI_ATTEMPT_TIMEOUT_MS) {     // het thoi gian moi tinh la that bai
      s_wifiBusy = false; s_wifiEnd = now; s_wifiBackoff = nextBackoff(s_wifiBackoff);
    }
    return;
  }
  s_wifiBusy = false; s_wifiBackoff = 1000;                         // reset ngay khi co WiFi
  if (g_mqtt.connected()) { g_mqtt.loop(); flushOfflineBuffer(5); return; }
  if (now - s_mqttTry >= s_mqttBackoff) {
    s_mqttTry = now;
    s_mqttBackoff = mqttConnect() ? 1000 : nextBackoff(s_mqttBackoff);   // backoff MQTT rieng
  }
}
```

- `mqttConnect()` đặt timeout ngắn trước khi gọi `connect`: `g_mqtt.setSocketTimeout(2)` và timeout 2 giây cho `WiFiClient` (kiểm tra đơn vị theo phiên bản core Arduino-ESP32). LWT dựng bằng `DEVICE_ID`, retained QoS 1; sau khi kết nối thì publish `online` retained, subscribe, gửi auth request.
- Tiêu chí D8: khi broker không tới được, độ trễ lớn nhất giữa hai vòng `loop()` ≤ 3000 ms (T-L1). Nếu đo vượt, chuyển sang kiến trúc dự phòng: task an toàn (cảm biến, FSM, còi, nút) chạy riêng bằng FreeRTOS, nhận lệnh từ MQTT qua hàng đợi và xuất ảnh chụp trạng thái cho tầng mạng đọc qua mutex.

### 8.6 Bộ đệm offline và payload

- Tách logic bộ đệm vòng vào `lib/core` (nhận hàm publish làm tham số) để test native. Xả dần tối đa 5 bản ghi mỗi `netTick`; khi publish thất bại thì dừng, chỉ trừ số bản ghi đã gửi, phần còn lại thử lại ở vòng sau theo đúng thứ tự.
- Sự kiện ALARM phát sinh lúc mất mạng cũng được đệm (có trường loại bản ghi).
- Telemetry gồm: `device_id` (= `DEVICE_ID`), `uptime_s`, `mq2_ppm` (null khi `mq2_valid` sai), `mq2_valid`, `temp`, `hum`, `dht_valid`, `fan`, `buzzer`, `buzzer_muted`, `fsm_state`, `alarm_th`, `safe_th`. Bản tin alarm có thêm `uptime_s` và `event` để khử trùng lặp. Keep-alive có `device_id`, `uptime_s`, `status` (HEALTHY, DEGRADED, FAULT).
- Vẫn publish song song topic V1 và V2 (Web đang đọc V1); Node-RED khử trùng lặp (mục 9.2).

### 8.7 Test cho Phase 2

| Mã | Kịch bản | Kết quả mong đợi |
| :-: | :-- | :-- |
| T-C1 | Payload JSON có `action:AUTO`; thêm ca `ACTION` trong trường khác | Vào AUTO, không bị hiểu thành ON |
| T-C2 | JSON hỏng cho từng handler (fan, buzzer, mode, scheduler) | `REJECTED_BAD_PAYLOAD` |
| T-C3 | Inject: DHT\_NAN, DHT\_TIMEOUT, CLEAR, RESTORE, NONE, tên lạ | Hai tên DHT bật `dhtFault`; ba tên xóa lỗi và reset EMA; tên lạ bị từ chối |
| T-C4 | Auth response cho `DEVICE_ID` khác; ngưỡng 250 và 500 | Bỏ qua; 300/225 và 400/300 |
| T-C5 | Scheduler NIGHT rồi DAY | 350/262.5 rồi 400/300 |
| T-C6 | TEST còi ngoài ALARM; TEST khi ALARM | Beep 500 ms không chặn (độ trễ vòng < 50 ms); bị từ chối khi ALARM |
| T-R1 | WiFi và MQTT lỗi xen kẽ | Hai backoff độc lập 1→16 s; `WiFi.begin` cách nhau ≥ 10 s |
| T-B1 | Đệm 25 bản ghi (sức chứa 20); xả với publish hỏng sau 7 bản | Còn 13 bản; lần xả sau tiếp tục đúng thứ tự, không mất bản nào |
| T-L1 | Broker không tới được trong 60 s (Wokwi hoặc mạch thật) | Độ trễ lớn nhất giữa hai vòng ≤ 3000 ms; báo động cục bộ vẫn chạy |

## 9. Phase 3 — Node-RED (≈ 6h)

### 9.1 Nguyên tắc

- Toàn bộ code function nằm trong `nodered/functions/*.js`; `generate_flows.py` đọc và nhúng vào flow. Test nạp đúng các file này.
- Trạng thái theo từng `deviceId` (Fleet Registry trong flow context). Không còn biến toàn cục `state`, `lastSeen`, `cooldownStart`.
- Trạng thái hiệu lực = trạng thái thiết bị báo, chỉ được leo thang bởi luật; không bao giờ hạ.
- Chỉ một node `mqtt out` phát lệnh xuống, để trống topic, đứng sau function Command Dispatcher (chặn topic có ký tự wildcard). Xóa node switch định tuyến theo topic và các node `mqtt out` topic cố định. Nút bấm trên dashboard (có topic riêng) nối vào cùng dispatcher.
- Rule 2 mới: khói vượt ngưỡng nhưng nhiệt thấp vẫn là ALARM kèm thông báo (khói âm ỉ là đúng ca cần cảnh báo sớm); luật chỉ bật quạt, không MUTE, không đợi 10 giây.
- Node-RED không tự đặt FAULT từ lệnh inject; trạng thái lấy từ telemetry của thiết bị (`fsm_state`, `mq2_valid`, `dht_valid`). Lệnh inject chỉ được ghi log.
- Firmware đã tự xả 30 giây: Node-RED không gửi MUTE, không gửi tắt quạt sau cooldown.

### 9.2 Parser và khử trùng lặp

```javascript
// functions/parse_telemetry.js
let d = msg.payload;
if (typeof d === 'string') { try { d = JSON.parse(d); } catch (e) { return null; } }
if (!d || typeof d !== 'object') return null;
const num = v => (v === null || v === undefined) ? NaN : Number(v);
msg.eventType = 'TELEMETRY';
msg.deviceId  = d.device_id || 'ESP32_SMOKE_N09_A01';
msg.uptime    = d.uptime_s;
msg.mq2Valid  = d.mq2_valid !== false;
msg.dhtValid  = d.dht_valid !== false;
msg.ppm = num(d.mq2_ppm); msg.temp = num(d.temp);
msg.fsmState = d.fsm_state;
msg.alarmTh = Number(d.alarm_th) || undefined; msg.safeTh = Number(d.safe_th) || undefined;
// ---- DEDUP: chen y nguyen doan nay vao parser telemetry, keep-alive va alarm ----
if (msg.uptime !== undefined) {
  const now = Date.now(), cache = flow.get('dedup') || {};
  for (const k in cache) if (now - cache[k] > 5000) delete cache[k];      // TTL 5 s, don cache
  const key = msg.deviceId + '|' + msg.eventType + '|' + (msg.eventName || '') + '|' + msg.uptime;
  if (cache[key]) return null;
  cache[key] = now; flow.set('dedup', cache);
}
return msg;
```

- Parser keep-alive: `eventType = 'KEEP_ALIVE'`, `uptime = d.uptime_s ?? d.uptime_sec`. Parser alarm: `eventType = 'ALARM_EVENT'`, `eventName = d.event`, `uptime = d.uptime_s`.
- Parser LWT (dùng chung cho V1 và V2):

```javascript
// functions/parse_lwt.js
let s = msg.payload, id, online;
try { const j = typeof s === 'string' ? JSON.parse(s) : s; id = j.device_id; online = String(j.status).toLowerCase() === 'online'; }
catch (e) { online = String(s).trim().toLowerCase() === 'online'; }
msg.eventType = 'LWT'; msg.deviceId = id || 'ESP32_SMOKE_N09_A01'; msg.isOnline = online;
return msg;
```

### 9.3 Core Engine

```javascript
// functions/core_engine.js  (4 output: lenh, log, fleet, thong bao)
const NOW = Date.now();
const FLOOR = 'F03', CROSS_PPM = 600, CROSS_RATE_MS = 60000, WATCHDOG_MS = 30000, ALERT_RATE_MS = 20000;
const fleet = flow.get('fleet') || {};
const cmds = [], logs = [];
let alert = null;

const dev = id => fleet[id] || (fleet[id] = { deviceId: id, status: 'UNKNOWN', deviceState: 'SAFE', effective: 'SAFE',
  lastSeen: 0, ppm: NaN, temp: NaN, rate: 0, lastPpm: 0, tempHist: [], alarmTh: 400, safeTh: 300,
  overActive: false, hotActive: false, cooldownStart: null, lastAlert: 0, topology: null, mq2Valid: true, dhtValid: true });
const log = (level, event, desc, id) => logs.push({ level, event, desc, deviceId: id, ts: NOW });
const topicOf = (d, kind) => (d.topology && d.topology.building && d.topology.floor && d.topology.room)
  ? `Nhom09/smoke/v2/${d.topology.building}/${d.topology.floor}/${d.topology.room}/${d.deviceId}/cmd/${kind}`
  : `Nhom09/smoke/cmd/${kind}`;
const cmd = (d, kind, payload) => ({ topic: topicOf(d, kind), payload });
const notify = (d, text) => { if (NOW - d.lastAlert > ALERT_RATE_MS) { d.lastAlert = NOW; alert = { deviceId: d.deviceId, text }; } };

switch (msg.eventType) {
  case 'TELEMETRY': {
    const d = dev(msg.deviceId);
    d.lastSeen = NOW; d.status = 'ONLINE';
    d.deviceState = msg.fsmState || d.deviceState;
    d.alarmTh = msg.alarmTh || d.alarmTh; d.safeTh = msg.safeTh || d.safeTh;
    d.mq2Valid = msg.mq2Valid; d.dhtValid = msg.dhtValid;
    d.cooldownStart = d.deviceState === 'COOLDOWN' ? (d.cooldownStart || NOW) : null;

    // Rule 1: dT/dt theo cua so; mau cu nhat co tuoi >= 20 s trong 60 s; giu rate giua cac lan tinh
    if (d.dhtValid && Number.isFinite(msg.temp)) {
      d.temp = msg.temp;
      d.tempHist.push({ t: NOW, v: msg.temp });
      d.tempHist = d.tempHist.filter(s => NOW - s.t <= 60000);
      const ref = d.tempHist.find(s => NOW - s.t >= 20000);
      if (ref) d.rate = (msg.temp - ref.v) / ((NOW - ref.t) / 60000);
    } else d.rate = 0;

    d.effective = d.deviceState;
    if (!d.mq2Valid || !Number.isFinite(msg.ppm)) {
      if (d.deviceState !== 'ALARM') d.effective = 'FAULT';          // khong dung PPM cua cam bien hong
    } else {
      d.ppm = msg.ppm;
      const over = msg.ppm >= d.alarmTh;
      const hot = d.rate >= 3.0 || msg.temp >= 50.0;
      if (over) {
        d.effective = 'ALARM';                                         // chi leo thang
        if (!d.overActive) {                                           // canh vuot nguong
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
      } else if (msg.ppm <= d.safeTh) { d.overActive = false; d.hotActive = false; }

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
  case 'KEEP_ALIVE': { const d = dev(msg.deviceId); d.lastSeen = NOW; if (d.status !== 'ONLINE') d.status = 'ONLINE'; break; }
  case 'LWT': {
    const d = dev(msg.deviceId);
    if (!msg.isOnline) { d.status = 'OFFLINE'; d.effective = 'OFFLINE'; log('CRITICAL', 'LWT_DISCONNECT', 'Broker bao thiet bi mat ket noi', d.deviceId); notify(d, 'Thiet bi mat ket noi (LWT)'); }
    else { d.status = 'ONLINE'; d.lastSeen = NOW; log('INFO', 'LWT_CONNECT', 'Thiet bi ket noi lai', d.deviceId); }   // khong tu dat SAFE
    break;
  }
  case 'WATCHDOG_TICK':
    Object.values(fleet).forEach(d => {
      if (d.status === 'ONLINE' && d.lastSeen && NOW - d.lastSeen > WATCHDOG_MS) {
        d.status = 'OFFLINE'; d.effective = 'OFFLINE'; log('CRITICAL', 'WATCHDOG_TIMEOUT', 'Qua 30 s khong co du lieu', d.deviceId); notify(d, 'Thiet bi im lang qua 30 s');
      }
    });
    break;
  case 'ALARM_EVENT': { const d = dev(msg.deviceId); log('CRITICAL', msg.eventName || 'ALARM_EVENT', 'Su kien tu thiet bi', d.deviceId); break; }
  case 'FAULT_INJECTION_CMD': log('INFO', 'FAULT_INJECTION_SEEN', 'Chi ghi nhan; trang thai lay tu telemetry thiet bi', msg.deviceId); break;
}

flow.set('fleet', fleet);
if (logs.length) flow.set('history', logs.concat(flow.get('history') || []).slice(0, 80));
return [
  cmds.length ? cmds.map(c => ({ topic: c.topic, payload: JSON.stringify(c.payload), qos: 1 })) : null,
  logs.length ? { payload: logs } : null,
  { payload: { fleet: Object.values(fleet) } },
  alert ? { payload: alert } : null
];
```

- Function Auth (Dịch vụ 1): đăng ký thiết bị vào `fleet` kèm `topology` đầy đủ (building, floor, room) khi xác thực PASS. Whitelist dùng `DEVICE_ID` mới. Thiết bị chưa xác thực không có topology nên không nhận broadcast; để minh họa Rule 5 cần giả lập A02, A03 xác thực qua MQTTX.
- Rule 3 (scheduler) là một function riêng chạy mỗi phút, phát lệnh theo cạnh:

```javascript
// functions/scheduler_tick.js
const h = new Date().getHours(), night = h >= 22 || h < 6;
if (flow.get('sched') === night) return null;
flow.set('sched', night);
return { topic: 'Nhom09/smoke/cmd/scheduler', payload: JSON.stringify({ mode: night ? 'NIGHT' : 'DAY', source: 'RULE_3_SCHEDULER' }) };
```

### 9.4 Command Dispatcher và thông báo

```javascript
// functions/command_dispatcher.js
if (typeof msg.topic !== 'string' || /[+#]/.test(msg.topic)) { node.warn('Bo qua topic khong hop le: ' + msg.topic); return null; }
return msg;
```

```javascript
// functions/alert_dispatcher.js  (output 1 -> http request, output 2 -> dashboard + debug)
const token = env.get('TELEGRAM_TOKEN'), chat = env.get('TELEGRAM_CHAT_ID');
const text = '[' + msg.payload.deviceId + '] ' + msg.payload.text;
if (!token || !chat) return [null, { payload: text }];
return [{ method: 'POST', url: 'https://api.telegram.org/bot' + token + '/sendMessage',
          headers: { 'content-type': 'application/json' },
          payload: JSON.stringify({ chat_id: chat, text: text }) }, { payload: text }];
```

### 9.5 Harness và test Node-RED (`node --test`)

```javascript
// nodered/tests/harness.js
const fs = require('fs');
exports.load = file => new Function('msg', 'flow', 'node', 'env', fs.readFileSync(file, 'utf8'));
exports.mkFlow = () => { const m = new Map(); return { get: k => m.get(k), set: (k, v) => m.set(k, v) }; };
exports.node = { warn() {}, log() {} };
```

Ghi đè `Date.now` trong test để điều khiển thời gian.

| Mã | Kịch bản | Kết quả mong đợi |
| :-: | :-- | :-- |
| T-N1 | Cùng bản tin V1 rồi V2 (cùng `uptime_s`); lại sau 6 s | Chỉ 1 bản được xử lý; sau 5 s TTL được xử lý lại |
| T-N2 | LWT JSON `status:online`; `status:offline`; chuỗi trần `online` | online không thành OFFLINE; offline thành OFFLINE; chuỗi trần vẫn đúng |
| T-N3 | PPM 450, nhiệt 30, dT/dt 0 | Hiệu lực ALARM, lệnh quạt ON, có thông báo, không có lệnh MUTE |
| T-N4 | Nhiệt 28 lên 29.5 trong 25 s kèm PPM 450 | Real fire, UNMUTE đúng 1 lần dù nhận nhiều gói |
| T-N5 | Bản tin đầu tiên của thiết bị mới có PPM 655; gói kế tiếp trong 60 s | Broadcast ngay ở gói đầu, topic cụ thể không có `+` hoặc `#`; gói sau không phát lại |
| T-N6 | `mq2_valid:false`, PPM null | Hiệu lực FAULT (nếu thiết bị không ALARM), bỏ qua luật PPM |
| T-N7 | Thiết bị báo COOLDOWN | Hiệu lực COOLDOWN, không sinh lệnh nào |
| T-N8 | A01 ALARM, A02 SAFE | Trạng thái không ảnh hưởng nhau |
| T-N9 | Dispatcher nhận topic có `+` | Bị loại, có cảnh báo log |
| T-N10 | Watchdog sau 31 s chỉ với A01 im lặng | Chỉ A01 thành OFFLINE |
| T-N11 | Inject: tên lạ và NONE | Chỉ ghi log, không đổi trạng thái |
| T-N12 | Không có `TELEGRAM_TOKEN` | Output 1 rỗng, output 2 có văn bản (mock) |

## 10. Phase 4 — Web SCADA (≈ 3h)

- Web chỉ phản chiếu: `STATE.fsmState = data.fsm_state`, ngưỡng lấy từ `alarm_th` và `safe_th`. Xóa `evaluateFsmRules` khỏi vai trò nguồn trạng thái (chỉ giữ làm dự phòng hiển thị khi telemetry thiếu `fsm_state`), xóa `triggerAlarmState` tự đặt quạt/còi, xóa bộ đếm cooldown tự gửi `fan OFF`.
- Trường mới `mq2_valid`, `dht_valid`, `buzzer_muted` hiển thị thành huy hiệu: cảm biến khói lỗi, DHT suy giảm, còi đã xác nhận 60 s.
- Khi trạng thái là ALARM: vô hiệu nút Mute và Fan OFF; khi nhận ACK `REJECTED_SAFETY_LOCK` hoặc `ACCEPTED_LOCAL_SILENCE` thì hiện toast tương ứng.
- Vai trò người dùng (dropdown) ghi rõ là minh họa giao diện, không phải cơ chế bảo mật.
- Chống XSS: giữ nguyên mảng `STATE.logs` (tối đa 80) và `renderAuditTable`; escape mọi chuỗi lấy từ MQTT ngay lúc render. Bản vá `showToast` (dùng `textContent`) vẫn bắt buộc. Khung Telegram mock chỉ cho phép thẻ `<b>` cố định do code tạo, mọi giá trị động đi qua `escapeHtml`.

```javascript
// web/util.js
export function escapeHtml(v) {
  return String(v === null || v === undefined ? '' : v)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}
const LEVELS = ['INFO', 'WARN', 'CRITICAL', 'SUCCESS'];
export const safeLevelClass = lv => (LEVELS.includes(lv) ? 'lvl-' + lv.toLowerCase() : 'lvl-info');
```

| Mã | Kịch bản | Kết quả mong đợi |
| :-: | :-- | :-- |
| T-W1 | `escapeHtml` với `<img src=x onerror=alert(1)>`, dấu nháy, `&` | Không còn ký tự đặc biệt chưa escape |
| T-W2 | `renderAuditTable` với log có `desc` chứa `<script>` (jsdom) | Không có phần tử script trong DOM |
| T-W3 | `showToast` với thông điệp chứa HTML | Hiển thị như văn bản thuần |
| T-W4 | Telemetry `fsm_state:ALARM`, `mq2_valid:false` | Giao diện hiện ALARM và huy hiệu lỗi; Web không tự gửi lệnh quạt/còi |

## 11. Phase 5 — MQTTX, tài liệu, Audit Matrix (≈ 4h)

### 11.1 Bộ MQTTX

Giữ MSG-14 (`DHT_TIMEOUT`) và MSG-15 (`NONE`), vì firmware nay chấp nhận. Thêm:

| Mã | Nội dung | Kỳ vọng |
| :-: | :-- | :-- |
| MSG-16 | Fan `AUTO` | ACCEPTED, về chế độ tự động |
| MSG-17 | Buzzer `MUTE` khi đang ALARM | `REJECTED_SAFETY_LOCK`, còi vẫn kêu |
| MSG-18 | Buzzer `TEST` khi đang ALARM | `REJECTED_SAFETY_LOCK` |
| MSG-19 | Scheduler `NIGHT` rồi `DAY` | Ngưỡng 350/262.5 rồi 400/300 (đọc từ telemetry) |
| MSG-20 | Inject `MQ2_DISCONNECT` khi đang ALARM | Còi vẫn liên tục; `CLEAR` khôi phục |
| MSG-21 | JSON hỏng cho fan | `REJECTED_BAD_PAYLOAD` |
| MSG-22 | Auth response giả cho thiết bị khác | Bị bỏ qua |
| MSG-23 | Auth PASS cho A02, A03 (topology tầng F03) | Fleet có đủ thiết bị để minh họa Rule 5 |

Telemetry mẫu trong bộ test phải có `uptime_s`, `mq2_valid`, `dht_valid`, `fsm_state`, `alarm_th`, `safe_th`.

### 11.2 Tiền tố topic (khuyến nghị)

Chạy một lần `scripts/apply_topic_root.py` thay `Nhom09` bằng tiền tố mới ở `config.h`, `app.js`, `generate_flows.py` và bộ MQTTX, rồi commit. Tài liệu ghi rõ đây chỉ giảm va chạm giữa các nhóm trên broker công cộng, không phải bảo mật.

### 11.3 Tài liệu Word cần sửa

| Mục | Nội dung sửa |
| :-- | :-- |
| Phần 7 (luật, FSM) | FSM firmware 5 trạng thái, OFFLINE do middleware suy ra; Rule 2 mới (không mute); Rule 5 theo cạnh và giới hạn 60 s; thêm bảng ưu tiên (mục 2); tách sơ đồ thành FSM firmware và luật Node-RED |
| Phần 9 (bộ lọc, mạng) | EMA theo công thức `spike_max = nền + (ngưỡng − nền)/α_rise` (nền 200: ngày 700 PPM, đêm 575 PPM); báo cháy: bước 600 PPM trong ≤ 4 s, 500 trong 6 s, 450 trong 8 s; backoff 1→16 s; bỏ tuyên bố xung gai < 196 PPM |
| Bảng test case Tuần 7 và 9 | Cập nhật các ca mô tả hành vi cũ (Rule 2 MUTE, EMA, backoff); thêm ca mới theo mục 7, 8.7, 9.5 |
| Bảo mật | Broker công cộng cổng 1883 không TLS, token minh họa; nêu các rủi ro còn lại; không tuyên bố TLS hay RBAC thật |
| Thông báo | Telegram là mock mặc định, gửi thật khi có biến môi trường |
| Phần cứng | Cầu phân áp (D12), sơ đồ Wokwi khác mạch thật, nền 200 PPM, PPM là giá trị tương đối đã hiệu chuẩn, ngưỡng 400 là tham số minh họa chứ không phải quy chuẩn PCCC |
| Bộ nhớ | Chỉ khẳng định không cấp phát heap trong vòng đọc cảm biến và FSM; handler JSON dùng heap tạm của ArduinoJson v7 |

### 11.4 Audit Matrix sinh từ claim có bằng chứng

```yaml
# docs/audit/claims.yaml
- claim: Lenh MUTE, tat quat, TEST coi bi tu choi khi ALARM
  evidence: { file: lib/core/fsm_core.h, symbol: cmdRemoteMute, test: T-F8 }
```

- `scripts/check_claims.py` kiểm từng claim: file tồn tại, ký hiệu có trong file, mã test có trong `docs/audit/test_results.json` với kết quả pass (file này do bước chạy test sinh ra).
- `scratch/build_dossier.py` chỉ in PASS cho claim đã được kiểm; claim thiếu bằng chứng thì build thất bại. Viết `claims.yaml` sau khi test đã xanh.
- T-D1: thêm một claim không có ký hiệu hoặc test thì `check_claims.py` phải thất bại.

## 12. Phase 6 — Nghiệm thu và demo (≈ 3h)

```
pio test -e native
node --test nodered/tests web/tests
pio run                          # khong warning
python run_all_tests.py --all    # da cap nhat cac ca mo ta hanh vi cu
python scripts/check_claims.py
```

Tiêu chí: mọi test T-\* pass; 63 test cũ pass sau khi cập nhật những ca mô tả hành vi cũ (liệt kê trong `snapshot_diff.md`, không sửa test để che lỗi); T-L1 đạt.

### Kịch bản demo (Wokwi, MQTTX, Dashboard)

1. Khởi động: thiết bị xác thực PASS, dashboard ONLINE, trạng thái SAFE.
2. Kéo khói lên 450 PPM và giữ: ALARM sau ≤ 8 s, còi và quạt bật. Node-RED báo ALARM; Rule 2 (nhiệt thấp) bật quạt và có thông báo.
3. Chứng minh downlink (UC08): gửi MUTE và fan OFF khi đang ALARM thì nhận `REJECTED_SAFETY_LOCK`, còi và quạt vẫn chạy (chứng minh ưu tiên an toàn). Khi không ALARM, gửi fan ON rồi AUTO thì ACCEPTED và thiết bị đổi trạng thái (chứng minh lệnh xuống hoạt động).
4. Nút bấm tại chỗ trên Wokwi: còi tắt 60 s, quạt giữ ON; hết 60 s còi kêu lại.
5. Hạ khói dưới 300: COOLDOWN 30 s rồi SAFE hoặc WARNING tùy PPM.
6. Inject `MQ2_DISCONNECT` khi SAFE: FAULT với beep 200/1800 ms. Inject khi đang ALARM: còi liên tục. `CLEAR` khôi phục và reset EMA.
7. Ngắt broker: thiết bị vẫn báo động cục bộ và đệm dữ liệu; nối lại thì xả đúng thứ tự, dashboard hiện LWT/ONLINE.
8. Rule 5: PPM 655 tại A01 (A02, A03 đã xác thực bằng MSG-23) thì UNMUTE tầng F03 được phát đúng một lần.

## 13. Bảng truy vết: lỗi → giải pháp → test

| Mã | Lỗi | Giải pháp | Test |
| :-: | :-- | :-- | :-- |
| F01 | DHT hỏng làm tê liệt báo khói | DHT chỉ dẫn tới WARNING; ALARM không phụ thuộc DHT | T-F6 |
| F02 | ADC > 4080 bị coi là đứt dây | Chỉ coi ADC < 30 là lỗi | T-H1, T-H2 |
| F03 | MQ-2 hỏng thì còi tắt | Beep lỗi; giữ ALARM nếu đã chốt | T-F4, T-F5 |
| F04 | Rule 2 gửi MUTE 180 s | Rule 2 mới không mute | T-N3 |
| F05 | dT/dt không bao giờ kích hoạt | Cửa sổ ≥ 20 s theo từng thiết bị, giữ giá trị rate | T-N4 |
| F06 | MQTTX 14/15 sai tên; NONE đặt FAULT | Firmware chấp nhận nhiều tên; Node-RED chỉ ghi log | T-C3, T-N11 |
| F07 | Auth luôn bị từ chối (client id ngẫu nhiên) | `DEVICE_ID` riêng; chỉ nhận response đúng thiết bị | T-C4, demo bước 1 |
| F08 | `strstr` hiểu AUTO thành ON | Parse JSON, so sánh nguyên chuỗi | T-C1 |
| F09 | LWT không được xử lý, parser sai | Parse JSON, engine xử lý LWT | T-N2 |
| F10 | Bản tin trùng V1/V2 | Khử trùng lặp có TTL | T-N1 |
| F11 | Rule 5 bị ghi đè topic, wildcard | Topic cụ thể, `mqtt out` rỗng, dispatcher | T-N5, T-N9 |
| F12 | Rule 5 phát liên tục hoặc bỏ lỡ cạnh đầu | Cạnh, giới hạn 60 s, `lastPpm` khởi tạo 0 | T-N5 |
| F13 | WARNING phá hysteresis | Giữ ALARM tới ≤ safe | T-F1 |
| F14 | FAULT bị ALARM ghi đè | FAULT suy ra từ cờ mỗi chu kỳ | T-F4, T-F5 |
| F15 | Mute nuốt báo động | Xóa mute ở cạnh vào ALARM | T-F7 |
| F16 | Nút xác nhận bị hủy mỗi chu kỳ | Mute chỉ xóa ở cạnh | T-F9 |
| F17 | TEST còi tắt báo động, `delay` | Driver còi duy nhất, từ chối TEST khi ALARM | T-C6 |
| F18 | Beep lỗi không kêu, ghi LEDC liên tục | `buzzerPattern` và ghi theo cạnh | T-F11 |
| F19 | EMA chậm, nhiễu, hỏng sau lỗi | EMA bất đối xứng, đóng băng, reset | T-E1 đến T-E5 |
| F20 | Ngưỡng server vô hạn, kẹt SAFE | `makeThresholds` | T-TH1, T-C4, T-C5 |
| F21 | Backoff cố định, dùng chung | Hai backoff, timeout WiFi | T-F12, T-R1 |
| F22 | Mạng chặn vòng an toàn | Timeout ngắn, đo độ trễ | T-L1 |
| F23 | Bộ đệm offline mất dữ liệu | Xả dần, đệm cả sự kiện | T-B1 |
| F24 | Lỗi DHT không bao giờ phát hiện | Đếm lần đọc hỏng liên tiếp | T-H3 |
| F25 | XSS dashboard | `escapeHtml`, `textContent` | T-W1 đến T-W3 |
| F26 | Ba FSM lệch nhau | Phản chiếu `fsm_state` | T-N7, T-W4 |
| F27 | Tài liệu nói sai | `claims.yaml` và `check_claims.py` | T-D1 |
| F28 | Ngưỡng đêm 262.5 lệch 250 | Một hàm ngưỡng duy nhất | T-C5 |

## 14. Kế hoạch triển khai

| Phase | Việc | Ước tính | Điều kiện xong |
| :-: | :-- | :-: | :-- |
| 0 | Chuẩn bị, đối chiếu repo, baseline | 2h | Tag, `snapshot_diff.md`, native chạy được |
| 1 | Lõi thuần và test native | 6h | T-TH1, T-E\*, T-H\*, T-F\* xanh |
| 2 | Tích hợp firmware | 7h | T-C\*, T-R1, T-B1, T-L1 đạt; `pio run` không warning |
| 3 | Node-RED | 6h | T-N1 đến T-N12 xanh |
| 4 | Web | 3h | T-W1 đến T-W4 xanh |
| 5 | MQTTX, tài liệu, claim | 4h | `check_claims.py` pass |
| 6 | Nghiệm thu, demo | 3h | Kịch bản mục 12 chạy trọn vẹn |

Tổng khoảng 31 giờ. Thứ tự 0 → 1 → 2; Phase 3 làm song song với Phase 2 sau khi chốt payload (mục 8.6); sau đó 4 → 5 → 6. Mỗi phase một commit hoặc PR, viết test của phase trước khi sửa, không sang phase sau khi phase trước chưa xanh.

## 15. Quyết định mở (mặc định nếu chưa trả lời)

| Câu hỏi | Mặc định |
| :-- | :-- |
| Đổi tiền tố topic? | Có, `Nhom09-N09-<hậu tố riêng>` |
| Gửi Telegram thật? | Mock mặc định, bật thật bằng biến môi trường |
| Cần tách FreeRTOS task? | Chỉ khi T-L1 đo vượt 3 s |
| Nút xác nhận 60 s áp dụng cho ALARM nào? | Mọi ALARM và FAULT, tự bật lại sau 60 s |
| Rule 5 (sơ tán liên vùng) có trong phạm vi demo? | Có, minh họa bằng A02, A03 giả lập |

## 16. Định nghĩa hoàn thành

- Mọi F-xx ở mục 13 có test xanh, hoặc đã chuyển thành tuyên bố giới hạn trong tài liệu.
- `check_claims.py` pass; Audit Matrix sinh tự động; không còn tuyên bố về TLS, Telegram thật, zero-heap, backoff hay EMA sai.
- Kịch bản demo mục 12 chạy trọn vẹn và có ảnh hoặc log kèm theo.
- Báo cáo có bảng ưu tiên điều khiển và sơ đồ FSM đã tách thành hai phần.

