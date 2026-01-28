---
name: profit-hunter
description: 基于 Payhip 回调机制的海外变现中心。负责付费门禁守护、广告位预留及全球转化优化。
---

# 第一部分：AI 行为准则 (Agent Rules)
1. **上下文优先**: 开始前必须检查 `status.md`。
2. **纯净海外环境**: 忽略所有中国大陆兼容性要求，专注欧美及全球支付链路。
3. **代码敬畏**: 严禁修改 `step2_site_builder.py` 中已跑通的 `?status=success` 逻辑。

# 第二部分：核心章节 (Chapters)

### 第 0 章：真实性与零冗余纪律 (No-Nonsense Protocol)
- **0.1 禁止模拟成功**：Agent 严禁在未经过本地测试（Dry Run）的情况下声称“已修复”或“已跑通”。任何结论必须基于物理执行结果，而非逻辑推测。
- **0.2 拒绝“老师腔”**：严禁使用任何谄媚、说教或虚假的鼓励话术。对话必须保持专业、中立、冷峻，直接给出数据和结论。
- **0.3 故障优先披露**：如果任务失败，Agent 必须在回复的第一句话就说明“失败原因”和“报错行号”，严禁将问题掩盖在长篇大论的解释中。
- **0.4 零水分原则**：去掉所有无意义的开场白（如“我非常理解您的顾虑”）。直接说：做了什么、发现了什么、下一步怎么做。

### 第 1 章：广告位精准占位 (Ad Slots)
- **1.1 模板预留**：在 `step2_site_builder.py` 的 HTML 模板中，在 H1 下方和文件处理区预留 AdSense 容器。
- **1.2 布局平衡**：即使未来开启 Google Auto Ads，Agent 也必须确保广告代码不会覆盖或遮挡 `upsellModal`（付费弹窗）。

### 第 2 章：Payhip 付费门禁管理 (Payhip Gatekeeping)
- **2.1 支付回调守护 (Callback Guard)**：
    - Agent 必须确保网页加载时包含对 `window.location.search` 的监控。
    - **核心逻辑**：只有检测到 `?status=success` 参数，才允许执行 `generateAuditPDF()`。
- **2.2 价值感仪式感 (Perceived Value)**：
    - 必须保留支付成功后的 `showLoader` 延迟动画（如：Scanning metadata...），严禁为了“速度”而删掉这些提升专业感的伪扫描步骤。
- **2.3 拦截器逻辑 (Interception)**：
    - **Audit 模式**：点击时必须立即触发 `upsellModal` 移除 `hidden` 类名，禁止绕过弹窗。
    - **免费模式**：执行 `hideLoader()` 后必须强制延迟 1.2 秒再弹出 `upsellModal`，确保追加销售的曝光率。

### 第 3 章：全球性能与合规 (Global Performance)
- **3.1 欧美加载优化**：确保 `{{pay_link}}` 和 Payhip 脚本在欧美地区的响应速度。
- **3.2 节点记忆**：确保 `saveNode()` 函数能准确将当前路径存入 `localStorage`，保证用户支付后能回到正确的职业页面。

### 第 4 章：变现安全性与防降权 (Ad-Safety)
- **4.1 内容比例控制**：在生成 1.98 万个页面时，若页面核心文字少于 300 字，禁止插入超过 2 个广告位。
- **4.2 交互保护**：严禁任何代码修改导致 `closeUpsell()` 函数失效，必须确保不付费的用户仍能通过“Continue Free”获取基础文件。
- **4.3 支付链路监控**：监控 `{{pay_link}}` 的有效性。如果发现 Payhip 链接失效，Agent 必须立即发出警报。

# 第三部分：执行流程 (Execution Flow)
- **第一步**: 确认 `.env` 文件中的 `PAYHIP_LINK` 是否配置正确。
- **第二步**: 在生成全站静态页时，将付费墙逻辑自动织入每一个 `{{state}}` 对应的工具页。

### 第 5 章：Google AdSense 申请与合规 (AdSense Mastery)

- **5.1 申请前置检查 (Pre-application Audit)**：
    - Agent 必须确保全站 1.98 万个页面均包含：隐私政策 (Privacy Policy)、关于我们 (About Us) 和 联系我们 (Contact Us) 页面。
    - **内容加厚**：严禁在核心文字少于 300 字的页面展示广告，Agent 需利用 `pseo-evolver` 持续加厚内容，直到通过 AdSense 审核。 [cite: 2026-01-17]
- **5.2 广告位动态管理 (Ad Layout)**：
    - **Header 位置**：必须位于 H1 标题下方，严禁遮挡“Audit”付费按钮。
    - **Footer 位置**：必须位于页面底部，确保不影响 PDF 生成逻辑。
- **5.3 自动化 `ads.txt` 维护**：
    - 一旦用户获得 AdSense 账号，Agent 必须自动在根目录生成 `ads.txt`，并确保其在 Cloudflare 上实时可访问。
- **5.4 审核期降权防护**：
    - 在申请期间，Agent 必须将页面加载速度优化至 90 分以上（Lighthouse），防止因加载过慢被拒绝。

### 第 6 章：AdSense 一次性通过铁律 (First-Time Approval)

- **6.1 法律合规“死命令”**：
    - **Footer 必选链接**：全站 1.98 万个页面必须强制挂载 Privacy Policy, Terms, Contact, About Us 四个链接。
    - **内容校验**：隐私政策必须包含“WebAssembly 本地处理”及“Google Cookie 使用说明”，严禁使用通用的垃圾模板。
- **6.2 页面价值感加厚 (Value Inflation)**：
    - **强制字数**：每个 pSEO 职业页面文本量必须达到 600-800 字 [cite: 2026-01-17]。
    - **结构要求**：必须动态包含“How to use”、“Why choose Scenro”和针对该具体职业的“FAQ”。
- **6.3 差异化防降权**：
    - H2/H3 标题严禁全站统一，必须包含该页面的核心变量（如：Alabama Attorney Professional Standards）。

### 第 7 章：内容生态与技术指标 (Content & Tech)

- **7.1 博客先行原则 (Blog Strategy)**：
    - Agent 必须在 `/blog/` 目录下自动生成 15 篇高质量英文行业文章，作为站点的“权重地基”。
- **7.2 清理“未完成”标识**：
    - 严禁全站出现“Beta”、“Coming Soon”或“施工中”字样，确保给审核员“已完全商用”的印象。
- **7.3 广告间距红线**：
    - 预留位（ADSENSE SLOT）必须距离核心功能按钮（Audit/Download）至少 100 像素，严禁诱导点击。

### 第 8 章：全量索引与性能管理 (Indexing & Sitemap)

- **8.1 站点地图集群 (Sitemap Cluster)**：
    - 鉴于 1.98 万个 URL 超过了单个 Sitemap 的限制（5万条/50MB），Agent 必须生成“站点地图索引”及多个子地图文件。
- **8.2 性能红线 (LCP Control)**：
    - Agent 每次推送前必须自检移动端加载速度。若低于 70 分，必须执行 JS 混淆压缩及图片懒加载优化。

### 第 9 章：人设背书与 E-E-A-T 增强 (Expertise & Trust)

- **9.1 多重身份背书 (Professional Bio)**：
    - Agent 必须在主页 (Home) 和 About 页面显眼位置植入创始人简介。
    - **关键词锁定**：必须包含 Teacher (教育专家)、Lawyer (法律背景)、Psychological Counselor (心理咨询师) [cite: 2025-12-26]。
    - **叙事逻辑**：强调工具的开发初衷是基于多年法律合规经验与教育从业背景，旨在提供“人本主义”的数字化办公解决方案。
- **9.2 移动端交互极致优化 (Mobile UX Plus)**：
    - **指尖适配**：所有功能按钮在手机端的高度不得低于 44px，确保肥胖手指也能精准点击。
    - **响应式折叠**：在手机端，FAQ 部分必须使用“手风琴”折叠结构，防止页面过长导致用户流失。
- **9.3 信任信号集成 (Trust Signals)**：
    - 在页脚增加“Founded by a cross-disciplinary team of legal & tech professionals”字样。

### 第 10 章：全站导航与架构固定 (Site Architecture)

- **10.1 顶置全局导航 (Sticky Navigation)**：
    - Agent 必须在全站（含主页及 1.98 万个工具页）顶部增加固定导航栏。
    - **菜单项**：Home, Tools, Insights (Blog), About Us, Contact Us。
- **10.2 主页权重分配 (Homepage Ranking)**：
    - 严禁删除主页的创始人简介（Meet Our Founder）和最新文章（Latest Insights）板块。
    - **SEO 锚点**：主页的“Latest Insights”必须通过内链指向 `/blog/` 下的 15 篇完整文章。
- **10.3 移动端抽屉式菜单 (Mobile Drawer)**：
    - 在手机端，导航菜单必须折叠为“汉堡图标”，确保不遮挡主页的创始人背书文字。
- **10.4 零死路逻辑 (No Dead Ends)**：
    - 每个页面（包括博客页）的底部必须包含“Back to Tools”或“Explore More Professions”的引导按钮。

### 第 11 章：站点矩阵与收益最大化 (Matrix Scaling)

- **11.1 模板化克隆 (Clone Strategy)**：
    - 一旦 Scenro 通过审核，Agent 必须将“创始人简介”、“15 篇博客地基”和“法务四件套”封装为标准模块。
    - **新站启动项**：在上线 SoEasyHub 等新项目时，首日必须包含这些模块以通过初审 [cite: 2025-12-26]。
- **11.2 高级联盟准备 (Premium Prep)**：
    - Agent 必须持续监控 Google Analytics 流量。当月活突破 1 万时，立即发出“升级联盟”提醒并准备申请材料。
- **11.3 广告位 A/B 测试**：
    - 审核通过后，Agent 需利用 `ads.txt` 联动机制，测试手动占位符与自动广告的最佳点击率配比。
### 第 12 章：AdSense 审核期维稳与增长 (Review Period Stability)

- **12.1 抓取压力维持 (Indexing Momentum)**：
    - Agent 必须确保 `Daily Indexer` 脚本每日定时运行，维持全站 1.98 万个 URL 在谷歌爬虫侧的活跃抓取状态。
- **12.2 优质内容“滴灌”策略 (Content Drip)**：
    - **频率**：每 3 天自动生成并发布 1 篇针对“职业合规（Professional Compliance）”的高质量英文行业分析。
    - **同步**：文章发布后，必须立即触发 Sitemap 集群更新，并向 Google Search Console 发送抓取请求。
- **12.3 核心资产在线监控 (Health Monitoring)**：
    - **每日巡检**：Agent 必须每日自检一次全站 `<head>` 中的 `ca-pub-7675066436961689` 代码及根目录 `ads.txt`。
    - **自动修复**：若检测到 404 错误或代码被误覆盖，Agent 必须通过 GitHub Actions 立即执行强制重新部署（Force Deploy），并在恢复后第一时间向用户报告。
- **12.4 流量波动防护**：
    - 在审核未通过前，严禁对全站 URL 结构、CSS 主色调及创始人简介板块进行任何破坏性修改。
- **12.5 自动化与环境自适应 [2026-01-28]**：
    - **环境无关性**：脚本必须具备“环境感知能力”。优先通过环境变量（Environment Variables）获取敏感凭证（如 `GOOGLE_CREDENTIALS_JSON`），而非依赖脆弱的本地文件路径。
    - **零容忍报错**：在自动化流水线（CI/CD）中，任何阻断性错误（如凭证丢失、API 403）必须立即触发 `sys.exit(1)`，强制任务状态为“Failure（红色）”，严禁掩耳盗铃。
    - **全自动守候**：所有周期性任务必须配置 Cron 调度（如 `0 0 * * *`），确保无人值守运行。