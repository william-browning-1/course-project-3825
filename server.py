import socket
import threading
import random
import sys

# checks whether sufficient arguments have been provided 
if len(sys.argv) != 3: 
	print ("Correct usage: script, IP address, port number")
	exit() 

# Specify IP address and port # for server from commandline arguments
HOST = str(sys.argv[1]) 
PORT = int(sys.argv[2]) 

clients = {}  # Dictionary to store clients with their unique identifiers

# Function to handle each client connection
def handle_client(client_socket, client_id):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message == ".exit":
                print(f"[{client_id}] has disconnected.")
                client_socket.send("You have been disconnected.".encode('utf-8'))
                client_socket.close()
                del clients[client_id]
                break
            else:
                # Assume the message format: "client_id: message"
                target_id, msg = message.split(":", 1)
                if target_id in clients:
                    clients[target_id].send(f"[{client_id}] says: {msg}".encode('utf-8'))
                else:
                    client_socket.send("Client not found.".encode('utf-8'))
        except:
            client_socket.close()
            break

# Function to start the server and accept connections
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print("Server is running...")

    while True:
        client_socket, addr = server.accept()
        # Generate a unique identifier for the client
        client_id = f"Client{random.randint(1000, 9999)}"
        clients[client_id] = client_socket
        print(f"{client_id} connected from {addr}")
        
        # Send the list of connected clients to the new client
        connected_clients = ", ".join(clients.keys())
        client_socket.send(f"Connected clients: {connected_clients}".encode('utf-8'))

        # Start a thread to handle the client's messages
        threading.Thread(target=handle_client, args=(client_socket, client_id)).start()

start_server()
