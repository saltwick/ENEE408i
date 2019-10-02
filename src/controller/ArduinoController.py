import serial

class ArduinoController():
    
    def __init__(self, device, baud):
        self.device = device
        self.baud_rate = baud
        self.ser = None
    
    def start(self):
        self.ser = serial.Serial(self.device, self.baud_rate)

    def send_message(self, msg):
#        self.ser.write(str(msg))
        print(str(msg.hex()))
