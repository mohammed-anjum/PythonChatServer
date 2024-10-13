# The Code

## General (Non-Testing Mode):
To run the server normally:

```
python3 server.py
```
The server will display its host and port in the terminal via print statements. Use this information to run the clients:

To run the clients, run the following the code
```
python3 client.py client_name host port
```
Where the client_name is a simple identifier for the client. Multiple clients can be created to communicate with each other via the server

### SQLite
The system uses an SQLite database to track test results and metrics, logging all message exchanges between clients and the server. The database.py file contains the code for the table implementation and methods that update the database. All data is stored in server.db.
The SQLite database uses the host and port as unique Client IDs, therefore we are able to keep track of
* senders = `client_id`
* recivers = `delivered_to`
* and ultimately keep track of undelivered messages for the bonus question

**NOTE** In the testing mode, the test argument records counts of messages sent by clients and received by the server, instead of showing logs on the server side normally

## Test Setup and Execution:
### Server
Run the server with the test argument to record metrics:
```
python3 server.py test
```
This will allow for the server to keep track and print counts of messages sent and received

### Clients
Use the bash script `./load_test.sh` to start multiple clients. Adjust the loop in the script for the number of clients. To record metrics, run:
```
python3 client.py client_name host port test
```
Without the test argument, clients will run without recording metrics. the metrics are sent to the server
