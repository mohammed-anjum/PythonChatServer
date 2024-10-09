import socket
import sys
import select

def client_program(client_name, host, port):

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    while True:

        potential_sockets = [sys.stdin, client_socket]

        readable, _, _ = select.select(potential_sockets, [], [])

        for s in readable:
            # if we are getting a message to the socket
            if s is client_socket:
                message = client_socket.recv(1024).decode()
                if not message:
                    print("Server disconnected")
                    return
                else:
                    print(message)
                    print(f"{client_name}: ", end="", flush=True)
            else:
                message = input(f"{client_name}: ")
                if message.lower() == "quit":
                    print("Client disconnected")
                    return

                client_socket.send(message.encode())

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 client.py <clientName> <host> <port>")
    else:
        client_name = sys.argv[1]
        host = sys.argv[2]
        port = sys.argv[3]
        client_program()