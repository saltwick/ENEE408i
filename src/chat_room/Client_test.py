from Client import Client
import threading

class ClientThread():
    def __init__(self, name, send):
        self.client = Client(name, "129.2.106.140")
        self.SEND = send
    
    def run(self):
        while True:
            if self.SEND:
                self.client.send("-60,20")
                self.SEND = False
            else:
                rec = self.client.listen()
                if rec != None:
                    print(rec)


c = ClientThread("Sam", True)
c.run()
