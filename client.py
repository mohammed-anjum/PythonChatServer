import socket
import sys
import select

def client_program(client_name, host, port):

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    # #send the name in a unique way so server can record it
    # name_const = "نام"
    # client_socket.send(f"{name_const} - {client_name}".encode())

    while True:
        try:
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
                        print(message.strip())
                else:
                    # sys.stdout.flush()
                    message = input(f"{client_name}: ")  # Get user input without preprinted prompt in input()
                    if message.lower() == "quit":
                        print("Client disconnected")
                        return

                    client_socket.send(message.encode())

        except KeyboardInterrupt:
            # print("I guess I'll just die")
            client_socket.close()
            sys.exit(0)

        except Exception as e:
            print("SOMETHING IS BAD")
            print(e)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 client.py <clientName> <host> <port>")
    else:
        client_name = sys.argv[1]
        host = sys.argv[2]
        port = int(sys.argv[3])
        client_program(client_name, host, port)