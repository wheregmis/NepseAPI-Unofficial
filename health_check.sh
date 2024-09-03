#!/bin/bash

# Replace localhost and 8000 with the correct host and port
if curl -s http://localhost:8000 > /dev/null; then
  exit 0
else
  exit 1
fi
