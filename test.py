from machine import Pin
from button import Button

# This code makes the button toggle the built in led
# and also print to the terminal the multiclick count
# when it's not 0
led = Pin(2, Pin.OUT)
button = Button(12)
while True:
    if button.was_pressed():
        led.value(not led.value())
    if (count:=button.multi_click_count)>0:
        print(count)