#include "FreeRTOS.h"
#include "cybsp.h"
#include "cycfg_capsense.h"
#include "cyhal.h"
#include "inference.h"
#include "model_data.h"
#include "queue.h"
#include "signal.h"
#include "task.h"
#include "wire.h"
#include <string.h>
typedef struct {
  uint8_t type;
  uint16_t len;
  uint8_t p[512];
} message;
typedef struct {
  uint16_t seq, len;
  uint8_t type, p[448];
} command;
typedef struct {
  uint32_t id, ms, us;
  float p[8], features[6];
  uint8_t prediction, flags;
} result;
static QueueHandle_t rawq, windowq, resultq, txq, cmdq;
static cyhal_uart_t uart;
/* IRQ-backed ring absorbs commands while telemetry drains the TX FIFO. */
static uint8_t uart_rx_buffer[1024];
static TaskHandle_t tasks[5];
static volatile uint32_t drops, fault;
static volatile uint16_t confidence = 800;
static volatile uint32_t acquire_beat, preprocess_beat, infer_beat,
    dispatch_beat;
static void halt(uint32_t code) {
  fault = code;
  taskDISABLE_INTERRUPTS();
  for (;;)
    __WFI();
}
void vApplicationMallocFailedHook(void) { halt(1); }
void vApplicationStackOverflowHook(TaskHandle_t t, char *n) {
  (void)t;
  (void)n;
  halt(2);
}
static void put16(uint8_t *p, uint16_t x) {
  p[0] = x;
  p[1] = x >> 8;
}
static void put32(uint8_t *p, uint32_t x) {
  for (unsigned i = 0; i < 4; i++)
    p[i] = x >> (8 * i);
}
static void drop(void) {
  taskENTER_CRITICAL();
  drops++;
  taskEXIT_CRITICAL();
}
static void post(message *m) {
  if (xQueueSend(txq, m, 0) != pdTRUE)
    drop();
}
static void ack(uint16_t seq, uint8_t type, uint8_t status) {
  message m = {.type = 128, .len = 4};
  put16(m.p, seq);
  m.p[2] = type;
  m.p[3] = status;
  post(&m);
}
static void cap_irq(void) {
  Cy_CapSense_InterruptHandler(CYBSP_CSD_HW, &cy_capsense_context);
}
static void acquisition(void *arg) {
  (void)arg;
  if (Cy_CapSense_Init(&cy_capsense_context) != CYRET_SUCCESS)
    halt(3);
  cy_stc_sysint_t irq = {.intrSrc = csd_interrupt_IRQn, .intrPriority = 5};
  if (Cy_SysInt_Init(&irq, cap_irq) != CY_SYSINT_SUCCESS)
    halt(4);
  NVIC_ClearPendingIRQ(csd_interrupt_IRQn);
  NVIC_EnableIRQ(csd_interrupt_IRQn);
  if (Cy_CapSense_Enable(&cy_capsense_context) != CYRET_SUCCESS)
    halt(5);
  TickType_t wake = xTaskGetTickCount();
  for (;;) {
    if (Cy_CapSense_ScanAllWidgets(&cy_capsense_context) != CYRET_SUCCESS)
      halt(6);
    TickType_t start = xTaskGetTickCount();
    while (Cy_CapSense_IsBusy(&cy_capsense_context) != CY_CAPSENSE_NOT_BUSY) {
      if (xTaskGetTickCount() - start > pdMS_TO_TICKS(100))
        halt(7);
      vTaskDelay(1);
    }
    if (Cy_CapSense_ProcessAllWidgets(&cy_capsense_context) != CYRET_SUCCESS)
      halt(8);
    cs_sample s = {.ms = xTaskGetTickCount() * portTICK_PERIOD_MS};
    unsigned k = 0;
    for (unsigned w = 0; w < 3; w++)
      for (unsigned j = 0; j < (w == 2 ? 5 : 1); j++) {
        const cy_stc_capsense_sensor_context_t *sns =
            &cy_capsense_context.ptrWdConfig[w].ptrSnsContext[j];
        s.raw[k] = sns->raw;
        s.base[k++] = sns->bsln;
      }
    if (xQueueSend(rawq, &s, 0) != pdTRUE)
      drop();
    acquire_beat = xTaskGetTickCount();
    vTaskDelayUntil(&wake, pdMS_TO_TICKS(20));
  }
}
static void preprocessing(void *arg) {
  (void)arg;
  cs_segment seg = {0};
  cs_sample s;
  cs_window w;
  uint32_t previous = 0;
  for (;;)
    if (xQueueReceive(rawq, &s, pdMS_TO_TICKS(100)) == pdTRUE) {
      if (previous && s.ms - previous > 40)
        memset(&seg, 0, sizeof(seg));
      previous = s.ms;
      uint8_t x[7];
      cs_normalize(&s, x);
      message m = {.type = 1, .len = 39};
      put32(m.p, s.ms);
      for (unsigned i = 0; i < 7; i++) {
        put16(m.p + 4 + 2 * i, s.raw[i]);
        put16(m.p + 18 + 2 * i, s.base[i]);
        m.p[32 + i] = x[i];
      }
      post(&m);
      if (cs_segment_step(&seg, x, s.ms, &w) &&
          xQueueSend(windowq, &w, 0) != pdTRUE)
        drop();
      preprocess_beat = xTaskGetTickCount();
    }
}
static void inference(void *arg) {
  (void)arg;
  if (cs_model_init())
    halt(20);
  CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
  DWT->CYCCNT = 0;
  DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
  cs_window w;
  uint32_t id = 0;
  command c;
  for (;;) {
    if (xQueueReceive(cmdq, &c, 0) == pdTRUE) {
      float p[8];
      int code = cs_model_run(c.p, p);
      ack(c.seq, c.type, code ? 3 : 0);
      if (!code) {
        message m = {.type = 4, .len = 34};
        put16(m.p, c.seq);
        memcpy(m.p + 2, p, 32);
        post(&m);
      }
    }
    if (xQueueReceive(windowq, &w, pdMS_TO_TICKS(10)) == pdTRUE) {
      result e = {.id = ++id, .ms = w.ms, .flags = w.truncated};
      memcpy(e.features, w.features, sizeof(e.features));
      uint32_t start = DWT->CYCCNT;
      int code = cs_model_run(&w.x[0][0], e.p);
      e.us = (uint32_t)(((uint64_t)(DWT->CYCCNT - start) * 1000000) /
                        SystemCoreClock);
      unsigned best = 0, second = 1;
      if (e.p[1] > e.p[0]) {
        best = 1;
        second = 0;
      }
      for (unsigned i = 2; i < 8; i++) {
        if (e.p[i] > e.p[best]) {
          second = best;
          best = i;
        } else if (e.p[i] > e.p[second])
          second = i;
      }
      e.prediction = (uint8_t)best;
      if (code || w.truncated || !CS_MODEL_TRAINED ||
          e.p[best] < confidence / 1000.f || e.p[best] - e.p[second] < .15f)
        e.prediction = 7;
      if (!CS_MODEL_TRAINED)
        e.flags |= 2;
      if (code)
        e.flags |= 4;
      if (xQueueSend(resultq, &e, 0) != pdTRUE)
        drop();
    }
    infer_beat = xTaskGetTickCount();
  }
}
static void dispatch(void *arg) {
  (void)arg;
  result e;
  for (;;) {
    if (xQueueReceive(resultq, &e, pdMS_TO_TICKS(100)) == pdTRUE) {
      cyhal_gpio_write(CYBSP_LED_RGB_RED, e.prediction == 7
                                              ? CYBSP_LED_STATE_ON
                                              : CYBSP_LED_STATE_OFF);
      cyhal_gpio_write(CYBSP_LED_RGB_GREEN,
                       e.prediction != 7 && e.p[e.prediction] >= .9f
                           ? CYBSP_LED_STATE_ON
                           : CYBSP_LED_STATE_OFF);
      cyhal_gpio_write(CYBSP_LED_RGB_BLUE,
                       e.prediction != 7 && e.p[e.prediction] < .9f
                           ? CYBSP_LED_STATE_ON
                           : CYBSP_LED_STATE_OFF);
      message m = {.type = 2, .len = 74};
      put32(m.p, e.id);
      put32(m.p + 4, e.ms);
      m.p[8] = e.prediction;
      m.p[9] = e.flags;
      put32(m.p + 10, e.us);
      put32(m.p + 14, drops);
      memcpy(m.p + 18, e.p, 32);
      memcpy(m.p + 50, e.features, 24);
      post(&m);
    }
    dispatch_beat = xTaskGetTickCount();
  }
}
static void send_message(message *m, uint16_t *seq) {
  uint8_t bytes[522];
  size_t total = cs_frame(m->type, (*seq)++, m->p, m->len, bytes), sent = 0;
  TickType_t start = xTaskGetTickCount();
  while (sent < total) {
    size_t n = total - sent;
    if (cyhal_uart_write(&uart, bytes + sent, &n) != CY_RSLT_SUCCESS)
      halt(9);
    sent += n;
    if (sent < total) {
      if (xTaskGetTickCount() - start > pdMS_TO_TICKS(100))
        halt(10);
      vTaskDelay(1);
    }
  }
}
static void communication(void *arg) {
  (void)arg;
  static cs_decoder decoder;
  static cs_packet packet;
  static command c;
  static message m;
  uint16_t seq = 0;
  TickType_t last = 0, health = 0;
  // Commands are idempotent; repeated parity requests recompute the same
  // output.
  for (;;) {
    for (unsigned budget = 0; budget < 512 && cyhal_uart_readable(&uart);
         budget++) {
      uint8_t b;
      if (cyhal_uart_getc(&uart, &b, 0) != CY_RSLT_SUCCESS)
        break;
      if (xTaskGetTickCount() - last > pdMS_TO_TICKS(200))
        decoder.used = 0;
      last = xTaskGetTickCount();
      if (cs_receive(&decoder, b, &packet)) {
        if (packet.type == 19 && packet.len == 0) {
          ack(packet.seq, packet.type, 0);
          message identity = {.type = 5, .len = 64};
          memcpy(identity.p, CS_MODEL_SHA256, 64);
          post(&identity);
        } else if (packet.type == 16 && packet.len == 0)
          ack(packet.seq, packet.type, 0);
        else if (packet.type == 17 && packet.len == 2) {
          unsigned v = packet.payload[0] | packet.payload[1] << 8;
          if (v >= 500 && v <= 990) {
            confidence = v;
            ack(packet.seq, packet.type, 0);
          } else
            ack(packet.seq, packet.type, 1);
        } else if (packet.type == 18 && packet.len == 448) {
          int valid = 1;
          for (unsigned i = 0; i < 448; i++)
            if (packet.payload[i] > 127)
              valid = 0;
          if (valid) {
            c.type = packet.type;
            c.seq = packet.seq;
            c.len = 448;
            memcpy(c.p, packet.payload, 448);
            if (xQueueSend(cmdq, &c, 0) != pdTRUE)
              ack(packet.seq, packet.type, 2);
          } else
            ack(packet.seq, packet.type, 1);
        } else
          ack(packet.seq, packet.type, 1);
      }
    }
    if (xQueueReceive(txq, &m, 0) == pdTRUE)
      send_message(&m, &seq);
    if (xTaskGetTickCount() - health >= pdMS_TO_TICKS(1000)) {
      health = xTaskGetTickCount();
      m.type = 3;
      m.len = 26;
      put32(m.p, health);
      put32(m.p + 4, drops);
      put32(m.p + 8, cs_arena_used());
      put32(m.p + 12, CS_MODEL_TRAINED);
      for (unsigned i = 0; i < 5; i++)
        put16(m.p + 16 + 2 * i,
              (uint16_t)uxTaskGetStackHighWaterMark(tasks[i]));
      send_message(&m, &seq);
      if (acquire_beat && health - acquire_beat > 500)
        halt(21);
      if (preprocess_beat && health - preprocess_beat > 500)
        halt(22);
      if (infer_beat && health - infer_beat > 500)
        halt(23);
      if (dispatch_beat && health - dispatch_beat > 500)
        halt(24);
    }
    vTaskDelay(1);
  }
}
int main(void) {
  if (cybsp_init() != CY_RSLT_SUCCESS)
    for (;;)
      __WFI();
  __enable_irq();
  cyhal_uart_cfg_t cfg = {
      .data_bits = 8, .stop_bits = 1, .parity = CYHAL_UART_PARITY_NONE};
  if (cyhal_uart_init(&uart, CYBSP_DEBUG_UART_TX, CYBSP_DEBUG_UART_RX, NC, NC,
                      NULL, &cfg) != CY_RSLT_SUCCESS)
    halt(11);
  if (cyhal_uart_set_baud(&uart, 115200, NULL) != CY_RSLT_SUCCESS)
    halt(12);
  if (cyhal_uart_config_software_buffer(
          &uart, uart_rx_buffer, sizeof(uart_rx_buffer)) != CY_RSLT_SUCCESS)
    halt(25);
  const cyhal_gpio_t pins[] = {CYBSP_LED_RGB_RED, CYBSP_LED_RGB_GREEN,
                               CYBSP_LED_RGB_BLUE};
  for (unsigned i = 0; i < 3; i++)
    if (cyhal_gpio_init(pins[i], CYHAL_GPIO_DIR_OUTPUT, CYHAL_GPIO_DRIVE_STRONG,
                        CYBSP_LED_STATE_OFF) != CY_RSLT_SUCCESS)
      halt(13);
  rawq = xQueueCreate(8, sizeof(cs_sample));
  windowq = xQueueCreate(2, sizeof(cs_window));
  resultq = xQueueCreate(4, sizeof(result));
  txq = xQueueCreate(12, sizeof(message));
  cmdq = xQueueCreate(2, sizeof(command));
  if (!rawq || !windowq || !resultq || !txq || !cmdq)
    halt(14);
  if (xTaskCreate(acquisition, "acquisition", 768, 0, 5, &tasks[0]) != pdPASS ||
      xTaskCreate(preprocessing, "preprocess", 1536, 0, 4, &tasks[1]) !=
          pdPASS ||
      xTaskCreate(inference, "inference", 2048, 0, 2, &tasks[2]) != pdPASS ||
      xTaskCreate(dispatch, "dispatch", 768, 0, 3, &tasks[3]) != pdPASS ||
      xTaskCreate(communication, "uart", 1024, 0, 3, &tasks[4]) != pdPASS)
    halt(15);
  vTaskStartScheduler();
  halt(16);
  return 0;
}
