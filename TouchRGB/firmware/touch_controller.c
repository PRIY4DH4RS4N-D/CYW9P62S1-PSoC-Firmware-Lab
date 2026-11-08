#include "touch_controller.h"
#include <string.h>
#define FADE_MS 180u
static uint16_t brightness_now(const touch_controller_t *c,uint32_t now) {
 uint32_t e=now-c->brightness_start;
 if(e>=FADE_MS) return c->brightness_to;
 return (uint16_t)((int32_t)c->brightness_from+((int32_t)c->brightness_to-c->brightness_from)*(int32_t)e/(int32_t)FADE_MS);
}
static void set_brightness(touch_controller_t *c,uint8_t b,uint32_t now) {
 c->brightness_from=brightness_now(c,now); c->brightness_to=(uint16_t)b*100u;
 c->brightness_start=now; c->brightness=b;
}
static void select_color(touch_controller_t *c,rgb_t rgb,uint32_t now,uint32_t duration) {
 c->selected=rgb;
 if(color_pack(c->fade.to)!=color_pack(rgb)) color_fade_set(&c->fade,rgb,now,duration);
}
void touch_controller_init(touch_controller_t *c,uint32_t now) {
 memset(c,0,sizeof(*c)); c->brightness=50; c->brightness_from=c->brightness_to=5000;
 c->brightness_start=now; c->demo_ms=2000; c->selected=color_unpack(0xFF0000);
 color_fade_set(&c->fade,c->selected,now,FADE_MS);
}
void touch_controller_step(touch_controller_t *c,const touch_event_t *e,uint32_t now) {
 /* Settle completed ramps so a long untouched session cannot replay them at
  * the next 32-bit timestamp wrap. The task calls this every 5 ms. */
 if(c->fade.duration && now-c->fade.start>=c->fade.duration) { c->fade.from=c->fade.to; c->fade.duration=0; }
 if(now-c->brightness_start>=FADE_MS) c->brightness_from=c->brightness_to;
 /* B1 wins simultaneous presses. No B2 action or slider jump on that frame. */
 if(e->pressed[0]) {
  c->mode=(touch_mode_t)((c->mode+1)%MODE_COUNT); c->selection=0;
  if(c->mode==MODE_DEMO) { c->demo_start=now; c->demo_index=0; select_color(c,color_unpack(color_presets[0].hex),now,c->demo_ms); }
  return;
 }
 if(e->slider_down) {
  switch(c->mode) {
  case MODE_WHEEL: select_color(c,color_from_hsv((hsv_t){color_slider_hue(e->position),255,255}),now,FADE_MS); break;
  case MODE_PRESETS: c->selection=(uint16_t)((e->position*6u)/1001u); break;
  case MODE_BRIGHTNESS: {
   uint8_t b=(uint8_t)((e->position+5u)/10u);
   if(b!=c->brightness) set_brightness(c,b,now);
   break;
  }
  case MODE_CUSTOM: c->selection=(uint16_t)((e->position*custom_preset_count)/1001u); break;
  case MODE_DEMO: c->demo_ms=300u+(uint32_t)e->position*9700u/1000u; break;
  default: break;
  }
 }
 if(e->pressed[1]) {
  switch(c->mode) {
  case MODE_PRESETS: select_color(c,color_unpack(color_presets[c->category*6u+c->selection].hex),now,FADE_MS); break;
  case MODE_CUSTOM: select_color(c,custom_presets[c->selection],now,FADE_MS); break;
  default: set_brightness(c,c->brightness>=100?0:(uint8_t)(((c->brightness/25u)+1u)*25u),now); break;
  }
 }
 /* Releasing the slider in preset mode advances the category only if B2 is held.
  * This keeps ordinary browsing stable and allows category selection without a display. */
 if(c->mode==MODE_PRESETS && e->slider_released && e->down[1]) { c->category=(c->category+1u)%5u; c->selection=0; }
 if(c->mode==MODE_DEMO && now-c->demo_start>=c->demo_ms) {
  c->demo_start=now; c->demo_index=(c->demo_index+1u)%color_preset_count;
  select_color(c,color_unpack(color_presets[c->demo_index].hex),now,c->demo_ms);
 }
}
void touch_controller_levels(const touch_controller_t *c,uint32_t now,uint16_t out[3]) {
 rgb_t rgb=color_fade_value(&c->fade,now); uint32_t b=brightness_now(c,now);
 out[0]=(uint16_t)(((uint32_t)color_gamma(rgb.r)*b+5000u)/10000u);
 out[1]=(uint16_t)(((uint32_t)color_gamma(rgb.g)*b+5000u)/10000u);
 out[2]=(uint16_t)(((uint32_t)color_gamma(rgb.b)*b+5000u)/10000u);
}
