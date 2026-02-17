"""
GSC 实时数据抓取脚本 - 获取171个已收录页面的真实数据
任务：连接Google Search Console API，抓取已收录页面清单和关键词数据
"""
import os
import sys
import json
from datetime import datetime, timedelta, timezone
from google.oauth2 import service_account
from googleapiclient.discovery import build
from collections import defaultdict
import re

# 设置输出编码为UTF-8，解决Windows控制台编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def configure_proxy():
    """配置代理设置，使用系统代理或自定义代理"""
    proxy_config = {
        'http_proxy': os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy'),
        'https_proxy': os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy'),
        'no_proxy': os.environ.get('NO_PROXY') or os.environ.get('no_proxy')
    }
    
    print("🔧 代理配置检查:")
    for key, value in proxy_config.items():
        if value:
            print(f"   {key}: {value}")
        else:
            print(f"   {key}: 未设置")
    
    # 如果有代理配置，设置给httplib2
    if proxy_config['http_proxy'] or proxy_config['https_proxy']:
        import httplib2
        proxy_info = httplib2.ProxyInfo(
            httplib2.socks.PROXY_TYPE_HTTP,
            '127.0.0.1',  # 假设本地代理，实际应从环境变量解析
            10809,        # 默认端口
            proxy_rdns=True
        )
        # 注意：实际实现需要更复杂的代理解析
        print("⚠️  代理检测到，但需要手动配置googleapiclient的代理")
    
    return proxy_config

def load_credentials():
    """加载 GSC API 凭证"""
    # 直接使用找到的密钥文件
    creds_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                               'gen-lang-client-0846513202-3d6c54387cae.json')
    
    if not os.path.exists(creds_path):
        print(f"❌ 凭证文件未找到: {creds_path}")
        return None
    
    print(f"✅ 凭证文件: {creds_path}")
    
    try:
        return service_account.Credentials.from_service_account_file(
            creds_path, 
            scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
        )
    except Exception as e:
        print(f"❌ 凭证加载失败: {e}")
        return None

def get_indexed_pages(service, site_url, days=7):
    """获取最近 N 天有搜索展示的已收录页面"""
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=days)
    
    print(f"\n📊 抓取时间范围: {start_date} 至 {end_date}")
    print(f"🌐 目标站点: {site_url}")
    
    try:
        # 获取页面维度的数据
        request = {
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
            'dimensions': ['page'],
            'rowLimit': 10000  # 获取最多10000行数据
        }
        
        response = service.searchanalytics().query(
            siteUrl=site_url,
            body=request
        ).execute()
        
        if 'rows' not in response:
            print("⚠️  未找到有搜索展示的页面")
            return []
        
        indexed_pages = []
        for row in response['rows']:
            page_data = {
                'url': row['keys'][0],
                'impressions': row.get('impressions', 0),
                'clicks': row.get('clicks', 0),
                'ctr': row.get('ctr', 0),
                'position': row.get('position', 0)
            }
            indexed_pages.append(page_data)
        
        print(f"✅ 找到 {len(indexed_pages)} 个有搜索展示的页面")
        return indexed_pages
        
    except Exception as e:
        print(f"❌ 获取页面数据失败: {e}")
        return []

def get_keywords(service, site_url, days=7):
    """获取最近 N 天的关键词数据"""
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=days)
    
    try:
        request = {
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
            'dimensions': ['query'],
            'rowLimit': 1000
        }
        
        response = service.searchanalytics().query(
            siteUrl=site_url,
            body=request
        ).execute()
        
        if 'rows' not in response:
            return []
        
        keywords = []
        for row in response['rows']:
            keyword_data = {
                'query': row['keys'][0],
                'impressions': row.get('impressions', 0),
                'clicks': row.get('clicks', 0),
                'ctr': row.get('ctr', 0),
                'position': row.get('position', 0)
            }
            keywords.append(keyword_data)
        
        print(f"✅ 找到 {len(keywords)} 个关键词")
        return keywords
        
    except Exception as e:
        print(f"❌ 获取关键词数据失败: {e}")
        return []

def extract_industry_from_url(url):
    """从URL中提取行业信息"""
    url_lower = url.lower()
    
    # 医疗行业
    if any(x in url_lower for x in ['doctor', 'nurse', 'medical', 'physician', 'surgeon', 'clinic', 'therapist', 'counselor', 'health']):
        return 'Medical'
    
    # 法律行业
    if any(x in url_lower for x in ['lawyer', 'attorney', 'paralegal', 'legal', 'judge', 'defense']):
        return 'Lawyer'
    
    # 教育行业
    if any(x in url_lower for x in ['tutor', 'teacher', 'education', 'instructor', 'professor', 'school']):
        return 'Tutor'
    
    # 金融行业
    if any(x in url_lower for x in ['accountant', 'cpa', 'tax', 'finance', 'audit', 'bookkeeper']):
        return 'Finance'
    
    # 房地产行业
    if any(x in url_lower for x in ['real estate', 'realtor', 'broker', 'agent']):
        return 'RealEstate'
    
    return 'Other'

def analyze_industry_distribution(pages):
    """分析行业分布"""
    industry_stats = defaultdict(lambda: {'count': 0, 'urls': []})
    
    for page in pages:
        industry = extract_industry_from_url(page['url'])
        industry_stats[industry]['count'] += 1
        industry_stats[industry]['urls'].append(page['url'])
    
    return industry_stats

def main():
    print("=" * 80)
    print("🚀 GSC 实时数据抓取工具")
    print("=" * 80)
    
    # 加载凭证
    creds = load_credentials()
    if not creds:
        print("❌ 无法继续，凭证加载失败")
        return
    
    # 连接 GSC
    site_url = "https://scenro.com/"
    try:
        service = build('searchconsole', 'v1', credentials=creds)
        print(f"✅ 已连接到 GSC 属性: {site_url}\n")
    except Exception as e:
        print(f"❌ 无法连接到 GSC: {e}")
        return
    
    # 获取已收录页面
    indexed_pages = get_indexed_pages(service, site_url, days=30)  # 扩大到30天以获取更多数据
    
    if not indexed_pages:
        print("⚠️  未找到已收录页面，尝试扩大时间范围...")
        indexed_pages = get_indexed_pages(service, site_url, days=90)
    
    # 获取关键词数据
    keywords = get_keywords(service, site_url, days=30)
    
    # 分析行业分布
    industry_stats = analyze_industry_distribution(indexed_pages)
    
    # 生成报告
    report = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'site_url': site_url,
        'total_indexed_pages': len(indexed_pages),
        'total_keywords': len(keywords),
        'industry_distribution': {},
        'indexed_pages': indexed_pages,
        'keywords': keywords
    }
    
    for industry, data in industry_stats.items():
        report['industry_distribution'][industry] = {
            'count': data['count'],
            'percentage': round((data['count'] / len(indexed_pages)) * 100, 2) if indexed_pages else 0,
            'sample_urls': data['urls'][:5]  # 只保留前5个URL作为示例
        }
    
    # 保存报告
    output_file = 'gsc_indexed_urls_report.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 报告已保存到: {output_file}")
    
    # 打印行业分布
    print("\n" + "=" * 80)
    print("📊 行业分布报告")
    print("=" * 80)
    for industry, data in sorted(report['industry_distribution'].items(), key=lambda x: x[1]['count'], reverse=True):
        print(f"\n{industry}:")
        print(f"  数量: {data['count']}")
        print(f"  占比: {data['percentage']}%")
        print(f"  示例URL:")
        for url in data['sample_urls']:
            print(f"    - {url}")
    
    print("\n" + "=" * 80)
    print(f"📈 总计: {report['total_indexed_pages']} 个已收录页面")
    print(f"🔑 总计: {report['total_keywords']} 个关键词")
    print("=" * 80)

if __name__ == "__main__":
    main()
