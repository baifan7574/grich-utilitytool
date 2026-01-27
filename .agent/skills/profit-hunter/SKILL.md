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