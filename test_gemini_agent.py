"""
Test Brick Agent with Google Gemini LLM
This script tests if the agent can use Gemini to generate SPARQL queries.
Includes custom logging to track all LLM calls.
"""

import json
from datetime import datetime
from brick_agent import BrickAgent

# Custom logging setup with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = f"test_gemini_logs_{timestamp}.jsonl"

def log_llm_call(prompt, response, model, timestamp=None):
    """Log LLM calls to a JSONL file"""
    if timestamp is None:
        timestamp = datetime.now().isoformat()

    log_entry = {
        "timestamp": timestamp,
        "model": model,
        "prompt": prompt,
        "response": response
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    print(f"📝 Logged to {LOG_FILE}")

def test_with_gemini():
    """Test agent with real Gemini LLM"""
    print("\n" + "="*80)
    print("Testing Brick Agent with Google Gemini")
    print(f"Logs will be saved to: {LOG_FILE}")
    print("="*80)

    # Clear previous logs
    with open(LOG_FILE, "w") as f:
        f.write("")
    print(f"🗑️  Cleared previous logs in {LOG_FILE}\n")

    # Initialize agent with Gemini
    agent = BrickAgent(engine="gemini-flash")

    # Patch the agent's controller to log LLM calls
    original_controller = agent.controller

    def logged_controller(state):
        """Wrapper that logs LLM calls"""
        print("\n🤖 Controller called - generating next action...")

        try:
            # Get the action
            action = original_controller(state)

            # Try to log what was sent (approximate)
            prompt_summary = {
                "question": state.question,
                "num_previous_actions": len(state.actions),
                "last_action": state.actions[-1].action_name if state.actions else "None"
            }

            action_info = {
                "thought": action.thought,
                "action_name": action.action_name,
                "action_argument": action.action_argument[:100] + "..." if len(action.action_argument) > 100 else action.action_argument
            }

            log_llm_call(
                prompt=prompt_summary,
                response=action_info,
                model="gemini-flash"
            )

            return action

        except Exception as e:
            print(f"❌ Error in controller: {e}")
            log_llm_call(
                prompt={"question": state.question, "error": str(e)},
                response={"error": str(e)},
                model="gemini-flash"
            )
            raise

    agent.controller = logged_controller

    # Load your Brick data
    print("\nLoading Brick schema and timeseries data...")
    agent.initialize_graph(
        ttl_file="LBNL_FDD_Data_Sets_FCU_ttl.ttl",
        csv_file="LBNL_FDD_Dataset_FCU/FCU_FaultFree.csv",
        max_csv_rows=50
    )
    print("Data loaded successfully!")

    # Get question from user input
    print("\n" + "="*80)
    user_question = input("Enter your question about the Brick data: ").strip()

    while not user_question:
        print("⚠️  Question cannot be empty. Please try again.")
        user_question = input("Enter your question about the Brick data: ").strip()

    questions = [user_question]
    print("="*80)

    for i, question in enumerate(questions, 1):
        print(f"\n{'='*80}")
        print(f"Question {i}: {question}")
        print("="*80)

        try:
            state, final_sparql = agent.run(question, verbose=True)

            if final_sparql and final_sparql.has_results():
                print(f"\n✅ SUCCESS!")
                print(f"   - Actions taken: {len(state.actions)}")
                print(f"   - Result rows: {len(final_sparql.execution_result)}")
                print(f"\n   Final SPARQL:\n{final_sparql.sparql}")
            else:
                print(f"\n⚠️  No results returned (check if mock mode is running)")

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*80)
    print("Test completed!")
    print("="*80)
    print(f"\n📊 Check {LOG_FILE} for detailed logs")
    print(f"📊 Also check prompt_logs_*.jsonl for LLM call logs")

if __name__ == "__main__":
    test_with_gemini()
