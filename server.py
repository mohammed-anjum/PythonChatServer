import select
import socket
import sys

from database import *

#test arg for metrics
def server_program(test):
    initialize_db()

    if test:
        print("\n\nServer is in test mode")

    #for testing
    count_received_messages = 0

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setblocking(False)
    server_socket.bind((socket.gethostname(), 42424))
    server_socket.listen(5)
    print(f"Listening on public interface: {socket.gethostname()}:{42424}")

    local_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local_server_socket.setblocking(False)
    local_server_socket.bind(('localhost', 12345))
    local_server_socket.listen(5)
    print(f"Listening on localhost: 127.0.0.1:12345")

    the_readable = [server_socket, local_server_socket]
    the_writable = []

    #a dict to keep track messages to send as a queue
    messages_to_send = {}
    # a dict to keep track of STATE or online clients
    online_sockets = {}

    #helper method to avoid repetition, for closing sockets
    def close_socket(s):
        if s in the_readable:
            the_readable.remove(s)
        if s in the_writable:
            the_writable.remove(s)
        online_sockets.pop(s, None)
        messages_to_send.pop(s, None)
        s.close()

    while True:
        try:
            readable, writable, _ = select.select(the_readable, the_writable, [])

            for s in readable:
                if s is server_socket or s is local_server_socket:
                    client_socket, address = s.accept()
                    client_socket.setblocking(False)

                    client_id = f"{address[0]}:{address[1]}"
                    if test:
                        print(f"\nClient {client_id} connected and is testing me")
                    else:
                        print(f"Client {client_id} connected")

                    the_readable.append(client_socket)
                    online_sockets[client_socket] = client_id
                    messages_to_send[client_socket] = []

                    undelivered_message_info = on_connect(client_id)

                    if test:
                        undelivered_message_info = undelivered_message_info[-20:]

                    #queing messages to be sent
                    for msg_id, sender_client_id, message in undelivered_message_info:
                        messages_to_send[client_socket].append([msg_id, sender_client_id, message])

                    #only add to writable if message is there to send
                    if messages_to_send[client_socket]:
                        if client_socket not in the_writable:
                            the_writable.append(client_socket)

                else:
                    try:
                        message = s.recv(1024).decode()
                        sender_client_id = online_sockets[s]

                        if message:
                            if test:
                                count_received_messages += 1
                                # a unique string to show the final message by client to show number of sent messages
                                if "*_*" in message:
                                    finalMessage = message.split("*_*")[0]
                                    print(finalMessage)
                            else:
                                print(f"Received message from client: {sender_client_id} - {message}")

                            msg_id = store_message(sender_client_id, message)

                            for client_socket, online_client_id in online_sockets.items():
                                if online_client_id != sender_client_id:
                                    if client_socket not in messages_to_send:
                                        messages_to_send[client_socket] = []
                                    messages_to_send[client_socket].append([msg_id, sender_client_id, message])

                                    if client_socket not in the_writable:
                                        the_writable.append(client_socket)

                        else:
                            print(f"{sender_client_id} disconnected")
                            close_socket(s)

                    except Exception as e:
                        print(f"Error receiving data from client: {e}")
                        print(f"I received {count_received_messages} messages so far")
                        close_socket(s)

            # if no more clients in testing then show all messages received
            if test and len(online_sockets) == 0:
                print(f"\nIn test mode, 0 clients connected, TEST END and i received {count_received_messages} messages")

            for s in writable:
                try:
                    receiver_client_id = online_sockets[s]

                    if messages_to_send.get(s):
                        oldest_msg_info = messages_to_send[s].pop(0)
                        s.send(f"{oldest_msg_info[1]}: {oldest_msg_info[2]}".encode())

                        set_delivered_to(oldest_msg_info[0], receiver_client_id)

                    if not messages_to_send.get(s):
                        the_writable.remove(s)

                except Exception as e:
                    print(f"Error sending data to client: {e}")
                    print(f"I received {count_received_messages} messages so far")
                    close_socket(s)

        except KeyboardInterrupt:
            print("I guess I'll just die")
            server_socket.close()
            local_server_socket.close()
            sys.exit(0)

        except Exception as e:
            print("SOMETHING IS BAD")
            print(f"I received {count_received_messages} messages so far")
            print(e)

if __name__ == "__main__":
    test = sys.argv[1] if len(sys.argv) > 1 else None
    server_program(test)