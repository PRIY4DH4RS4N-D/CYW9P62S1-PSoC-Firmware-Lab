#pragma once
#include <stdint.h>
#include <stdbool.h>
typedef struct { bool b1,b2,slider; uint16_t position; } touch_raw_t;
typedef struct { bool candidate,stable; uint32_t since; } touch_debounce_t;
typedef struct { touch_debounce_t buttons[2],slider; uint16_t position; } touch_filter_t;
typedef struct {
 bool down[2],pressed[2],released[2],slider_down,slider_pressed,slider_released;
 uint16_t position;
} touch_event_t;
touch_event_t capsense_filter(touch_filter_t *f,touch_raw_t raw,uint32_t now);
bool capsense_input_init(void);
/* Returns 1 for a new processed frame, 0 while scanning, -1 on failure. */
int capsense_input_poll(uint32_t now,touch_raw_t *out);
