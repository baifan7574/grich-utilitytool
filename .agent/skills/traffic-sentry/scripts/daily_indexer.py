import os
import json
import time
import datetime
import random
import requests # Added for fetching live sitemap
import xml.etree.ElementTree as ET
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configuration
LIMIT_PER_DAY = 180
# Force script to run in current directory context for GitHub Actions
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) 
# In CI/CD, we must save log to REPO ROOT to allow git add to find it
LOG_FILE = os.path.abspath(os.path.join(ROOT_DIR, "../../../../indexed_progress.log")) 
# CRITICAL FIX for Cloud: Read from LIVE site, not local disk
LIVE_SITEMAP_URL = "https://scenro.com/sitemap.xml"

# Placeholder to prevent NameError in legacy calls
def check_verification_file():
    return True

import sys

def load_credentials():
    """Load credentials from ENV JSON content (Priority) or File."""
    # 0. Local Dev: Try loading .env
    if 'GOOGLE_CREDENTIALS_JSON' not in os.environ and 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
         # Need 5 levels up: scripts -> traffic-sentry -> skills -> .agent -> scenro
         env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))), '.env')
         if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        parts = line.strip().split('=', 1)
                        if len(parts) == 2:
                            os.environ[parts[0]] = parts[1]

    # 1. Try Loading from Direct JSON String in Env (Cloud/GitHub Actions Best Practice)
    env_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
    if env_json:
        try:
            info = json.loads(env_json)
            return service_account.Credentials.from_service_account_info(
                info, scopes=["https://www.googleapis.com/auth/indexing"]
            )
        except json.JSONDecodeError as e:
            print(f"❌ Error: Failed to decode GOOGLE_CREDENTIALS_JSON: {e}")
            sys.exit(1) # Critical Failure

    # 2. Fallback to File Path (Local Dev)
    creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'google_service_account.json')
    
    # Try to find file if path is relative
    if not os.path.exists(creds_path):
        # Check current dir
        if os.path.exists("google_service_account.json"):
            creds_path = "google_service_account.json"
        else:
             print(f"❌ Error: Credential file not found at {creds_path} and GOOGLE_CREDENTIALS_JSON not set.")
             sys.exit(1) # Critical Failure
    
    try:
        return service_account.Credentials.from_service_account_file(
            creds_path, scopes=["https://www.googleapis.com/auth/indexing"]
        )
    except Exception as e:
        print(f"❌ Credential Error: {e}")
        sys.exit(1) # Critical Failure

def parse_sitemap(url):
    """Recursively fetch URLs from a sitemap or sitemap index."""
    print(f"   📍 Parsing: {url}")
    urls = []
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code != 200:
            print(f"   ❌ Failed to fetch {url}: {resp.status_code}")
            return []
            
        root = ET.fromstring(resp.content)
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        # Check if it's a sitemap index
        if 'sitemapindex' in root.tag:
            for sm in root.findall('ns:sitemap', namespace):
                loc = sm.find('ns:loc', namespace)
                if loc is not None and loc.text:
                    urls.extend(parse_sitemap(loc.text.strip()))
        else:
             # Regular sitemap
            for url_tag in root.findall('ns:url', namespace):
                loc = url_tag.find('ns:loc', namespace)
                if loc is not None and loc.text:
                    urls.append(loc.text.strip())
                    
        return urls
    except Exception as e:
        print(f"   ❌ Error parsing {url}: {e}")
        return []

def get_urls_from_sitemap():
    """Parse the sitemap to get all target URLs. Supports Remote URL."""
    print(f"🌍 Fetching Sitemap from: {LIVE_SITEMAP_URL}")
    urls = parse_sitemap(LIVE_SITEMAP_URL)
    print(f"✅ Found {len(urls)} URLs in Live Sitemap.")
    return urls


def load_log():
    # Ensure dir exists for log file
    log_dir = os.path.dirname(LOG_FILE)
    if not os.path.exists(log_dir):
        try: os.makedirs(log_dir)
        except: pass

    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"submitted": [], "failed_429": [], "last_run": ""}
    return {"submitted": [], "failed_429": [], "last_run": ""}

def save_log(data):
    with open(LOG_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    print("🚦 Traffic Sentry - Daily Indexer & Auditor (Cloud Fix V2.1)")
    
    # Verification file check skipped in cloud environment as dist might not exist locally
    if not check_verification_file(): return
    creds = load_credentials()
    if not creds: return
    
    # Snapshot Logic
    sitemap_urls = get_urls_from_sitemap()
    log_data = load_log()
    
    submitted_set = set(log_data["submitted"])
    virgin_territory = [u for u in sitemap_urls if u not in submitted_set]
    
    print("\n📊 === STATUS SNAPSHOT ===")
    print(f"Total Pages (Sitemap): {len(sitemap_urls)}")
    print(f"Already Submitted    : {len(submitted_set)}")
    print(f"Virgin Territory     : {len(virgin_territory)} (Unsubmitted)")
    print("=========================\n")
    
    if not virgin_territory:
        print("✅ Analysis Complete: No new pages to index.")
        return

    # Submitting
    to_submit = virgin_territory[:LIMIT_PER_DAY]
    print(f"🚀 Launching submission for {len(to_submit)} URLs...")
    
    service = build("indexing", "v3", credentials=creds)
    success_count = 0
    quota_hit = False
    
    for url in to_submit:
        try:
            body = {"url": url, "type": "URL_UPDATED"}
            service.urlNotifications().publish(body=body).execute()
            print(f"   ✅ Submitted: {url}")
            log_data["submitted"].append(url)
            success_count += 1
            time.sleep(0.5) # Gentle rate limit
        except HttpError as e:
            if e.resp.status == 429:
                print(f"   🛑 QUOTA HIT (429)! Stopping immediately as per Rule 4.1.")
                log_data["failed_429"].append({"url": url, "time": datetime.datetime.now().isoformat()})
                quota_hit = True
                break
            elif e.resp.status == 403:
                print(f"   ❌ 403 Permission Denied. Check Owner status.")
                break
            else:
                print(f"   ⚠️ Failed {url}: {e}")
        except Exception as e:
             print(f"   ❌ Error: {e}")

    log_data["last_run"] = datetime.datetime.now().isoformat()
    log_data["last_batch_count"] = success_count
    save_log(log_data)
    
    print(f"\n🏁 Mission Report: Submitted {success_count}/{len(to_submit)}.")
    if quota_hit:
        print("⚠️ Circuit Breaker Active. Resuming in 24h.")
    else:
        print(f"✅ Daily batch complete. {len(virgin_territory) - success_count} remaining for future batches.")

if __name__ == "__main__":
    main()
