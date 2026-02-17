"""
Sitemap 主动更新与 Ping 提交器
任务：
1. 更新 sitemap.xml 的 lastmod 时间戳
2. Ping Google 让其重新爬取 Sitemap（被动收录）
"""
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import requests
from urllib.parse import quote

def update_sitemap_lastmod(sitemap_path):
    """更新 sitemap.xml 中所有 URL 的 lastmod 时间"""
    print(f"🔄 更新 Sitemap 的 lastmod 时间戳...")
    print(f"   文件路径: {sitemap_path}")
    
    if not os.path.exists(sitemap_path):
        print(f"   ❌ 文件不存在")
        return False
    
    try:
        # 解析 XML
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        
        # 获取当前 UTC 时间（ISO 8601 格式）
        current_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')
        
        # XML 命名空间
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        # 统计更新数量
        updated_count = 0
        
        # 检查是否为 sitemap index
        if 'sitemapindex' in root.tag:
            print(f"   📍 检测到 Sitemap Index")
            for sitemap in root.findall('ns:sitemap', namespace):
                lastmod = sitemap.find('ns:lastmod', namespace)
                if lastmod is not None:
                    lastmod.text = current_time
                    updated_count += 1
                else:
                    # 创建 lastmod 元素
                    lastmod_elem = ET.SubElement(sitemap, 'lastmod')
                    lastmod_elem.text = current_time
                    updated_count += 1
        else:
            # 常规 sitemap
            print(f"   📍 检测到常规 Sitemap")
            for url in root.findall('ns:url', namespace):
                lastmod = url.find('ns:lastmod', namespace)
                if lastmod is not None:
                    lastmod.text = current_time
                    updated_count += 1
                else:
                    # 创建 lastmod 元素
                    lastmod_elem = ET.SubElement(url, 'lastmod')
                    lastmod_elem.text = current_time
                    updated_count += 1
        
        # 保存更新后的 XML
        tree.write(sitemap_path, encoding='utf-8', xml_declaration=True)
        
        print(f"   ✅ 成功更新 {updated_count} 个 URL 的 lastmod 时间")
        print(f"   🕐 新时间戳: {current_time}")
        return True
        
    except Exception as e:
        print(f"   ❌ 更新失败: {e}")
        return False

def ping_google_sitemap(sitemap_url):
    """向 Google 提交 Sitemap Ping"""
    print(f"\n📡 Ping Google 搜索引擎...")
    
    # Google Ping URL
    google_ping_url = f"https://www.google.com/ping?sitemap={quote(sitemap_url)}"
    
    print(f"   目标 Sitemap: {sitemap_url}")
    print(f"   Ping URL: {google_ping_url}")
    
    try:
        response = requests.get(google_ping_url, timeout=10)
        
        if response.status_code == 200:
            print(f"   ✅ Google Ping 成功 (HTTP 200)")
            print(f"   ℹ️ Google 将在接下来几小时内重新爬取 Sitemap")
            return True
        else:
            print(f"   ⚠️ Ping 响应异常: HTTP {response.status_code}")
            print(f"   {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Ping 失败: {e}")
        return False

def ping_bing_sitemap(sitemap_url):
    """向 Bing 提交 Sitemap Ping"""
    print(f"\n📡 Ping Bing 搜索引擎...")
    
    # Bing Ping URL
    bing_ping_url = f"https://www.bing.com/ping?sitemap={quote(sitemap_url)}"
    
    print(f"   目标 Sitemap: {sitemap_url}")
    print(f"   Ping URL: {bing_ping_url}")
    
    try:
        response = requests.get(bing_ping_url, timeout=10)
        
        if response.status_code == 200:
            print(f"   ✅ Bing Ping 成功 (HTTP 200)")
            return True
        else:
            print(f"   ⚠️ Ping 响应异常: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Ping 失败: {e}")
        return False

def main():
    print("=" * 70)
    print("🔄 Sitemap 主动更新与 Ping 提交器 - 被动收录策略")
    print("=" * 70)
    
    # 配置
    LOCAL_SITEMAP = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))),
        'dist',
        'sitemap.xml'
    )
    LIVE_SITEMAP_URL = "https://scenro.com/sitemap.xml"
    
    # 检查本地文件是否存在
    if not os.path.exists(LOCAL_SITEMAP):
        print(f"⚠️ 警告: 本地 sitemap.xml 不存在，跳过本地更新")
        print(f"   路径: {LOCAL_SITEMAP}")
        print(f"\n   ℹ️ 仅执行线上 Sitemap Ping（假设已部署到生产环境）")
    else:
        # 1. 更新本地 Sitemap 的 lastmod
        update_success = update_sitemap_lastmod(LOCAL_SITEMAP)
        
        if update_success:
            print(f"\n   ⚠️ 注意：本地更新完成后，需要重新部署到 Cloudflare Pages")
            print(f"   命令：git add dist/sitemap.xml && git commit -m 'chore: update sitemap lastmod' && git push")
    
    # 2. Ping Google 和 Bing
    google_success = ping_google_sitemap(LIVE_SITEMAP_URL)
    bing_success = ping_bing_sitemap(LIVE_SITEMAP_URL)
    
    # 总结
    print("\n" + "=" * 70)
    print("📊 执行总结")
    print("=" * 70)
    
    if os.path.exists(LOCAL_SITEMAP):
        print(f"  • 本地 Sitemap 更新: {'✅ 成功' if update_success else '❌ 失败'}")
    else:
        print(f"  • 本地 Sitemap 更新: ⚠️ 跳过（文件不存在）")
    
    print(f"  • Google Ping: {'✅ 成功' if google_success else '❌ 失败'}")
    print(f"  • Bing Ping: {'✅ 成功' if bing_success else '❌ 失败'}")
    
    print("\n📝 后续步骤:")
    print("  1. 若本地 sitemap 已更新，请部署到生产环境")
    print("  2. 等待 24-48 小时观察 GSC 的爬取日志")
    print("  3. 监控 '已发现但未索引' 页面的状态变化")
    print("  4. 考虑将此脚本加入每日自动任务（GitHub Actions）")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
