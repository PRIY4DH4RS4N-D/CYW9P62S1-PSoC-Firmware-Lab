/* Call-contract tests; this does not simulate PSoC electrical behavior. */
#include "cyhal.h"
#include "rgb_output.h"
#include <assert.h>
#include <stdio.h>
static int init_calls,free_calls,starts,gpio_off,fail_init=-1,fail_write=-1,writes;
static float duties[3];
void Cy_GPIO_Pin_FastInit(int port,int pin,int mode,int value,int hsiom) {
 assert((port==1 && pin==1)||(port==0 && pin==5)||(port==7 && pin==3));
 assert(mode==CY_GPIO_DM_STRONG && value==1 && hsiom==HSIOM_SEL_GPIO); gpio_off++;
}
int cyhal_pwm_init_adv(cyhal_pwm_t *p,int pin,int compl,int align,bool continuous,uint32_t dead,bool invert,void *clock) {
 const int expected[]={11,5,73}; int i=init_calls++;
 assert(pin==expected[i%3] && compl==NC && align==CYHAL_PWM_LEFT_ALIGN && continuous && dead==0 && invert && clock==NULL);
 if(i==fail_init) return 1;
 p->pin=pin; return 0;
}
int cyhal_pwm_set_duty_cycle(cyhal_pwm_t *p,float duty,uint32_t frequency) {
 assert(duty>=0 && duty<=100 && frequency==1000);
 int i=p->pin==11?0:p->pin==5?1:2;
 duties[i]=duty; return writes++==fail_write?1:0;
}
int cyhal_pwm_start(cyhal_pwm_t *p) { (void)p; starts++; return 0; }
int cyhal_pwm_stop(cyhal_pwm_t *p) { (void)p; return 0; }
void cyhal_pwm_free(cyhal_pwm_t *p) { (void)p; free_calls++; }
int main(void) {
 assert(rgb_output_init()); assert(starts==3 && duties[0]==0 && duties[1]==0 && duties[2]==0);
 uint16_t levels[]={0,32768,65535}; assert(rgb_output_write(levels));
 assert(duties[0]==0 && duties[1]>49.99f && duties[1]<50.01f && duties[2]==100);
 int before=writes; assert(rgb_output_write(levels)); assert(writes==before);
 levels[0]=1; fail_write=writes; assert(!rgb_output_write(levels)); assert(free_calls==3 && gpio_off==6);
 assert(!rgb_output_write(levels));
 for(int fail=0;fail<3;fail++) {
  init_calls=0; free_calls=0; starts=0; writes=0; fail_init=fail; fail_write=-1;
  assert(!rgb_output_init()); assert(free_calls==fail && starts==0);
 }
 puts("PASS: PWM pin/inversion/duty contract, off startup, runtime error shutdown, partial init cleanup");
 return 0;
}
