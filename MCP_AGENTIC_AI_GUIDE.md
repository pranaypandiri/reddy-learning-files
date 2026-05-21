# MCP for Agentic AI - Intuitive Guide

## What is MCP? (Simple Explanation)

Think of **MCP (Model Context Protocol)** as **USB-C for AI agents**:

- **USB-C**: One standard port to connect ANY device (phone, laptop, mouse)
- **MCP**: One standard protocol to connect ANY AI agent to ANY data source or tool

### Real World Analogy

```
Without MCP (Old Way):
├── Agent 1 → Custom code for Google Calendar
├── Agent 2 → Custom code for Notion
├── Agent 3 → Custom code for Database
└── Agent 4 → Custom code for Slack
     ❌ Every agent needs custom integration for every tool

With MCP (New Way):
├── Any Agent → MCP Protocol → Google Calendar MCP Server
├── Any Agent → MCP Protocol → Notion MCP Server  
├── Any Agent → MCP Protocol → Database MCP Server
└── Any Agent → MCP Protocol → Slack MCP Server
     ✅ One standard interface, plug and play!
```

---

## Core Concepts (No Jargon!)

### 1. **Three Players in MCP**

```
┌──────────────────┐
│   MCP HOST       │  ← Your AI application (Claude, VS Code, custom agent)
│  (AI App)        │
└────────┬─────────┘
         │ Creates multiple clients
         │
    ┌────┴────┬────────┬────────┐
    │         │        │        │
┌───▼───┐ ┌──▼───┐ ┌──▼───┐ ┌──▼───┐
│Client │ │Client│ │Client│ │Client│  ← Each client connects to ONE server
│   1   │ │  2   │ │  3   │ │  4   │
└───┬───┘ └──┬───┘ └──┬───┘ └──┬───┘
    │        │        │        │
┌───▼───┐ ┌──▼───┐ ┌──▼───┐ ┌──▼───┐
│Server │ │Server│ │Server│ │Server│  ← Servers provide tools/data
│   A   │ │  B   │ │  C   │ │  D   │
└───────┘ └──────┘ └──────┘ └──────┘
```

**Roles:**
- **MCP Host**: Your AI agent application (the brain)
- **MCP Client**: Connector that talks to ONE server
- **MCP Server**: Program that provides tools/data/context

### 2. **Three Things MCP Servers Provide**

```python
# 1. TOOLS - Actions the AI can take
@tool
def send_email(to: str, subject: str, body: str):
    """Send an email"""
    # Do the actual work
    return "Email sent!"

# 2. RESOURCES - Data the AI can read
@resource("file://document.txt")
def get_document():
    """Provide file contents"""
    return "Document content here..."

# 3. PROMPTS - Pre-built templates
@prompt("analyze-code")
def code_analysis_prompt():
    """Template for code analysis"""
    return "Analyze this code: {code}"
```

**Simple Explanation:**
- **Tools** = Things AI can DO (send email, search web, calculate)
- **Resources** = Things AI can READ (files, databases, API responses)
- **Prompts** = Pre-written instructions to help AI

---

## How to Build & Integrate MCP

### **Method 1: Create an MCP Server (Python)**

```python
from mcp.server.fastmcp import FastMCP
import httpx

# 1. Initialize server
mcp = FastMCP("my-awesome-server")

# 2. Create a tool
@mcp.tool()
async def search_web(query: str) -> str:
    """Search the web for information.
    
    Args:
        query: What to search for
    """
    # Your logic here
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/search?q={query}")
        return response.json()["results"]

# 3. Create a resource
@mcp.resource("database://users")
async def get_users() -> str:
    """Get list of users from database"""
    # Fetch from database
    return "User1, User2, User3"

# 4. Run the server
if __name__ == "__main__":
    mcp.run(transport="stdio")  # Local server
    # OR
    # mcp.run(transport="http")  # Remote server
```

**What happens:**
1. Server exposes tools/resources
2. AI agent connects to it
3. AI can discover what's available
4. AI uses tools when needed

---

### **Method 2: Connect Agent to MCP Server**

```python
from langchain_openai import ChatOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 1. Configure which MCP server to connect to
server_params = StdioServerParameters(
    command="python",  # Or "uv", "node", etc.
    args=["path/to/your_server.py"]
)

# 2. Create your AI agent
llm = ChatOpenAI(model="gpt-4")

# 3. Connect agent to MCP server
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        # Initialize connection
        await session.initialize()
        
        # List available tools
        tools_response = await session.list_tools()
        print(f"Available tools: {tools_response.tools}")
        
        # Call a tool
        result = await session.call_tool("search_web", {"query": "Python MCP"})
        print(f"Result: {result.content}")
```

---

## Practical Integration Patterns

### **Pattern 1: Agent with Multiple MCP Servers**

```python
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, MessagesState
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configure multiple MCP servers
servers = {
    "database": StdioServerParameters(
        command="python",
        args=["database_server.py"]
    ),
    "email": StdioServerParameters(
        command="python",
        args=["email_server.py"]
    ),
    "slack": StdioServerParameters(
        command="python",
        args=["slack_server.py"]
    )
}

async def setup_mcp_tools():
    """Connect to all MCP servers and gather tools"""
    all_tools = []
    
    for server_name, server_params in servers.items():
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Get tools from this server
                tools = await session.list_tools()
                all_tools.extend(tools.tools)
    
    return all_tools

# Create agent with all MCP tools
async def create_agent():
    tools = await setup_mcp_tools()
    
    agent = create_react_agent(
        model=ChatOpenAI(model="gpt-4"),
        tools=tools,  # All MCP tools available
        state_modifier="You have access to database, email, and Slack tools."
    )
    
    return agent
```

### **Pattern 2: Dynamic Tool Discovery**

```python
async def agent_with_dynamic_mcp(user_query: str):
    """Agent that discovers and uses MCP tools on the fly"""
    
    # Step 1: Connect to MCP server
    server = StdioServerParameters(command="python", args=["my_server.py"])
    
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Step 2: Discover available tools
            tools_list = await session.list_tools()
            
            # Step 3: Let LLM decide which tool to use
            llm = ChatOpenAI(model="gpt-4")
            
            # Build tool descriptions for LLM
            tool_descriptions = "\n".join([
                f"- {tool.name}: {tool.description}"
                for tool in tools_list.tools
            ])
            
            prompt = f"""
            Available tools:
            {tool_descriptions}
            
            User query: {user_query}
            
            Which tool should I use and what arguments?
            """
            
            # LLM decides
            response = llm.invoke(prompt)
            
            # Step 4: Execute the chosen tool
            # Parse LLM response to get tool_name and args
            result = await session.call_tool(tool_name, arguments)
            
            return result
```

### **Pattern 3: Multi-Agent System with MCP**

```python
from langgraph.graph import StateGraph, MessagesState, START, END

# Agent 1: Uses Database MCP Server
database_server = StdioServerParameters(
    command="python",
    args=["database_mcp_server.py"]
)

# Agent 2: Uses Email MCP Server  
email_server = StdioServerParameters(
    command="python",
    args=["email_mcp_server.py"]
)

# Build workflow
workflow = StateGraph(MessagesState)

async def database_agent(state):
    """Agent that queries database via MCP"""
    async with stdio_client(database_server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("query_database", {
                "query": "SELECT * FROM users"
            })
            return {"messages": [result.content]}

async def email_agent(state):
    """Agent that sends emails via MCP"""
    async with stdio_client(email_server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("send_email", {
                "to": "user@example.com",
                "subject": "Report",
                "body": state["messages"][-1]
            })
            return {"messages": [result.content]}

# Add nodes
workflow.add_node("database_agent", database_agent)
workflow.add_node("email_agent", email_agent)

# Connect
workflow.add_edge(START, "database_agent")
workflow.add_edge("database_agent", "email_agent")
workflow.add_edge("email_agent", END)

app = workflow.compile()
```

---

## Real-World Use Cases

### **Use Case 1: Customer Support Bot**

```python
# MCP Server provides:
# - Tool: query_tickets (search support tickets)
# - Tool: create_ticket (create new ticket)
# - Tool: send_response (reply to customer)
# - Resource: knowledge_base (company docs)

@mcp.tool()
async def query_tickets(customer_email: str):
    """Find all tickets for a customer"""
    return database.query(f"SELECT * FROM tickets WHERE email='{customer_email}'")

# Agent uses these tools automatically when helping customers
```

### **Use Case 2: Code Analysis Assistant**

```python
# MCP Server provides:
# - Tool: run_tests (execute test suite)
# - Tool: analyze_code (static analysis)
# - Tool: check_security (security scan)
# - Resource: codebase (access to files)

@mcp.tool()
async def analyze_code(file_path: str):
    """Analyze code for issues"""
    code = read_file(file_path)
    return linter.analyze(code)
```

### **Use Case 3: Data Pipeline Orchestrator**

```python
# Multiple MCP servers:
# - Database MCP: query_data, insert_data
# - S3 MCP: upload_file, download_file
# - Notification MCP: send_alert

# Agent orchestrates entire pipeline
async def data_pipeline_agent():
    # 1. Query from database (Database MCP)
    data = await database_session.call_tool("query_data")
    
    # 2. Process and upload (S3 MCP)
    await s3_session.call_tool("upload_file", {"data": data})
    
    # 3. Notify (Notification MCP)
    await notif_session.call_tool("send_alert", {"message": "Pipeline complete"})
```

---

## Key Benefits of MCP for Agents

### **1. Reusability**
```
One database MCP server → Used by 10 different agents
One email MCP server → Used by 20 different applications
```

### **2. Standardization**
```
All agents speak the same protocol → Easy integration
New tool? Just create MCP server → All agents can use it
```

### **3. Scalability**
```
Local MCP servers → Fast, no network overhead (STDIO)
Remote MCP servers → Share across team/org (HTTP)
```

### **4. Security**
```
MCP servers can enforce authentication
Tools can require user approval before execution
Permissions controlled at server level
```

---

## Quick Setup Checklist

```bash
# 1. Install MCP SDK
pip install mcp

# 2. Create MCP Server
# File: my_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-tools")

@mcp.tool()
def my_tool(input: str) -> str:
    """My awesome tool"""
    return f"Processed: {input}"

if __name__ == "__main__":
    mcp.run(transport="stdio")

# 3. Test server
uv run my_server.py

# 4. Connect from agent
# (See integration patterns above)
```

---

## Common Patterns Summary

| Pattern | When to Use | Example |
|---------|------------|---------|
| **Single MCP Server** | Simple agent, one data source | Agent + Database MCP |
| **Multiple MCP Servers** | Agent needs diverse tools | Agent + DB + Email + Slack |
| **Remote MCP** | Share tools across team | Company-wide API gateway |
| **Local MCP** | Fast, private tools | File system, local DB |
| **Dynamic Discovery** | Tools change frequently | Plugin system |

---

## Best Practices

1. **One Server = One Domain**
   - ✅ Email MCP Server (handles all email operations)
   - ❌ Generic MCP Server (does everything)

2. **Clear Tool Descriptions**
   ```python
   @mcp.tool()
   def search(query: str) -> str:
       """Search the database for users.
       
       Args:
           query: Search term (name, email, or ID)
           
       Returns:
           JSON list of matching users
       """
   ```

3. **Error Handling**
   ```python
   @mcp.tool()
   async def safe_api_call(endpoint: str):
       try:
           result = await api.call(endpoint)
           return result
       except Exception as e:
           return f"Error: {str(e)}"
   ```

4. **Use Type Hints**
   ```python
   # ✅ Good
   def tool(name: str, age: int) -> dict[str, Any]:
       pass
   
   # ❌ Bad
   def tool(name, age):
       pass
   ```

---

## Debugging Tips

```python
# Enable logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test MCP server standalone
# Run: uv run my_server.py
# Should start without errors

# Use MCP Inspector (debugging tool)
npx @modelcontextprotocol/inspector python my_server.py

# Check tool listing
tools = await session.list_tools()
print(tools)  # Should show your tools
```

---

## Next Steps

1. **Build a simple MCP server** with one tool
2. **Connect it to an agent** (Claude, LangGraph, etc.)
3. **Add more tools** as needed
4. **Create multiple servers** for different domains
5. **Share servers** with team (use HTTP transport)

**Remember**: MCP is just a protocol. The power comes from:
- Tools you create
- How agents use them
- Integration patterns you design

Start simple, then scale up! 🚀
