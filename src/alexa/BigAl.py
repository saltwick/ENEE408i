from flask import Flask, render_template
from flask_ask import Ask, statement, question
import threading
import socket
import sys
import errno
from queue import *

passedMessage = Queue()
app = Flask(__name__)
ask = Ask(app, '/')

class AlexaThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app

    def run(self):
        self.app.run(debug=False, host='127.0.0.1')   

    def halt():
	    valueToWrite= 0
	    ser.write(struct.pack('>B', valueToWrite))

    def right():
        valueToWrite= 2
        ser.write(struct.pack('>B', valueToWrite))

    def left():
        valueToWrite= 1
        ser.write(struct.pack('>B', valueToWrite))

    def forward():
        valueToWrite= 3
        ser.write(struct.pack('>B', valueToWrite))

    def backward():
        valueToWrite= 4
        ser.write(struct.pack('>B', valueToWrite))

    @ask.launch
    def launched():
        return question("Yo. I'm Big Al. If you need some kneecaps broken, I'm your man").reprompt(
            "Give me a job or let me watch the Yanks sweep the Sox")


    @ask.intent('AMAZON.FallbackIntent')
    def default():
        return question("Big Al don't know what you mean. Do you want me to break some kneecaps?").reprompt(
            "Give me a job or let me watch the Yanks sweep the Sox")


    @ask.intent('MoveIntent')
    def move(direction):
        msg = ""
        if direction == 'left':
            # left()
            # time.sleep(1.0)
            # halt()
            msg = "Big Al has protected his left side blind spot"
        elif direction == 'right':
            # right()
            # time.sleep(1.0)
            # halt()
            msg = "There's a ton of cocaine to the right of me. Big Al's moving in"
        elif direction == 'forward':
            # forward()
            # time.sleep(4.0)
            # halt()
            msg = "Big Al moving in for the kill"
        elif direction == 'backward':
            # backward()
            # time.sleep(2.0)
            # halt()
            msg = "Big Al don't back down from nobody. Let me take a swing at him"
        elif direction == 'halt':
            # halt()
            msg = "Big Al is staying right here"
        elif direction == "move":
            return question("In what direction, bozo?").reprompt("Tell me where to go or let me die in peace")	
        return question(msg).reprompt("Now what?")


    # @ask.intent('FollowIntent')
    # def followMe(command):

    #     return question("Big Al is on the prowl").reprompt(
    #         "How much longer until I take care of this guy for good?")

    @ask.intent('SleepIntent')
    def sleep():
        return statement("That'll be 500 big ones for today. Big Al out")


    @ask.intent('DistressIntent')
    def distress():
        
        passedMessage.put("distress: 2.25,3.14")
        
        return question("Distress signal sent").reprompt(
            "Move out. We got a job to do.")

        
class ClientThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):

        HEADER_LENGTH = 10

        IP = "192.168.43.193"
        PORT = 1234
        my_username = 'Frank' # Change to your team number

        # Create a socket
        # socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
        # socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to a given ip and port
        client_socket.connect((IP, PORT))

        # Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
        client_socket.setblocking(False)

        # Prepare username and header and send them
        # We need to encode username to bytes, then count number of bytes and prepare header of fixed size, that we encode to bytes as well
        username = my_username.encode('utf-8')
        username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(username_header + username)

        def send():
            while True:
                message = None
                if not passedMessage.empty():
                    message = passedMessage.get()
                # Wait for user to input a message
                # If message is not empty - send it
                
                if message:
                    # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
                    message = message.encode('utf-8')
                    message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                    client_socket.send(message_header + message)

        def receive():
            while True:

                try:
                    # Now we want to loop over received messages (there might be more than one) and print them
                    while True:

                        # Receive our "header" containing username length, it's size is defined and constant
                        username_header = client_socket.recv(HEADER_LENGTH)

                        # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
                        if not len(username_header):
                            print('Connection closed by the server')
                            sys.exit()

                        # Convert header to int value
                        username_length = int(username_header.decode('utf-8').strip())

                        # Receive and decode username
                        username = client_socket.recv(username_length).decode('utf-8')

                        # Now do the same for message (as we received username, we received whole message, there's no need to check if it has any length)
                        message_header = client_socket.recv(HEADER_LENGTH)
                        message_length = int(message_header.decode('utf-8').strip())
                        message = client_socket.recv(message_length).decode('utf-8')

                        # Print message
                        print(f'\n{username} > {message}')
                        #print(my_username + ' > ')

                except IOError as e:
                    # This is normal on non blocking connections - when there are no incoming data error is going to be raised
                    # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
                    # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
                    # If we got different error code - something happened
                    if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                        print('Reading error: {}'.format(str(e)))
                        sys.exit()

                    # We just did not receive anything
                    continue

                except Exception as e:
                    # Any other exception - something happened, exit
                    print('Reading error: '.format(str(e)))
                    sys.exit()


        t1 = threading.Thread(target=send, name='t1')
        t2 = threading.Thread(target=receive, name='t2')

        t1.start()
        t2.start()


client = ClientThread()
alexa = AlexaThread(app)

client.start()
alexa.start()

