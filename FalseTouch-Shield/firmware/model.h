#pragma once
/* Replaced ONLY by ml/train.py --install after recorded-data training. */
#define FT_MODEL_TRAINED 0
#define FT_MODEL_ID "untrained"
static inline unsigned char ft_predict(const float *f,float *confidence) { (void)f;*confidence=0;return 255; }
