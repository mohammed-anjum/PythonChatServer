#!/bin/bash

# magic that will kill our children when the script exits
trap "kill 0" EXIT

for thing in {1..200}
do
    python3 client.py "client_$i" localhost 11111 &
done

wait # waits for detached terminals to quit
# Press ctrl-c to kill this, which will also kill the
# detached terminals

echo done

