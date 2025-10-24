"""
Brick Agent
An iterative framework for converting natural language questions to Brick SPARQL queries.
Uses a part-to-whole approach to build queries incrementally.
"""

import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import pandas as pd

from brick_utils import (
    BrickGraph,
    execute_sparql,
    search_brick,
    get_brick_entity,
    get_property_examples,
    format_search_results,
    format_entity_info,
    SparqlExecutionStatus,
    BRICK_PREFIXES
)

# Try to import chainlite, but allow running without it for testing
try:
    from chainlite import chain, llm_generation_chain
    CHAINLITE_AVAILABLE = True
except ImportError:
    print("Warning: chainlite not available. Running in mock mode.")
    CHAINLITE_AVAILABLE = False


@dataclass
class BrickAction:
    """
    Represents a single action in the reasoning chain.
    Follows the Thought-Action-Observation pattern.
    """
    thought: str
    action_name: str
    action_argument: str
    observation: Optional[str] = None
    observation_raw: Optional[any] = None

    POSSIBLE_ACTIONS = [
        "search_brick",           # Search for entities/sensors
        "get_brick_entity",       # Explore entity properties
        "get_property_examples",  # See how properties are used
        "execute_sparql",         # Test SPARQL query
        "stop"                    # Finalize answer
    ]

    def __post_init__(self):
        if self.action_name not in self.POSSIBLE_ACTIONS:
            raise ValueError(f"Invalid action: {self.action_name}. Must be one of {self.POSSIBLE_ACTIONS}")

    def to_string(self, include_observation: bool = True) -> str:
        """Format action for display"""
        result = f"Thought: {self.thought}\n"
        result += f"Action: {self.action_name}({self.action_argument})\n"
        if include_observation and self.observation:
            result += f"Observation: {self.observation}\n"
        return result

    def __eq__(self, other):
        """Check if two actions are duplicates"""
        if not isinstance(other, BrickAction):
            return False
        return (self.action_name == other.action_name and
                self.action_argument == other.action_argument)

    def __hash__(self):
        return hash((self.action_name, self.action_argument))


@dataclass
class BrickSparqlQuery:
    """Represents a SPARQL query with its execution results"""
    sparql: str
    execution_result: Optional[List[Dict]] = None
    execution_status: Optional[SparqlExecutionStatus] = None

    def execute(self):
        """Execute the SPARQL query"""
        self.execution_result, self.execution_status = execute_sparql(
            self.sparql,
            return_status=True
        )

    def has_results(self) -> bool:
        """Check if query returned results"""
        return bool(self.execution_result)

    def results_as_table(self, max_rows: int = 10) -> str:
        """Format results as a text table"""
        if not self.execution_result:
            return "No results"

        # Convert to DataFrame for nice formatting
        formatted_data = []
        for row in self.execution_result:
            formatted_row = {}
            for key, val in row.items():
                formatted_row[key] = val.get('value', str(val))
            formatted_data.append(formatted_row)

        df = pd.DataFrame(formatted_data)

        if len(df) > max_rows:
            # Show first and last rows
            half = max_rows // 2
            top = df.head(half)
            bottom = df.tail(max_rows - half)
            result = top.to_string(index=False) + f"\n... ({len(df) - max_rows} rows omitted) ...\n" + bottom.to_string(index=False, header=False)
        else:
            result = df.to_string(index=False)

        return result


@dataclass
class AgentState:
    """Maintains the state of the Brick agent"""
    question: str
    actions: List[BrickAction] = field(default_factory=list)
    generated_sparqls: List[BrickSparqlQuery] = field(default_factory=list)
    final_sparql: Optional[BrickSparqlQuery] = None
    max_iterations: int = 15

    def get_action_history(self, last_n: int = 10, include_observation: bool = True) -> str:
        """Get formatted action history for context"""
        recent_actions = self.actions[-last_n:] if len(self.actions) > last_n else self.actions

        history = []
        for i, action in enumerate(recent_actions):
            # Skip observations for search/get actions in the middle
            should_include_obs = include_observation
            if i < len(recent_actions) - 2 and action.action_name in ["search_brick", "get_brick_entity"]:
                should_include_obs = False

            history.append(action.to_string(include_observation=should_include_obs))

        return "\n".join(history)

    def is_duplicate_action(self, action: BrickAction) -> bool:
        """Check if action is a duplicate of recent actions"""
        return action in self.actions[-5:]

    def should_stop(self) -> bool:
        """Check if agent should stop (max iterations or stop action)"""
        if len(self.actions) >= self.max_iterations:
            return True
        if self.actions and self.actions[-1].action_name == "stop":
            return True
        return False


class BrickAgent:
    """
    Main agent class that implements the iterative approach for Brick SPARQL generation.
    """

    def __init__(self, engine: str = "gpt-4o"):
        """
        Initialize the agent.

        Args:
            engine: LLM engine to use (e.g., 'gpt-4o', 'gpt-3.5-turbo')
        """
        self.engine = engine
        self.brick_graph = BrickGraph()

    def initialize_graph(self, ttl_file: str = None, csv_file: str = None, max_csv_rows: int = 100):
        """
        Initialize the Brick graph with data.

        Args:
            ttl_file: Path to Turtle file with Brick schema
            csv_file: Path to CSV file with timeseries data
            max_csv_rows: Maximum rows to load from CSV
        """
        self.brick_graph.initialize(ttl_file=ttl_file)

        if csv_file:
            self.brick_graph.add_timeseries_data(csv_file, max_rows=max_csv_rows)

    def controller(self, state: AgentState) -> BrickAction:
        """
        The controller decides the next action based on the question and history.
        This is the "brain" of the agent.

        Args:
            state: Current agent state

        Returns:
            Next action to take
        """
        if not CHAINLITE_AVAILABLE:
            # Mock mode for testing
            return self._mock_controller(state)

        # Build context for LLM
        context = {
            "question": state.question,
            "action_history": state.get_action_history()
        }

        # Use LLM to decide next action
        # This would use chainlite's llm_generation_chain with a prompt
        # For now, using a simple prompt template

        prompt = self._build_controller_prompt(context)

        # Call LLM (placeholder - would use chainlite)
        # response = llm_generation_chain(...)(prompt)

        # Parse response into BrickAction
        # For now, return a mock action
        return self._mock_controller(state)

    def _build_controller_prompt(self, context: Dict) -> str:
        """Build the prompt for the controller LLM"""
        prompt = f"""Your task is to write a Brick SPARQL query to answer the given question. Follow a step-by-step process:

1. Start by constructing very simple fragments of the SPARQL query.
2. Execute each fragment to verify its correctness. Adjust as needed based on observations.
3. Confirm all your assumptions about the Brick schema structure before proceeding.
4. Gradually build the complete SPARQL query by adding one piece at a time.
5. Do NOT repeat the same action, as the results will be the same.
6. Continue until you find the answer.

Form exactly one "Thought" and perform exactly one "Action", then wait for the "Observation".

Possible actions:
- search_brick(string): Search for Brick entities (sensors, equipment) matching the string
- get_brick_entity(entity_id): Get all properties and relationships of a Brick entity
- get_property_examples(property_name): See examples of how a property is used
- execute_sparql(SPARQL): Run a SPARQL query and get results
- stop(): Mark the last SPARQL query as final answer and end

User Question: {context['question']}

{context['action_history']}

Output one "Thought" and one "Action":
"""
        return prompt

    def _mock_controller(self, state: AgentState) -> BrickAction:
        """Mock controller for testing without LLM"""
        num_actions = len(state.actions)

        if num_actions == 0:
            # First action: search for relevant entities
            return BrickAction(
                thought="I need to find sensors related to the question",
                action_name="search_brick",
                action_argument="temperature"
            )
        elif num_actions == 1:
            # Second action: explore an entity
            return BrickAction(
                thought="Let me explore the RM_TEMP sensor to understand its properties",
                action_name="get_brick_entity",
                action_argument="RM_TEMP"
            )
        elif num_actions == 2:
            # Third action: test a simple SPARQL
            return BrickAction(
                thought="I'll test a simple query to get temperature values",
                action_name="execute_sparql",
                action_argument="SELECT ?value WHERE { bldg:RM_TEMP ref:hasObservation ?obs . ?obs ref:hasValue ?value } LIMIT 10"
            )
        else:
            # Stop
            return BrickAction(
                thought="Query works! Ready to finalize",
                action_name="stop",
                action_argument=""
            )

    def execute_action(self, action: BrickAction) -> BrickAction:
        """
        Execute an action and populate its observation.

        Args:
            action: Action to execute

        Returns:
            Action with observation filled
        """
        try:
            if action.action_name == "search_brick":
                results = search_brick(action.action_argument)
                action.observation_raw = results
                action.observation = format_search_results(results)

            elif action.action_name == "get_brick_entity":
                entity_info = get_brick_entity(action.action_argument)
                action.observation_raw = entity_info
                action.observation = format_entity_info(entity_info)

            elif action.action_name == "get_property_examples":
                examples = get_property_examples(action.action_argument)
                action.observation_raw = examples
                if examples:
                    lines = [f"{subj} -- {prop} --> {obj}" for subj, prop, obj in examples]
                    action.observation = "\n".join(lines)
                else:
                    action.observation = "No examples found"

            elif action.action_name == "execute_sparql":
                sparql_query = BrickSparqlQuery(sparql=action.action_argument)
                sparql_query.execute()

                action.observation_raw = sparql_query

                if sparql_query.has_results():
                    action.observation = sparql_query.results_as_table()
                else:
                    action.observation = f"Query returned no results. Status: {sparql_query.execution_status.value}"

                # Store the SPARQL query
                return action, sparql_query

            elif action.action_name == "stop":
                action.observation = "Stopping execution"

            else:
                action.observation = f"Unknown action: {action.action_name}"

        except Exception as e:
            action.observation = f"Error executing action: {str(e)}"

        return action, None

    def run(self, question: str, verbose: bool = True) -> Tuple[AgentState, Optional[BrickSparqlQuery]]:
        """
        Run the agent on a question.

        Args:
            question: Natural language question
            verbose: If True, print progress

        Returns:
            (final_state, final_sparql) tuple
        """
        state = AgentState(question=question)

        if verbose:
            print(f"\n{'='*80}")
            print(f"Question: {question}")
            print(f"{'='*80}\n")

        while not state.should_stop():
            # Get next action from controller
            action = self.controller(state)

            # Check for duplicates
            if state.is_duplicate_action(action):
                if verbose:
                    print(f"[WARNING] Duplicate action detected: {action.action_name}({action.action_argument})")
                    print("   Skipping...\n")
                # Force stop if repeating
                action = BrickAction(
                    thought="Detected duplicate action, stopping",
                    action_name="stop",
                    action_argument=""
                )

            # Execute action
            action, sparql_query = self.execute_action(action)

            # Store action
            state.actions.append(action)

            # Store SPARQL if generated
            if sparql_query:
                state.generated_sparqls.append(sparql_query)

            # Print progress
            if verbose:
                print(action.to_string(include_observation=True))
                print()

        # Set final SPARQL
        if state.generated_sparqls:
            state.final_sparql = state.generated_sparqls[-1]

        if verbose:
            print(f"{'='*80}")
            print(f"Completed in {len(state.actions)} actions")
            if state.final_sparql:
                print(f"\nFinal SPARQL:\n{state.final_sparql.sparql}")
                print(f"\nFinal Results:\n{state.final_sparql.results_as_table()}")
            print(f"{'='*80}\n")

        return state, state.final_sparql


# Simple helper function for quick testing
def ask_brick(question: str, ttl_file: str = None, csv_file: str = None, verbose: bool = True):
    """
    Quick helper to ask a question about Brick data.

    Args:
        question: Natural language question
        ttl_file: Path to Brick TTL file
        csv_file: Path to timeseries CSV file
        verbose: Print progress

    Returns:
        Final SPARQL query results
    """
    agent = BrickAgent()
    agent.initialize_graph(ttl_file=ttl_file, csv_file=csv_file)

    state, final_sparql = agent.run(question, verbose=verbose)

    if final_sparql and final_sparql.has_results():
        return final_sparql.execution_result
    return None


if __name__ == "__main__":
    # Example usage
    print("Brick Agent - Iterative framework for Brick SPARQL generation")
    print("="*80)

    # Initialize with your data files
    agent = BrickAgent(engine="gpt-4o")

    # Load Brick schema and timeseries data
    agent.initialize_graph(
        ttl_file="LBNL_FDD_Data_Sets_FCU_ttl.ttl",
        csv_file="LBNL_FDD_Dataset_FCU/FCU_FaultFree.csv",
        max_csv_rows=100
    )

    # Ask a question
    question = "What are the room temperature values?"
    state, final_sparql = agent.run(question, verbose=True)
