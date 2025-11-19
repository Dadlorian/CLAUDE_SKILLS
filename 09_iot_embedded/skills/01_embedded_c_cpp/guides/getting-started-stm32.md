# Getting Started with STM32 Embedded Development

## Development Environment Setup

### Required Tools

1. **STM32CubeMX** - Configuration tool
2. **STM32CubeIDE** - IDE (Eclipse-based) OR VS Code + extensions
3. **ARM GCC Toolchain** - Compiler
4. **ST-Link** - Debugger/programmer
5. **OpenOCD** or **STM32CubeProgrammer** - Flashing tools

### Installation (Ubuntu/Debian)

```bash
# Install ARM GCC toolchain
sudo apt-get install gcc-arm-none-eabi gdb-multiarch

# Install OpenOCD
sudo apt-get install openocd

# Install ST-Link tools
sudo apt-get install stlink-tools

# Install build tools
sudo apt-get install cmake make ninja-build
```

## Project Creation with STM32CubeMX

### Step 1: New Project

1. Open STM32CubeMX
2. File → New Project
3. Select your MCU (e.g., STM32F401RET6)
4. Click "Start Project"

### Step 2: Pin Configuration

```
PA5  → GPIO_Output (LED)
PA0  → GPIO_EXTI0 (Button with interrupt)
PA9  → USART1_TX
PA10 → USART1_RX
PB6  → I2C1_SCL
PB7  → I2C1_SDA
```

### Step 3: Clock Configuration

- Set HCLK to maximum (84 MHz for STM32F401)
- Enable HSE if using external crystal
- Configure PLL

### Step 4: Peripheral Configuration

#### USART1 Setup
- Mode: Asynchronous
- Baud Rate: 115200
- Word Length: 8 Bits
- Stop Bits: 1
- Parity: None

#### I2C1 Setup
- Mode: I2C
- Speed: 100 kHz (Standard) or 400 kHz (Fast)
- Addressing Mode: 7-bit

### Step 5: Generate Code

- Project Manager → Project
  - Project Name: "my_project"
  - Toolchain/IDE: Makefile or STM32CubeIDE
- Generate Code

## Project Structure

```
my_project/
├── Core/
│   ├── Inc/           # Header files
│   │   ├── main.h
│   │   └── stm32f4xx_it.h
│   ├── Src/           # Source files
│   │   ├── main.c
│   │   └── stm32f4xx_it.c
│   └── Startup/
│       └── startup_stm32f401xe.s
├── Drivers/
│   ├── STM32F4xx_HAL_Driver/
│   └── CMSIS/
├── Makefile
└── STM32F401RETX_FLASH.ld  # Linker script
```

## Hello World: Blink LED

### main.c

```c
#include "main.h"

void SystemClock_Config(void);
static void MX_GPIO_Init(void);

int main(void) {
    /* Reset of all peripherals, Initializes Flash and Systick */
    HAL_Init();

    /* Configure system clock */
    SystemClock_Config();

    /* Initialize GPIO */
    MX_GPIO_Init();

    /* Infinite loop */
    while (1) {
        /* Toggle LED */
        HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5);

        /* Delay 500ms */
        HAL_Delay(500);
    }
}

static void MX_GPIO_Init(void) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    /* GPIO Ports Clock Enable */
    __HAL_RCC_GPIOA_CLK_ENABLE();

    /* Configure GPIO pin : PA5 */
    GPIO_InitStruct.Pin = GPIO_PIN_5;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
}

void SystemClock_Config(void) {
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

    /* Configure main internal regulator voltage */
    __HAL_RCC_PWR_CLK_ENABLE();
    __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE2);

    /* Initialize RCC Oscillators */
    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
    RCC_OscInitStruct.HSIState = RCC_HSI_ON;
    RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
    RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
    RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
    RCC_OscInitStruct.PLL.PLLM = 16;
    RCC_OscInitStruct.PLL.PLLN = 336;
    RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV4;
    RCC_OscInitStruct.PLL.PLLQ = 7;
    HAL_RCC_OscConfig(&RCC_OscInitStruct);

    /* Initialize CPU, AHB and APB busses clocks */
    RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK
                                | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
    RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
    HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2);
}
```

## Building the Project

### Using Makefile

```bash
# Build
make

# Clean
make clean

# Output: build/my_project.elf, build/my_project.bin, build/my_project.hex
```

### Using CMake (Alternative)

```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 3.15)
project(my_project C ASM)

set(CMAKE_C_STANDARD 11)

enable_language(C ASM)

set(MCU_FLAGS "-mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard")

set(CMAKE_C_FLAGS "${MCU_FLAGS} -Wall -Wextra -O2 -g")
set(CMAKE_EXE_LINKER_FLAGS "${MCU_FLAGS} -T${CMAKE_SOURCE_DIR}/STM32F401RETX_FLASH.ld")

# Add sources
file(GLOB_RECURSE SOURCES "Core/Src/*.c" "Drivers/**/*.c")
add_executable(${PROJECT_NAME}.elf ${SOURCES} Core/Startup/startup_stm32f401xe.s)

# Include directories
target_include_directories(${PROJECT_NAME}.elf PRIVATE
    Core/Inc
    Drivers/STM32F4xx_HAL_Driver/Inc
    Drivers/CMSIS/Device/ST/STM32F4xx/Include
    Drivers/CMSIS/Include
)

# Generate .bin and .hex
add_custom_command(TARGET ${PROJECT_NAME}.elf POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} -O binary $<TARGET_FILE:${PROJECT_NAME}.elf> ${PROJECT_NAME}.bin
    COMMAND ${CMAKE_OBJCOPY} -O ihex $<TARGET_FILE:${PROJECT_NAME}.elf> ${PROJECT_NAME}.hex
)
```

```bash
mkdir build && cd build
cmake -DCMAKE_TOOLCHAIN_FILE=../arm-none-eabi-gcc.cmake ..
make
```

## Flashing the Firmware

### Using ST-Link

```bash
# Flash .bin file
st-flash write build/my_project.bin 0x8000000

# Erase flash
st-flash erase
```

### Using OpenOCD

```bash
# Flash
openocd -f interface/stlink.cfg -f target/stm32f4x.cfg \
    -c "program build/my_project.elf verify reset exit"
```

### Using STM32CubeProgrammer (GUI)

1. Connect ST-Link to PC and board
2. Open STM32CubeProgrammer
3. Select ST-LINK, click Connect
4. Open File → Open file (select .hex or .bin)
5. Click "Download"

## Debugging with GDB

### Terminal 1: Start OpenOCD

```bash
openocd -f interface/stlink.cfg -f target/stm32f4x.cfg
```

### Terminal 2: Start GDB

```bash
arm-none-eabi-gdb build/my_project.elf

(gdb) target remote localhost:3333
(gdb) monitor reset halt
(gdb) load
(gdb) monitor reset init
(gdb) break main
(gdb) continue
```

### VS Code Integration (launch.json)

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug STM32",
            "type": "cppdbg",
            "request": "launch",
            "program": "${workspaceFolder}/build/my_project.elf",
            "cwd": "${workspaceFolder}",
            "MIMode": "gdb",
            "miDebuggerPath": "/usr/bin/arm-none-eabi-gdb",
            "miDebuggerServerAddress": "localhost:3333",
            "setupCommands": [
                {
                    "text": "target remote localhost:3333"
                },
                {
                    "text": "monitor reset halt"
                },
                {
                    "text": "load"
                },
                {
                    "text": "monitor reset init"
                }
            ]
        }
    ]
}
```

## Common Issues & Solutions

### Issue: st-flash: error while loading shared libraries

```bash
sudo apt-get install libusb-1.0-0-dev
```

### Issue: Permission denied /dev/ttyUSB0

```bash
sudo usermod -a -G dialout $USER
sudo usermod -a -G plugdev $USER
# Logout and login
```

### Issue: ST-Link not detected

```bash
# Install udev rules
sudo cp /usr/share/doc/stlink-tools/stlink-udev-rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## Next Steps

1. **UART Communication**: Implement printf via UART
2. **Interrupts**: Handle button press with EXTI
3. **Timers**: Generate PWM for LED brightness control
4. **I2C**: Read sensor data (BME280, MPU6050)
5. **DMA**: Efficient data transfer
6. **Low Power**: Sleep modes and wake-up

## Resources

- [STM32 Documentation](https://www.st.com/en/microcontrollers-microprocessors/stm32-32-bit-arm-cortex-mcus.html)
- [STM32CubeMX User Manual](https://www.st.com/resource/en/user_manual/dm00104712.pdf)
- [ARM Cortex-M4 Programming](https://www.arm.com/products/silicon-ip-cpu/cortex-m/cortex-m4)
