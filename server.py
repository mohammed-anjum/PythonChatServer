import select
import socket
import sys
from database import *
initialize_db()

# Create server sockets
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

online_sockets= {}
inputs = [server_socket, local_server_socket]
outputs = []  # Keep track of sockets that have data to send
message_queues = {}  # Store messages to be sent for each client

while True:
    try:
        # Monitor sockets for readability and writability
        readable, writable, _ = select.select(inputs, outputs, inputs)

        for s in readable:
            if s is server_socket or s is local_server_socket:
                client_socket, address = s.accept()
                client_socket.setblocking(False)
                client_id = f"{address[0]}:{address[1]}"
                print(f"Client {client_id} connected")

                online_sockets[client_id] = client_socket
                message_queues[client_socket] = []  # Initialize the message queue

                # Retrieve and queue undelivered messages
                undelivered_message_info = on_connect(client_id)
                for msg_id, sender_client_id, message in undelivered_message_info:
                    message_queues[client_socket].append(f"{sender_client_id}: {message}".encode())
                    set_delivered_to(msg_id, client_id)

                inputs.append(client_socket)

            else:
                try:
                    message = s.recv(1024).decode()
                    client_id = f"{s.getpeername()[0]}:{s.getpeername()[1]}"

                    if message:
                        print(f"Received message from client: {client_id} - {message}")
                        message_id = store_message(client_id, message)

                        # Queue the message to send to all other clients
                        online_client_ids = get_online_client_ids()
                        for online_id in online_client_ids:
                            if online_id != client_id:
                                online_sockets[online_id].send((f"{client_id}: {message}").encode())
                                set_delivered_to(client_id, message_id)
                                if online_sockets[online_id] not in outputs:
                                    outputs.append(online_sockets[online_id])
                    else:
                        del online_sockets[client_id]
                        on_disconnect(client_id)
                        print(f"Client {client_id} disconnected")
                        inputs.remove(s)
                        s.close()

                except Exception as e:
                    print(f"Error receiving data from client: {e}")
                    inputs.remove(s)
                    s.close()

        # Handle writable sockets
        for s in writable:
            try:
                if message_queues[s]:
                    next_msg = message_queues[s].pop(0)
                    s.send(next_msg)

                if not message_queues[s]:
                    outputs.remove(s)  # Stop monitoring if no more messages

            except Exception as e:
                print(f"Error sending data to client: {e}")
                outputs.remove(s)
                s.close()

    except KeyboardInterrupt:
        print("Shutting down the server")
        set_everyone_offline()
        server_socket.close()
        local_server_socket.close()
        sys.exit(0)

    except Exception as e:
        print("SOMETHING IS BAD")
        print(e)