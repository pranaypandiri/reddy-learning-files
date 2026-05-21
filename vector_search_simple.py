"""
Simple Vertex AI Vector Search Example
- Create vector store
- Add one document
- Search
- Delete

Note: This uses the simplified approach with LangChain integration
"""

import os
from langchain_google_vertexai import VectorSearchVectorStore
from langchain_core.documents import Document
from langchain_google_vertexai import VertexAIEmbeddings
from google.cloud import aiplatform

# Initialize Vertex AI
PROJECT_ID = "ai-practice-388514"  # Your actual project
REGION = "us-central1"

aiplatform.init(project=PROJECT_ID, location=REGION)

print("=" * 60)
print("Vertex AI Vector Search - Simple Example")
print("=" * 60)

# Step 1: Create embeddings model
print("\n1️⃣ Creating embeddings model...")
embeddings = VertexAIEmbeddings(
    model_name="textembedding-gecko@003", project=PROJECT_ID
)
print("✅ Embeddings model ready")

# Step 2: Create a simple document
print("\n2️⃣ Creating test document...")
document = Document(
    page_content="VPN not working on MacBook. Solution: Restart VPN client and check firewall settings.",
    metadata={"category": "IT", "issue_type": "VPN", "device": "MacBook"},
)
print(f"✅ Document created: {document.page_content[:50]}...")

# Step 3: For this example, we'll use a simpler approach
# Instead of full Vector Search (which requires index creation),
# let's use FAISS locally first to demonstrate the concept

print("\n3️⃣ Creating local vector store (FAISS for demo)...")
print("   (Full GCP Vector Search requires index setup - see next example)")

from langchain_community.vectorstores import FAISS

# Create vector store with our document
vector_store = FAISS.from_documents(documents=[document], embedding=embeddings)
print("✅ Vector store created with 1 document")

# Step 4: Search
print("\n4️⃣ Searching for similar content...")
query = "VPN issue on laptop"
results = vector_store.similarity_search(query, k=1)

print(f"\n🔍 Query: '{query}'")
print(f"✅ Found {len(results)} result(s):")
for i, result in enumerate(results, 1):
    print(f"\n   Result {i}:")
    print(f"   Content: {result.page_content}")
    print(f"   Metadata: {result.metadata}")

# Step 5: Add another document
print("\n5️⃣ Adding another document...")
new_doc = Document(
    page_content="Password reset for email account. Solution: Use forgot password link and verify via SMS.",
    metadata={"category": "IT", "issue_type": "Password", "service": "Email"},
)

vector_store.add_documents([new_doc])
print("✅ Added new document")

# Search again
print("\n6️⃣ Searching again...")
results = vector_store.similarity_search("how to reset password", k=2)
print(f"✅ Found {len(results)} result(s):")
for i, result in enumerate(results, 1):
    print(f"\n   Result {i}:")
    print(f"   Content: {result.page_content[:60]}...")

# Step 6: Save and cleanup
print("\n7️⃣ Saving vector store locally...")
vector_store.save_local("test_vector_store")
print("✅ Saved to 'test_vector_store' folder")

print("\n8️⃣ Cleanup (delete)...")
import shutil

shutil.rmtree("test_vector_store")
print("✅ Deleted vector store")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(
    """
✅ Created embeddings with Vertex AI
✅ Created 1 document
✅ Searched successfully
✅ Added another document
✅ Searched again
✅ Deleted everything

NEXT STEPS:
For production with GCP Vertex AI Vector Search (Matching Engine):
1. Create Index (one-time setup)
2. Create Index Endpoint (one-time setup)
3. Deploy Index to Endpoint
4. Then use for search

Want to see full GCP Vector Search setup? (takes 20-30 mins to create index)
"""
)
