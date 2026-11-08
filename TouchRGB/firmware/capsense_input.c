#include "capsense_input.h"
static void debounce(touch_debounce_t *b,bool raw,uint32_t now,uint32_t delay) {
 if(raw!=b->candidate) { b->candidate=raw; b->since=now; }
 if(b->stable!=b->candidate && now-b->since>=delay) b->stable=b->candidate;
}
touch_event_t capsense_filter(touch_filter_t *f,touch_raw_t r,uint32_t now) {
 touch_event_t e={0}; bool raw[2]={r.b1,r.b2};
 for(unsigned i=0;i<2;i++) {
  bool prev=f->buttons[i].stable; debounce(&f->buttons[i],raw[i],now,30);
  e.down[i]=f->buttons[i].stable; e.pressed[i]=!prev && e.down[i]; e.released[i]=prev && !e.down[i];
 }
 bool prev=f->slider.stable; debounce(&f->slider,r.slider,now,20);
 /* Keep the last valid position through release debounce. Never move on invalid data. */
 if(r.slider) f->position=r.position>1000?1000:r.position;
 e.slider_down=f->slider.stable; e.slider_pressed=!prev && e.slider_down;
 e.slider_released=prev && !e.slider_down; e.position=f->position; return e;
}
#ifndef TOUCHRGB_HOST
#include "cybsp.h"
#include "cycfg_capsense.h"
static uint32_t scan_start;
static bool scanning;
static void cap_irq(void) { Cy_CapSense_InterruptHandler(CYBSP_CSD_HW,&cy_capsense_context); }
bool capsense_input_init(void) {
 if(Cy_CapSense_Init(&cy_capsense_context)!=CYRET_SUCCESS) return false;
 const cy_stc_sysint_t irq={.intrSrc=csd_interrupt_IRQn,.intrPriority=5};
 if(Cy_SysInt_Init(&irq,cap_irq)!=CY_SYSINT_SUCCESS) return false;
 NVIC_ClearPendingIRQ(csd_interrupt_IRQn); NVIC_EnableIRQ(csd_interrupt_IRQn);
 return Cy_CapSense_Enable(&cy_capsense_context)==CYRET_SUCCESS;
}
int capsense_input_poll(uint32_t now,touch_raw_t *out) {
 if(!scanning) {
  if(Cy_CapSense_ScanAllWidgets(&cy_capsense_context)!=CYRET_SUCCESS) return -1;
  scanning=true; scan_start=now; return 0;
 }
 if(Cy_CapSense_IsBusy(&cy_capsense_context)!=CY_CAPSENSE_NOT_BUSY) return now-scan_start>=100u?-1:0;
 if(Cy_CapSense_ProcessAllWidgets(&cy_capsense_context)!=CYRET_SUCCESS) return -1;
 scanning=false; *out=(touch_raw_t){0};
 out->b1=Cy_CapSense_IsWidgetActive(CY_CAPSENSE_BUTTON0_WDGT_ID,&cy_capsense_context)!=0;
 out->b2=Cy_CapSense_IsWidgetActive(CY_CAPSENSE_BUTTON1_WDGT_ID,&cy_capsense_context)!=0;
 const cy_stc_capsense_touch_t *t=Cy_CapSense_GetTouchInfo(CY_CAPSENSE_LINEARSLIDER0_WDGT_ID,&cy_capsense_context);
 uint32_t max=cy_capsense_context.ptrWdConfig[CY_CAPSENSE_LINEARSLIDER0_WDGT_ID].xResolution;
 if(t && t->numPosition==1 && max && t->ptrPosition && t->ptrPosition[0].x<=max) {
  out->slider=true; out->position=(uint16_t)((1000u*t->ptrPosition[0].x+max/2u)/max);
 }
 return 1;
}
#endif
