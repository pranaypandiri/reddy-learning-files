"""
Check if we have Vertex AI Agent Engine Memory permissions
"""

print("=" * 60)
print("Checking Vertex AI Agent Engine Memory Permissions")
print("=" * 60)

import subprocess
import json

# 1. Check our current IAM permissions
print("\n1️⃣ Checking IAM permissions...")
try:
    result = subprocess.run(
        ["gcloud", "projects", "get-iam-policy", "ge-poc-poc2", "--format=json"],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        policy = json.loads(result.stdout)

        # Look for aiplatform.memories permissions
        memory_permissions = []
        for binding in policy.get("bindings", []):
            role = binding.get("role", "")
            if "aiplatform" in role.lower() or "agent" in role.lower():
                print(f"\n   Found role: {role}")
                for member in binding.get("members", []):
                    if "serviceAccount" in member or "user" in member:
                        print(f"      Member: {member}")

        print("\n✅ IAM policy retrieved")
    else:
        print(f"❌ Error: {result.stderr}")

except Exception as e:
    print(f"❌ Error checking IAM: {e}")

# 2. Check if we can test the permissions
print("\n" + "=" * 60)
print("2️⃣ Testing aiplatform.memories permissions")
print("=" * 60)

try:
    result = subprocess.run(
        ["gcloud", "auth", "list", "--format=json"], capture_output=True, text=True
    )

    if result.returncode == 0:
        accounts = json.loads(result.stdout)
        print(f"\n✅ Active account: {accounts[0].get('account', 'unknown')}")

        # Test specific permissions
        permissions_to_test = [
            "aiplatform.memories.generate",
            "aiplatform.memories.retrieve",
            "aiplatform.memories.create",
            "aiplatform.memories.list",
        ]

        print(f"\n🔍 Testing permissions:")
        for perm in permissions_to_test:
            test_result = subprocess.run(
                [
                    "gcloud",
                    "projects",
                    "test-iam-permissions",
                    "ge-poc-poc2",
                    f"--permissions={perm}",
                ],
                capture_output=True,
                text=True,
            )

            if perm in test_result.stdout:
                print(f"   ✅ {perm}")
            else:
                print(f"   ❌ {perm} - NOT granted")

except Exception as e:
    print(f"❌ Error testing permissions: {e}")

# 3. Try to access the Memory API
print("\n" + "=" * 60)
print("3️⃣ Trying to Access Memory API")
print("=" * 60)

try:
    from google.cloud import aiplatform
    from vertexai.preview.reasoning_engines import LangchainAgent

    aiplatform.init(project="ge-poc-poc2", location="us-central1")

    # Try to access via gapic client
    print("\n🔍 Checking for Memory service in gapic...")
    gapic_items = dir(aiplatform.gapic)
    memory_items = [
        item
        for item in gapic_items
        if "memory" in item.lower() or "memories" in item.lower()
    ]

    if memory_items:
        print(f"✅ Found memory-related items:")
        for item in memory_items:
            print(f"   - {item}")

        # Try to get the client
        for item in memory_items:
            if "Client" in item:
                try:
                    client_class = getattr(aiplatform.gapic, item)
                    print(f"\n✅ Found client class: {client_class}")

                    # Try to create client
                    client = client_class()
                    print(f"✅ Client created successfully!")

                    # Check methods
                    methods = [m for m in dir(client) if not m.startswith("_")]
                    print(f"\n📦 Available methods:")
                    for method in methods[:10]:
                        print(f"   - {method}")

                except Exception as e:
                    print(f"❌ Error creating client: {e}")
    else:
        print("❌ No memory-related items found in gapic")

except Exception as e:
    print(f"❌ Error: {e}")

# 4. Try direct API access
print("\n" + "=" * 60)
print("4️⃣ Trying Direct Memory API Call")
print("=" * 60)

try:
    # Try to call the API endpoint directly
    result = subprocess.run(
        [
            "gcloud",
            "ai",
            "reasoning-engines",
            "list",
            "--project=ge-poc-poc2",
            "--location=us-central1",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("✅ Reasoning engines command works:")
        print(result.stdout)

        # Try memory-specific command
        print("\n🔍 Trying memory commands...")
        memory_result = subprocess.run(
            ["gcloud", "ai", "--help"], capture_output=True, text=True
        )

        if "memories" in memory_result.stdout or "memory" in memory_result.stdout:
            print("✅ Memory commands might be available!")
        else:
            print("❌ No memory commands in gcloud ai")
    else:
        print(f"❌ Error: {result.stderr}")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("CONCLUSION")
print("=" * 60)
print(
    """
If memory API is found above with proper permissions:
→ We can use Vertex AI Agent Engine Memory!

If NOT found:
→ Feature exists but not available to us yet
→ Might need to enable specific APIs or get allowlisted
→ Use custom memory solution with Vector Search

Check the results above to decide!
"""
)
