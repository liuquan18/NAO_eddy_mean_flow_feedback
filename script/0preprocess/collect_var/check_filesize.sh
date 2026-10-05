#!/bin/bash
directory=$1
threshold_size=$2

# Find files smaller than the threshold size and print their names
find "$directory" -type f -size -${threshold_size}c -print