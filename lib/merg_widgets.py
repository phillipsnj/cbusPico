from machine import Pin, PWM, Timer
from time import sleep
import time


class Button():
    def __init__(self, pin, event, on_function, off_function):
        self.button = Pin(21, Pin.IN, Pin.PULL_DOWN)
        self.button_status = self.button.value()
        self.event=event
        self.on_function = on_function
        self.off_function = off_function
        #self.timer = Timer(freq=10, mode=Timer.PERIODIC, callback=self.check())
        #self.timer.init(freq=10, mode=Timer.PERIODIC, callback=self.check())
        
    def check(self):
        if self.button_status != self.button.value():
            print('Button Changed : '+str(self.button.value()))
            if self.button.value() == 0:
                if self.off_function != None:
                   self.off_function(self.event) 
            else:
                if self.on_function != None:
                    self.on_function(self.event)
            self.button_status = self.button.value()


class MergInput():
    def __init__(self, pin, on_function, off_function):
        self.button = Pin(pin, Pin.IN, Pin.PULL_DOWN)
        self.button_status = self.button.value()
        self.duration = 50
        self.on_function = on_function
        self.off_function = off_function
        tim = Timer(period=self.duration, mode=Timer.ONE_SHOT, callback = self.check)
        
    def check(self, t):
        # print('Check Button '+str(self.button.value()))
        if self.button_status != self.button.value():
            # print('Button Changed : '+str(self.button.value()))
            if self.button.value() == 0:
                if self.off_function != None:
                   self.off_function() 
            else:
                if self.on_function != None:
                    self.on_function()
            self.button_status = self.button.value()
        tim = Timer(period=self.duration, mode=Timer.ONE_SHOT, callback = self.check)


class MergLed():
    def __init__(self, led_pin):
        self.led = PWM(Pin(led_pin))
        self.led.freq(50)
        self.gamma = [0,256,768,2304,5120,9216,15616,23808,34560,47616,65535]
        #self.action_time = time.ticks_ms()
        self.on = True
        self.level = 10
        self.position(self.level)
        self.flash_frequency = 5
        self.flash_duration = 500
        self.flash = False
        self.tim = Timer(period=self.flash_duration, mode=Timer.ONE_SHOT, callback = self.check)
#         timer = Timer()
#         timer.init(freq=self.flash_frequency, mode=Timer.PERIODIC, callback=self.check())
        #print('MERG_LED2 Initialised')
        
    def check(self, t):
        #print('MERG_LED2 Check')
        if self.flash:
            if self.on:
                self.position(0)
                self.on = False
            else:
                self.position(self.level)
                self.on = True
        else:
            if self.on:
                self.position(self.level)
            else:
                self.position(0)
        self.tim.deinit()
        self.tim = Timer(period=self.flash_duration, mode=Timer.ONE_SHOT, callback = self.check)
        
    def position(self, value):
        self.value = value
        if self.value > 10: self.value = 10
        if self.value <0 : self.value = 0
        self.led.duty_u16(self.gamma[self.value])
        