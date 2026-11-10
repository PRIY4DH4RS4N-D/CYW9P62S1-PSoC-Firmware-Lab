#pragma once
#include <stddef.h>
#include <stdint.h>
#define CS_MAX_PAYLOAD 512
uint16_t cs_crc(const uint8_t *, size_t);
size_t cs_frame(uint8_t, uint16_t, const void *, uint16_t, uint8_t *);
typedef struct {
  uint8_t bytes[522];
  uint16_t used;
  uint32_t errors;
} cs_decoder;
typedef struct {
  uint8_t type;
  uint16_t seq, len;
  uint8_t payload[512];
} cs_packet;
int cs_receive(cs_decoder *, uint8_t, cs_packet *);
