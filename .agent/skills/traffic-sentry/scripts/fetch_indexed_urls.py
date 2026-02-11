import os
import json
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

def load_credentials():
    """Load credentials from ENV JSON content or file."""
    env_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
    if env_json:
        try:
            info = json.loads(env_json)
            return service_account.Credentials.from_service_account_info(
                info, scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
            )
        except json.JSONDecodeError as e:
            print(f"❌ Error: Failed to decode GOOGLE_CREDENTIALS_JSON: {e}")
            return None

    # Fallback to file
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('GOOGLE_APPLICATION_CREDENTIALS='):
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = line.split('=', 1)[1].strip()
                    break

    creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'google_service_account.json')
    if not os.path.isabs(creds_path):
        creds_path = os.path.abspath(creds_path)
        
    if not os.path.exists(creds_path):
        print(f"❌ Error: Credential file not found at {creds_path}")
        return None
    
    try:
        return service_account.Credentials.from_service_account_file(
            creds_path, scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
        )
    except Exception as e:
        print(f"❌ Credential Error: {e}")
        return None

def get_indexed_urls(service, site_url):
    """Fetch all indexed URLs from GSC using URL Inspection API."""
    print(f"🔍 Fetching indexed URLs from {site_url}...")
    
    # Use Search Analytics to get pages with impressions (proxy for indexed)
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=28)  # Last 28 days
    
    request = {
        'startDate': start_date.isoformat(),
        'endDate': end_date.isoformat(),
        'dimensions': ['page'],
        'rowLimit': 25000
    }
    
    try:
        response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
        rows = response.get('rows', [])
        urls = [row['keys'][0] for row in rows]
        
        print(f"✅ Found {len(urls)} indexed URLs")
        return urls
    except Exception as e:
        print(f"❌ Error fetching indexed URLs: {e}")
        return []

def main():
    print("🚦 GSC Indexed URLs Fetcher")
    creds = load_credentials()
    if not creds:
        return
    
    service = build("webmasters", "v3", credentials=creds)
    site_url_domain = "sc-domain:scenro.com"
    
    try:
        service.sites().get(siteUrl=site_url_domain).execute()
        target_site = site_url_domain
        print(f"✅ Accessed property: {target_site}")
    except Exception as e:
        print(f"❌ Failed to access property: {e}")
        return

    indexed_urls = get_indexed_urls(service, target_site)
    
    # Categorize URLs
    categorized = {
        "/p/": [],
        "/blog/": [],
        "homepage": [],
        "legal": [],
        "other": []
    }
    
    for url in indexed_urls:
        if "/p/" in url:
            categorized["/p/"].append(url)
        elif "/blog/" in url:
            categorized["/blog/"].append(url)
        elif url.endswith("/") or url.endswith("index"):
            categorized["homepage"].append(url)
        elif any(x in url for x in ["/privacy", "/terms", "/contact", "/about"]):
            categorized["legal"].append(url)
        else:
            categorized["other"].append(url)
    
    # Save report
    output_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))),
        "gsc_indexed_urls_report.json"
    )
    
    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "total_count": len(indexed_urls),
        "path_stats": {k: len(v) for k, v in categorized.items()},
        "categorized_urls": categorized,
        "all_urls": indexed_urls
    }
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📊 === INDEXED URLS REPORT ===")
    print(f"Total Indexed: {len(indexed_urls)}")
    print(f"  /p/ pages: {len(categorized['/p/'])}")
    print(f"  /blog/ pages: {len(categorized['/blog/'])}")
    print(f"  Legal pages: {len(categorized['legal'])}")
    print(f"  Homepage: {len(categorized['homepage'])}")
    print(f"  Other: {len(categorized['other'])}")
    print(f"\n✅ Report saved to: {output_file}")

if __name__ == "__main__":
    main()
