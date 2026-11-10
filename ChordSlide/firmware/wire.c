#include "wire.h"
#include <string.h>
uint16_t cs_crc(const uint8_t *p, size_t n) {
  uint16_t c = 0xffff;
  while (n--) {
    c ^= (uint16_t)*p++ << 8;
    for (int i = 0; i < 8; i++)
      c = (c & 0x8000) ? (c << 1) ^ 0x1021 : c << 1;
  }
  return c;
}
size_t cs_frame(uint8_t type, uint16_t seq, const void *data, uint16_t n,
                uint8_t *o) {
  if (n > 512) {
    return 0;
  }
  o[0] = 0xa5;
  o[1] = 0x5a;
  o[2] = 1;
  o[3] = type;
  o[4] = seq;
  o[5] = seq >> 8;
  o[6] = n;
  o[7] = n >> 8;
  memcpy(o + 8, data, n);
  uint16_t c = cs_crc(o + 2, n + 6);
  o[n + 8] = c;
  o[n + 9] = c >> 8;
  return n + 10;
}
int cs_receive(cs_decoder *d, uint8_t byte, cs_packet *p) {
  if (d->used == sizeof(d->bytes)) {
    d->used = 0;
    d->errors++;
  }
  d->bytes[d->used++] = byte;
  for (;;) {
    uint8_t *b = d->bytes;
    if (d->used < 2)
      return 0;
    if (b[0] != 0xa5 || b[1] != 0x5a) {
      memmove(b, b + 1, --d->used);
      continue;
    }
    if (d->used < 8)
      return 0;
    unsigned n = b[6] | (b[7] << 8);
    if (b[2] != 1 || n > 512) {
      d->errors++;
      memmove(b, b + 1, --d->used);
      continue;
    }
    if (d->used < n + 10)
      return 0;
    if (cs_crc(b + 2, n + 6) != (uint16_t)(b[n + 8] | (b[n + 9] << 8))) {
      d->errors++;
      memmove(b, b + 1, --d->used);
      continue;
    }
    p->type = b[3];
    p->seq = b[4] | (b[5] << 8);
    p->len = n;
    memcpy(p->payload, b + 8, n);
    d->used -= n + 10;
    memmove(b, b + n + 10, d->used);
    return 1;
  }
}
