# Customization Guide - How to Improve Your Brick Agent

This guide shows you where and how to customize the system to improve performance.

---

## 📝 1. Edit Prompts (Most Important!)

### Location: `prompts/brick_controller.prompt`

**What it controls**: The agent's reasoning, strategy, and behavior

**What to customize**:

#### A. Add domain-specific instructions
Lines 1-12 contain the main instructions. You can add:

```
9. When dealing with HVAC systems, remember that FCU = Fan Coil Unit
10. For fault detection, check if values are outside normal ranges
11. When querying timeseries, always include timestamps for context
```

#### B. Improve Brick Schema patterns
Lines 23-28 teach the agent about Brick patterns. Add your specific patterns:

```
- Equipment relationships: ?equipment brick:feeds ?equipment2
- Location hierarchy: ?room brick:isPartOf ?floor
- Points feed equipment: ?point brick:isPointOf ?equipment
- Common sensor types: Temperature_Sensor, Pressure_Sensor, Flow_Sensor
```

#### C. Add error handling hints

After line 11, add:
```
12. If a query returns no results, try searching with broader terms
13. If you get a syntax error, check namespace prefixes (brick:, bldg:, ref:)
14. Always use LIMIT in queries to avoid overwhelming results
```

#### D. Add examples of good reasoning

After line 28, add a section:
```
Example reasoning patterns:
- First search → then explore entities → then build query → then execute
- If unsure about property names, use get_property_examples()
- Test queries with LIMIT 5 first, then increase if needed
```

---

### Location: `prompts/brick_format_actions.prompt`

**What it controls**: How Gemini's output is converted to structured actions

**What to customize**:

#### Add more examples (lines 13-101)

Add examples for common patterns you see failing:

```
# input
Thought: I need to find all sensors measuring air flow in the building.
Action: search_brick(air flow sensor)

# output
{
    'thought': 'I need to find all sensors measuring air flow in the building.',
    'action_name': 'search_brick',
    'action_argument': 'air flow sensor'
}
```

The more examples you add, the better Gemini formats its output!

---

## 🔧 2. Modify Agent Behavior (`brick_agent.py`)

### A. Change max iterations

Line 128 in `brick_agent.py`:
```python
max_iterations: int = 15  # Increase to 20 for complex queries
```

### B. Adjust action history length

Line 130:
```python
def get_action_history(self, last_n: int = 10, include_observation: bool = True):
```

Change `last_n` to show more or fewer previous actions to Gemini:
- **More (15-20)**: Better context, more tokens
- **Less (5-7)**: Faster, cheaper, less context

### C. Customize duplicate detection

Line 147:
```python
def is_duplicate_action(self, action: BrickAction) -> bool:
    return action in self.actions[-5:]  # Check last 5 actions
```

Change `-5` to `-3` for stricter duplicate checking, or `-10` for looser.

---

## 🎛️ 3. Adjust LLM Settings (`llm_config.yaml`)

### A. Switch models based on task

```yaml
engine_map:
  gemini-flash: vertex_ai/gemini-2.0-flash-exp       # Fast, cheap
  gemini-pro: vertex_ai/gemini-1.5-pro-002           # Accurate, expensive
  gemini-flash-lite: vertex_ai/publishers/google/models/gemini-2.5-flash-lite  # Ultra-fast
```

In code, switch per task:
```python
# For simple queries
agent = BrickAgent(engine="gemini-flash-lite")

# For complex reasoning
agent = BrickAgent(engine="gemini-pro")
```

### B. Enable verbose logging

Line 6 in `llm_config.yaml`:
```yaml
litellm_set_verbose: true  # See all LLM API calls
```

### C. Adjust prompt logging

Lines 8-9:
```yaml
prompt_logging:
  log_file: "./prompt_logs.jsonl"  # Check this file to see what Gemini sees
```

Review `prompt_logs.jsonl` to see:
- What prompts are being sent
- What responses Gemini gives
- Where it's making mistakes

---

## 🔍 4. Improve Search and Entity Functions (`brick_utils.py`)

### A. Customize search ranking

Line 95 in `brick_utils.py` - `search_brick()`:

Current behavior: Returns entities matching the search term.

**Improve by**:
- Add fuzzy matching
- Prioritize certain entity types
- Include descriptions in search

### B. Enhance entity information

Line 140 - `get_brick_entity()`:

Current: Returns all properties and relationships.

**Improve by**:
- Adding entity descriptions
- Showing example values
- Grouping related properties

### C. Add new actions

Add custom actions in `BrickAction.POSSIBLE_ACTIONS` (line 45):

```python
POSSIBLE_ACTIONS = [
    "search_brick",
    "get_brick_entity",
    "get_property_examples",
    "execute_sparql",
    "get_similar_entities",     # NEW: Find similar sensors
    "validate_query",            # NEW: Check SPARQL syntax before executing
    "get_value_range",           # NEW: Get min/max values for a sensor
    "stop"
]
```

Then implement them in `execute_action()` (line 282).

---

## 📊 5. Add Few-Shot Examples

### Create example Q&A pairs

Create `prompts/brick_examples.txt`:

```
Question: What is the current room temperature?
Expected Actions:
1. search_brick("room temperature")
2. get_brick_entity("RM_TEMP")
3. execute_sparql("SELECT ?value WHERE { bldg:RM_TEMP ref:hasObservation ?obs . ?obs ref:hasValue ?value } LIMIT 1")
4. stop()

Question: Which sensors are in the HVAC system?
Expected Actions:
1. search_brick("HVAC sensor")
2. execute_sparql("SELECT ?sensor ?type WHERE { ?sensor a ?type . FILTER(CONTAINS(STR(?sensor), 'FCU')) } LIMIT 10")
3. stop()
```

Then add to `brick_controller.prompt` at line 29:

```
Examples of good reasoning:
{% include 'brick_examples.txt' %}
```

---

## 🧪 6. Measure and Iterate

### A. Create evaluation dataset

Create `test_questions.json`:
```json
[
  {
    "question": "What is the room temperature?",
    "expected_vars": ["value"],
    "expected_results": "> 0"
  },
  {
    "question": "List all temperature sensors",
    "expected_vars": ["sensor", "type"],
    "expected_results": "> 5"
  }
]
```

### B. Create evaluation script

```python
# evaluate_agent.py
import json
from brick_agent import BrickAgent

agent = BrickAgent(engine="gemini-flash")
agent.initialize_graph(ttl_file="LBNL_FDD_Data_Sets_FCU_ttl.ttl")

with open("test_questions.json") as f:
    test_cases = json.load(f)

correct = 0
for test in test_cases:
    state, sparql = agent.run(test["question"], verbose=False)
    if sparql and sparql.has_results():
        correct += 1

print(f"Accuracy: {correct}/{len(test_cases)}")
```

### C. Track metrics

Add to your evaluation:
- **Success rate**: % of questions answered
- **Average actions**: How many steps to answer
- **Query correctness**: Does SPARQL return expected results?
- **Token usage**: Cost per question

---

## 🎯 Recommended Improvement Workflow

### Phase 1: Start Simple (Week 1)
1. ✅ Run `test_gemini_agent.py` - get baseline
2. ✅ Review `prompt_logs.jsonl` - see what Gemini is doing
3. ✅ Add 3-5 domain-specific instructions to `brick_controller.prompt`
4. ✅ Add 2-3 examples to `brick_format_actions.prompt`

### Phase 2: Test & Iterate (Week 2)
5. Create 10 test questions from your domain
6. Run evaluation, measure success rate
7. Find patterns in failures
8. Update prompts to address failures
9. Repeat steps 6-8

### Phase 3: Advanced (Week 3+)
10. Add custom actions to `brick_utils.py`
11. Implement error recovery strategies
12. Fine-tune search and entity functions
13. Add multi-step reasoning examples

---

## 📈 Common Issues & Solutions

### Issue: Agent repeats the same action
**Solution**: Strengthen duplicate detection (line 147 in `brick_agent.py`)

### Issue: Agent stops too early
**Solution**: Add more specific success criteria in `brick_controller.prompt`

### Issue: Queries have syntax errors
**Solution**: Add more SPARQL examples to `brick_format_actions.prompt`

### Issue: Agent can't find entities
**Solution**: Improve search function in `brick_utils.py` (fuzzy matching)

### Issue: Too many actions taken
**Solution**: Reduce `max_iterations` or add "be concise" instruction to prompt

---

## 🔑 Quick Wins

**5-Minute Improvements**:
1. Add `litellm_set_verbose: true` to see what's happening
2. Add "Always use LIMIT 10" to controller prompt
3. Increase `max_iterations` from 15 to 20

**30-Minute Improvements**:
1. Add 5 examples to `brick_format_actions.prompt`
2. Add domain-specific Brick patterns to `brick_controller.prompt`
3. Create 10 test questions and run evaluation

**1-Hour Improvements**:
1. Review `prompt_logs.jsonl` and identify failure patterns
2. Add error handling instructions to controller prompt
3. Create custom action for your most common query pattern

---

## 📚 Files Quick Reference

| File | Purpose | Edit Frequency |
|------|---------|----------------|
| `prompts/brick_controller.prompt` | Agent reasoning | **HIGH** |
| `prompts/brick_format_actions.prompt` | Output formatting | Medium |
| `brick_agent.py` | Core logic | Low |
| `brick_utils.py` | Brick operations | Low |
| `llm_config.yaml` | LLM settings | Medium |
| `prompt_logs.jsonl` | Debug logs | **Read Often** |

---

## 🎓 Learning Resources

**Understanding your agent**:
1. Read `prompt_logs.jsonl` after each run
2. Enable verbose mode to see decision-making
3. Compare successful vs failed runs

**Improving prompts**:
- [Gemini Prompting Best Practices](https://ai.google.dev/gemini-api/docs/prompting-strategies)
- [Few-shot Learning Guide](https://ai.google.dev/gemini-api/docs/few-shot-learning)

**SPARQL query patterns**:
- Check `query_brick_with_timeseries.py` for working examples
- Review Brick Schema docs: https://brickschema.org/

---

Start with the prompts! 90% of improvement comes from better prompt engineering. Good luck! 🚀
