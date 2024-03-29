from flask import Flask, render_template
from flask_ask import Ask, statement, question
import threading
import socket
import sys
import errno
import random
from queue import *

# Creating a queue to put a message in for the Distress Intent
passedMessage = Queue()

# app and ask must be defined globally or Alexa will not work
app = Flask(__name__)
ask = Ask(app, '/')

class AlexaThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app
        
    def run(self):
        self.app.run(debug=False, host='127.0.0.1')   

    # When the Big Al skill is launched Alexa will say this 
    @ask.launch
    def launched():
        return question("Yo. I'm Big Al. If you need some kneecaps broken, I'm your man").reprompt(
            "Give me a job or let me watch the Yanks sweep the Sox")

    # When Alexa doesn't understand what you said she'll say this
    @ask.intent('AMAZON.FallbackIntent')
    def default():
        return question("Big Al don't know what you mean. Do you want me to break some kneecaps?").reprompt(
            "Give me a job or let me watch the Yanks sweep the Sox")

    # Intent to exit the Big Al skill
    @ask.intent('SleepIntent')
    def sleep():
        return statement("That'll be 500 big ones for today. Big Al out")

    # Sends a distress signal through the client class below
    @ask.intent('DistressIntent')
    def distress():
        
        # Puts a message into the global queue to be sent my the client below
        passedMessage.put("distress: Tag 14")
        
        return question("Distress signal sent").reprompt(
            "Move out. We got a job to do.")

    # Determines whether Big Al is in the classroom or the hallway. Not fully implemented. Just a skeleton
    @ask.intent('LocationIntent')
    def location():
        return question("I am in the classroom").reprompt("Now that you know where I am, I suggest running away before someone gets hurt")

    # Randomly selects a joke from the list below and tells it
    @ask.intent('JokeIntent')
    def joke():
        jokes = [
            ["What's red and bad for your teeth?", "A brick."],
            ["If at first you don't succeed… then skydiving definitely isn't for you.", "Don't give up on me"],
            ["Where does the person with one leg work?", "IHOP"],
            ["My Grandfather has the heart of a lion and a lifetime ban from the Atlanta Zoo.", "Yeah, I come from a long line of romantics"],
            ["How did the dentist suddenly become a brain surgeon?", "A slip of the hand."],
            ["It turns out a major new study recently found that humans eat more bananas than monkeys.", "It’s true. I can’t remember the last time I ate a monkey."],
            ["I hate double standards. Burn a body at a crematorium, you’re being a respectful friend. Do it at home and you’re “destroying evidence.", "I'll be here all week"]
        ]

        value = random.randint(0,6)
        print(value)
        return question(jokes[value][0]).reprompt(jokes[value][1])


# This is almost the same client code as in 'client_multithreading.py' in the chat_room folder
# It is in here to test the distress signal
class ClientThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):

        HEADER_LENGTH = 10

        IP = "192.168.43.193"
        PORT = 1234
        my_username = 'Team 3' # Change to your team number

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

