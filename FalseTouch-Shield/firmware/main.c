#include "cybsp.h"
#include "cyhal.h"
#include "cycfg_capsense.h"
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include "core.h"
#include "model.h"
#include <string.h>
typedef struct { uint8_t type,len; uint8_t p[128]; } message;
typedef struct { uint8_t type,len;uint16_t seq;uint8_t p[24]; } command;
static QueueHandle_t telemetry,events,commands;
static cyhal_uart_t uart;
static cyhal_wdt_t watchdog;
static volatile uint32_t fault,drops,scan_beat,uart_beat;
static uint16_t txseq,threshold=60;
static void halt(uint32_t code){fault=code;taskDISABLE_INTERRUPTS();for(;;)__WFI();}
void vApplicationMallocFailedHook(void){halt(1);}
void vApplicationStackOverflowHook(TaskHandle_t t,char *n){(void)t;(void)n;halt(2);}
static void cap_irq(void){Cy_CapSense_InterruptHandler(CYBSP_CSD_HW,&cy_capsense_context);}
static void put16(uint8_t *p,uint16_t v){p[0]=v;p[1]=v>>8;}
static void put32(uint8_t *p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=v>>(8*i);}
static void publish(QueueHandle_t q,message *m){if(xQueueSend(q,m,0)!=pdTRUE){taskENTER_CRITICAL();drops++;taskEXIT_CRITICAL();}}
static void led(uint8_t prediction){
 cyhal_gpio_write(CYBSP_LED_RGB_RED,(prediction==FT_GRAZE||prediction==FT_WIDE)?CYBSP_LED_STATE_ON:CYBSP_LED_STATE_OFF);
 cyhal_gpio_write(CYBSP_LED_RGB_GREEN,prediction<2?CYBSP_LED_STATE_ON:CYBSP_LED_STATE_OFF);
 cyhal_gpio_write(CYBSP_LED_RGB_BLUE,prediction==255?CYBSP_LED_STATE_ON:CYBSP_LED_STATE_OFF);
}
static void acquisition(void *arg){
 (void)arg;ft_segment segment={0};float f[6];uint32_t event_id=0;uint8_t recalibrate=0;
 if(Cy_CapSense_Init(&cy_capsense_context)!=CYRET_SUCCESS)halt(3);
 cy_stc_sysint_t irq={.intrSrc=csd_interrupt_IRQn,.intrPriority=5};
 if(Cy_SysInt_Init(&irq,cap_irq)!=CY_SYSINT_SUCCESS)halt(4);
 NVIC_ClearPendingIRQ(csd_interrupt_IRQn);NVIC_EnableIRQ(csd_interrupt_IRQn);
 if(Cy_CapSense_Enable(&cy_capsense_context)!=CYRET_SUCCESS)halt(5);
 TickType_t wake=xTaskGetTickCount();
 for(;;){
  command c;
  while(xQueueReceive(commands,&c,0)==pdTRUE){
   message a={.type=0x80,.len=4};put16(a.p,c.seq);a.p[2]=c.type;a.p[3]=0;
   if(c.type==0x10 && c.len==0){}
   else if(c.type==0x11 && c.len==2){uint16_t t=c.p[0]|(c.p[1]<<8);if(t>=10&&t<=4000){threshold=t;memset(&segment,0,sizeof(segment));}else a.p[3]=2;}
   else if(c.type==0x12 && c.len==0){recalibrate=1;memset(&segment,0,sizeof(segment));}
   else if(c.type==0x13 && c.len==24){float v[6],conf;memcpy(v,c.p,24);uint8_t pred=ft_predict(v,&conf);message r={.type=4,.len=7};put16(r.p,c.seq);r.p[2]=pred;memcpy(r.p+3,&conf,4);publish(events,&r);}
   else a.p[3]=1;
   if(recalibrate){
    if(Cy_CapSense_CalibrateAllWidgets(&cy_capsense_context)!=CYRET_SUCCESS)a.p[3]=3;
    else {
     if(Cy_CapSense_ScanAllWidgets(&cy_capsense_context)!=CYRET_SUCCESS)halt(6);
     TickType_t calibration_start=xTaskGetTickCount();
     while(Cy_CapSense_IsBusy(&cy_capsense_context)!=CY_CAPSENSE_NOT_BUSY){
      if(xTaskGetTickCount()-calibration_start>pdMS_TO_TICKS(100))halt(7);
      vTaskDelay(1);
     }
     Cy_CapSense_InitializeAllBaselines(&cy_capsense_context);
     Cy_CapSense_InitializeAllStatuses(&cy_capsense_context);
     Cy_CapSense_InitializeAllFilters(&cy_capsense_context);
    }
    recalibrate=0;
   }
   publish(events,&a);
  }
  if(Cy_CapSense_ScanAllWidgets(&cy_capsense_context)!=CYRET_SUCCESS)halt(6);
  TickType_t start=xTaskGetTickCount();
  while(Cy_CapSense_IsBusy(&cy_capsense_context)!=CY_CAPSENSE_NOT_BUSY){if(xTaskGetTickCount()-start>pdMS_TO_TICKS(100))halt(7);vTaskDelay(1);}
  if(Cy_CapSense_ProcessAllWidgets(&cy_capsense_context)!=CYRET_SUCCESS)halt(8);
  ft_sample s={.ms=xTaskGetTickCount()};
  unsigned k=0;for(unsigned w=0;w<3;w++)for(unsigned j=0;j<(w==2?5:1);j++)s.d[k++]=cy_capsense_context.ptrWdConfig[w].ptrSnsContext[j].diff;
  message m={.type=1,.len=18};put32(m.p,s.ms);for(unsigned i=0;i<7;i++)put16(m.p+4+i*2,s.d[i]);publish(telemetry,&m);
  if(ft_step(&segment,&s,threshold,f)){
   float conf;uint8_t prediction=ft_predict(f,&conf),base=ft_baseline(f);led(prediction);
   message e={.type=2,.len=42};put32(e.p,++event_id);put32(e.p+4,s.ms);memcpy(e.p+8,f,24);
   e.p[32]=prediction;e.p[33]=base;memcpy(e.p+34,&conf,4);put32(e.p+38,drops);publish(events,&e);
  }
  scan_beat=xTaskGetTickCount();vTaskDelayUntil(&wake,pdMS_TO_TICKS(10));
 }
}
static void send_message(message *m){
 uint8_t b[138];size_t total=ft_frame(m->type,txseq++,m->p,m->len,b),sent=0;
 TickType_t start=xTaskGetTickCount();
 while(sent<total){
  size_t n=total-sent;
  if(cyhal_uart_write(&uart,b+sent,&n)!=CY_RSLT_SUCCESS){fault=9;return;}
  sent+=n;
  if(sent<total){if(xTaskGetTickCount()-start>pdMS_TO_TICKS(50)){fault=9;return;}vTaskDelay(1);}
 }
}
static void communication(void *arg){
 (void)arg;ft_decoder decoder={0};ft_packet packet;TickType_t last=0;
 for(;;){
  for(unsigned budget=0;budget<160 && cyhal_uart_readable(&uart);budget++){
   uint8_t byte;if(cyhal_uart_getc(&uart,&byte,0)!=CY_RSLT_SUCCESS)break;
   if(xTaskGetTickCount()-last>200){decoder.used=0;}
   last=xTaskGetTickCount();
   if(ft_receive(&decoder,byte,&packet)){
    if(packet.len<=24){
     command c={.type=packet.type,.len=packet.len,.seq=packet.seq};memcpy(c.p,packet.payload,c.len);
     if(xQueueSend(commands,&c,0)!=pdTRUE){message a={.type=0x80,.len=4};put16(a.p,c.seq);a.p[2]=c.type;a.p[3]=5;send_message(&a);}
    }else{message a={.type=0x80,.len=4};put16(a.p,packet.seq);a.p[2]=packet.type;a.p[3]=1;send_message(&a);}
   }
  }
  message m;if(xQueueReceive(events,&m,0)==pdTRUE)send_message(&m);
  if(xQueueReceive(telemetry,&m,0)==pdTRUE)send_message(&m);
  uart_beat=xTaskGetTickCount();vTaskDelay(pdMS_TO_TICKS(1));
 }
}
static void health(void *arg){(void)arg;for(;;){vTaskDelay(pdMS_TO_TICKS(1000));uint32_t now=xTaskGetTickCount();
 if(now-scan_beat>500||now-uart_beat>500)halt(10);
 message m={.type=3,.len=13};put32(m.p,now);put32(m.p+4,drops);put32(m.p+8,fault);m.p[12]=FT_MODEL_TRAINED;publish(events,&m);
 cyhal_wdt_kick(&watchdog);
}}
int main(void){
 if(cybsp_init()!=CY_RSLT_SUCCESS){for(;;)__WFI();}
 __enable_irq();
 cyhal_uart_cfg_t cfg={.data_bits=8,.stop_bits=1,.parity=CYHAL_UART_PARITY_NONE};
 if(cyhal_uart_init(&uart,CYBSP_DEBUG_UART_TX,CYBSP_DEBUG_UART_RX,NC,NC,NULL,&cfg)!=CY_RSLT_SUCCESS)halt(11);
 if(cyhal_uart_set_baud(&uart,115200,NULL)!=CY_RSLT_SUCCESS)halt(12);
 const cyhal_gpio_t pins[]={CYBSP_LED_RGB_RED,CYBSP_LED_RGB_GREEN,CYBSP_LED_RGB_BLUE};
 for(unsigned i=0;i<3;i++)if(cyhal_gpio_init(pins[i],CYHAL_GPIO_DIR_OUTPUT,CYHAL_GPIO_DRIVE_STRONG,1)!=CY_RSLT_SUCCESS)halt(13);
 if(cyhal_wdt_init(&watchdog,4000)!=CY_RSLT_SUCCESS)halt(17);
 cyhal_wdt_start(&watchdog);
 telemetry=xQueueCreate(16,sizeof(message));events=xQueueCreate(16,sizeof(message));commands=xQueueCreate(8,sizeof(command));
 if(!telemetry||!events||!commands)halt(14);
 if(xTaskCreate(acquisition,"sense",1024,NULL,4,NULL)!=pdPASS||xTaskCreate(communication,"uart",1024,NULL,3,NULL)!=pdPASS||xTaskCreate(health,"health",384,NULL,2,NULL)!=pdPASS)halt(15);
 vTaskStartScheduler();halt(16);return 0;
}

