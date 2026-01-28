import os
import json
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

def load_credentials():
    """Load credentials from JSON file defined in ENV, .env file, or default path."""
    # Try to load from .env file manually if env var not set
    if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), '.env')
        # Fallback to current working directory
        if not os.path.exists(env_path):
             env_path = ".env"
             
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('GOOGLE_APPLICATION_CREDENTIALS='):
                        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = line.split('=', 1)[1].strip()
                        break

    creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'google_service_account.json')
    # If path is relative, make it absolute based on current working dir (which should be project root)
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

def get_indexing_stats(service, site_url):
    """Fetch sitemap status to infer indexing count."""
    try:
        # Check Sitemaps
        sitemaps = service.sitemaps().list(siteUrl=site_url).execute()
        
        total_indexed = 0
        print(f"🔍 Checking Sitemaps for {site_url}...")
        
        if 'sitemap' in sitemaps:
            for sm in sitemaps['sitemap']:
                path = sm.get('path', 'Unknown')
                # Note: 'indexed' field in sitemaps resource is deprecated/removed in some API versions 
                # or not always reliable, but let's check what we get.
                # Actually, the 'contents' field might contain stats per type depending on API version
                # But typically valid Sitemaps don't directly return 'indexed pages' count reliably in this API endpoint anymore.
                # However, let's try to inspect carefully.
                
                # Alternate approach: Search Analytics for pages that have impressions
                print(f"   - Sitemap: {path} | Last Download: {sm.get('lastDownloaded')}")
        else:
            print("   ⚠️ No sitemaps found.")

        # Real "Index" status is best approximated by Search Analytics for "pages receiving impressions"
        # OR by using the URL Inspection API for a sample (too slow for "total count")
        # GSC API doesn't give a simple "Total Indexed Pages" number directly like the UI does.
        # But we can query search analytics for pages with >0 impressions in last few days to see "active" pages.
        
        # Let's try to query status for the last 3 days to get a sense of "active in search"
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=3)
        
        request = {
            'startDate': start_date.isoformat(),
            'endDate': end_date.isoformat(),
            'dimensions': ['page'],
            'rowLimit': 25000  # Max limit
        }
        
        response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
        rows = response.get('rows', [])
        active_pages = len(rows)
        
        print(f"📊 Active Pages (Impressions > 0 in last 3 days): {active_pages}")
        return active_pages

    except Exception as e:
        print(f"❌ Error fetching stats: {e}")
        return 0

def main():
    print("🚦 GSC Status Checker")
    creds = load_credentials()
    if not creds: return
    
    service = build("webmasters", "v3", credentials=creds)
    site_url = "https://scenro.com/" # Ensure it matches GSC property exactly (sc-domain:scenro.com or https://scenro.com/)
    
    # Try sc-domain first if URL fails, or inspect logic. 
    # Usually 'sc-domain:scenro.com' is safer for domain properties.
    site_url_domain = "sc-domain:scenro.com"
    
    try:
        # Quick verify access
        service.sites().get(siteUrl=site_url_domain).execute()
        target_site = site_url_domain
        print(f"✅ Accessed property: {target_site}")
    except:
        target_site = site_url
        print(f"⚠️ Falling back to URL property: {target_site}")

    current_count = get_indexing_stats(service, target_site)
    
    # Check for previous log locally
    today = datetime.date.today().isoformat()
    log_file = "gsc_daily_stats.json"
    
    history = {}
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                history = json.load(f)
        except: pass
        
    last_count = history.get("last_count", 0)
    diff = current_count - last_count
    
    # Update log
    history["last_count"] = current_count
    history["last_check"] = today
    with open(log_file, 'w') as f:
        json.dump(history, f)
        
    
    # Read Indexing Log for Briefing
    indexing_log = {}
    log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "indexed_progress.log")
    if os.path.exists(log_path):
        try:
            with open(log_path, 'r') as f:
                indexing_log = json.load(f)
        except: pass

    last_run = indexing_log.get("last_run", "N/A")
    last_batch = indexing_log.get("last_batch_count", 0)
    total_submitted = len(indexing_log.get("submitted", []))
        
    print("\n📈 === REPORT SUMMARY ===")
    print(f"Current Active Pages: {current_count}")
    print(f"Growth vs Last Check: {diff:+d}")
    print(f"API Successful Pushes (Last Run): {last_batch} (Total: {total_submitted})")
    print(f"Last Run Time: {last_run}")

if __name__ == "__main__":
    main()
