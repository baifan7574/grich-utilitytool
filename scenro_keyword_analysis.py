"""
Scenro 创始人数据看板 V2 - 关键词深度挖掘
专注于搜索查询词分析
"""
import os
import json
from datetime import datetime, timedelta, timezone
from google.oauth2 import service_account
from googleapiclient.discovery import build
from collections import defaultdict

def load_credentials():
    """加载 GSC API 凭证"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    
    creds_path = None
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('GOOGLE_APPLICATION_CREDENTIALS='):
                    creds_path = line.split('=', 1)[1].strip()
                    break
    
    if not creds_path:
        creds_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                   'gen-lang-client-0846513202-3d6c54387cae.json')
    
    if not os.path.exists(creds_path):
        print(f"❌ 凭证文件未找到: {creds_path}")
        return None
    
    try:
        return service_account.Credentials.from_service_account_file(
            creds_path, 
            scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
        )
    except Exception as e:
        print(f"❌ 凭证加载失败: {e}")
        return None

def main():
    print("=" * 80)
    print("🔍 SCENRO 创始人数据看板 V2")
    print("   关键词 & 细分行业深度分析")
    print("=" * 80)
    
    creds = load_credentials()
    if not creds:
        return
    
    service = build("webmasters", "v3", credentials=creds)
    site_url = "https://scenro.com/"
    
    try:
        service.sites().get(siteUrl=site_url).execute()
        print(f"✅ 已连接到 GSC 属性: {site_url}\n")
    except Exception as e:
        print(f"❌ 无法连接到 GSC: {e}")
        return
    
    # 查询最近 7 天的数据
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=7)
    
    print(f"📅 查询时间范围: {start_date} → {end_date}\n")
    
    # 查询 1: 仅关键词维度
    print("🔍 查询 1: 所有搜索关键词...")
    request_queries = {
        'startDate': start_date.isoformat(),
        'endDate': end_date.isoformat(),
        'dimensions': ['query'],
        'rowLimit': 1000
    }
    
    try:
        response_queries = service.searchanalytics().query(
            siteUrl=site_url, 
            body=request_queries
        ).execute()
        
        queries = response_queries.get('rows', [])
        print(f"   ✅ 找到 {len(queries)} 个关键词\n")
        
        if queries:
            print("=" * 80)
            print("🎯 关键词表现 TOP 10（按展示量排序）")
            print("=" * 80)
            
            # 按展示量排序
            sorted_queries = sorted(queries, 
                                   key=lambda x: x.get('impressions', 0), 
                                   reverse=True)
            
            for i, row in enumerate(sorted_queries[:10], 1):
                query = row['keys'][0]
                impressions = row.get('impressions', 0)
                clicks = row.get('clicks', 0)
                ctr = row.get('ctr', 0) * 100
                position = row.get('position', 999)
                
                print(f"\n【{i}】关键词: \"{query}\"")
                print(f"    展示量: {impressions}")
                print(f"    点击数: {clicks}")
                print(f"    CTR: {ctr:.2f}%")
                print(f"    平均排名: {position:.1f}")
        else:
            print("⚠️ 未找到关键词数据")
    
    except Exception as e:
        print(f"❌ 关键词查询失败: {e}")
    
    # 查询 2: 页面维度（获取那 8 个页面的详情）
    print("\n" + "=" * 80)
    print("📄 查询 2: 页面表现详情...")
    print("=" * 80)
    
    request_pages = {
        'startDate': start_date.isoformat(),
        'endDate': end_date.isoformat(),
        'dimensions': ['page'],
        'rowLimit': 100
    }
    
    try:
        response_pages = service.searchanalytics().query(
            siteUrl=site_url, 
            body=request_pages
        ).execute()
        
        pages = response_pages.get('rows', [])
        print(f"✅ 找到 {len(pages)} 个活跃页面\n")
        
        if pages:
            # 提取行业关键词
            industry_stats = defaultdict(lambda: {
                'impressions': 0,
                'clicks': 0,
                'pages': []
            })
            
            for row in pages:
                url = row['keys'][0]
                impressions = row.get('impressions', 0)
                clicks = row.get('clicks', 0)
                
                # 简单提取行业（从 URL 最后一段）
                if '/p/' in url:
                    parts = url.split('/')[-1].replace('.html', '').replace('-expert', '').split('-')
                    # 跳过州名和级别词
                    skip_words = {'senior', 'junior', 'certified', 'professional', 
                                 'licensed', 'lead', 'assistant', 'associate', 
                                 'expert', 'consulting'}
                    
                    # 取最后2-3个词作为行业
                    industry_words = [w for w in parts if w not in skip_words and len(w) > 3]
                    
                    if industry_words:
                        industry = ' '.join(industry_words[-2:]) if len(industry_words) >= 2 else industry_words[-1]
                        industry_stats[industry]['impressions'] += impressions
                        industry_stats[industry]['clicks'] += clicks
                        industry_stats[industry]['pages'].append(url)
            
            # 按展示量排序
            sorted_industries = sorted(industry_stats.items(), 
                                      key=lambda x: x[1]['impressions'], 
                                      reverse=True)
            
            print("🏆 最受欢迎的细分行业 TOP 3\n")
            
            for i, (industry, stats) in enumerate(sorted_industries[:3], 1):
                ctr = (stats['clicks'] / stats['impressions'] * 100) if stats['impressions'] > 0 else 0
                print(f"【第 {i} 名】{industry.upper()}")
                print(f"  总展示量: {stats['impressions']}")
                print(f"  总点击数: {stats['clicks']}")
                print(f"  整体 CTR: {ctr:.2f}%")
                print(f"  覆盖页面数: {len(stats['pages'])}")
                if stats['pages']:
                    print(f"  代表页面: {stats['pages'][0]}")
                print()
            
    except Exception as e:
        print(f"❌ 页面查询失败: {e}")
    
    # 查询 3: 查询词+页面组合（获取具体哪个词对应哪个页面）
    print("=" * 80)
    print("🔗 查询 3: 关键词-页面对应关系...")
    print("=" * 80)
    
    request_combined = {
        'startDate': start_date.isoformat(),
        'endDate': end_date.isoformat(),
        'dimensions': ['query', 'page'],
        'rowLimit': 100
    }
    
    try:
        response_combined = service.searchanalytics().query(
            siteUrl=site_url, 
            body=request_combined
        ).execute()
        
        combined = response_combined.get('rows', [])
        print(f"✅ 找到 {len(combined)} 个关键词-页面组合\n")
        
        if combined:
            # 按展示量排序
            sorted_combined = sorted(combined, 
                                    key=lambda x: x.get('impressions', 0), 
                                    reverse=True)
            
            print("TOP 8 关键词-页面组合:\n")
            
            for i, row in enumerate(sorted_combined[:8], 1):
                query = row['keys'][0]
                page = row['keys'][1]
                impressions = row.get('impressions', 0)
                clicks = row.get('clicks', 0)
                ctr = row.get('ctr', 0) * 100
                position = row.get('position', 999)
                
                # 提取页面简称
                page_name = page.split('/')[-1].replace('.html', '')
                
                print(f"【{i}】")
                print(f"  关键词: \"{query}\"")
                print(f"  页面: {page_name}")
                print(f"  展示: {impressions} | 点击: {clicks} | CTR: {ctr:.1f}% | 排名: {position:.1f}")
                print()
                
    except Exception as e:
        print(f"❌ 组合查询失败: {e}")
    
    print("=" * 80)
    print("✅ 数据分析完成")
    print("=" * 80)

if __name__ == "__main__":
    main()
