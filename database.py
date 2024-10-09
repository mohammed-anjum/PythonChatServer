import sqlite3

def initialize_db():
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()

    # Create the messages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        delivered_to TEXT
    )
    ''')

    # Create the clients table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        client_id TEXT PRIMARY KEY,
        status TEXT NOT NULL,
        last_seen DATETIME
    )
    ''')

    conn.commit()
    conn.close()

##################################
##################################
##################################

def on_connect(client_id):
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()

    cursor.execute(
        '''
        insert into clients (client_id, status, last_seen)
        values(?, "ONLINE", CURRENT_TIMESTAMP)
        ''', (client_id,)
    )
    conn.commit()

    cursor.execute(
        '''
        select distinct id from messages 
            where delivered_to is null
                or delivered_to not like ?
        order by timestamp
        ''', (f'%{client_id}%',)
    )
    undelivered_message_ids = cursor.fetchall()
    conn.close()

    return [id[0] for id in undelivered_message_ids]


def get_message_from_message_id(message_id):
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()

    cursor.execute(
        '''
        select message from messages where id = ?
        ''', (message_id,)
    )
    message = cursor.fetchone()[0]
    conn.close()

    return message

#GOOD
def on_disconnect(client_id):
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()

    cursor.execute(
        '''
        update clients
        set status="OFFLINE", last_seen=CURRENT_TIMESTAMP
            where client_id=?
        ''', (client_id,)
    )
    conn.commit()
    conn.close()

#GOOD
#returns stored messages id
def store_message(client_id, message):
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()

    # Insert the message into the table
    cursor.execute(
        '''
        insert into messages (client_id, message, delivered_to)
        values (?, ?, ?)
        ''', (client_id, message, client_id)
    )

    # Get the id of the last inserted row
    message_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return message_id

#GOOD
def get_online_client_ids():
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()

    cursor.execute(
        '''
        select client_id from clients
            where status="ONLINE"
        '''
    )
    online_clients = cursor.fetchall()
    conn.close()

    return [client[0] for client in online_clients]

#GOOD
def set_everyone_offline():
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()

    cursor.execute(
        '''
        update clients
        set status = "OFFLINE", last_seen=CURRENT_TIMESTAMP
        '''
    )
    conn.commit()
    conn.close()

#GOOD
def set_delivered_to(client_id, message_id):
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()

    cursor.execute(
        '''
        update messages
        set delivered_to = coalesce(delivered_to || ', ', '') || ?
            where id = ?
        ''', (client_id, message_id)
    )
    conn.commit()
    conn.close()


# Call this function when the module is run directly
if __name__ == '__main__':
    initialize_db()