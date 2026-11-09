#include "FreeRTOS.h"
#include "task.h"
#include "cybsp.h"
#include "cyhal.h"
#include "cycfg_capsense.h"
#include "gesture.h"
#include <stdio.h>
#include <string.h>
static cyhal_uart_t uart;
static uint32_t seq, tx_errors;
static void halt(void) { taskDISABLE_INTERRUPTS(); for (;;) __WFI(); }
void vApplicationMallocFailedHook(void) { halt(); }
void vApplicationStackOverflowHook(TaskHandle_t t, char *n) { (void)t; (void)n; halt(); }
static void cap_irq(void) { Cy_CapSense_InterruptHandler(CYBSP_CSD_HW, &cy_capsense_context); }
/* A single task owns UART. Bounded writes cannot hang sensing indefinitely. */
static void transmit(const char *fields) {
    char line[240];
    int len=snprintf(line,sizeof(line),"{\"v\":1,\"seq\":%lu,%s}\n",(unsigned long)seq++,fields);
    if (len<=0 || len>=(int)sizeof(line)) { tx_errors++; return; }
    size_t sent=0; TickType_t start=xTaskGetTickCount();
    while (sent<(size_t)len) {
        size_t n=(size_t)len-sent;
        if (cyhal_uart_write(&uart,(void *)(line+sent),&n)!=CY_RSLT_SUCCESS) { tx_errors++; return; }
        sent+=n;
        if (xTaskGetTickCount()-start>pdMS_TO_TICKS(50)) { tx_errors++; return; }
        if (sent<(size_t)len) vTaskDelay(1);
    }
}
static void emit(const char *type,int value,char mode,void *u) {
    (void)u; char s[120];
    if (!strcmp(type,"MOVE")) snprintf(s,sizeof(s),"\"type\":\"MOVE\",\"position\":%d,\"mode\":\"%c\"",value,mode);
    else if (!strcmp(type,"MODE")) snprintf(s,sizeof(s),"\"type\":\"MODE\",\"mode\":\"%c\"",mode);
    else if (!strcmp(type,"RELEASE")) snprintf(s,sizeof(s),"\"type\":\"RELEASE\"");
    else if (!strcmp(type,"BUTTON1") || !strcmp(type,"BUTTON2"))
        snprintf(s,sizeof(s),"\"type\":\"BUTTON\",\"button\":%d,\"state\":%d",type[6]-'0',value);
    else snprintf(s,sizeof(s),"\"type\":\"%s\",\"state\":%d",type,value);
    transmit(s);
}
static void touch_task(void *arg) {
    (void)arg; cap_gesture g={0};
    if (Cy_CapSense_Init(&cy_capsense_context)!=CYRET_SUCCESS) halt();
    cy_stc_sysint_t irq={.intrSrc=csd_interrupt_IRQn,.intrPriority=5};
    if (Cy_SysInt_Init(&irq,cap_irq)!=CY_SYSINT_SUCCESS) halt();
    NVIC_ClearPendingIRQ(csd_interrupt_IRQn); NVIC_EnableIRQ(csd_interrupt_IRQn);
    if (Cy_CapSense_Enable(&cy_capsense_context)!=CYRET_SUCCESS) halt();
    transmit("\"type\":\"HELLO\",\"device\":\"CapSlide\",\"controls\":\"toggle-b1-click-b2\"");
    TickType_t wake=xTaskGetTickCount(), health=0;
    for (;;) {
        if (Cy_CapSense_ScanAllWidgets(&cy_capsense_context)!=CYRET_SUCCESS) halt();
        TickType_t start=xTaskGetTickCount();
        while (Cy_CapSense_IsBusy(&cy_capsense_context)!=CY_CAPSENSE_NOT_BUSY) {
            if (xTaskGetTickCount()-start>pdMS_TO_TICKS(100)) halt();
            vTaskDelay(1);
        }
        if (Cy_CapSense_ProcessAllWidgets(&cy_capsense_context)!=CYRET_SUCCESS) halt();
        bool b1=Cy_CapSense_IsWidgetActive(CY_CAPSENSE_BUTTON0_WDGT_ID,&cy_capsense_context)!=0;
        bool b2=Cy_CapSense_IsWidgetActive(CY_CAPSENSE_BUTTON1_WDGT_ID,&cy_capsense_context)!=0;
        cy_stc_capsense_touch_t *touch=Cy_CapSense_GetTouchInfo(CY_CAPSENSE_LINEARSLIDER0_WDGT_ID,&cy_capsense_context);
        int pos=-1;
        uint32_t max=cy_capsense_context.ptrWdConfig[CY_CAPSENSE_LINEARSLIDER0_WDGT_ID].xResolution;
        if (touch && touch->numPosition==1 && max && touch->ptrPosition[0].x<=max)
            pos=(int)((100u*touch->ptrPosition[0].x+max/2u)/max);
        uint32_t ms=xTaskGetTickCount()*portTICK_PERIOD_MS;
        cap_step(&g,ms,b1,b2,pos,emit,NULL);
        if (xTaskGetTickCount()-health>=pdMS_TO_TICKS(500)) {
            health=xTaskGetTickCount(); char s[180];
            snprintf(s,sizeof(s),"\"type\":\"STATUS\",\"controls\":\"toggle-b1-click-b2\",\"b1\":%d,\"b2\":%d,\"position\":%d,\"mode\":\"%c\",\"tx_errors\":%lu",g.b[0].stable,g.b[1].stable,pos,g.vertical?'Y':'X',(unsigned long)tx_errors);
            transmit(s);
        }
        vTaskDelayUntil(&wake,pdMS_TO_TICKS(10));
    }
}
int main(void) {
    if (cybsp_init()!=CY_RSLT_SUCCESS) halt();
    __enable_irq();
    cyhal_uart_cfg_t cfg={.data_bits=8,.stop_bits=1,.parity=CYHAL_UART_PARITY_NONE};
    if (cyhal_uart_init(&uart,CYBSP_DEBUG_UART_TX,CYBSP_DEBUG_UART_RX,NC,NC,NULL,&cfg)!=CY_RSLT_SUCCESS) halt();
    if (cyhal_uart_set_baud(&uart,115200,NULL)!=CY_RSLT_SUCCESS) halt();
    if (xTaskCreate(touch_task,"touch_uart",1024,NULL,4,NULL)!=pdPASS) halt();
    vTaskStartScheduler(); halt(); return 0;
}
