"""
Deep dive: What's actually available in vertexai.preview?
"""

print("=" * 60)
print("What's Inside vertexai.preview Module?")
print("=" * 60)

try:
    import vertexai.preview as preview

    # List all available modules/classes
    all_items = dir(preview)

    print("\n✅ Available modules in vertexai.preview:")
    for item in all_items:
        if not item.startswith("_"):  # Skip private stuff
            print(f"   - {item}")

    print("\n" + "=" * 60)
    print("Checking Specific Items:")
    print("=" * 60)

    # Check reasoning_engines
    if "reasoning_engines" in all_items:
        print("\n✅ reasoning_engines - EXISTS")
        from vertexai.preview import reasoning_engines

        print(f"   Available: {dir(reasoning_engines)[:5]}...")
    else:
        print("\n❌ reasoning_engines - DOES NOT EXIST")

    # Check memory
    if "memory" in all_items:
        print("\n✅ memory - EXISTS")
        from vertexai.preview import memory

        print(f"   Available: {dir(memory)}")
    else:
        print("\n❌ memory - DOES NOT EXIST")
        print("   This confirms Memory Bank is not available")

    # Try to import memory anyway
    print("\n" + "=" * 60)
    print("Attempting Direct Import:")
    print("=" * 60)
    try:
        from vertexai.preview.memory import MemoryBankService

        print("✅ MemoryBankService imported successfully!")
    except ImportError as e:
        print(f"❌ Cannot import MemoryBankService")
        print(f"   Error: {e}")

except Exception as e:
    print(f"❌ Error checking vertexai.preview: {e}")

print("\n" + "=" * 60)
print("CONCLUSION:")
print("=" * 60)
print(
    """
If 'memory' is NOT in the list above, it means:
- Google hasn't released Memory Bank to general availability
- It's still in private beta/preview
- Only specific Google Cloud customers have access
- We need to build custom memory solution

What IS available:
- Vertex AI Vector Search (Matching Engine) ✅
- ADK (reasoning_engines) ✅
- We can build our own memory with these!
"""
)
