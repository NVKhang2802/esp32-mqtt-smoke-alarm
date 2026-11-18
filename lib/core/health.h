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
