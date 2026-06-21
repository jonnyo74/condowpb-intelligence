import requests
from xml.etree import ElementTree

SITEMAP_URL = "https://www.condowpb.com/sitemap.xml"


def get_sitemap_urls():
    resp = requests.get(SITEMAP_URL, timeout=10)
    root = ElementTree.fromstring(resp.content)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [loc.text for loc in root.findall(".//sm:loc", ns)]
    # handle sitemap index
    if not urls:
        sitemaps = [loc.text for loc in root.findall(".//sm:sitemap/sm:loc", ns)]
        for sm in sitemaps:
            r = requests.get(sm, timeout=10)
            sub = ElementTree.fromstring(r.content)
            urls += [loc.text for loc in sub.findall(".//sm:loc", ns)]
    return urls


def check_broken_links(urls, sample=50):
    broken = []
    for url in urls[:sample]:
        try:
            r = requests.head(url, timeout=8, allow_redirects=True)
            if r.status_code >= 400:
                broken.append((url, r.status_code))
        except Exception:
            broken.append((url, "timeout"))
    return broken


def check_meta_descriptions(urls, sample=30):
    missing = []
    for url in urls[:sample]:
        try:
            r = requests.get(url, timeout=8)
            if '<meta name="description"' not in r.text and "<meta name='description'" not in r.text:
                missing.append(url)
        except Exception:
            pass
    return missing
