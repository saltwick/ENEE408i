#Original from https://pythonprogramming.net/client-chatroom-sockets-tutorial-python-3/
#Modified by Huy Do
import socket
import sys
import errno
import threading

class ChatClientClass:
    HEADER_LENGTH = 10
    PORT = 1234
    client_socket = None    

    def __create_header(self, strLen, headLen):
        result = "{}".format(strLen)
        resultLen = len(result)
        if resultLen < headLen:
            for x in range(headLen - resultLen) :
                result = result + " "
        return result
    
    def __init__(self, user, ip):
        self.IP = ip
        self.my_username = user
        # Create a socket
        # socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
        # socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets    
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to a given ip and port
        self.client_socket.connect((self.IP, self.PORT))

        # Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
        self.client_socket.setblocking(False)

        # Prepare username and header and send them
        # We need to encode username to bytes, then count number of bytes and prepare header of fixed size, that we encode to bytes as well
        username = self.my_username.encode('utf-8')        
        username_header = self.__create_header(len(username), self.HEADER_LENGTH).encode('utf-8')
        self.client_socket.sendall(username_header + username)
        #start thread for receiving message
        t1 = threading.Thread(target=self.__receive, name='t1')        
        t1.start()

    
    #sendValue will be a tuple
    def send(self, x, z):        
        message = "{} > distress: {},{}".format(self.my_username, x, z).encode('utf-8')            
        message_header = self.__create_header(len(message), self.HEADER_LENGTH).encode('utf-8')
        self.client_socket.sendall(message_header + message)        

    def __receive(self):
        while True:
            try:
                # Now we want to loop over received messages (there might be more than one) and print them
                while True:                    
                    # Receive our "header" containing username length, it's size is defined and constant
                    username_header = self.client_socket.recv(self.HEADER_LENGTH)

                    # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)                    
                    if not len(username_header):
                        print('Connection closed by the server')
                        sys.exit()                    
                    # Convert header to int value
                    username_length = int(username_header.decode('utf-8').strip())

                    # Receive and decode username
                    username = self.client_socket.recv(username_length).decode('utf-8')

                    # Now do the same for message (as we received username, we received whole message, there's no need to check if it has any length)
                    message_header = self.client_socket.recv(self.HEADER_LENGTH)
                    message_length = int(message_header.decode('utf-8').strip())
                    message = self.client_socket.recv(message_length).decode('utf-8')

                    # Print message
                    print('\n{} > {}'.format(username, message))                    

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
                
