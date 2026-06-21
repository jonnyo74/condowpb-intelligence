import requests
from bs4 import BeautifulSoup
from datetime import datetime

TARGET_BUILDINGS = [
    "Olara", "Nora House", "The Ritz-Carlton Residences", "Mr. C Residences",
    "Mandarin Oriental Residences", "The Berkeley Palm Beach", "Alba Palm Beach",
    "Maison d'Or", "South Flagler House", "Forté on Flagler", "Shorecrest",
    "Banyan Tree Residences", "Edgeworth", "The Bristol", "Esperanté",
    "La Clara", "Plaza of the Palm Beaches", "Esplanade Grande", "Rapallo",
    "One Watermark Place", "The Edge", "Flagler Pointe",
    "Tower Condominium at CityPlace", "CityPlace South Tower", "Portofino North",
    "Portofino South", "The Whitney", "Waterview Towers", "The Slade",
    "The Prado", "The Strand", "Montecito Palm Beach", "One City Plaza",
    "Two City Plaza", "Courtyards in CityPlace", "610 Clematis", "City Palms",
    "The Metropolitan", "Villa del Lago", "Palm Beach House", "Placido Mar",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

STALE_DOM_THRESHOLD = 45


def get_market_listings():
    listings = []
    try:
        url = "https://www.zillow.com/west-palm-beach-fl/condos/"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("article", {"data-test": "property-card"})
        for card in cards:
            try:
                address_el = card.find("address")
                price_el = card.find("span", {"data-test": "property-card-price"})
                link_el = card.find("a", {"data-test": "property-card-link"})
                address = address_el.text.strip() if address_el else "Unknown"
                price = price_el.text.strip() if price_el else "Unknown"
                link = "https://www.zillow.com" + link_el["href"] if link_el else ""
                listings.append({"address": address, "price": price, "link": link})
            except Exception:
                continue
    except Exception as e:
        return [], f"Zillow fetch failed: {e}"
    return listings, None


def flag_target_building_listings(listings):
    flagged = []
    for listing in listings:
        for building in TARGET_BUILDINGS:
            if building.lower() in listing["address"].lower():
                listing["building"] = building
                flagged.append(listing)
                break
    return flagged


def get_price_drops():
    reduced = []
    try:
        url = "https://www.zillow.com/west-palm-beach-fl/condos/?reducedIn=30"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("article", {"data-test": "property-card"})
        for card in cards[:10]:
            try:
                address_el = card.find("address")
                price_el = card.find("span", {"data-test": "property-card-price"})
                link_el = card.find("a", {"data-test": "property-card-link"})
                address = address_el.text.strip() if address_el else "Unknown"
                price = price_el.text.strip() if price_el else "Unknown"
                link = "https://www.zillow.com" + link_el["href"] if link_el else ""
                reduced.append({"address": address, "price": price, "link": link})
            except Exception:
                continue
    except Exception as e:
        return [], f"Price drop fetch failed: {e}"
    return reduced, None


def format_market_pulse_section(listings, flagged, price_drops):
    lines = []
    lines.append("=" * 55)
    lines.append("MARKET PULSE — West Palm Beach Condos")
    lines.append("=" * 55)
    lines.append(f"\n  Active WPB condo listings found: {len(listings)}")
    if flagged:
        lines.append(f"\n  YOUR BUILDINGS ({len(flagged)} active listings):")
        for l in flagged:
            lines.append(f"    {l['address']}")
            lines.append(f"    Price: {l['price']}")
            lines.append(f"    {l['link']}\n")
    else:
        lines.append("\n  No active listings found in target buildings.")
    lines.append(f"\n  RECENT PRICE DROPS (last 30 days):")
    if price_drops:
        for l in price_drops[:5]:
            lines.append(f"    {l['address']}  —  {l['price']}")
            lines.append(f"    {l['link']}\n")
    else:
        lines.append("    None detected.")
    lines.append(f"\n  Note: Units over {STALE_DOM_THRESHOLD} DOM = potential listing conversation.")
    return "\n".join(lines)


def get_market_pulse():
    listings, err1 = get_market_listings()
    flagged = flag_target_building_listings(listings)
    price_drops, err2 = get_price_drops()
    return format_market_pulse_section(listings, flagged, price_drops)
