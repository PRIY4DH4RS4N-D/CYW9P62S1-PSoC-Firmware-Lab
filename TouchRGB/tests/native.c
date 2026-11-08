#include "touch_controller.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#define RGB_EQ(c,v) assert(color_pack(c)==(v))
static void conversions(void) {
 const uint32_t prim[]={0xFF0000,0xFFFF00,0x00FF00,0x00FFFF,0x0000FF,0xFF00FF};
 for(unsigned i=0;i<6;i++) {
  RGB_EQ(color_from_hsv((hsv_t){(uint16_t)(i*60),255,255}),prim[i]);
  hsv_t h=color_to_hsv(color_unpack(prim[i])); assert(h.h==i*60 && h.s==255 && h.v==255);
 }
 RGB_EQ(color_from_hsv((hsv_t){360,255,255}),0xFF0000);
 RGB_EQ(color_from_hsv((hsv_t){12,0,255}),0xFFFFFF);
 RGB_EQ(color_from_hsv((hsv_t){12,255,0}),0);
 /* Independent floating point HSV reference over the entire hue wheel. */
 for(unsigned h=0;h<360;h++) for(unsigned s=0;s<=255;s+=17) for(unsigned v=0;v<=255;v+=17) {
  double c=v*(s/255.0),x=c*(1-fabs(fmod(h/60.0,2)-1)),m=v-c;
  double refs[6][3]={{c,x,0},{x,c,0},{0,c,x},{0,x,c},{x,0,c},{c,0,x}};
  rgb_t rgb=color_from_hsv((hsv_t){(uint16_t)h,(uint8_t)s,(uint8_t)v});
  assert(abs(rgb.r-(int)lround(refs[h/60][0]+m))<=1);
  assert(abs(rgb.g-(int)lround(refs[h/60][1]+m))<=1);
  assert(abs(rgb.b-(int)lround(refs[h/60][2]+m))<=1);
 }
 for(unsigned r=0;r<=255;r+=5) for(unsigned g=0;g<=255;g+=5) for(unsigned b=0;b<=255;b+=5) {
  rgb_t a={(uint8_t)r,(uint8_t)g,(uint8_t)b}; RGB_EQ(color_unpack(color_pack(a)),color_pack(a));
  rgb_t z=color_from_hsv(color_to_hsv(a));
  assert(abs(z.r-(int)r)<=5 && abs(z.g-(int)g)<=5 && abs(z.b-(int)b)<=5);
 }
 assert(color_presets[1].hex==0xFF8000 && color_presets[16].hex==0x8000FF);
 assert(color_presets[19].hex==0xFF69B4 && color_preset_count>=24);
 for(unsigned i=0;i<256;i++) {
  assert(color_gamma((uint8_t)i)==(uint16_t)lround(pow(i/255.0,2.2)*65535.0));
  if(i) assert(color_gamma((uint8_t)i)>=color_gamma((uint8_t)(i-1)));
  assert(color_level((uint8_t)i,0)==0);
  assert(color_level((uint8_t)i,100)==color_gamma((uint8_t)i));
  for(unsigned b=0;b<=100;b++) assert(color_level((uint8_t)i,(uint8_t)b)==(color_gamma((uint8_t)i)*b+50u)/100u);
 }
 assert(color_gamma(0)==0 && color_gamma(255)==65535 && color_level(255,255)==65535);
 uint16_t last=0;
 for(unsigned p=0;p<=1000;p++) { uint16_t h=color_slider_hue((uint16_t)p); assert(h>=last && h<=359); last=h; }
 assert(color_slider_hue(0)==0 && color_slider_hue(1000)==359 && color_slider_hue(65535)==359);
 puts("PASS: HSV reference (92160 vectors), RGB round trips (140608 vectors), gamma, brightness, slider mapping");
}
static void filtering(void) {
 touch_filter_t f={0}; touch_raw_t r={0}; touch_event_t e;
 r.b1=true; e=capsense_filter(&f,r,0); assert(!e.pressed[0]);
 r.b1=false; capsense_filter(&f,r,10); r.b1=true; capsense_filter(&f,r,20);
 e=capsense_filter(&f,r,49); assert(!e.down[0]);
 e=capsense_filter(&f,r,50); assert(e.pressed[0] && e.down[0]);
 e=capsense_filter(&f,r,1000); assert(e.down[0] && !e.pressed[0]);
 r.b1=false; capsense_filter(&f,r,1001); e=capsense_filter(&f,r,1031); assert(e.released[0] && !e.down[0]);
 r.b2=true; r.slider=true; r.position=999; capsense_filter(&f,r,1040);
 e=capsense_filter(&f,r,1060); assert(e.slider_pressed && e.position==999 && !e.down[1]);
 e=capsense_filter(&f,r,1070); assert(e.pressed[1]);
 r.slider=false; r.position=0; capsense_filter(&f,r,1080);
 e=capsense_filter(&f,r,1100); assert(e.slider_released && e.position==999);
 f=(touch_filter_t){0}; r=(touch_raw_t){.b1=true};
 capsense_filter(&f,r,UINT32_MAX-10); e=capsense_filter(&f,r,20); assert(e.pressed[0]);
 puts("PASS: button/slider bounce, hold, touch, release, timestamp wrap");
}
static void transitions(void) {
 rgb_t red=color_unpack(0xFF0000),blue=color_unpack(0x0000FF),black={0};
 RGB_EQ(color_lerp(red,blue,0,100),0xFF0000);
 RGB_EQ(color_lerp(red,blue,100,100),0x0000FF);
 RGB_EQ(color_lerp(red,blue,1,0),0x0000FF);
 rgb_t mid=color_lerp(red,blue,50,100); assert(mid.r==128 && mid.b==127);
 color_fade_t f={.from=black,.to=red,.start=UINT32_MAX-49,.duration=100};
 assert(color_fade_value(&f,0).r==127);
 rgb_t before=color_fade_value(&f,0); color_fade_set(&f,blue,0,100);
 RGB_EQ(color_fade_value(&f,0),color_pack(before)); RGB_EQ(color_fade_value(&f,100),0x0000FF);
 touch_controller_t c; touch_controller_init(&c,0); touch_event_t e={0}; uint16_t levels[3];
 touch_controller_levels(&c,0,levels); assert(levels[0]==0);
 touch_controller_levels(&c,180,levels); assert(levels[0]==32768);
 e=(touch_event_t){.slider_down=true,.position=1000}; touch_controller_step(&c,&e,200);
 assert(color_to_hsv(c.selected).h==359);
 e=(touch_event_t){.pressed={true,true}}; touch_controller_step(&c,&e,400); assert(c.mode==MODE_PRESETS && c.brightness==50);
 for(unsigned cat=0;cat<5;cat++) {
  assert(c.category==cat);
  e=(touch_event_t){.slider_down=true,.position=1000,.pressed={false,true}};
  touch_controller_step(&c,&e,500+cat*10); assert(c.selection==5);
  RGB_EQ(c.selected,color_presets[cat*6+5].hex);
  e=(touch_event_t){.slider_released=true,.down={false,true}};
  touch_controller_step(&c,&e,505+cat*10);
 }
 assert(c.category==0);
 e=(touch_event_t){.pressed={true,false}}; touch_controller_step(&c,&e,600); assert(c.mode==MODE_BRIGHTNESS);
 e=(touch_event_t){.slider_down=true,.position=0}; touch_controller_step(&c,&e,610);
 touch_controller_levels(&c,790,levels); assert(levels[0]==0 && levels[1]==0 && levels[2]==0);
 e.position=1000; touch_controller_step(&c,&e,800); assert(c.brightness==100);
 e=(touch_event_t){.pressed={false,true}}; touch_controller_step(&c,&e,810); assert(c.brightness==0);
 e=(touch_event_t){.pressed={true,false}}; touch_controller_step(&c,&e,1000); assert(c.mode==MODE_CUSTOM);
 e=(touch_event_t){.slider_down=true,.position=1000,.pressed={false,true}}; touch_controller_step(&c,&e,1010);
 RGB_EQ(c.selected,color_pack(custom_presets[custom_preset_count-1]));
 e=(touch_event_t){.pressed={true,false}}; touch_controller_step(&c,&e,1100); assert(c.mode==MODE_DEMO);
 e=(touch_event_t){.slider_down=true,.position=0}; touch_controller_step(&c,&e,1105); assert(c.demo_ms==300);
 e=(touch_event_t){0}; touch_controller_step(&c,&e,1400); assert(c.demo_index==1);
 for(unsigned i=0;i<100;i++) touch_controller_step(&c,&e,1700+300*i);
 assert(c.demo_index<color_preset_count);
 e=(touch_event_t){.pressed={true,false}}; touch_controller_step(&c,&e,40000); assert(c.mode==MODE_WHEEL);
 touch_controller_init(&c,0);
 e=(touch_event_t){0}; touch_controller_step(&c,&e,180);
 touch_controller_levels(&c,0,levels); assert(levels[0]==32768);
 c.brightness_from=5000; c.brightness_to=10000; c.brightness_start=0;
 touch_controller_step(&c,&e,180); touch_controller_levels(&c,0,levels); assert(levels[0]==65535);
 puts("PASS: fade endpoints/retargeting/wrap, all modes, all categories, confirmation, demo timing");
}
int main(void) { conversions(); filtering(); transitions(); puts("ALL SOFTWARE TESTS PASSED"); return 0; }
