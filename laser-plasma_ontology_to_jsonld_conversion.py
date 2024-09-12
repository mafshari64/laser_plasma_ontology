# in this code we read .rdf file of ontology and convert it to a JSONLD  (JSON for Linked Data) file.


# python laser-plasma_ontology_to_jsonld_conversion.py


import os
from rdflib import Graph

# Path to ontology directory
directory_path = "P:\\afshari\\Projects\\HZDR_Project\\ontology_laser-plasma\\ontology_git"
input_filename = "laser-plasma_ontology.rdf"
input_path = os.path.join(directory_path, input_filename)

# Ensure the ontology file exists
if not os.path.isfile(input_path):
    raise FileNotFoundError(f"The ontology file was not found at {input_path}")

# Load the ontology using rdflib
g = Graph()
g.parse(input_path, format='application/rdf+xml')

# JSON-LD (JSON for Linked Data) is a widely used format that extends JSON to represent linked data structures, making it a good choice for ontologies.
# Output path for the JSON-LD file

output_filename = "laser-plasma_ontology.jsonld"
output_path = os.path.join(directory_path, output_filename)

# Serialize to JSON-LD
g.serialize(destination=output_path, format='json-ld')

print(f"Ontology has been converted to JSON-LD and saved to {output_path}")
