import socket
import ssl
import threading
import sys

if len(sys.argv) != 3: 
    print("Correct usage: script, IP address, port number")
    exit()

HOST = str(sys.argv[1])
PORT = int(sys.argv[2])

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(message)
        except socket.error:
            pass  # No message, continue trying

def send_messages(client_socket):
    try:
        while True:
            message = input()  # Take input from the user
            if message:
                client_socket.send(message.encode('utf-8'))
                if message == ".exit":
                    break
    except KeyboardInterrupt:
        client_socket.send(".exit".encode('utf-8'))

def start_client():
    raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Wrap the socket with SSL
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations("server.crt")
    client_socket = context.wrap_socket(raw_socket, server_hostname=HOST)

    client_socket.connect((HOST, PORT))

    threading.Thread(target=receive_messages, args=(client_socket,)).start()
    send_messages(client_socket)
    client_socket.close()

start_client()
