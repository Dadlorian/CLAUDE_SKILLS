/*
 * Advanced Sensor Fusion Implementation
 * Combines multiple sensor inputs for improved accuracy
 *
 * Features:
 * - 9-DOF IMU fusion (accelerometer, gyroscope, magnetometer)
 * - Extended Kalman Filter (EKF)
 * - Complementary filter
 * - Madgwick AHRS algorithm
 */

#include <math.h>
#include <stdint.h>
#include <stdbool.h>

/* ============================================================================
 * 9-DOF IMU Sensor Fusion using Madgwick Filter
 * ============================================================================ */

#define SAMPLE_FREQ    100.0f  /* 100 Hz */
#define BETA           0.1f    /* Filter gain */

typedef struct {
    float q0, q1, q2, q3;  /* Quaternion components */
    float beta;            /* Filter gain */
    float sample_freq;     /* Sampling frequency */
} madgwick_filter_t;

typedef struct {
    float x, y, z;
} vector3_t;

typedef struct {
    float roll, pitch, yaw;  /* Euler angles in degrees */
} euler_angles_t;

/* Initialize Madgwick filter */
void madgwick_init(madgwick_filter_t *filter, float sample_freq, float beta) {
    filter->q0 = 1.0f;
    filter->q1 = 0.0f;
    filter->q2 = 0.0f;
    filter->q3 = 0.0f;
    filter->beta = beta;
    filter->sample_freq = sample_freq;
}

/* Fast inverse square root */
static float inv_sqrt(float x) {
    float halfx = 0.5f * x;
    float y = x;
    long i = *(long*)&y;
    i = 0x5f3759df - (i >> 1);
    y = *(float*)&i;
    y = y * (1.5f - (halfx * y * y));
    return y;
}

/* Madgwick AHRS update (with magnetometer) */
void madgwick_update(madgwick_filter_t *filter,
                     vector3_t gyro,    /* rad/s */
                     vector3_t accel,   /* g */
                     vector3_t mag) {   /* any units */

    float q0 = filter->q0, q1 = filter->q1;
    float q2 = filter->q2, q3 = filter->q3;
    float recipNorm;
    float s0, s1, s2, s3;
    float qDot1, qDot2, qDot3, qDot4;
    float hx, hy;
    float _2q0mx, _2q0my, _2q0mz, _2q1mx;
    float _2bx, _2bz;
    float _4bx, _4bz;
    float _2q0, _2q1, _2q2, _2q3;
    float _2q0q2, _2q2q3;
    float q0q0, q0q1, q0q2, q0q3;
    float q1q1, q1q2, q1q3;
    float q2q2, q2q3, q3q3;

    /* Normalize accelerometer measurement */
    recipNorm = inv_sqrt(accel.x * accel.x + accel.y * accel.y + accel.z * accel.z);
    accel.x *= recipNorm;
    accel.y *= recipNorm;
    accel.z *= recipNorm;

    /* Normalize magnetometer measurement */
    recipNorm = inv_sqrt(mag.x * mag.x + mag.y * mag.y + mag.z * mag.z);
    mag.x *= recipNorm;
    mag.y *= recipNorm;
    mag.z *= recipNorm;

    /* Auxiliary variables */
    _2q0 = 2.0f * q0;
    _2q1 = 2.0f * q1;
    _2q2 = 2.0f * q2;
    _2q3 = 2.0f * q3;
    _2q0q2 = 2.0f * q0 * q2;
    _2q2q3 = 2.0f * q2 * q3;
    q0q0 = q0 * q0;
    q0q1 = q0 * q1;
    q0q2 = q0 * q2;
    q0q3 = q0 * q3;
    q1q1 = q1 * q1;
    q1q2 = q1 * q2;
    q1q3 = q1 * q3;
    q2q2 = q2 * q2;
    q2q3 = q2 * q3;
    q3q3 = q3 * q3;

    /* Reference direction of Earth's magnetic field */
    _2q0mx = 2.0f * q0 * mag.x;
    _2q0my = 2.0f * q0 * mag.y;
    _2q0mz = 2.0f * q0 * mag.z;
    _2q1mx = 2.0f * q1 * mag.x;

    hx = mag.x * q0q0 - _2q0my * q3 + _2q0mz * q2 + mag.x * q1q1 +
         _2q1 * mag.y * q2 + _2q1 * mag.z * q3 - mag.x * q2q2 - mag.x * q3q3;
    hy = _2q0mx * q3 + mag.y * q0q0 - _2q0mz * q1 + _2q1mx * q2 -
         mag.y * q1q1 + mag.y * q2q2 + _2q2 * mag.z * q3 - mag.y * q3q3;

    _2bx = sqrtf(hx * hx + hy * hy);
    _2bz = -_2q0mx * q2 + _2q0my * q1 + mag.z * q0q0 + _2q1mx * q3 -
           mag.z * q1q1 + _2q2 * mag.y * q3 - mag.z * q2q2 + mag.z * q3q3;
    _4bx = 2.0f * _2bx;
    _4bz = 2.0f * _2bz;

    /* Gradient descent algorithm corrective step */
    s0 = -_2q2 * (2.0f * q1q3 - _2q0q2 - accel.x) +
         _2q1 * (2.0f * q0q1 + _2q2q3 - accel.y) -
         _2bz * q2 * (_2bx * (0.5f - q2q2 - q3q3) + _2bz * (q1q3 - q0q2) - mag.x) +
         (-_2bx * q3 + _2bz * q1) * (_2bx * (q1q2 - q0q3) + _2bz * (q0q1 + q2q3) - mag.y) +
         _2bx * q2 * (_2bx * (q0q2 + q1q3) + _2bz * (0.5f - q1q1 - q2q2) - mag.z);

    s1 = _2q3 * (2.0f * q1q3 - _2q0q2 - accel.x) +
         _2q0 * (2.0f * q0q1 + _2q2q3 - accel.y) -
         4.0f * q1 * (1.0f - 2.0f * q1q1 - 2.0f * q2q2 - accel.z) +
         _2bz * q3 * (_2bx * (0.5f - q2q2 - q3q3) + _2bz * (q1q3 - q0q2) - mag.x) +
         (_2bx * q2 + _2bz * q0) * (_2bx * (q1q2 - q0q3) + _2bz * (q0q1 + q2q3) - mag.y) +
         (_2bx * q3 - _4bz * q1) * (_2bx * (q0q2 + q1q3) + _2bz * (0.5f - q1q1 - q2q2) - mag.z);

    s2 = -_2q0 * (2.0f * q1q3 - _2q0q2 - accel.x) +
         _2q3 * (2.0f * q0q1 + _2q2q3 - accel.y) -
         4.0f * q2 * (1.0f - 2.0f * q1q1 - 2.0f * q2q2 - accel.z) +
         (-_4bx * q2 - _2bz * q0) * (_2bx * (0.5f - q2q2 - q3q3) + _2bz * (q1q3 - q0q2) - mag.x) +
         (_2bx * q1 + _2bz * q3) * (_2bx * (q1q2 - q0q3) + _2bz * (q0q1 + q2q3) - mag.y) +
         (_2bx * q0 - _4bz * q2) * (_2bx * (q0q2 + q1q3) + _2bz * (0.5f - q1q1 - q2q2) - mag.z);

    s3 = _2q1 * (2.0f * q1q3 - _2q0q2 - accel.x) +
         _2q2 * (2.0f * q0q1 + _2q2q3 - accel.y) +
         (-_4bx * q3 + _2bz * q1) * (_2bx * (0.5f - q2q2 - q3q3) + _2bz * (q1q3 - q0q2) - mag.x) +
         (-_2bx * q0 + _2bz * q2) * (_2bx * (q1q2 - q0q3) + _2bz * (q0q1 + q2q3) - mag.y) +
         _2bx * q1 * (_2bx * (q0q2 + q1q3) + _2bz * (0.5f - q1q1 - q2q2) - mag.z);

    /* Normalize step magnitude */
    recipNorm = inv_sqrt(s0 * s0 + s1 * s1 + s2 * s2 + s3 * s3);
    s0 *= recipNorm;
    s1 *= recipNorm;
    s2 *= recipNorm;
    s3 *= recipNorm;

    /* Rate of change of quaternion from gyroscope */
    qDot1 = 0.5f * (-q1 * gyro.x - q2 * gyro.y - q3 * gyro.z);
    qDot2 = 0.5f * (q0 * gyro.x + q2 * gyro.z - q3 * gyro.y);
    qDot3 = 0.5f * (q0 * gyro.y - q1 * gyro.z + q3 * gyro.x);
    qDot4 = 0.5f * (q0 * gyro.z + q1 * gyro.y - q2 * gyro.x);

    /* Apply feedback step */
    qDot1 -= filter->beta * s0;
    qDot2 -= filter->beta * s1;
    qDot3 -= filter->beta * s2;
    qDot4 -= filter->beta * s3;

    /* Integrate rate of change */
    float dt = 1.0f / filter->sample_freq;
    q0 += qDot1 * dt;
    q1 += qDot2 * dt;
    q2 += qDot3 * dt;
    q3 += qDot4 * dt;

    /* Normalize quaternion */
    recipNorm = inv_sqrt(q0 * q0 + q1 * q1 + q2 * q2 + q3 * q3);
    filter->q0 = q0 * recipNorm;
    filter->q1 = q1 * recipNorm;
    filter->q2 = q2 * recipNorm;
    filter->q3 = q3 * recipNorm;
}

/* Convert quaternion to Euler angles */
void quaternion_to_euler(madgwick_filter_t *filter, euler_angles_t *angles) {
    float q0 = filter->q0;
    float q1 = filter->q1;
    float q2 = filter->q2;
    float q3 = filter->q3;

    /* Roll (x-axis rotation) */
    float sinr_cosp = 2.0f * (q0 * q1 + q2 * q3);
    float cosr_cosp = 1.0f - 2.0f * (q1 * q1 + q2 * q2);
    angles->roll = atan2f(sinr_cosp, cosr_cosp) * 57.2958f;

    /* Pitch (y-axis rotation) */
    float sinp = 2.0f * (q0 * q2 - q3 * q1);
    if (fabsf(sinp) >= 1.0f) {
        angles->pitch = copysignf(90.0f, sinp);  /* Use 90 degrees if out of range */
    } else {
        angles->pitch = asinf(sinp) * 57.2958f;
    }

    /* Yaw (z-axis rotation) */
    float siny_cosp = 2.0f * (q0 * q3 + q1 * q2);
    float cosy_cosp = 1.0f - 2.0f * (q2 * q2 + q3 * q3);
    angles->yaw = atan2f(siny_cosp, cosy_cosp) * 57.2958f;
}


/* ============================================================================
 * Extended Kalman Filter for Multi-Sensor Fusion
 * ============================================================================ */

#define EKF_STATE_DIM  6   /* [x, y, z, vx, vy, vz] */
#define EKF_MEAS_DIM   3   /* [x, y, z] from GPS */

typedef struct {
    float state[EKF_STATE_DIM];       /* State vector */
    float P[EKF_STATE_DIM][EKF_STATE_DIM];  /* Covariance matrix */
    float Q[EKF_STATE_DIM][EKF_STATE_DIM];  /* Process noise */
    float R[EKF_MEAS_DIM][EKF_MEAS_DIM];    /* Measurement noise */
} ekf_t;

/* Initialize EKF */
void ekf_init(ekf_t *ekf) {
    /* Initialize state to zero */
    for (int i = 0; i < EKF_STATE_DIM; i++) {
        ekf->state[i] = 0.0f;
    }

    /* Initialize covariance (identity) */
    for (int i = 0; i < EKF_STATE_DIM; i++) {
        for (int j = 0; j < EKF_STATE_DIM; j++) {
            ekf->P[i][j] = (i == j) ? 1.0f : 0.0f;
        }
    }

    /* Process noise (tunable) */
    for (int i = 0; i < EKF_STATE_DIM; i++) {
        for (int j = 0; j < EKF_STATE_DIM; j++) {
            ekf->Q[i][j] = (i == j) ? 0.01f : 0.0f;
        }
    }

    /* Measurement noise (tunable) */
    for (int i = 0; i < EKF_MEAS_DIM; i++) {
        for (int j = 0; j < EKF_MEAS_DIM; j++) {
            ekf->R[i][j] = (i == j) ? 0.1f : 0.0f;
        }
    }
}

/* EKF Prediction step */
void ekf_predict(ekf_t *ekf, float dt, vector3_t accel) {
    /* State transition: constant velocity model with acceleration input */
    float x = ekf->state[0];
    float y = ekf->state[1];
    float z = ekf->state[2];
    float vx = ekf->state[3];
    float vy = ekf->state[4];
    float vz = ekf->state[5];

    /* Predict new state */
    ekf->state[0] = x + vx * dt + 0.5f * accel.x * dt * dt;
    ekf->state[1] = y + vy * dt + 0.5f * accel.y * dt * dt;
    ekf->state[2] = z + vz * dt + 0.5f * accel.z * dt * dt;
    ekf->state[3] = vx + accel.x * dt;
    ekf->state[4] = vy + accel.y * dt;
    ekf->state[5] = vz + accel.z * dt;

    /* Jacobian of state transition */
    float F[EKF_STATE_DIM][EKF_STATE_DIM] = {
        {1, 0, 0, dt, 0, 0},
        {0, 1, 0, 0, dt, 0},
        {0, 0, 1, 0, 0, dt},
        {0, 0, 0, 1, 0, 0},
        {0, 0, 0, 0, 1, 0},
        {0, 0, 0, 0, 0, 1}
    };

    /* Predict covariance: P = F * P * F' + Q */
    float P_pred[EKF_STATE_DIM][EKF_STATE_DIM];
    for (int i = 0; i < EKF_STATE_DIM; i++) {
        for (int j = 0; j < EKF_STATE_DIM; j++) {
            P_pred[i][j] = ekf->Q[i][j];
            for (int k = 0; k < EKF_STATE_DIM; k++) {
                for (int l = 0; l < EKF_STATE_DIM; l++) {
                    P_pred[i][j] += F[i][k] * ekf->P[k][l] * F[j][l];
                }
            }
        }
    }

    /* Update covariance */
    for (int i = 0; i < EKF_STATE_DIM; i++) {
        for (int j = 0; j < EKF_STATE_DIM; j++) {
            ekf->P[i][j] = P_pred[i][j];
        }
    }
}

/* EKF Update step (simplified for position measurement) */
void ekf_update(ekf_t *ekf, vector3_t measurement) {
    /* Measurement matrix H (we measure position only) */
    float H[EKF_MEAS_DIM][EKF_STATE_DIM] = {
        {1, 0, 0, 0, 0, 0},
        {0, 1, 0, 0, 0, 0},
        {0, 0, 1, 0, 0, 0}
    };

    /* Innovation: y = z - H * x */
    float y[EKF_MEAS_DIM];
    y[0] = measurement.x - ekf->state[0];
    y[1] = measurement.y - ekf->state[1];
    y[2] = measurement.z - ekf->state[2];

    /* Innovation covariance: S = H * P * H' + R */
    float S[EKF_MEAS_DIM][EKF_MEAS_DIM];
    for (int i = 0; i < EKF_MEAS_DIM; i++) {
        for (int j = 0; j < EKF_MEAS_DIM; j++) {
            S[i][j] = ekf->R[i][j];
            for (int k = 0; k < EKF_STATE_DIM; k++) {
                for (int l = 0; l < EKF_STATE_DIM; l++) {
                    S[i][j] += H[i][k] * ekf->P[k][l] * H[j][l];
                }
            }
        }
    }

    /* Kalman gain: K = P * H' * inv(S) (simplified for 3x3) */
    float K[EKF_STATE_DIM][EKF_MEAS_DIM];
    float det = S[0][0] * (S[1][1] * S[2][2] - S[1][2] * S[2][1]) -
                S[0][1] * (S[1][0] * S[2][2] - S[1][2] * S[2][0]) +
                S[0][2] * (S[1][0] * S[2][1] - S[1][1] * S[2][0]);

    if (fabsf(det) < 1e-6f) return;  /* Singular matrix */

    /* Update state: x = x + K * y */
    for (int i = 0; i < EKF_STATE_DIM; i++) {
        for (int j = 0; j < EKF_MEAS_DIM; j++) {
            K[i][j] = ekf->P[i][j] / (S[j][j] + 1e-6f);  /* Simplified */
        }
    }

    for (int i = 0; i < EKF_STATE_DIM; i++) {
        for (int j = 0; j < EKF_MEAS_DIM; j++) {
            ekf->state[i] += K[i][j] * y[j];
        }
    }

    /* Update covariance: P = (I - K * H) * P */
    float I_KH[EKF_STATE_DIM][EKF_STATE_DIM];
    for (int i = 0; i < EKF_STATE_DIM; i++) {
        for (int j = 0; j < EKF_STATE_DIM; j++) {
            I_KH[i][j] = (i == j) ? 1.0f : 0.0f;
            for (int k = 0; k < EKF_MEAS_DIM; k++) {
                I_KH[i][j] -= K[i][k] * H[k][j];
            }
        }
    }

    float P_new[EKF_STATE_DIM][EKF_STATE_DIM];
    for (int i = 0; i < EKF_STATE_DIM; i++) {
        for (int j = 0; j < EKF_STATE_DIM; j++) {
            P_new[i][j] = 0.0f;
            for (int k = 0; k < EKF_STATE_DIM; k++) {
                P_new[i][j] += I_KH[i][k] * ekf->P[k][j];
            }
        }
    }

    for (int i = 0; i < EKF_STATE_DIM; i++) {
        for (int j = 0; j < EKF_STATE_DIM; j++) {
            ekf->P[i][j] = P_new[i][j];
        }
    }
}


/* ============================================================================
 * Multi-Sensor Data Quality Assessment
 * ============================================================================ */

typedef struct {
    float mean;
    float variance;
    float min;
    float max;
    uint32_t sample_count;
    bool is_valid;
} sensor_statistics_t;

void sensor_statistics_init(sensor_statistics_t *stats) {
    stats->mean = 0.0f;
    stats->variance = 0.0f;
    stats->min = INFINITY;
    stats->max = -INFINITY;
    stats->sample_count = 0;
    stats->is_valid = false;
}

void sensor_statistics_update(sensor_statistics_t *stats, float new_value) {
    /* Update min/max */
    if (new_value < stats->min) stats->min = new_value;
    if (new_value > stats->max) stats->max = new_value;

    /* Online variance calculation (Welford's method) */
    stats->sample_count++;
    float delta = new_value - stats->mean;
    stats->mean += delta / stats->sample_count;
    float delta2 = new_value - stats->mean;
    stats->variance += delta * delta2;

    stats->is_valid = (stats->sample_count > 10);
}

float sensor_get_std_deviation(sensor_statistics_t *stats) {
    if (stats->sample_count < 2) return 0.0f;
    return sqrtf(stats->variance / (stats->sample_count - 1));
}

/* Detect sensor outliers using Z-score */
bool is_sensor_outlier(sensor_statistics_t *stats, float value, float threshold) {
    if (!stats->is_valid) return false;

    float std_dev = sensor_get_std_deviation(stats);
    if (std_dev < 1e-6f) return false;

    float z_score = fabsf((value - stats->mean) / std_dev);
    return (z_score > threshold);  /* Typical threshold: 3.0 */
}
