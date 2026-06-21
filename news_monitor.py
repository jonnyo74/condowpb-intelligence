import requests
from xml.etree import ElementTree
from datetime import datetime, timezone

FEEDS = [
    "https://news.google.com/rss/search?q=West+Palm+Beach+condo&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Palm+Beach+County+real+estate&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=West+Palm+Beach+new+construction&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=South+Flagler+House+West+Palm+Beach&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Olara+West+Palm+Beach&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=West+Palm+Beach+luxury+tower&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=site:bisnow.com+West+Palm+Beach&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=site:bizjournals.com+West+Palm+Beach+real+estate&hl=en-US&gl=US&ceid=US:en",
]


def get_recent_news(days=1):
    articles = []
    cutoff = datetime.now(timezone.utc).timestamp() - (days * 86400)

    for feed_url in FEEDS:
        try:
            resp = requests.get(feed_url, timeout=10)
            root = ElementTree.fromstring(resp.content)
            for item in root.findall(".//item"):
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                pub_date = item.findtext("pubDate", "")
                source = item.findtext("source", "")

                try:
                    from email.utils import parsedate_to_datetime
                    dt = parsedate_to_datetime(pub_date)
                    if dt.timestamp() < cutoff:
                        continue
                except Exception:
                    pass

                if any(kw in title.lower() for kw in ["condo", "luxury", "development", "tower", "flagler", "high-rise", "groundbreaking", "approved", "permit", "rezoning", "mixed-use", "residences"]):
                    articles.append({"title": title, "link": link, "source": source, "date": pub_date})
        except Exception:
            pass

    BLOCKED_DOMAINS = [
        "palmbeachpost.com",
        "pbpost.com",
        "gatehousemedianewsservice.com",

        "sun-sentinel.com",
        "miamiherald.com",
        "wsj.com",
        "bloomberg.com",
        "ft.com",
        "realtor.com",
        "zillow.com",
        "redfin.com",
        "trulia.com",
        "apartments.com",
        "rent.com",
        "hotpads.com",
        "homes.com",
    ]

    # deduplicate and filter paywalls
    seen = set()
    unique = []
    for a in articles:
        if a["title"] in seen:
            continue
        if any(domain in a["link"] for domain in BLOCKED_DOMAINS):
            continue
        if any(domain in a.get("source", "") for domain in BLOCKED_DOMAINS):
            continue
        if "Palm Beach Post" in a.get("source", ""):
            continue
        seen.add(a["title"])
        unique.append(a)

    return unique[:10]
