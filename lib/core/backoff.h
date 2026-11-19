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
    uint32_t currentMs = 1000;
    uint32_t initialMs = 1000;
    uint32_t maxMs     = 16000;

    void fail() {
        currentMs = nextBackoff(currentMs, maxMs);
    }

    void reset() {
        currentMs = initialMs;
    }
};

#endif // BACKOFF_H
