import socket
import select
import sys
import os

def main():
    # Check command-line arguments
    if len(sys.argv) != 3:
        print("Correct usage: script, IP address, port number")
        sys.exit()

    IP_address = sys.argv[1]
    Port = int(sys.argv[2])

    # Initialize the socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((IP_address, Port))

    # On Windows, `select` may not work properly with standard input (sys.stdin)
    # In this case, we use `msvcrt` to check for keyboard input
    use_msvcrt = os.name == 'nt'

    try:
        while True:
            sockets_list = [server]
            if not use_msvcrt:
                sockets_list.append(sys.stdin)  # Only add sys.stdin if not on Windows

            # Wait for input on server socket or stdin
            read_sockets, _, _ = select.select(sockets_list, [], [])

            for socks in read_sockets:
                if socks == server:
                    # Server has sent a message
                    message = socks.recv(2048)
                    if message:
                        print(message.decode())
                    else:
                        print("Connection closed by server.")
                        sys.exit()
                else:
                    # User has typed a message
                    if use_msvcrt:  # Windows-specific input handling
                        import msvcrt
                        if msvcrt.kbhit():
                            message = input()
                            if message:
                                server.send(message.encode())
                                print(f"<You> {message}")
                    else:  # Unix-like systems
                        message = sys.stdin.readline()
                        if message:
                            server.send(message.encode())
                            print(f"<You> {message}", end='')

    except KeyboardInterrupt:
        print("Disconnected from chat.")
    finally:
        server.close()

if __name__ == "__main__":
    main()
