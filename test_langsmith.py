import os

# Set LangSmith credentials
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["LANGCHAIN_PROJECT"] = "Test-Project"

from langchain_openai import AzureChatOpenAI

llm = AzureChatOpenAI(
    api_key="92dc252cdb0c4079b4712a9ead4179ca",
    api_version="2024-12-01-preview",
    azure_endpoint="https://azureaitest4641590782.openai.azure.com/",
    model="gpt-4",
)

print("Testing LangSmith integration...")
response = llm.invoke("Say hello in 5 words")
print(f"\nResponse: {response.content}")

print("\n✅ Check LangSmith dashboard: https://smith.langchain.com/")
print("   Look for 'Test-Project' and you'll see your trace!")
