import ast
import json
import sys

data_py = sys.argv[1]

# Load the data from the data.py file
with open(data_py, 'r') as f:
    data = f.read()

# Parse the data.py file to extract the SM_MAP dictionary
parsed = ast.parse(data)
data_dict = None

# Search for the SM_MAP dictionary in the parsed data
for node in ast.walk(parsed):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "SM_MAP":
                data_dict = ast.literal_eval(node.value)

# If SM_MAP is found, extract its types, entities, and chan_no
if data_dict:
    result = {}
    for type_name, entities in data_dict.items():
        result[type_name] = {}
        for entity_name, entity_info in entities.items():
            chan_no = entity_info.get("chan_no", "N/A")
            result[type_name][entity_name] = chan_no

    # Output the result as JSON to easily parse in Bash
    print(json.dumps(result))
else:
    print(json.dumps({}))

