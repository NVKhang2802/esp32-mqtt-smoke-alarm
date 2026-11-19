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
