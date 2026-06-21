import os
import json
from datetime import date, timedelta
from search_console import get_service, get_top_pages, get_top_queries

MONTHLY_REPORT_FILE = os.path.join(os.path.dirname(__file__), "monthly_report_cache.json")

NEIGHBORHOODS = [
    "Rosemary Square",
    "Clematis",
    "Flagler Drive",
    "CityPlace",
    "Downtown West Palm Beach",
    "Palm Beach Island",
    "Northwood",
    "South Flagler",
    "North Flagler",
    "Nora District",
]


def should_generate_monthly():
    return date.today().day == 1


def load_monthly_cache():
    if os.path.exists(MONTHLY_REPORT_FILE):
        with open(MONTHLY_REPORT_FILE, "r") as f:
            return json.load(f)
    return {}


def save_monthly_cache(data):
    with open(MONTHLY_REPORT_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_monthly_search_stats(service):
    end_date = date.today() - timedelta(days=2)
    start_date = end_date - timedelta(days=30)
    pages = get_top_pages(service, days=30)
    queries = get_top_queries(service, days=30)
    total_clicks = sum(r["clicks"] for r in pages)
    total_impressions = sum(r["impressions"] for r in pages)
    avg_position = (
        sum(r["position"] for r in pages) / len(pages) if pages else 0
    )
    top_pages = [(r["keys"][0], r["clicks"], r["impressions"]) for r in pages[:5]]
    top_queries = [(r["keys"][0], r["clicks"], r["impressions"]) for r in queries[:5]]
    return {
        "period": f"{start_date.isoformat()} to {end_date.isoformat()}",
        "total_clicks": total_clicks,
        "total_impressions": total_impressions,
        "avg_position": round(avg_position, 1),
        "top_pages": top_pages,
        "top_queries": top_queries,
    }


def get_neighborhood_page_stats(pages):
    neighborhood_stats = {}
    for neighborhood in NEIGHBORHOODS:
        slug = neighborhood.lower().replace(" ", "-")
        matching = [
            r for r in pages
            if slug in r["keys"][0].lower() or neighborhood.lower() in r["keys"][0].lower()
        ]
        if matching:
            total_clicks = sum(r["clicks"] for r in matching)
            total_impressions = sum(r["impressions"] for r in matching)
            neighborhood_stats[neighborhood] = {
                "clicks": total_clicks,
                "impressions": total_impressions,
                "pages": len(matching),
            }
    return neighborhood_stats


def format_monthly_report_section(stats, neighborhood_stats):
    lines = []
    lines.append("=" * 55)
    lines.append(f"MONTHLY MARKET REPORT — {date.today().strftime('%B %Y')}")
    lines.append("=" * 55)
    lines.append(f"  Period: {stats['period']}")
    lines.append(f"\n  SITE PERFORMANCE THIS MONTH:")
    lines.append(f"    Total clicks:       {stats['total_clicks']:,}")
    lines.append(f"    Total impressions:  {stats['total_impressions']:,}")
    lines.append(f"    Avg position:       {stats['avg_position']}")
    lines.append(f"\n  TOP 5 PAGES:")
    for url, clicks, impr in stats["top_pages"]:
        short = url.replace("https://condowpb.com", "").replace("https://www.condowpb.com", "") or "/"
        lines.append(f"    {clicks:4.0f} clicks  {impr:6.0f} impr  {short}")
    lines.append(f"\n  TOP 5 QUERIES:")
    for query, clicks, impr in stats["top_queries"]:
        lines.append(f"    {clicks:4.0f} clicks  {impr:6.0f} impr  '{query}'")
    if neighborhood_stats:
        lines.append(f"\n  NEIGHBORHOOD PAGE PERFORMANCE:")
        for neighborhood, data in neighborhood_stats.items():
            lines.append(f"    {neighborhood}")
            lines.append(f"      {data['clicks']:.0f} clicks · {data['impressions']:.0f} impressions · {data['pages']} pages")
    lines.append(f"\n  → Use this data in your monthly email blast.")
    lines.append(f"  → Post neighborhood stats to Google Business Profile.")
    lines.append(f"  → Share top pages on social as proof of market expertise.")
    return "\n".join(lines)


def get_monthly_report():
    if not should_generate_monthly():
        return None
    service = get_service()
    pages = get_top_pages(service, days=30)
    stats = get_monthly_search_stats(service)
    neighborhood_stats = get_neighborhood_page_stats(pages)
    cache = {
        "generated": date.today().isoformat(),
        "stats": stats,
        "neighborhood_stats": neighborhood_stats,
    }
    save_monthly_cache(cache)
    return format_monthly_report_section(stats, neighborhood_stats)
