"""
Simple SPARQL Query Script for BRICK Schema HVAC Data
This script loads the LBNL FCU dataset and runs SPARQL queries to explore the building data.
"""

from rdflib import Graph, Namespace
from rdflib.plugins.sparql import prepareQuery

# Initialize the RDF graph
g = Graph()

# Load the BRICK schema TTL file
print("Loading BRICK schema data...")
g.parse("LBNL_FDD_Data_Sets_FCU_ttl.ttl", format="turtle")
print(f"Loaded {len(g)} triples from the dataset.\n")

# Define namespaces
BRICK = Namespace("https://brickschema.org/schema/Brick#")

# Auto-detect the building namespace by finding any subject URI containing "bldg-59#"
# This handles the case where relative URIs get expanded to file:// URIs
bldg_uri = None
for s, p, o in g:
    if "bldg-59#" in str(s):
        bldg_uri = str(s).split("bldg-59#")[0] + "bldg-59#"
        break

if bldg_uri:
    print(f"Detected building namespace: {bldg_uri}")
    BLDG = Namespace(bldg_uri)
else:
    print("Warning: Could not detect building namespace, using default")
    BLDG = Namespace("bldg-59#")

# Bind namespaces for cleaner query output
g.bind("brick", BRICK)
g.bind("bldg", BLDG)

# Debug: Print some sample triples
print("\nSample triples from the graph:")
for i, (s, p, o) in enumerate(g):
    if i < 3:
        print(f"  Subject: {s}")
        print(f"  Predicate: {p}")
        print(f"  Object: {o}\n")
print()


def run_query(query_name, query_string):
    """Execute a SPARQL query and display results."""
    print(f"\n{'='*80}")
    print(f"Query: {query_name}")
    print(f"{'='*80}")
    print(f"SPARQL:\n{query_string}\n")

    results = g.query(query_string)

    print("Results:")
    print("-" * 80)
    for row in results:
        print(" | ".join(str(item) for item in row))
    print(f"\nTotal results: {len(results)}\n")
    return results


# Example Query 1: Get all equipment in the building
query1 = """
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX bldg: <bldg-59#>

SELECT ?equipment ?type
WHERE {
?equipment a ?type .
FILTER (?type != brick:Zone)
FILTER EXISTS { ?equipment brick:hasPoint|brick:hasPart|brick:feeds ?x }
}
ORDER BY ?type
"""

# Example Query 2: Get all sensor points associated with the FCU
query2 = """
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX bldg: <bldg-59#>

SELECT ?point ?pointType
WHERE {
    bldg:FCU_OAT brick:hasPoint ?point .
    ?point a ?pointType .
}
ORDER BY ?pointType
"""

# Example Query 3: Get all components of the FCU and their types
query3 = """
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX bldg: <bldg-59#>

SELECT ?component ?componentType
WHERE {
    bldg:FCU brick:hasPart ?component .
    ?component a ?componentType .
}
"""

# Example Query 4: Get all temperature sensors
query4 = """
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX bldg: <bldg-59#>

SELECT ?sensor ?sensorType
WHERE {
    ?sensor a ?sensorType .
    FILTER(CONTAINS(STR(?sensorType), "Temperature_Sensor"))
}
"""

# Example Query 5: Get equipment hierarchy (FCU -> components -> points)
query5 = """
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX bldg: <bldg-59#>

SELECT ?equipment ?component ?point ?pointType
WHERE {
    bldg:FCU brick:hasPart ?component .
    ?component brick:hasPoint ?point .
    ?point a ?pointType .
}
ORDER BY ?component
"""

# Example Query 6: Get all points related to the cooling coil
query6 = """
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX bldg: <bldg-59#>

SELECT ?point ?pointType
WHERE {
    bldg:Cooling_coil brick:hasPoint ?point .
    ?point a ?pointType .
}
"""


if __name__ == "__main__":
    print("\n" + "="*80)
    print("BRICK Schema SPARQL Query Examples - LBNL FCU Dataset")
    print("="*80)

    # Run all example queries
    run_query("1. Get all equipment in the building", query1)
    run_query("2. Get all sensor points of the FCU", query2)
    run_query("3. Get all components of the FCU", query3)
    run_query("4. Get all temperature sensors", query4)
    run_query("5. Get equipment hierarchy (FCU -> components -> points)", query5)
    run_query("6. Get all points related to the cooling coil", query6)

    print("\n" + "="*80)
    print("Custom Query Section")
    print("="*80)
    print("\nYou can add your own SPARQL queries below:")
    print("Example:")
    print("""
    custom_query = \"\"\"
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX bldg: <bldg-59#>

    SELECT ?s ?p ?o
    WHERE {
        ?s ?p ?o .
    }
    LIMIT 10
    \"\"\"

    run_query("My Custom Query", custom_query)
    """)
