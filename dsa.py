"""
=============================================================================
Smart Lost & Found System - Core DSA Module (dsa.py)
=============================================================================
Course Project: Data Structures & Algorithms (BTech CSE 2nd Year)
Team Size: 2 Members

This module contains manual implementations of fundamental Data Structures
and Algorithms without relying on Python built-ins like sorted(), .sort(),
or bisect. Every algorithm is explained with its campus application, time
complexity, and space complexity.
=============================================================================
"""

import time
from typing import List, Dict, Any, Optional, Tuple


# =============================================================================
# PART 1: SORTING ALGORITHMS
# Applied to sort lost & found reports by:
# - item_name (alphabetical order)
# - date (chronological order)
# - item_id (numerical order for Binary Search)
# =============================================================================

def bubble_sort(items: List[Dict[str, Any]], key: str = "item_name", reverse: bool = False) -> Tuple[List[Dict[str, Any]], int, int, float]:
    """
    Bubble Sort Algorithm:
    --------------------
    Logic: Repeatedly steps through the list, compares adjacent elements,
    and swaps them if they are in the wrong order. An optimization flag
    ('swapped') stops execution early if the list becomes sorted before
    completing all passes.

    Campus Use Case:
    Sorting recently reported lost items by Date or Item Name for display
    in the student feed.

    Time Complexity:
    - Best Case:    O(n)   (when already sorted, early exit via flag)
    - Average Case: O(n^2)
    - Worst Case:   O(n^2) (reverse sorted)
    Space Complexity: O(1) in-place auxiliary space.
    """
    start_time = time.perf_counter()
    arr = list(items)  # Create a shallow copy to prevent mutating original directly
    n = len(arr)
    comparisons = 0
    swaps = 0

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            val_a = str(arr[j].get(key, "")).lower() if isinstance(arr[j].get(key), str) else (arr[j].get(key) or 0)
            val_b = str(arr[j + 1].get(key, "")).lower() if isinstance(arr[j + 1].get(key), str) else (arr[j + 1].get(key) or 0)
            
            comparisons += 1
            condition = (val_a < val_b) if reverse else (val_a > val_b)
            if condition:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                swapped = True
        
        # If no two elements were swapped by inner loop, array is sorted
        if not swapped:
            break

    elapsed_time_ms = (time.perf_counter() - start_time) * 1000
    return arr, comparisons, swaps, elapsed_time_ms


def insertion_sort(items: List[Dict[str, Any]], key: str = "date", reverse: bool = False) -> Tuple[List[Dict[str, Any]], int, int, float]:
    """
    Insertion Sort Algorithm:
    -----------------------
    Logic: Builds the sorted array one item at a time. It takes an element
    and shifts all greater elements in the sorted portion to the right
    to make space for insertion.

    Campus Use Case:
    Ideal when new lost items are continuously reported throughout the day.
    As each new report arrives, it can be efficiently inserted into an
    already sorted list of daily reports.

    Time Complexity:
    - Best Case:    O(n)   (already sorted)
    - Average Case: O(n^2)
    - Worst Case:   O(n^2) (reverse sorted)
    Space Complexity: O(1) auxiliary space.
    """
    start_time = time.perf_counter()
    arr = list(items)
    n = len(arr)
    comparisons = 0
    shifts = 0

    for i in range(1, n):
        current_item = arr[i]
        current_val = str(current_item.get(key, "")).lower() if isinstance(current_item.get(key), str) else (current_item.get(key) or 0)
        j = i - 1

        while j >= 0:
            comparisons += 1
            compare_val = str(arr[j].get(key, "")).lower() if isinstance(arr[j].get(key), str) else (arr[j].get(key) or 0)
            condition = (compare_val < current_val) if reverse else (compare_val > current_val)
            
            if condition:
                arr[j + 1] = arr[j]
                shifts += 1
                j -= 1
            else:
                break
        
        arr[j + 1] = current_item

    elapsed_time_ms = (time.perf_counter() - start_time) * 1000
    return arr, comparisons, shifts, elapsed_time_ms


def selection_sort(items: List[Dict[str, Any]], key: str = "item_id", reverse: bool = False) -> Tuple[List[Dict[str, Any]], int, int, float]:
    """
    Selection Sort Algorithm:
    -----------------------
    Logic: Divides the list into a sorted and unsorted region. In each pass,
    it finds the minimum (or maximum) element from the unsorted region
    and swaps it to the boundary index.

    Campus Use Case:
    Used when memory write operations are costly, as Selection Sort
    guarantees at most O(n) swaps.

    Time Complexity:
    - Best Case:    O(n^2)
    - Average Case: O(n^2)
    - Worst Case:   O(n^2)
    Space Complexity: O(1) auxiliary space.
    """
    start_time = time.perf_counter()
    arr = list(items)
    n = len(arr)
    comparisons = 0
    swaps = 0

    for i in range(n):
        target_idx = i
        for j in range(i + 1, n):
            val_target = str(arr[target_idx].get(key, "")).lower() if isinstance(arr[target_idx].get(key), str) else (arr[target_idx].get(key) or 0)
            val_j = str(arr[j].get(key, "")).lower() if isinstance(arr[j].get(key), str) else (arr[j].get(key) or 0)
            
            comparisons += 1
            condition = (val_j > val_target) if reverse else (val_j < val_target)
            if condition:
                target_idx = j

        if target_idx != i:
            arr[i], arr[target_idx] = arr[target_idx], arr[i]
            swaps += 1

    elapsed_time_ms = (time.perf_counter() - start_time) * 1000
    return arr, comparisons, swaps, elapsed_time_ms


# =============================================================================
# PART 2: SEARCHING ALGORITHMS
# Applied to search campus reports:
# - Linear Search: Search by keywords across multiple fields (name, location, category).
# - Binary Search: High-speed O(log n) lookup by item ID on a sorted array.
# =============================================================================

def linear_search_items(items: List[Dict[str, Any]], keyword: str, fields: Optional[List[str]] = None) -> Tuple[List[Dict[str, Any]], int, float]:
    """
    Linear Search Algorithm:
    -----------------------
    Logic: Sequentially checks each element of the list from index 0 to n-1
    until all matching records are gathered.

    Campus Use Case:
    Students searching for lost items by typing flexible keywords like "water bottle",
    "library", or "laptop" across multiple attributes without requiring pre-sorted data.

    Time Complexity:
    - Best Case:    O(1) (found at first index)
    - Average Case: O(n)
    - Worst Case:   O(n) (scans entire list)
    Space Complexity: O(k) where k is the number of matching records found.
    """
    if fields is None:
        fields = ["item_name", "category", "location", "description"]

    start_time = time.perf_counter()
    query = keyword.strip().lower()
    matches = []
    comparisons = 0

    for item in items:
        matched = False
        for field in fields:
            comparisons += 1
            field_val = str(item.get(field, "")).lower()
            if query in field_val:
                matched = True
                break
        if matched:
            matches.append(item)

    elapsed_time_ms = (time.perf_counter() - start_time) * 1000
    return matches, comparisons, elapsed_time_ms


def binary_search_by_id(items: List[Dict[str, Any]], target_id: int) -> Tuple[Optional[Dict[str, Any]], int, List[int], float]:
    """
    Binary Search Algorithm:
    -----------------------
    Logic: Works only on sorted arrays. Divides the search interval in half
    at each step by comparing the target with the middle element.
    If target is less, narrow to left half; if greater, right half.

    Campus Use Case:
    Campus administrators and students instantly looking up an official report
    by its Unique Report ID (e.g., retrieving details for item #42 out of 10,000).

    Prerequisite:
    Records must be sorted by `item_id`. We sort them first using our
    custom Selection/Insertion sort.

    Time Complexity:
    - Best Case:    O(1) (target is at exact middle)
    - Average Case: O(log n)
    - Worst Case:   O(log n)
    Space Complexity: O(1) iterative space.
    """
    start_time = time.perf_counter()
    
    # Sort array by item_id using our custom insertion sort
    sorted_items, _, _, _ = insertion_sort(items, key="item_id")
    
    low = 0
    high = len(sorted_items) - 1
    comparisons = 0
    step_history = []  # stores mid indices visited for visual tracing

    found_item = None
    while low <= high:
        mid = (low + high) // 2
        comparisons += 1
        step_history.append(mid)
        
        mid_id = int(sorted_items[mid].get("item_id", 0))

        if mid_id == target_id:
            found_item = sorted_items[mid]
            break
        elif mid_id < target_id:
            low = mid + 1
        else:
            high = mid - 1

    elapsed_time_ms = (time.perf_counter() - start_time) * 1000
    return found_item, comparisons, step_history, elapsed_time_ms


# =============================================================================
# PART 3: SINGLY LINKED LIST
# Applied to manage "Recently Reported Items" and temporary feeds
# without array reallocation overhead.
# =============================================================================

class Node:
    """A Node in a Singly Linked List representing a single lost/found item."""
    def __init__(self, data: Dict[str, Any]):
        self.data: Dict[str, Any] = data
        self.next: Optional['Node'] = None


class SinglyLinkedList:
    """
    Singly Linked List Implementation:
    --------------------------------
    A linear collection of data elements whose order is not given by their
    physical placement in memory. Each element points to the next.

    Campus Use Case:
    Maintaining a dynamically growing feed of 'Recently Reported Items'.
    When a student submits a new report, it is inserted at the head in O(1) time.

    Operations & Complexities:
    - Insert at Head: O(1)
    - Insert at Tail: O(n) (or O(1) if tail pointer maintained)
    - Delete by ID:   O(n)
    - Traversal:      O(n)
    Space Complexity: O(n) with 1 pointer per node.
    """
    def __init__(self):
        self.head: Optional[Node] = None
        self._size: int = 0

    def insert_head(self, data: Dict[str, Any]) -> None:
        """Insert new report at beginning of the list in O(1) time."""
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self._size += 1

    def insert_tail(self, data: Dict[str, Any]) -> None:
        """Insert new report at the end of the list."""
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            curr = self.head
            while curr.next:
                curr = curr.next
            curr.next = new_node
        self._size += 1

    def delete_by_id(self, item_id: int) -> bool:
        """
        Delete a report by item_id (e.g. when an item is claimed or deleted).
        Returns True if deleted, False if not found.
        """
        curr = self.head
        prev = None

        while curr:
            if int(curr.data.get("item_id", 0)) == item_id:
                if prev is None:
                    # Deleting head node
                    self.head = curr.next
                else:
                    prev.next = curr.next
                self._size -= 1
                return True
            prev = curr
            curr = curr.next

        return False

    def traverse(self) -> List[Dict[str, Any]]:
        """Traverse the entire linked list and return items."""
        items = []
        curr = self.head
        while curr:
            items.append(curr.data)
            curr = curr.next
        return items

    def to_list(self) -> List[Dict[str, Any]]:
        """Alias for traverse() for pythonic list output."""
        return self.traverse()

    def get_recent(self, limit: int = 6) -> List[Dict[str, Any]]:
        """Retrieve top 'limit' recent items from the head of the list."""
        recent = []
        curr = self.head
        count = 0
        while curr and count < limit:
            recent.append(curr.data)
            curr = curr.next
            count += 1
        return recent

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self.head is None


# =============================================================================
# PART 4: BINARY SEARCH TREE (BST)
# Applied for structured indexing and efficient O(log n) retrieval of items.
# Supports insertion, searching, deletion, and inorder traversal.
# =============================================================================

class BSTNode:
    """A Node in a Binary Search Tree."""
    def __init__(self, key: int, data: Dict[str, Any]):
        self.key: int = key  # item_id used as primary search key
        self.data: Dict[str, Any] = data
        self.left: Optional['BSTNode'] = None
        self.right: Optional['BSTNode'] = None


class BinarySearchTree:
    """
    Binary Search Tree (BST) Implementation:
    --------------------------------------
    A node-based binary tree data structure where each node has at most two children:
    - Left subtree contains only nodes with keys < node's key.
    - Right subtree contains only nodes with keys > node's key.

    Campus Use Case:
    Maintains an in-memory index of all campus reports. Allows campus security
    and students to search for any item by its ID in average O(log n) time,
    and produce sorted listings via Inorder Traversal.

    Operations & Complexities:
    - Search:            Average O(log n), Worst O(n) (skewed tree)
    - Insertion:         Average O(log n), Worst O(n)
    - Deletion:          Average O(log n), Worst O(n)
    - Inorder Traversal: O(n) -> always yields elements in strictly sorted order!
    Space Complexity: O(n) for storing n items.
    """
    def __init__(self):
        self.root: Optional[BSTNode] = None
        self.node_count: int = 0

    def insert(self, data: Dict[str, Any], key: Optional[int] = None) -> None:
        """Insert a report into the BST using item_id as the key."""
        if key is None:
            key = int(data.get("item_id", 0))

        new_node = BSTNode(key, data)
        if not self.root:
            self.root = new_node
            self.node_count += 1
            return

        curr = self.root
        while True:
            if key < curr.key:
                if curr.left is None:
                    curr.left = new_node
                    self.node_count += 1
                    break
                curr = curr.left
            elif key > curr.key:
                if curr.right is None:
                    curr.right = new_node
                    self.node_count += 1
                    break
                curr = curr.right
            else:
                # Key already exists: update payload
                curr.data = data
                break

    def search(self, key: int) -> Tuple[Optional[Dict[str, Any]], int, List[int]]:
        """
        Search for an item by key (item_id).
        Returns (item_data, comparisons_count, path_keys_traversed).
        """
        comparisons = 0
        path = []
        curr = self.root

        while curr:
            comparisons += 1
            path.append(curr.key)
            if key == curr.key:
                return curr.data, comparisons, path
            elif key < curr.key:
                curr = curr.left
            else:
                curr = curr.right

        return None, comparisons, path

    def _min_value_node(self, node: BSTNode) -> BSTNode:
        """Helper to find node with minimum key value in a subtree."""
        curr = node
        while curr.left is not None:
            curr = curr.left
        return curr

    def delete(self, key: int) -> bool:
        """
        Delete a node with the given key from the BST.
        Handles three cases:
        1. Node with no child (leaf): Simply remove.
        2. Node with one child: Replace node with its child.
        3. Node with two children: Replace with inorder successor (min in right subtree).
        """
        deleted_flag = [False]

        def _delete_recursive(root: Optional[BSTNode], target_key: int) -> Optional[BSTNode]:
            if root is None:
                return None

            if target_key < root.key:
                root.left = _delete_recursive(root.left, target_key)
            elif target_key > root.key:
                root.right = _delete_recursive(root.right, target_key)
            else:
                # Target node found
                deleted_flag[0] = True

                # Case 1 & 2: Zero or one child
                if root.left is None:
                    return root.right
                elif root.right is None:
                    return root.left

                # Case 3: Two children
                successor = self._min_value_node(root.right)
                root.key = successor.key
                root.data = successor.data
                root.right = _delete_recursive(root.right, successor.key)

            return root

        self.root = _delete_recursive(self.root, key)
        if deleted_flag[0]:
            self.node_count -= 1
        return deleted_flag[0]

    def inorder_traversal(self) -> List[Dict[str, Any]]:
        """
        Inorder Traversal (Left -> Root -> Right):
        Always produces items sorted in ascending order of key!
        """
        result = []

        def _inorder(node: Optional[BSTNode]):
            if node:
                _inorder(node.left)
                result.append(node.data)
                _inorder(node.right)

        _inorder(self.root)
        return result

    def preorder_traversal(self) -> List[Dict[str, Any]]:
        """Preorder Traversal (Root -> Left -> Right): Useful for tree copying/serialization."""
        result = []

        def _preorder(node: Optional[BSTNode]):
            if node:
                result.append(node.data)
                _preorder(node.left)
                _preorder(node.right)

        _preorder(self.root)
        return result

    def postorder_traversal(self) -> List[Dict[str, Any]]:
        """Postorder Traversal (Left -> Right -> Root): Useful for tree deletion."""
        result = []

        def _postorder(node: Optional[BSTNode]):
            if node:
                _postorder(node.left)
                _postorder(node.right)
                result.append(node.data)

        _postorder(self.root)
        return result

    def to_hierarchy_dict(self) -> Optional[Dict[str, Any]]:
        """
        Converts the BST into a nested dictionary structure for frontend
        visualization (e.g. Canvas or DOM-based Tree rendering).
        """
        def _build_dict(node: Optional[BSTNode]):
            if not node:
                return None
            return {
                "key": node.key,
                "name": node.data.get("item_name", f"ID {node.key}"),
                "category": node.data.get("category", ""),
                "left": _build_dict(node.left),
                "right": _build_dict(node.right)
            }
        return _build_dict(self.root)
