"""
Cloudflare Page Rule 自动创建器 - Ads.txt 缓存攻坚
任务：通过 Cloudflare API 为 scenro.com/ads.txt 创建 Page Rule（Cache Everything）
"""
import requests
import json
import os
import sys

def load_env():
    """加载 .env 文件中的环境变量"""
    env_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))),
        '.env'
    )
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    parts = line.strip().split('=', 1)
                    if len(parts) == 2:
                        os.environ[parts[0]] = parts[1]

def get_cloudflare_headers():
    """获取 Cloudflare API 认证头"""
    load_env()
    
    cf_api_token = os.environ.get("CLOUDFLARE_API_TOKEN")
    cf_email = os.environ.get("CLOUDFLARE_EMAIL")
    cf_api_key = os.environ.get("CLOUDFLARE_API_KEY")
    
    if cf_api_token:
        print("✅ 使用 Cloudflare API Token 认证")
        return {
            "Authorization": f"Bearer {cf_api_token}",
            "Content-Type": "application/json"
        }
    elif cf_email and cf_api_key:
        print(f"✅ 使用 Cloudflare Global API Key 认证 ({cf_email})")
        return {
            "X-Auth-Email": cf_email,
            "X-Auth-Key": cf_api_key,
            "Content-Type": "application/json"
        }
    else:
        print("❌ 未找到有效的 Cloudflare 凭据")
        sys.exit(1)

def get_zone_id():
    """从环境变量获取 Zone ID"""
    load_env()
    zone_id = os.environ.get("CLOUDFLARE_ZONE_ID")
    if not zone_id:
        print("❌ 未找到 CLOUDFLARE_ZONE_ID")
        sys.exit(1)
    return zone_id

def list_existing_page_rules(zone_id, headers):
    """列出现有的 Page Rules"""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/pagerules"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            rules = data.get('result', [])
            print(f"\n📋 现有 Page Rules 数量: {len(rules)}")
            
            for i, rule in enumerate(rules, 1):
                targets = rule.get('targets', [])
                actions = rule.get('actions', [])
                status = rule.get('status', 'unknown')
                
                target_url = targets[0]['constraint']['value'] if targets else 'N/A'
                action_details = ', '.join([f"{a['id']}: {a.get('value', 'enabled')}" for a in actions])
                
                print(f"  {i}. [{status.upper()}] {target_url}")
                print(f"     Actions: {action_details}")
                
            return rules
        else:
            print(f"⚠️ 无法获取现有规则: HTTP {response.status_code}")
            print(f"   {response.text}")
            return []
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        return []

def check_ads_txt_rule_exists(rules):
    """检查是否已存在 ads.txt 规则"""
    for rule in rules:
        targets = rule.get('targets', [])
        for target in targets:
            constraint = target.get('constraint', {})
            value = constraint.get('value', '')
            if 'ads.txt' in value.lower():
                print(f"\n⚠️ 发现已存在的 ads.txt 规则:")
                print(f"   ID: {rule['id']}")
                print(f"   URL: {value}")
                print(f"   状态: {rule.get('status', 'unknown')}")
                return rule
    return None

def create_ads_txt_page_rule(zone_id, headers):
    """创建 ads.txt 专用 Page Rule"""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/pagerules"
    
    # Page Rule 配置
    payload = {
        "targets": [
            {
                "target": "url",
                "constraint": {
                    "operator": "matches",
                    "value": "scenro.com/ads.txt"
                }
            }
        ],
        "actions": [
            {
                "id": "cache_level",
                "value": "cache_everything"
            },
            {
                "id": "edge_cache_ttl",
                "value": 86400  # 24 小时
            }
        ],
        "priority": 1,
        "status": "active"
    }
    
    print("\n🚀 正在创建 Page Rule...")
    print(f"   目标 URL: scenro.com/ads.txt")
    print(f"   缓存级别: Cache Everything")
    print(f"   Edge TTL: 86400 秒（24小时）")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                rule_id = data['result']['id']
                print(f"\n✅ Page Rule 创建成功！")
                print(f"   规则 ID: {rule_id}")
                print(f"   状态: active")
                return True
            else:
                errors = data.get('errors', [])
                print(f"\n❌ 创建失败:")
                for error in errors:
                    print(f"   错误码 {error.get('code')}: {error.get('message')}")
                return False
        else:
            print(f"\n❌ API 请求失败: HTTP {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ 创建过程出错: {e}")
        return False

def verify_ads_txt_cache():
    """验证 ads.txt 缓存状态"""
    print("\n🔍 验证 ads.txt 缓存状态...")
    
    try:
        response = requests.get(
            "https://scenro.com/ads.txt",
            headers={'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
        )
        
        cf_cache_status = response.headers.get('CF-Cache-Status', 'UNKNOWN')
        cache_control = response.headers.get('Cache-Control', 'N/A')
        
        print(f"   HTTP 状态: {response.status_code}")
        print(f"   CF-Cache-Status: {cf_cache_status}")
        print(f"   Cache-Control: {cache_control}")
        
        if cf_cache_status in ['HIT', 'EXPIRED']:
            print(f"   ✅ 缓存已生效（或即将生效）")
        elif cf_cache_status == 'MISS':
            print(f"   ⏳ 缓存未命中（首次访问后会被缓存）")
        elif cf_cache_status == 'DYNAMIC':
            print(f"   ⚠️ 仍为 DYNAMIC（规则可能需要几分钟生效，或需要清除缓存）")
        
    except Exception as e:
        print(f"   ❌ 验证失败: {e}")

def main():
    print("=" * 70)
    print("🎯 Cloudflare Page Rule 自动创建器 - Ads.txt 缓存攻坚")
    print("=" * 70)
    
    # 1. 获取认证信息
    headers = get_cloudflare_headers()
    zone_id = get_zone_id()
    
    print(f"\n📌 Zone ID: {zone_id}")
    
    # 2. 列出现有规则
    existing_rules = list_existing_page_rules(zone_id, headers)
    
    # 3. 检查是否已存在 ads.txt 规则
    existing_ads_rule = check_ads_txt_rule_exists(existing_rules)
    
    if existing_ads_rule:
        print("\n⚠️ 检测到已存在的 ads.txt 规则，跳过创建")
        print("   如需重新配置，请先在 Cloudflare 后台手动删除旧规则")
    else:
        # 4. 创建新规则
        success = create_ads_txt_page_rule(zone_id, headers)
        
        if success:
            print("\n⏳ 等待 10 秒让规则生效...")
            import time
            time.sleep(10)
    
    # 5. 验证缓存状态
    verify_ads_txt_cache()
    
    print("\n" + "=" * 70)
    print("✅ Ads.txt 缓存攻坚完成")
    print("=" * 70)
    
    print("\n📝 后续步骤:")
    print("  1. 在 AdSense 后台点击'重新检查 ads.txt'")
    print("  2. 等待 24-48 小时观察 AdSense 状态变化")
    print("  3. 若仍为 DYNAMIC，请在 Cloudflare 清除缓存（Purge Everything）")

if __name__ == "__main__":
    main()
