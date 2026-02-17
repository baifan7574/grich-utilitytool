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
    raw_urls = parse_sitemap(LIVE_SITEMAP_URL)
    
    # CRITICAL FIX: Force strip .html suffix to align with Cloudflare Pretty URLs
    urls = []
    stripped_count = 0
    for url in raw_urls:
        if url.endswith('.html'):
            clean_url = url[:-5]  # Remove last 5 chars (.html)
            urls.append(clean_url)
            stripped_count += 1
        else:
            urls.append(url)
    
    print(f"✅ Found {len(urls)} URLs in Live Sitemap.")
    if stripped_count > 0:
        print(f"🔧 Stripped .html suffix from {stripped_count} URLs (Cloudflare Pretty URLs alignment)")
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

    # FOUNDER DIRECTIVE: Prioritize Medical URLs (50 slots) for higher Google authority weight
    MEDICAL_KEYWORDS = ['surgeon', 'physician', 'doctor', 'nurse', 'medical', 'therapist', 'counselor', 'chiropractor', 'dentist', 'pharmacist', 'optometrist', 'veterinarian', 'psychiatrist', 'psychologist', 'radiologist', 'anesthesiologist', 'pathologist', 'dermatologist', 'cardiologist', 'neurologist', 'oncologist', 'pediatrician', 'urologist', 'gynecologist']
    MEDICAL_PRIORITY_SLOTS = 50
    
    medical_urls = [u for u in virgin_territory if any(kw in u.lower() for kw in MEDICAL_KEYWORDS)]
    other_urls = [u for u in virgin_territory if u not in medical_urls]
    
    # Assemble: Medical first (up to 50), then fill remaining with others
    priority_batch = medical_urls[:MEDICAL_PRIORITY_SLOTS]
    remaining_slots = LIMIT_PER_DAY - len(priority_batch)
    priority_batch.extend(other_urls[:remaining_slots])
    
    to_submit = priority_batch
    print(f"🚀 Launching submission for {len(to_submit)} URLs (Medical Priority: {min(len(medical_urls), MEDICAL_PRIORITY_SLOTS)})...")
    
    service = build("indexing", "v3", credentials=creds)
    success_count = 0
    quota_hit = False
    
    # 优化配额管理：使用更智能的错误处理
    daily_quota_used = 0
    max_daily_quota = LIMIT_PER_DAY
    
    for url in to_submit:
        # 检查是否已达到每日配额上限
        if daily_quota_used >= max_daily_quota:
            print(f"   📊 已达到每日配额上限 ({max_daily_quota})，停止提交")
            break
            
        try:
            body = {"url": url, "type": "URL_UPDATED"}
            service.urlNotifications().publish(body=body).execute()
            print(f"   ✅ Submitted: {url}")
            log_data["submitted"].append(url)
            success_count += 1
            daily_quota_used += 1
            time.sleep(0.5) # Gentle rate limit
        except HttpError as e:
            if e.resp.status == 429:
                print(f"   ⚠️ 配额限制 (429)，跳过当前URL，继续尝试下一个")
                log_data["failed_429"].append({"url": url, "time": datetime.datetime.now().isoformat()})
                # 不再立即停止，而是跳过当前URL继续尝试
                time.sleep(2) # 遇到429后增加等待时间
                continue  # 跳过当前URL，继续下一个
            elif e.resp.status == 403:
                print(f"   ❌ 403 Permission Denied. Check Owner status.")
                break
            else:
                print(f"   ⚠️ Failed {url}: {e}")
                time.sleep(1) # 其他错误也稍作等待
        except Exception as e:
             print(f"   ❌ Error: {e}")
             time.sleep(1)

    log_data["last_run"] = datetime.datetime.now().isoformat()
    log_data["last_batch_count"] = success_count
    save_log(log_data)
    
    print(f"\n🏁 Mission Report: Submitted {success_count}/{len(to_submit)} URLs.")
    
    # 详细统计报告
    print(f"📊 详细统计:")
    print(f"   • 每日配额上限: {LIMIT_PER_DAY}")
    print(f"   • 目标提交数量: {len(to_submit)}")
    print(f"   • 成功提交数量: {success_count}")
    print(f"   • 成功率: {round((success_count/len(to_submit))*100, 1) if to_submit else 0}%")
    print(f"   • 剩余未提交URL: {len(virgin_territory) - success_count}")
    print(f"   • 累计已提交总数: {len(log_data['submitted'])}")
    
    if quota_hit:
        print("⚠️ 配额限制触发，部分URL遇到429错误（已跳过）")
    else:
        print(f"✅ 每日批次完成，配额使用: {daily_quota_used}/{max_daily_quota}")
        
    # 提供优化建议
    print(f"\n💡 优化建议:")
    print(f"   1. 确保sitemap包含足够多的URL（当前找到 {len(sitemap_urls)} 个）")
    print(f"   2. 每日配额: {LIMIT_PER_DAY}，实际使用: {daily_quota_used}")
    print(f"   3. 下次运行时间: 24小时后")

if __name__ == "__main__":
    main()
