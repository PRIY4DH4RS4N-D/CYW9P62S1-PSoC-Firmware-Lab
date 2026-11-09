#pragma once
#include <math.h>
#define FT_MODEL_TRAINED 0
#define FT_MODEL_ID "synthetic-smoke-only"
static inline unsigned char ft_predict(const float *f,float *confidence) {
 for(int i=0;i<6;i++)if(!isfinite(f[i])){*confidence=0;return 255;}
 if(f[0]<=85.656299591064453) {
  *confidence=1;return 2;
 } else {
  if(f[2]<=2.5) {
   if(f[5]<=67.890703201293945) {
    *confidence=1;return 0;
   } else {
    *confidence=1;return 1;
   }
  } else {
   *confidence=1;return 3;
  }
 }
}
