#pragma once
#include "cybsp.h"
typedef int cyhal_gpio_t;
typedef struct { int pin; } cyhal_pwm_t;
#define CY_RSLT_SUCCESS 0
#define CYHAL_PWM_LEFT_ALIGN 0
#define NC -1
int cyhal_pwm_init_adv(cyhal_pwm_t *,int,int,int,bool,uint32_t,bool,void *);
int cyhal_pwm_set_duty_cycle(cyhal_pwm_t *,float,uint32_t);
int cyhal_pwm_start(cyhal_pwm_t *);
int cyhal_pwm_stop(cyhal_pwm_t *);
void cyhal_pwm_free(cyhal_pwm_t *);
