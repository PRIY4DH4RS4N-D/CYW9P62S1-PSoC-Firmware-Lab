#pragma once
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
int cs_model_init(void);
int cs_model_run(const uint8_t *x, float p[8]);
unsigned cs_arena_used(void);
#ifdef __cplusplus
}
#endif
