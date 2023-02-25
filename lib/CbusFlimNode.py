# from machine import Pin, SPI, Timer
# import time
# import cbus2515
import json
# import io
# import os


class CbusNode:
    def __init__(self, config):
        
        # self.nodeId = node_id
        self.debug = False
        self.data_file = config['data_file']
        self.count = 0
        self.canId = 75
        self.priority1 = 2
        self.priority2 = 3
        self.learn = False
        self.interface = 2  # 1 can, 2 ethernet
        self.intOut = 0
        self.chrOut = ""
        
        try:
            with open(self.data_file) as f:
                self.data = json.load(f)
                self.nodeId = self.data['nodeId']
        except OSError:
            print('Initialise Module')
            print('create flim_data_test.json')
            self.data = {'parameters': [],
                         'variables': [0] * (config["node_variables"] + 1),
                         'events': {},
                         'manufId': config["manufacturer"],
                         'cpuManufId':config["cpuManufId"],
                         'moduleId': config["module"],
                         'name': config["name"],
                         'minorVersion': config["minor_version"],
                         'numEvents': 255,
                         'numEventVariables': config["event_variables"],
                         'numNodeVariables': config["node_variables"],
                         'majorVersion': config["major_version"],
                         'beta': config["beta"],
                         'consumer': config["consumer"],
                         'producer': config["producer"],
                         'flim': True,
                         'bootloader': False,
                         'coe': config["consume_own_events"],
                         'nodeId': 0
                         }

            self.data['parameters'].append(self.pad(20, 2))
            self.data['parameters'].append(self.pad(self.data['manufId'], 2))
            self.data['parameters'].append(self.pad(ord(self.data['minorVersion']), 2))  # Character
            self.data['parameters'].append(self.pad(self.data['moduleId'], 2))
            self.data['parameters'].append(self.pad(self.data['numEvents'], 2))
            self.data['parameters'].append(self.pad(self.data['numEventVariables'], 2))            
            self.data['parameters'].append(self.pad(self.data['numNodeVariables'], 2))
            self.data['parameters'].append(self.pad(self.data['majorVersion'], 2))
            self.data['parameters'].append(self.pad(self.flags(), 2))
            self.data['parameters'].append(self.pad(0, 2))
            self.data['parameters'].append(self.pad(self.interface, 2))
            self.data['parameters'].append(self.pad(0, 2))
            self.data['parameters'].append(self.pad(0, 2))
            self.data['parameters'].append(self.pad(0, 2))
            self.data['parameters'].append(self.pad(0, 2))
            self.data['parameters'].append(self.pad(0, 2))
            self.data['parameters'].append(self.pad(0, 2))
            self.data['parameters'].append(self.pad(0, 2))
            self.data['parameters'].append(self.pad(0, 2))
            self.data['parameters'].append(self.pad(self.data['cpuManufId'], 2))
            self.data['parameters'].append(self.pad(self.data['beta'], 2))

            print("New Node")
            self.nodeId = self.data['nodeId']
            self.save_data()

        self.actions = {
            "53": self.learn_mode_on,
            "54": self.learn_mode_off,
            "57": self.send_all_events,
            "58": self.send_number_of_events,
            "71": self.read_nv,
            "90": self.acc_on,
            "91": self.acc_off,
            "95": self.remove_event,
            "96": self.write_nv,
            "98": self.asc_on,
            "99": self.asc_off,
            "73": self.paran,
            "0D": self.qnn,
            "9C": self.read_ev,
            "D2": self.write_ev,
            "10": self.params,
            "42": self.set_node_id
            }

    @staticmethod
    def pad(num, length):
        output = '0000000000' + hex(num)[2:]
        return output[length * -1:]

    @staticmethod
    def get_int(msg, start, length):
        return int(msg[start: start + length], 16)

    @staticmethod
    def get_str(msg, start, length):
        return msg[start: start + length]

    def save_data(self):
        if self.debug:
            print('save_data : '+self.data_file)
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f)

    def get_op_code(self, msg):
        return self.get_str(msg, 7, 2)

    def get_node_id(self, msg):
        return int(self.get_str(msg, 9, 4), 16)

    def get_header(self):
        output = 0
        output = output + self.priority1
        output = output << 2
        output = output + self.priority2
        output = output << 7
        output = output + self.canId
        output = output << 5
        # print(str(output))
        # return str(output)
        # print (":S"+format(output, '02x')+"N")
        # return ":S"+format(output, '02x')+"N"
        return ":S" + hex(output)[2:] + "N"
        # return ":SB020N"

    def flags(self):
        flags = 0
        if self.data['consumer']:
            flags += 1
        if self.data['producer']:
            flags += 2
        if self.data['flim']:
            flags += 4
        if self.data['bootloader']:
            flags += 8
        if self.data['coe']:
            flags += 16
        if self.learn:
            flags += 32
        return flags

    def execute(self, msg):
        """
        Executes the function passed when class created.
        :param msg: Dictionary containing the message task (On|Off) and Variables
                    which was passed when the event was taught to the module.
        """
        self.my_function(msg)

    def send(self, msg):
        """
        This function send a message to the CBUS network. In the Parent class it
        does nothing, it will be overridden by a child class to handle the network
        type specifically
        :param msg: CBUS Message to be sent to the CBUS Network
        """
        print("Merg LCB NODE Send : " + msg)

    def acon(self, event_id):
        """
        Sends a Accessory On Long Event to the CBUS Network
        :param event_id: Id for the event
        """
        output = self.get_header() + "90" + self.pad(self.nodeId, 4) + self.pad(event_id, 4) + ";"
        self.send(output)
        if self.get_str(output, 9, 8) in self.data['events']:
            print("Local Event is Known")
            if self.debug:
                print("Local Event is Known")
            # self.execute({'task': 'on', 'variables': self.events[self.get_str(msg, 9, 8)]})
            self.my_function({'task': 'on', 'variables': self.data['events'][self.get_str(output, 9, 8)]['variables']})

    def acof(self, event_id):
        output = self.get_header() + "91" + self.pad(self.nodeId, 4) + self.pad(event_id, 4) + ";"
        self.send(output)
        if self.get_str(output, 9, 8) in self.data['events']:
            print("Local Event is Known")
            if self.debug:
                print("Local Event is Known")
            # self.execute({'task': 'on', 'variables': self.events[self.get_str(msg, 9, 8)]})
            self.my_function({'task': 'off', 'variables': self.data['events'][self.get_str(output, 9, 8)]['variables']})

    def ason(self, event_id):
        print("ASON :" + str(event_id))
        output = self.get_header() + "98" + self.pad(self.nodeId, 4) + self.pad(event_id, 4) + ";"
        self.send(output)
        if self.debug:
            print('ASON : '+output)

    def asof(self, event_id):
        output = self.get_header() + "99" + self.pad(self.nodeId, 4) + self.pad(event_id, 4) + ";"
        self.send(output)

    def pnn(self):
        output = self.get_header() + "B6" + self.pad(self.nodeId, 4) + self.pad(self.data['manufId'], 2) + self.pad(
            self.data['moduleId'], 2) + self.pad(self.flags(), 2) + ";"
        self.send(output)

    # def heartb(self):
    #     output = self.get_header() + "AB" + self.pad(self.nodeId, 4) + '000000'+";"
    #     self.send(output)
        
    def rqnn(self):
        output = self.get_header() + "50" + "0000;"
        self.learn = True
        self.send(output)

    def set_parameter(self, param, value):
        self.data['parameters'][param] = self.pad(value, 2)

    def parameter(self, param):
        if self.debug:
            print("parameter : " + str(self.nodeId) + " : " + str(param) + " : " + str(self.data['parameters'][param]))
        output = self.get_header() + "9B" + self.pad(self.nodeId, 4) + self.pad(param, 2) + self.data['parameters'][param] + ";"
        if self.debug:
            print("parameter output : " + output)
        return output
    
    def parameters(self):
        print('Parameters')
        output = self.get_header() + "EF"
        output = output + self.data['parameters'][1] 
        output = output + self.data['parameters'][2]
        output = output + self.data['parameters'][3]
        output = output + self.data['parameters'][4]
        output = output + self.data['parameters'][5]
        output = output + self.data['parameters'][6]
        output = output + self.data['parameters'][7]
        output = output + ";"
        self.send(output)

    def teach_long_event(self, node_id, event_id, variables):
        """
        Teaches a long CBUS event to the module
        :param node_id: node id of the event
        :param event_id: event od of the event
        :param variables: Variable that will be sent to the function when event
                is received. Can be String, number, list etc
        """
        new_id = self.pad(node_id, 4) + self.pad(event_id, 4)
        # self.events[new_id] = variables
        self.data['events'][new_id.upper()] = variables
        if self.debug:
            print(self.events)

    def teach_short_event(self, event_id, variables):
        """
        Teaches a short CBUS event to the module
        :param event_id: event of the short event
        :param variables: Variable that will be sent to the function when event
               is received. Can be String, number, list etc
        """
        new_id = self.pad(0, 4) + self.pad(event_id, 4)
        # self.events[new_id] = variables
        self.data['events'][new_id.upper()] = variables
        if self.debug:
            print(json.dumps(self.events, indent=4))

    def rloc(self, loco_id):
        output = self.get_header() + "40" + self.pad(loco_id, 4) + ";"
        self.send(output)

    def stmod(self, session_id, speed):
        output = self.get_header() + "47" + self.pad(session_id, 2) + self.pad(spee2, 4) + ";"
        self.send(output)

    def nvans(self, nv_index):
        if self.debug:
            print("NVANS : " + str(self.nodeId) + " : " + str(nv_index) + " : " + str(self.data['variables'][nv_index]))
        output = self.get_header() + "97" + self.pad(self.nodeId, 4) + self.pad(nv_index, 2) + self.pad(
            self.data['variables'][nv_index], 2) + ";"
        if self.debug:
            print("NVANS output : " + output)
        return output

    def neval(self, event_index, event_variable_index):
        print("NEVAL : " + str(self.nodeId) + " : " + str(event_index) + " : " + str(event_variable_index))
        # print("NEVAL : " + str(self.data['events'][event_index-1]['variables'][event_variable_index]))
        events = list(self.data['events'].values())
        if self.debug:
            print('NEVAL events : '+str(events))
            print("NEVAL : " + str(self.nodeId) + " : " + self.pad(event_index, 2) + " : " + str(
                events[event_index - 1]['variables']))
        output = self.get_header() \
                 + "B5" + self.pad(self.nodeId, 4) \
                 + self.pad(event_index, 2) \
                 + self.pad(event_variable_index, 2) \
                 + self.pad(events[event_index - 1]['variables'][event_variable_index], 2) \
                 + ";"
        if self.debug:
            print("NEVAL output : " + output)
        return output

    def ensrp(self, event_index, event_identifier):
        if self.debug:
            print("ENSRP : " + str(self.nodeId) + " : " + event_identifier + " : " + str(event_index))
        output = self.get_header() + "F2" + self.pad(self.nodeId, 4) + event_identifier + self.pad(event_index, 2) + ";"
        if self.debug:
            print("ENSRP output : " + output)
        return output

    def cmderror(self, error):
        if self.debug:
            print("CMDERROR received: " + str(self.nodeId) + " : " + str(error))
        output = self.get_header() + "6F" + self.pad(self.nodeId, 4) + self.pad(error, 2) + ";"
        if self.debug:
            print("CMDERROR Output: " + output)
        return output

    def wrack(self):
        if self.debug:
            print("WRACK : " + str(self.nodeId))
        output = self.get_header() + "59" + self.pad(self.nodeId, 4) + ";"
        if self.debug:
            print("WRACK : " + output)
        return output
    
    def nnack(self):
        print("NNACK : " + str(self.nodeId))
        if self.debug:
            print("NNACK : " + str(self.nodeId))
        output = self.get_header() + "52" + self.pad(self.nodeId, 4) + ";"
        if self.debug:
            print("NNACK : " + output)
        return output

    def numev(self):
        if self.debug:
            print("NUMEV : " + str(self.nodeId))
        output = self.get_header() + "74" + self.pad(self.nodeId, 4) + self.pad(len(self.data['events']), 2) + ";"
        if self.debug:
            print("NUMEV : " + output)
        return output

    def acc_on(self, msg):
        if self.debug:
            print("acc_on : " + msg + " Event : " + self.get_str(msg, 9, 8))
        if self.get_str(msg, 9, 8) in self.data['events']:
            if self.debug:
                print("Event is Known")
            # self.execute({'task': 'on', 'variables': self.events[self.get_str(msg, 9, 8)]})
            self.my_function({'task': 'on', 'variables': self.data['events'][self.get_str(msg, 9, 8)]['variables']})
        else:
            if self.debug:
                print("Event is Unknown")

    def acc_off(self, msg):
        if self.debug:
            print("acc_off : " + msg)
        if self.get_str(msg, 9, 8) in self.data['events']:
            if self.debug:
                print("Event is Known")
            # self.execute({'task': 'off', 'variables': self.events[self.get_str(msg, 9, 8)]})
            self.my_function({'task': 'off', 'variables': self.data['events'][self.get_str(msg, 9, 8)]['variables']})
        else:
            if self.debug:
                print("Event is Unknown")

    def asc_on(self, msg):
        event_identifier = "0000" + self.get_str(msg, 13, 4)
        if self.debug:
            print("asc_on : " + msg + " Event : " + event_identifier)
        if event_identifier in self.data['events']:
            if self.debug:
                print("Event is Known")
            # self.execute({'task': 'on', 'variables': self.events[self.get_str(msg, 9, 8)]})
            self.my_function({'task': 'on', 'variables': self.data['events'][self.get_str(msg, 9, 8)]['variables']})
        else:
            if self.debug:
                print("Event is Unknown")

    def asc_off(self, msg):
        event_identifier = "0000" + self.get_str(msg, 13, 4)
        if self.debug:
            print("asc_off : " + msg + " Event : " + event_identifier)
        if event_identifier in self.data['events']:
            if self.debug:
                print("Event is Known")
            # self.execute({'task': 'on', 'variables': self.events[self.get_str(msg, 9, 8)]})
            self.my_function({'task': 'off', 'variables': self.data['events'][self.get_str(msg, 9, 8)]['variables']})
        else:
            if self.debug:
                print("Event is Unknown")

    def paran(self, msg):
        parameter_id = self.get_int(msg, 13, 2)
        parameter_value = self.data['parameters'][parameter_id]
        if self.debug:
            print("paran : " + msg + " nodeId : " + str(self.get_node_id(msg)))
        if self.get_node_id(msg) == self.nodeId:
            if self.debug:
                print("paran for " + str(self.nodeId) +
                      " Parameter " + str(parameter_id) +
                      " Value : " + str(parameter_value))
            if self.debug:
                print("Paran Output " + str(self.parameter(parameter_id)))
            # time.sleep(1)
            # self.parameter(parameter_id)
            if parameter_id == 0:
                for i in range(21):
                    self.send(str(self.parameter(i)))
            else:
                self.send(str(self.parameter(parameter_id)))

    def qnn(self, msg):
        if self.debug:
            print("qnn : " + msg)
        self.pnn()

    def session_info(self, msg):
        if self.debug:
            print("E1 : PLOC - " + msg)
        self.Function({'task': 'dcc',
                       'sesson': self.get_str(msg, 9, 2),
                       'loco_id': self.get_str(msg, 11, 2)})

    def read_nv(self, msg):
        if self.get_node_id(msg) == self.nodeId:
            if self.debug:
                print("NVRD : " + msg)
            nv_index = self.get_int(msg, 13, 2)
            if nv_index == 0:
                for i in range(self.data['numNodeVariables'] + 1):
                    self.send(self.nvans(i))
            elif nv_index <= self.data['numNodeVariables']:
                self.send(self.nvans(nv_index))
            else:
                self.send(self.cmderror(10))

    def read_ev(self, msg):
        if self.get_node_id(msg) == self.nodeId:
            if self.debug:
                print("REVAL : " + msg)
            ev_index = self.get_int(msg, 13, 2)
            
            ev_variable_index = self.get_int(msg, 15, 2)
            if ev_variable_index == 0:
                for i in range(self.data['numEventVariables'] + 1):
                    self.send(self.neval(ev_index, i))
            elif ev_index <= self.data["numEventVariables"]:
                self.send(self.neval(ev_index, ev_variable_index))
            else:
                self.send(self.cmderror(6))

    def write_nv(self, msg):
        if self.get_node_id(msg) == self.nodeId:
            if self.debug:
                print("NVSET : " + msg)
            nv_index = self.get_int(msg, 13, 2)
            nv_value = self.get_int(msg, 15, 2)
            if nv_index <= self.data["numNodeVariables"]:
                if self.debug:
                    print("NVSET : " + str(nv_index) + ' : ' + str(nv_value))
                self.data["variables"][nv_index] = nv_value
                self.save_data()
                self.send(self.wrack())
            else:
                self.send(self.cmderror(10))

    def write_ev(self, msg):
        if self.learn:
            if self.debug:
                print("EVLRN : " + msg)
            event_identifier = self.get_str(msg, 9, 8)
            ev_index = self.get_int(msg, 17, 2)
            ev_value = self.get_int(msg, 19, 2)
            # event_list = [event for event in self.data['events'] if event['event_identifier'] == event_indentifier]
            if (event_identifier in self.data['events']):
                # event_id = next(index for (index, event) in enumerate(self.data['events']) if
                #                 event['event_identifier'] == event_indentifier)
                event_id = list(self.data['events']).index(event_identifier) + 1
                # print('EVLRN : Update Event Variable ' + str(event_id) + ' : ' + str(event_list))
                print('EVLRN : Update Event Variable ' + event_identifier + ' : ' + str(ev_index) + ' : ' + str(
                    ev_value))
                self.data['events'][event_identifier]['variables'][ev_index] = ev_value
                self.save_data()
            else:
                print('EVLRN : Create New Event')
                self.data['events'][event_identifier] = {}
                self.data['events'][event_identifier]["event_identifier"] = event_identifier
                self.data['events'][event_identifier]["variables"] = [0] * (self.data['numEventVariables'] + 1)
                self.data['events'][event_identifier]['variables'][ev_index] = ev_value
                self.save_data()
                # self.send(self.cmderror(7))

    def remove_event(self, msg):
        if self.learn:
            if self.debug:
                print("EVULN : " + msg)
            event_indentifier = self.get_str(msg, 9, 8)
            event_list = [event for event in self.data['events'] if event['event_identifier'] == event_indentifier]
            if len(event_list) > 0:
                event_id = next(index for (index, event) in enumerate(self.data['events']) if
                                    event['event_identifier'] == event_indentifier)
                del self.data['events'][event_id]
                self.save_data()
            elif len(event_list) == 0:
                print('EVULN : Too Many Events')
                self.send(self.cmderror(7))
            else:
                print('EVULN : Too Many Events')
                self.send(self.cmderror(4))

    def learn_mode_on(self, msg):
        if self.get_node_id(msg) == self.nodeId:
            if self.debug:
                print("NNLRN : " + msg)
            self.learn = True

    def learn_mode_off(self, msg):
        if self.get_node_id(msg) == self.nodeId:
            if self.debug:
                print("NNLUN : " + msg)
            self.learn = False

    def send_all_events(self, msg):
        if self.get_node_id(msg) == self.nodeId:
            event_count = 1
            if self.debug:
                print("NERD : " + msg)
            for event in self.data['events']:
                print('ENSRP ' + str(event_count) + ' : ' + str(event))
                self.send(self.ensrp(event_count, str(event)))
                event_count += 1

    def send_number_of_events(self, msg):
        if self.get_node_id(msg) == self.nodeId:
            if self.debug:
                print("RQEVN : " + msg)
            self.send(self.numev())

    def params(self, msg):
        print('PARAMS')
        if self.learn:
            self.parameters()

    def set_node_id(self, msg):
        if self.learn:
            self.data['nodeId'] = self.get_node_id(msg)
            self.nodeId = self.data['nodeId']
            self.nnack()
            self.learn = False
            self.save_data()

    def action_opcode(self, msg):

        opcode = self.get_op_code(msg)
        if self.debug:
            print("Opcode : " + opcode)
        self.count += 1
        if self.debug:
            print("Msg Count" + str(self.count))
        if opcode in self.actions:
            if self.debug:
                print("Processing Opcode : " + opcode)
            func = self.actions[opcode]
            func(msg)
        else:
            if self.debug:
                print("Unknown Opcode : " + opcode)
            # self.Function(msg)
            
    def my_function(self, event_variables):
        print('my_function ' + str(self.data['variables']) + ' : ' + str(event_variables))

    def execute(self, msg):
        # self.Function(msg)
        if self.debug:
            print("Execute MSG : " + msg)
        self.action_opcode(msg)

    def send(self, msg):
        # print("Pico Node Send : " + msg)
        self.can.send(msg)
        
    def process(self):
        print("NODE PROCESS")

    def run(self):
        print("NODE RUN")

