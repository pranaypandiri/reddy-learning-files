# LangGraph Cheat Sheet

## Essential Imports
```python
from langchain_google_vertexai import ChatVertexAI
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Literal
import operator
```

---

## 1. LLM Setup
```python
llm = ChatVertexAI(
    model="gemini-2.0-flash-exp",
    project="ai-practice-388514",
    location="us-central1",
    temperature=0.3
)
```

---

## 2. Define Tools
```python
@tool
def my_tool(param: str) -> str:
    """Tool description - LLM reads this to decide when to use it"""
    return "result"
```

**Key points:**
- `@tool` decorator auto-extracts name from function name
- Docstring = tool description (required!)
- Type hints help LLM understand parameters

---

## 3. Create Agents
```python
agent = create_react_agent(
    model=llm,           # NOT llm= (old API)
    tools=[tool1, tool2],
    prompt=SystemMessage(content="Agent instructions")  # NOT state_modifier= (old API)
)
```

**Remember:** `model=` and `prompt=` (new API in LangGraph 0.6+)

---

## 4. Define State
```python
class MyState(TypedDict):
    input: str
    output: str
    messages: Annotated[list, operator.add]  # Accumulates messages
```

**State management:**
- `Annotated[list, operator.add]` → appends to list
- Without `operator.add` → replaces value
- State = shared whiteboard between agents

---

## 5. Create Workflow Nodes
```python
def my_node(state: MyState):
    result = agent.invoke({
        "messages": [HumanMessage(content=f"Process: {state['input']}")]
    })
    
    # Extract from messages
    output = ""
    for msg in result["messages"]:
        if "ToolMessage" in msg.__class__.__name__:
            output = msg.content
    
    return {"output": output, "messages": result["messages"]}
```

**Key points:**
- Use `agent.invoke()` NOT `agent.run()`
- Input must be `{"messages": [...]}`
- Result is dict with `result["messages"]`
- Return dict automatically merges into state

---

## 6. Build Graph

### Sequential Flow
```python
workflow = StateGraph(MyState)
workflow.add_node("node1", node1_function)
workflow.add_node("node2", node2_function)

workflow.set_entry_point("node1")      # Start here
workflow.add_edge("node1", "node2")    # node1 → node2
workflow.add_edge("node2", END)        # node2 → END

graph = workflow.compile()
```

### Conditional Flow
```python
def route_function(state: MyState) -> Literal["path_a", "path_b"]:
    if state["condition"] == "A":
        return "path_a"
    return "path_b"

workflow.add_conditional_edges(
    "classifier",                              # FROM this node
    route_function,                            # Decision function
    {"path_a": "node_a", "path_b": "node_b"}  # Map return → node
)
```

### Router Flow (conditional entry)
```python
def determine_start(state: MyState) -> Literal["billing", "technical"]:
    if state["query_type"] == "billing":
        return "billing"
    return "technical"

workflow.set_conditional_entry_point(
    determine_start,
    {"billing": "billing_node", "technical": "tech_node"}
)
```

### Parallel Flow
```python
workflow.set_entry_point("task1")  # Both start simultaneously
workflow.set_entry_point("task2")
workflow.add_edge("task1", "merger")
workflow.add_edge("task2", "merger")
workflow.add_edge("merger", END)
```

---

## 7. Run Graph
```python
result = graph.invoke({
    "input": "user query",
    "output": "",
    "messages": []
})

print(result["output"])
```

**Remember:** `graph.invoke()` NOT `graph.run()`

---

## 8. Visualize Graph
```python
png_bytes = graph.get_graph().draw_mermaid_png()
with open("graph.png", "wb") as f:
    f.write(png_bytes)
```

---

## Flow Pattern Comparison

| Pattern | When to Use | Entry Point | Routing |
|---------|-------------|-------------|---------|
| **Sequential** | Linear steps (A → B → C) | `set_entry_point()` | `add_edge()` |
| **Conditional** | Decision after processing | `set_entry_point()` | `add_conditional_edges()` |
| **Router** | Decision from initial input | `set_conditional_entry_point()` | No edges before routing |
| **Parallel** | Run tasks simultaneously | Multiple `set_entry_point()` | Merge at end |

---

## Common Mistakes ❌ → ✅

| Wrong ❌ | Correct ✅ |
|---------|----------|
| `llm=llm` | `model=llm` |
| `state_modifier=` | `prompt=` |
| `agent.run()` | `agent.invoke()` |
| `graph.run()` | `graph.invoke()` |
| `add_entry_point()` | `set_entry_point()` |
| `add_edges()` (plural) | `add_edge()` (singular) |
| `result.content` | `result["messages"]` |
| `Annotated[list]` | `Annotated[list, operator.add]` |

---

## Message Types

```python
# Input to agent
HumanMessage(content="user input")

# Agent thinking
AIMessage(content="agent response")

# Tool execution result
ToolMessage(content="tool output", tool_call_id="...")
```

**Extract tool output:**
```python
for msg in result["messages"]:
    if "ToolMessage" in msg.__class__.__name__:
        output = msg.content
```

---

## Type Hints

### Literal (for routing)
```python
def route(state) -> Literal["option_a", "option_b"]:
    return "option_a"  # Must match one of the literals
```

**Purpose:** Type safety + LangGraph validates return matches node mapping

---

## State Updates

When node returns dict:
```python
return {"field1": value1, "field2": value2}
```

LangGraph **automatically merges** into state:
- Normal fields → **replace** value
- `Annotated[list, operator.add]` fields → **append** to list

---

## Quick Template

```python
# 1. Define tools
@tool
def my_tool(input: str) -> str:
    """What the tool does"""
    return "result"

# 2. Create agent
agent = create_react_agent(
    model=llm,
    tools=[my_tool],
    prompt=SystemMessage(content="Instructions")
)

# 3. Define state
class State(TypedDict):
    input: str
    output: str
    messages: Annotated[list, operator.add]

# 4. Create node
def my_node(state: State):
    result = agent.invoke({"messages": [HumanMessage(content=state['input'])]})
    return {"output": "extracted", "messages": result["messages"]}

# 5. Build graph
workflow = StateGraph(State)
workflow.add_node("node", my_node)
workflow.set_entry_point("node")
workflow.add_edge("node", END)
graph = workflow.compile()

# 6. Run
result = graph.invoke({"input": "test", "output": "", "messages": []})
print(result["output"])
```

---

## Debugging Tips

1. **Print messages to see flow:**
```python
for msg in result["messages"]:
    print(f"{msg.__class__.__name__}: {msg.content}")
```

2. **Check state at each step:**
```python
def debug_node(state):
    print(f"Current state: {state}")
    return {}
```

3. **Visualize graph first:**
```python
png = graph.get_graph().draw_mermaid_png()
# Check if flow matches your intention
```

---

## Next Steps

1. ✅ Understand these basics
2. ✅ Practice with simple 2-agent workflows
3. → Implement Agent 1 tools (categorize, create_ticket, save_session, load_session)
4. → Setup SQLite database
5. → Build Agent 2 (KB RAG with FAISS)
6. → Connect all agents in multi-agent orchestration
7. → Add Streamlit UI

---

**Remember:** Focus on understanding patterns, not memorizing package names!


# 1. After interrupt, store case in DB
case_id = save_pending_review(result["draft_response"], config["configurable"]["thread_id"])

# 2. Send notification to supervisor (Slack/Email/UI)
notify_supervisor(case_id, result["draft_response"])

# 3. Supervisor clicks Approve/Reject in UI → calls your API

# 4. Your API endpoint:
@app.post("/review/{case_id}")
def handle_review(case_id: str, decision: str):  # decision = "yes" or "no"
    thread_id = get_thread_id(case_id)
    config = {"configurable": {"thread_id": thread_id}}
    
    # Update and resume
    graph.update_state(config, {"human_decision": decision})
    final = graph.invoke(None, config)
    
    return {"status": "completed", "result": final["final_response"]}