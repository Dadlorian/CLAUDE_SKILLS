# Edge Computing & Analytics - Subskill

**Expert in edge AI/ML, TensorFlow Lite Micro, on-device inference, and local processing**

---

## Expertise Overview

Specialist in edge computing for IoT:
- TensorFlow Lite Micro for MCU inference
- Edge Impulse for embedded ML workflows
- Quantized neural networks (INT8, INT16)
- On-device anomaly detection and classification
- Edge analytics frameworks (AWS Greengrass, Azure IoT Edge)

---

## Core Skills

### 1. TensorFlow Lite Micro

**Inference on MCU**:
```cpp
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_error_reporter.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"

/* Model generated from Python */
#include "model.h"

namespace {
    tflite::ErrorReporter* error_reporter = nullptr;
    const tflite::Model* model = nullptr;
    tflite::MicroInterpreter* interpreter = nullptr;
    TfLiteTensor* input = nullptr;
    TfLiteTensor* output = nullptr;

    /* Tensor arena (adjust size based on model) */
    constexpr int kTensorArenaSize = 60 * 1024;
    alignas(16) uint8_t tensor_arena[kTensorArenaSize];
}

void tflite_init() {
    /* Set up logging */
    static tflite::MicroErrorReporter micro_error_reporter;
    error_reporter = &micro_error_reporter;

    /* Load model */
    model = tflite::GetModel(g_model);
    if (model->version() != TFLITE_SCHEMA_VERSION) {
        TF_LITE_REPORT_ERROR(error_reporter,
            "Model schema version %d not supported",
            model->version());
        return;
    }

    /* Pull in all operations */
    static tflite::AllOpsResolver resolver;

    /* Build interpreter */
    static tflite::MicroInterpreter static_interpreter(
        model, resolver, tensor_arena, kTensorArenaSize, error_reporter);
    interpreter = &static_interpreter;

    /* Allocate tensors */
    TfLiteStatus allocate_status = interpreter->AllocateTensors();
    if (allocate_status != kTfLiteOk) {
        TF_LITE_REPORT_ERROR(error_reporter, "AllocateTensors() failed");
        return;
    }

    /* Get input/output tensors */
    input = interpreter->input(0);
    output = interpreter->output(0);
}

/* Run inference */
float tflite_classify(const float* features, size_t num_features) {
    /* Copy features to input tensor */
    for (size_t i = 0; i < num_features; i++) {
        input->data.f[i] = features[i];
    }

    /* Run inference */
    TfLiteStatus invoke_status = interpreter->Invoke();
    if (invoke_status != kTfLiteOk) {
        TF_LITE_REPORT_ERROR(error_reporter, "Invoke failed");
        return -1.0f;
    }

    /* Get output */
    float confidence = output->data.f[0];
    return confidence;
}

/* Example: Anomaly detection */
void detect_anomaly() {
    /* Collect sensor data */
    float features[10];
    features[0] = read_temperature();
    features[1] = read_vibration();
    /* ... more features */

    /* Run inference */
    float anomaly_score = tflite_classify(features, 10);

    if (anomaly_score > 0.8f) {
        /* Anomaly detected */
        trigger_alert();
    }
}
```

### 2. Edge Impulse Integration

**Keyword Spotting Example**:
```cpp
#include <your_project_inferencing.h>

/* Audio buffer */
#define SAMPLE_RATE         16000
#define SAMPLE_LENGTH_MS    1000
#define BUFFER_SIZE         (SAMPLE_RATE * SAMPLE_LENGTH_MS / 1000)

static int16_t audio_buffer[BUFFER_SIZE];
static size_t audio_index = 0;

/* Edge Impulse inference */
void run_keyword_detection() {
    signal_t signal;
    signal.total_length = BUFFER_SIZE;
    signal.get_data = &get_audio_data;

    ei_impulse_result_t result = {0};

    /* Run classifier */
    EI_IMPULSE_ERROR res = run_classifier(&signal, &result, false);

    if (res != EI_IMPULSE_OK) {
        printf("ERR: Failed to run classifier (%d)\n", res);
        return;
    }

    /* Print predictions */
    for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {
        printf("    %s: %.5f\n",
               result.classification[ix].label,
               result.classification[ix].value);

        /* Check for keyword */
        if (strcmp(result.classification[ix].label, "hello") == 0 &&
            result.classification[ix].value > 0.8f) {
            /* "Hello" detected */
            trigger_wake_word_action();
        }
    }
}

/* Get audio data callback */
static int get_audio_data(size_t offset, size_t length, float *out_ptr) {
    for (size_t i = 0; i < length; i++) {
        out_ptr[i] = (float)audio_buffer[offset + i] / 32768.0f;
    }
    return 0;
}
```

### 3. Local Anomaly Detection

**Statistical Method (Z-Score)**:
```c
#include <math.h>

#define WINDOW_SIZE 100
#define ANOMALY_THRESHOLD 3.0f  /* 3 standard deviations */

typedef struct {
    float samples[WINDOW_SIZE];
    size_t index;
    size_t count;
    float mean;
    float std_dev;
} anomaly_detector_t;

void anomaly_detector_init(anomaly_detector_t *detector) {
    memset(detector, 0, sizeof(anomaly_detector_t));
}

void update_statistics(anomaly_detector_t *detector) {
    /* Calculate mean */
    float sum = 0.0f;
    size_t n = (detector->count < WINDOW_SIZE) ?
               detector->count : WINDOW_SIZE;

    for (size_t i = 0; i < n; i++) {
        sum += detector->samples[i];
    }
    detector->mean = sum / (float)n;

    /* Calculate standard deviation */
    float variance = 0.0f;
    for (size_t i = 0; i < n; i++) {
        float diff = detector->samples[i] - detector->mean;
        variance += diff * diff;
    }
    detector->std_dev = sqrtf(variance / (float)n);
}

bool is_anomaly(anomaly_detector_t *detector, float value) {
    /* Add sample to window */
    detector->samples[detector->index] = value;
    detector->index = (detector->index + 1) % WINDOW_SIZE;
    detector->count++;

    /* Need minimum samples */
    if (detector->count < WINDOW_SIZE / 2) {
        return false;
    }

    /* Update statistics */
    update_statistics(detector);

    /* Calculate z-score */
    float z_score = fabsf((value - detector->mean) / detector->std_dev);

    return (z_score > ANOMALY_THRESHOLD);
}
```

### 4. AWS IoT Greengrass Integration

**Lambda Function (C)**:
```c
#include <aws/greengrass/gg_api.h>

gg_error gg_lambda_handler(
    const gg_lambda_context *cxt,
    const gg_request *req,
    gg_response **resp) {

    /* Parse input */
    const char *input = (const char *)req->payload;

    /* Process data locally */
    float temperature = parse_temperature(input);

    /* Run local ML inference */
    float anomaly_score = detect_temperature_anomaly(temperature);

    if (anomaly_score > 0.8f) {
        /* Publish to cloud */
        gg_request *pub_req = gg_request_init();
        gg_request_set_topic(pub_req, "alerts/temperature");

        char alert[128];
        snprintf(alert, sizeof(alert),
                 "{\"temp\":%.2f,\"score\":%.2f}",
                 temperature, anomaly_score);

        gg_request_set_payload(pub_req, alert, strlen(alert));
        gg_publish(pub_req);
        gg_request_close(pub_req);
    }

    /* Return response */
    *resp = gg_response_init();
    gg_response_set_status(*resp, GG_STATUS_SUCCESS);

    return GG_ERR_SUCCESS;
}
```

---

## Model Optimization Techniques

### Quantization

```python
# Post-training quantization (INT8)
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]

# Representative dataset for calibration
def representative_dataset():
    for _ in range(100):
        yield [np.random.random((1, 10)).astype(np.float32)]

converter.representative_dataset = representative_dataset
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.inference_input_type = tf.int8
converter.inference_output_type = tf.int8

tflite_quant_model = converter.convert()
```

### Pruning

```python
import tensorflow_model_optimization as tfmot

# Prune model to 50% sparsity
prune_low_magnitude = tfmot.sparsity.keras.prune_low_magnitude

pruning_params = {
    'pruning_schedule': tfmot.sparsity.keras.PolynomialDecay(
        initial_sparsity=0.0,
        final_sparsity=0.5,
        begin_step=0,
        end_step=1000
    )
}

model_for_pruning = prune_low_magnitude(model, **pruning_params)
```

---

## Best Practices

1. **Model Size**: Keep < 100KB for MCU deployment
2. **Latency**: Target < 100ms for real-time applications
3. **Power**: Optimize inference for battery life
4. **Quantization**: Use INT8 for 4x speedup on Cortex-M
5. **Validation**: Test on-device accuracy vs cloud model

---

## References

- TensorFlow Lite Micro documentation
- Edge Impulse embedded ML guides
- ARM CMSIS-NN library
- "TinyML" by Pete Warden

---

---

## Advanced Model Deployment Strategies

### Model Conversion Pipeline
```python
# Convert TensorFlow model to TFLite with optimization
import tensorflow as tf

def convert_and_optimize_model(model_path, output_path):
    # Load trained model
    model = tf.keras.models.load_model(model_path)

    # Convert to TFLite
    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    # Enable optimizations
    converter.optimizations = [tf.lite.Optimize.DEFAULT]

    # Quantization settings
    converter.target_spec.supported_ops = [
        tf.lite.OpsSet.TFLITE_BUILTINS_INT8
    ]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8

    # Representative dataset for calibration
    def representative_dataset():
        for _ in range(100):
            yield [np.random.random((1, 10)).astype(np.float32)]

    converter.representative_dataset = representative_dataset

    # Convert
    tflite_model = converter.convert()

    # Save
    with open(output_path, 'wb') as f:
        f.write(tflite_model)

    # Print model size
    original_size = len(model.to_json())
    optimized_size = len(tflite_model)
    print(f"Original: {original_size/1024:.1f}KB, Optimized: {optimized_size/1024:.1f}KB")
```

### Dynamic Model Switching
```c
/* Load different models based on device capability */
typedef enum {
    MODEL_TINY,     /* For low-power MCU */
    MODEL_SMALL,    /* For mid-range MCU */
    MODEL_MEDIUM    /* For powerful edge device */
} model_variant_t;

typedef struct {
    const uint8_t *model_data;
    size_t model_size;
    size_t tensor_arena_size;
    float accuracy_baseline;
} model_info_t;

const model_info_t models[] = {
    { tiny_model, sizeof(tiny_model), 20*1024, 0.92 },
    { small_model, sizeof(small_model), 60*1024, 0.95 },
    { medium_model, sizeof(medium_model), 200*1024, 0.98 }
};

status_t load_model_for_device(model_variant_t variant,
                               tflite_interpreter_t *interp) {
    const model_info_t *selected = &models[variant];

    /* Check available RAM */
    uint32_t available_ram = get_available_ram();
    if (available_ram < selected->tensor_arena_size) {
        printf("Insufficient RAM, selecting smaller model\n");
        return load_model_for_device(variant - 1, interp);
    }

    return tflite_load_model(selected->model_data,
                             selected->model_size, interp);
}
```

---

## Real-World Deployment Patterns

### Continuous Learning on Edge
```c
/* Update model with edge device data */
typedef struct {
    float weights[100];
    float biases[10];
    uint32_t training_samples;
} incremental_model_t;

void update_model_with_local_data(incremental_model_t *model,
                                   const float *features,
                                   const float *labels) {
    /* Perform single gradient step with new sample */
    float predictions[10];
    forward_pass(model, features, predictions);

    /* Calculate loss and gradients */
    float loss = calculate_loss(predictions, labels);

    /* Small learning rate to avoid instability */
    float learning_rate = 0.001f;
    float gradients[100];
    backward_pass(model, features, labels, gradients);

    /* Update weights incrementally */
    for (int i = 0; i < 100; i++) {
        model->weights[i] -= learning_rate * gradients[i];
    }

    model->training_samples++;

    /* Periodically sync with cloud for validation */
    if (model->training_samples % 100 == 0) {
        sync_model_to_cloud(model);
    }
}
```

### Ensemble Models for Robustness
```c
/* Use multiple small models for better accuracy and robustness */
#define NUM_MODELS 3

typedef struct {
    tflite_interpreter_t interpreters[NUM_MODELS];
    float model_weights[NUM_MODELS];
    uint32_t ensemble_size;
} ensemble_t;

float ensemble_inference(ensemble_t *ensemble, const float *features) {
    float predictions[NUM_MODELS];
    float confidence_sum = 0.0f;

    /* Run each model */
    for (int i = 0; i < ensemble->ensemble_size; i++) {
        predictions[i] = tflite_inference(&ensemble->interpreters[i],
                                          features);
    }

    /* Weighted average */
    float result = 0.0f;
    for (int i = 0; i < ensemble->ensemble_size; i++) {
        result += predictions[i] * ensemble->model_weights[i];
        confidence_sum += ensemble->model_weights[i];
    }

    return result / confidence_sum;
}
```

---

## Edge Analytics Frameworks

### AWS Greengrass Lambda Functions
```c
/* Custom ML logic in Greengrass Lambda */
#include <greengrasscoresdk.h>

gg_error analyze_data(const gg_lambda_context *cxt,
                      const gg_request *req,
                      gg_response **resp) {
    /* Parse incoming telemetry */
    json_t *data = json_loads((const char*)req->payload, NULL);

    float temperature = json_real_value(json_object_get(data, "temp"));
    float humidity = json_real_value(json_object_get(data, "humidity"));

    /* Local ML inference */
    float features[] = {temperature, humidity};
    float anomaly_score = run_local_ml_model(features);

    /* Decision logic */
    if (anomaly_score > 0.8f) {
        /* Alert: Send to cloud */
        gg_publish_message("alerts/anomaly",
            "{\"type\":\"environmental\",\"severity\":\"high\"}");
    } else if (anomaly_score > 0.5f) {
        /* Warning: Store locally for batch processing */
        log_to_local_storage("{\"type\":\"warning\",\"score\":%.2f}",
                            anomaly_score);
    }

    /* Return response */
    *resp = gg_response_init();
    gg_response_set_status(*resp, GG_STATUS_SUCCESS);

    return GG_ERR_SUCCESS;
}
```

### Azure IoT Edge Module
```c
/* C module for Azure IoT Edge */
typedef struct {
    void *model;
    int input_size;
    int output_size;
} edge_module_t;

/* Input message callback */
void input_message_callback(IOTHUB_MESSAGE_HANDLE msg,
                            edge_module_t *module) {
    /* Extract data */
    const char *payload = IoTHubMessage_GetString(msg);

    /* Preprocess */
    float *features = preprocess_input(payload);

    /* Run inference */
    float *results = tflite_run_inference(module->model, features);

    /* Send results to output */
    char output[128];
    snprintf(output, sizeof(output),
             "{\"prediction\":%.2f,\"confidence\":%.2f}",
             results[0], results[1]);

    IOTHUB_MESSAGE_HANDLE output_msg =
        IoTHubMessage_CreateFromString(output);

    send_to_output(output_msg, "output1");

    IoTHubMessage_Destroy(output_msg);
    free(features);
    free(results);
}
```

---

## Performance Monitoring & Optimization

### Latency Profiling
```c
/* Measure inference time to ensure real-time performance */
typedef struct {
    uint32_t preprocess_ms;
    uint32_t inference_ms;
    uint32_t postprocess_ms;
    uint32_t total_ms;
} latency_profile_t;

latency_profile_t profile_edge_inference(const float *features) {
    latency_profile_t profile = {0};
    uint32_t start_time;

    /* Preprocessing */
    start_time = get_time_ms();
    float *normalized = normalize_features(features, FEATURE_COUNT);
    profile.preprocess_ms = get_time_ms() - start_time;

    /* Inference */
    start_time = get_time_ms();
    float *output = tflite_run_inference(model, normalized);
    profile.inference_ms = get_time_ms() - start_time;

    /* Postprocessing */
    start_time = get_time_ms();
    float confidence = apply_sigmoid(output[0]);
    profile.postprocess_ms = get_time_ms() - start_time;

    profile.total_ms = profile.preprocess_ms +
                       profile.inference_ms +
                       profile.postprocess_ms;

    /* Log if exceeds latency budget */
    if (profile.total_ms > LATENCY_BUDGET_MS) {
        printf("Warning: Inference latency %.0fms exceeds budget\n",
               profile.total_ms);
    }

    return profile;
}
```

### Memory Usage Monitoring
```c
/* Track tensor arena usage to prevent out-of-memory */
uint32_t get_tensor_arena_usage(tflite_interpreter_t *interp) {
    /* TFLite Micro provides tensor arena usage info */
    uint32_t max_size = interp->tensor_arena_size;
    uint32_t used = interp->arena_position;

    uint32_t usage_percent = (used * 100) / max_size;

    if (usage_percent > 90) {
        printf("Warning: Tensor arena 90%% full\n");
    }

    return used;
}
```

---

**Deploy efficient, low-latency ML inference on resource-constrained edge devices with production-grade accuracy.**
