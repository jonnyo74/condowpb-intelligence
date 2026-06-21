BUILDING_NAMES = {
    "olara": "Olara",
    "south-flagler-house": "South Flagler House",
    "alba-palm-beach": "Alba Palm Beach",
    "the-bristol": "The Bristol",
    "mr-c-residences-wpb": "Mr. C Residences",
    "mandarin-oriental-residences-wpb": "Mandarin Oriental Residences",
    "ritz-carlton-residences-wpb": "Ritz-Carlton Residences",
    "nora-house": "Nora House",
    "forte-on-flagler": "Forte on Flagler",
    "shorecrest": "Shorecrest",
    "the-berkeley-palm-beach": "The Berkeley Palm Beach",
    "banyan-tree-residences-wpb": "Banyan Tree Residences",
    "maison-dor-wpb": "Maison d'Or",
    "flagler-pointe": "Flagler Pointe",
}

HASHTAGS = "#WestPalmBeach #WPBCondos #PalmBeachRealEstate #LuxuryRealEstate #CondoLife #JohnOliver #DOHomesGroup"


def get_fix_these(pages):
    """Pages almost on page 1 with zero clicks — fix title/meta first."""
    return [
        r for r in pages
        if r["impressions"] >= 20 and r["clicks"] == 0 and r["position"] <= 30
    ][:3]


def get_blog_ideas(pages, queries):
    ideas = []
    seen = set()

    # From high-impression queries with no good page yet
    for r in queries:
        if len(ideas) >= 3:
            break
        query = r["keys"][0]
        if r["impressions"] < 3 or query in seen:
            continue
        q = query.lower()
        idea = None

        if "hoa" in q:
            idea = {
                "keyword": query,
                "headline": "HOA Fees in West Palm Beach Condos: What's Actually Included",
                "angle": "Break down HOA fees by building tier. What does $500/mo get you vs $2,500/mo? Cover reserves, amenities, special assessments.",
                "impressions": r["impressions"],
            }
        elif "rental restriction" in q or "rent" in q:
            idea = {
                "keyword": query,
                "headline": "Which West Palm Beach Condos Allow Rentals (And Which Don't)",
                "angle": "Cover 30-day vs 1-year minimums, investor-friendly buildings, and what to check before buying.",
                "impressions": r["impressions"],
            }
        elif "new construction" in q or "pre-construction" in q:
            idea = {
                "keyword": query,
                "headline": "New Construction Condos in West Palm Beach: What's Coming in 2026",
                "angle": "Cover all active projects, expected delivery dates, price ranges, and which are still accepting reservations.",
                "impressions": r["impressions"],
            }
        elif "flagler" in q:
            idea = {
                "keyword": query,
                "headline": "Living on Flagler Drive: West Palm Beach's Most Coveted Address",
                "angle": "Cover the buildings, the views, the lifestyle, price ranges, and what makes Flagler different from everything else.",
                "impressions": r["impressions"],
            }
        elif "beachfront" in q or "waterfront" in q:
            idea = {
                "keyword": query,
                "headline": "Beachfront vs Intracoastal Condos in Palm Beach County: What's the Difference",
                "angle": "Cover price differences, lifestyle differences, buildings available in each category.",
                "impressions": r["impressions"],
            }
        elif "sell" in q or "selling" in q:
            idea = {
                "keyword": query,
                "headline": "How to Sell Your West Palm Beach Condo in 2026",
                "angle": "Cover timing, pricing strategy, staging, HOA disclosures, and what buyers are looking for right now.",
                "impressions": r["impressions"],
            }

        if idea:
            ideas.append(idea)
            seen.add(query)

    # From high-impression building pages
    for r in pages:
        if len(ideas) >= 3:
            break
        url = r["keys"][0].replace("https://condowpb.com", "").replace("https://www.condowpb.com", "")
        parts = url.strip("/").split("/")
        if len(parts) == 2 and parts[0] == "buildings" and r["impressions"] >= 20:
            slug = parts[1]
            if slug in seen:
                continue
            name = BUILDING_NAMES.get(slug, slug.replace("-", " ").title())
            ideas.append({
                "keyword": f"{name} West Palm Beach",
                "headline": f"{name}: Everything You Need to Know Before Buying",
                "angle": f"Cover floor plans, pricing, amenities, HOA fees, views, pet policy, rental restrictions, and who this building is best for.",
                "impressions": r["impressions"],
            })
            seen.add(slug)

    return ideas[:3]


def get_social_captions(blog_ideas):
    captions = []
    for idea in blog_ideas:
        caption = (
            f"{idea['headline'].split(':')[0]} — "
            f"new guide on condowpb.com covers everything you need to know. "
            f"Link in bio. {HASHTAGS}"
        )
        captions.append({"blog": idea["headline"], "caption": caption})
    return captions


def format_content_section(pages, queries):
    lines = []

    # FIX THESE
    fix_these = get_fix_these(pages)
    lines.append("=" * 55)
    lines.append("FIX THESE FIRST — Quick wins on existing pages")
    lines.append("=" * 55)
    if fix_these:
        for r in fix_these:
            url = r["keys"][0].replace("https://condowpb.com", "").replace("https://www.condowpb.com", "")
            lines.append(f"  {url}")
            lines.append(f"    {r['impressions']:.0f} impressions · position {r['position']:.1f} · 0 clicks")
            lines.append(f"    → Rewrite the page title and meta description to get clicks")
        lines.append("")
    else:
        lines.append("  No quick-win pages identified this week.\n")

    # WRITE THESE
    blog_ideas = get_blog_ideas(pages, queries)
    lines.append("=" * 55)
    lines.append("WRITE THESE — Blog ideas from your search data")
    lines.append("=" * 55)
    if blog_ideas:
        for i, idea in enumerate(blog_ideas, 1):
            lines.append(f"  BLOG {i}: {idea['headline']}")
            lines.append(f"  Keyword: {idea['keyword']} ({idea['impressions']:.0f} impressions)")
            lines.append(f"  Angle: {idea['angle']}")
            lines.append("")
    else:
        lines.append("  No blog ideas generated this week — check back tomorrow.\n")

    # POST THESE
    social = get_social_captions(blog_ideas)
    lines.append("=" * 55)
    lines.append("POST THESE — Social captions for your blogs")
    lines.append("=" * 55)
    if social:
        for i, s in enumerate(social, 1):
            lines.append(f"  POST {i} — For: {s['blog']}")
            lines.append(f"  {s['caption']}")
            lines.append("")
    else:
        lines.append("  No social posts generated this week.\n")

    return "\n".join(lines)
