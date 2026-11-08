#pragma once
#include "capsense_input.h"
#include "color_engine.h"
typedef enum { MODE_WHEEL,MODE_PRESETS,MODE_BRIGHTNESS,MODE_CUSTOM,MODE_DEMO,MODE_COUNT } touch_mode_t;
typedef struct {
 touch_mode_t mode;
 uint8_t brightness,category;
 uint16_t selection;
 rgb_t selected;
 color_fade_t fade;
 uint32_t demo_ms,demo_start;
 size_t demo_index;
 uint16_t brightness_from,brightness_to;
 uint32_t brightness_start;
} touch_controller_t;
void touch_controller_init(touch_controller_t *c,uint32_t now);
void touch_controller_step(touch_controller_t *c,const touch_event_t *e,uint32_t now);
void touch_controller_levels(const touch_controller_t *c,uint32_t now,uint16_t levels[3]);
