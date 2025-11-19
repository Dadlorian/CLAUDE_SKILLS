/**
 * @file    gpio_driver.h
 * @brief   Generic GPIO driver interface
 * @author  Embedded Systems Team
 * @date    2025-11-19
 */

#ifndef GPIO_DRIVER_H
#define GPIO_DRIVER_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief GPIO status codes
 */
typedef enum {
    GPIO_OK = 0,
    GPIO_ERROR,
    GPIO_ERROR_INVALID_PARAM,
    GPIO_ERROR_NOT_INITIALIZED,
    GPIO_ERROR_INVALID_MODE,
    GPIO_ERROR_TIMEOUT
} gpio_status_t;

/**
 * @brief GPIO port identifiers
 */
typedef enum {
    GPIO_PORT_A = 0,
    GPIO_PORT_B,
    GPIO_PORT_C,
    GPIO_PORT_D,
    GPIO_PORT_E,
    GPIO_PORT_F,
    GPIO_PORT_G,
    GPIO_PORT_H,
    GPIO_PORT_COUNT
} gpio_port_t;

/**
 * @brief GPIO pin modes
 */
typedef enum {
    GPIO_MODE_INPUT = 0,
    GPIO_MODE_OUTPUT,
    GPIO_MODE_ALTERNATE,
    GPIO_MODE_ANALOG,
    GPIO_MODE_COUNT
} gpio_mode_t;

/**
 * @brief GPIO pull-up/pull-down configuration
 */
typedef enum {
    GPIO_PULL_NONE = 0,
    GPIO_PULL_UP,
    GPIO_PULL_DOWN,
    GPIO_PULL_COUNT
} gpio_pull_t;

/**
 * @brief   Initialize GPIO pin
 * @param   port  GPIO port
 * @param   pin   Pin number (0-15)
 * @param   mode  Pin mode
 * @param   pull  Pull-up/pull-down configuration
 * @return  GPIO_OK on success, error code otherwise
 */
gpio_status_t gpio_init(gpio_port_t port, uint8_t pin,
                         gpio_mode_t mode, gpio_pull_t pull);

/**
 * @brief   Set GPIO pin high
 * @param   port  GPIO port
 * @param   pin   Pin number
 * @return  GPIO_OK on success, error code otherwise
 */
gpio_status_t gpio_set(gpio_port_t port, uint8_t pin);

/**
 * @brief   Set GPIO pin low
 * @param   port  GPIO port
 * @param   pin   Pin number
 * @return  GPIO_OK on success, error code otherwise
 */
gpio_status_t gpio_clear(gpio_port_t port, uint8_t pin);

/**
 * @brief   Toggle GPIO pin
 * @param   port  GPIO port
 * @param   pin   Pin number
 * @return  GPIO_OK on success, error code otherwise
 */
gpio_status_t gpio_toggle(gpio_port_t port, uint8_t pin);

/**
 * @brief   Read GPIO pin state
 * @param   port   GPIO port
 * @param   pin    Pin number
 * @param   state  Pointer to store pin state (true=high, false=low)
 * @return  GPIO_OK on success, error code otherwise
 */
gpio_status_t gpio_read(gpio_port_t port, uint8_t pin, bool *state);

/**
 * @brief   Write GPIO pin state
 * @param   port   GPIO port
 * @param   pin    Pin number
 * @param   state  State to write (true=high, false=low)
 * @return  GPIO_OK on success, error code otherwise
 */
gpio_status_t gpio_write(gpio_port_t port, uint8_t pin, bool state);

#ifdef __cplusplus
}
#endif

#endif /* GPIO_DRIVER_H */
