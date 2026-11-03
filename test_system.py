"""
Smart Lost & Found System - Comprehensive Verification Suite
Tests database, DSA algorithms, matching system, and Flask routes.
"""

import unittest
import database as db
import dsa
import matching
from app import app


class TestSmartLostFound(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_dsa_sorting(self):
        """Test Bubble, Insertion, and Selection sort on item dictionaries."""
        data = [
            {"item_id": 5, "item_name": "Zebra Pen", "date": "2026-10-30"},
            {"item_id": 2, "item_name": "Apple Charger", "date": "2026-10-28"},
            {"item_id": 8, "item_name": "MacBook Pro", "date": "2026-11-01"},
        ]

        # Bubble sort by name
        sorted_bubble, comps_b, swaps_b, _ = dsa.bubble_sort(data, key="item_name")
        self.assertEqual([x["item_name"] for x in sorted_bubble], ["Apple Charger", "MacBook Pro", "Zebra Pen"])

        # Insertion sort by date
        sorted_ins, comps_i, shifts_i, _ = dsa.insertion_sort(data, key="date")
        self.assertEqual([x["date"] for x in sorted_ins], ["2026-10-28", "2026-10-30", "2026-11-01"])

        # Selection sort by item_id
        sorted_sel, comps_s, swaps_s, _ = dsa.selection_sort(data, key="item_id")
        self.assertEqual([x["item_id"] for x in sorted_sel], [2, 5, 8])

    def test_dsa_searching(self):
        """Test Linear Search and Binary Search."""
        data = [
            {"item_id": 10, "item_name": "Blue Bottle", "category": "Others", "location": "Library"},
            {"item_id": 25, "item_name": "Dell Laptop", "category": "Electronics", "location": "Lab 3"},
            {"item_id": 40, "item_name": "Campus ID Card", "category": "ID & Cards", "location": "Cafeteria"},
        ]

        # Linear search for "Laptop"
        linear_results, comps, _ = dsa.linear_search_items(data, "Laptop")
        self.assertEqual(len(linear_results), 1)
        self.assertEqual(linear_results[0]["item_id"], 25)

        # Binary search for ID 25
        found, comps_bin, steps, _ = dsa.binary_search_by_id(data, 25)
        self.assertIsNotNone(found)
        self.assertEqual(found["item_id"], 25)

        # Binary search for non-existent ID
        not_found, _, _, _ = dsa.binary_search_by_id(data, 999)
        self.assertIsNone(not_found)

    def test_dsa_linked_list(self):
        """Test Singly Linked List operations."""
        ll = dsa.SinglyLinkedList()
        self.assertTrue(ll.is_empty())

        ll.insert_head({"item_id": 1, "item_name": "First"})
        ll.insert_head({"item_id": 2, "item_name": "Second (New Head)"})
        ll.insert_tail({"item_id": 3, "item_name": "Third (Tail)"})

        items = ll.to_list()
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]["item_id"], 2)
        self.assertEqual(items[2]["item_id"], 3)

        # Recent items limit
        recent = ll.get_recent(2)
        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[0]["item_id"], 2)

        # Deletion
        deleted = ll.delete_by_id(1)
        self.assertTrue(deleted)
        self.assertEqual(len(ll.to_list()), 2)

    def test_dsa_bst(self):
        """Test Binary Search Tree operations."""
        bst = dsa.BinarySearchTree()
        bst.insert({"item_id": 50, "item_name": "Fifty"})
        bst.insert({"item_id": 30, "item_name": "Thirty"})
        bst.insert({"item_id": 70, "item_name": "Seventy"})
        bst.insert({"item_id": 20, "item_name": "Twenty"})

        # Search existing
        item, comps, path = bst.search(30)
        self.assertIsNotNone(item)
        self.assertEqual(item["item_name"], "Thirty")

        # Inorder traversal (must be strictly sorted!)
        inorder = bst.inorder_traversal()
        keys = [x["item_id"] for x in inorder]
        self.assertEqual(keys, [20, 30, 50, 70])

        # Deletion
        del_res = bst.delete(30)
        self.assertTrue(del_res)
        inorder_after = bst.inorder_traversal()
        self.assertEqual([x["item_id"] for x in inorder_after], [20, 50, 70])

    def test_matching_algorithm(self):
        """Test item comparison logic."""
        lost = {
            "item_id": 1,
            "item_name": "Dell XPS Laptop",
            "category": "Electronics",
            "description": "Silver laptop with stickers",
            "location": "Computer Lab 3",
            "date": "2026-10-28",
            "report_type": "Lost"
        }

        found_match = {
            "item_id": 2,
            "item_name": "Dell Laptop",
            "category": "Electronics",
            "description": "Found silver laptop in lab 3",
            "location": "Computer Lab 3",
            "date": "2026-10-28",
            "report_type": "Found"
        }

        is_match, score, reason = matching.compare_items(lost, found_match)
        self.assertTrue(is_match)
        self.assertGreaterEqual(score, 60)
        self.assertIn("category", reason.lower())

    def test_flask_routes(self):
        """Test critical Flask routes."""
        res_home = self.app.get("/")
        self.assertEqual(res_home.status_code, 200)

        res_search = self.app.get("/search?q=Dell&search_algo=linear&sort_algo=bubble")
        self.assertEqual(res_search.status_code, 200)

        res_matches = self.app.get("/matches")
        self.assertEqual(res_matches.status_code, 200)

        res_vis = self.app.get("/dsa-visualizer")
        self.assertEqual(res_vis.status_code, 200)

        res_item = self.app.get("/item/1")
        self.assertEqual(res_item.status_code, 200)

        # Test registration
        res_reg = self.app.post("/register", data={
            "name": "New Student",
            "email": "new.student@campus.edu",
            "student_id": "23BCSE999",
            "password": "mypassword123",
            "confirm_password": "mypassword123"
        }, follow_redirects=True)
        self.assertEqual(res_reg.status_code, 200)

        # Test login
        res_login = self.app.post("/login", data={
            "email": "aarav.sharma@campus.edu",
            "password": "password123"
        }, follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)

        # Test report lost submission
        res_lost = self.app.post("/report-lost", data={
            "item_name": "Test Scientific Calculator",
            "category": "Electronics",
            "description": "Black calculator with cover",
            "location": "Seminar Hall 2",
            "date": "2026-11-03"
        }, follow_redirects=True)
        self.assertEqual(res_lost.status_code, 200)

        # Test report found submission
        res_found = self.app.post("/report-found", data={
            "item_name": "Found Scientific Calculator",
            "category": "Electronics",
            "description": "Black calculator picked up from seminar hall 2",
            "location": "Seminar Hall 2",
            "date": "2026-11-03"
        }, follow_redirects=True)
        self.assertEqual(res_found.status_code, 200)

        # Test API sort
        res_api = self.app.post("/api/dsa/sort", json={
            "array": [50, 20, 80, 10],
            "algorithm": "bubble"
        })
        self.assertEqual(res_api.status_code, 200)
        self.assertEqual(res_api.get_json()["sorted"], [10, 20, 50, 80])


if __name__ == "__main__":
    unittest.main()
