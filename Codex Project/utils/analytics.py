import json
import os
from collections import Counter
from datetime import datetime
from threading import Lock

from config import Config


_analytics_lock = Lock()


def _default_store():
    """Return the default analytics structure."""
    return {
        "users": [],
        "predictions": [],
    }


def _ensure_analytics_file():
    """Create the analytics file the first time the app runs."""
    analytics_dir = os.path.dirname(Config.ANALYTICS_FILE)
    os.makedirs(analytics_dir, exist_ok=True)

    if not os.path.exists(Config.ANALYTICS_FILE):
        with open(Config.ANALYTICS_FILE, "w", encoding="utf-8") as file:
            json.dump(_default_store(), file, indent=2)


def load_analytics_store():
    """Load analytics data from disk."""
    _ensure_analytics_file()
    with _analytics_lock:
        with open(Config.ANALYTICS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

    data.setdefault("users", [])
    data.setdefault("predictions", [])
    return data


def save_analytics_store(data):
    """Persist analytics data to disk."""
    _ensure_analytics_file()
    with _analytics_lock:
        with open(Config.ANALYTICS_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)


def rank_range_label(rank):
    """Group ranks into readable buckets for the admin dashboard."""
    if rank <= 100000:
        return "0 - 1 Lakh"
    if rank <= 300000:
        return "1 - 3 Lakh"
    if rank <= 500000:
        return "3 - 5 Lakh"
    if rank <= 700000:
        return "5 - 7 Lakh"
    if rank <= 1000000:
        return "7 - 10 Lakh"
    return "10 Lakh+"


def track_prediction(user_id, candidate, prediction_results):
    """Record one search event for lightweight SaaS analytics."""
    analytics_data = load_analytics_store()

    if user_id not in analytics_data["users"]:
        analytics_data["users"].append(user_id)

    top_colleges = []
    seen_colleges = set()
    for item in prediction_results[:10]:
        college_name = item["college_name"]
        if college_name not in seen_colleges:
            top_colleges.append(college_name)
            seen_colleges.add(college_name)

    analytics_data["predictions"].append(
        {
            "user_id": user_id,
            "rank": int(candidate["rank"]),
            "category": candidate["category"],
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "results_count": len(prediction_results),
            "rank_range": rank_range_label(int(candidate["rank"])),
            "top_colleges": top_colleges,
        }
    )

    save_analytics_store(analytics_data)


def get_total_users():
    """Return the number of unique tracked sessions."""
    analytics_data = load_analytics_store()
    return len(set(analytics_data["users"]))


def get_total_predictions():
    """Return the total number of searches recorded."""
    analytics_data = load_analytics_store()
    return len(analytics_data["predictions"])


def get_top_colleges(limit=5):
    """Return the most frequently surfaced colleges in predictions."""
    analytics_data = load_analytics_store()
    college_counter = Counter()

    for prediction in analytics_data["predictions"]:
        for college_name in prediction.get("top_colleges", []):
            college_counter[college_name] += 1

    return college_counter.most_common(limit)


def get_rank_distribution():
    """Return the most searched rank buckets."""
    analytics_data = load_analytics_store()
    range_counter = Counter()

    for prediction in analytics_data["predictions"]:
        range_counter[prediction.get("rank_range", "Unknown")] += 1

    return range_counter.most_common()


def get_category_distribution():
    """Return category popularity for the dashboard."""
    analytics_data = load_analytics_store()
    category_counter = Counter()

    for prediction in analytics_data["predictions"]:
        category_counter[prediction.get("category", "Unknown")] += 1

    return category_counter.most_common()


def get_recent_predictions(limit=8):
    """Return the most recent prediction events for admin visibility."""
    analytics_data = load_analytics_store()
    return list(reversed(analytics_data["predictions"]))[:limit]
