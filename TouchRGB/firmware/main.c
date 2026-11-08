#include "FreeRTOS.h"
#include "task.h"
#include "cybsp.h"
#include "cyhal.h"
#include "capsense_input.h"
#include "touch_controller.h"
#include "rgb_output.h"
#include <stdio.h>
static cyhal_uart_t uart;
static bool uart_ready;
static volatile unsigned fault_code;
static void halt(unsigned code) {
 fault_code=code; taskDISABLE_INTERRUPTS(); rgb_output_off(); for(;;) __WFI();
}
void vApplicationMallocFailedHook(void) { halt(1); }
void vApplicationStackOverflowHook(TaskHandle_t t,char *n) { (void)t; (void)n; halt(2); }
static void controller_task(void *arg) {
 (void)arg; touch_filter_t filter={0}; touch_event_t event={0}; touch_controller_t controller;
 if(!capsense_input_init()) halt(3);
 touch_controller_init(&controller,(uint32_t)xTaskGetTickCount());
 TickType_t wake=xTaskGetTickCount(); uint32_t report=0;
 char tx[192]; size_t pending=0,sent=0;
 for(;;) {
  uint32_t now=(uint32_t)xTaskGetTickCount()*portTICK_PERIOD_MS;
  touch_raw_t raw; int result=capsense_input_poll(now,&raw);
  if(result<0) halt(4);
  if(result>0) event=capsense_filter(&filter,raw,now);
  else { event.pressed[0]=event.pressed[1]=false; event.released[0]=event.released[1]=false; event.slider_pressed=event.slider_released=false; }
  touch_controller_step(&controller,&event,now);
  uint16_t levels[3]; touch_controller_levels(&controller,now,levels);
  if(!rgb_output_write(levels)) halt(5);
  if(uart_ready) {
   if(sent==pending && now-report>=500u) {
    report=now; sent=0;
    int n=snprintf(tx,sizeof(tx),"TouchRGB mode=%u category=%u slot=%u RGB=%06lX brightness=%u B1=%u B2=%u slider=%d speed_ms=%lu\r\n",
     (unsigned)controller.mode+1u,(unsigned)controller.category,(unsigned)controller.selection,
     (unsigned long)color_pack(controller.selected),(unsigned)controller.brightness,
     (unsigned)event.down[0],(unsigned)event.down[1],event.slider_down?(int)event.position:-1,(unsigned long)controller.demo_ms);
    pending=n>0 && n<(int)sizeof(tx)?(size_t)n:0;
   }
   size_t n=cyhal_uart_writable(&uart); if(n>pending-sent) n=pending-sent;
   if(n && cyhal_uart_write(&uart,tx+sent,&n)==CY_RSLT_SUCCESS) sent+=n;
  }
  vTaskDelayUntil(&wake,pdMS_TO_TICKS(5));
 }
}
int main(void) {
 if(cybsp_init()!=CY_RSLT_SUCCESS) halt(6);
 __enable_irq();
 if(!rgb_output_init()) halt(7);
 const cyhal_uart_cfg_t cfg={.data_bits=8,.stop_bits=1,.parity=CYHAL_UART_PARITY_NONE};
 if(cyhal_uart_init(&uart,CYBSP_DEBUG_UART_TX,CYBSP_DEBUG_UART_RX,NC,NC,NULL,&cfg)==CY_RSLT_SUCCESS)
  uart_ready=cyhal_uart_set_baud(&uart,115200,NULL)==CY_RSLT_SUCCESS;
 if(xTaskCreate(controller_task,"TouchRGB",1024,NULL,4,NULL)!=pdPASS) halt(8);
 vTaskStartScheduler(); halt(9); return 0;
}
