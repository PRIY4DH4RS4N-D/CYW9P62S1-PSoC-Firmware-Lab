#include "signal.h"
#include "wire.h"
#include <fcntl.h>
#include <io.h>
#include <stdio.h>
#include <string.h>
static int readn(void *p, size_t n) { return fread(p, 1, n, stdin) == n; }
int main(void) {
  _setmode(0, _O_BINARY);
  _setmode(1, _O_BINARY);
  setvbuf(stdout, NULL, _IONBF, 0);
  cs_segment s = {0};
  cs_decoder d = {0};
  uint8_t cmd, buf[1024];
  while (readn(&cmd, 1)) {
    if (cmd == 0) {
      memset(&s, 0, sizeof(s));
      memset(&d, 0, sizeof(d));
      fputc(0, stdout);
    } else if (cmd == 1) {
      uint16_t n;
      readn(&n, 2);
      readn(buf, n);
      uint16_t c = cs_crc(buf, n);
      fwrite(&c, 2, 1, stdout);
    } else if (cmd == 2) {
      uint8_t type;
      uint16_t seq, n;
      readn(&type, 1);
      readn(&seq, 2);
      readn(&n, 2);
      readn(buf, n);
      uint8_t out[522];
      uint16_t len = cs_frame(type, seq, buf, n, out);
      fwrite(&len, 2, 1, stdout);
      fwrite(out, 1, len, stdout);
    } else if (cmd == 3) {
      uint32_t ms;
      readn(&ms, 4);
      readn(buf, 7);
      cs_window w;
      uint8_t ret = cs_segment_step(&s, buf, ms, &w);
      if (ret)
        ret = w.truncated ? 2 : 1;
      fwrite(&ret, 1, 1, stdout);
      if (ret) {
        fwrite(w.x, 1, 448, stdout);
        fwrite(w.features, 1, 24, stdout);
      }
    } else if (cmd == 4) {
      uint8_t b;
      readn(&b, 1);
      cs_packet p;
      uint16_t ret = cs_receive(&d, b, &p) ? p.type + 1 : 0;
      fwrite(&ret, 2, 1, stdout);
      if (ret) {
        fwrite(&p.seq, 2, 1, stdout);
        fwrite(&p.len, 2, 1, stdout);
        fwrite(p.payload, 1, p.len, stdout);
      }
    } else if (cmd == 5) {
      cs_sample sample;
      readn(sample.raw, 14);
      readn(sample.base, 14);
      cs_normalize(&sample, buf);
      fwrite(buf, 1, 7, stdout);
    } else
      return 2;
  }
  return 0;
}
