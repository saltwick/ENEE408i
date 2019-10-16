from serial import Serial

class ArduinoController():
    
    def __init__(self, device, baud, lock):
        self.device = device
        self.baud_rate = baud
        self.ser = None 
        self.lock = lock
    
    def start(self):
        self.ser = Serial(self.device, self.baud_rate)
        print("Arduino Controller started")        

    def send_message(self, msg):
        self.ser.write(msg)
        print(msg)
        return
