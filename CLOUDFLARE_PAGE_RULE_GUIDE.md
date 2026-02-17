# ============================================================
# Cloudflare Page Rule 傻瓜式操作指南
# 目标：为 scenro.com/ads.txt 启用缓存（5 分钟完成）
# ============================================================

## 📌 背景说明
**问题**：AdSense 后台显示"未找到 ads.txt"  
**根因**：Cloudflare 未缓存该文件（CF-Cache-Status: DYNAMIC），Google Bot 爬取时可能遭遇临时限流  
**解决方案**：创建 Page Rule 强制缓存 ads.txt 文件

---

## ✅ 操作步骤（共 5 步，约 5 分钟）

### 步骤 1: 登录 Cloudflare 仪表板
1. 打开浏览器，访问 https://dash.cloudflare.com/
2. 使用账号 `baifan7574@gmail.com` 登录
3. 点击左侧菜单找到 **scenro.com** 域名
4. 点击进入该域名的管理页面

---

### 步骤 2: 进入 Page Rules 配置页面
1. 在 scenro.com 的管理页面，找到顶部导航栏
2. 点击 **Rules**（规则）
3. 在下拉菜单中选择 **Page Rules**（页面规则）

**截图参考**：
```
顶部菜单栏：
┌─────────────────────────────────────────┐
│ Overview │ Analytics │ Rules │ Settings │
│                         ↓                │
│                   Page Rules             │
└─────────────────────────────────────────┘
```

---

### 步骤 3: 创建新的 Page Rule
1. 在 Page Rules 页面，点击右上角的 **Create Page Rule** 按钮
2. 看到 "If the URL matches:" 输入框

**填写规则配置**：

#### 3.1 URL Pattern（URL 匹配模式）
在 "If the URL matches:" 输入框中填写：
```
scenro.com/ads.txt
```

#### 3.2 添加设置项
点击 **Pick a Setting** 下拉菜单，依次添加以下两项：

**设置 1：Cache Level（缓存级别）**
- 选择：`Cache Level`
- 设置为：`Cache Everything`

**设置 2：Edge Cache TTL（边缘缓存时间）**
- 选择：`Edge Cache TTL`
- 设置为：`1 day`（或输入 86400 秒）

**完整配置截图参考**：
```
┌─────────────────────────────────────────────────────┐
│ If the URL matches:                                 │
│ ┌─────────────────────────────────────────────────┐ │
│ │ scenro.com/ads.txt                              │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│ Then the settings are:                             │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Cache Level:       Cache Everything             │ │
│ └─────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Edge Cache TTL:    1 day                        │ │
│ └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

---

### 步骤 4: 保存并启用规则
1. 检查配置是否正确（URL 和两个设置项）
2. 点击页面底部的 **Save and Deploy** 按钮
3. 等待 5-10 秒，看到绿色提示 "Page Rule created successfully"

**重要**：
- Page Rule 会在 **1-2 分钟内全球生效**
- 免费账号最多可创建 **3 条** Page Rules

---

### 步骤 5: 验证缓存是否生效
等待 2 分钟后，在命令行运行以下命令验证：

```bash
curl -I https://scenro.com/ads.txt
```

**预期结果**：
```
HTTP/2 200 
content-type: text/plain; charset=utf-8
cf-cache-status: HIT          ← 必须为 HIT 或 MISS（首次访问）
cache-control: public, max-age=86400
```

**关键检查点**：
- `cf-cache-status` 应该是 `HIT`（缓存命中）或 `MISS`（首次访问，下次会命中）
- 绝对不能是 `DYNAMIC`（动态内容，不缓存）

---

## 🔍 如果验证失败怎么办？

### 情况 1: CF-Cache-Status 仍为 DYNAMIC
**解决方案**：
1. 回到 Cloudflare 仪表板
2. 进入 **Caching** → **Configuration**
3. 点击 **Purge Everything**（清除所有缓存）
4. 等待 30 秒后重新访问 https://scenro.com/ads.txt

### 情况 2: 页面规则未显示
**解决方案**：
1. 检查是否在正确的域名（scenro.com）下
2. 确认规则状态为 "Active"（绿色勾）
3. 检查是否超过免费账号的 3 条规则限制

### 情况 3: AdSense 仍显示"未找到"
**解决方案**：
1. 在 AdSense 后台找到 ads.txt 警告
2. 点击 **"重新检查 ads.txt"** 按钮
3. 等待 **24-48 小时**（Google 重新爬取需要时间）

---

## 📊 完成后的状态

### ✅ Cloudflare 侧
- Page Rule 数量：1 条
- 规则状态：Active（绿色）
- URL Pattern：scenro.com/ads.txt
- 缓存级别：Cache Everything

### ✅ ads.txt 响应头
```
cf-cache-status: HIT
cache-control: public, max-age=86400
content-type: text/plain
```

### ✅ AdSense 后台（48 小时后）
- ads.txt 状态：✅ 已找到
- 发布商 ID：pub-7675066436961689
- 行数：1

---

## 🆘 紧急联系

如遇问题，请提供以下信息：
1. Cloudflare Page Rule 的截图
2. `curl -I https://scenro.com/ads.txt` 的完整输出
3. AdSense 后台的 ads.txt 状态截图

---

**预计完成时间**：5 分钟  
**生效时间**：2-5 分钟  
**AdSense 确认时间**：24-48 小时
