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

GUIDE_TOPICS = {
    "hoa-fees-explained": ("HOA Fees in WPB Condos", "HOA fees in West Palm Beach condos range from $500 to $3,000+/month. Here's what's actually included — and what to watch out for before you buy."),
    "rental-restrictions-guide": ("Rental Restrictions", "Not all West Palm Beach condos allow short-term rentals. Some require 1-year minimums. Know the rules before you buy as an investment."),
    "new-construction-vs-resale": ("New Construction vs Resale", "New construction or resale — which is the better buy in West Palm Beach right now? The answer might surprise you."),
    "condo-investment-guide": ("Condo Investing in WPB", "West Palm Beach condos are attracting investors from New York, London, and beyond. Here's what makes this market different."),
    "prepare-condo-for-sale": ("Preparing Your Condo to Sell", "Thinking about selling your West Palm Beach condo? A few simple moves before you list can add thousands to your sale price."),
    "downtown-wpb-food-tour": ("Downtown WPB Food Scene", "Downtown West Palm Beach has one of the best restaurant scenes in South Florida — and most people don't even know it."),
}

HASHTAGS = "#WestPalmBeach #WPBCondos #PalmBeachRealEstate #LuxuryRealEstate #CondoLife #PalmBeachCounty #JohnOliver #DOHomesGroup"


def make_building_caption(slug, impressions):
    name = BUILDING_NAMES.get(slug, slug.replace("-", " ").title())
    return (
        f"{name} is one of the most searched luxury buildings in West Palm Beach right now — "
        f"{impressions:.0f} people looked it up this month. "
        f"Want to know what units are available and what they're selling for? DM me. "
        f"{HASHTAGS}"
    )


def make_guide_caption(slug, impressions):
    if slug in GUIDE_TOPICS:
        title, teaser = GUIDE_TOPICS[slug]
        return f"{teaser} Full guide at condowpb.com. {HASHTAGS}"
    return None


def make_query_caption(query, impressions):
    q = query.lower()
    if "hoa" in q:
        return f"One of the most common questions I get: what are HOA fees like in West Palm Beach condos? It varies wildly by building — here's how to think about it. {HASHTAGS}"
    if "rental" in q or "rent" in q:
        return f"Can you rent out a West Palm Beach condo? Some buildings allow it, some don't. Here's what you need to know before buying as an investment. {HASHTAGS}"
    if "flagler" in q:
        return f"Flagler Drive is the most coveted address in West Palm Beach. Intracoastal views, luxury towers, walkable to downtown. Here's what's available right now. {HASHTAGS}"
    if "new construction" in q or "pre-construction" in q:
        return f"West Palm Beach has more new construction condo projects underway than ever before. Here's what's coming — and what's still available at pre-construction pricing. {HASHTAGS}"
    if "beachfront" in q or "waterfront" in q:
        return f"Waterfront condos in Palm Beach County start around $1M. What you get for your money varies wildly by building. Want a breakdown? DM me. {HASHTAGS}"
    if "sell" in q or "selling" in q:
        return f"Thinking about selling your West Palm Beach condo? The market is still strong for well-priced luxury units. DM me for a free valuation. {HASHTAGS}"
    return None


def generate_social_ideas(pages, queries):
    ideas = []
    seen = set()

    for r in pages:
        if len(ideas) >= 3:
            break
        url = r["keys"][0].replace("https://condowpb.com", "").replace("https://www.condowpb.com", "")
        impressions = r["impressions"]
        if impressions < 10:
            continue

        parts = url.strip("/").split("/")

        if len(parts) == 2 and parts[0] == "buildings":
            slug = parts[1]
            if slug in seen:
                continue
            caption = make_building_caption(slug, impressions)
            ideas.append({"source": f"{impressions:.0f} impressions on /buildings/{slug}", "caption": caption})
            seen.add(slug)

        elif len(parts) == 2 and parts[0] == "guides":
            slug = parts[1]
            if slug in seen:
                continue
            caption = make_guide_caption(slug, impressions)
            if caption:
                ideas.append({"source": f"{impressions:.0f} impressions on /guides/{slug}", "caption": caption})
                seen.add(slug)

        elif parts[0] == "new-construction":
            if "new-construction" not in seen:
                ideas.append({"source": f"{impressions:.0f} impressions on /new-construction", "caption": f"West Palm Beach has more new luxury condo towers under construction than at any point in its history. Here's what's coming. {HASHTAGS}"})
                seen.add("new-construction")

    for r in queries:
        if len(ideas) >= 3:
            break
        query = r["keys"][0]
        if r["impressions"] < 3 or query in seen:
            continue
        caption = make_query_caption(query, r["impressions"])
        if caption:
            ideas.append({"source": f"{r['impressions']:.0f} people searched '{query}'", "caption": caption})
            seen.add(query)

    if not ideas:
        ideas.append({
            "source": "General WPB content",
            "caption": f"West Palm Beach's luxury condo market is unlike anywhere else in Florida. Intracoastal towers, world-class amenities, and a downtown that keeps growing. Thinking about buying? Let's talk. {HASHTAGS}"
        })

    return ideas[:3]


def format_social_section(pages, queries):
    ideas = generate_social_ideas(pages, queries)
    lines = []
    lines.append("=" * 55)
    lines.append("POST THESE TODAY — Social Media Ideas")
    lines.append("=" * 55)
    lines.append("Based on what people are actually searching for:\n")

    for i, idea in enumerate(ideas, 1):
        lines.append(f"  POST {i} — {idea['source']}")
        lines.append(f"  {idea['caption']}")
        lines.append("")

    return "\n".join(lines)
