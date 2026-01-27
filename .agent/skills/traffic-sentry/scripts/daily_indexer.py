
import os
import json
import glob
import shutil
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
import xml.etree.ElementTree as ET

# Configuration
LIMIT_PER_DAY = 180
TRACKER_FILE = "submission_tracker.json"
SITEMAP_PATH = "../../../../dist/sitemap.xml"
DIST_DIR = "../../../../dist"
ROOT_DIR = "../../../../"

def load_env_file():
    env_path = os.path.join(ROOT_DIR, ".env")
    if os.path.exists(env_path):
        print(f"Loading .env from {env_path}")
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, _, value = line.partition('=')
                    if key and value:
                        os.environ[key.strip()] = value.strip()

def load_credentials():
    load_env_file() # Load env vars first
    key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not key_path:
        print("❌ Error: GOOGLE_APPLICATION_CREDENTIALS not found in environment.")
        return None
    
    # Resolve absolute path if needed, though env usually has absolute
    if not os.path.isabs(key_path):
        key_path = os.path.abspath(os.path.join(ROOT_DIR, key_path)) # Best guess if relative

    try:
        creds = service_account.Credentials.from_service_account_file(
            key_path, scopes=["https://www.googleapis.com/auth/indexing"]
        )
        return creds
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return None

def check_verification_file():
    print("🔍 Checking for Google Verification File...")
    # Search in Root
    gsc_files = glob.glob(os.path.join(ROOT_DIR, "google*.html"))
    if not gsc_files:
        print("❌ CRITICAL: No google*.html verification file found in project root!")
        print("   Please upload your Google Search Console verification HTML file to the root directory.")
        return False
    
    # Check in Dist
    dist_gsc_files = glob.glob(os.path.join(DIST_DIR, "google*.html"))
    if not dist_gsc_files:
        print("⚠️ File found in root but missing in dist. Attempting to copy...")
        try:
            shutil.copy(gsc_files[0], DIST_DIR)
            print(f"✅ Copied {os.path.basename(gsc_files[0])} to dist/")
            return True
        except Exception as e:
            print(f"❌ Error copying verification file: {e}")
            return False
    
    print(f"✅ Verification file present in dist: {os.path.basename(dist_gsc_files[0])}")
    return True

def get_urls_from_sitemap():
    try:
        tree = ET.parse(SITEMAP_PATH)
        root = tree.getroot()
        # Namespace handling might be needed depending on sitemap format
        # Common sitemap ns: {http://www.sitemaps.org/schemas/sitemap/0.9}
        urls = []
        for url in root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
            loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
            urls.append(loc)
        print(f"📄 Found {len(urls)} URLs in sitemap.")
        return urls
    except Exception as e:
        print(f"❌ Error parsing sitemap: {e}")
        return []

def load_tracker():
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, 'r') as f:
            return json.load(f)
    return {"submitted": [], "last_run": ""}

def save_tracker(data):
    with open(TRACKER_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    print("🚦 Traffic Sentry - Daily Indexer Starting...")
    
    # 1. Verification Check
    if not check_verification_file():
        print("🛑 Aborting indexing due to verification issues.")
        return

    # 2. Get Credentials
    creds = load_credentials()
    if not creds: return

    # 3. Get Service
    service = build("indexing", "v3", credentials=creds)

    # 4. Get URLs and Tracker
    all_urls = get_urls_from_sitemap()
    tracker = load_tracker()

    # Determine what to submit
    submitted_set = set(tracker["submitted"])
    candidates = [u for u in all_urls if u not in submitted_set]
    
    to_submit = candidates[:LIMIT_PER_DAY]
    
    if not to_submit:
        print("✅ No new URLs to submit today. All verified URLs from sitemap are processed.")
        return

    print(f"🚀 Submitting {len(to_submit)} URLs to Google Indexing API...")
    
    success_count = 0
    for url in to_submit:
        try:
            # Construct the request
            body = {
                "url": url,
                "type": "URL_UPDATED"
            }
            service.urlNotifications().publish(body=body).execute()
            print(f"   Using quota: Submitted {url}")
            tracker["submitted"].append(url)
            success_count += 1
        except Exception as e:
            print(f"   ❌ Failed {url}: {e}")

    tracker["last_run"] = datetime.datetime.now().isoformat()
    save_tracker(tracker)
    
    print(f"🏁 Done. Successfully submitted {success_count}/{len(to_submit)} URLs.")

if __name__ == "__main__":
    main()
