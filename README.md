# Button-Micropython

A pretty lightweight and configurable interrupt-based button driver for Micropython.

It includes:

* Timing and same-state software debounce
* Pressed/released events
* Hold duration
* Multi-click detection
* Custom callback function

Boards tested on:

* ESP32

## Table of Contents

* [Installation](#installation)
* [Usage](#usage)
* [Documentation](#documentation)

## Installation

There are 2 main ways of installing the library

1. Through a pc
   * Install [mpremote](https://pypi.org/project/mpremote/) on your pc
   * Connect your micropython device
   * Type in the console `mpremote connect <PORT> mip install github:https://github.com/Sasson100/Button-Micropython/package.json
`
2. Manual installation
    * Download the `button.py` file
    * Import it into your micropython device

## Usage

Here's a basic example of it's usage

```python
from button import Button
from machine import Pin

button = Button(15)
led = Pin(2,Pin.OUT)

while True:
    if button.was_pressed():
        led.value(1-led.value())
```

What this code does is define the button, define an LED pin, then do a loop where it checks if the button's been pressed, and toggles the led if it was.

Here's an example of a custom callback function for doing the same thing:

```python
from button import Button
from machine import Pin

led = Pin(2,Pin.OUT)
def button_callback(state:bool):
    if state:
        led.value(1-led.value())
button = Button(15, custom_callback = button_callback)

# a loop just to keep the program running
while True:
    pass
```

Do note that the custom callback function must only take 1 argument, that being the button's state

## Documentation

### Construction of a `Button` object

* `pin_id` – The pin's id.

* `debounce_ms` (optional) – The minimum time between changes in the button's state for them to be valid, in milliseconds. Default is 30ms.
* `pull` (optional) – Determines if the button is a pull-up or pull-down button, only accepts the strings "up" or "down" (without a care for capitalization). Default is set to pull-up.
* `multi_click_timeout` (optional) – The maximum time between presses for them to count for multi-click, in milliseconds. Default is 200ms.
* `custom_callback` (optional) – Allows you to define a custom callback function that'll trigger every time the button's state changes, must take only one variable, that being the state of the button.

### Methods

* `is_pressed()` – Returns the button's current state.
* `was_pressed()` – Returns if the button's been pressed since this method was last called.
* `was_released()` – Returns if the button's been released since this method was last called.
* `clear_events()` – Resets `was_pressed()`, `was_released()`, `multi_click_count` and `multi_click_final`.

### Attributes

* `hold_time` – The duration that the button's been held for in milliseconds.
* `multi_click_count` – The number of times the button's been pressed in a row, resets to 0 after the time after the last click goes over `multi_click_timeout`.
* `multi_click_final` – The number of times the button's been pressed in a row, but only gets updated after `multi_click_count` gets reset, and gets reset itself after being called.
