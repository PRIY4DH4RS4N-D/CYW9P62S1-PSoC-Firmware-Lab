#pragma once
#include <stdint.h>
#include <stdbool.h>
bool rgb_output_init(void);
bool rgb_output_write(const uint16_t levels[3]);
/* Emergency shutdown latches all channels off until reset. */
void rgb_output_off(void);
