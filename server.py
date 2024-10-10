import select
import socket
import sys
from database import *

# Initialize database
initialize_db()

# Create server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setblocking(False)
server_socket.bind((socket.gethostname(), 42424))
server_socket.listen(5)
print(f"Server listening on {socket.gethostname()}:42424")

local_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
local_server_socket.setblocking(False)
local_server_socket.bind(('localhost', 12345))
local_server_socket.listen(5)
print(f"Server listening on localhost:12345")

# Store active sockets
inputs = [server_socket, local_server_socket]
outputs = []
online_sockets = {}
message_queues = {}

# Main loop
while True:
    # Monitor sockets for readability and writability
    readable, writable, exceptional = select.select(inputs, outputs, inputs)

    # Handle readable sockets (incoming messages)
    for s in readable:
        if s is server_socket or local_server_socket in readable:
            # New client connection
            client_socket, address = s.accept()
            client_socket.setblocking(False)
            client_id = f"{address[0]}:{address[1]}"
            print(f"Client {client_id} connected")

            # Add new client to tracking
            online_sockets[client_id] = client_socket
            message_queues[client_socket] = []
            inputs.append(client_socket)

            # Queue undelivered messages for the client
            undelivered_messages = on_connect(client_id)
            for msg_id, sender_client_id, message in undelivered_messages:
                message_queues[client_socket].append(f"{sender_client_id}: {message}".encode())
                set_delivered_to(msg_id, client_id)

            # Ensure the client is in the outputs list to send messages
            if client_socket not in outputs:
                outputs.append(client_socket)

        else:
            try:
                # Receive message from client
                message = s.recv(1024).decode()
                client_id = f"{s.getpeername()[0]}:{s.getpeername()[1]}"

                if message:
                    print(f"Received message from {client_id}: {message}")
                    message_id = store_message(client_id, message)

                    # Queue the message to be sent to all online clients (except the sender)
                    for online_id, online_socket in online_sockets.items():
                        if online_id != client_id:
                            message_queues[online_socket].append(f"{client_id}: {message}".encode())
                            set_delivered_to(message_id, online_id)

                            # Ensure the recipient socket is in the outputs list
                            if online_socket not in outputs:
                                outputs.append(online_socket)
                else:
                    # Client disconnected
                    print(f"Client {client_id} disconnected")
                    inputs.remove(s)
                    if s in outputs:
                        outputs.remove(s)
                    s.close()
                    del online_sockets[client_id]
                    on_disconnect(client_id)

            except Exception as e:
                print(f"Error receiving data from client: {e}")
                inputs.remove(s)
                if s in outputs:
                    outputs.remove(s)
                s.close()

    # Handle writable sockets (sending queued messages)
    for s in writable:
        try:
            if message_queues[s]:
                next_msg = message_queues[s].pop(0)
                s.send(next_msg)

            if not message_queues[s]:
                # No more messages to send, stop monitoring for writability
                outputs.remove(s)

        except Exception as e:
            print(f"Error sending message to client: {e}")
            outputs.remove(s)
            s.close()

    # Handle exceptional conditions (e.g., errors)
    for s in exceptional:
        print(f"Handling exception for {s.getpeername()}")
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()