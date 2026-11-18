#ifndef NETUTIL_H
#define NETUTIL_H

#include <stdint.h>

inline uint32_t nextBackoff(uint32_t cur, uint32_t maxMs = 16000) {
    return cur * 2 > maxMs ? maxMs : cur * 2;
}

#endif // NETUTIL_H
