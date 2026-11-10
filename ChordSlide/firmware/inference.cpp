#include "inference.h"
#include "model_data.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/schema/schema_generated.h"
#include <cmath>
#include <cstring>
alignas(16) static uint8_t arena[24576];
static tflite::MicroInterpreter *engine;
static tflite::MicroMutableOpResolver<6> resolver;
extern "C" int cs_model_init(void) {
  const tflite::Model *m = tflite::GetModel(cs_model_data);
  if (m->version() != TFLITE_SCHEMA_VERSION)
    return 1;
  if (resolver.AddConv2D() != kTfLiteOk ||
      resolver.AddAveragePool2D() != kTfLiteOk ||
      resolver.AddReshape() != kTfLiteOk ||
      resolver.AddFullyConnected() != kTfLiteOk ||
      resolver.AddSoftmax() != kTfLiteOk)
    return 2;
  static tflite::MicroInterpreter instance(m, resolver, arena, sizeof(arena));
  engine = &instance;
  if (engine->AllocateTensors() != kTfLiteOk)
    return 3;
  if (engine->input(0)->type != kTfLiteInt8 || engine->input(0)->bytes != 448 ||
      engine->output(0)->type != kTfLiteInt8 || engine->output(0)->bytes != 8)
    return 4;
  return 0;
}
extern "C" int cs_model_run(const uint8_t *x, float p[8]) {
  if (!engine)
    return 1;
  TfLiteTensor *in = engine->input(0);
  for (unsigned i = 0; i < 448; i++) {
    int v = (int)std::lround((x[i] / 127.f) / in->params.scale) +
            in->params.zero_point;
    in->data.int8[i] = (int8_t)(v < -128 ? -128 : v > 127 ? 127 : v);
  }
  if (engine->Invoke() != kTfLiteOk)
    return 2;
  TfLiteTensor *out = engine->output(0);
  for (unsigned i = 0; i < 8; i++)
    p[i] = (out->data.int8[i] - out->params.zero_point) * out->params.scale;
  return 0;
}
extern "C" unsigned cs_arena_used(void) {
  return engine ? (unsigned)engine->arena_used_bytes() : 0;
}
