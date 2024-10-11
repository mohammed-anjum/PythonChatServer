import random
import socket
import string
import sys
import select
import time


def print_server_message(message, current_input):
    sys.stdout.write('\r')  # move cursor all the way back
    sys.stdout.write('\033[K')  # Clear the current line
    if not message.endswith('\n'):
        message += '\n'
    print(message.strip())  # print server's message
    sys.stdout.write(f"{current_input}")  # reprint what I was typing
    sys.stdout.flush()  # Flush to make sure it shows up in the terminal immediately


def send_automated_message(client_socket):
    time.sleep(random.uniform(0.5, 1.5))  # random interval
    random_word = ''.join(random.choices(string.ascii_letters, k=10))  # random message
    client_socket.send(random_word.encode())


def client_program(client_name, host, port, test):

    current_input = ""

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    while True:
        try:
            if not test:
                # Non-automated mode (waiting for user input and server messages)
                potential_sockets = [sys.stdin, client_socket]
                readable, _, _ = select.select(potential_sockets, [], [])

                for s in readable:
                    if s is client_socket:
                        message = client_socket.recv(1024).decode()
                        if not message:
                            print("Server disconnected")
                            return
                        else:
                            print_server_message(message, current_input)
                    else:
                        current_input = input(f"{client_name}: ")  # Get user input
                        if current_input.lower() == "quit":
                            print("Client disconnected")
                            return
                        client_socket.send(current_input.encode())

            #testing phase
            else:
                potential_sockets = [client_socket]
                readable, _, _ = select.select(potential_sockets, [], [], 0)  # non-blocking select

                if client_socket in readable:
                    message = client_socket.recv(1024).decode()
                    if not message:
                        print("Server disconnected")
                        return
                    else:
                        print_server_message(message, current_input)
                #Send automated messages at random intervals
                send_automated_message(client_socket)

        except KeyboardInterrupt:
            print("I guess I'll just die")
            client_socket.close()
            sys.exit(0)

        except Exception as e:
            print("SOMETHING IS BAD")
            print(e)
            client_socket.close()
            return


if __name__ == "__main__":
    if len(sys.argv) < 4:  # Should be 4 or more, not less than 4
        print("Usage: python3 client.py <clientName> <host> <port> [test]")
    else:
        client_name = sys.argv[1]
        host = sys.argv[2]
        port = int(sys.argv[3])
        test = sys.argv[4] if len(sys.argv) > 4 else None

        # Call the function with or without the test argument
        client_program(client_name, host, port, test)