"""
Test script for Brick Agent framework
Demonstrates how to use the iterative approach for Brick SPARQL generation.
"""

from brick_agent import BrickAgent, ask_brick
from brick_utils import BrickGraph


def test_basic_functionality():
    """Test basic functionality without LLM (mock mode)"""
    print("\n" + "="*80)
    print("TEST 1: Basic Framework Functionality (Mock Mode)")
    print("="*80)

    # Initialize agent
    agent = BrickAgent()

    # Load your Brick data
    print("\nLoading Brick schema and timeseries data...")
    agent.initialize_graph(
        ttl_file="LBNL_FDD_Data_Sets_FCU_ttl.ttl",
        csv_file="LBNL_FDD_Dataset_FCU/FCU_FaultFree.csv",
        max_csv_rows=50
    )

    # Test questions
    questions = [
        "What are the room temperature values?",
        "Show me all temperature sensors in the building",
        "What is the average discharge air temperature?"
    ]

    for question in questions:
        print(f"\n{'='*80}")
        print(f"Testing Question: {question}")
        print("="*80)

        state, final_sparql = agent.run(question, verbose=True)

        if final_sparql:
            print(f"\n[SUCCESS] Generated SPARQL query")
            print(f"  Actions taken: {len(state.actions)}")
            print(f"  Result rows: {len(final_sparql.execution_result) if final_sparql.execution_result else 0}")
        else:
            print(f"\n[FAILED] Failed to generate SPARQL query")


def test_brick_utils():
    """Test Brick utility functions"""
    print("\n" + "="*80)
    print("TEST 2: Brick Utility Functions")
    print("="*80)

    # Initialize graph
    brick_graph = BrickGraph()
    brick_graph.initialize(ttl_file="LBNL_FDD_Data_Sets_FCU_ttl.ttl")
    brick_graph.add_timeseries_data("LBNL_FDD_Dataset_FCU/FCU_FaultFree.csv", max_rows=50)

    # Test search
    print("\n--- Test search_brick() ---")
    from brick_utils import search_brick, format_search_results
    results = search_brick("temperature", limit=5)
    print(format_search_results(results))

    # Test get entity
    print("\n--- Test get_brick_entity() ---")
    from brick_utils import get_brick_entity, format_entity_info
    if results:
        entity_id = results[0]['id']
        print(f"\nGetting info for entity: {entity_id}")
        entity_info = get_brick_entity(entity_id)
        print(format_entity_info(entity_info))

    # Test execute SPARQL
    print("\n--- Test execute_sparql() ---")
    from brick_utils import execute_sparql
    query = """
    SELECT ?sensor ?type
    WHERE {
        ?sensor a ?type .
        FILTER(CONTAINS(STR(?type), "Sensor"))
    }
    LIMIT 5
    """
    results = execute_sparql(query)
    print(f"Found {len(results)} sensors:")
    for i, row in enumerate(results[:5], 1):
        sensor = row.get('sensor', {}).get('value', 'N/A')
        type_ = row.get('type', {}).get('value', 'N/A')
        print(f"  {i}. {sensor.split('#')[-1]} ({type_.split('#')[-1]})")

    # Test property examples
    print("\n--- Test get_property_examples() ---")
    from brick_utils import get_property_examples
    examples = get_property_examples("hasObservation", limit=3)
    print(f"Found {len(examples)} examples:")
    for subj, prop, obj in examples:
        print(f"  {subj} --{prop}--> {obj}")


def test_action_observation_loop():
    """Test the action-observation loop in detail"""
    print("\n" + "="*80)
    print("TEST 3: Action-Observation Loop")
    print("="*80)

    from brick_agent import BrickAction, AgentState

    # Create a state
    state = AgentState(question="What is the room temperature?")

    print(f"\nQuestion: {state.question}")
    print("\nSimulating action-observation loop:\n")

    # Simulate a few actions
    actions = [
        BrickAction(
            thought="I need to search for room temperature sensors",
            action_name="search_brick",
            action_argument="room temperature"
        ),
        BrickAction(
            thought="Let me explore the RM_TEMP entity",
            action_name="get_brick_entity",
            action_argument="RM_TEMP"
        ),
        BrickAction(
            thought="I'll query for temperature values",
            action_name="execute_sparql",
            action_argument="SELECT ?value WHERE { bldg:RM_TEMP ref:hasObservation ?obs . ?obs ref:hasValue ?value } LIMIT 5"
        ),
    ]

    agent = BrickAgent()
    agent.initialize_graph(
        ttl_file="LBNL_FDD_Data_Sets_FCU_ttl.ttl",
        csv_file="LBNL_FDD_Dataset_FCU/FCU_FaultFree.csv",
        max_csv_rows=50
    )

    for i, action in enumerate(actions, 1):
        print(f"--- Step {i} ---")
        action, sparql = agent.execute_action(action)
        print(action.to_string(include_observation=True))

        if sparql:
            state.generated_sparqls.append(sparql)

        state.actions.append(action)
        print()

    print(f"Total actions: {len(state.actions)}")
    print(f"Total SPARQL queries generated: {len(state.generated_sparqls)}")


def test_quick_helper():
    """Test the quick helper function"""
    print("\n" + "="*80)
    print("TEST 4: Quick Helper Function")
    print("="*80)

    print("\nUsing ask_brick() helper function...")

    result = ask_brick(
        question="What sensors are in the building?",
        ttl_file="LBNL_FDD_Data_Sets_FCU_ttl.ttl",
        csv_file="LBNL_FDD_Dataset_FCU/FCU_FaultFree.csv",
        verbose=True
    )

    if result:
        print(f"\n[SUCCESS] Got {len(result)} results")
    else:
        print(f"\n[FAILED] No results")


def show_framework_structure():
    """Show the structure of the framework"""
    print("\n" + "="*80)
    print("BRICK AGENT FRAMEWORK STRUCTURE")
    print("="*80)

    structure = """
Framework Components:

1. brick_utils.py
   - Brick-specific operations (replaces wikidata_utils.py)
       - BrickGraph: Manages RDF graph
       - execute_sparql(): Run SPARQL queries
       - search_brick(): Search for entities
       - get_brick_entity(): Explore entity properties
       - get_property_examples(): Show property usage

2. brick_agent.py
   - Main agent implementation
       - BrickAction: Thought-Action-Observation
       - BrickSparqlQuery: Query + execution results
       - AgentState: Maintains agent state
       - BrickAgent: Main agent class
           - controller(): Decides next action (uses LLM)
           - execute_action(): Executes actions
           - run(): Main execution loop

3. Integration Points:
   - TTL files: Brick schema metadata
   - CSV files: Timeseries sensor data
   - LLM (chainlite): Decision-making for controller

How it works:
1. User asks a question
2. Controller (LLM) decides next action based on question + history
3. Action is executed (search, explore, query)
4. Observation is returned
5. Loop continues until answer is found
6. Final SPARQL query is returned

Supported Actions:
- search_brick(query): Find relevant sensors/entities
- get_brick_entity(id): Explore entity properties
- get_property_examples(prop): See property usage
- execute_sparql(query): Test SPARQL fragments
- stop(): Finalize answer
"""

    print(structure)


if __name__ == "__main__":
    print("\n" + "="*100)
    print(" "*30 + "BRICK AGENT FRAMEWORK TEST SUITE")
    print("="*100)

    # Show framework structure
    show_framework_structure()

    # Run tests
    try:
        test_brick_utils()
    except Exception as e:
        print(f"\n[WARNING] Test failed: {e}")

    try:
        test_action_observation_loop()
    except Exception as e:
        print(f"\n[WARNING] Test failed: {e}")

    try:
        test_basic_functionality()
    except Exception as e:
        print(f"\n[WARNING] Test failed: {e}")

    try:
        test_quick_helper()
    except Exception as e:
        print(f"\n[WARNING] Test failed: {e}")

    print("\n" + "="*100)
    print("Test suite completed!")
    print("="*100)
    print("\nNext steps:")
    print("1. Add your API key to the API_KEYS file")
    print("2. Implement LLM-based controller (replace mock_controller)")
    print("3. Create Brick-specific prompts in prompts/ directory")
    print("4. Train on example question-SPARQL pairs")
    print("5. Evaluate on your building data questions")
    print("="*100 + "\n")
