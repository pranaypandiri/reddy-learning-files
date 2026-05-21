"""
Check all possible import paths for Vertex AI Memory Bank
"""

import sys

print("=" * 60)
print("Searching for Memory Bank in Vertex AI SDK")
print("=" * 60)

# List of possible import paths to try
possible_imports = [
    # Preview paths
    ("vertexai.preview.memory", "MemoryBankService"),
    ("vertexai.preview.generative_models.memory", "MemoryBank"),
    ("vertexai.preview", "memory"),
    # Generative AI paths
    ("vertexai.generative_models", "memory"),
    ("vertexai.generative_models.memory", "MemoryBank"),
    # Direct paths
    ("vertexai.memory", "MemoryBank"),
    ("vertexai", "memory"),
    # Agent Builder / Reasoning Engine paths
    ("vertexai.preview.reasoning_engines.memory", "MemoryBank"),
    ("vertexai.reasoning_engines.memory", "MemoryBank"),
    # Language models path
    ("vertexai.language_models.memory", "MemoryBank"),
    ("vertexai.preview.language_models.memory", "MemoryBank"),
]

found_memory = False

for module_path, class_name in possible_imports:
    try:
        # Try to import the module
        parts = module_path.split(".")
        module = __import__(module_path)

        # Navigate to the actual module
        for part in parts[1:]:
            module = getattr(module, part)

        # Try to get the class
        if class_name:
            cls = getattr(module, class_name, None)
            if cls:
                print(f"✅ FOUND: from {module_path} import {class_name}")
                print(f"   Class: {cls}")
                found_memory = True
            else:
                print(f"⚠️  Module exists but {class_name} not found: {module_path}")
        else:
            print(f"✅ FOUND MODULE: {module_path}")
            print(f"   Contents: {dir(module)}")
            found_memory = True

    except (ImportError, AttributeError) as e:
        print(f"❌ Not found: {module_path}")

if not found_memory:
    print("\n" + "=" * 60)
    print("Memory Bank not found in any path")
    print("=" * 60)

# Now let's explore what's actually available
print("\n" + "=" * 60)
print("What's Actually Available in VertexAI SDK?")
print("=" * 60)

try:
    import vertexai

    print("\n📦 Main vertexai module contents:")
    main_items = [item for item in dir(vertexai) if not item.startswith("_")]
    for item in main_items:
        print(f"   - {item}")

    # Check preview
    try:
        import vertexai.preview as preview

        print("\n📦 vertexai.preview contents:")
        preview_items = [item for item in dir(preview) if not item.startswith("_")]
        for item in preview_items:
            print(f"   - {item}")
    except:
        pass

    # Check generative_models
    try:
        from vertexai import generative_models

        print("\n📦 vertexai.generative_models contents:")
        gm_items = [item for item in dir(generative_models) if not item.startswith("_")]
        for item in gm_items:
            print(f"   - {item}")
    except:
        pass

    # Check if GenerativeModel has memory features
    try:
        from vertexai.generative_models import GenerativeModel

        print("\n🤖 GenerativeModel attributes (checking for memory):")
        model_attrs = [
            attr for attr in dir(GenerativeModel) if "memory" in attr.lower()
        ]
        if model_attrs:
            print("   Memory-related attributes found:")
            for attr in model_attrs:
                print(f"      - {attr}")
        else:
            print("   ❌ No memory-related attributes in GenerativeModel")
    except:
        pass

except Exception as e:
    print(f"Error exploring SDK: {e}")

print("\n" + "=" * 60)
print("CONCLUSION")
print("=" * 60)
print(
    """
If nothing found above, Memory Bank is definitely not available yet.
It's likely in closed beta/preview requiring special access.

Proceed with custom memory solution using Vector Search!
"""
)
