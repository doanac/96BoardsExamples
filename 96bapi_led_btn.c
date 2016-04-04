#include <stdio.h>

/* 96BoardsGPIO header file */
#include <gpio.h>


int main(int argc, char * argv[])
{
	unsigned int gpio_led = gpio_id("GPIO_G");
	unsigned int gpio_btn = gpio_id("GPIO_E");

	if (gpio_open(gpio_led, "out") || gpio_open(gpio_btn, "in")) {
		fprintf(stderr, "Unable to open GPIOs\n");
		return -1;
	}

	while(1) {
		digitalWrite(gpio_led, digitalRead(gpio_btn));
		usleep(100000);
	}
	return 0;
}
