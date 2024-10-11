import select
import socket
import sys

from database import *

def server_program(test):
    initialize_db()

    if test:
        print("Server is in test mode")

    handshake_str = "_*_"
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
    messages_to_send = {}
    online_sockets = {}

    while True:
        try:
            readable, writable, _ = select.select(the_readable, the_writable, [])

            for s in readable:
                if s is server_socket or s is local_server_socket:
                    client_socket, address = s.accept()
                    client_socket.setblocking(False)

                    #default client id
                    client_port_host = f"{address[0]}:{address[1]}"
                    client_id = client_port_host

                    try:
                        handshake_message = client_socket.recv(1024).decode().strip()
                        if handshake_str in handshake_message:
                            client_name = handshake_message.split("-")[-1].strip()
                            if client_name:
                                client_id = client_name
                            print(f"Handshake completed with client: {client_id}")
                        else:
                            raise ValueError("Invalid handshake message")
                    except Exception as e:
                        print(f"Error during handshake with {client_port_host}: {e}")
                        client_socket.close()
                        continue
                    finally:
                        # Set back to non-blocking mode after the handshake
                        client_socket.setblocking(False)


                    if test:
                        print(f"Client {client_id} connected and is testing me")
                    else:
                        print(f"Client {client_id} connected")

                    the_readable.append(client_socket)
                    online_sockets[client_socket] = client_id
                    messages_to_send[client_socket] = []

                    undelivered_message_info = get_undelivered_messages(client_id)

                    if test:
                        undelivered_message_info = undelivered_message_info[-20:]

                    for msg_id, sender_client_id, message in undelivered_message_info:
                        messages_to_send[client_socket].append([msg_id, sender_client_id, message])

                    if client_socket not in the_writable:
                        the_writable.append(client_socket)

                else:
                    try:
                        message = s.recv(1024).decode()
                        sender_client_id = online_sockets[s]

                        if message:
                            if test:
                                count_received_messages += 1
                                if "*_*" in message:
                                    thisMessage = message.split("*_*")[0]
                                    print(thisMessage)
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
                            if s in the_readable:
                                the_readable.remove(s)
                            if s in the_writable:
                                the_writable.remove(s)
                            online_sockets.pop(s, None)
                            messages_to_send.pop(s, None)
                            s.close()

                    except Exception as e:
                        print(f"Error receiving data from client: {e}")
                        if s in the_readable:
                            the_readable.remove(s)
                        if s in the_writable:
                            the_writable.remove(s)
                        online_sockets.pop(s, None)
                        messages_to_send.pop(s, None)
                        s.close()

            if test and len(online_sockets) == 0:
                print(f"In test mode, 0 clients connected, and i received {count_received_messages} messages")

            # Handle sending messages to writable clients
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
                    if s in the_writable:
                        the_writable.remove(s)
                    online_sockets.pop(s, None)
                    messages_to_send.pop(s, None)
                    s.close()

        except KeyboardInterrupt:
            print("I guess I'll just die")
            online_sockets = {}
            server_socket.close()
            local_server_socket.close()
            sys.exit(0)
        except Exception as e:
            print("SOMETHING IS BAD")
            print(e)

if __name__ == "__main__":
    test = sys.argv[1] if len(sys.argv) > 1 else None
    server_program(test)