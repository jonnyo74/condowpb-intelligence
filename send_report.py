import os
import smtplib
from datetime import date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from search_console import get_service, get_top_pages, get_top_queries
from site_health import get_sitemap_urls, check_broken_links, check_meta_descriptions
from news_monitor import get_recent_news
from content_ideas import format_content_section
from market_pulse import get_market_pulse
from rank_tracker import get_rank_tracker
from report_builder import get_monthly_report

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RECIPIENTS = [r.strip() for r in os.getenv("REPORT_RECIPIENT", "").split(",")]


def clean_url(url):
    return url.replace("https://condowpb.com", "").replace("https://www.condowpb.com", "") or "/"


def build_report():
    today = date.today().strftime("%B %d, %Y")
    end_date = (date.today() - timedelta(days=2)).isoformat()
    lines = []

    lines.append(f"CondoWPB Intelligence Report — {today}")
    lines.append(f"Data through {end_date}\n")

    # --- SEARCH CONSOLE ---
    print("Pulling Search Console data...")
    service = get_service()
    pages = get_top_pages(service, days=28)
    queries = get_top_queries(service, days=28)
    pages_prev = get_top_pages(service, days=56)

    prev_positions = {r["keys"][0]: r["position"] for r in pages_prev}

    opportunities = [
        r for r in pages
        if r["impressions"] >= 20 and r["clicks"] == 0 and 10 < r["position"] <= 35
    ]

    wins = []
    for r in pages:
        url = r["keys"][0]
        prev = prev_positions.get(url)
        if prev and (prev - r["position"]) >= 3:
            wins.append((url, prev, r["position"]))

    lines.append("=" * 55)
    lines.append("OPPORTUNITIES — Almost on page 1")
    lines.append("=" * 55)
    if opportunities:
        for r in opportunities:
            lines.append(f"  {clean_url(r['keys'][0])}")
            lines.append(f"    {r['impressions']:.0f} impressions · position {r['position']:.1f} · 0 clicks")
            lines.append(f"    → Improve title/meta description to drive clicks")
    else:
        lines.append("  No immediate opportunities detected.")

    lines.append("")
    lines.append("=" * 55)
    lines.append("WINS — Pages that climbed in rankings")
    lines.append("=" * 55)
    if wins:
        for url, prev, curr in wins:
            lines.append(f"  {clean_url(url)}")
            lines.append(f"    Position {prev:.1f} → {curr:.1f} (up {prev-curr:.1f} spots)")
    else:
        lines.append("  No significant ranking improvements this period.")

    lines.append("")
    lines.append("=" * 55)
    lines.append("TOP PAGES BY CLICKS (last 28 days)")
    lines.append("=" * 55)
    for r in pages[:15]:
        lines.append(f"  {r['clicks']:3.0f} clicks  {r['impressions']:5.0f} impr  pos {r['position']:5.1f}  {clean_url(r['keys'][0])}")

    lines.append("")
    lines.append("=" * 55)
    lines.append("TOP QUERIES BY IMPRESSIONS")
    lines.append("=" * 55)
    for r in queries[:15]:
        lines.append(f"  {r['clicks']:3.0f} clicks  {r['impressions']:5.0f} impr  pos {r['position']:5.1f}  {r['keys'][0]}")

    lines.append("")
    lines.append(format_content_section(pages, queries))

    # --- SITE HEALTH ---
    print("Checking site health...")
    try:
        urls = get_sitemap_urls()
        broken = check_broken_links(urls)
        missing_meta = check_meta_descriptions(urls)
        lines.append("")
        lines.append("=" * 55)
        lines.append(f"SITE HEALTH — {len(urls)} pages in sitemap")
        lines.append("=" * 55)
        if broken:
            lines.append(f"  BROKEN LINKS ({len(broken)} found):")
            for url, code in broken[:10]:
                lines.append(f"    {code}  {url}")
        else:
            lines.append("  No broken links found.")
        if missing_meta:
            lines.append(f"\n  MISSING META DESCRIPTIONS ({len(missing_meta)} found):")
            for url in missing_meta[:10]:
                lines.append(f"    {url}")
        else:
            lines.append("  All checked pages have meta descriptions.")
    except Exception as e:
        lines.append(f"\n  Site health check failed: {e}")

    # --- NEWS ---
    print("Fetching news...")
    try:
        news = get_recent_news(days=2)
        lines.append("")
        lines.append("=" * 55)
        lines.append("PALM BEACH CONDO NEWS — Last 24 hours")
        lines.append("=" * 55)
        if news:
            for a in news:
                lines.append(f"  {a['title']}")
                lines.append(f"    {a['link']}\n")
        else:
            lines.append("  No relevant news in the last 24 hours.")
    except Exception as e:
        lines.append(f"\n  News fetch failed: {e}")

    # --- MARKET PULSE ---
    print("Pulling market pulse...")
    try:
        lines.append("")
        lines.append(get_market_pulse())
    except Exception as e:
        lines.append(f"\n  Market pulse failed: {e}")

    # --- RANK TRACKER ---
    print("Running rank tracker...")
    try:
        lines.append("")
        lines.append(get_rank_tracker())
    except Exception as e:
        lines.append(f"\n  Rank tracker failed: {e}")

    # --- MONTHLY REPORT (1st of month only) ---
    print("Checking monthly report...")
    try:
        monthly = get_monthly_report()
        if monthly:
            lines.append("")
            lines.append(monthly)
    except Exception as e:
        lines.append(f"\n  Monthly report failed: {e}")

    lines.append("")
    lines.append("-" * 55)
    lines.append("CondoWPB Intelligence System")

    return "\n".join(lines)


def send_report():
    body = build_report()

    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = ", ".join(RECIPIENTS)
    msg["Subject"] = f"CondoWPB Intelligence Report — {date.today().strftime('%B %d, %Y')}"
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        for recipient in RECIPIENTS:
            server.sendmail(GMAIL_USER, recipient, msg.as_string())

    print(f"Report sent to: {', '.join(RECIPIENTS)}")


if __name__ == "__main__":
    send_report()
