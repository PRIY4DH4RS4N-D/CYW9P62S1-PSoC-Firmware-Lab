#include "signal.h"
#include <string.h>
void cs_normalize(const cs_sample *s, uint8_t out[7]) {
  for (unsigned i = 0; i < 7; i++) {
    int v = (int)s->raw[i] - s->base[i];
    out[i] = v < 0 ? 0 : v >= 512 ? 127 : (uint8_t)(v * 127 / 512);
  }
}
void cs_features(cs_window *w) {
  float total = 0, peak = 0, travel = 0, first = -1, last = -1, prev = -1,
        b0 = 0, b1 = 0;
  for (unsigned t = 0; t < 64; t++) {
    float sum = 0, pos = 0;
    int on = 0;
    for (unsigned c = 0; c < 7; c++) {
      float x = w->x[t][c];
      total += x;
      if (x > peak)
        peak = x;
      if (x >= 15)
        on = 1;
      if (c >= 2) {
        sum += x;
        pos += (c - 2) * x;
      }
    }
    if (on) {
      if (first < 0)
        first = (float)t;
      last = (float)t;
    }
    if (sum >= 15) {
      pos /= sum;
      if (prev >= 0)
        travel += pos - prev;
      prev = pos;
    }
    b0 += w->x[t][0];
    b1 += w->x[t][1];
  }
  w->features[0] = first < 0 ? 0 : (last - first + 1) * 20;
  w->features[1] = peak;
  w->features[2] = travel;
  w->features[3] = total / (64 * 7);
  w->features[4] = b0 / 64;
  w->features[5] = b1 / 64;
}
int cs_segment_step(cs_segment *s, const uint8_t x[7], uint32_t ms,
                    cs_window *out) {
  unsigned peak = 0;
  for (unsigned i = 0; i < 7; i++)
    if (x[i] > peak)
      peak = x[i];
  if (s->wait_release) {
    if (peak < 10)
      s->wait_release = 0;
    return 0;
  }
  if (!s->active && peak >= 15) {
    memset(&s->window, 0, sizeof(s->window));
    s->window.ms = ms;
    s->active = 1;
    s->n = 8;
    for (unsigned j = 0; j < s->count; j++)
      memcpy(s->window.x[8 - s->count + j],
             s->ring[(s->head + 8 - s->count + j) % 8], 7);
  }
  if (s->active) {
    memcpy(s->window.x[s->n++], x, 7);
    if (s->n == 64) {
      s->window.truncated = peak >= 15;
      cs_features(&s->window);
      *out = s->window;
      s->active = 0;
      s->wait_release = peak >= 10;
      s->count = 0;
      s->head = 0;
      return 1;
    }
  } else {
    memcpy(s->ring[s->head], x, 7);
    s->head = (s->head + 1) % 8;
    if (s->count < 8)
      s->count++;
  }
  return 0;
}
