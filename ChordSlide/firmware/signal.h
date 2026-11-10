#pragma once
#include <stdint.h>
typedef struct {
  uint32_t ms;
  uint16_t raw[7], base[7];
} cs_sample;
typedef struct {
  uint32_t ms;
  uint8_t x[64][7];
  float features[6];
  uint8_t truncated;
} cs_window;
typedef struct {
  uint8_t ring[8][7];
  unsigned head, count, active, n, wait_release;
  cs_window window;
} cs_segment;
void cs_normalize(const cs_sample *, uint8_t[7]);
int cs_segment_step(cs_segment *, const uint8_t[7], uint32_t, cs_window *);
void cs_features(cs_window *);
