"""
Scenro 创始人数据看板 - GSC 核心指标分析
任务：抓取最近 7 天的真实流量数据，识别最受欢迎的细分行业
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

def load_credentials():
    """加载 GSC API 凭证"""
    # 从 .env 读取凭证文件路径
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    
    creds_path = None
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('GOOGLE_APPLICATION_CREDENTIALS='):
                    creds_path = line.split('=', 1)[1].strip()
                    break
    
    if not creds_path:
        # 回退到本地查找
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

def get_performance_data(service, site_url, days=7):
    """获取最近 N 天的性能数据（页面+关键词维度）"""
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=days)
    
    print(f"📅 查询时间范围: {start_date} → {end_date}")
    
    # 查询 1: 页面维度
    request_pages = {
        'startDate': start_date.isoformat(),
        'endDate': end_date.isoformat(),
        'dimensions': ['page'],
        'rowLimit': 25000
    }
    
    # 查询 2: 页面+关键词维度
    request_queries = {
        'startDate': start_date.isoformat(),
        'endDate': end_date.isoformat(),
        'dimensions': ['page', 'query'],
        'rowLimit': 25000
    }
    
    try:
        print(f"\n🔍 正在查询页面数据...")
        response_pages = service.searchanalytics().query(
            siteUrl=site_url, 
            body=request_pages
        ).execute()
        
        print(f"🔍 正在查询关键词数据...")
        response_queries = service.searchanalytics().query(
            siteUrl=site_url, 
            body=request_queries
        ).execute()
        
        return response_pages, response_queries
        
    except Exception as e:
        print(f"❌ 数据查询失败: {e}")
        return None, None

def extract_industry_from_url(url):
    """从 URL 中提取行业关键词"""
    # 示例: https://scenro.com/p/texas-senior-medical-specialist-expert
    # 提取: medical specialist
    
    patterns = [
        r'/p/[\w-]+-[\w-]+-(.+)-expert',  # 匹配 {state}-{level}-{industry}-expert
        r'/p/[\w-]+-(.+)-expert',         # 匹配 {state}-{industry}-expert
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            industry = match.group(1).replace('-', ' ')
            # 清理常见的级别词汇
            industry = re.sub(r'\b(senior|junior|certified|professional|licensed|lead|assistant|associate|expert|consulting)\b', '', industry)
            industry = ' '.join(industry.split())  # 清理多余空格
            return industry.strip()
    
    return 'unknown'

def analyze_data(response_pages, response_queries):
    """分析数据，提取核心指标"""
    if not response_pages or 'rows' not in response_pages:
        return None
    
    pages_data = response_pages.get('rows', [])
    queries_data = response_queries.get('rows', []) if response_queries else []
    
    # 按页面汇总
    page_stats = {}
    for row in pages_data:
        url = row['keys'][0]
        page_stats[url] = {
            'impressions': row.get('impressions', 0),
            'clicks': row.get('clicks', 0),
            'ctr': row.get('ctr', 0) * 100,  # 转为百分比
            'position': row.get('position', 999),
            'queries': []
        }
    
    # 添加关键词数据
    for row in queries_data:
        url = row['keys'][0]
        query = row['keys'][1]
        
        if url in page_stats:
            page_stats[url]['queries'].append({
                'query': query,
                'impressions': row.get('impressions', 0),
                'clicks': row.get('clicks', 0),
                'ctr': row.get('ctr', 0) * 100,
                'position': row.get('position', 999)
            })
    
    # 按展示量排序
    sorted_pages = sorted(page_stats.items(), 
                         key=lambda x: x[1]['impressions'], 
                         reverse=True)
    
    return sorted_pages

def identify_top_industries(page_data):
    """识别最受欢迎的细分行业"""
    industry_stats = defaultdict(lambda: {
        'impressions': 0,
        'clicks': 0,
        'pages': []
    })
    
    for url, stats in page_data:
        industry = extract_industry_from_url(url)
        if industry and industry != 'unknown':
            industry_stats[industry]['impressions'] += stats['impressions']
            industry_stats[industry]['clicks'] += stats['clicks']
            industry_stats[industry]['pages'].append(url)
    
    # 按展示量排序
    sorted_industries = sorted(industry_stats.items(), 
                              key=lambda x: x[1]['impressions'], 
                              reverse=True)
    
    return sorted_industries

def main():
    print("=" * 80)
    print("🎯 SCENRO 创始人数据看板")
    print("   近 7 天核心流量分析 & 细分行业识别")
    print("=" * 80)
    
    # 加载凭证
    creds = load_credentials()
    if not creds:
        return
    
    service = build("webmasters", "v3", credentials=creds)
    
    # 连接 GSC
    site_url = "https://scenro.com/"
    
    try:
        service.sites().get(siteUrl=site_url).execute()
        print(f"✅ 已连接到 GSC 属性: {site_url}\n")
    except Exception as e:
        print(f"❌ 无法连接到 GSC: {e}")
        return
    
    # 获取数据
    response_pages, response_queries = get_performance_data(service, site_url, days=7)
    
    if not response_pages:
        print("⚠️ 未获取到数据")
        return
    
    # 分析数据
    page_data = analyze_data(response_pages, response_queries)
    
    if not page_data:
        print("⚠️ 无有效数据")
        return
    
    # 生成报告
    print("\n" + "=" * 80)
    print("📊 第一部分：核心页面表现（Top 8）")
    print("=" * 80)
    
    for i, (url, stats) in enumerate(page_data[:8], 1):
        print(f"\n【页面 {i}】")
        print(f"  URL: {url}")
        print(f"  展示量: {stats['impressions']:,}")
        print(f"  点击数: {stats['clicks']}")
        print(f"  CTR: {stats['ctr']:.2f}%")
        print(f"  平均排名: {stats['position']:.1f}")
        
        # 显示 Top 3 关键词
        if stats['queries']:
            top_queries = sorted(stats['queries'], 
                               key=lambda x: x['impressions'], 
                               reverse=True)[:3]
            print(f"  Top 关键词:")
            for j, q in enumerate(top_queries, 1):
                print(f"    {j}. \"{q['query']}\" - {q['impressions']} 展示, {q['clicks']} 点击 (CTR: {q['ctr']:.1f}%)")
    
    # 识别最受欢迎的行业
    industries = identify_top_industries(page_data)
    
    print("\n" + "=" * 80)
    print("🏆 第二部分：最受欢迎的细分行业 TOP 3")
    print("=" * 80)
    
    for i, (industry, stats) in enumerate(industries[:3], 1):
        ctr = (stats['clicks'] / stats['impressions'] * 100) if stats['impressions'] > 0 else 0
        print(f"\n【第 {i} 名】{industry.upper()}")
        print(f"  总展示量: {stats['impressions']:,}")
        print(f"  总点击数: {stats['clicks']}")
        print(f"  整体 CTR: {ctr:.2f}%")
        print(f"  覆盖页面数: {len(stats['pages'])}")
        print(f"  代表页面: {stats['pages'][0] if stats['pages'] else 'N/A'}")
    
    # 总览统计
    total_impressions = sum(stats['impressions'] for _, stats in page_data)
    total_clicks = sum(stats['clicks'] for _, stats in page_data)
    overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    
    print("\n" + "=" * 80)
    print("📈 第三部分：整体表现概览")
    print("=" * 80)
    print(f"  活跃页面数: {len(page_data)}")
    print(f"  总展示量: {total_impressions:,}")
    print(f"  总点击数: {total_clicks}")
    print(f"  整体 CTR: {overall_ctr:.2f}%")
    print(f"  平均排名: {sum(s['position'] for _, s in page_data) / len(page_data):.1f}")
    
    # 保存详细数据
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_pages': len(page_data),
            'total_impressions': total_impressions,
            'total_clicks': total_clicks,
            'overall_ctr': overall_ctr
        },
        'top_pages': [
            {
                'url': url,
                'stats': stats
            }
            for url, stats in page_data[:8]
        ],
        'top_industries': [
            {
                'industry': industry,
                'stats': stats
            }
            for industry, stats in industries[:3]
        ]
    }
    
    report_file = "scenro_founder_dashboard.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 详细数据已保存: {os.path.abspath(report_file)}")
    print("=" * 80)

if __name__ == "__main__":
    main()
