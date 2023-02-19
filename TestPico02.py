from lib.pico02 import can_picoX
# import json
import time
# from machine import Pin
from lib.merg_widgets import MergInput, MergLed

config = {
    "manufacturer": 165,
    "cpuManufId": 3,
    "module": 58,
    "name": "TEST",
    "major_version":  1,
    "minor_version": "A",
    "beta": 1,
    "consumer": True,
    "producer": True,
    "flim": True,
    "bootloader": False,
    "consume_own_events": False,
    "node_variables": 2,
    "event_variables": 3,
    "data_file": "TestCanPico.json"
}


class Test(can_picoX):
    def __init__(self):
        can_picoX.__init__(self, config)
        self.debug = False
        self.button = MergInput(21, self.button_on, self.button_off)
        self.green_led = MergLed(1)
        self.green_led.on = False
        self.amber_led = MergLed(0)
        self.amber_led.on = True
        self.amber_led.flash = True
        self.amber_led.level = 10
        self.amber_led.flash_frequency = 10
        self.red_led = MergLed(2)
        
    def button_on(self):
        self.acon(2)
        self.green_led.on = True
        self.red_led.flash = True
        self.red_led.flash_duration = 1000
        self.amber_led.level = 10
        
    def button_off(self):
        self.asof(2)
        self.green_led.on = False
        self.red_led.flash = False
        self.amber_led.level = 5

    def my_function(self, event):
        print('my_function ' + str(self.data['variables']) + ' : ' + str(event))
        # print('Event Variable 1 : '+str(event['variables'][1]))
        if event['variables'][1] == 1:
            print('Event Variable set to 1')
            if event['task'] == 'on':
                self.red_led.flash_frequency = 1
                self.red_led.flash = True
                self.red_led.flash_duration = event['variables'][2] * 10
                self.red_led.on = True
            else:
                self.red_led.flash = False
                self.red_led.on = False
        
    def run(self):
        print("TestPico02 RUN")
        while True:
            self.process()
            # self.button.check()
            # self.amber_led.check()
            time.sleep(0.001)
