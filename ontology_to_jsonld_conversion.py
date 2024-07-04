# in this code we read .rdf file of ontology and convert it to a JSONLD  (JSON for Linked Data) file.


# python ontology_to_jsonld_conversion.py


import os
from rdflib import Graph

# Path to your ontology file
ontology_path = "P:\\afshari\\Projects\\HZDR_Project\\ontology_laser-plasma\\laser-plasma_ontology.rdf"

# Ensure the ontology file exists
if not os.path.isfile(ontology_path):
    raise FileNotFoundError(f"The ontology file was not found at {ontology_path}")

# Load the ontology using rdflib
g = Graph()
g.parse(ontology_path, format='application/rdf+xml')

# JSON-LD (JSON for Linked Data) is a widely used format that extends JSON to represent linked data structures, making it a good choice for ontologies.
# Output path for the JSON-LD file
output_directory = "P:\\afshari\\Projects\\HZDR_Project\\ontology_laser-plasma"
output_filename = "laser-plasma_ontology.jsonld"
output_path = os.path.join(output_directory, output_filename)

# Serialize to JSON-LD
g.serialize(destination=output_path, format='json-ld')

print(f"Ontology has been converted to JSON-LD and saved to {output_path}")
