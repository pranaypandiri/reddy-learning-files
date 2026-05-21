"""
Setup FAISS Vector Store with sample IT knowledge base
Run this once to create the vector store
"""

from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

print("Setting up vector store...")

# Initialize embeddings
embeddings = VertexAIEmbeddings(
    model_name="textembedding-gecko@003", project="ai-practice-388514"
)

# Sample knowledge base documents
sample_docs = [
    Document(
        page_content="VPN not connecting: Solution - Restart VPN client, check firewall settings, verify network credentials, try different VPN server",
        metadata={"category": "IT", "topic": "VPN", "issue_type": "connection"},
    ),
    Document(
        page_content="Password reset procedure: Go to account settings, click 'Forgot Password', verify via email or SMS, create new strong password",
        metadata={"category": "IT", "topic": "Password", "issue_type": "account"},
    ),
    Document(
        page_content="Email not syncing on phone: Solution - Check internet connection, remove and re-add email account, clear app cache, update email app",
        metadata={"category": "IT", "topic": "Email", "issue_type": "sync"},
    ),
    Document(
        page_content="Laptop won't turn on: Check power cable connection, hold power button for 10 seconds, try different power outlet, check battery indicator",
        metadata={"category": "Hardware", "topic": "Laptop", "issue_type": "power"},
    ),
    Document(
        page_content="Monitor screen flickering: Solution - Check cable connections, adjust refresh rate, update graphics drivers, try different HDMI/DisplayPort cable",
        metadata={"category": "Hardware", "topic": "Monitor", "issue_type": "display"},
    ),
    Document(
        page_content="Keyboard keys not working: Clean keyboard with compressed air, check USB connection, restart computer, try external keyboard to test",
        metadata={"category": "Hardware", "topic": "Keyboard", "issue_type": "input"},
    ),
]

# Create FAISS vector store
print("Creating vector store with sample documents...")
vector_store = FAISS.from_documents(sample_docs, embeddings)

# Save to disk
print("Saving vector store to disk...")
vector_store.save_local("it_knowledge_base")

print("✅ Vector store created and saved!")
print(f"✅ Total documents: {len(sample_docs)}")
print("\nYou can now use it in your agent with:")
print('vector_store = FAISS.load_local("it_knowledge_base", embeddings)')
