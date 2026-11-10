#include "wire.h"
#include "signal.h"
#include <string.h>
static cs_segment segment;
static cs_decoder decoder;
void test_reset(void){memset(&segment,0,sizeof(segment));memset(&decoder,0,sizeof(decoder));}
int test_step(const uint8_t*x,uint32_t ms,uint8_t*out,float*f){cs_window w;int done=cs_segment_step(&segment,x,ms,&w);if(done){memcpy(out,w.x,448);memcpy(f,w.features,24);return w.truncated?2:1;}return 0;}
int test_receive(uint8_t b,uint8_t*out,uint16_t*seq,uint16_t*n){cs_packet p;int ok=cs_receive(&decoder,b,&p);if(ok){memcpy(out,p.payload,p.len);*seq=p.seq;*n=p.len;return p.type+1;}return 0;}
void test_normalize(const uint16_t*raw,const uint16_t*base,uint8_t*out){cs_sample s;memcpy(s.raw,raw,14);memcpy(s.base,base,14);cs_normalize(&s,out);}
