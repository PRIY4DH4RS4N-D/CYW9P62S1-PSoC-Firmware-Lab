#include "color_engine.h"
#include "gamma_table.h"
/* Categories: 0 warm hues, 1 greens, 2 blues, 3 pinks, 4 neutrals. */
const color_preset_t color_presets[]={
 {"Red",0xFF0000,0},{"Orange",0xFF8000,0},{"Amber",0xFFBF00,0},
 {"Yellow",0xFFFF00,0},{"Coral",0xFF7F50,0},{"Salmon",0xFA8072,0},
 {"Lime",0xBFFF00,1},{"Green",0x00FF00,1},{"Spring green",0x00FF80,1},
 {"Sea green",0x2E8B57,1},{"Teal",0x008080,1},{"Cyan",0x00FFFF,1},
 {"Sky blue",0x00BFFF,2},{"Blue",0x0000FF,2},{"Indigo",0x4B0082,2},
 {"Violet",0x8F00FF,2},{"Purple",0x8000FF,2},{"Royal blue",0x4169E1,2},
 {"Magenta",0xFF00FF,3},{"Pink",0xFF69B4,3},{"Rose",0xFF007F,3},
 {"Orchid",0xDA70D6,3},{"Lavender",0xE6E6FA,3},{"Plum",0xDDA0DD,3},
 {"White",0xFFFFFF,4},{"Warm white",0xFFD6AA,4},{"Cool white",0xD6E8FF,4},
 {"Silver",0xC0C0C0,4},{"Gray",0x808080,4},{"Black/off",0x000000,4}
};
const size_t color_preset_count=sizeof(color_presets)/sizeof(color_presets[0]);
/* Edit these explicit 8-bit channels to add custom colors. */
const rgb_t custom_presets[]={{255,0,0},{0,255,0},{0,0,255},{18,52,86},
 {255,105,180},{128,0,255},{255,214,170},{214,232,255}};
const size_t custom_preset_count=sizeof(custom_presets)/sizeof(custom_presets[0]);
rgb_t color_unpack(uint32_t v) { return (rgb_t){(uint8_t)(v>>16),(uint8_t)(v>>8),(uint8_t)v}; }
uint32_t color_pack(rgb_t c) { return ((uint32_t)c.r<<16)|((uint32_t)c.g<<8)|c.b; }
rgb_t color_from_hsv(hsv_t a) {
 uint32_t h=a.h%360u, sector=h/60u, f=h%60u;
 uint8_t p=(uint8_t)((a.v*(255u-a.s)+127u)/255u);
 uint8_t q=(uint8_t)((a.v*(15300u-a.s*f)+7650u)/15300u);
 uint8_t t=(uint8_t)((a.v*(15300u-a.s*(60u-f))+7650u)/15300u);
 switch(sector) {
 case 0:return (rgb_t){a.v,t,p}; case 1:return (rgb_t){q,a.v,p};
 case 2:return (rgb_t){p,a.v,t}; case 3:return (rgb_t){p,q,a.v};
 case 4:return (rgb_t){t,p,a.v}; default:return (rgb_t){a.v,p,q};
 }
}
static int rounded_div(int n,int d) { return n<0?-((-n+d/2)/d):(n+d/2)/d; }
hsv_t color_to_hsv(rgb_t c) {
 int max=c.r, min=c.r, h=0;
 if(c.g>max) max=c.g;
 if(c.b>max) max=c.b;
 if(c.g<min) min=c.g;
 if(c.b<min) min=c.b;
 int d=max-min;
 if(d) {
  if(max==c.r) h=rounded_div(60*((int)c.g-c.b),d);
  else if(max==c.g) h=120+rounded_div(60*((int)c.b-c.r),d);
  else h=240+rounded_div(60*((int)c.r-c.g),d);
 }
 if(h<0) h+=360;
 return (hsv_t){(uint16_t)h,(uint8_t)(max?(255*d+max/2)/max:0),(uint8_t)max};
}
uint16_t color_slider_hue(uint16_t p) { if(p>1000) p=1000; return (uint16_t)((p*359u+500u)/1000u); }
uint16_t color_gamma(uint8_t c) { return gamma_table[c]; }
uint16_t color_level(uint8_t c,uint8_t b) { if(b>100) b=100; return (uint16_t)(((uint32_t)color_gamma(c)*b+50u)/100u); }
static uint8_t mix(uint8_t a,uint8_t b,uint32_t e,uint32_t d) {
 return (uint8_t)((int32_t)a+((int64_t)((int)b-a)*e)/(int64_t)d);
}
rgb_t color_lerp(rgb_t a,rgb_t b,uint32_t e,uint32_t d) {
 if(!d || e>=d) return b;
 return (rgb_t){mix(a.r,b.r,e,d),mix(a.g,b.g,e,d),mix(a.b,b.b,e,d)};
}
rgb_t color_fade_value(const color_fade_t *f,uint32_t now) { return color_lerp(f->from,f->to,now-f->start,f->duration); }
void color_fade_set(color_fade_t *f,rgb_t to,uint32_t now,uint32_t duration) {
 f->from=color_fade_value(f,now); f->to=to; f->start=now; f->duration=duration;
}
