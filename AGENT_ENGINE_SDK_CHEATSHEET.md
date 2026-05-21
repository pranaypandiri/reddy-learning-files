# Agent Engine SDK Production Cheatsheet

## 1. Agent Deployment Patterns

### Basic Deployment
```python
from google.cloud.aiplatform import agent_engines

agent = agent_engines.LanggraphAgent(
    model="gemini-1.5-pro",
    runnable_builder=runnable_builder,           # Your graph logic
    checkpointer_builder=checkpointer_builder,   # Session memory
    project="your-project",
    location="us-central1"
)

# Deploy with auto-scaling
response = agent.create(
    min_replica_count=1,      # Always-on instances
    max_replica_count=10      # Scale up under load
)

AGENT_ID = response.name
print(f"Deployed: {AGENT_ID}")
```

### Use Deployed Agent (Production)
```python
# Get deployed agent
deployed_agent = agent_engines.LanggraphAgent.get(AGENT_ID)

# Query with session isolation
response = deployed_agent.query(
    query="User message here",
    config={
        "configurable": {
            "thread_id": f"user_{user_id}_session",  # Session isolation
            "user_id": user_id                        # For Memory Bank filtering
        }
    }
)
```

---


# Just point to file - SDK reads it automatically
shell_engine.update(
    reasoning_engine_object=agent,
    requirements_path="requirements.txt"  # SDK reads file
)

## 2. LangGraph Integration

### Why Builder Pattern?
**Problem**: Agent runs in remote container (sandbox for scaling)  
**Solution**: Builder functions serialize your code to remote environment

```python
def runnable_builder(**kwargs):
    # ⚠️ ALL IMPORTS MUST BE INSIDE BUILDER
    from langgraph.graph import StateGraph, MessagesState
    from langchain_google_vertexai import ChatVertexAI
    
    # Define state
    class AgentState(MessagesState):
        user_id: str
        recalled_memories: str
    
    # Define nodes
    def agent_node(state):
        model = ChatVertexAI(model="gemini-1.5-pro", temperature=0)
        response = model.invoke(state["messages"])
        return {"messages": [response]}
    
    # Build graph
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.set_entry_point("agent")
    graph.add_edge("agent", "__end__")
    
    # Compile with checkpointer
    return graph.compile(checkpointer=kwargs.get("checkpointer"))
```

### Key Rules:
- ✅ All imports inside builder
- ✅ All tools/functions defined inside builder
- ✅ Return compiled graph
- ❌ No external dependencies outside builder
- ❌ No global variables

---

## 3. Cloud SQL Checkpointer (Short-term Memory)

### Purpose: Session-level conversation memory

```python
def checkpointer_builder(**kwargs):
    from langgraph.checkpoint.postgres import PostgresSaver, PostgresEngine
    from sqlalchemy import create_engine
    
    # Cloud SQL connection via Unix socket
    DATABASE_URL = "postgresql+psycopg://user:pass@/db?host=/cloudsql/PROJECT:REGION:INSTANCE"
    
    engine = create_engine(DATABASE_URL)
    pg_engine = PostgresEngine.from_engine(engine)
    
    # Create checkpoint table (idempotent)
    pg_engine.init_checkpoint_table()
    
    return PostgresSaver.create_sync(pg_engine)
```

### How It Works:
- Same `thread_id` → Same conversation history
- Different `thread_id` → Fresh conversation
- Automatic state persistence on each node

---

## 4. Memory Bank (Long-term Memory)

### Purpose: Cross-session user facts, preferences, task state

### Step 1: Reserve Resource (Create Container)
```python
from google.cloud import aiplatform

aiplatform.init(project="your-project", location="us-central1")

# Create Memory Bank container
shell_engine = aiplatform.ReasoningEngine.create(
    display_name="my-agent-with-memory"
)

AGENT_RESOURCE_NAME = shell_engine.resource_name
```

### Step 2: Link Memory Bank to Agent
```python
from vertexai import agent_engines

agent = agent_engines.LanggraphAgent(
    model="gemini-1.5-pro",
    runnable_builder=runnable_builder,
    checkpointer_builder=checkpointer_builder,
    
    # LINK MEMORY BANK
    memory_config={
        "type": "vertex_ai_memory_bank",
        "memory_bank": AGENT_RESOURCE_NAME  # Physical storage location
    },
    
    project="your-project",
    location="us-central1"
)
```

### Step 3: Deploy to Resource
```python
shell_engine.update(
    reasoning_engine_object=agent,
    requirements=["google-cloud-aiplatform[langgraph]", "langgraph"]
)
```

### Step 4: Use Memory Bank in Runnable
```python
def runnable_builder(**kwargs):
    from google.cloud import aiplatform
    from langgraph.graph import StateGraph, MessagesState
    
    # Initialize client
    client = aiplatform.gapic.AgentEnginesServiceClient()
    AGENT_NAME = "projects/PROJECT/locations/REGION/agentEngines/AGENT_ID"
    
    # Memory recall node
    def recall_memories(state):
        user_id = state.get("user_id", "default")
        user_message = state["messages"][-1].content
        
        # SEMANTIC SEARCH (automatic similarity)
        memories = client.list_memories(
            parent=AGENT_NAME,
            filter=f'scope.user_id="{user_id}"',
            query=user_message  # Finds similar memories
        )
        
        memory_context = "\n".join([m.fact for m in memories[:3]])
        return {"recalled_memories": memory_context}
    
    # Memory storage node
    def store_memory(state):
        user_id = state.get("user_id", "default")
        last_response = state["messages"][-1].content
        
        # Extract facts (simple pattern)
        if "my favorite" in last_response.lower():
            client.create_memory(
                parent=AGENT_NAME,
                memory={
                    "scope": {"user_id": user_id},
                    "fact": last_response
                }
            )
        return state
    
    # Build graph with memory nodes
    graph = StateGraph(MessagesState)
    graph.add_node("recall", recall_memories)
    graph.add_node("agent", agent_node)
    graph.add_node("store", store_memory)
    
    graph.set_entry_point("recall")
    graph.add_edge("recall", "agent")
    graph.add_edge("agent", "store")
    graph.add_edge("store", "__end__")
    
    return graph.compile(checkpointer=kwargs.get("checkpointer"))
```

### What Memory Bank Stores:
- ✅ User facts: "User's name is John"
- ✅ Preferences: "User likes pizza"
- ✅ Task state: "Task: Report. Status: 50% complete. Next: Generate charts"
- ✅ Progress: "Workflow step 2 of 5 completed on Monday"
- ✅ Context: "User was analyzing Q1 sales data"

### Semantic Search Example:
```python
# MONDAY: Store
"My favorite food is pizza"

# WEDNESDAY: Query
"What meal do I like?"  # Words don't match!

# Result: FINDS "pizza" via semantic similarity ✅
```

---

## 5. Evaluation & Observability

### DeepEval (Agent Metrics)
```python
def runnable_builder(**kwargs):
    from deepeval.metrics import ToolCorrectnessMetric, AnswerRelevancyMetric
    from deepeval.integrations.langchain import DeepEvalCallbackHandler
    
    metrics = [
        ToolCorrectnessMetric(),
        AnswerRelevancyMetric(threshold=0.7)
    ]
    
    callback = DeepEvalCallbackHandler(metrics=metrics)
    
    def agent_node(state):
        model = ChatVertexAI(
            model="gemini-1.5-pro",
            callbacks=[callback]  # Real-time evaluation
        )
        response = model.invoke(state["messages"])
        return {"messages": [response]}
    
    # ... rest of graph
```

### LangSmith (Observability)
```python
def runnable_builder(**kwargs):
    import os
    
    # 3-line setup
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = "your-langsmith-key"
    os.environ["LANGCHAIN_PROJECT"] = "prod-agent"
    
    # Automatic tracing for all LangChain calls
    # ... rest of your code
```

### FastAPI Background Evaluation (Zero Latency)
```python
from fastapi import FastAPI, BackgroundTasks
from deepeval import evaluate
from deepeval.test_case import LLMTestCase

app = FastAPI()
deployed_agent = agent_engines.LanggraphAgent.get(AGENT_ID)

def evaluate_in_background(query, response):
    test_case = LLMTestCase(
        input=query,
        actual_output=response,
        retrieval_context=["context here"]
    )
    results = evaluate([test_case], metrics=[AnswerRelevancyMetric()])
    print(f"Quality Score: {results[0].score}")

@app.post("/chat")
async def chat(message: str, user_id: str, background_tasks: BackgroundTasks):
    response = deployed_agent.query(
        query=message,
        config={"configurable": {"thread_id": f"user_{user_id}"}}
    )
    
    # Evaluate AFTER response sent (no user wait)
    background_tasks.add_task(evaluate_in_background, message, response["output"])
    
    return {"response": response["output"]}
```

---

## 6. Production Patterns

### Multi-Tenant Isolation
```python
# Checkpointer isolation (session)
config = {"configurable": {"thread_id": f"tenant_{tenant_id}_user_{user_id}"}}

# Memory Bank isolation (long-term)
memories = client.list_memories(
    parent=AGENT_NAME,
    filter=f'scope.tenant_id="{tenant_id}" AND scope.user_id="{user_id}"'
)
```

### Secret Management
```python
def runnable_builder(**kwargs):
    from google.cloud import secretmanager
    
    client = secretmanager.SecretManagerServiceClient()
    secret_name = f"projects/PROJECT/secrets/API_KEY/versions/latest"
    response = client.access_secret_version(request={"name": secret_name})
    API_KEY = response.payload.data.decode("UTF-8")
    
    # Use API_KEY in tools
```

### Error Handling
```python
def agent_node(state):
    try:
        model = ChatVertexAI(model="gemini-1.5-pro")
        response = model.invoke(state["messages"])
        return {"messages": [response]}
    except Exception as e:
        error_msg = f"Agent error: {str(e)}"
        return {"messages": [error_msg], "error": True}
```

### Monitoring
```python
# Cloud Monitoring custom metrics
from google.cloud import monitoring_v3

client = monitoring_v3.MetricServiceClient()
series = monitoring_v3.TimeSeries()
series.metric.type = "custom.googleapis.com/agent/query_count"
# ... send metrics
```

---

## 7. Why Builder Pattern?

### The Problem:
- Agent needs to **scale horizontally** (multiple containers)
- Each container needs **same code logic**
- Cannot pickle/serialize external functions

### The Solution:
```
Your Code → Builder Function → Serialized → Remote Container
```

### What Happens:
1. You define `runnable_builder()` with **all code inside**
2. SDK serializes it to **cloud storage**
3. Remote container **downloads and executes** on startup
4. **Each replica** runs same code independently

### Why Imports Inside:
```python
# ❌ WRONG - External import can't serialize
from langchain_google_vertexai import ChatVertexAI

def runnable_builder(**kwargs):
    model = ChatVertexAI()  # Import not available in remote container!
```

```python
# ✅ CORRECT - Import inside builder
def runnable_builder(**kwargs):
    from langchain_google_vertexai import ChatVertexAI  # Available in sandbox
    model = ChatVertexAI()
```

### Runner in Sandbox:
- **Sandbox** = Isolated container environment
- **Runner** = LangGraph executor that runs your graph
- Each container has its own runner
- Scaling = More containers = More runners
- Builders ensure **all runners have same code**

---

## 8. Short-term vs Long-term Memory

| Feature | Checkpointer (Short-term) | Memory Bank (Long-term) |
|---------|---------------------------|-------------------------|
| **Scope** | Single conversation thread | Cross-session, cross-conversation |
| **Storage** | Cloud SQL Postgres | Vertex AI Memory Bank |
| **Key** | `thread_id` | `user_id` in scope |
| **Automatic** | ✅ Auto-saves state | ❌ Manual create_memory() |
| **Recall** | ✅ Auto-loads state | ❌ Manual list_memories() |
| **Use Case** | "What did I just say?" | "What's my favorite food from Monday?" |
| **TTL** | Delete old threads | Manual delete or scope filter |

### Example Flow:
```
Monday Session:
  User: "My name is John. I like pizza"
  → Checkpointer: Stores in thread_abc123
  → Memory Bank: Stores "User's name is John. Favorite food: pizza"

Tuesday Session (NEW thread):
  User: "What's my name?"
  → Checkpointer: Empty (new thread_xyz789)
  → Memory Bank: Recalls "User's name is John" ✅
```

---

## 9. Streaming Responses

### Why Streaming?
- Better UX: Users see response as it's generated
- Lower perceived latency
- Token-by-token display (like ChatGPT)

### Pattern 1: Agent SDK Stream
```python
deployed_agent = agent_engines.LanggraphAgent.get(AGENT_ID)

# Stream with .stream() method
for chunk in deployed_agent.stream(
    query="Tell me a story",
    config={"configurable": {"thread_id": "user_123"}}
):
    print(chunk, end="", flush=True)
```

### Pattern 2: FastAPI Server-Sent Events (SSE)
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json

app = FastAPI()
deployed_agent = agent_engines.LanggraphAgent.get(AGENT_ID)

@app.post("/chat/stream")
async def chat_stream(message: str, user_id: str):
    
    async def event_generator():
        """Generator for SSE stream"""
        try:
            # Stream from agent
            for chunk in deployed_agent.stream(
                query=message,
                config={"configurable": {"thread_id": f"user_{user_id}"}}
            ):
                # Format as SSE
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            
            # Send completion signal
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
```

### Pattern 3: Streaming in Runnable Builder
```python
def runnable_builder(**kwargs):
    from langgraph.graph import StateGraph, MessagesState
    from langchain_google_vertexai import ChatVertexAI
    
    def agent_node(state):
        model = ChatVertexAI(
            model="gemini-1.5-pro",
            streaming=True  # Enable streaming
        )
        
        # Stream tokens
        full_response = ""
        for chunk in model.stream(state["messages"]):
            full_response += chunk.content
            # Chunk automatically propagated by LangGraph
        
        return {"messages": [full_response]}
    
    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent_node)
    graph.set_entry_point("agent")
    graph.add_edge("agent", "__end__")
    
    return graph.compile(checkpointer=kwargs.get("checkpointer"))
```

### Pattern 4: WebSocket Streaming
```python
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            message = data["message"]
            user_id = data["user_id"]
            
            # Stream response
            for chunk in deployed_agent.stream(
                query=message,
                config={"configurable": {"thread_id": f"user_{user_id}"}}
            ):
                await websocket.send_json({"content": chunk})
            
            # Send completion
            await websocket.send_json({"done": True})
            
    except WebSocketDisconnect:
        print(f"Client disconnected")
```

### Frontend Integration (React Example)
```javascript
// SSE Client
const eventSource = new EventSource('/chat/stream');

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.done) {
        eventSource.close();
    } else if (data.content) {
        // Append token to UI
        document.getElementById('response').innerText += data.content;
    }
};

// WebSocket Client
const ws = new WebSocket('ws://localhost:8000/ws/chat');

ws.onopen = () => {
    ws.send(JSON.stringify({
        message: "Hello",
        user_id: "user_123"
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.content) {
        document.getElementById('response').innerText += data.content;
    }
};
```

### Streaming with Memory Bank
```python
@app.post("/chat/stream")
async def chat_stream_with_memory(message: str, user_id: str):
    
    async def event_generator():
        full_response = ""
        
        # Stream response
        for chunk in deployed_agent.stream(
            query=message,
            config={
                "configurable": {
                    "thread_id": f"user_{user_id}",
                    "user_id": user_id  # For Memory Bank filtering
                }
            }
        ):
            full_response += chunk
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        
        # Store in Memory Bank AFTER streaming completes
        if "my favorite" in full_response.lower():
            client = aiplatform.gapic.AgentEnginesServiceClient()
            client.create_memory(
                parent=AGENT_NAME,
                memory={"scope": {"user_id": user_id}, "fact": full_response}
            )
        
        yield f"data: {json.dumps({'done': True})}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

### Best Practices:
- ✅ Use SSE for simple one-way streaming
- ✅ Use WebSocket for bidirectional communication
- ✅ Add timeout handling for long responses
- ✅ Store to Memory Bank AFTER streaming completes
- ✅ Send completion signal to frontend
- ❌ Don't block on memory operations during streaming
- ❌ Don't forget CORS headers for SSE

### Error Handling in Streams
```python
async def event_generator():
    try:
        for chunk in deployed_agent.stream(query=message, config=config):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
    except TimeoutError:
        yield f"data: {json.dumps({'error': 'Response timeout'})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': f'Stream error: {str(e)}'})}\n\n"
    finally:
        yield f"data: {json.dumps({'done': True})}\n\n"
```

---

## 10. Complete Production Example

```python
from google.cloud import aiplatform
from google.cloud.aiplatform import agent_engines

# 1. RESERVE MEMORY BANK
aiplatform.init(project="your-project", location="us-central1")
shell_engine = aiplatform.ReasoningEngine.create(display_name="prod-agent")
AGENT_RESOURCE_NAME = shell_engine.resource_name

# 2. DEFINE CHECKPOINTER
def checkpointer_builder(**kwargs):
    from langgraph.checkpoint.postgres import PostgresSaver, PostgresEngine
    from sqlalchemy import create_engine
    DATABASE_URL = "postgresql+psycopg://user:pass@/db?host=/cloudsql/PROJECT:REGION:INSTANCE"
    engine = create_engine(DATABASE_URL)
    pg_engine = PostgresEngine.from_engine(engine)
    pg_engine.init_checkpoint_table()
    return PostgresSaver.create_sync(pg_engine)

# 3. DEFINE AGENT LOGIC
def runnable_builder(**kwargs):
    from langgraph.graph import StateGraph, MessagesState
    from langchain_google_vertexai import ChatVertexAI
    from google.cloud import aiplatform
    
    client = aiplatform.gapic.AgentEnginesServiceClient()
    AGENT_NAME = "projects/PROJECT/locations/REGION/agentEngines/AGENT_ID"
    
    def recall_node(state):
        memories = client.list_memories(
            parent=AGENT_NAME,
            filter=f'scope.user_id="{state.get("user_id")}"',
            query=state["messages"][-1].content
        )
        return {"recalled_memories": "\n".join([m.fact for m in memories[:3]])}
    
    def agent_node(state):
        context = state.get("recalled_memories", "")
        prompt = f"Context: {context}\n\nUser: {state['messages'][-1].content}"
        model = ChatVertexAI(model="gemini-1.5-pro", temperature=0)
        response = model.invoke([{"role": "user", "content": prompt}])
        return {"messages": [response]}
    
    def store_node(state):
        if "my" in state["messages"][-1].content.lower():
            client.create_memory(
                parent=AGENT_NAME,
                memory={"scope": {"user_id": state.get("user_id")}, "fact": state["messages"][-1].content}
            )
        return state
    
    graph = StateGraph(MessagesState)
    graph.add_node("recall", recall_node)
    graph.add_node("agent", agent_node)
    graph.add_node("store", store_node)
    graph.set_entry_point("recall")
    graph.add_edge("recall", "agent")
    graph.add_edge("agent", "store")
    graph.add_edge("store", "__end__")
    
    return graph.compile(checkpointer=kwargs.get("checkpointer"))

# 4. CREATE AGENT WITH MEMORY BANK
agent = agent_engines.LanggraphAgent(
    model="gemini-1.5-pro",
    runnable_builder=runnable_builder,
    checkpointer_builder=checkpointer_builder,
    memory_config={
        "type": "vertex_ai_memory_bank",
        "memory_bank": AGENT_RESOURCE_NAME
    },
    project="your-project",
    location="us-central1"
)

# 5. DEPLOY TO RESOURCE
shell_engine.update(
    reasoning_engine_object=agent,
    requirements=["google-cloud-aiplatform[langgraph]", "langgraph", "langchain-google-vertexai"]
)

print(f"✅ Production agent deployed: {AGENT_RESOURCE_NAME}")

# 6. USE IN FASTAPI
from fastapi import FastAPI
app = FastAPI()
deployed_agent = agent_engines.LanggraphAgent.get(AGENT_RESOURCE_NAME)

@app.post("/chat")
async def chat(message: str, user_id: str):
    response = deployed_agent.query(
        query=message,
        config={"configurable": {"thread_id": f"user_{user_id}", "user_id": user_id}}
    )
    return {"response": response["output"]}
```

---

## 11. Key Takeaways

### Agent Engine SDK vs ADK
- **Agent Engine SDK** = Production (LangGraph + scaling + checkpointer)
- **ADK** = Simpler wrapper (newer, less common)
- KPMG wants Agent Engine SDK

### Memory Architecture
- **Checkpointer** = Conversation state (automatic)
- **Memory Bank** = User facts across sessions (manual semantic search)
- Use BOTH for complete memory system

### Builder Pattern Purpose
- Serializes code to remote containers
- Enables horizontal scaling
- All imports/tools must be inside builder

### Production Checklist
- ✅ Checkpointer for session state
- ✅ Memory Bank for long-term facts
- ✅ Multi-tenant isolation (thread_id + scope filtering)
- ✅ Secret Manager for credentials
- ✅ LangSmith for observability
- ✅ DeepEval for quality metrics
- ✅ Error handling in all nodes
- ✅ Background evaluation in FastAPI
- ✅ Streaming responses (SSE or WebSocket)
- ✅ Timeout handling for long operations
