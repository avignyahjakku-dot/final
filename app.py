"""
=============================================================================
Smart Lost & Found System - Main Application (app.py)
=============================================================================
Course Project: Data Structures & Algorithms (BTech CSE 2nd Year)
Team Size: 2 Members
- Member 1: Frontend and Database
- Member 2: Backend and DSA

A full-stack campus web application built with Python Flask, MySQL, and
custom Data Structures and Algorithms (Arrays, Linked Lists, BST, Searching,
and Sorting).
=============================================================================
"""

import os
import time
from functools import wraps
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify, send_from_directory
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

import database as db
import dsa
import matching

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "smart_lost_found_super_secret_key_2026")

# Configure Uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB max upload

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize in-memory DSA instances for campus runtime
recent_items_list = dsa.SinglyLinkedList()
campus_bst = dsa.BinarySearchTree()


def allowed_file(filename: str) -> bool:
    """Validate permitted image extensions."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    """Decorator to protect routes requiring student authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to protect admin-only routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in with admin privileges.", "warning")
            return redirect(url_for("login", next=request.path))
        if session.get("role") != "admin":
            flash("Access denied. Administrator credentials required.", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated_function


def sync_dsa_structures():
    """
    Synchronizes the in-memory Singly Linked List and Binary Search Tree
    with current records from the database.
    """
    global recent_items_list, campus_bst
    items = db.get_all_items()

    # Rebuild Singly Linked List (Recent reports at head)
    recent_items_list = dsa.SinglyLinkedList()
    for item in reversed(items):
        recent_items_list.insert_head(item)

    # Rebuild Binary Search Tree indexed by item_id
    campus_bst = dsa.BinarySearchTree()
    for item in items:
        campus_bst.insert(item, key=int(item["item_id"]))


# Initialize database upon startup
with app.app_context():
    db.init_db()
    sync_dsa_structures()


@app.context_processor
def inject_global_data():
    """Injects user authentication status and utility data into all Jinja templates."""
    return {
        "current_user": {
            "is_authenticated": "user_id" in session,
            "user_id": session.get("user_id"),
            "name": session.get("name"),
            "email": session.get("email"),
            "role": session.get("role"),
            "student_id": session.get("student_id")
        },
        "now_year": datetime.now().year,
        "is_db_online": db.DB_ONLINE
    }


# =============================================================================
# FILE UPLOAD ROUTE
# =============================================================================

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    """Serve uploaded item photos."""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# =============================================================================
# AUTHENTICATION ROUTES
# =============================================================================

@app.route("/register", methods=["GET", "POST"])
def register():
    """Student registration page."""
    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        student_id = request.form.get("student_id", "").strip().upper()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Validation
        if not name or not email or not student_id or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("register.html")

        existing_user = db.get_user_by_email(email)
        if existing_user:
            flash("An account with this email address already exists.", "danger")
            return render_template("register.html")

        # Hash password and create record
        hashed_pw = generate_password_hash(password)
        user_id = db.create_user(name, email, student_id, hashed_pw, role="student")

        if user_id:
            flash("Registration successful! You may now log in.", "success")
            return redirect(url_for("login"))
        else:
            flash("Failed to register. Please try again.", "danger")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Student and Administrator login page."""
    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = db.get_user_by_email(email)
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["user_id"]
            session["name"] = user["name"]
            session["email"] = user["email"]
            session["student_id"] = user["student_id"]
            session["role"] = user["role"]

            flash(f"Welcome back, {user['name']}!", "success")
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/"):
                return redirect(next_page)
            return redirect(url_for("admin" if user["role"] == "admin" else "index"))
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Logs out user and clears session."""
    session.clear()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for("index"))


# =============================================================================
# MAIN PAGES
# =============================================================================

@app.route("/")
def index():
    """
    Home Page:
    - Demonstrates Singly Linked List by retrieving top recent items via get_recent(6).
    - Displays overall campus recovery statistics.
    """
    all_items = db.get_all_items()
    sync_dsa_structures()

    # Retrieve recent items from the Singly Linked List
    recent_items = recent_items_list.get_recent(6)

    # Compute quick stats
    total_items = len(all_items)
    lost_count = sum(1 for it in all_items if it.get("report_type") == "Lost")
    found_count = sum(1 for it in all_items if it.get("report_type") == "Found")
    reunited_count = sum(1 for it in all_items if it.get("status") in ["Claimed", "Resolved"])

    return render_template(
        "index.html",
        recent_items=recent_items,
        total_items=total_items,
        lost_count=lost_count,
        found_count=found_count,
        reunited_count=reunited_count
    )


@app.route("/report-lost", methods=["GET", "POST"])
@login_required
def report_lost():
    """Page to submit a lost item report."""
    if request.method == "POST":
        item_name = request.form.get("item_name", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        location = request.form.get("location", "").strip()
        date = request.form.get("date", "").strip()

        if not item_name or not category or not description or not location or not date:
            flash("Please fill in all required fields.", "danger")
            return render_template("report_lost.html")

        # Handle image upload
        image_path = None
        if "image" in request.files:
            file = request.files["image"]
            if file and file.filename != "" and allowed_file(file.filename):
                safe_name = secure_filename(f"lost_{int(time.time())}_{file.filename}")
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], safe_name))
                image_path = safe_name

        item_id = db.create_item(
            user_id=session["user_id"],
            item_name=item_name,
            category=category,
            description=description,
            location=location,
            date=date,
            report_type="Lost",
            image_path=image_path
        )

        if item_id:
            # Sync DSA structures
            sync_dsa_structures()

            # Automatic rule-based matching check against existing Found items
            new_item = db.get_item_by_id(item_id)
            found_items = db.get_all_items(report_type="Found", status="Pending")
            potential_matches = matching.find_matches_for_item(new_item, found_items)

            for match in potential_matches:
                db.save_match(
                    lost_item_id=item_id,
                    found_item_id=match["found_item_id"],
                    match_reason=match["match_reason"]
                )

            if potential_matches:
                flash(f"Report submitted! System detected {len(potential_matches)} possible match(es)! Check the Matches page.", "success")
                return redirect(url_for("matches"))
            else:
                flash("Your Lost Item report has been successfully submitted.", "success")
                return redirect(url_for("my_reports"))
        else:
            flash("Failed to submit report. Please try again.", "danger")

    return render_template("report_lost.html")


@app.route("/report-found", methods=["GET", "POST"])
@login_required
def report_found():
    """Page to submit a found item report."""
    if request.method == "POST":
        item_name = request.form.get("item_name", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        location = request.form.get("location", "").strip()
        date = request.form.get("date", "").strip()

        if not item_name or not category or not description or not location or not date:
            flash("Please fill in all required fields.", "danger")
            return render_template("report_found.html")

        # Handle image upload
        image_path = None
        if "image" in request.files:
            file = request.files["image"]
            if file and file.filename != "" and allowed_file(file.filename):
                safe_name = secure_filename(f"found_{int(time.time())}_{file.filename}")
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], safe_name))
                image_path = safe_name

        item_id = db.create_item(
            user_id=session["user_id"],
            item_name=item_name,
            category=category,
            description=description,
            location=location,
            date=date,
            report_type="Found",
            image_path=image_path
        )

        if item_id:
            # Sync DSA structures
            sync_dsa_structures()

            # Automatic rule-based matching check against existing Lost items
            new_item = db.get_item_by_id(item_id)
            lost_items = db.get_all_items(report_type="Lost", status="Pending")
            potential_matches = matching.find_matches_for_item(new_item, lost_items)

            for match in potential_matches:
                db.save_match(
                    lost_item_id=match["lost_item_id"],
                    found_item_id=item_id,
                    match_reason=match["match_reason"]
                )

            if potential_matches:
                flash(f"Found item recorded! System detected {len(potential_matches)} possible owner(s)! Check the Matches tab.", "success")
                return redirect(url_for("matches"))
            else:
                flash("Your Found Item report has been recorded. Thank you for your honesty!", "success")
                return redirect(url_for("my_reports"))
        else:
            flash("Failed to submit report. Please try again.", "danger")

    return render_template("report_found.html")


@app.route("/search")
def search():
    """
    Search Items Page:
    Directly incorporates:
    - Linear Search (Keyword search across title, description, category, location)
    - Binary Search (Lookup by Item ID on sorted items array)
    - Sorting Algorithms (Bubble Sort, Insertion Sort, Selection Sort)
    Displays DSA performance metrics (comparisons, swaps, execution time).
    """
    query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    location = request.args.get("location", "").strip()
    report_type = request.args.get("type", "").strip()
    search_algo = request.args.get("search_algo", "linear").strip().lower()
    sort_algo = request.args.get("sort_algo", "bubble").strip().lower()
    sort_key = request.args.get("sort_key", "date").strip()
    sort_order = request.args.get("sort_order", "desc").strip()
    reverse = (sort_order == "desc")

    # Fetch all items matching type filter
    all_records = db.get_all_items(report_type=report_type if report_type else None)

    # Apply category & location filters if provided
    filtered_records = []
    for it in all_records:
        if category and it.get("category") != category:
            continue
        if location and location.lower() not in str(it.get("location", "")).lower():
            continue
        filtered_records.append(it)

    search_metrics = {
        "search_algo": search_algo.title(),
        "search_comparisons": 0,
        "search_time_ms": 0.0,
        "step_history": []
    }

    # Execute Searching
    if query:
        if search_algo == "binary":
            # Binary Search requires integer ID
            try:
                target_id = int(query)
                found, comps, steps, elapsed = dsa.binary_search_by_id(filtered_records, target_id)
                results = [found] if found else []
                search_metrics["search_comparisons"] = comps
                search_metrics["search_time_ms"] = round(elapsed, 4)
                search_metrics["step_history"] = steps
            except ValueError:
                # If query is text, fall back to linear search with notification
                flash("Binary search operates on numerical Item IDs. Showing Linear Search results instead.", "info")
                results, comps, elapsed = dsa.linear_search_items(filtered_records, query)
                search_metrics["search_algo"] = "Linear (Auto-Fallback)"
                search_metrics["search_comparisons"] = comps
                search_metrics["search_time_ms"] = round(elapsed, 4)
        else:
            # Linear Search
            results, comps, elapsed = dsa.linear_search_items(filtered_records, query)
            search_metrics["search_comparisons"] = comps
            search_metrics["search_time_ms"] = round(elapsed, 4)
    else:
        results = filtered_records

    # Execute Sorting using user-selected manual DSA algorithm
    sort_metrics = {
        "sort_algo": sort_algo.title(),
        "sort_key": sort_key,
        "sort_comparisons": 0,
        "sort_swaps": 0,
        "sort_time_ms": 0.0
    }

    if results:
        if sort_algo == "insertion":
            sorted_results, comps, swaps, elapsed = dsa.insertion_sort(results, key=sort_key, reverse=reverse)
        elif sort_algo == "selection":
            sorted_results, comps, swaps, elapsed = dsa.selection_sort(results, key=sort_key, reverse=reverse)
        else:
            # Default: Bubble Sort
            sorted_results, comps, swaps, elapsed = dsa.bubble_sort(results, key=sort_key, reverse=reverse)

        sort_metrics["sort_comparisons"] = comps
        sort_metrics["sort_swaps"] = swaps
        sort_metrics["sort_time_ms"] = round(elapsed, 4)
        results = sorted_results

    return render_template(
        "search.html",
        items=results,
        query=query,
        category=category,
        location=location,
        report_type=report_type,
        search_algo=search_algo,
        sort_algo=sort_algo,
        sort_key=sort_key,
        sort_order=sort_order,
        search_metrics=search_metrics,
        sort_metrics=sort_metrics,
        total_found=len(results)
    )


@app.route("/matches")
def matches():
    """
    Matching Results Page:
    Displays identified correspondences between Lost and Found reports with reasons.
    """
    # Recalculate matches dynamically if needed to ensure any new items are captured
    lost_items = db.get_all_items(report_type="Lost")
    found_items = db.get_all_items(report_type="Found")

    live_matches = matching.run_all_matches(lost_items, found_items)
    # Sync with DB table
    for m in live_matches:
        db.save_match(m["lost_item_id"], m["found_item_id"], m["match_reason"])

    all_matches = db.get_all_matches()

    return render_template("matches.html", matches=all_matches)


@app.route("/my-reports")
@login_required
def my_reports():
    """My Reports Page: Displays items submitted by logged-in student."""
    user_items = db.get_items_by_user_id(session["user_id"])
    return render_template("my_reports.html", items=user_items)


@app.route("/item/<int:item_id>")
def item_details(item_id: int):
    """
    Item Details Page:
    - Demonstrates BST lookup: attempts O(log n) retrieval via campus_bst.search()
    - Displays full item metadata, location, image, and contact details of the reporter.
    """
    # Demonstrate BST Search
    bst_item, bst_comps, bst_path = campus_bst.search(item_id)
    
    # Fallback to database if not in BST yet
    item = bst_item if bst_item else db.get_item_by_id(item_id)

    if not item:
        flash(f"Item #{item_id} was not found in the system.", "danger")
        return redirect(url_for("index"))

    # If it's a lost item, find potential matching found items
    candidate_matches = []
    if item.get("report_type") == "Lost":
        found_pool = db.get_all_items(report_type="Found")
        candidate_matches = matching.find_matches_for_item(item, found_pool)
    elif item.get("report_type") == "Found":
        lost_pool = db.get_all_items(report_type="Lost")
        candidate_matches = matching.find_matches_for_item(item, lost_pool)

    return render_template(
        "item_details.html",
        item=item,
        bst_comps=bst_comps,
        bst_path=bst_path,
        candidate_matches=candidate_matches
    )


@app.route("/item/<int:item_id>/claim", methods=["POST"])
@login_required
def claim_item(item_id: int):
    """Allows student reporter or finder to mark an item as Claimed/Resolved."""
    item = db.get_item_by_id(item_id)
    if not item:
        flash("Item not found.", "danger")
        return redirect(url_for("index"))

    # Only owner or admin can update status
    if item["user_id"] != session["user_id"] and session.get("role") != "admin":
        flash("Unauthorized action.", "danger")
        return redirect(url_for("item_details", item_id=item_id))

    action_status = request.form.get("status", "Claimed")
    if action_status not in ["Pending", "Claimed", "Resolved"]:
        action_status = "Claimed"

    db.update_item_status(item_id, action_status)
    sync_dsa_structures()
    flash(f"Item #{item_id} status updated to '{action_status}'.", "success")
    return redirect(url_for("item_details", item_id=item_id))


# =============================================================================
# ADMIN DASHBOARD
# =============================================================================

@app.route("/admin")
@admin_required
def admin():
    """
    Admin Dashboard:
    - View all reports (Lost & Found).
    - Update item status (Pending, Claimed, Resolved).
    - Remove inappropriate or duplicate reports.
    """
    items = db.get_all_items()
    matches_list = db.get_all_matches()

    stats = {
        "total_reports": len(items),
        "total_lost": sum(1 for it in items if it.get("report_type") == "Lost"),
        "total_found": sum(1 for it in items if it.get("report_type") == "Found"),
        "total_resolved": sum(1 for it in items if it.get("status") in ["Claimed", "Resolved"]),
        "total_matches": len(matches_list)
    }

    return render_template("admin.html", items=items, matches=matches_list, stats=stats)


@app.route("/admin/item/<int:item_id>/status", methods=["POST"])
@admin_required
def admin_update_status(item_id: int):
    """Admin updates item status."""
    new_status = request.form.get("status", "Pending")
    if new_status in ["Pending", "Claimed", "Resolved"]:
        db.update_item_status(item_id, new_status)
        sync_dsa_structures()
        flash(f"Status of item #{item_id} successfully updated to '{new_status}'.", "success")
    return redirect(url_for("admin"))


@app.route("/admin/item/<int:item_id>/delete", methods=["POST"])
@admin_required
def admin_delete_item(item_id: int):
    """Admin removes inappropriate or duplicate report."""
    db.delete_item(item_id)
    # Also delete from Linked List and BST
    recent_items_list.delete_by_id(item_id)
    campus_bst.delete(item_id)
    sync_dsa_structures()
    flash(f"Report #{item_id} has been permanently removed.", "warning")
    return redirect(url_for("admin"))


# =============================================================================
# DSA VISUALIZER & BENCHMARK SUITE
# =============================================================================

@app.route("/dsa-visualizer")
def dsa_visualizer():
    """
    Dedicated Interactive DSA Visualizer Page:
    Covers Array, Linear Search, Binary Search, Bubble/Insertion/Selection Sort,
    Singly Linked List, and Binary Search Tree (BST).
    """
    items = db.get_all_items()
    return render_template("dsa_visualizer.html", items=items)


@app.route("/api/dsa/sort", methods=["POST"])
def api_dsa_sort():
    """API for visual sorting operations."""
    data = request.get_json() or {}
    array = data.get("array", [64, 34, 25, 12, 22, 11, 90])
    algo = data.get("algorithm", "bubble").lower()

    # Wrap integers in dictionary structure for dsa functions
    dict_array = [{"val": x} for x in array]

    if algo == "insertion":
        sorted_arr, comps, swaps, elapsed = dsa.insertion_sort(dict_array, key="val")
    elif algo == "selection":
        sorted_arr, comps, swaps, elapsed = dsa.selection_sort(dict_array, key="val")
    else:
        sorted_arr, comps, swaps, elapsed = dsa.bubble_sort(dict_array, key="val")

    return jsonify({
        "original": array,
        "sorted": [x["val"] for x in sorted_arr],
        "algorithm": algo.title(),
        "comparisons": comps,
        "swaps_or_shifts": swaps,
        "time_ms": round(elapsed, 4)
    })


@app.route("/api/dsa/bst-hierarchy", methods=["GET"])
def api_bst_hierarchy():
    """Returns tree structure for visual BST rendering."""
    sync_dsa_structures()
    return jsonify({
        "hierarchy": campus_bst.to_hierarchy_dict(),
        "node_count": campus_bst.node_count,
        "inorder": campus_bst.inorder_traversal(),
        "preorder": campus_bst.preorder_traversal(),
        "postorder": campus_bst.postorder_traversal()
    })


@app.route("/api/dsa/benchmark", methods=["GET"])
def api_dsa_benchmark():
    """Runs live performance comparison of Bubble, Insertion, and Selection sort."""
    import random
    sizes = [10, 25, 50, 100, 200]
    results = {"bubble": [], "insertion": [], "selection": [], "sizes": sizes}

    for size in sizes:
        test_data = [{"val": random.randint(1, 1000)} for _ in range(size)]

        _, b_c, _, b_t = dsa.bubble_sort(test_data, key="val")
        _, i_c, _, i_t = dsa.insertion_sort(test_data, key="val")
        _, s_c, _, s_t = dsa.selection_sort(test_data, key="val")

        results["bubble"].append({"time_ms": round(b_t, 3), "comps": b_c})
        results["insertion"].append({"time_ms": round(i_t, 3), "comps": i_c})
        results["selection"].append({"time_ms": round(s_t, 3), "comps": s_c})

    return jsonify(results)


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def page_not_found(e):
    return render_template("index.html"), 404


@app.errorhandler(500)
def server_error(e):
    flash("An internal server error occurred. Please try again.", "danger")
    return redirect(url_for("index"))


# =============================================================================
# MAIN RUNNER
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("   SMART LOST & FOUND SYSTEM - CAMPUS RECOVERY PORTAL")
    print("   Team: 2 BTech CSE Students | Flask + MySQL + Pure DSA")
    print("=" * 60)
    print("-> App running on http://127.0.0.1:5000")
    print("-> Default Student: aarav.sharma@campus.edu / password123")
    print("-> Default Admin:   admin@campus.edu / password123")
    print("=" * 60 + "\n")
    app.run(debug=True, host="127.0.0.1", port=5000)
