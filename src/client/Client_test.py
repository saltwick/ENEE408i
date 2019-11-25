from Client_class import Client
import threading

class ClientThread():
    def __init__(self, name, send):
        self.client = Client(name)
        self.SEND = send
    
    def run(self):
        while True:
            if self.SEND:
                self.client.send("hi")
                self.SEND = False
            else:
                rec = self.client.listen()
                if rec != None:
                    print(rec)



c = ClientThread("Sam", True)
c.run()