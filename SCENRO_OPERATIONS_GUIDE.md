# Scenro 上线操作清单

这份清单给不懂代码的人看，只写必须做的事。

## 先做安全

仓库里曾经出现过明文密钥。不要继续用旧密钥。

需要重新生成并替换：

- Cloudflare API Token
- GitHub Token
- Payhip API Key
- DeepSeek API Key

旧密钥要在对应平台后台作废。

## Cloudflare Pages 必填变量

进入 Cloudflare Pages 项目后台，找到环境变量，添加：

- `DEEPSEEK_API_KEY`
- `PAYHIP_API_KEY`

这两个是网站收费报告能不能跑的关键。

## GitHub Actions 必填 Secrets

进入 GitHub 仓库后台，找到 Secrets，添加：

- `CF_API_TOKEN`
- `CF_ACCOUNT_ID`
- `GOOGLE_SERVICE_ACCOUNT_JSON`

没有这几个，自动部署和 Google 收录检查会失败。

## 网站是否能赚钱的判断

现在技术修复只是让网站能跑，不代表马上有收入。

必须重点验证：

1. 用户付款后是否能回到成功页。
2. 成功页是否能生成 AI 报告。
3. 报告内容是否值得用户付费。
4. 是否有人愿意为 PDF 风险报告付费。

## 正确的变现方向

不要主打低价 `$4.99`。

优先测试：

- `$99` 单次 PDF 风险审计报告
- `$299/月` 小团队版
- `$999/月` 专业事务所版

目标是一万美金每月时，靠低价小单太难，靠高客单 B2B 才有机会。
