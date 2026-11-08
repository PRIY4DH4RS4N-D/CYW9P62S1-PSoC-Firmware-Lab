#include "rgb_output.h"
#include "cybsp.h"
#include "cyhal.h"
static cyhal_pwm_t pwm[3];
static unsigned allocated;
static bool ready;
static uint16_t last_levels[3];
static const cyhal_gpio_t pins[]={CYBSP_LED_RGB_RED,CYBSP_LED_RGB_GREEN,CYBSP_LED_RGB_BLUE};
void rgb_output_off(void) {
 ready=false;
 for(unsigned i=0;i<allocated;i++) { (void)cyhal_pwm_stop(&pwm[i]); cyhal_pwm_free(&pwm[i]); }
 allocated=0;
 /* LED5 common anode: a HIGH cathode is off, even after a PWM error. */
 Cy_GPIO_Pin_FastInit(GPIO_PRT1,1,CY_GPIO_DM_STRONG,1,HSIOM_SEL_GPIO);
 Cy_GPIO_Pin_FastInit(GPIO_PRT0,5,CY_GPIO_DM_STRONG,1,HSIOM_SEL_GPIO);
 Cy_GPIO_Pin_FastInit(GPIO_PRT7,3,CY_GPIO_DM_STRONG,1,HSIOM_SEL_GPIO);
}
bool rgb_output_init(void) {
 rgb_output_off();
 for(unsigned i=0;i<3;i++) {
  /* HAL supports LINE_COMPL pins as the primary output and normalizes duty.
   * Explicit inversion gives active-low light duty on this common-anode LED. */
  if(cyhal_pwm_init_adv(&pwm[i],pins[i],NC,CYHAL_PWM_LEFT_ALIGN,true,0,true,NULL)!=CY_RSLT_SUCCESS) goto fail;
  allocated++;
  if(cyhal_pwm_set_duty_cycle(&pwm[i],0.0f,1000)!=CY_RSLT_SUCCESS) goto fail;
  last_levels[i]=0;
 }
 for(unsigned i=0;i<3;i++) if(cyhal_pwm_start(&pwm[i])!=CY_RSLT_SUCCESS) goto fail;
 ready=true; return true;
fail: rgb_output_off(); return false;
}
bool rgb_output_write(const uint16_t levels[3]) {
 if(!ready) return false;
 for(unsigned i=0;i<3;i++) {
  if(levels[i]==last_levels[i]) continue;
  if(cyhal_pwm_set_duty_cycle(&pwm[i],100.0f*((float)levels[i]/65535.0f),1000)!=CY_RSLT_SUCCESS) {
   rgb_output_off(); return false;
  }
  last_levels[i]=levels[i];
 }
 return true;
}
