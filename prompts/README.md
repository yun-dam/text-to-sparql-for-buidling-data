# Brick Agent Prompts

This directory contains prompt templates for the Brick Agent. These prompts use the Jinja2 template format.

## Prompt Files

### 1. `brick_controller.prompt`
**Purpose**: Main reasoning prompt that guides the agent's step-by-step query construction.

**Variables**:
- `question` (str): The user's natural language question
- `action_history` (list): List of previous Thought-Action-Observation strings
- `conversation_history` (list): Previous conversation turns (for multi-turn dialogue)

**Key Instructions**:
- Build queries incrementally
- Execute fragments to verify
- Don't repeat actions
- Understand Brick schema patterns

**Usage in code**:
```python
from chainlite import llm_generation_chain

controller_output = llm_generation_chain(
    template_file="brick_controller.prompt",
    engine="gemini-flash",
    max_tokens=700,
    temperature=1.0
).invoke({
    "question": "What is the room temperature?",
    "action_history": state.get_action_history(),
    "conversation_history": []
})
```

### 2. `brick_format_actions.prompt`
**Purpose**: Formats LLM output into structured JSON using few-shot examples.

**Variables**:
- `input` (str): The raw output from the controller (Thought + Action text)

**Contains 6 Few-Shot Examples**:
1. `search_brick` - Finding sensors
2. `get_brick_entity` - Exploring entity properties
3. `get_property_examples` - Learning property usage
4. `execute_sparql` - Simple timeseries query
5. `execute_sparql` - Filtered query with CONTAINS
6. `stop` - Finalizing answer

**Output Format**:
```json
{
    "thought": "string describing reasoning",
    "action_name": "one of the 5 actions",
    "action_argument": "argument for the action"
}
```

**Usage in code**:
```python
formatted_action = llm_generation_chain(
    template_file="brick_format_actions.prompt",
    engine="gemini-flash",
    max_tokens=700,
    output_json=True
).invoke({
    "input": controller_output
})
```

## How Prompts Work Together

```
User Question
     ↓
[brick_controller.prompt]
     ↓
LLM generates: "Thought: ... Action: ..."
     ↓
[brick_format_actions.prompt]
     ↓
Structured JSON: {"thought": "...", "action_name": "...", "action_argument": "..."}
     ↓
Agent executes action
     ↓
Observation added to action_history
     ↓
Repeat until stop()
```

## Comparison with SPINACH Prompts

| Feature | Traditional | Brick Agent |
|---------|---------|--------------|
| Actions | 5 (Wikidata-specific) | 5 (Brick-specific) |
| Examples in format prompt | 4 | 6 |
| Schema patterns mentioned | Generic SPARQL | Brick-specific (hasObservation, etc.) |
| Query complexity | High (Wikidata qualifiers) | Medium (timeseries focus) |

## Adding Custom Prompts

### Example: Add a pruning prompt for Brick entities

```jinja2
# instruction
Given a Brick entity and a question, remove properties that are not relevant.

# input
Entity: {{ entity_info }}
Question: {{ question }}

# output
{
  "relevant_properties": [...]
}
```

### Example: Add a reporter prompt for natural language responses

```jinja2
# instruction
Generate a natural language answer based on the SPARQL results.

# input
Question: {{ question }}
Results: {{ results }}
SPARQL: {{ sparql }}

# output
Based on the building data, ...
```

## Brick-Specific Patterns to Include in Examples

When creating more examples, emphasize these Brick patterns:

### Pattern 1: Basic Timeseries Query
```sparql
SELECT ?value ?timestamp
WHERE {
  bldg:SENSOR_ID ref:hasObservation ?obs .
  ?obs ref:hasValue ?value .
  ?obs ref:hasTimestamp ?timestamp .
}
```

### Pattern 2: Type-Based Search
```sparql
SELECT ?sensor
WHERE {
  ?sensor a brick:Temperature_Sensor .
}
```

### Pattern 3: Equipment Relationships
```sparql
SELECT ?equipment ?sensor
WHERE {
  ?equipment brick:hasPart ?sensor .
  ?sensor a brick:Sensor .
}
```

### Pattern 4: Aggregations
```sparql
SELECT (AVG(?value) as ?avgValue)
WHERE {
  bldg:RM_TEMP ref:hasObservation ?obs .
  ?obs ref:hasValue ?value .
}
```

### Pattern 5: Filtering by Time or Value
```sparql
SELECT ?value ?timestamp
WHERE {
  bldg:RM_TEMP ref:hasObservation ?obs .
  ?obs ref:hasValue ?value .
  ?obs ref:hasTimestamp ?timestamp .
  FILTER(?value > 75.0)
}
```

## Integrating Prompts into Brick Agent

To use these prompts in `brick_agent.py`, update the controller method:

```python
def controller(self, state: AgentState) -> BrickAction:
    """Use LLM with prompts to decide next action"""

    # Stage 1: Generate thought + action
    controller_output = llm_generation_chain(
        template_file="prompts/brick_controller.prompt",
        engine=self.engine,
        max_tokens=700,
        temperature=1.0,
        keep_indentation=True
    ).invoke({
        "question": state.question,
        "action_history": state.get_action_history(),
        "conversation_history": []
    })

    # Stage 2: Format to JSON
    action_json = llm_generation_chain(
        template_file="prompts/brick_format_actions.prompt",
        engine=self.engine,
        max_tokens=700,
        output_json=True
    ).invoke({
        "input": controller_output
    })

    # Parse to BrickAction
    return BrickAction(
        thought=action_json["thought"],
        action_name=action_json["action_name"],
        action_argument=action_json["action_argument"]
    )
```

## Testing Prompts

You can test prompts independently:

```python
from chainlite import llm_generation_chain

# Test controller prompt
result = llm_generation_chain(
    template_file="prompts/brick_controller.prompt",
    engine="gemini-flash"
).invoke({
    "question": "What is the room temperature?",
    "action_history": "",
    "conversation_history": []
})

print(result)
```

## Next Steps

1. Test prompts with your OpenAI API key
2. Add more Brick-specific examples based on your use cases
3. Create domain-specific variants (e.g., HVAC-focused, lighting-focused)
4. Collect real question-answer pairs from building operators
5. Fine-tune prompts based on failure cases
