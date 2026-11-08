#pragma once
#include <stdint.h>
#include <stddef.h>
typedef struct { uint8_t r,g,b; } rgb_t;
typedef struct { uint16_t h; uint8_t s,v; } hsv_t;
typedef struct { const char *name; uint32_t hex; uint8_t category; } color_preset_t;
extern const color_preset_t color_presets[];
extern const size_t color_preset_count;
extern const rgb_t custom_presets[];
extern const size_t custom_preset_count;
rgb_t color_unpack(uint32_t hex);
uint32_t color_pack(rgb_t c);
rgb_t color_from_hsv(hsv_t hsv);
hsv_t color_to_hsv(rgb_t rgb);
uint16_t color_slider_hue(uint16_t position);
uint16_t color_gamma(uint8_t channel);
uint16_t color_level(uint8_t channel, uint8_t brightness);
rgb_t color_lerp(rgb_t a, rgb_t b, uint32_t elapsed, uint32_t duration);
typedef struct { rgb_t from,to; uint32_t start,duration; } color_fade_t;
rgb_t color_fade_value(const color_fade_t *f, uint32_t now);
void color_fade_set(color_fade_t *f, rgb_t to, uint32_t now, uint32_t duration);
