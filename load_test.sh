#!/bin/bash

# Kill all child processes when the script exits
trap "kill 0" EXIT

# Launch 200 clients, with a delay between each
for thing in {1..200}
do
    python3 client.py "client_$thing" localhost 12345 test &
done

# Wait for all background processes to finish
wait

echo "All clients have finished."