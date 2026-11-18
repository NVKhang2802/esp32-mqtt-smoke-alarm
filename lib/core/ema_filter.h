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
