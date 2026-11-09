#include "core.h"
#include <string.h>
uint16_t ft_crc(const uint8_t *p,size_t n) { uint16_t c=0xffff; while(n--){c^=(uint16_t)*p++<<8; for(int i=0;i<8;i++) c=(c&0x8000)?(c<<1)^0x1021:c<<1;}return c; }
size_t ft_frame(uint8_t type,uint16_t seq,const void *data,uint16_t n,uint8_t *o) {
 if(n>128){return 0;}
 o[0]=0xa5;o[1]=0x5a;o[2]=1;o[3]=type;o[4]=seq;o[5]=seq>>8;o[6]=n;o[7]=n>>8;
 memcpy(o+8,data,n);uint16_t c=ft_crc(o+2,n+6);o[n+8]=c;o[n+9]=c>>8;return n+10;
}
int ft_step(ft_segment *s,const ft_sample *v,uint16_t t,float f[6]) {
 unsigned total=0,peak=0,width=0,weighted=0;
 for(unsigned i=0;i<7;i++){total+=v->d[i];if(v->d[i]>peak)peak=v->d[i];if(v->d[i]>=t)width++;weighted+=v->d[i]*i;}
 if(!s->active && !width)return 0;
 if(!s->active){memset(s,0,sizeof(*s));s->active=1;s->start=v->ms;s->previous=total?weighted*100/total:0;}
 if(width){s->last=v->ms;s->quiet=0;}else s->quiet++;
 unsigned pos=total?weighted*100/total:s->previous;
 s->travel+=pos>s->previous?pos-s->previous:s->previous-pos;s->previous=pos;
 s->n++;s->sum+=total;if(peak>s->peak)s->peak=peak;if(width>s->width)s->width=width;
 if(s->quiet<3 && v->ms-s->start<5000)return 0;
 f[0]=(float)(s->last-s->start+10);f[1]=(float)s->peak;f[2]=(float)s->width;
 f[3]=(float)s->sum/s->n;f[4]=(float)s->travel;f[5]=(float)s->n;
 s->active=0;return 1;
}
uint8_t ft_baseline(const float f[6]) { if(f[2]>=3)return FT_WIDE;if(f[0]<80||f[1]<100)return FT_GRAZE;return f[0]>=650?FT_HOLD:FT_TAP; }
int ft_receive(ft_decoder *d,uint8_t byte,ft_packet *p){
 if(d->used==sizeof(d->bytes)){d->used=0;d->errors++;}
 d->bytes[d->used++]=byte;
 for(;;){
  uint8_t *b=d->bytes;
  if(d->used<2)return 0;
  if(b[0]!=0xa5||b[1]!=0x5a){memmove(b,b+1,--d->used);continue;}
  if(d->used<8)return 0;
  unsigned n=b[6]|(b[7]<<8);
  if(b[2]!=1||n>128){d->errors++;memmove(b,b+1,--d->used);continue;}
  if(d->used<n+10)return 0;
  if(ft_crc(b+2,n+6)!=(uint16_t)(b[n+8]|(b[n+9]<<8))){d->errors++;memmove(b,b+1,--d->used);continue;}
  p->type=b[3];p->seq=b[4]|(b[5]<<8);p->len=n;memcpy(p->payload,b+8,n);
  d->used-=n+10;memmove(b,b+n+10,d->used);return 1;
 }
}

