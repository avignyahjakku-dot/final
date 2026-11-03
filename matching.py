"""
=============================================================================
Smart Lost & Found System - Matching Module (matching.py)
=============================================================================
Course Project: Data Structures & Algorithms (BTech CSE 2nd Year)
Team Size: 2 Members

Rule-based matching engine comparing Lost Items against Found Items using:
1. Category Match
2. Item Name & Description Keyword Overlap
3. Location Proximity
4. Date Plausibility

No AI/ML libraries used - pure algorithmic string analysis, set comparisons,
and conditional weighting logic.
=============================================================================
"""

from datetime import datetime
from typing import Dict, Any, List, Tuple, Set


STOP_WORDS = {
    "a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "of",
    "with", "by", "from", "my", "is", "was", "near", "found", "lost", "left",
    "some", "this", "that", "it", "i", "me", "color", "has", "have"
}


def tokenize(text: str) -> Set[str]:
    """
    Sanitize and split a text string into normalized lowercase keyword tokens,
    removing punctuation and common stop words.
    """
    if not text:
        return set()
    cleaned = "".join(ch.lower() if ch.isalnum() else " " for ch in str(text))
    tokens = set(cleaned.split())
    return tokens - STOP_WORDS


def parse_date(date_val: Any) -> datetime.date:
    """Helper to safely parse string or date objects into a standard date."""
    if hasattr(date_val, "strftime"):
        return date_val
    if isinstance(date_val, str):
        try:
            return datetime.strptime(date_val[:10], "%Y-%m-%d").date()
        except Exception:
            pass
    return datetime.now().date()


def compare_items(lost_item: Dict[str, Any], found_item: Dict[str, Any]) -> Tuple[bool, int, str]:
    """
    Compares a Lost item against a Found item and computes a compatibility score.

    Scoring Distribution (Max 100 points):
    - Category Match:           30 points
    - Name & Keyword Match:     35 points
    - Location Match:           20 points
    - Date Proximity:           15 points

    Returns:
    (is_match: bool, score: int, match_reason: str)
    """
    score = 0
    reasons = []

    # ---------------------------------------------------------
    # 1. Category Comparison (30 points)
    # ---------------------------------------------------------
    lost_cat = str(lost_item.get("category", "")).strip().lower()
    found_cat = str(found_item.get("category", "")).strip().lower()

    if lost_cat and lost_cat == found_cat:
        score += 30
        reasons.append(f"Matching category '{lost_item.get('category')}'")
    else:
        # If categories are distinctly different, mismatch unless one is 'Others'
        if lost_cat != "others" and found_cat != "others":
            return False, 0, "Mismatched categories"
        score += 10
        reasons.append("Category partially compatible")

    # ---------------------------------------------------------
    # 2. Name & Description Keyword Overlap (35 points)
    # ---------------------------------------------------------
    lost_name_tokens = tokenize(lost_item.get("item_name", ""))
    found_name_tokens = tokenize(found_item.get("item_name", ""))

    lost_desc_tokens = tokenize(lost_item.get("description", ""))
    found_desc_tokens = tokenize(found_item.get("description", ""))

    # Direct name token intersection
    name_common = lost_name_tokens.intersection(found_name_tokens)
    # Cross description intersection
    all_lost = lost_name_tokens.union(lost_desc_tokens)
    all_found = found_name_tokens.union(found_desc_tokens)
    all_common = all_lost.intersection(all_found)

    if name_common:
        # Found exact words in both item names (e.g. "dell", "laptop", "casio")
        score += min(25, 12 * len(name_common))
        reasons.append(f"Name keywords matched ({', '.join(sorted(name_common))})")
    elif all_common:
        score += min(18, 8 * len(all_common))
        reasons.append(f"Description keywords matched ({', '.join(sorted(all_common))})")
    else:
        # Check substring containment (e.g., 'xps' in 'dell xps 13')
        l_name = str(lost_item.get("item_name", "")).lower()
        f_name = str(found_item.get("item_name", "")).lower()
        if l_name in f_name or f_name in l_name:
            score += 20
            reasons.append("Item titles share common phrasing")

    # ---------------------------------------------------------
    # 3. Location Proximity (20 points)
    # ---------------------------------------------------------
    lost_loc = str(lost_item.get("location", "")).strip().lower()
    found_loc = str(found_item.get("location", "")).strip().lower()

    if lost_loc and (lost_loc == found_loc):
        score += 20
        reasons.append(f"Identical campus location: '{lost_item.get('location')}'")
    else:
        # Check token overlap in location (e.g., "Library", "Cafeteria", "Lab")
        lost_loc_tokens = tokenize(lost_loc)
        found_loc_tokens = tokenize(found_loc)
        common_loc = lost_loc_tokens.intersection(found_loc_tokens)
        if common_loc:
            score += 15
            reasons.append(f"Same zone on campus ({', '.join(sorted(common_loc))})")

    # ---------------------------------------------------------
    # 4. Date Proximity (15 points)
    # ---------------------------------------------------------
    try:
        lost_date = parse_date(lost_item.get("date"))
        found_date = parse_date(found_item.get("date"))
        delta_days = (found_date - lost_date).days

        # Found date should logically be on or after the loss date,
        # or within +/- 2 days if reporting dates were slightly off.
        if -2 <= delta_days <= 14:
            if abs(delta_days) <= 1:
                score += 15
                reasons.append(f"Dates aligned ({lost_date} vs {found_date})")
            elif delta_days <= 5:
                score += 10
                reasons.append(f"Dates within {delta_days} days")
            else:
                score += 5
                reasons.append("Reported within two weeks")
        elif delta_days < -7:
            # Item found weeks BEFORE it was lost? Unlikely match
            score = max(0, score - 20)
    except Exception:
        pass

    # Threshold for a viable potential match
    is_match = score >= 45 and (len(name_common) > 0 or score >= 60)
    match_reason = " | ".join(reasons) if reasons else "General criteria similarity"

    return is_match, score, match_reason


def find_matches_for_item(target_item: Dict[str, Any], candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Finds all potential candidate matches for a single item (lost or found).
    """
    results = []
    target_type = str(target_item.get("report_type", "")).capitalize()

    for cand in candidates:
        cand_type = str(cand.get("report_type", "")).capitalize()
        # Must compare Lost against Found only
        if target_type == cand_type:
            continue

        lost = target_item if target_type == "Lost" else cand
        found = cand if target_type == "Lost" else target_item

        is_match, score, reason = compare_items(lost, found)
        if is_match:
            results.append({
                "lost_item": lost,
                "found_item": found,
                "lost_item_id": lost.get("item_id"),
                "found_item_id": found.get("item_id"),
                "score": score,
                "match_reason": reason,
                "match_status": "Potential"
            })

    # Sort matches by highest score first (using our custom selection sort logic or score)
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def run_all_matches(lost_items: List[Dict[str, Any]], found_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Runs global matching between all active Lost items and all active Found items.
    """
    matches = []
    for lost in lost_items:
        if lost.get("status") in ["Resolved", "Claimed"]:
            continue
        for found in found_items:
            if found.get("status") in ["Resolved", "Claimed"]:
                continue
            
            is_match, score, reason = compare_items(lost, found)
            if is_match:
                matches.append({
                    "lost_item_id": lost.get("item_id"),
                    "found_item_id": found.get("item_id"),
                    "lost_item": lost,
                    "found_item": found,
                    "score": score,
                    "match_reason": reason,
                    "match_status": "Potential"
                })

    # Sort descending by score
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches
