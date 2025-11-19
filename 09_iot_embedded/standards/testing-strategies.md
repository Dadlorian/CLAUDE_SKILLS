# Embedded Systems Testing Strategies

## Unit Testing

**Framework**: Unity (C), Google Test (C++)

```c
void test_gpio_init(void) {
    gpio_status_t status = gpio_init(GPIO_PORT_A, 5, GPIO_MODE_OUTPUT, GPIO_PULL_NONE);
    TEST_ASSERT_EQUAL(GPIO_OK, status);
}

void test_gpio_set(void) {
    gpio_init(GPIO_PORT_A, 5, GPIO_MODE_OUTPUT, GPIO_PULL_NONE);
    TEST_ASSERT_EQUAL(GPIO_OK, gpio_set(GPIO_PORT_A, 5));
}
```

## Hardware-in-the-Loop (HIL)

- Connect real hardware to test rig
- Automate GPIO stimulus/measurement
- Power cycle testing
- Temperature chamber testing

## Coverage Targets

- **Statement Coverage**: > 80%
- **Branch Coverage**: > 70%
- **MC/DC (safety-critical)**: 100% critical paths

## Continuous Integration

```yaml
# .github/workflows/embedded-ci.yml
name: Embedded CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install ARM GCC
        run: sudo apt-get install gcc-arm-none-eabi
      - name: Build
        run: make
      - name: Unit Tests
        run: make test
```
