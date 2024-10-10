import select
import socket
import sys

from database import *
initialize_db()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setblocking(False)
server_socket.bind((socket.gethostname(), 42424))
server_socket.listen(5)
print(f"Listening on public interface: {socket.gethostname()}:{42424}")

local_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
local_server_socket.setblocking(False)
local_server_socket.bind(('localhost', 12345))
local_server_socket.listen(5)  # Start listening for connections
print(f"Listening on localhost: 127.0.0.1:12345")

#a dictionary to hold client_id = socket
online_sockets= {}
#this is what needs to be read
the_readables = [server_socket, local_server_socket]

while True:
    try:
        # Monitor sockets for readability
        readable, _, _ = select.select(the_readables, [], [])

        for s in readable:

            if s is server_socket or s is local_server_socket:

                #connect via TCP
                client_socket, address = s.accept()
                client_socket.setblocking(False)

                #make unique client id
                client_id = f"{address[0]}:{address[1]}"
                # announce it
                print(f"Client {client_id} connected")

                #store socket so you can write to it later
                online_sockets[client_id] = client_socket

                #on_connect
                #   update online status
                #   get undelivered_message_ids
                undelivered_message_info = on_connect(client_id)

                #send the ones that didnt go through
                for msg_id, sender_client_id, message in undelivered_message_info:
                    #send all und msg to the current client id
                    online_sockets[client_id].send((f"{sender_client_id}: {message}").encode())
                    #mark this as delivered for current client
                    set_delivered_to(msg_id, client_id)

                #append your readables to have the client socket
                the_readables.append(client_socket)

            else:
                try:
                    #receive a message if any
                    message = s.recv(1024).decode()
                    #keep client id handy
                    client_id = f"{s.getpeername()[0]}:{s.getpeername()[1]}"

                    if message:
                        print(f"Received message from client: {client_id} - {message}")

                        #store this message
                        #   mark it as delivered to sender
                        #   get its id
                        message_id = store_message(client_id, message)


                        #now send it to everyone online
                        #get all onliners
                        online_client_ids = get_online_client_ids()
                        for online_id in online_client_ids:
                            #get their sockets and send it by getting the message from id
                            if online_id != client_id:
                                online_sockets[online_id].send((f"{client_id}: {message}").encode())
                                #mark the people that got it as delivered
                                set_delivered_to(client_id, message_id)

                    # Client disconnected
                    else:
                        #remove offline socket
                        del online_sockets[client_id]
                        #set client to offline
                        on_disconnect(client_id)
                        print(f"Client disconnected")
                        #remove readable socket
                        the_readables.remove(s)
                        #close select statement
                        s.close()

                except Exception as e:
                    print(f"Error receiving data from client: {e}")
                    # set_everyone_offline() # i dont think this should be here
                    the_readables.remove(s)
                    s.close()

        #for s in writeable
            #try:
            #except Exception as e:

    except KeyboardInterrupt:
        print("I guess I'll just die")
        set_everyone_offline()
        server_socket.close()
        local_server_socket.close()
        sys.exit(0)
    except Exception as e:
        print("SOMETHING IS BAD")
        print(e)
