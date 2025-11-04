# API Keys Setup Guide

## ⚠️ THIS PROJECT NOW USES GOOGLE GEMINI

This project has been configured to use **Google Gemini via Vertex AI**.

**👉 See [GEMINI_SETUP_GUIDE.md](GEMINI_SETUP_GUIDE.md) for complete setup instructions.**

The configuration is already done - you just need to:
1. Set up Google Cloud authentication
2. Update your project ID in the `API_KEYS` file

---

## Alternative: Other LLM Providers

If you prefer to use a different LLM provider, see the legacy instructions below.

### OpenAI (Legacy - Not Currently Configured)

### Step 1: Get Your API Key

1. Go to **https://platform.openai.com/api-keys**
2. Sign in (or create an account)
3. Click **"Create new secret key"**
4. Name it (e.g., "Brick Agent")
5. Copy the key - it looks like: `sk-proj-abc123xyz...`

### Step 2: Add to API_KEYS File

Open the `API_KEYS` file in your project directory and add:

```bash
OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_KEY_HERE
```

**That's it!** Your framework is now ready to use GPT-4o.

### Step 3: Test It

```python
from brick_agent import Brick AgentAgent

agent = Brick AgentAgent(engine="gpt-4o")
agent.initialize_graph(ttl_file="LBNL_FDD_Data_Sets_FCU_ttl.ttl")
state, sparql = agent.run("What is the room temperature?")
```

---

## 💰 Cost Estimates

**OpenAI Pricing (as of 2024)**:
- **GPT-4o**: $2.50 per 1M input tokens, $10 per 1M output tokens
- **GPT-3.5-turbo**: $0.50 per 1M input tokens, $1.50 per 1M output tokens

**Typical Query Cost**:
- Simple question (4-5 actions): ~$0.01 - $0.05 with GPT-4o
- Complex question (10+ actions): ~$0.10 - $0.20 with GPT-4o

**Budget Option**: Use `gpt-3.5-turbo` for 10x cheaper:
```python
agent = Brick AgentAgent(engine="gpt-3.5-turbo")
```

---

## 🔄 Alternative Providers

### Anthropic Claude

**Why choose Claude:**
- Often better reasoning for complex queries
- Larger context window (200K tokens)
- Strong code generation

**Setup:**
1. Get key: https://console.anthropic.com/
2. Add to `API_KEYS`:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE
   ```
3. Update `llm_config.yaml` (see `llm_config_examples.yaml`)
4. Use in code:
   ```python
   agent = Brick AgentAgent(engine="claude-3.5-sonnet")
   ```

### Azure OpenAI (Enterprise)

**Why choose Azure:**
- Enterprise compliance requirements
- Already have Azure subscription
- Need SLA guarantees

**Setup:**
1. Deploy GPT-4o in Azure Portal
2. Get endpoint and key
3. Add to `API_KEYS`:
   ```bash
   AZURE_OPENAI_API_KEY=your-azure-key
   ```
4. Update `llm_config.yaml` with your endpoint

### Other Options

See `llm_config_examples.yaml` for:
- **Mistral AI** - European provider, GDPR compliant
- **Together AI** - Open source models (Llama, Mixtral)
- **Local Models** - Run locally with Ollama/LM Studio (free!)

---

## 🧪 Testing Without API Keys

The framework includes a **mock mode** for testing:

```python
from brick_agent import Brick AgentAgent

# Will use mock controller if no API key
agent = Brick AgentAgent()
agent.initialize_graph(ttl_file="your_data.ttl")
state, sparql = agent.run("What is the room temperature?")
```

**Mock mode**:
- ✅ Tests framework logic
- ✅ Tests Brick utilities
- ✅ Executes SPARQL queries
- ❌ Uses predefined actions (not intelligent)
- ❌ Can't handle arbitrary questions

---

## 🔧 Configuration Files

### API_KEYS File Format

```bash
# Add your API keys here
# Format: KEY_NAME=value

OPENAI_API_KEY=sk-proj-abc123...
ANTHROPIC_API_KEY=sk-ant-xyz789...
MISTRAL_API_KEY=abc123xyz...

# Lines starting with # are comments
# Don't commit this file to git!
```

### llm_config.yaml

Already configured for OpenAI. Key sections:

```yaml
prompt_dirs:
  - "./prompts"  # Your Brick Agent prompts

llm_endpoints:
  - api_base: https://api.openai.com/v1
    api_key: OPENAI_API_KEY  # References API_KEYS file
    engine_map:
      gpt-4o: gpt-4o
```

---

## ✅ Verify Setup

### Check 1: API Key is Loaded

```python
import os
from dotenv import load_dotenv

# If using .env file (optional)
load_dotenv("API_KEYS")

# Check key is present
print("OpenAI key present:", "OPENAI_API_KEY" in os.environ)
```

### Check 2: Chainlite Can Connect

```python
from chainlite import llm_generation_chain

# Simple test
response = llm_generation_chain(
    template_file="prompts/brick_controller.prompt",
    engine="gpt-4o",
    max_tokens=100
).invoke({
    "question": "Test question",
    "action_history": "",
    "conversation_history": []
})

print("LLM Response:", response)
```

### Check 3: Full Agent Test

```bash
python test_brick_agent.py
```

Should now use real LLM instead of mock mode!

---

## 🔒 Security Best Practices

### Do NOT:
- ❌ Commit `API_KEYS` file to git
- ❌ Share your API key publicly
- ❌ Hardcode keys in your code

### DO:
- ✅ Add `API_KEYS` to `.gitignore`
- ✅ Rotate keys periodically
- ✅ Set spending limits in provider dashboard
- ✅ Use environment variables in production

### Add to .gitignore:

```bash
# Add this line to .gitignore
API_KEYS
.env
```

---

## 🚨 Troubleshooting

### "FileNotFoundError: API_KEYS"

**Solution**: Create the file in your project root:
```bash
touch API_KEYS  # On Mac/Linux
type nul > API_KEYS  # On Windows
```

### "Authentication Error / Invalid API Key"

**Check:**
1. Key is correctly copied (no extra spaces)
2. Key starts with correct prefix (`sk-proj-` for OpenAI)
3. Key hasn't been revoked
4. Billing is set up in provider dashboard

### "chainlite not available"

**Solution**: Install chainlite:
```bash
pip install chainlite==0.1.12
```

### "Rate Limit Error"

**Solution**:
- Wait a few seconds and retry
- Use GPT-3.5 for faster, cheaper queries
- Set up rate limiting in your code

---

## 💡 Next Steps

Once your API key is set up:

1. **Replace mock controller** in `brick_agent.py`
2. **Test with real questions** from your building data
3. **Collect examples** of good/bad responses
4. **Fine-tune prompts** based on results
5. **Monitor costs** in provider dashboard

---

## 📚 Additional Resources

- **OpenAI Platform**: https://platform.openai.com/docs
- **Anthropic Console**: https://console.anthropic.com/
- **LiteLLM Docs**: https://docs.litellm.ai/
- **Chainlite Docs**: https://github.com/stanford-oval/chainlite

---

## 🎯 Summary

**For most users:**
1. Get OpenAI API key from https://platform.openai.com/api-keys
2. Add to `API_KEYS` file: `OPENAI_API_KEY=sk-proj-...`
3. Run your agent with `engine="gpt-4o"`
4. Done!

**Current config is ready** - just needs your actual API key!
