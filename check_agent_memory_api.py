"""
Check if reasoning_engines has memory capabilities via agent_engines
"""

print("=" * 60)
print("Checking Reasoning Engines Memory API")
print("=" * 60)

# Check if reasoning_engines exists and has memory
try:
    from vertexai.preview import reasoning_engines

    print("✅ reasoning_engines module found")

    # Check what's in it
    print("\n📦 Contents of reasoning_engines:")
    items = [item for item in dir(reasoning_engines) if not item.startswith("_")]
    for item in items:
        print(f"   - {item}")

    # Try to access LangchainAgent
    try:
        agent_class = reasoning_engines.LangchainAgent
        print(f"\n✅ LangchainAgent found: {agent_class}")

        # Check if it has memory-related methods
        print("\n🔍 LangchainAgent attributes:")
        agent_attrs = dir(agent_class)

        memory_attrs = [attr for attr in agent_attrs if "memory" in attr.lower()]
        if memory_attrs:
            print("   Memory-related attributes:")
            for attr in memory_attrs:
                print(f"      - {attr}")
        else:
            print("   ❌ No memory-related attributes")

    except AttributeError:
        print("❌ LangchainAgent not found")

    # Check for agent_engines client
    print("\n" + "=" * 60)
    print("Checking agent_engines API client")
    print("=" * 60)

    try:
        from google.cloud import aiplatform

        # Initialize to get client
        aiplatform.init(project="ge-poc-poc2")

        # Check if there's an agent_engines client
        if hasattr(aiplatform, "gapic"):
            print("✅ aiplatform.gapic exists")
            gapic = aiplatform.gapic

            # Look for agent-related clients
            gapic_items = dir(gapic)
            agent_items = [
                item
                for item in gapic_items
                if "agent" in item.lower() or "reasoning" in item.lower()
            ]

            if agent_items:
                print("\n📦 Agent/Reasoning related items in gapic:")
                for item in agent_items:
                    print(f"   - {item}")
            else:
                print("\n❌ No agent-related items in gapic")

    except Exception as e:
        print(f"❌ Error checking gapic: {e}")

    # Try the actual syntax from your example
    print("\n" + "=" * 60)
    print("Testing Your Syntax: client.agent_engines.memories")
    print("=" * 60)

    try:
        from google.cloud.aiplatform import gapic

        # Try to find agent_engines client
        client_attrs = dir(gapic)
        print(f"\n📦 Available clients in gapic (first 20):")
        for attr in client_attrs[:20]:
            if not attr.startswith("_"):
                print(f"   - {attr}")

        # Look for agent or reasoning engine service
        agent_clients = [
            attr
            for attr in client_attrs
            if "agent" in attr.lower()
            or "reasoning" in attr.lower()
            or "engine" in attr.lower()
        ]
        if agent_clients:
            print(f"\n✅ Agent/Engine related clients:")
            for client in agent_clients:
                print(f"   - {client}")
        else:
            print("\n❌ No agent_engines client found")

    except Exception as e:
        print(f"❌ Error: {e}")

except ImportError as e:
    print(f"❌ reasoning_engines not available: {e}")

print("\n" + "=" * 60)
print("FINAL CHECK: Can we use .memories.generate()?")
print("=" * 60)

try:
    from vertexai.preview.reasoning_engines import LangchainAgent

    # Create a dummy agent to check its methods
    print("\n🔍 Checking if LangchainAgent instance has memory methods...")

    # Just check the class methods, don't create instance
    methods = [m for m in dir(LangchainAgent) if not m.startswith("_")]
    print(f"\nAvailable methods on LangchainAgent:")
    for method in methods:
        print(f"   - {method}")

    # Check specifically for memory-related
    memory_methods = [
        m for m in methods if "memory" in m.lower() or "memories" in m.lower()
    ]
    if memory_methods:
        print(f"\n✅ FOUND memory methods:")
        for m in memory_methods:
            print(f"   - {m}")
    else:
        print(f"\n❌ No memory/memories methods found")

except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("CONCLUSION")
print("=" * 60)
print(
    """
The syntax `client.agent_engines.memories.generate()` might be:
1. From Google's internal/beta documentation
2. For enterprise customers only
3. Not yet available in public SDK
4. Upcoming feature

If no memory methods found above, we use custom solution!
"""
)
