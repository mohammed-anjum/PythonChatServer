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

#this is where the server will read from
the_readable = [server_socket, local_server_socket]

#this is what the server will write to
the_writable = []
#a dictionary to hold socket = [messages]
messages_to_send = {}

#a dictionary to hold client_id = socket
online_sockets= {}

while True:
    try:
        # SELECT
        readable, writable, _ = select.select(the_readable, the_writable, [])

        for s in readable:
            #here we establish connections
            if s is server_socket or s is local_server_socket:

                #connect via TCP
                client_socket, address = s.accept()
                client_socket.setblocking(False)
                #make unique client id
                client_id = f"{address[0]}:{address[1]}"
                print(f"Client {client_id} connected")

                #HERE WE ARE KEEPING TRACK OF STATE
                #add the client so we can read from them in the else statement
                if client_socket not in the_readable:
                    the_readable.append(client_socket)
                #assosiate the socket with the id
                online_sockets[client_id] = client_socket

                #now we keep track of messages to send
                messages_to_send[client_socket] = []
                #get undelivered_message_ids
                undelivered_message_info = on_connect(client_id)
                # queue up messages here
                for msg_id, sender_client_id, message in undelivered_message_info:
                    messages_to_send[client_socket].append([msg_id, sender_client_id, message])

                # also add it in writables
                if client_socket not in the_writable:
                    the_writable.append(client_socket)








            #here we get data
            else:
                try:
                    #receive a message if any
                    message = s.recv(1024).decode()
                    #keep client id handy
                    sender_client_id = f"{s.getpeername()[0]}:{s.getpeername()[1]}"

                    if message:
                        print(f"Received message from client: {sender_client_id} - {message}")

                        #store this message
                        #   mark it as delivered to sender
                        #   get its id
                        msg_id = store_message(sender_client_id, message)


                        #queue up the message to send
                        for online_client_id in online_sockets:
                            #don't send it to the sender again
                            if online_client_id != sender_client_id:

                                #making sure its arrays
                                if online_sockets[online_client_id] not in messages_to_send:
                                    messages_to_send[online_sockets[online_client_id]] = []

                                messages_to_send[online_sockets[online_client_id]].append([msg_id, sender_client_id, message])

                                #if exception removes the socket from writables
                                if online_sockets[online_client_id] not in the_writable:
                                    the_writable.append(online_sockets[online_client_id])

                    # Client disconnected
                    else:
                        print(f"{sender_client_id} disconnected")
                        #remove socket from readable
                        the_readable.remove(s)
                        #remove socket from writable
                        if s in the_writable:
                            the_writable.remove(s)
                        #close socket
                        s.close()

                except Exception as e:
                    print(f"Error receiving data from client: {e}")
                    #since we cannot receive data we should remove em
                    the_writable.remove(s)
                    s.close()

        #now we write and mark as delivered in database
        for s in writable:
            try:

                receiver_client_id = f"{s.getpeername()[0]}:{s.getpeername()[1]}"

                #if we have messages
                if messages_to_send[s]:

                    #[[id, sender, message]]
                    oldest_msg_info = messages_to_send[s].pop(0)


                    s.send(f"{oldest_msg_info[1]}: {oldest_msg_info[2]}".encode())
                    set_delivered_to(oldest_msg_info[0], receiver_client_id)

            except Exception as e:
                print(f"Error sending data to client: {e}")
                # since we cannot send data we should remove em
                the_readable.remove(s)
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
