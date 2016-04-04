#!/usr/bin/python3

from libsoc import gpio


def main(led, btn):
    with gpio.request_gpios((led, btn)):
        while True:
            if btn.poll(100):
                if btn.is_high():
                    led.set_high()
                else:
                    led.set_low()


if __name__ == '__main__':
    led = gpio.GPIO(gpio.GPIO.gpio_id('GPIO_G'), gpio.DIRECTION_OUTPUT)
    btn = gpio.GPIO(
        gpio.GPIO.gpio_id('GPIO_E'), gpio.DIRECTION_INPUT, gpio.EDGE_BOTH)
    main(led, btn)
