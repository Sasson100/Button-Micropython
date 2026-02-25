from machine import Pin
from button import Button

# This code makes the button toggle the built in led,
# print to the terminal the multiclick count, and does
# a custom callback function

counter = 0

def custom_callback(state):
    global counter
    if state:
        counter += 1

led = Pin(2, Pin.OUT)
button = Button(12,custom_callback = custom_callback)
while True:
    if button.was_pressed():
        led.value(not led.value())
        print("Press count:",counter)
    if (count:=button.multi_click_final)>0:
        print("Multi-click count:",count)