import json
import sys

# Load the dictionary correlated to picongpu_and ontology 
picongpu_ontology_dictionary_path = r"P:\afshari\Projects\HZDR_Project\ontology_laser-plasma\ontology_git\picongpu_ontology_dictionary.json"
picongpu_params_path = r"P:\afshari\Projects\HZDR_Project\ontology_laser-plasma\ontology_git\pypicongpu.json"
ontology_params_path = r"P:\afshari\Projects\HZDR_Project\ontology_laser-plasma\ontology_git\laser-plasma_ontology.jsonld"

# Load the dictionary correlated to PIConGPU and ontology
with open(picongpu_ontology_dictionary_path) as dict_file:
    correlation_dict = json.load(dict_file)

# Load the PIConGPU JSON file
with open(picongpu_params_path) as picongpu_file:
    picongpu_params = json.load(picongpu_file)

# Load the JSON-LD file from the ontology
with open(ontology_params_path, encoding="utf-8") as ontology_file:  
    ontology_data = json.load(ontology_file)

# Handle the case where ontology_data is a list
if isinstance(ontology_data, list):
    ontology_graph = ontology_data
else:
    ontology_graph = ontology_data.get("@graph", [])

# Create a dictionary for easy access to ontology entries by parameter name
ontology_params = {entry["@id"].split('#')[-1]: entry for entry in ontology_graph}

# Helper function to get the parameter name from the ontology @id
# def get_parameter_name_from_id(ontology_id):
#     return ontology_id.split('#')[-1]

# Helper function to get the type from the ontology entry
def get_ontology_type(ontology_entry):
    try:
        range_entries = ontology_entry.get('http://www.w3.org/2000/01/rdf-schema#range', [])
        for entry in range_entries:
            ontology_type_uri = entry.get('@id')
            if ontology_type_uri:
                datatype_prefix = 'http://www.w3.org/2001/XMLSchema#'
                if ontology_type_uri.startswith(datatype_prefix):
                    return ontology_type_uri[len(datatype_prefix):]  # Extract datatype name
        return None
    except (KeyError, IndexError):
        return None


# Function to recursively handle nested dictionary structure in correlation_dict
def process_correlation_dict(correlation_dict, prefix=""):
    results = []
    for picongpu_param, ontology_param in correlation_dict.items():
        if isinstance(ontology_param, dict):
            nested_results = process_correlation_dict(ontology_param, prefix + picongpu_param + ".")
            results.extend(nested_results)
        elif isinstance(ontology_param, list):
            for i, item in enumerate(ontology_param):
                if isinstance(item, dict):
                    nested_results = process_correlation_dict(item, f"{prefix}{picongpu_param}[{i}].")
                    results.extend(nested_results)
                else:
                    full_picongpu_param = f"{prefix}{picongpu_param}[{i}]"
                    results.append((full_picongpu_param, item))
        else:
            full_picongpu_param = prefix + picongpu_param
            results.append((full_picongpu_param, ontology_param))
    return results

# Flatten the correlation dictionary
flat_correlation_list = process_correlation_dict(correlation_dict)

# The section `# Define parameters that require special handling` is creating a dictionary named
# `params_requiring_special_handling` that contains specific instructions for handling a particular
# parameter during the data processing.
# Define parameters that require special handling
params_requiring_special_handling = {
    "laser.polarization_direction[2].component": {
        "ontology_param": "laser_polarization_direction_z",
        "value_map": {0: "false", 1: "true"}
    }
}


# Helper function to print messages in color
def print_colored(message, color):
    colors = {
        "red": "\033[91m",
        "orange": "\033[93m",
        "blue": "\033[94m",
        "yellow": "\033[93m",
        "magenta": "\033[95m",
        "green": "\033[92m",
        "white": "\033[97m",
        "reset": "\033[0m"
    }
    print(f"{colors[color]}{message}{colors['reset']}")

# Helper function to map ontology types to Python types
def map_ontology_type_to_python(ontology_type):
    ontology_to_python_type = {
        'double': float,
        'float': float,
        'int': int,
        'integer': int,
        'boolean': bool,
        'string': str
    }
    return ontology_to_python_type.get(ontology_type, None)


def get_nested_value(dic, keys):
    for key in keys:
        if isinstance(dic, list):
            try:
                key = int(key)
            except ValueError:
                print_colored(f"ValueError: key '{key}' is not an integer and cannot be used to index a list.", "red")
                return None
            if key < 0 or key >= len(dic):
                print_colored(f"IndexError: key '{key}' is out of bounds for the list. List length: {len(dic)}", "yellow")
                return None
            dic = dic[key]
        else:
            if '[' in key and ']' in key:
                key, index = key.rstrip(']').split('[')
                if key not in dic:
                    print_colored(f"KeyError: key '{key}' not found in the dictionary. Current dictionary: {dic}", "orange")
                    return None
                dic = dic[key]
                try:
                    index = int(index)
                except ValueError:
                    print_colored(f"ValueError: index '{index}' is not an integer.", "red")
                    return None
                if index < 0 or index >= len(dic):
                    print_colored(f"IndexError: index '{index}' is out of bounds for the list. List length: {len(dic)}", "yellow")
                    return None
                dic = dic[index]
            else:
                if key not in dic:
                    print_colored(f"KeyError: key '{key}' not found in the dictionary. Current dictionary: {dic}", "orange")
                    return None
                dic = dic[key]
        #print_colored(f"Accessing key '{key}': {dic}", "magenta")
        #print_colored(f" ", "magenta")
    return dic

# sys.exit()

# Debugging function to print parameters and types from a JSON structure
def print_json_structure(json_data, prefix=""):
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            full_key = prefix + key
            if isinstance(value, (dict, list)):
                print_json_structure(value, full_key + ".")
            else:
                print(f"{full_key}: {type(value).__name__}")
    elif isinstance(json_data, list):
        for i, item in enumerate(json_data):
            print_json_structure(item, f"{prefix}[{i}].")
            
            

# # Print PIConGPU JSON structure
# print_colored("PIConGPU JSON structure:", "green")
# print_json_structure(picongpu_params)

          
# # Print dictionary JSON structure
# print_colored("Dictionary JSON structure:", "green")
# print_json_structure(correlation_dict)


# # Print Ontology JSON-LD structure
# print_colored("Ontology JSON-LD structure:", "green")
# print_json_structure(ontology_params)

# sys.exit()

# Function to cross-check parameters with debugging
def cross_check_params(picongpu_params, ontology_params, flat_correlation_list):
    for picongpu_param, ontology_param in flat_correlation_list:
        picongpu_value = get_nested_value(picongpu_params, picongpu_param.split('.'))
        
        if picongpu_value is None:  # Skip parameters with null values
            print_colored(f"Parameter {picongpu_param} is null and not found in PIConGPU JSON file, skipping.", "white")
            continue

        if ontology_param not in ontology_params:
            print_colored(f"Parameter {ontology_param} (corresponding to {picongpu_param}) not found in the Ontology JSON-LD.", "orange")
            continue

        ontology_entry = ontology_params[ontology_param]
        ontology_type = get_ontology_type(ontology_entry)

        if ontology_type is None:
            print_colored(f"Type information for parameter {ontology_param} not found in the Ontology JSON-LD.", "yellow")
            continue

        # Check for special handling
        if picongpu_param in params_requiring_special_handling:
            special_handling = params_requiring_special_handling[picongpu_param]
            if ontology_param == special_handling["ontology_param"]:
                picongpu_value = special_handling["value_map"].get(picongpu_value, picongpu_value)
                expected_type = bool if ontology_type == 'boolean' else str
            else:
                expected_type = map_ontology_type_to_python(ontology_type)
        else:
            expected_type = map_ontology_type_to_python(ontology_type)

        if expected_type is None:
            print_colored(f"Unknown type {ontology_type} for parameter {ontology_param} in the Ontology JSON-LD.", "red")
            continue

        # Handle boolean conversion separately if needed
        if ontology_type == 'boolean':
            picongpu_value = bool(picongpu_value == "true" or picongpu_value == "false")

        picongpu_type = type(picongpu_value)

        if not isinstance(picongpu_value, expected_type):
            print_colored(f"Type mismatch for parameter {picongpu_param}: PIConGPU ({picongpu_type}) vs Ontology ({ontology_type})", "magenta")
        else:
            print_colored(f"PIConGPU Parameter: {picongpu_param} ({picongpu_type}), Ontology Parameter: {ontology_param} ({ontology_type})", "green")

# Run the cross-check
cross_check_params(picongpu_params, ontology_params, flat_correlation_list)
