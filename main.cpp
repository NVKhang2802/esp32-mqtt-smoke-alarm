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
