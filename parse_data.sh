#!/bin/bash

DATA_PY="data.py"
data_py=${1:=$DATA_PY}

# Run the Python script and capture its output as JSON
json_output=$(python3 /home/vlad/bin/parse_data.py "${data_py}")

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "jq is not installed. Please install jq."
    exit 1
fi

# Parse the JSON output to get the types
types=$(echo "$json_output" | jq -r 'keys[]')

# Loop through each type
for type in $types; do
    echo "$type:"
    
    # Get the entities for the current type
    entities=$(echo "$json_output" | jq -r --arg type "$type" '.[$type] | keys[]')
    
    # Loop through each entity and get the chan_no
    for entity in $entities; do
        chan_no=$(echo "$json_output" | jq -r --arg type "$type" --arg entity "$entity" '.[$type][$entity]')
        echo "  $entity: chan_no=$chan_no"
    done
done
