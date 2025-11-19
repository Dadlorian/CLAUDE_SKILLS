# TensorFlow Lite Micro Quick Start

## Model Conversion Pipeline

### Python: Train Model
```python
import tensorflow as tf

# Simple model
model = tf.keras.Sequential([
    tf.keras.layers.Dense(16, activation='relu', input_shape=(10,)),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy')
model.fit(X_train, y_train, epochs=10)
```

### Convert to TFLite
```python
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# Enable optimizations
converter.optimizations = [tf.lite.Optimize.DEFAULT]

# Quantize to INT8
def representative_dataset():
    for i in range(100):
        yield [X_train[i:i+1].astype(np.float32)]

converter.representative_dataset = representative_dataset
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.inference_input_type = tf.int8
converter.inference_output_type = tf.int8

# Convert
tflite_model = converter.convert()

# Save
with open('model.tflite', 'wb') as f:
    f.write(tflite_model)
```

### Convert to C Array
```bash
xxd -i model.tflite > model.h
```

## C++ Integration

### model.h (Generated)
```cpp
unsigned char model_tflite[] = {
  0x1c, 0x00, 0x00, 0x00, 0x54, 0x46, 0x4c, 0x33, ...
};
unsigned int model_tflite_len = 2048;
```

### inference.cpp
```cpp
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_error_reporter.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"
#include "model.h"

namespace {
    tflite::ErrorReporter* error_reporter = nullptr;
    const tflite::Model* model = nullptr;
    tflite::MicroInterpreter* interpreter = nullptr;
    TfLiteTensor* input = nullptr;
    TfLiteTensor* output = nullptr;

    constexpr int kTensorArenaSize = 10 * 1024;  // 10 KB
    alignas(16) uint8_t tensor_arena[kTensorArenaSize];
}

void setup() {
    // Error reporter
    static tflite::MicroErrorReporter micro_error_reporter;
    error_reporter = &micro_error_reporter;

    // Load model
    model = tflite::GetModel(model_tflite);
    if (model->version() != TFLITE_SCHEMA_VERSION) {
        TF_LITE_REPORT_ERROR(error_reporter, "Schema mismatch");
        return;
    }

    // Ops resolver
    static tflite::AllOpsResolver resolver;

    // Build interpreter
    static tflite::MicroInterpreter static_interpreter(
        model, resolver, tensor_arena, kTensorArenaSize, error_reporter);
    interpreter = &static_interpreter;

    // Allocate tensors
    TfLiteStatus allocate_status = interpreter->AllocateTensors();
    if (allocate_status != kTfLiteOk) {
        TF_LITE_REPORT_ERROR(error_reporter, "AllocateTensors() failed");
        return;
    }

    // Get I/O tensors
    input = interpreter->input(0);
    output = interpreter->output(0);

    TF_LITE_REPORT_ERROR(error_reporter, "Model loaded successfully");
}

float run_inference(float* features, int num_features) {
    // Copy input
    for (int i = 0; i < num_features; i++) {
        input->data.f[i] = features[i];
    }

    // Run inference
    TfLiteStatus invoke_status = interpreter->Invoke();
    if (invoke_status != kTfLiteOk) {
        TF_LITE_REPORT_ERROR(error_reporter, "Invoke failed");
        return -1.0f;
    }

    // Get output
    return output->data.f[0];
}
```

## Quantization Types

| Type | Size | Accuracy | Speed | Use Case |
|------|------|----------|-------|----------|
| FP32 | 100% | Highest | Slowest | Baseline |
| FP16 | 50% | Very High | Medium | GPU |
| INT8 | 25% | High | Fast | MCU (recommended) |
| INT16 | 50% | Very High | Medium | Audio/DSP |

## Supported Operations (TFLite Micro)

**Fully Supported:**
- Conv2D, DepthwiseConv2D
- FullyConnected (Dense)
- MaxPool2D, AveragePool2D
- Relu, Relu6, Softmax
- Reshape, Transpose
- Add, Mul, Sub

**Limited Support:**
- LSTM, GRU (basic)
- BatchNormalization (fused)

**Not Supported:**
- Complex operations (e.g., some custom ops)
- Large models (> 1 MB typical limit)

## Memory Optimization

### Tensor Arena Sizing
```cpp
// Start with estimate
constexpr int kTensorArenaSize = 50 * 1024;

// Measure actual usage
size_t used_bytes = interpreter->arena_used_bytes();
printf("Arena used: %zu bytes\n", used_bytes);

// Reduce to minimum + margin
constexpr int kTensorArenaSize = (used_bytes * 1.2);
```

### Model Optimization
1. **Prune weights** (remove unimportant connections)
2. **Quantize** to INT8
3. **Reduce layer sizes** (fewer neurons)
4. **Simplify architecture** (fewer layers)

## Platform-Specific Acceleration

### ARM Cortex-M (CMSIS-NN)
```cpp
#define CMSIS_NN 1

#include "tensorflow/lite/micro/kernels/cmsis_nn/cmsis_nn.h"

// CMSIS-NN optimized ops will be used automatically
```

### ESP32
```cpp
// ESP-NN optimizations
#define ESP_NN 1
```

## Debugging

### Check Model Details
```python
import tensorflow as tf

interpreter = tf.lite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()

# Input details
input_details = interpreter.get_input_details()
print("Input shape:", input_details[0]['shape'])
print("Input dtype:", input_details[0]['dtype'])

# Output details
output_details = interpreter.get_output_details()
print("Output shape:", output_details[0]['shape'])
```

### Profiling
```cpp
#include "tensorflow/lite/micro/micro_profiler.h"

tflite::MicroProfiler profiler;
interpreter->SetProfiler(&profiler);

// Run inference
interpreter->Invoke();

// Print profiling results
profiler.LogTicksPerTagCsv();
```

## Example: Anomaly Detection

```cpp
float detect_anomaly(float sensor_values[], int num_sensors) {
    // Normalize inputs (based on training data stats)
    for (int i = 0; i < num_sensors; i++) {
        float normalized = (sensor_values[i] - mean[i]) / std[i];
        input->data.f[i] = normalized;
    }

    // Inference
    interpreter->Invoke();

    // Anomaly score (0-1, higher = more anomalous)
    float anomaly_score = output->data.f[0];

    return anomaly_score;
}

void loop() {
    float sensors[10];

    // Read sensors
    sensors[0] = read_temperature();
    sensors[1] = read_vibration();
    // ... more sensors

    float score = detect_anomaly(sensors, 10);

    if (score > 0.8f) {
        Serial.println("Anomaly detected!");
        trigger_alert();
    }

    delay(1000);
}
```

## Build Configuration

### PlatformIO (platformio.ini)
```ini
[env:esp32]
platform = espressif32
framework = arduino
lib_deps =
    https://github.com/tensorflow/tflite-micro-arduino-examples

build_flags =
    -DTF_LITE_STATIC_MEMORY
    -DESP_NN
```

### Arduino
```cpp
#include <TensorFlowLite.h>
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_interpreter.h"

// Rest of code...
```

## Performance Benchmarks

| Platform | Clock | Inference Time (10-input model) |
|----------|-------|--------------------------------|
| STM32F4 (Cortex-M4) | 84 MHz | 15 ms |
| STM32F7 (Cortex-M7) | 216 MHz | 5 ms |
| ESP32 | 240 MHz | 8 ms |
| ESP32-S3 | 240 MHz | 6 ms (ESP-NN) |
| nRF52840 | 64 MHz | 25 ms |

## Resources

- [TFLite Micro GitHub](https://github.com/tensorflow/tflite-micro)
- [Model Optimization Guide](https://www.tensorflow.org/lite/performance/model_optimization)
- [CMSIS-NN](https://github.com/ARM-software/CMSIS_5)
- [ESP-NN](https://github.com/espressif/esp-nn)
