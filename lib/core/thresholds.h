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
