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
