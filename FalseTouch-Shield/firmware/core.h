#pragma once
#include <stdint.h>
#include <stddef.h>
#define FT_FEATURES 6
enum { FT_TAP, FT_HOLD, FT_GRAZE, FT_WIDE, FT_UNKNOWN=255 };
typedef struct { uint32_t ms; uint16_t d[7]; } ft_sample;
typedef struct { uint32_t start,last; uint32_t n,sum,peak,width,travel,previous; uint8_t quiet,active; } ft_segment;
int ft_step(ft_segment *s,const ft_sample *v,uint16_t threshold,float f[6]);
uint8_t ft_baseline(const float f[6]);
uint16_t ft_crc(const uint8_t *p,size_t n);
size_t ft_frame(uint8_t type,uint16_t seq,const void *data,uint16_t n,uint8_t *out);
typedef struct {uint8_t bytes[138];uint16_t used;uint32_t errors;} ft_decoder;
typedef struct {uint8_t type;uint16_t seq,len;uint8_t payload[128];} ft_packet;
int ft_receive(ft_decoder *d,uint8_t byte,ft_packet *p);
