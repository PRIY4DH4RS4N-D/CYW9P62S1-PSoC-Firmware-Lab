#ifndef CAPSLIDE_GESTURE_H
#define CAPSLIDE_GESTURE_H
#include <stdint.h>
#include <stdbool.h>
typedef void (*cap_emit)(const char *type, int value, char mode, void *user);
typedef struct { bool candidate, stable; uint32_t since; } cap_button;
typedef struct {
    cap_button b[2];
    bool vertical, slider;
    int position;
    char last_mode;
    uint32_t last_move;
} cap_gesture;
void cap_step(cap_gesture *g, uint32_t ms, bool b1, bool b2, int position,
              cap_emit emit, void *user);
#endif
