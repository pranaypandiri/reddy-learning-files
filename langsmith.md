## **LangSmith Learning Plan - Summary**

---

### **What We Covered:**

1. **LangSmith Basics**
   - Free tier: 5,000 traces/month
   - Setup: 3 environment variables (LANGCHAIN_TRACING_V2, LANGCHAIN_API_KEY, LANGCHAIN_PROJECT)
   - Automatic tracing - zero code changes needed
   - Dashboard shows: latency, tokens, cost, success/fail

2. **What is a Trace?**
   - Complete record of one execution
   - Shows all LLM calls, tool executions, timing, costs
   - Like a "receipt" for each conversation

3. **Testing Approaches**
   - **A/B Testing**: Test 2 different prompts, compare performance
   - **Dataset Testing**: Run 5 test cases through LLM
   - **Conversational Agent**: Test multi-turn conversations with LangGraph

4. **Evaluation Problem**
   - Exact match doesn't work for LLMs (different wording, same meaning)
   - Solutions:
     - Keyword-based evaluator (simple)
     - Semantic similarity (embeddings)
     - LLM-as-judge (best for complex cases)

---

### **What We'll Implement:**

#### **Test 1: A/B Testing**
- 2 different system prompts (detailed vs concise)
- Same 5 test inputs
- Compare in LangSmith which performs better

#### **Test 2: Dataset Testing**
- 5 IT support test cases
- Run through agent
- See all traces in dashboard

#### **Test 3: Conversational Agent**
- Multi-turn conversation (3-4 turns)
- Test with your LangGraph IT support agent
- See full conversation flow in one trace

#### **Test 4: Custom Evaluator**
- Semantic similarity or LLM-as-judge
- Handle "similar but different wording" responses
- Show pass/fail based on meaning, not exact match

---

### **Files to Create:**

1. `test_ab_prompts.py` - A/B testing with 2 prompts
2. `test_dataset.py` - 5 test cases
3. `test_conversation.py` - Multi-turn chat
4. `test_evaluator.py` - Custom semantic evaluator

---

**Enjoy dinner! When you're back, we'll build these one by one!** 🍽️