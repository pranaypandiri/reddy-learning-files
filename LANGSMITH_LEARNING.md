# LangSmith Learning Summary

## What is LangSmith?

**LangSmith = Observability & Testing Tool for LLM Applications**

- Built by LangChain company
- Automatically tracks all LLM calls, agents, and tools
- Zero code changes needed - just set environment variables
- Beautiful UI dashboard for debugging and monitoring

---

## Setup (Completed ✅)

### 1. Account Created
- Signed up at: https://smith.langchain.com/
- Used Gmail account
- Region: US Central
- Tier: Free (5,000 traces/month)

### 2. API Key Generated
```
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
```

### 3. Basic Test Completed ✅
- Created `test_langsmith.py`
- Ran simple LLM call
- Saw first trace in dashboard:
  - Latency: 1.87s
  - Tokens: 21
  - Cost: $0.00087

---

## Key Concepts

### What is a Trace?
**Trace = Complete record of ONE execution/conversation flow**

Example trace includes:
- All LLM calls (prompts + responses)
- All tool executions
- Timing breakdown (latency per step)
- Token usage per call
- Total cost
- Success/failure status
- Full conversation history

**One user interaction = One trace** (even if it involves multiple LLM calls internally)

---

## Free Tier Details

**Limits:**
- 5,000 traces/month
- 14 days retention
- Basic dashboards
- Manual evaluations

**Sufficient for:**
- ✅ Learning and development
- ✅ Resume projects
- ✅ Small POCs
- ✅ A/B testing experiments
- ✅ Dataset testing (hundreds of tests)

**When to upgrade ($39/month Plus tier):**
- Production with >5,000 traces/month
- Need 90 days retention
- Team collaboration
- Automated evaluations

---

## What We'll Test (3 Experiments)

### Test 1: A/B Testing (2 Different Prompts)
**Goal:** Compare two prompt strategies to see which performs better

**Method:**
```python
# Prompt A: Detailed instructions
os.environ["LANGCHAIN_PROJECT"] = "Prompt-A-Detailed"
system_prompt_a = "You are an IT support agent. Provide detailed step-by-step solutions."

# Prompt B: Concise instructions  
os.environ["LANGCHAIN_PROJECT"] = "Prompt-B-Concise"
system_prompt_b = "You are an IT support agent. Be extremely concise, max 3 bullet points."

# Test same inputs with both prompts
# Compare results in LangSmith UI
```

**What to compare:**
- Response quality
- Token usage (cost)
- Latency (speed)
- User preference

**Traces used:** ~10 traces (well under free tier)

---

### Test 2: Dataset Testing (5 Test Cases)
**Goal:** Run multiple test scenarios through the agent

**Method:**
```python
test_cases = [
    "My VPN is not connecting",
    "Laptop screen is broken", 
    "Forgot my password",
    "Email not syncing",
    "Slow computer performance"
]

for case in test_cases:
    response = agent.invoke(case)
    # Each creates one trace in LangSmith
```

**What to check:**
- Success rate across all cases
- Average latency
- Token usage per case
- Which cases fail and why

**Traces used:** 5 traces

---

### Test 3: Conversational Agent Flow
**Goal:** Test multi-turn conversations (realistic user behavior)

**Method:**
```python
# Full conversation = ONE trace with multiple sub-steps
config = {"configurable": {"thread_id": "test-conversation-1"}}

# Turn 1
app.invoke({"messages": [("user", "My VPN is not working")]}, config)

# Turn 2  
app.invoke({"messages": [("user", "Yes, I restarted it")]}, config)

# Turn 3
app.invoke({"messages": [("user", "It worked!")]}, config)

# LangSmith shows full conversation flow in ONE trace
```

**What you'll see:**
- Full conversation trace
- Each agent node execution (category, search, solution, etc.)
- Timing for each step
- How state flows through the graph
- Total cost for entire conversation

**Traces used:** 1 trace per conversation (maybe 5 conversations = 5 traces)

---

## Important: Semantic Evaluation Problem

### The Challenge:
LLMs are non-deterministic - same prompt can give different (but correct) answers!

**Example:**
```
Expected: "Check your VPN credentials in Settings"
Actual:   "Please verify your VPN login details in the Settings menu"

❌ Exact match = FAIL
✅ Semantically = SAME MEANING!
```

### Solution: Custom Evaluators

#### **Method 1: Keyword-Based (Simple)**
```python
def check_vpn_solution(run, example):
    output = run.outputs["answer"].lower()
    
    # Check if mentions key concepts
    has_credentials = "credential" in output or "login" in output
    has_restart = "restart" in output or "reboot" in output
    
    passed = has_credentials or has_restart
    
    return {
        "key": "vpn_solution_check",
        "score": 1 if passed else 0,
        "comment": f"Credentials: {has_credentials}, Restart: {has_restart}"
    }
```

#### **Method 2: Semantic Similarity (Better)**
```python
from langchain_openai import OpenAIEmbeddings
from numpy import dot
from numpy.linalg import norm

def semantic_similarity_evaluator(run, example):
    expected = example.outputs["answer"]
    actual = run.outputs["answer"]
    
    # Get embeddings
    expected_emb = embeddings.embed_query(expected)
    actual_emb = embeddings.embed_query(actual)
    
    # Calculate cosine similarity
    similarity = dot(expected_emb, actual_emb) / (norm(expected_emb) * norm(actual_emb))
    
    # Pass if >80% similar
    passed = similarity > 0.8
    
    return {
        "key": "semantic_similarity",
        "score": similarity,
        "comment": f"Similarity: {similarity:.2%}"
    }
```

**Example Result:**
```
Expected: "Check VPN credentials"
Actual:   "Verify your VPN login details"
Similarity: 92% ✅ PASS!
```

#### **Method 3: LLM-as-Judge (Best for Complex Cases)**
```python
def llm_judge_evaluator(run, example):
    expected = example.outputs["answer"]
    actual = run.outputs["answer"]
    
    judgment_prompt = f"""
    You are evaluating an IT support agent's response.
    
    Expected type of answer: {expected}
    Actual agent response: {actual}
    
    Does the actual response correctly address the expected solution?
    Answer: [PASS/FAIL/PARTIAL] - Explanation
    """
    
    judgment = judge_llm.invoke(judgment_prompt).content
    
    passed = "PASS" in judgment.upper()
    score = 1 if passed else (0.5 if "PARTIAL" in judgment.upper() else 0)
    
    return {
        "key": "llm_judge",
        "score": score,
        "comment": judgment
    }
```

**Example Result:**
```
Expected: "Reset password via email link"
Actual:   "You can recover your password by clicking the reset link sent to your email"

LLM Judge: "PASS - Both responses correctly explain password reset via email"
✅ Score: 1.0
```

---

## Best Practice: Combine Multiple Evaluators

```python
evaluators = [
    semantic_similarity_evaluator,  # Check if meaning is similar
    llm_judge_evaluator,            # Check if solution is correct
    custom_keyword_evaluator        # Check if contains required info
]

# LangSmith runs ALL 3 and shows individual scores
evaluate(
    lambda inputs: your_agent.invoke(inputs),
    data="IT-Support-Dataset",
    evaluators=evaluators
)
```

**LangSmith UI shows:**
- ✅ Semantic Similarity: 0.92
- ✅ LLM Judge: PASS
- ✅ Keyword Check: PASS
- **Overall: PASS**

---

## Total Trace Usage for All Tests

**Planned experiments:**
1. A/B Testing: ~10 traces
2. Dataset Testing: 5 traces
3. Conversational Testing: 5 traces
4. Multiple runs for validation: ~20 traces

**Total: ~40 traces** (out of 5,000 free tier) ✅

**Plenty of room for experimentation!**

---

## Next Steps (To Implement)

### 1. Create A/B Testing Script
- Test 2 different system prompts
- Same 5 inputs for each
- Compare in LangSmith dashboard

### 2. Create Dataset Testing Script
- 5 IT support scenarios
- Run through agent
- Check success rate

### 3. Create Conversational Testing Script
- Multi-turn conversation
- See full agent flow in trace
- Validate state management

### 4. Add Custom Evaluators
- Semantic similarity for flexible matching
- LLM-as-judge for quality assessment

---

## LangSmith vs Cloud Logging

| Feature | LangSmith | Cloud Logging |
|---------|-----------|---------------|
| **Setup** | 2 env vars ✅ | Custom callbacks ❌ |
| **UI** | Beautiful, AI-focused ✅ | Generic logs ❌ |
| **Tracing** | Auto-trace LLM chains ✅ | Manual ❌ |
| **Free tier** | 5K traces ✅ | Unlimited (GCP quotas) ✅ |
| **Production scale** | Paid after 5K ❌ | Free (mostly) ✅ |
| **LLM debugging** | Excellent ✅ | Basic ⚠️ |
| **Best for** | Development ✅ | Production (GCP) ✅ |

**Recommendation:**
- **Development/Learning:** Use LangSmith (best UX, easy debugging)
- **Production (GCP):** Use Cloud Logging (unlimited, integrated)
- **Or both:** LangSmith for LLM traces + Cloud Logging for infrastructure

---

## Resume Impact

**Can now claim:**
- ✅ "Implemented LangSmith for LLM observability and performance monitoring"
- ✅ "Conducted A/B testing of prompt strategies with automated evaluation"
- ✅ "Built comprehensive test suites with semantic similarity validation"
- ✅ "Monitored token usage and cost optimization across agent workflows"
- ✅ "Tracked multi-agent system performance with distributed tracing"

**Fills the gap in job description requirements!**

---

## Key Takeaways

1. **LangSmith = Flight Recorder for AI Agents**
   - See everything that happens
   - Debug when things break
   - Optimize performance and cost

2. **Zero Code Changes**
   - Just set 3 environment variables
   - Works with existing code

3. **Free Tier is Generous**
   - 5,000 traces = months of testing
   - Perfect for learning and portfolio projects

4. **Semantic Evaluation is Critical**
   - LLMs don't give exact same answers
   - Use embeddings or LLM-as-judge for validation
   - Don't rely on exact string matching

5. **Production Benefits**
   - Instant debugging when users report issues
   - Track performance degradation
   - Cost monitoring in real-time
   - A/B test different prompts
   - Quality metrics dashboard

---

## Resources

- **Dashboard:** https://smith.langchain.com/
- **API Key:** `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`
- **Project Name:** Set via `LANGCHAIN_PROJECT` env var
- **Test File:** `test_langsmith.py` (basic test completed ✅)
