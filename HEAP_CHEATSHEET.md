# HEAP CHEATSHEET - Complete Guide

---

## **What is a Heap?**

**Definition:** A specialized tree-based data structure that maintains a partial ordering.

**Visual:**
```
Min Heap:               Max Heap:
    1                       9
   / \                     / \
  3   2                   7   8
 / \                     / \
5   4                   4   5
```

**Key Property:**
- **Min Heap:** Parent ≤ Children (smallest at root)
- **Max Heap:** Parent ≥ Children (largest at root)

**NOT a sorted array!** Just maintains parent-child relationship.

---

## **Python Heap (heapq) - Min Heap Only**

Python's `heapq` module only provides **min heap** by default.

```python
import heapq

heap = []  # Empty heap (just a list)
```

---

## **Core Operations**

### **1. heappush - Add Element**
```python
heapq.heappush(heap, 5)
heapq.heappush(heap, 3)
heapq.heappush(heap, 7)

print(heap)  # [3, 5, 7] - min heap property maintained
```

**Time:** O(log n)  
**What it does:** Adds element and "bubbles up" to maintain heap property

---

### **2. heappop - Remove Smallest**
```python
heap = [1, 3, 2, 5, 4]

smallest = heapq.heappop(heap)
print(smallest)  # 1
print(heap)      # [2, 3, 4, 5]
```

**Time:** O(log n)  
**What it does:** Removes root, moves last to root, "bubbles down"

---

### **3. heappushpop - Push then Pop**
```python
heap = [1, 3, 5]
result = heapq.heappushpop(heap, 2)
# Equivalent to: push(2), then pop()
print(result)  # 1 (smallest between existing and new)
print(heap)    # [2, 3, 5]
```

**Time:** O(log n)  
**Use:** More efficient than separate push + pop

---

### **4. heapreplace - Pop then Push**
```python
heap = [1, 3, 5]
result = heapq.heapreplace(heap, 2)
# Equivalent to: pop(), then push(2)
print(result)  # 1
print(heap)    # [2, 3, 5]
```

**Time:** O(log n)

---

### **5. heapify - Convert List to Heap**
```python
nums = [5, 2, 8, 1, 9]
heapq.heapify(nums)
print(nums)  # [1, 2, 8, 5, 9] - min heap
```

**Time:** O(n)  
**Use:** Convert existing list to heap in-place

---

### **6. nlargest - Get Top K**
```python
nums = [5, 1, 9, 3, 7, 2]

top3 = heapq.nlargest(3, nums)
print(top3)  # [9, 7, 5] - descending order
```

**Time:** O(n log k)  
**Use:** Get k largest elements efficiently

---

### **7. nsmallest - Get Bottom K**
```python
nums = [5, 1, 9, 3, 7, 2]

bottom3 = heapq.nsmallest(3, nums)
print(bottom3)  # [1, 2, 3] - ascending order
```

**Time:** O(n log k)

---

### **8. nlargest with Custom Key**
```python
count = {'a': 5, 'b': 3, 'c': 8, 'd': 1}

# Get 2 keys with highest counts
top2 = heapq.nlargest(2, count.keys(), key=count.get)
print(top2)  # ['c', 'a'] (counts: 8, 5)

# With lambda
top2 = heapq.nlargest(2, count.keys(), key=lambda x: count[x])
```

---

## **Max Heap in Python (Trick)**

Python doesn't have built-in max heap. **Solution: Negate values!**

```python
# Max heap simulation
max_heap = []
for num in [5, 1, 9, 3]:
    heapq.heappush(max_heap, -num)  # Negate!

# Pop largest
largest = -heapq.heappop(max_heap)
print(largest)  # 9

# View actual values
actual_values = [-x for x in max_heap]
print(actual_values)  # [5, 3, 1]
```

**Why it works:**
```
Original: 9 > 5 > 3 > 1
Negated:  -9 < -5 < -3 < -1
Min heap of negatives = Max heap of originals!
```

---

## **Common Patterns**

### **Pattern 1: Top K Frequent Elements**

```python
from collections import Counter
import heapq

def topKFrequent(nums, k):
    count = Counter(nums)
    return heapq.nlargest(k, count.keys(), key=count.get)

# Example
nums = [1,1,1,2,2,3]
print(topKFrequent(nums, 2))  # [1, 2]
```

**Time:** O(n log k)

---

### **Pattern 2: Kth Largest Element**

```python
def findKthLargest(nums, k):
    # Min heap of size k
    heap = []
    for num in nums:
        heapq.heappush(heap, num)
        if len(heap) > k:
            heapq.heappop(heap)  # Remove smallest
    
    return heap[0]  # Smallest in heap = kth largest

# Example
nums = [3,2,1,5,6,4]
print(findKthLargest(nums, 2))  # 5
```

**Time:** O(n log k)  
**Key Insight:** Keep heap of k largest. Smallest in heap = kth largest.

---

### **Pattern 3: Merge K Sorted Arrays**

```python
def mergeKArrays(arrays):
    heap = []
    result = []
    
    # Add first element from each array
    for i, arr in enumerate(arrays):
        if arr:
            heapq.heappush(heap, (arr[0], i, 0))
            # (value, array_index, element_index)
    
    # Extract min and add next from same array
    while heap:
        val, arr_idx, elem_idx = heapq.heappop(heap)
        result.append(val)
        
        # Add next element from same array
        if elem_idx + 1 < len(arrays[arr_idx]):
            next_val = arrays[arr_idx][elem_idx + 1]
            heapq.heappush(heap, (next_val, arr_idx, elem_idx + 1))
    
    return result

# Example
arrays = [[1,4,7], [2,5,8], [3,6,9]]
print(mergeKArrays(arrays))  # [1,2,3,4,5,6,7,8,9]
```

**Time:** O(N log k) where N = total elements, k = number of arrays

---

### **Pattern 4: Running Median (Two Heaps)**

```python
class MedianFinder:
    def __init__(self):
        self.small = []  # Max heap (negated)
        self.large = []  # Min heap
    
    def addNum(self, num):
        # Add to max heap (small)
        heapq.heappush(self.small, -num)
        
        # Balance: largest in small ≤ smallest in large
        if self.small and self.large and (-self.small[0] > self.large[0]):
            val = -heapq.heappop(self.small)
            heapq.heappush(self.large, val)
        
        # Keep sizes balanced
        if len(self.small) > len(self.large) + 1:
            val = -heapq.heappop(self.small)
            heapq.heappush(self.large, val)
        
        if len(self.large) > len(self.small):
            val = heapq.heappop(self.large)
            heapq.heappush(self.small, -val)
    
    def findMedian(self):
        if len(self.small) > len(self.large):
            return -self.small[0]
        return (-self.small[0] + self.large[0]) / 2

# Usage
mf = MedianFinder()
mf.addNum(1)
mf.addNum(2)
print(mf.findMedian())  # 1.5
mf.addNum(3)
print(mf.findMedian())  # 2
```

**Time:** O(log n) per add, O(1) per median

---

## **When to Use Heap?**

### **✅ Use Heap When:**
- Finding kth largest/smallest (k << n)
- Top k elements
- Merge k sorted lists
- Running median
- Streaming data (online algorithm)
- Priority queue needed

### **❌ Don't Use Heap When:**
- Need full sorted array
- Need to search for specific element
- Need random access
- k is close to n (just sort instead)

---

## **Time Complexity Summary**

| Operation | Time | Space |
|-----------|------|-------|
| heappush | O(log n) | O(1) |
| heappop | O(log n) | O(1) |
| heappushpop | O(log n) | O(1) |
| heapify | O(n) | O(1) |
| nlargest(k) | O(n log k) | O(k) |
| nsmallest(k) | O(n log k) | O(k) |
| peek (heap[0]) | O(1) | O(1) |

---

## **Heap vs Sorting**

```python
nums = [3, 1, 4, 1, 5, 9, 2, 6]
k = 3

# Sorting: O(n log n)
sorted_nums = sorted(nums)
top_k = sorted_nums[-k:]  # [5, 6, 9]

# Heap: O(n log k)  ← Better when k << n
top_k = heapq.nlargest(k, nums)  # [9, 6, 5]
```

**When k=3, n=1000:**
- Sorting: 1000 × log(1000) ≈ 10,000 ops
- Heap: 1000 × log(3) ≈ 1,585 ops (6x faster!)

---

## **Important Insights**

### **1. Min Heap for Max Elements**
> "Use MIN heap to track k LARGEST elements"

```python
# Why? Root = smallest in heap = kth largest overall
heap = []
for num in nums:
    heappush(heap, num)
    if len(heap) > k:
        heappop(heap)  # Remove smallest
# heap[0] = kth largest
```

### **2. Heap is NOT Sorted**
```python
heap = [1, 3, 2, 5, 4]
# This is valid min heap!
# Only guarantees: parent < children
# NOT fully sorted
```

### **3. Can Store Tuples**
```python
# First element is priority
heap = []
heappush(heap, (5, 'task1'))
heappush(heap, (2, 'task2'))
heappush(heap, (8, 'task3'))

# Pop by priority
priority, task = heappop(heap)
print(task)  # 'task2' (priority 2 is smallest)
```

---

## **Interview Problems**

### **Easy:**
1. Kth Largest Element in Array
2. Last Stone Weight
3. Merge Two Sorted Lists

### **Medium:**
4. Top K Frequent Elements ⭐
5. Kth Largest Element in Stream
6. Merge K Sorted Lists ⭐
7. Find Median from Data Stream ⭐
8. Task Scheduler

### **Hard:**
9. Sliding Window Median
10. Find Median from Data Stream

---

## **Quick Reference**

```python
import heapq

# Create heap
heap = []

# Add elements
heapq.heappush(heap, 5)

# Remove smallest
smallest = heapq.heappop(heap)

# Peek smallest
smallest = heap[0]  # Don't pop

# Convert list to heap
heapq.heapify(nums)

# Top k elements
top_k = heapq.nlargest(k, nums)
bottom_k = heapq.nsmallest(k, nums)

# With custom key
top_k = heapq.nlargest(k, items, key=lambda x: x.value)

# Max heap (negate values)
heapq.heappush(max_heap, -value)
largest = -heapq.heappop(max_heap)
```

---

## **Common Mistakes**

### **❌ Mistake 1: Confusing Min/Max**
```python
# Want largest element
heap = [1, 3, 5]
print(heap[0])  # 1 ← WRONG! This is smallest
```

### **❌ Mistake 2: Modifying Heap Directly**
```python
heap[0] = 10  # ❌ Breaks heap property!
heapq.heappush(heap, 10)  # ✅ Correct
```

### **❌ Mistake 3: Forgetting to Negate for Max Heap**
```python
# Want max heap
heapq.heappush(heap, 5)  # ❌ Still min heap!
heapq.heappush(heap, -5)  # ✅ Correct for max
```

---

## **Summary**

**Core Concept:**
- Heap = Tree that maintains parent-child ordering
- Python has MIN heap only
- Use negation for MAX heap

**Key Operations:**
- `heappush` → Add (O(log n))
- `heappop` → Remove smallest (O(log n))
- `nlargest/nsmallest` → Top k (O(n log k))

**When to Use:**
- Top k problems
- Streaming data
- Merge sorted lists
- Running median

**Magic Insight:**
> "MIN heap of size k tracks k LARGEST elements.  
> Root = kth largest (the boundary)."

---

**Good luck with interviews! 🚀**
