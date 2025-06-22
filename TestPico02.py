from lib.pico02 import can_pico
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
    "node_variables": 8,
    "event_variables": 8,
    "data_file": "TestCanPico.json"
}


class Test(can_pico):
    def __init__(self):
        can_pico.__init__(self, config)
        self.debug = True
        self.actions['E1'] = self.session_info # Add E1 opcode

    def my_function(self, event):
        print('my_function ' + str(self.data['variables']) + ' : ' + str(event))
        # print('Event Variable 1 : '+str(event['variables'][1]))
        
    def rloc(self, loco_id):
        output = self.get_header() + "40" + self.pad(loco_id, 4) + ";"
        self.send(output)

    def stmod(self, session_id, speed):
        output = self.get_header() + "47" + self.pad(session_id, 2) + self.pad(spee2, 4) + ";"
        self.send(output)
        
    def session_info(self, msg):  # i.e. session requested from CANCMD.
        # CbusFlimNode does not take account of long/short address variations.
        self.my_function({'task': 'dcc', 'variables':{'session': self.get_str(msg, 9, 2), 'loco_id': self.get_str(msg, 11, 4)}}) 
        
    def run(self):
        print("TestPico02 RUN")
        while True:
            self.process()
            # self.button.check()
            # self.amber_led.check()
            time.sleep(0.001)
