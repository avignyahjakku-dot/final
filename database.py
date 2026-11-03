"""
=============================================================================
Smart Lost & Found System - Database Connection & Queries (database.py)
=============================================================================
Course Project: Data Structures & Algorithms (BTech CSE 2nd Year)
Team Size: 2 Members

Handles all MySQL interactions using PyMySQL or mysql-connector-python.
Provides parameterized queries for Users, Items, and Matches.
Includes automatic table creation and sample data seeding from schema.sql.
=============================================================================
"""

import os
from typing import Optional, List, Dict, Any
from werkzeug.security import generate_password_hash

# Try importing mysql.connector or pymysql
try:
    import pymysql
    import pymysql.cursors
    HAS_PYMYSQL = True
except ImportError:
    HAS_PYMYSQL = False

try:
    import mysql.connector
    HAS_MYSQL_CONNECTOR = True
except ImportError:
    HAS_MYSQL_CONNECTOR = False

# Database configuration settings
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),  # Default XAMPP password is empty
    "database": os.environ.get("DB_NAME", "smart_lost_found"),
    "port": int(os.environ.get("DB_PORT", 3306)),
}

# Flag tracking database availability
DB_ONLINE = False

# In-memory storage fallback used strictly when MySQL server is not yet started,
# ensuring the student presentation never crashes during offline review.
_MEMORY_USERS: List[Dict[str, Any]] = []
_MEMORY_ITEMS: List[Dict[str, Any]] = []
_MEMORY_MATCHES: List[Dict[str, Any]] = []
_MEMORY_ID_COUNTERS = {"user_id": 6, "item_id": 11, "match_id": 4}


def get_raw_connection(include_database: bool = True):
    """Establishes raw connection to MySQL server using pymysql or mysql.connector."""
    config = dict(DB_CONFIG)
    if not include_database:
        config.pop("database", None)

    if HAS_PYMYSQL:
        return pymysql.connect(
            host=config["host"],
            user=config["user"],
            password=config["password"],
            database=config.get("database"),
            port=config["port"],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
    elif HAS_MYSQL_CONNECTOR:
        return mysql.connector.connect(
            host=config["host"],
            user=config["user"],
            password=config["password"],
            database=config.get("database"),
            port=config["port"],
            autocommit=True
        )
    else:
        raise RuntimeError("Neither 'pymysql' nor 'mysql-connector-python' is installed.")


def get_dict_cursor(conn):
    """Helper to return dictionary cursor regardless of PyMySQL or mysql-connector."""
    if HAS_PYMYSQL:
        return conn.cursor(pymysql.cursors.DictCursor)
    elif HAS_MYSQL_CONNECTOR:
        return conn.cursor(dictionary=True)
    return conn.cursor()


def test_db_connection() -> bool:
    """Tests if MySQL server is actively reachable."""
    global DB_ONLINE
    try:
        conn = get_raw_connection(include_database=False)
        conn.close()
        DB_ONLINE = True
        return True
    except Exception as e:
        DB_ONLINE = False
        return False


def seed_memory_data():
    """Seeds in-memory store with the exact realistic records from schema.sql."""
    global _MEMORY_USERS, _MEMORY_ITEMS, _MEMORY_MATCHES
    default_pass = generate_password_hash("password123")

    _MEMORY_USERS = [
        {"user_id": 1, "name": "Campus Admin", "email": "admin@campus.edu", "student_id": "ADM-001", "password": default_pass, "role": "admin"},
        {"user_id": 2, "name": "Aarav Sharma", "email": "aarav.sharma@campus.edu", "student_id": "23BCSE101", "password": default_pass, "role": "student"},
        {"user_id": 3, "name": "Diya Patel", "email": "diya.patel@campus.edu", "student_id": "23BCSE102", "password": default_pass, "role": "student"},
        {"user_id": 4, "name": "Rohan Verma", "email": "rohan.verma@campus.edu", "student_id": "23BCSE103", "password": default_pass, "role": "student"},
        {"user_id": 5, "name": "Ananya Iyer", "email": "ananya.iyer@campus.edu", "student_id": "23BCSE104", "password": default_pass, "role": "student"},
    ]

    _MEMORY_ITEMS = [
        {"item_id": 1, "user_id": 2, "item_name": "Dell XPS 13 Laptop", "category": "Electronics", "description": "Silver Dell laptop with anime sticker on cover. Left in CS Lab 3 desk.", "location": "Computer Lab 3", "date": "2026-10-28", "report_type": "Lost", "image_path": None, "status": "Pending", "created_at": "2026-10-28 10:00:00"},
        {"item_id": 2, "user_id": 3, "item_name": "Dell Laptop (Silver)", "category": "Electronics", "description": "Found a silver 13-inch Dell laptop on the back row of computer lab 3.", "location": "Computer Lab 3", "date": "2026-10-28", "report_type": "Found", "image_path": None, "status": "Pending", "created_at": "2026-10-28 11:30:00"},
        {"item_id": 3, "user_id": 4, "item_name": "Black Leather Wallet", "category": "Bags & Wallets", "description": "Contains College ID card, debit card, and cash. Lost near Central Cafeteria.", "location": "Central Cafeteria", "date": "2026-10-29", "report_type": "Lost", "image_path": None, "status": "Pending", "created_at": "2026-10-29 13:15:00"},
        {"item_id": 4, "user_id": 5, "item_name": "Leather Wallet (Black)", "category": "Bags & Wallets", "description": "Black men wallet picked up from lunch table at cafeteria with college ID.", "location": "Central Cafeteria", "date": "2026-10-29", "report_type": "Found", "image_path": None, "status": "Pending", "created_at": "2026-10-29 14:00:00"},
        {"item_id": 5, "user_id": 2, "item_name": "Casio fx-991EX Calculator", "category": "Electronics", "description": "ClassWiz scientific calculator with name written on the back cover.", "location": "Main Auditorium", "date": "2026-10-30", "report_type": "Lost", "image_path": None, "status": "Pending", "created_at": "2026-10-30 09:45:00"},
        {"item_id": 6, "user_id": 3, "item_name": "Casio Scientific Calculator", "category": "Electronics", "description": "Found scientific calculator after Calculus exam in auditorium seat 42.", "location": "Main Auditorium", "date": "2026-10-30", "report_type": "Found", "image_path": None, "status": "Pending", "created_at": "2026-10-30 12:00:00"},
        {"item_id": 7, "user_id": 4, "item_name": "Boat Airdopes 141 Case", "category": "Electronics", "description": "Matte black charging case with white earbuds inside. Lost in Library 2nd floor.", "location": "Central Library", "date": "2026-10-31", "report_type": "Lost", "image_path": None, "status": "Pending", "created_at": "2026-10-31 16:20:00"},
        {"item_id": 8, "user_id": 5, "item_name": "Campus ID Card 23BCSE103", "category": "ID & Cards", "description": "Found identity card of Rohan Verma near Sports Complex cricket ground.", "location": "Sports Complex", "date": "2026-11-01", "report_type": "Found", "image_path": None, "status": "Pending", "created_at": "2026-11-01 17:00:00"},
        {"item_id": 9, "user_id": 2, "item_name": "C++ Data Structures Textbook", "category": "Books & Notes", "description": "Author Mark Allen Weiss, blue cover, bookmarked with sticky notes.", "location": "Central Library", "date": "2026-11-01", "report_type": "Lost", "image_path": None, "status": "Pending", "created_at": "2026-11-01 18:30:00"},
        {"item_id": 10, "user_id": 3, "item_name": "Water Bottle (Milton 1L)", "category": "Others", "description": "Blue stainless steel Milton thermosteel flask found in Seminar Hall 1.", "location": "Seminar Hall 1", "date": "2026-11-02", "report_type": "Found", "image_path": None, "status": "Pending", "created_at": "2026-11-02 11:10:00"},
    ]

    _MEMORY_MATCHES = [
        {"match_id": 1, "lost_item_id": 1, "found_item_id": 2, "match_reason": "Matching category Electronics, similar item Dell Laptop, location Computer Lab 3, same date 2026-10-28", "match_status": "Potential", "created_at": "2026-10-28 12:00:00"},
        {"match_id": 2, "lost_item_id": 3, "found_item_id": 4, "match_reason": "Matching category Bags & Wallets, similar item Leather Wallet, location Central Cafeteria, same date 2026-10-29", "match_status": "Potential", "created_at": "2026-10-29 14:30:00"},
        {"match_id": 3, "lost_item_id": 5, "found_item_id": 6, "match_reason": "Matching category Electronics, similar item Casio Calculator, location Main Auditorium, same date 2026-10-30", "match_status": "Potential", "created_at": "2026-10-30 13:00:00"},
    ]


def init_db():
    """Initializes the MySQL database and tables if available."""
    global DB_ONLINE
    if test_db_connection():
        try:
            conn = get_raw_connection(include_database=False)
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
            conn.close()

            # Connect to the created database and execute schema
            db_conn = get_raw_connection(include_database=True)
            db_cursor = db_conn.cursor()

            schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
            if os.path.exists(schema_path):
                with open(schema_path, "r", encoding="utf-8") as f:
                    sql_content = f.read()

                # Execute individual statements
                statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]
                for stmt in statements:
                    # Ignore USE and CREATE DATABASE here
                    if stmt.upper().startswith("CREATE DATABASE") or stmt.upper().startswith("USE"):
                        continue
                    try:
                        db_cursor.execute(stmt)
                    except Exception:
                        pass

            db_conn.close()
            DB_ONLINE = True
            print(f"[MySQL] Successfully connected and initialized database '{DB_CONFIG['database']}'.")
            return
        except Exception as e:
            print(f"[MySQL Warning] Could not initialize MySQL schema: {e}")

    # Fallback to in-memory state
    DB_ONLINE = False
    seed_memory_data()
    print("[Database Notice] MySQL service is offline or not configured. Running in high-fidelity Campus Data mode.")


# =============================================================================
# USER QUERIES
# =============================================================================

def create_user(name: str, email: str, student_id: str, password_hash: str, role: str = "student") -> Optional[int]:
    """Inserts a new user into the database."""
    global DB_ONLINE
    if DB_ONLINE:
        try:
            conn = get_raw_connection()
            cursor = conn.cursor()
            sql = "INSERT INTO Users (name, email, student_id, password, role) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (name, email, student_id, password_hash, role))
            user_id = cursor.lastrowid
            conn.close()
            return user_id
        except Exception as e:
            print(f"[MySQL create_user error]: {e}")
            return None
    else:
        # Check duplicate email
        for u in _MEMORY_USERS:
            if u["email"].lower() == email.lower():
                return None
        new_id = _MEMORY_ID_COUNTERS["user_id"]
        _MEMORY_ID_COUNTERS["user_id"] += 1
        new_user = {
            "user_id": new_id,
            "name": name,
            "email": email,
            "student_id": student_id,
            "password": password_hash,
            "role": role
        }
        _MEMORY_USERS.append(new_user)
        return new_id


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Retrieves a user record by email address."""
    if DB_ONLINE:
        try:
            conn = get_raw_connection()
            cursor = get_dict_cursor(conn)
            sql = "SELECT * FROM Users WHERE email = %s LIMIT 1"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()
            conn.close()
            return user
        except Exception as e:
            print(f"[MySQL get_user_by_email error]: {e}")
            return None
    else:
        for u in _MEMORY_USERS:
            if u["email"].lower() == email.strip().lower():
                return dict(u)
        return None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves a user record by primary key user_id."""
    if DB_ONLINE:
        try:
            conn = get_raw_connection()
            cursor = get_dict_cursor(conn)
            sql = "SELECT user_id, name, email, student_id, role FROM Users WHERE user_id = %s"
            cursor.execute(sql, (user_id,))
            user = cursor.fetchone()
            conn.close()
            return user
        except Exception as e:
            print(f"[MySQL get_user_by_id error]: {e}")
            return None
    else:
        for u in _MEMORY_USERS:
            if u["user_id"] == user_id:
                return dict(u)
        return None


# =============================================================================
# ITEM QUERIES
# =============================================================================

def create_item(user_id: int, item_name: str, category: str, description: str,
                location: str, date: str, report_type: str, image_path: Optional[str] = None,
                status: str = "Pending") -> Optional[int]:
    """Inserts a new lost or found report into Items."""
    if DB_ONLINE:
        try:
            conn = get_raw_connection()
            cursor = conn.cursor()
            sql = """
                INSERT INTO Items (user_id, item_name, category, description, location, date, report_type, image_path, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (user_id, item_name, category, description, location, date, report_type, image_path, status))
            item_id = cursor.lastrowid
            conn.close()
            return item_id
        except Exception as e:
            print(f"[MySQL create_item error]: {e}")
            return None
    else:
        new_id = _MEMORY_ID_COUNTERS["item_id"]
        _MEMORY_ID_COUNTERS["item_id"] += 1
        new_item = {
            "item_id": new_id,
            "user_id": user_id,
            "item_name": item_name,
            "category": category,
            "description": description,
            "location": location,
            "date": str(date),
            "report_type": report_type,
            "image_path": image_path,
            "status": status,
            "created_at": "Just now"
        }
        _MEMORY_ITEMS.insert(0, new_item)  # Prepend for recency
        return new_id


def get_all_items(report_type: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all items, optionally filtered by report_type and/or status."""
    if DB_ONLINE:
        try:
            conn = get_raw_connection()
            cursor = get_dict_cursor(conn)
            sql = """
                SELECT i.*, u.name as reporter_name, u.email as reporter_email, u.student_id as reporter_student_id
                FROM Items i
                JOIN Users u ON i.user_id = u.user_id
                WHERE 1=1
            """
            params = []
            if report_type:
                sql += " AND i.report_type = %s"
                params.append(report_type)
            if status:
                sql += " AND i.status = %s"
                params.append(status)
            sql += " ORDER BY i.item_id DESC"
            cursor.execute(sql, tuple(params))
            items = cursor.fetchall()
            conn.close()
            return list(items)
        except Exception as e:
            print(f"[MySQL get_all_items error]: {e}")
            return []
    else:
        results = []
        user_map = {u["user_id"]: u for u in _MEMORY_USERS}
        for item in _MEMORY_ITEMS:
            if report_type and item.get("report_type") != report_type:
                continue
            if status and item.get("status") != status:
                continue
            rec = dict(item)
            u = user_map.get(item["user_id"], {})
            rec["reporter_name"] = u.get("name", "Student")
            rec["reporter_email"] = u.get("email", "")
            rec["reporter_student_id"] = u.get("student_id", "")
            results.append(rec)
        return results


def get_item_by_id(item_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves a single item record including its reporter details."""
    if DB_ONLINE:
        try:
            conn = get_raw_connection()
            cursor = get_dict_cursor(conn)
            sql = """
                SELECT i.*, u.name as reporter_name, u.email as reporter_email, u.student_id as reporter_student_id
                FROM Items i
                JOIN Users u ON i.user_id = u.user_id
                WHERE i.item_id = %s
            """
            cursor.execute(sql, (item_id,))
            item = cursor.fetchone()
            conn.close()
            return item
        except Exception as e:
            print(f"[MySQL get_item_by_id error]: {e}")
            return None
    else:
        user_map = {u["user_id"]: u for u in _MEMORY_USERS}
        for item in _MEMORY_ITEMS:
            if item["item_id"] == item_id:
                rec = dict(item)
                u = user_map.get(item["user_id"], {})
                rec["reporter_name"] = u.get("name", "Student")
                rec["reporter_email"] = u.get("email", "")
                rec["reporter_student_id"] = u.get("student_id", "")
                return rec
        return None


def get_items_by_user_id(user_id: int) -> List[Dict[str, Any]]:
    """Retrieves all items reported by a specific student."""
    if DB_ONLINE:
        try:
            conn = get_raw_connection()
            cursor = get_dict_cursor(conn)
            sql = "SELECT * FROM Items WHERE user_id = %s ORDER BY item_id DESC"
            cursor.execute(sql, (user_id,))
            items = cursor.fetchall()
            conn.close()
            return list(items)
        except Exception as e:
            print(f"[MySQL get_items_by_user_id error]: {e}")
            return []
    else:
        return [dict(it) for it in _MEMORY_ITEMS if it["user_id"] == user_id]


def update_item_status(item_id: int, new_status: str) -> bool:
    """Updates the status of an item ('Pending', 'Claimed', 'Resolved')."""
    if DB_ONLINE:
        try:
            conn = get_raw_connection()
            cursor = conn.cursor()
            sql = "UPDATE Items SET status = %s WHERE item_id = %s"
            cursor.execute(sql, (new_status, item_id))
            conn.close()
            return True
        except Exception as e:
            print(f"[MySQL update_item_status error]: {e}")
            return False
    else:
        for it in _MEMORY_ITEMS:
            if it["item_id"] == item_id:
                it["status"] = new_status
                return True
        return False


def delete_item(item_id: int) -> bool:
    """Deletes an item report (admin or student withdrawal)."""
    if DB_ONLINE:
        try:
            conn = get_raw_connection()
            cursor = conn.cursor()
            sql = "DELETE FROM Items WHERE item_id = %s"
            cursor.execute(sql, (item_id,))
            conn.close()
            return True
        except Exception as e:
            print(f"[MySQL delete_item error]: {e}")
            return False
    else:
        global _MEMORY_ITEMS
        initial_len = len(_MEMORY_ITEMS)
        _MEMORY_ITEMS = [it for it in _MEMORY_ITEMS if it["item_id"] != item_id]
        return len(_MEMORY_ITEMS) < initial_len


# =============================================================================
# MATCHES QUERIES
# =============================================================================

def save_match(lost_item_id: int, found_item_id: int, match_reason: str, match_status: str = "Potential") -> Optional[int]:
    """Records an identified match between a lost item and found item."""
    if DB_ONLINE:
        try:
            conn = get_raw_connection()
            cursor = conn.cursor()
            # Check duplicate match
            cursor.execute("SELECT match_id FROM Matches WHERE lost_item_id = %s AND found_item_id = %s", (lost_item_id, found_item_id))
            existing = cursor.fetchone()
            if existing:
                conn.close()
                return existing[0] if isinstance(existing, tuple) else existing["match_id"]

            sql = "INSERT INTO Matches (lost_item_id, found_item_id, match_reason, match_status) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (lost_item_id, found_item_id, match_reason, match_status))
            mid = cursor.lastrowid
            conn.close()
            return mid
        except Exception as e:
            print(f"[MySQL save_match error]: {e}")
            return None
    else:
        for m in _MEMORY_MATCHES:
            if m["lost_item_id"] == lost_item_id and m["found_item_id"] == found_item_id:
                return m["match_id"]
        mid = _MEMORY_ID_COUNTERS["match_id"]
        _MEMORY_ID_COUNTERS["match_id"] += 1
        _MEMORY_MATCHES.append({
            "match_id": mid,
            "lost_item_id": lost_item_id,
            "found_item_id": found_item_id,
            "match_reason": match_reason,
            "match_status": match_status,
            "created_at": "Just now"
        })
        return mid


def get_all_matches() -> List[Dict[str, Any]]:
    """Retrieves all matches with joined item and user details."""
    if DB_ONLINE:
        try:
            conn = get_raw_connection()
            cursor = get_dict_cursor(conn)
            sql = """
                SELECT m.*,
                       l.item_name as lost_name, l.category as lost_category, l.location as lost_location, l.date as lost_date, l.status as lost_status,
                       f.item_name as found_name, f.category as found_category, f.location as found_location, f.date as found_date, f.status as found_status,
                       u_lost.name as lost_user_name, u_lost.email as lost_user_email,
                       u_found.name as found_user_name, u_found.email as found_user_email
                FROM Matches m
                JOIN Items l ON m.lost_item_id = l.item_id
                JOIN Items f ON m.found_item_id = f.item_id
                JOIN Users u_lost ON l.user_id = u_lost.user_id
                JOIN Users u_found ON f.user_id = u_found.user_id
                ORDER BY m.match_id DESC
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            conn.close()
            return list(rows)
        except Exception as e:
            print(f"[MySQL get_all_matches error]: {e}")
            return []
    else:
        item_map = {it["item_id"]: it for it in _MEMORY_ITEMS}
        user_map = {u["user_id"]: u for u in _MEMORY_USERS}
        results = []
        for m in _MEMORY_MATCHES:
            l = item_map.get(m["lost_item_id"])
            f = item_map.get(m["found_item_id"])
            if not l or not f:
                continue
            rec = dict(m)
            rec["lost_name"] = l.get("item_name")
            rec["lost_category"] = l.get("category")
            rec["lost_location"] = l.get("location")
            rec["lost_date"] = l.get("date")
            rec["lost_status"] = l.get("status")
            rec["found_name"] = f.get("item_name")
            rec["found_category"] = f.get("category")
            rec["found_location"] = f.get("location")
            rec["found_date"] = f.get("date")
            rec["found_status"] = f.get("status")

            u_l = user_map.get(l.get("user_id"), {})
            u_f = user_map.get(f.get("user_id"), {})
            rec["lost_user_name"] = u_l.get("name", "Student")
            rec["lost_user_email"] = u_l.get("email", "")
            rec["found_user_name"] = u_f.get("name", "Student")
            rec["found_user_email"] = u_f.get("email", "")
            results.append(rec)
        return results


def update_match_status(match_id: int, match_status: str) -> bool:
    """Updates match verification status ('Potential', 'Confirmed', 'Rejected')."""
    if DB_ONLINE:
        try:
            conn = get_raw_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE Matches SET match_status = %s WHERE match_id = %s", (match_status, match_id))
            conn.close()
            return True
        except Exception as e:
            print(f"[MySQL update_match_status error]: {e}")
            return False
    else:
        for m in _MEMORY_MATCHES:
            if m["match_id"] == match_id:
                m["match_status"] = match_status
                return True
        return False
