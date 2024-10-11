#!/bin/bash

# Kill all child processes when the script exits
trap "kill 0" EXIT

# Launch 200 clients, with a delay between each
for thing in {1..2}
do
    python3 client.py "client_$thing" localhost 12345 &
    sleep 0.5  # Delay of 0.1 seconds between launching each client
done

# Wait for all background processes to finish
wait

echo "All clients have finished."