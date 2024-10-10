1. a name sender
2. update client table to record name
3. update db to have a method to retrieve name
4. check with gpt if it is better in big o to return multiple things rather just one
5. add the name string to the last message received from server
6. scripts to ceate multiple clients
7. box plot to show the lines etc
last. that name interweave issue


### New List
1. heavily comment the code - DONE
2. see what can be compressed into methods
   1. i think one method to take care of all undelivered
3. see how sockets can be saved 
   1. i guess my online_sockets need to be writable
4. clean up code accordingly
5. update the clients table to have names


1. Check for graceful quits and quit messages
   1. Check on client side
   2. Check on server side
2. for the testing
   1. create a method t make random string
   2. create a method to sleep for somewhere in between 0.5 to 1.5 seconds
   3. then make method send the message
   4. run for 5 minutes
   5. client should count successful sends
   6. server should count successful receives
