"""
Ads.txt 自检与压力测试工具
任务：验证 scenro.com/ads.txt 的可访问性，模拟 Google 爬虫访问
"""
import requests
import time
from datetime import datetime

def check_ads_txt(url="https://scenro.com/ads.txt", pressure_test=False):
    """检查 ads.txt 文件的可访问性"""
    
    print("=" * 70)
    print("🔍 Ads.txt 自检工具")
    print("=" * 70)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    }
    
    # 1. 基础可达性检查
    print(f"\n【第1步】基础可达性测试")
    print(f"  目标 URL: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"  状态码: {response.status_code}")
        print(f"  响应时间: {response.elapsed.total_seconds():.3f}s")
        print(f"  Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"  Content-Length: {response.headers.get('Content-Length', 'N/A')}")
        print(f"  Cache-Control: {response.headers.get('Cache-Control', 'N/A')}")
        print(f"  CF-Cache-Status: {response.headers.get('CF-Cache-Status', 'N/A')}")
        
        if response.status_code == 200:
            print(f"\n  ✅ 文件可访问")
            print(f"\n  【文件内容】")
            content = response.text
            for line in content.split('\n'):
                if line.strip():
                    print(f"    {line.strip()}")
            
            # 验证内容格式
            if 'google.com' in content and 'pub-' in content:
                print(f"\n  ✅ 内容格式正确（包含 Google AdSense 发布商 ID）")
            else:
                print(f"\n  ⚠️ 内容格式异常（未检测到标准 AdSense 声明）")
        else:
            print(f"\n  ❌ HTTP {response.status_code} - 文件不可访问")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n  ❌ 请求失败: {e}")
        return False
    
    # 2. 压力测试（可选）
    if pressure_test:
        print(f"\n【第2步】访问压力模拟（10次连续请求）")
        success_count = 0
        total_time = 0
        
        for i in range(1, 11):
            try:
                start = time.time()
                r = requests.get(url, headers=headers, timeout=5)
                elapsed = time.time() - start
                total_time += elapsed
                
                if r.status_code == 200:
                    success_count += 1
                    status_symbol = "✅"
                else:
                    status_symbol = "❌"
                
                print(f"  请求 {i:2d}/10: {status_symbol} HTTP {r.status_code} ({elapsed:.3f}s)")
                time.sleep(0.5)  # 500ms 间隔
                
            except Exception as e:
                print(f"  请求 {i:2d}/10: ❌ 失败 - {e}")
        
        avg_time = total_time / 10
        print(f"\n  【压力测试结果】")
        print(f"    成功率: {success_count}/10 ({success_count*10}%)")
        print(f"    平均响应时间: {avg_time:.3f}s")
    
    # 3. Cloudflare 缓存状态分析
    print(f"\n【第3步】Cloudflare 缓存分析")
    try:
        # 发送多次请求检查缓存行为
        cache_statuses = []
        for _ in range(3):
            r = requests.get(url, headers=headers, timeout=5)
            cache_status = r.headers.get('CF-Cache-Status', 'UNKNOWN')
            cache_statuses.append(cache_status)
            time.sleep(0.3)
        
        print(f"  连续3次请求的缓存状态: {' → '.join(cache_statuses)}")
        
        if 'HIT' in cache_statuses:
            print(f"  ✅ Cloudflare 缓存已激活")
        elif 'MISS' in cache_statuses or 'EXPIRED' in cache_statuses:
            print(f"  ⚠️ 缓存未命中或已过期（可能影响爬虫抓取）")
        elif 'BYPASS' in cache_statuses or 'DYNAMIC' in cache_statuses:
            print(f"  ⚠️ 缓存被绕过（文件未被缓存，每次都回源）")
        else:
            print(f"  ℹ️ 缓存状态未知或不适用")
            
    except Exception as e:
        print(f"  ❌ 缓存测试失败: {e}")
    
    # 4. 建议
    print(f"\n【第4步】优化建议")
    suggestions = []
    
    if response.status_code != 200:
        suggestions.append("❌ 修复 HTTP 响应码（必须为 200 OK）")
    
    content_type = response.headers.get('Content-Type', '')
    if 'text/plain' not in content_type:
        suggestions.append("⚠️ 建议设置 Content-Type: text/plain")
    
    cf_cache = response.headers.get('CF-Cache-Status', '')
    if cf_cache in ['BYPASS', 'DYNAMIC']:
        suggestions.append("⚠️ 建议在 Cloudflare Page Rules 中为 /ads.txt 启用缓存")
    
    cache_control = response.headers.get('Cache-Control', '')
    if 'no-cache' in cache_control or 'private' in cache_control:
        suggestions.append("⚠️ 建议设置 Cache-Control: public, max-age=3600")
    
    if not suggestions:
        print(f"  ✅ 无需优化，配置符合最佳实践")
    else:
        for suggestion in suggestions:
            print(f"  {suggestion}")
    
    print("\n" + "=" * 70)
    print(f"✅ Ads.txt 自检完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    # 默认执行基础检查 + 压力测试
    check_ads_txt(pressure_test=True)
