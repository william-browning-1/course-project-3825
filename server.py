import socket
import threading
import random
import ssl
import sys

# Check arguments
if len(sys.argv) != 3: 
    print("Correct usage: script, IP address, port number")
    exit()

HOST = str(sys.argv[1])
PORT = int(sys.argv[2])

clients = {}
groupchats = {}

def broadcast_client_list():
    connected_clients = ", ".join(clients.keys())
    for client_socket in clients.values():
        try:
            client_socket.send(f"Connected clients: {connected_clients}".encode('utf-8'))
        except:
            pass

def handle_client(client_socket, client_id):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break  # In case of an empty message, client may have disconnected unexpectedly

            if message == ".exit":
                # Handle client disconnection
                print(f"[{client_id}] has disconnected.")
                client_socket.send("You have been disconnected.".encode('utf-8'))
                client_socket.close()
                del clients[client_id]
                remove_from_groupchats(client_id)
                broadcast_client_list()
                break

            elif message.startswith(".dm"):
                # Direct message: .dm <client_id> <message>
                parts = message.split(" ", 2)
                if len(parts) < 3:
                    client_socket.send("Usage: .dm <client_id> <message>".encode('utf-8'))
                else:
                    target_id = parts[1]
                    direct_message = parts[2]
                    if target_id in clients:
                        clients[target_id].send(f"Direct message from {client_id}: {direct_message}".encode('utf-8'))
                    else:
                        client_socket.send(f"Client {target_id} not found.".encode('utf-8'))

            elif message.startswith(".msg"):
                # Broadcast message: .msg <message>
                broadcast_message(message[5:], client_id)

            elif message.startswith(".group"):
                # Command to join or leave a group chat
                parts = message.split(" ", 2)
                if len(parts) < 3:
                    client_socket.send("Usage: .group <join/leave> <group_name>".encode('utf-8'))
                else:
                    action, group_name = parts[1], parts[2]
                    if action == "join":
                        join_groupchat(client_id, group_name)
                    elif action == "leave":
                        leave_groupchat(client_id, group_name)
                    else:
                        client_socket.send("Invalid group action. Use 'join' or 'leave'.".encode('utf-8'))

            elif message.startswith(".gm"):
                # Group chat message: .gm <groupchat_name> <message>
                parts = message.split(" ", 2)
                if len(parts) < 3:
                    client_socket.send("Usage: .gm <groupchat_name> <message>".encode('utf-8'))
                else:
                    target_id = parts[1]
                    direct_message = parts[2]

                    groupchat = groupchats[target_id]

                    if client_id not in groupchats[target_id]: # Check if client is member of the groupchat
                        client_socket.send(f"You are not in this groupchat".encode('utf-8'))
                    else:
                        for client in groupchat:
                            # Forward the message to the clients in the groupchat
                            clients[client].send(f"[{client_id}] in {target_id} says: {msg}".encode('utf-8'))
                        # Send a receipt confirmation back to the sender
                        client_socket.send(f"Message delivered to [{target_id}]".encode('utf-8'))
                    



            else:
                # Handle unrecognized message types
                client_socket.send("Unknown command. Type .exit to disconnect.".encode('utf-8'))

        except Exception as e:
            print(f"Error handling client {client_id}: {e}")
            client_socket.close()
            del clients[client_id]
            remove_from_groupchats(client_id)
            broadcast_client_list()
            break

def broadcast_message(message, sender_id):
    # Send the message to all clients except the sender
    for client_id, client_socket in clients.items():
        if client_id != sender_id:
            try:
                client_socket.send(f"Broadcast from {sender_id}: {message}".encode('utf-8'))
            except:
                continue

def join_groupchat(client_id, group_name):
    if group_name not in groupchats:
        groupchats[group_name] = []
    if client_id not in groupchats[group_name]:
        groupchats[group_name].append(client_id)
        for client_socket in clients.values():
            client_socket.send(f"{client_id} has joined the group chat '{group_name}'.".encode('utf-8'))
    else:
        clients[client_id].send(f"You are already in the group chat '{group_name}'.".encode('utf-8'))

def leave_groupchat(client_id, group_name):
    if group_name in groupchats and client_id in groupchats[group_name]:
        groupchats[group_name].remove(client_id)
        for client_socket in clients.values():
            client_socket.send(f"{client_id} has left the group chat '{group_name}'.".encode('utf-8'))
    else:
        clients[client_id].send(f"You are not in the group chat '{group_name}'.".encode('utf-8'))

def remove_from_groupchats(client_id):
    for group_name, members in groupchats.items():
        if client_id in members:
            members.remove(client_id)
            for client_socket in clients.values():
                client_socket.send(f"{client_id} has left the group chat '{group_name}'.".encode('utf-8'))

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    # Wrap the socket with SSL
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")
    print("Server is running with SSL...")

    while True:
        client_socket, addr = server.accept()
        secure_socket = context.wrap_socket(client_socket, server_side=True)
        client_id = f"Client{random.randint(1000, 9999)}"
        clients[client_id] = secure_socket
        print(f"{client_id} connected from {addr}")
        broadcast_client_list()
        threading.Thread(target=handle_client, args=(secure_socket, client_id)).start()

start_server()
