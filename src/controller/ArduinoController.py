from serial import Serial

class ArduinoController():
    
    def __init__(self, device, baud, lock=None):
        self.device = device
        self.baud_rate = baud
        self.ser = None 
        self.lock = lock
        self.prevControls = []
    def start(self):
        self.ser = Serial(self.device, self.baud_rate)
        print("Arduino Controller started")        

    def send_message(self, msg):
        if msg != self.prevControls: 
            self.ser.write(msg)
            self.prevControls = msg.copy()
            print("writing " + ' '.join([str(x) for x in msg]))

        else:
            print("not writing " + ' '.join([str(x) for x in msg]))
        return
