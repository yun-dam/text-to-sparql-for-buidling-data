# Git Commit Guide for Today's Work

## Files to COMMIT ✅

### Core Framework Files (NEW)
```bash
git add brick_agent.py
git add brick_utils.py
git add test_brick_agent.py
```

### Documentation Files (NEW)
```bash
git add BRICK_README.md
git add SETUP_API_KEYS.md
git add RENAMING_SUMMARY.md
git add GIT_COMMIT_GUIDE.md
```

### Configuration Files (NEW)
```bash
git add .gitignore
git add requirements.txt
git add llm_config.yaml
git add llm_config_examples.yaml
git add API_KEYS_TEMPLATE
```

### Prompt Templates (NEW)
```bash
git add prompts/
```

### Modified Files
```bash
git add query_brick_data.py
git add query_brick_with_timeseries.py
```

## Files to NOT COMMIT ❌

### Sensitive Files (Already in .gitignore)
- `API_KEYS` - **NEVER commit this! Contains your API keys**
- `*.key`, `*.secret`

### Build/Cache Files
- `__pycache__/` - Python cache
- `*.pyc`, `*.pyo`
- `nul` - Stray file

### Log Files
- `prompt_logs.jsonl` - LLM logs
- `*.log`

### Large Data Files (Your Choice)
Consider if you want to commit these:
- `LBNL_FDD_Dataset_FCU/` - Large dataset directory
- `LBNL_FDD_Data_Sets_FCU_ttl.ttl` - TTL schema
- `"Inventory of LBNL FDD Data Sets_FCU.pdf"` - PDF documentation
- `semantic_parser.txt`, `semantic_parser_vs0.txt` - Scratch files?

**Decision**: If these are example/reference data, commit them. If they're large (>100MB) or regenerable, don't commit.

### External Libraries
- `spinach/` - The original SPINACH repository
  - **Recommendation**: Don't commit. Users can clone it separately if needed.
  - Already in your directory structure but massive (adds MB to repo)

## Quick Commit Commands

### Option 1: Commit Core Framework Only (Recommended)
```bash
# Add framework files
git add brick_agent.py brick_utils.py test_brick_agent.py
git add BRICK_README.md SETUP_API_KEYS.md RENAMING_SUMMARY.md GIT_COMMIT_GUIDE.md
git add .gitignore requirements.txt llm_config.yaml llm_config_examples.yaml API_KEYS_TEMPLATE
git add prompts/
git add query_brick_data.py query_brick_with_timeseries.py

# Commit
git commit -m "Add Brick Agent framework for text-to-SPARQL conversion

- Created iterative agent for Brick Schema SPARQL generation
- Implemented part-to-whole query building approach
- Added comprehensive test suite
- Included Brick-specific prompts and examples
- Full documentation and setup guides"

# Push
git push origin main
```

### Option 2: Include Example Data
```bash
# Do Option 1 commands first, then:
git add LBNL_FDD_Data_Sets_FCU_ttl.ttl
git add "Inventory of LBNL FDD Data Sets_FCU.pdf"
# Note: Skip LBNL_FDD_Dataset_FCU/ if it's too large

git commit --amend -m "Add Brick Agent framework with example data

- Created iterative agent for Brick Schema SPARQL generation
- Implemented part-to-whole query building approach
- Added comprehensive test suite
- Included Brick-specific prompts and examples
- Full documentation and setup guides
- Included LBNL FCU example data for testing"

git push origin main
```

## Verify Before Pushing

### Check what will be committed:
```bash
git status
git diff --cached  # Shows changes to be committed
```

### Check file sizes:
```bash
du -sh LBNL_FDD_Dataset_FCU/  # Check if too large
```

### Verify API_KEYS is ignored:
```bash
git status | grep API_KEYS
# Should show "API_KEYS" under "Untracked files" if not in .gitignore
# Should NOT show it at all if properly ignored
```

## Post-Commit Checklist

After pushing:
- ✅ Verify API_KEYS was NOT pushed (check GitHub/remote)
- ✅ Check that .gitignore is working
- ✅ Verify all framework files are present
- ✅ Test clone: `git clone <your-repo>` in a new directory
- ✅ Run tests: `python test_brick_agent.py`

## If You Accidentally Committed API_KEYS

**URGENT**: If API_KEYS got committed:

```bash
# Remove from git but keep local file
git rm --cached API_KEYS

# Commit the removal
git commit -m "Remove API_KEYS from repository"

# Force push (if already pushed to remote)
git push origin main --force

# IMPORTANT: Rotate your API keys immediately!
# Go to OpenAI/Anthropic and create new keys
```

## Summary of Today's Work

**New Framework**: Brick Agent for text-to-SPARQL conversion
**Files Created**: 15+ new files
**Lines of Code**: ~1500+ lines
**Key Features**:
- Iterative SPARQL query building
- Brick Schema integration
- LLM-powered reasoning
- Comprehensive test suite
- Full documentation

**Commit Message Suggestion**:
```
Add Brick Agent framework for building data SPARQL generation

Major additions:
- brick_agent.py: Main agent with iterative query building
- brick_utils.py: Brick-specific utilities and graph management
- test_brick_agent.py: Comprehensive test suite
- Prompts: Brick-specific few-shot examples
- Documentation: Complete setup and usage guides

Features:
- Part-to-whole SPARQL construction
- Action-observation reasoning loop
- Mock mode for testing without API keys
- Integration with GPT-4o/Claude
- Support for timeseries data

Tested with LBNL FCU dataset
```
