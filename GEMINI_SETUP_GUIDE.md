# Google Gemini / Vertex AI Setup Guide

This guide will help you set up Google Gemini via Vertex AI for the Brick Agent text-to-SPARQL project.

## Prerequisites

- Google Cloud account with active credits
- GCP project with Vertex AI API enabled
- Python 3.8+ installed

---

## Step 1: Set Up Google Cloud Project

### 1.1 Create or Select a Project

1. Go to **Google Cloud Console**: https://console.cloud.google.com
2. Create a new project or select an existing one
3. Note your **Project ID** (e.g., `cs224v-yundamko`)

### 1.2 Enable Vertex AI API

1. In GCP Console, go to **APIs & Services > Library**
2. Search for **"Vertex AI API"**
3. Click **"Enable"**
4. Also enable **"Cloud AI Platform API"** if prompted

### 1.3 Choose a Region

Select a region for your Vertex AI resources:
- **us-central1** (recommended, best availability)
- **us-east1**
- **europe-west1**
- **asia-northeast1**

**Note**: Make sure Gemini models are available in your chosen region.

---

## Step 2: Install Google Cloud SDK

### 2.1 Install gcloud CLI

**Windows**:
1. Download: https://cloud.google.com/sdk/docs/install
2. Run the installer
3. Follow the installation prompts

**Mac/Linux**:
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### 2.2 Initialize and Authenticate

```bash
# Initialize gcloud
gcloud init

# Login to your Google account
gcloud auth login

# Set up application default credentials
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

**Example**:
```bash
gcloud config set project cs224v-yundamko
```

---

## Step 3: Install Required Python Packages

Update your `requirements.txt` to include Vertex AI packages:

```bash
pip install google-cloud-aiplatform
pip install vertexai
```

Or add to `requirements.txt`:
```
google-cloud-aiplatform>=1.38.0
vertexai>=1.38.0
```

---

## Step 4: Configure Your Project

### 4.1 Update llm_config.yaml

The `llm_config.yaml` file is already configured for Vertex AI. Update the project ID and location:

```yaml
llm_endpoints:
  - vertex_project: VERTEX_PROJECT_ID     # Your GCP project ID
    vertex_location: VERTEX_LOCATION      # GCP region
    engine_map:
      gemini-flash: vertex_ai/gemini-2.0-flash-exp
      gemini-pro: vertex_ai/gemini-1.5-pro-002
      gemini-flash-lite: vertex_ai/publishers/google/models/gemini-2.5-flash-lite
```

### 4.2 Create API_KEYS File

1. Copy the template:
   ```bash
   copy API_KEYS_TEMPLATE API_KEYS
   ```
   (On Mac/Linux: `cp API_KEYS_TEMPLATE API_KEYS`)

2. The file is already pre-filled with your project info:
   ```
   VERTEX_PROJECT_ID=cs224v-yundamko
   VERTEX_LOCATION=us-central1
   ```

3. Update if needed with your actual values

**Important**: Don't commit `API_KEYS` to git! It's already in `.gitignore`.

---

## Step 5: Test Your Setup

### 5.1 Quick Test with test_gemini.py

Your `test_gemini.py` already works! Run it to verify:

```bash
python test_gemini.py
```

You should see a response from Gemini about using VS Code with Google Cloud.

### 5.2 Test with Brick Agent

Create a simple test script (`test_gemini_agent.py`):

```python
from brick_agent import BrickAgent

# Initialize agent with Gemini
agent = BrickAgent(engine="gemini-flash")

# Load your data
agent.initialize_graph(
    ttl_file="LBNL_FDD_Data_Sets_FCU_ttl.ttl"
)

# Test with a simple question
question = "What sensors are available?"
state, sparql = agent.run(question, verbose=True)

print("\nSuccess! Gemini is working with Brick Agent.")
```

Run it:
```bash
python test_gemini_agent.py
```

If you see LLM-generated responses (not mock mode), you're all set!

---

## Available Gemini Models

Your project is configured with three Gemini models:

### 1. gemini-flash (Default)
- **Model**: `gemini-2.0-flash-exp`
- **Use case**: Fast responses, good for most queries
- **Speed**: Fastest
- **Cost**: Lowest
- **Context**: 32K tokens

### 2. gemini-pro
- **Model**: `gemini-1.5-pro-002`
- **Use case**: Complex reasoning, longer context
- **Speed**: Moderate
- **Cost**: Higher
- **Context**: 1M tokens

### 3. gemini-flash-lite
- **Model**: `publishers/google/models/gemini-2.5-flash-lite`
- **Use case**: Ultra-fast, simple queries
- **Speed**: Fastest
- **Cost**: Lowest
- **Context**: Limited

**To change models**, just pass the engine name:
```python
agent = BrickAgent(engine="gemini-pro")  # Use Pro model
```

---

## Step 6: Monitor Usage and Costs

### 6.1 Monitor Usage

1. Go to **Google Cloud Console**
2. Navigate to **Vertex AI > Dashboard**
3. Check **"Model Metrics"** for API calls and token usage

### 6.2 View Billing

1. Go to **Billing > Reports**
2. Filter by **"Vertex AI"** service
3. Monitor costs by model and region

### 6.3 Gemini Pricing (as of 2025)

**Gemini Flash**:
- Input: ~$0.075 per 1M tokens
- Output: ~$0.30 per 1M tokens

**Gemini Pro**:
- Input: ~$1.25 per 1M tokens
- Output: ~$5.00 per 1M tokens

**Typical Query Cost**:
- Simple question with Gemini Flash: $0.001 - $0.01
- Complex question with Gemini Pro: $0.02 - $0.10

**Much cheaper than OpenAI GPT-4!** Your Google Cloud credits should last a long time.

---

## Troubleshooting

### Error: "Authentication failed" or "Default credentials not found"

**Solution**:
```bash
# Re-authenticate
gcloud auth application-default login

# Verify credentials exist
ls ~/.config/gcloud/application_default_credentials.json  # Mac/Linux
dir %APPDATA%\gcloud\application_default_credentials.json  # Windows
```

### Error: "Vertex AI API not enabled"

**Solution**:
```bash
# Enable Vertex AI API via command line
gcloud services enable aiplatform.googleapis.com

# Or enable in GCP Console:
# APIs & Services > Library > Search "Vertex AI" > Enable
```

### Error: "Permission denied" or "403 Forbidden"

**Solution**:
1. Go to **IAM & Admin > IAM** in GCP Console
2. Find your user account
3. Add role: **Vertex AI User** or **Vertex AI Administrator**

### Error: "Model not found" or "Region not supported"

**Solution**:
1. Check model availability: https://cloud.google.com/vertex-ai/docs/generative-ai/learn/models
2. Try a different region (e.g., switch from `europe-west1` to `us-central1`)
3. Update `VERTEX_LOCATION` in your `API_KEYS` file

### Error: "Quota exceeded"

**Solution**:
1. Go to **IAM & Admin > Quotas** in GCP Console
2. Search for "Vertex AI"
3. Request quota increase if needed

### Chainlite not recognizing Vertex AI config

**Check**:
1. `llm_config.yaml` has correct YAML syntax (indentation matters!)
2. Environment variables are loaded from `API_KEYS` file
3. Try setting verbose mode: `litellm_set_verbose: true` in `llm_config.yaml`

---

## Next Steps

Once Gemini is working:

1. **Test with real questions** from your building data
2. **Monitor costs** in GCP Console
3. **Experiment with models**: Try `gemini-pro` for complex queries
4. **Optimize prompts** based on Gemini's strengths
5. **Check quota usage** to avoid interruptions

---

## Comparison: Gemini vs OpenAI

| Feature | Gemini Flash | GPT-4o |
|---------|--------------|--------|
| **Cost (Input)** | $0.075 / 1M tokens | $2.50 / 1M tokens |
| **Cost (Output)** | $0.30 / 1M tokens | $10 / 1M tokens |
| **Speed** | Very Fast | Fast |
| **Context Window** | 32K tokens | 128K tokens |
| **Multimodal** | Yes | Yes |
| **Best For** | Cost-effective, fast queries | Complex reasoning |

**Gemini is ~30x cheaper than GPT-4o!** Perfect for development and testing.

---

## Additional Resources

- **Vertex AI Documentation**: https://cloud.google.com/vertex-ai/docs
- **Gemini API Docs**: https://cloud.google.com/vertex-ai/docs/generative-ai/learn/models
- **LiteLLM Vertex AI Docs**: https://docs.litellm.ai/docs/providers/vertex
- **GCP Console**: https://console.cloud.google.com
- **Vertex AI Pricing**: https://cloud.google.com/vertex-ai/pricing

---

## Quick Reference

**Files to configure**:
- `llm_config.yaml` - Vertex AI endpoint configuration
- `API_KEYS` - Your GCP project ID and region (copy from API_KEYS_TEMPLATE)

**What you need**:
- GCP Project ID (e.g., `cs224v-yundamko`)
- Region (e.g., `us-central1`)
- Google Cloud authentication (`gcloud auth application-default login`)

**Test commands**:
```bash
# Test Vertex AI directly
python test_gemini.py

# Test with Brick Agent
python test_brick_agent.py
```

**Switch models**:
```python
# Fast and cheap (default)
agent = BrickAgent(engine="gemini-flash")

# Best for complex queries
agent = BrickAgent(engine="gemini-pro")

# Ultra-fast for simple queries
agent = BrickAgent(engine="gemini-flash-lite")
```
