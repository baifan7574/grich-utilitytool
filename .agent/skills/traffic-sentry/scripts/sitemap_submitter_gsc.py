"""
Sitemap 提交器（GSC API 方式）
任务：通过 Google Search Console API 提交 Sitemap（替代已废弃的 Ping 接口）
"""
import os
import json
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
                info, scopes=["https://www.googleapis.com/auth/webmasters"]
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
            creds_path, scopes=["https://www.googleapis.com/auth/webmasters"]
        )
    except Exception as e:
        print(f"❌ 凭据加载失败: {e}")
        sys.exit(1)

def submit_sitemap_via_gsc(service, site_url, sitemap_url):
    """通过 GSC API 提交 Sitemap"""
    print(f"\n📡 通过 GSC API 提交 Sitemap...")
    print(f"   站点属性: {site_url}")
    print(f"   Sitemap URL: {sitemap_url}")
    
    try:
        # 提交 Sitemap
        service.sitemaps().submit(siteUrl=site_url, feedpath=sitemap_url).execute()
        print(f"   ✅ Sitemap 提交成功")
        return True
        
    except Exception as e:
        error_msg = str(e)
        if '404' in error_msg:
            print(f"   ⚠️ Sitemap 可能已存在（404 错误通常表示已提交）")
            return True
        else:
            print(f"   ❌ 提交失败: {e}")
            return False

def list_submitted_sitemaps(service, site_url):
    """列出已提交的 Sitemaps"""
    print(f"\n📋 查询已提交的 Sitemaps...")
    
    try:
        sitemaps = service.sitemaps().list(siteUrl=site_url).execute()
        
        if 'sitemap' in sitemaps:
            print(f"   ✅ 找到 {len(sitemaps['sitemap'])} 个 Sitemap:")
            for sm in sitemaps['sitemap']:
                path = sm.get('path', 'Unknown')
                last_downloaded = sm.get('lastDownloaded', 'Never')
                last_submitted = sm.get('lastSubmitted', 'Unknown')
                print(f"\n     • {path}")
                print(f"       最后提交: {last_submitted}")
                print(f"       最后下载: {last_downloaded}")
        else:
            print(f"   ⚠️ 未找到已提交的 Sitemap")
            
    except Exception as e:
        print(f"   ❌ 查询失败: {e}")

def main():
    print("=" * 70)
    print("📡 Sitemap 提交器（GSC API）- 被动收录加速")
    print("=" * 70)
    
    creds = load_credentials()
    if not creds:
        return
    
    service = build("webmasters", "v3", credentials=creds)
    
    # 配置
    site_url_https = "https://scenro.com/"
    site_url_domain = "sc-domain:scenro.com"
    sitemap_url = "https://scenro.com/sitemap.xml"
    
    # 优先使用 HTTPS 属性
    target_site = None
    try:
        service.sites().get(siteUrl=site_url_https).execute()
        target_site = site_url_https
        print(f"✅ 已连接到 GSC 属性: {target_site}")
    except:
        try:
            service.sites().get(siteUrl=site_url_domain).execute()
            target_site = site_url_domain
            print(f"✅ 已连接到 GSC 属性: {target_site}")
        except Exception as e:
            print(f"❌ 无法连接到任何 GSC 属性: {e}")
            return
    
    # 1. 列出现有 Sitemaps
    list_submitted_sitemaps(service, target_site)
    
    # 2. 提交/更新 Sitemap
    submit_sitemap_via_gsc(service, target_site, sitemap_url)
    
    print("\n" + "=" * 70)
    print("✅ Sitemap 提交完成")
    print("=" * 70)
    
    print("\n📝 关键说明:")
    print("  • Google 已于 2023 年 6 月废弃 Ping 接口")
    print("  • 现在推荐通过 GSC API 或后台手动提交 Sitemap")
    print("  • Sitemap 提交后，Google 会定期自动爬取（24-72 小时）")
    print("  • 更新 lastmod 时间戳可加速重新爬取")
    
    print("\n📊 预期效果:")
    print("  • 已提交 URL 会进入'已发现但未索引'队列")
    print("  • 配合每日 Indexing API 推送，双管齐下加速收录")

if __name__ == "__main__":
    main()
