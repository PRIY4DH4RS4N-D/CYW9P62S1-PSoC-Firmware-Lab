#include "core.h"
#include "model.h"
#include <stdio.h>
#include <string.h>
int main(int argc,char **argv){
 if(argc>1 && strcmp(argv[1],"features")==0){
  ft_segment s={0};ft_sample v;float f[6];
  unsigned ms;
  while(scanf("%u",&ms)==1){v.ms=ms;for(int i=0;i<7;i++){unsigned n;if(scanf("%u",&n)!=1)return 2;v.d[i]=n;}
   if(ft_step(&s,&v,60,f)){for(int i=0;i<6;i++)printf("%.9g ",f[i]);puts("");}}
 }else if(argc>1 && strcmp(argv[1],"decode")==0){unsigned n;ft_decoder d={0};ft_packet p;while(scanf("%u",&n)==1){if(ft_receive(&d,n,&p)){printf("%u %u %u\n",p.type,p.seq,p.len);}}
 }else if(argc>1 && strcmp(argv[1],"crc")==0){unsigned n;uint8_t b[128];size_t k=0;while(k<128&&scanf("%u",&n)==1)b[k++]=n;printf("%u\n",ft_crc(b,k));
 }else if(argc>1 && strcmp(argv[1],"frame")==0){uint8_t b[138],p[]={1,2,3};size_t n=ft_frame(16,65535,p,3,b);for(size_t i=0;i<n;i++)printf("%02x",b[i]);puts("");
 }else{float f[6],c;while(scanf("%f %f %f %f %f %f",f,f+1,f+2,f+3,f+4,f+5)==6){unsigned p=ft_predict(f,&c);printf("%u %.9g\n",p,c);}}
 return 0;
}
