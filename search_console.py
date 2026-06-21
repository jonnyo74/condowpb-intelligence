import os
from datetime import date, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "credentials.json")
SITE_URL = "sc-domain:condowpb.com"
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]


def get_service():
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    return build("searchconsole", "v1", credentials=creds)


def get_top_pages(service, days=28):
    end_date = date.today() - timedelta(days=2)
    start_date = end_date - timedelta(days=days)

    response = service.searchanalytics().query(
        siteUrl=SITE_URL,
        body={
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "dimensions": ["page"],
            "rowLimit": 25,
            "orderBy": [{"fieldName": "clicks", "sortOrder": "DESCENDING"}],
        },
    ).execute()

    return response.get("rows", [])


def get_top_queries(service, days=28):
    end_date = date.today() - timedelta(days=2)
    start_date = end_date - timedelta(days=days)

    response = service.searchanalytics().query(
        siteUrl=SITE_URL,
        body={
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "dimensions": ["query"],
            "rowLimit": 25,
            "orderBy": [{"fieldName": "impressions", "sortOrder": "DESCENDING"}],
        },
    ).execute()

    return response.get("rows", [])


def print_report():
    service = get_service()

    print("=" * 60)
    print("CondoWPB Search Console Report")
    print(f"Last 28 days ending {(date.today() - timedelta(days=2)).isoformat()}")
    print("=" * 60)

    print("\nTOP PAGES BY CLICKS")
    print("-" * 60)
    pages = get_top_pages(service)
    for row in pages:
        url = row["keys"][0].replace("https://condowpb.com", "")
        clicks = row["clicks"]
        impressions = row["impressions"]
        position = round(row["position"], 1)
        print(f"  {clicks:4.0f} clicks  {impressions:6.0f} impr  pos {position:5.1f}  {url}")

    print("\nTOP QUERIES BY IMPRESSIONS")
    print("-" * 60)
    queries = get_top_queries(service)
    for row in queries:
        query = row["keys"][0]
        clicks = row["clicks"]
        impressions = row["impressions"]
        position = round(row["position"], 1)
        print(f"  {clicks:4.0f} clicks  {impressions:6.0f} impr  pos {position:5.1f}  {query}")


if __name__ == "__main__":
    print_report()
