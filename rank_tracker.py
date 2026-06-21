import json
import os
from datetime import date, timedelta
from search_console import get_service

RANK_HISTORY_FILE = os.path.join(os.path.dirname(__file__), "rank_history.json")

MONEY_KEYWORDS = [
    "west palm beach condos for sale",
    "west palm beach luxury condos",
    "wpb condos",
    "condos west palm beach",
    "550 okeechobee condos",
    "esperante west palm beach",
    "the bristol west palm beach",
    "cityplace tower condos",
    "flagler house west palm beach",
    "one watermark place west palm beach",
    "west palm beach waterfront condos",
    "palm beach county luxury condos",
    "downtown west palm beach condos",
    "west palm beach high rise condos",
    "esplanade grande west palm beach",
    "la clara west palm beach",
    "south flagler house west palm beach",
    "olara west palm beach",
    "forte on flagler",
    "waterview towers west palm beach",
]

DROP_ALERT_THRESHOLD = 3


def load_history():
    if os.path.exists(RANK_HISTORY_FILE):
        with open(RANK_HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}


def save_history(history):
    with open(RANK_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def get_current_positions(service):
    end_date = date.today() - timedelta(days=2)
    start_date = end_date - timedelta(days=7)
    response = service.searchanalytics().query(
        siteUrl="sc-domain:condowpb.com",
        body={
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "dimensions": ["query"],
            "rowLimit": 500,
        },
    ).execute()
    rows = response.get("rows", [])
    positions = {}
    for row in rows:
        query = row["keys"][0]
        if query in MONEY_KEYWORDS:
            positions[query] = round(row["position"], 1)
    return positions


def compare_positions(current, history):
    drops = []
    gains = []
    new_entries = []
    last_date = None
    last_positions = {}
    if history:
        last_date = sorted(history.keys())[-1]
        last_positions = history[last_date]
    for keyword in MONEY_KEYWORDS:
        curr_pos = current.get(keyword)
        prev_pos = last_positions.get(keyword)
        if curr_pos is None:
            continue
        if prev_pos is None:
            new_entries.append((keyword, curr_pos))
        else:
            diff = curr_pos - prev_pos
            if diff >= DROP_ALERT_THRESHOLD:
                drops.append((keyword, prev_pos, curr_pos, diff))
            elif diff <= -DROP_ALERT_THRESHOLD:
                gains.append((keyword, prev_pos, curr_pos, abs(diff)))
    return drops, gains, new_entries, last_date


def format_rank_tracker_section(current, drops, gains, new_entries, last_date):
    lines = []
    lines.append("=" * 55)
    lines.append("RANK TRACKER — Money Keywords")
    lines.append("=" * 55)
    if drops:
        lines.append(f"\n  WARNING - POSITION DROPS (threshold: {DROP_ALERT_THRESHOLD} spots):")
        for kw, prev, curr, diff in drops:
            lines.append(f"    '{kw}'")
            lines.append(f"     Position {prev} → {curr}  (down {diff:.1f} spots) — ACT ON THIS")
    else:
        lines.append("\n  No significant position drops detected.")
    if gains:
        lines.append(f"\n  POSITION GAINS:")
        for kw, prev, curr, diff in gains:
            lines.append(f"    '{kw}'")
            lines.append(f"     Position {prev} → {curr}  (up {diff:.1f} spots)")
    lines.append(f"\n  CURRENT POSITIONS:")
    for kw in MONEY_KEYWORDS:
        pos = current.get(kw)
        if pos:
            indicator = "PAGE 1" if pos <= 10 else f"pos {pos}"
            lines.append(f"    {indicator:8}  '{kw}'")
        else:
            lines.append(f"    {'not ranking':8}  '{kw}'")
    if last_date:
        lines.append(f"\n  Compared to: {last_date}")
    return "\n".join(lines)


def get_rank_tracker():
    service = get_service()
    history = load_history()
    current = get_current_positions(service)
    drops, gains, new_entries, last_date = compare_positions(current, history)
    today_str = date.today().isoformat()
    history[today_str] = current
    save_history(history)
    return format_rank_tracker_section(current, drops, gains, new_entries, last_date)
