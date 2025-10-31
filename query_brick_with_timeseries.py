"""
SPARQL Query Script with Timeseries Data Integration
This script loads both Brick schema metadata AND CSV timeseries data into RDF,
allowing you to query sensor values directly using SPARQL.
"""

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, XSD
import pandas as pd

# Initialize graph
g_temp = Graph()
g = Graph()

# Load TTL file
ttl_file = "LBNL_FDD_Data_Sets_FCU_ttl.ttl" ### TTL File Directory
print("Loading TTL file...")
g_temp.parse(ttl_file, format="turtle")
print(f"Loaded {len(g_temp)} triples from TTL")

# Define relative path namespaces
BLDG = Namespace("bldg-59#")
BRICK = Namespace("https://brickschema.org/schema/Brick#")
REF = Namespace("https://brickschema.org/schema/Brick/ref#")

g.bind("brick", BRICK)
g.bind("bldg", BLDG)
g.bind("ref", REF)

# Convert absolute URIs from TTL to relative URIs
print("Converting absolute URIs to relative URIs...")
converted = 0
for s, p, o in g_temp:
    # Convert subject
    if isinstance(s, URIRef) and "bldg-59#" in str(s):
        local_name = str(s).split("#")[-1]
        s = BLDG[local_name]
        converted += 1

    # Convert object
    if isinstance(o, URIRef) and "bldg-59#" in str(o):
        local_name = str(o).split("#")[-1]
        o = BLDG[local_name]
        converted += 1

    g.add((s, p, o))

print(f"Converted {converted} URIs")
print(f"Total triples: {len(g)}")
print(f"Using namespace: {BLDG}\n")

# Now add CSV data (timeseries observations)
MAX_ROWS = 100
csv_file = "LBNL_FDD_Dataset_FCU/FCU_FaultFree.csv" ### csv File Directory

print(f"Loading CSV: {csv_file}")
df = pd.read_csv(csv_file, nrows=MAX_ROWS)
print(f"Loaded {len(df)} rows\n")

print("Converting CSV to RDF...")
for idx, row in df.iterrows():
    timestamp_str = row['Datetime']
    
    for column_name in df.columns:
        if column_name == 'Datetime':
            continue
        
        value = row[column_name]
        if pd.isna(value):
            continue
        
        obs_uri = BLDG[f"obs_{column_name}_{idx}"]
        sensor_uri = BLDG[column_name]
        
        g.add((sensor_uri, REF.hasObservation, obs_uri))
        g.add((obs_uri, REF.hasTimestamp, Literal(timestamp_str, datatype=XSD.string)))
        g.add((obs_uri, REF.hasValue, Literal(float(value), datatype=XSD.float)))
    
    if (idx + 1) % 20 == 0:
        print(f"  Processed {idx + 1} rows")

print(f"\nCompleted! Total triples: {len(g)}\n")


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


# ============================================================================
# Example Queries: Now you can query both metadata AND values!
# ============================================================================

# Query 1: Find sensors of a specific type and get their latest values
# query1 = """
# PREFIX brick: <https://brickschema.org/schema/Brick#>
# PREFIX bldg: <bldg-59#>
# PREFIX ref: <https://brickschema.org/schema/Brick/ref#>

# SELECT ?sensor ?timestamp ?value
# WHERE {
#   ?sensor a brick:Entering_Water_Temperature_Sensor .
#   ?sensor ref:hasObservation ?obs .
#   ?obs ref:hasTimestamp ?timestamp .
#   ?obs ref:hasValue ?value .
# }
# ORDER BY ?sensor ?timestamp
# LIMIT 20
# """

# Query 1: Show me room temperature over time
query1 = """
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX bldg: <bldg-59#>
PREFIX ref: <https://brickschema.org/schema/Brick/ref#>

SELECT ?timestamp ?temperature
WHERE {
  bldg:RM_TEMP ref:hasObservation ?obs .
  ?obs ref:hasTimestamp ?timestamp .
  ?obs ref:hasValue ?temperature .
}
ORDER BY ?timestamp
LIMIT 100
"""


# Query 2: Get outdoor air temperature data
query2 = """
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX bldg: <bldg-59#>
PREFIX ref: <https://brickschema.org/schema/Brick/ref#>

SELECT ?timestamp ?value
WHERE {
  bldg:FCU_OAT ref:hasObservation ?obs .
  ?obs ref:hasTimestamp ?timestamp .
  ?obs ref:hasValue ?value .
}
ORDER BY ?timestamp
LIMIT 10
"""

# Query 3: What is the discharge air temperature?
query3 = """
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX bldg: <bldg-59#>
PREFIX ref: <https://brickschema.org/schema/Brick/ref#>

SELECT ?timestamp ?oat ?rat ?dat ?mat
WHERE {

  # Discharge Air Temperature
  bldg:FCU_DAT ref:hasObservation ?obs3 .
  ?obs3 ref:hasTimestamp ?timestamp .
  ?obs3 ref:hasValue ?dat .
}
ORDER BY ?timestamp
LIMIT 10
"""

# Query 4: Show me all entering water temperature sensors
query4 = """

PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX bldg: <bldg-59#>
PREFIX ref: <https://brickschema.org/schema/Brick/ref#>

SELECT ?sensor ?timestamp ?value
WHERE {
  ?sensor a brick:Entering_Water_Temperature_Sensor .
  ?sensor ref:hasObservation ?obs .
  ?obs ref:hasTimestamp ?timestamp .
  ?obs ref:hasValue ?value .
}
ORDER BY ?sensor ?timestamp
LIMIT 20
"""

# Query 5: Show me the water temperature entering the cooling coil
query5 = """
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX bldg: <bldg-59#>
PREFIX ref: <https://brickschema.org/schema/Brick/ref#>

SELECT ?timestamp ?value
WHERE {
  bldg:FCU_CLG_EWT ref:hasObservation ?obs .
  ?obs ref:hasTimestamp ?timestamp .
  ?obs ref:hasValue ?value .
}
LIMIT 10
"""

# Query 6: Show me when the room temperature was outside the setpoint range
query6 = """
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX bldg: <bldg-59#>
PREFIX ref: <https://brickschema.org/schema/Brick/ref#>

SELECT ?timestamp ?roomTemp ?heatingSetpoint ?coolingSetpoint
WHERE {
  # Room temperature
  bldg:RM_TEMP ref:hasObservation ?obs1 .
  ?obs1 ref:hasTimestamp ?timestamp .
  ?obs1 ref:hasValue ?roomTemp .

  # Heating setpoint
  bldg:RMHTGSPT ref:hasObservation ?obs2 .
  ?obs2 ref:hasTimestamp ?timestamp .
  ?obs2 ref:hasValue ?heatingSetpoint .

  # Cooling setpoint
  bldg:RMCLGSPT ref:hasObservation ?obs3 .
  ?obs3 ref:hasTimestamp ?timestamp .
  ?obs3 ref:hasValue ?coolingSetpoint .

  # Filter: temperature outside range
  FILTER(?roomTemp < ?heatingSetpoint || ?roomTemp > ?coolingSetpoint)
}
ORDER BY ?timestamp
"""

# Query 7: What are the operating ranges for each temperature sensor?
query7 = """
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX bldg: <bldg-59#>
PREFIX ref: <https://brickschema.org/schema/Brick/ref#>

SELECT ?sensor (AVG(?value) AS ?avgValue) (MIN(?value) AS ?minValue) (MAX(?value) AS ?maxValue)
WHERE {
  # Find all temperature sensors
  ?sensor a ?sensorType .
  FILTER(CONTAINS(STR(?sensorType), "Temperature_Sensor"))

  # Get their observations
  ?sensor ref:hasObservation ?obs .
  ?obs ref:hasValue ?value .
}
GROUP BY ?sensor
ORDER BY ?sensor
"""

# Query 8: Show me all the sensors monitoring water entering the system
query8 = """
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX bldg: <bldg-59#>

SELECT ?sensor ?type
WHERE {
  ?sensor a brick:Entering_Water_Temperature_Sensor .
}
"""
run_query("8. Check if schema loaded (find Entering Water Temp sensors)", query8)

query9 = """

PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX bldg: <bldg-59#>
PREFIX ref: <https://brickschema.org/schema/Brick/ref#>

SELECT ?timestamp ?value
WHERE {
  bldg:FCU_CTRL ref:hasObservation ?obs .
  ?obs ref:hasTimestamp ?timestamp .
  ?obs ref:hasValue ?value .
}
ORDER BY ?timestamp
LIMIT 10
"""


# Run all example queries
if __name__ == "__main__":
    print("\n" + "="*80)
    print("SPARQL QUERIES WITH TIMESERIES DATA")
    print("="*80)

    # run_query("1. Get room temperature (RM_TEMP) values", query1)
    # run_query("2. Get all observations for FCU_OAT sensor", query2)
    # run_query("3. Get discharge air temperature (FCU_DAT)", query3)
    # run_query("4. Get all Entering Water Temperature Sensors", query4)
    # run_query("5. Get cooling coil entering water temp (FCU_CLG_EWT)", query5)
    # run_query("6. Find when room temp was outside setpoint range", query6)
    # run_query("7. Get average/min/max for all temperature sensors", query7)
    # run_query("8. Check if schema is loaded by finding Entering Water Temperature Sensors", query8)
    run_query("9. ", query9)

    print("\n" + "="*80)
    print("DONE!")
    print("="*80)
    print("\nTips:")
    print("- Modify MAX_ROWS variable to load more/less data")
    print("- Use LIMIT in queries to control result size")
    print("- Join metadata (sensor types, equipment) with timeseries values")
    print("- Use FILTER for time ranges or value thresholds")
