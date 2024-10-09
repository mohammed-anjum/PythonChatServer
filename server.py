import select
import socket
import sys
from xml.sax.handler import feature_namespace_prefixes

from database import *
initialize_db()

# Create server sockets
#AF_INET: IPv4 address family (for standard IP addresses)
#SOCK_STREAM: TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setblocking(False)
server_socket.bind((socket.gethostname(), 42424))
server_socket.listen(5)  # Start listening for connections
print(f"Listening on public interface: {socket.gethostname()}:{42424}")

local_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
local_server_socket.setblocking(False)
#ip =  'localhost' = 127.0.0.1
local_server_socket.bind(('localhost', 12345))
local_server_socket.listen(5)  # Start listening for connections
print(f"Listening on localhost: 127.0.0.1:12345")

online_sockets= {}
inputs = [server_socket, local_server_socket]

while True:
    try:
        # Monitor sockets for readability
        readable, _, _ = select.select(inputs, [], [])

        for s in readable:

            if s is server_socket or s is local_server_socket:

                #connect via TCP
                client_socket, address = s.accept()
                client_socket.setblocking(False)

                #make unique id
                client_id = f"{address[0]}:{address[1]}"

                # announce it
                print(f"Client {client_id} connected")

                #store socket for communication
                online_sockets[client_id] = client_socket

                #get undelivered_message_ids on_connect and store online status
                undelivered_message_info = on_connect(client_id)

                #send the ones that didnt go through
                for msg_id, sender_client_id, message in undelivered_message_info:
                    #send all und msg to the current client id
                    online_sockets[client_id].send((f"{sender_client_id}: {message}").encode())
                    #mark this as delivered for current client
                    set_delivered_to(msg_id, client_id)

                #i am not sure if we need this tbh
                inputs.append(client_socket)

            else:
                try:
                    #receive a message if any
                    message = s.recv(1024).decode()
                    #keep client id handy
                    client_id = f"{s.getpeername()[0]}:{s.getpeername()[1]}"

                    if message:
                        print(f"Received message from client: {client_id} - {message}")

                        #store this message and get its id
                        message_id = store_message(client_id, message)

                        #now to send it to everyone online

                        #all online people
                        online_client_ids = get_online_client_ids()
                        for client_id in online_client_ids:
                            #get their sockets and send it by getting the message from id
                            online_sockets[client_id].send(message.encode())
                            #mark the people that got it as delivered
                            set_delivered_to(client_id, message_id)

                    else:
                        # Client disconnected
                        #remove sockets
                        del online_sockets[client_id]
                        #set to offline
                        on_disconnect(client_id)
                        print(f"Client disconnected")

                        #not sure if we even need this
                        inputs.remove(s)

                        #close select statement
                        s.close()

                except Exception as e:
                    print(f"Error receiving data from client: {e}")
                    set_everyone_offline()
                    inputs.remove(s)
                    s.close()

    except KeyboardInterrupt:
        print("I guess I'll just die")
        set_everyone_offline()
        server_socket.close()
        local_server_socket.close()
        sys.exit(0)
    except Exception as e:
        print("SOMETHING IS BAD")
        print(e)




"""
fixes required
1. need to make sure that the message i sent isnt sent back to me
2. need to show who sent the message
3. need to update the on_connect method so it gets the message_ids, messages, and the senders
4. should update the other message method to do the same
"""