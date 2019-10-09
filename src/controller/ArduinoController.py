from serial import Serial

class ArduinoController():
    
    def __init__(self, device, baud):
        self.device = device
        self.baud_rate = baud
        self.ser = None 
    
    def start(self):
        self.ser = Serial(self.device, self.baud_rate)

    def send_message(self, msg):
        self.ser.write(msg)
        print(msg)
        return
