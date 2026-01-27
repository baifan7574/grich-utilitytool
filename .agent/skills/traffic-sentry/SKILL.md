---
name: traffic-sentry
description: 网站身份护卫与收录自动化中心。负责 GSC 验证、Sitemap 提交及每日 429 避险配额管理。
---

# 第一部分：AI 行为准则 (The Meta Rules)
1. **上下文优先**: 开始前必须检查根目录 `status.md` 了解最新进度。
2. **技能合规**: 修改代码前必须对照本 SKILL 规则，确保操作不越界。
3. **自我更新**: 完成重要任务（如成功提交一批 URL）后，必须更新 `status.md`。
4. **中文回复**: 始终使用中文与用户沟通。

# 第二部分：核心执行规范 (Chapters)

### 第 0 章：真实性与零冗余纪律 (No-Nonsense Protocol)
- **0.1 禁止模拟成功**：Agent 严禁在未经过本地测试（Dry Run）的情况下声称“已修复”或“已跑通”。任何结论必须基于物理执行结果，而非逻辑推测。
- **0.2 拒绝“老师腔”**：严禁使用任何谄媚、说教或虚假的鼓励话术。对话必须保持专业、中立、冷峻，直接给出数据和结论。
- **0.3 故障优先披露**：如果任务失败，Agent 必须在回复的第一句话就说明“失败原因”和“报错行号”，严禁将问题掩盖在长篇大论的解释中。
- **0.4 零水分原则**：去掉所有无意义的开场白（如“我非常理解您的顾虑”）。直接说：做了什么、发现了什么、下一步怎么做。

### 第 1 章：身份验证锁定 (Verification)
- **1.1 自动巡检**：每次构建任务结束后，强制核查 `dist/` 目录。
- **1.2 物理恢复**：若发现 `google*.html` 丢失，强制从根目录复制到 `dist/`。

### 第 2 章：收录配额与队列 (Indexing Quota)
- **2.1 严禁过载**：单日提交上限严格锁定为 200 个，严禁一次性提交 1.98 万个 URL。
- **2.2 自动分批**：每天北京时间 09:00 自动从待提交队列提取 180 个 URL。
- **2.3 进度记忆**：在根目录维护 `indexed_progress.log`，记录已成功和因 429 失败的 URL。

### 第 3 章：监控与预警 (Audit)
- **3.1 差额对比**：每 48 小时对比“本地 URL 数”与“GSC 索引数”。
- **3.2 深度诊断**：若收录率低于 30% 或环比下降 > 5%，立即分析原因并发出终端警告。

### 第 4 章：全自动避险 (Circuit Breaker)
- **4.1 自动熔断**：捕获到 429 错误立即停止任务，记录时间并进入 24 小时冷却期。
- **4.2 静默执行**：每天首次启动自动读取队列，静默处理后输出简报：“今日 X/180 已完成，总进度：X/19803”。

## 任务指令 (Task Trigger)
1. 检查 `dist/` 下的验证 HTML。
2. 对比 Sitemap 与 GSC 索引，找出“失踪”页面。
3. 自动维持 `indexed_progress.log` 状态。

### 第 5 章：数据一致性与断点续传 (Data Integrity)

- **5.1 账本优先原则**：
    - 即使 `step2_site_builder.py` 重新生成了新的 Sitemap，Agent 必须以根目录的 `indexed_progress.log` 为唯一真理。
    - 严禁重复提交日志中已标记为“Success”的 URL，哪怕它们在新的 Sitemap 中位置发生了变化。

- **5.2 增量识别逻辑**：
    - 每次扫描时，Agent 应自动对比 Sitemap 与 `indexed_progress.log`。
    - 发现新出现的 URL，自动将其追加到待提交队列的末尾；发现消失的 URL，在日志中标记为“Obsolete”。

- **5.3 故障恢复**：
    - 若 `indexed_progress.log` 意外丢失或损坏，Agent 禁止盲目开始任务。
    - 必须先调用 GSC API 抓取当前的索引状态，尝试反向重构一份“已收录清单”，确保配额不被浪费在已收录的页面上。

### 第 6 章：全自动云端部署 (Cloud Deployment)

- **6.1 零人工依赖 (Path B)**：
    - Agent 必须优先通过 GitHub Actions 实现自动化。严禁让收录任务长期依赖用户本地电脑。
- **6.2 密钥安全隔离 (Secret Management)**：
    - 严禁将 Google JSON 密钥直接上传到仓库。必须指导用户将其配置在 GitHub Repository Secrets 中。
- **6.3 自动化握手 (CI/CD Handshake)**：
    - Agent 需自动生成 `.github/workflows/daily_indexing.yml`，设定每天北京时间 09:00 自动启动。
    - 任务结束后，必须由 GitHub Action 自动将更新后的 `indexed_progress.log` 推回仓库，保持数据同步。

### 第 7 章：代码上线质量控制 (Pre-flight Checks)

- **7.1 本地语法校验**：在行使 `GH_TOKEN` 推送代码至 GitHub 前，Agent 必须在本地模拟环境运行一次 `python -m py_compile daily_indexer.py`。
- **7.2 变量完整性检查**：严禁出现未定义的函数名（如 `check_verification_file`）。
- **7.3 云端路径一致性**：Agent 必须确保 `.yml` 中的 `working-directory` 与仓库真实层级（如 `./grich-utilitytool/`）完全匹配。
- **7.4 失败重试机制**：若云端报错，Agent 必须主动读取报错日志（Logs），不得在未修正代码逻辑的情况下重复尝试推送。
### 第 8 章：物理验证与云端对齐 (Cloud-Truth Verification)

- **8.1 严禁“脑补”运行**：Agent 在声明任务完成前，必须在本地终端物理执行一次该脚本，并截取前 10 行运行日志作为证据，严禁模拟输出。
- **8.2 云端对齐测试 (Path B Focus)**：
    - 凡是涉及 GitHub Actions 的修改，Agent 必须利用 `GH_TOKEN` 权限主动推送到 `main` 或 `test` 分支。
    - 只有当 GitHub Actions 给出绿色对勾（Success）后，Agent 才允许向用户汇报“已修复”。
- **8.3 路径映射感知**：Agent 必须在脑中建立映射表：`D:\...\scenro\` 对应云端的 `./grich-utilitytool/`。任何路径引用必须使用相对路径，严禁使用 Windows 物理盘符。
- **8.4 真实性惩罚**：若 Agent 在未通过物理测试的情况下声称“已修复”，用户将视其为“逻辑漂移”，Agent 必须立即停工并重新进行环境自检。