"""
GSC 收录深度审计工具
任务：查询已收录的 41 个页面的具体 URL，分析路径结构
"""
import os
import json
import datetime
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

def get_indexed_urls(service, site_url, days_back=7):
    """获取最近有展示记录的 URL（近似"已收录"）"""
    try:
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=days_back)
        
        request = {
            'startDate': start_date.isoformat(),
            'endDate': end_date.isoformat(),
            'dimensions': ['page'],
            'rowLimit': 25000  # GSC API 最大限制
        }
        
        print(f"🔍 查询时间范围: {start_date} → {end_date}")
        response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
        rows = response.get('rows', [])
        
        urls = [row['keys'][0] for row in rows]
        return urls
        
    except Exception as e:
        print(f"❌ API 查询失败: {e}")
        return []

def analyze_url_structure(urls):
    """分析 URL 路径结构"""
    path_stats = {
        '/p/': 0,          # 工具页
        '/blog/': 0,       # 博客页
        'homepage': 0,     # 首页
        'legal': 0,        # 法务页 (privacy, terms, contact)
        'other': 0
    }
    
    categorized = {
        '/p/': [],
        '/blog/': [],
        'homepage': [],
        'legal': [],
        'other': []
    }
    
    for url in urls:
        if '/p/' in url:
            path_stats['/p/'] += 1
            categorized['/p/'].append(url)
        elif '/blog/' in url:
            path_stats['/blog/'] += 1
            categorized['/blog/'].append(url)
        elif url.endswith('scenro.com/') or url.endswith('scenro.com'):
            path_stats['homepage'] += 1
            categorized['homepage'].append(url)
        elif any(x in url for x in ['privacy.html', 'terms.html', 'contact.html']):
            path_stats['legal'] += 1
            categorized['legal'].append(url)
        else:
            path_stats['other'] += 1
            categorized['other'].append(url)
    
    return path_stats, categorized

def main():
    print("=" * 70)
    print("🕵️ GSC 收录深度审计工具 - 1月27日数据追溯")
    print("=" * 70)
    
    creds = load_credentials()
    if not creds:
        return
    
    service = build("webmasters", "v3", credentials=creds)
    
    # 优先使用 sc-domain 属性
    site_url_domain = "sc-domain:scenro.com"
    site_url_https = "https://scenro.com/"
    
    target_site = None
    try:
        service.sites().get(siteUrl=site_url_domain).execute()
        target_site = site_url_domain
        print(f"✅ 已连接到 GSC 属性: {target_site}")
    except:
        try:
            service.sites().get(siteUrl=site_url_https).execute()
            target_site = site_url_https
            print(f"✅ 已连接到 GSC 属性: {target_site}")
        except Exception as e:
            print(f"❌ 无法连接到任何 GSC 属性: {e}")
            return
    
    # 获取最近 7 天的有展示数据的 URL
    indexed_urls = get_indexed_urls(service, target_site, days_back=7)
    
    if not indexed_urls:
        print("⚠️ 未找到任何有展示记录的 URL")
        return
    
    # 分析路径结构
    path_stats, categorized = analyze_url_structure(indexed_urls)
    
    # ===== 生成报告 =====
    print("\n" + "=" * 70)
    print("📊 12.6 协议 - 收录审计报告")
    print("=" * 70)
    
    print(f"\n【总览】")
    print(f"  • 收录总数（近7天有展示）: {len(indexed_urls)} 个页面")
    print(f"  • 查询时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n【路径分布】")
    for path_type, count in path_stats.items():
        percentage = (count / len(indexed_urls) * 100) if indexed_urls else 0
        print(f"  • {path_type:12} : {count:3d} 个 ({percentage:5.1f}%)")
    
    # 保存详细 URL 清单到文件
    report_file = "gsc_indexed_urls_report.json"
    report_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "total_count": len(indexed_urls),
        "path_stats": path_stats,
        "categorized_urls": categorized,
        "all_urls": indexed_urls
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n【详细清单已保存】")
    print(f"  📄 文件路径: {os.path.abspath(report_file)}")
    
    # 打印 /p/ 路径下的前 10 个 URL 作为样本
    print(f"\n【/p/ 工具页样本】(前10个)")
    for i, url in enumerate(categorized['/p/'][:10], 1):
        print(f"  {i:2d}. {url}")
    
    if len(categorized['/p/']) > 10:
        print(f"  ... 还有 {len(categorized['/p/']) - 10} 个（详见 JSON 报告）")
    
    # 打印其他类型页面
    if categorized['homepage']:
        print(f"\n【首页】")
        for url in categorized['homepage']:
            print(f"  • {url}")
    
    if categorized['/blog/']:
        print(f"\n【博客页】({len(categorized['/blog/'])} 个)")
        for url in categorized['/blog/'][:5]:
            print(f"  • {url}")
        if len(categorized['/blog/']) > 5:
            print(f"  ... 还有 {len(categorized['/blog/']) - 5} 个")
    
    if categorized['legal']:
        print(f"\n【法务页】")
        for url in categorized['legal']:
            print(f"  • {url}")
    
    if categorized['other']:
        print(f"\n【其他页面】({len(categorized['other'])} 个)")
        for url in categorized['other'][:5]:
            print(f"  • {url}")
    
    print("\n" + "=" * 70)
    print("✅ 审计完成")
    print("=" * 70)

if __name__ == "__main__":
    main()
