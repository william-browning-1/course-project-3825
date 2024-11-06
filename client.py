import socket
import threading
import sys 

if len(sys.argv) != 3: 
	print ("Correct usage: script, IP address, port number")
	exit() 

# Specify  IP address and port number of the chat server
HOST = str(sys.argv[1]) 
PORT = int(sys.argv[2]) 


# Function to receive messages from the server
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(message)
        except:
            print("Connection closed by the server.")
            break

# Function to send messages to other clients via the server
def send_messages(client_socket):
    while True:
        message = input()
        client_socket.send(message.encode('utf-8'))
        if message == ".exit":
            break

# Function to start the client and connect to the server
def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    # Start threads for receiving and sending messages
    threading.Thread(target=receive_messages, args=(client_socket,)).start()
    send_messages(client_socket)
    client_socket.close()

start_client()
