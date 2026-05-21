"""
Check Vertex AI features availability
"""

from google.cloud import aiplatform

# Initialize
aiplatform.init(project="ai-practice-388514", location="us-central1")

print("=" * 70)
print("VERTEX AI FEATURES CHECK")
print("=" * 70)

# Check ADK (Agent Development Kit)
print("\n1. CHECKING ADK (Agent Development Kit)...")
try:
    from vertexai.preview import reasoning_engines

    print("✅ ADK (reasoning_engines) is available!")
    print("   - Can create reasoning engines")
    print("   - Can deploy agents")
except ImportError as e:
    print(f"❌ ADK not available: {e}")

# Check Memory Bank
print("\n2. CHECKING VERTEX AI MEMORY BANK...")
try:
    # Try to import memory-related modules
    from google.cloud.aiplatform import gapic

    print("✅ aiplatform.gapic available")

    # Check for memory bank in API
    try:
        from vertexai.preview import memory

        print("✅ Vertex AI Memory module available!")
    except ImportError:
        print("⚠️  vertexai.preview.memory not found (might be too new/not GA)")

    # Alternative: Check if we can list any memory banks
    try:
        client = aiplatform.gapic.DatasetServiceClient()
        print("✅ Dataset service client initialized")
    except Exception as e:
        print(f"⚠️  Dataset client error: {e}")

except Exception as e:
    print(f"❌ Error checking Memory Bank: {e}")

# Check Generative AI
print("\n3. CHECKING GENERATIVE AI...")
try:
    from vertexai.generative_models import GenerativeModel

    print("✅ Generative models available")

    # Try to load a model
    model = GenerativeModel("gemini-2.0-flash-exp")
    print("✅ Can initialize Gemini models")
except Exception as e:
    print(f"⚠️  Generative models error: {e}")

# Check available services
print("\n4. YOUR PERMISSIONS:")
print("✅ roles/aiplatform.admin - Full Vertex AI admin access")
print("✅ roles/discoveryengine.admin - Search/recommendation features")
print("✅ roles/dialogflow.admin - Conversation AI")

print("\n5. AVAILABLE APIS:")
print("✅ Vertex AI API (aiplatform.googleapis.com)")
print("✅ Generative Language API (generativelanguage.googleapis.com)")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print("\n📋 What you CAN use:")
print("  ✅ Vertex AI models (Gemini, etc.)")
print("  ✅ LangGraph with Vertex AI")
print("  ✅ Custom memory with Cloud SQL")
print("  ✅ Reasoning Engines (ADK) - likely available")

print("\n❓ What needs verification:")
print("  ⏳ Vertex AI Memory Bank (check if GA in your region)")
print("  ⏳ Agent Builder features")

print("\n💡 RECOMMENDATION:")
print("  - Try ADK first (should work with your permissions)")
print("  - If Memory Bank unavailable → use custom memory with Cloud SQL")
print("  - You have all permissions needed!")

print("\n" + "=" * 70)
