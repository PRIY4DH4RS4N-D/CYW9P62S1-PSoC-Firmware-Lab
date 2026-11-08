#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#define CYBSP_LED_RGB_RED 11
#define CYBSP_LED_RGB_GREEN 5
#define CYBSP_LED_RGB_BLUE 73
#define GPIO_PRT1 1
#define GPIO_PRT0 0
#define GPIO_PRT7 7
#define CY_GPIO_DM_STRONG 6
#define HSIOM_SEL_GPIO 0
void Cy_GPIO_Pin_FastInit(int port,int pin,int mode,int value,int hsiom);
