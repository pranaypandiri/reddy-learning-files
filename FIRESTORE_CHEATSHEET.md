# FIRESTORE CHEATSHEET - Complete Guide

## 1. Setup & Initialization

```python
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from datetime import datetime

# Initialize Firestore
db = firestore.Client(project="your-project-id")
```

---

## 2. CRUD Operations

### CREATE (Add Documents)

```python
# Method 1: Auto-generated ID
doc_ref = db.collection('sessions').add({
    'user_id': 'john',
    'created_at': firestore.SERVER_TIMESTAMP,
    'status': 'active'
})
print(f"Created with ID: {doc_ref[1].id}")

# Method 2: Custom ID
db.collection('sessions').document('session-123').set({
    'user_id': 'john',
    'created_at': firestore.SERVER_TIMESTAMP,
    'status': 'active'
})

# Method 3: Merge (update if exists, create if not)
db.collection('sessions').document('session-123').set({
    'last_updated': firestore.SERVER_TIMESTAMP
}, merge=True)
```

### READ (Get Documents)

```python
# Get single document
doc = db.collection('sessions').document('session-123').get()
if doc.exists:
    print(doc.to_dict())
    print(doc.id)
else:
    print("Document not found")

# Get all documents in collection
docs = db.collection('sessions').stream()
for doc in docs:
    print(f"{doc.id}: {doc.to_dict()}")

# Get with where clause
docs = db.collection('sessions').where(
    filter=FieldFilter('user_id', '==', 'john')
).stream()
```

### UPDATE

```python
# Update specific fields
db.collection('sessions').document('session-123').update({
    'status': 'inactive',
    'updated_at': firestore.SERVER_TIMESTAMP
})

# Update nested fields
db.collection('sessions').document('session-123').update({
    'metadata.last_action': 'logout',
    'metadata.device': 'mobile'
})

# Increment a value
db.collection('sessions').document('session-123').update({
    'message_count': firestore.Increment(1)
})

# Add to array
db.collection('sessions').document('session-123').update({
    'tags': firestore.ArrayUnion(['important', 'urgent'])
})

# Remove from array
db.collection('sessions').document('session-123').update({
    'tags': firestore.ArrayRemove(['urgent'])
})
```

### DELETE

```python
# Delete document
db.collection('sessions').document('session-123').delete()

# Delete field (not document)
db.collection('sessions').document('session-123').update({
    'field_to_delete': firestore.DELETE_FIELD
})

# Delete collection (must delete all docs first)
def delete_collection(collection_ref, batch_size=100):
    docs = collection_ref.limit(batch_size).stream()
    deleted = 0
    
    for doc in docs:
        doc.reference.delete()
        deleted += 1
    
    if deleted >= batch_size:
        return delete_collection(collection_ref, batch_size)

delete_collection(db.collection('sessions'))
```

---

## 3. Queries & Filtering

### Basic Queries

```python
# Simple where
sessions = db.collection('sessions').where(
    filter=FieldFilter('user_id', '==', 'john')
).stream()

# Multiple conditions (AND)
sessions = db.collection('sessions').where(
    filter=FieldFilter('user_id', '==', 'john')
).where(
    filter=FieldFilter('status', '==', 'active')
).stream()

# Comparison operators
sessions = db.collection('sessions').where(
    filter=FieldFilter('message_count', '>', 10)
).stream()

# Operators: ==, !=, <, <=, >, >=, in, not-in, array-contains
```

### Order By & Limit

```python
# Order by field
sessions = db.collection('sessions').order_by(
    'created_at', 
    direction=firestore.Query.DESCENDING
).stream()

# Limit results
sessions = db.collection('sessions').limit(10).stream()

# Offset (skip first N)
sessions = db.collection('sessions').offset(5).limit(10).stream()
```

### Array Queries

```python
# Array contains
sessions = db.collection('sessions').where(
    filter=FieldFilter('tags', 'array_contains', 'urgent')
).stream()

# Array contains any
sessions = db.collection('sessions').where(
    filter=FieldFilter('tags', 'array_contains_any', ['urgent', 'important'])
).stream()
```

### IN Queries

```python
# In query (max 10 values)
sessions = db.collection('sessions').where(
    filter=FieldFilter('status', 'in', ['active', 'pending'])
).stream()

# Not in query
sessions = db.collection('sessions').where(
    filter=FieldFilter('status', 'not-in', ['deleted', 'archived'])
).stream()
```

---

## 4. Pagination

### Cursor-based Pagination (Recommended)

```python
# First page
page_size = 10
query = db.collection('sessions').order_by('created_at').limit(page_size)
docs = query.stream()

results = []
last_doc = None
for doc in docs:
    results.append(doc.to_dict())
    last_doc = doc

# Next page (use last document as cursor)
if last_doc:
    next_query = db.collection('sessions').order_by('created_at').start_after(last_doc).limit(page_size)
    next_docs = next_query.stream()
```

### Complete Pagination Example

```python
def paginate_sessions(page_size=10, last_doc=None):
    query = db.collection('sessions').order_by('created_at').limit(page_size)
    
    if last_doc:
        query = query.start_after(last_doc)
    
    docs = list(query.stream())
    
    return {
        'results': [doc.to_dict() for doc in docs],
        'last_doc': docs[-1] if docs else None,
        'has_more': len(docs) == page_size
    }

# Usage
page1 = paginate_sessions(page_size=10)
page2 = paginate_sessions(page_size=10, last_doc=page1['last_doc'])
```

### Offset Pagination (Simple but slower)

```python
# Page 1
page_1 = db.collection('sessions').offset(0).limit(10).stream()

# Page 2
page_2 = db.collection('sessions').offset(10).limit(10).stream()

# Not recommended for large datasets!
```

---

## 5. Transactions (ACID Operations)

### Basic Transaction

```python
@firestore.transactional
def transfer_messages(transaction, from_session, to_session):
    # Read
    from_doc = from_session.get(transaction=transaction)
    to_doc = to_session.get(transaction=transaction)
    
    from_count = from_doc.get('message_count')
    to_count = to_doc.get('message_count')
    
    # Write
    transaction.update(from_session, {'message_count': from_count - 1})
    transaction.update(to_session, {'message_count': to_count + 1})

# Execute transaction
transaction = db.transaction()
from_ref = db.collection('sessions').document('session-1')
to_ref = db.collection('sessions').document('session-2')

transfer_messages(transaction, from_ref, to_ref)
```

### Transaction with Error Handling

```python
from google.api_core.exceptions import FailedPrecondition

@firestore.transactional
def update_with_check(transaction, doc_ref):
    snapshot = doc_ref.get(transaction=transaction)
    
    if not snapshot.exists:
        raise ValueError("Document does not exist!")
    
    current_value = snapshot.get('counter')
    if current_value < 0:
        raise ValueError("Counter cannot be negative!")
    
    transaction.update(doc_ref, {'counter': current_value + 1})

try:
    transaction = db.transaction()
    doc_ref = db.collection('sessions').document('session-123')
    update_with_check(transaction, doc_ref)
except FailedPrecondition:
    print("Transaction failed - will retry")
except ValueError as e:
    print(f"Business logic error: {e}")
```

---

## 6. Batch Writes

### Batch Operations (Max 500 operations)

```python
# Create batch
batch = db.batch()

# Add operations to batch
session_ref_1 = db.collection('sessions').document('session-1')
batch.set(session_ref_1, {'user_id': 'john', 'status': 'active'})

session_ref_2 = db.collection('sessions').document('session-2')
batch.update(session_ref_2, {'status': 'inactive'})

session_ref_3 = db.collection('sessions').document('session-3')
batch.delete(session_ref_3)

# Commit all at once
batch.commit()
```

### Bulk Write Example

```python
def bulk_create_sessions(sessions_data):
    batch = db.batch()
    batch_count = 0
    
    for i, session in enumerate(sessions_data):
        doc_ref = db.collection('sessions').document(f'session-{i}')
        batch.set(doc_ref, session)
        batch_count += 1
        
        # Firestore limit: 500 operations per batch
        if batch_count == 500:
            batch.commit()
            batch = db.batch()
            batch_count = 0
    
    # Commit remaining
    if batch_count > 0:
        batch.commit()

# Usage
sessions = [
    {'user_id': 'john', 'status': 'active'},
    {'user_id': 'jane', 'status': 'active'},
    # ... more sessions
]
bulk_create_sessions(sessions)
```

---

## 7. Real-time Listeners (Watch for Changes)

### Listen to Document

```python
def on_snapshot(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        print(f"Received document: {doc.id}")
        print(f"Data: {doc.to_dict()}")

# Watch document
doc_ref = db.collection('sessions').document('session-123')
doc_watch = doc_ref.on_snapshot(on_snapshot)

# Stop watching
doc_watch.unsubscribe()
```

### Listen to Collection/Query

```python
def on_snapshot(col_snapshot, changes, read_time):
    for change in changes:
        if change.type.name == 'ADDED':
            print(f"New session: {change.document.id}")
        elif change.type.name == 'MODIFIED':
            print(f"Modified session: {change.document.id}")
        elif change.type.name == 'REMOVED':
            print(f"Removed session: {change.document.id}")

# Watch collection
query = db.collection('sessions').where(
    filter=FieldFilter('status', '==', 'active')
)
query_watch = query.on_snapshot(on_snapshot)

# Stop watching
query_watch.unsubscribe()
```

---

## 8. Advanced Queries

### Compound Queries

```python
# Multiple filters
sessions = db.collection('sessions')\
    .where(filter=FieldFilter('user_id', '==', 'john'))\
    .where(filter=FieldFilter('status', '==', 'active'))\
    .where(filter=FieldFilter('message_count', '>', 5))\
    .order_by('created_at', direction=firestore.Query.DESCENDING)\
    .limit(10)\
    .stream()
```

### Date Range Queries

```python
from datetime import datetime, timedelta

# Last 7 days
seven_days_ago = datetime.now() - timedelta(days=7)

sessions = db.collection('sessions').where(
    filter=FieldFilter('created_at', '>=', seven_days_ago)
).stream()

# Between dates
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 12, 31)

sessions = db.collection('sessions')\
    .where(filter=FieldFilter('created_at', '>=', start_date))\
    .where(filter=FieldFilter('created_at', '<=', end_date))\
    .stream()
```

---

## 9. Collections & Subcollections

### Subcollections

```python
# Create subcollection
db.collection('sessions').document('session-123')\
    .collection('messages').add({
        'text': 'Hello',
        'timestamp': firestore.SERVER_TIMESTAMP
    })

# Query subcollection
messages = db.collection('sessions').document('session-123')\
    .collection('messages')\
    .order_by('timestamp')\
    .stream()

# Collection group query (all subcollections with same name)
all_messages = db.collection_group('messages')\
    .where(filter=FieldFilter('text', '==', 'Hello'))\
    .stream()
```

---

## 10. Common Patterns

### Session Management Pattern

```python
class SessionManager:
    def __init__(self, db):
        self.db = db
        self.collection = db.collection('sessions')
    
    def create_session(self, user_id):
        session_ref = self.collection.document()
        session_ref.set({
            'user_id': user_id,
            'created_at': firestore.SERVER_TIMESTAMP,
            'last_activity': firestore.SERVER_TIMESTAMP,
            'messages': [],
            'status': 'active'
        })
        return session_ref.id
    
    def add_message(self, session_id, message):
        self.collection.document(session_id).update({
            'messages': firestore.ArrayUnion([{
                'text': message,
                'timestamp': datetime.now()
            }]),
            'last_activity': firestore.SERVER_TIMESTAMP
        })
    
    def get_active_sessions(self, user_id):
        return self.collection\
            .where(filter=FieldFilter('user_id', '==', user_id))\
            .where(filter=FieldFilter('status', '==', 'active'))\
            .order_by('last_activity', direction=firestore.Query.DESCENDING)\
            .stream()
    
    def close_session(self, session_id):
        self.collection.document(session_id).update({
            'status': 'closed',
            'closed_at': firestore.SERVER_TIMESTAMP
        })
```

---

## 11. Error Handling

```python
from google.api_core.exceptions import (
    NotFound, 
    AlreadyExists, 
    PermissionDenied,
    DeadlineExceeded
)

try:
    doc = db.collection('sessions').document('session-123').get()
    if doc.exists:
        print(doc.to_dict())
except NotFound:
    print("Document not found")
except PermissionDenied:
    print("No permission to access this document")
except DeadlineExceeded:
    print("Request timed out")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## 12. Best Practices

### ✅ DO

```python
# Use server timestamps
db.collection('sessions').add({
    'created_at': firestore.SERVER_TIMESTAMP  # ✅ Consistent across clients
})

# Use transactions for atomic updates
@firestore.transactional
def safe_update(transaction, doc_ref):
    snapshot = doc_ref.get(transaction=transaction)
    transaction.update(doc_ref, {'count': snapshot.get('count') + 1})

# Batch writes for multiple operations
batch = db.batch()
for i in range(100):
    ref = db.collection('sessions').document(f'session-{i}')
    batch.set(ref, {'index': i})
batch.commit()

# Index frequently queried fields
# (done in Firestore console or via composite indexes)
```

### ❌ DON'T

```python
# DON'T use client-side timestamps
db.collection('sessions').add({
    'created_at': datetime.now()  # ❌ Can be inconsistent
})

# DON'T query without indexes for complex queries
# This will fail if you haven't created composite index:
sessions = db.collection('sessions')\
    .where(filter=FieldFilter('status', '==', 'active'))\
    .where(filter=FieldFilter('priority', '>', 5))\
    .order_by('created_at')\
    .stream()

# DON'T use offset pagination for large datasets
sessions = db.collection('sessions').offset(10000).limit(10)  # ❌ Slow!
```

---

## 13. Performance Tips

```python
# ✅ Use limit to avoid fetching too much data
sessions = db.collection('sessions').limit(100).stream()

# ✅ Use select to fetch only needed fields
sessions = db.collection('sessions').select(['user_id', 'status']).stream()

# ✅ Use cursors for pagination (not offset)
query = db.collection('sessions').order_by('created_at').start_after(last_doc).limit(10)

# ✅ Denormalize data to avoid joins
# Store user info in session doc instead of referencing users collection
```

---

## Quick Reference

| Operation | Code |
|-----------|------|
| **Create** | `collection.add({...})` or `document.set({...})` |
| **Read** | `document.get()` or `collection.stream()` |
| **Update** | `document.update({...})` |
| **Delete** | `document.delete()` |
| **Where** | `.where(filter=FieldFilter('field', '==', 'value'))` |
| **Order** | `.order_by('field', direction=firestore.Query.DESCENDING)` |
| **Limit** | `.limit(10)` |
| **Pagination** | `.start_after(last_doc).limit(10)` |
| **Transaction** | `@firestore.transactional` |
| **Batch** | `batch = db.batch()` then `batch.commit()` |

---

**That's it! You're now a Firestore pro! 🚀**
