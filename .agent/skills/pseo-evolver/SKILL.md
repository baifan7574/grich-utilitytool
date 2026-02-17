---
name: pseo-evolver
description: 网站进化与排名优化。负责模板迭代、内容加厚、AdSense 攻坚及全站质量控制。
---

# 第一部分：AI 行为总纲 (Agent Behavior Rules)
1. **上下文优先**: 开始前必须检查根目录 `status.md` 了解项目最新进度。
2. **技能合规**: 修改代码前必须对照本 SKILL 规则，严禁违规操作。
3. **强制中文沟通**: 始终使用中文与用户沟通，但生成的网站内容必须为地道美式英语。
4. **代码敬畏**: 严禁在未实现“内容加厚”逻辑前声称已解决 AdSense 审核问题。

# 第二部分：核心执行章节 (Rules)

### 第 0 章：真实性与零冗余纪律 (No-Nonsense Protocol)
- **0.1 禁止模拟成功**：严禁在未经过本地测试的情况下声称“已修复”。
- **0.2 拒绝“老师腔”**：保持专业、中立、冷峻，直接给出数据和结论。

### 第 1 章：AdSense 审核攻坚 (AdSense Approval Mastery)
- **1.1 500字内容红线 (Word Count Floor)**：
    - **硬性要求**：所有生成页面的 `<article>` 标签内纯文字内容不得低于 **500 字**。
    - **执行**：若字数不足，Agent 必须通过 AI 生成该职业在特定州的“行业合规报告”进行填充。
- **1.2 动态州政策隔离 (State-Specific Content)**：
    - **核心逻辑**：严禁全美使用统一模板。
    - **执行**：每个页面必须包含至少 150 字关于该州（State）特定法律、执照要求或行业痛点的原创描述。
- **1.3 创始人专家背书 (Expert E-E-A-T Injection)**：
    - **注入点**：在每个子页面显著位置展示创始人资质（律师、教师、校长、心理咨询师背景）。
    - **文案**：使用“Verified by Michael - Legal & Education Expert”等标签，增加真人审核感，对冲“自动化”标签。

### 第 2 章：内容指纹加厚 (Content Thickening)
- **2.1 拒绝低价值重复**：
    - **逻辑**：通过 `step2_site_builder.py` 引入 `expert_insights.json`，为不同职业组合注入差异化指纹。
- **2.2 交互价值增强**：
    - **要求**：每个页面必须包含一个“Professional Checklist”（职业自检清单），通过工具属性提升页面在 Google 眼中的“有用性”。

### 第 3 章：SEO 倒推进化逻辑 (SEO Reverse Evolution)
- **3.1 TDK 自动对齐**：
    - 根据 GSC 的展示数据，将“高展示、低点击”的页面标题修改为更具转化力的行动词。
- **3.2 末位淘汰制**：
    - 若某页面在 30 天内 0 展现且 0 索引，Agent 需触发“深度重写”逻辑或将其在 Sitemap 中临时下线。

### 第 4 章：Action 闭环记账 (Action Loopback)
- **4.1 权限保障**：
    - 确保 `GITHUB_TOKEN` 具有 `write` 权限，Action 运行后必须成功回写 `indexed_progress.log`。
- **4.2 账本唯一性**：
    - 始终以云端日志为准，本地操作前强制执行 `git pull`。