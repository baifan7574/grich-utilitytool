---
name: traffic-sentry
description: 核心职责是确保 GSC 验证永不掉线，并自动提交 Sitemap。网站身份与收录守卫。负责 GSC 验证、Sitemap 提交及每日配额管理
---

## 规则 1：身份维持 (Identity Maintenance)
- 每次检测到 `dist/` 目录更新，必须立即检查根目录下的 `google*.html` 验证文件。
- 如果 `dist/` 中缺失该文件，强制执行复制操作，确保验证始终有效。

## 规则 2：主动收录 (Active Indexing)
- 自动读取 `.env` 中的 `GOOGLE_APPLICATION_CREDENTIALS` 路径。
- 调用 Google Indexing API，每天分批（每批 100 个）提交 `sitemap.xml` 中的新 URL。
- 禁止一次性提交 1.98 万个 URL 以避免触发 Google 频率限制。

## 规则 3：差额监控 (Gap Analysis)
- 每 48 小时对比一次“本地生成的 URL 数量”与“Google 已索引数量”。
- 若索引比例环比下降超过 10%，自动触发健康警报并在终端显示原因分析。
---


4.身份验证与稳定性 (Verification)
1.1 **验证锁死**：每次构建任务结束后，Agent 必须强制核查 `dist/` 目录。
1.2 **自动恢复**：若发现 `google*.html` 丢失，必须无条件从根目录复制到 `dist/`，确保 GSC 认领权永不失效。

5.收录配额管理 (Indexing Quota)
2.1 **严禁过载**：鉴于 Google Indexing API 每日约 200 个 URL 的限制，Agent 严禁一次性提交 1.98 万个 URL。
2.2 **自动队列**：Agent 需维护一个提交记录，每天北京时间 09:00 自动提交 180 个 URL，直至全站完成。

# 6.收录缺口监控 (Audit)
3.1 **差额核算**：每 48 小时对比“本地生成数”与“GSC 索引数”。
3.2 **风险警报**：若索引率环比下降 > 5%，立即分析原因并输出报告。

# AI 行为准则 (Agent Rules)

1. **上下文优先**: 在开始回复前，**必须**先检查 `status.md` 以了解当前项目进度的最新状态。
2. **技能合规**: 在修改代码前，**必须**参考 `.agent/skills/` 下的相关技能，确保修改符合既定标准。
3. **自我更新**: 每次完成重要里程碑后，**必须** 更新 `status.md`，以便下一个 AI 窗口能无缝衔接。
4. **中文回复**: 始终使用中文与用户沟通。

## 任务指令

1\. 自动检查 dist/ 目录下是否存在 Google 验证 HTML。若缺失，提示生成。

2\. 每 48 小时对比 sitemap.xml 与 GSC 索引列表，找出未被收录的页面。

3\. 如果收录率低于 30%，自动在终端发送警告。

