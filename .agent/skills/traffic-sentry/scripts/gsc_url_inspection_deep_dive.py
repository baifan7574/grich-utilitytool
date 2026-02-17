"""
GSC URL Inspection API 深度审计器
任务：使用 URL Inspection API 逐一检查页面的"真实收录状态"
"""
import os
import json
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
import sys

def load_credentials():
    """从环境变量或 JSON 文件加载凭据"""
    # 1. 尝试从直接 JSON 字符串环境变量加载（云端场景）
    env_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
    if env_json:
        try:
            info = json.loads(env_json)
            return service_account.Credentials.from_service_account_info(
                info, scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
            )
        except json.JSONDecodeError as e:
            print(f"❌ 凭据解析失败: {e}")
            sys.exit(1)

    # 2. 尝试从 .env 文件手动加载
    if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
        env_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))),
            '.env'
        )
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('GOOGLE_APPLICATION_CREDENTIALS='):
                        creds_path = line.split('=', 1)[1].strip()
                        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
                        break

    # 3. 从文件路径加载
    creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'google_service_account.json')
    if not os.path.isabs(creds_path):
        creds_path = os.path.abspath(creds_path)
        
    if not os.path.exists(creds_path):
        print(f"❌ 凭据文件未找到: {creds_path}")
        sys.exit(1)
    
    try:
        return service_account.Credentials.from_service_account_file(
            creds_path, scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
        )
    except Exception as e:
        print(f"❌ 凭据加载失败: {e}")
        sys.exit(1)

def inspect_url(service, site_url, inspection_url):
    """使用 URL Inspection API 检查单个 URL 的收录状态"""
    try:
        body = {
            "inspectionUrl": inspection_url,
            "siteUrl": site_url
        }
        
        result = service.urlInspection().index().inspect(body=body).execute()
        
        # 提取关键字段
        inspection_result = result.get('inspectionResult', {})
        index_status = inspection_result.get('indexStatusResult', {})
        
        coverage_state = index_status.get('coverageState', 'UNKNOWN')
        robotsTxtState = index_status.get('robotsTxtState', 'UNKNOWN')
        indexing_state = index_status.get('verdict', 'UNKNOWN')
        
        # 获取最后爬取时间
        last_crawl_time = index_status.get('lastCrawlTime', 'Never')
        
        return {
            'url': inspection_url,
            'coverage_state': coverage_state,
            'indexing_state': indexing_state,
            'robotsTxt': robotsTxtState,
            'last_crawl': last_crawl_time,
            'raw_data': index_status
        }
        
    except Exception as e:
        return {
            'url': inspection_url,
            'coverage_state': 'ERROR',
            'error': str(e)
        }

def main():
    print("=" * 70)
    print("🔬 GSC URL Inspection API 深度审计器")
    print("=" * 70)
    
    creds = load_credentials()
    if not creds:
        return
    
    # 使用 searchconsole v1（URL Inspection API 在 v1）
    service = build("searchconsole", "v1", credentials=creds)
    
    # 优先使用 sc-domain 属性
    site_url_domain = "sc-domain:scenro.com"
    site_url_https = "https://scenro.com/"
    
    target_site = None
    try:
        # URL Inspection API 需要使用 sc-domain 格式
        target_site = site_url_https
        print(f"✅ 目标属性: {target_site}")
    except Exception as e:
        print(f"❌ 无法连接到 GSC 属性: {e}")
        return
    
    # 读取 indexed_progress.log 中已提交的 URL
    log_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))),
        'indexed_progress.log'
    )
    
    urls_to_inspect = []
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                log_data = json.load(f)
                urls_to_inspect = log_data.get('submitted', [])[:50]  # 限制前 50 个，避免配额耗尽
        except:
            print("⚠️ 无法读取 indexed_progress.log")
            return
    
    if not urls_to_inspect:
        print("⚠️ 未找到已提交的 URL")
        return
    
    print(f"\n🔍 开始检查 {len(urls_to_inspect)} 个已提交的 URL...")
    print("⚠️ 注意: URL Inspection API 有配额限制（约 2000 次/天），本次仅检查前 50 个\n")
    
    results = []
    indexed_count = 0
    
    for i, url in enumerate(urls_to_inspect, 1):
        print(f"[{i:2d}/{len(urls_to_inspect)}] 检查中: {url}")
        
        result = inspect_url(service, target_site, url)
        results.append(result)
        
        coverage = result.get('coverage_state', 'UNKNOWN')
        if coverage == 'Submitted and indexed':
            indexed_count += 1
            print(f"         ✅ 已收录")
        elif coverage == 'Discovered - currently not indexed':
            print(f"         ⏳ 已发现但未收录")
        elif coverage == 'Crawled - currently not indexed':
            print(f"         🔄 已爬取但未收录")
        elif coverage == 'ERROR':
            print(f"         ❌ 检查失败: {result.get('error', 'Unknown')}")
        else:
            print(f"         ⚠️ {coverage}")
        
        # 避免触发配额限制，延迟 1 秒
        if i < len(urls_to_inspect):
            time.sleep(1)
    
    # 生成统计报告
    print("\n" + "=" * 70)
    print("📊 URL Inspection 统计报告")
    print("=" * 70)
    
    status_stats = {}
    for r in results:
        state = r.get('coverage_state', 'UNKNOWN')
        status_stats[state] = status_stats.get(state, 0) + 1
    
    print(f"\n【状态分布】")
    for state, count in sorted(status_stats.items(), key=lambda x: -x[1]):
        percentage = (count / len(results) * 100) if results else 0
        print(f"  • {state:35s} : {count:3d} ({percentage:5.1f}%)")
    
    print(f"\n【核心指标】")
    print(f"  • 检查总数: {len(results)}")
    print(f"  • 真实收录数: {indexed_count}")
    print(f"  • 收录率: {(indexed_count/len(results)*100) if results else 0:.1f}%")
    
    # 保存详细报告
    report_file = "gsc_url_inspection_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_inspected': len(results),
            'indexed_count': indexed_count,
            'status_stats': status_stats,
            'detailed_results': results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 详细报告已保存: {os.path.abspath(report_file)}")
    print("=" * 70)

if __name__ == "__main__":
    main()
