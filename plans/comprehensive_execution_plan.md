# Scenro/GRICH 项目综合执行计划

## 项目背景与目标

### 项目现状
- **Scenro (GRICH Utility Tool)**: 职业合规文档生成平台
- **页面规模**: 22,442个职业页面，19,800个目标页面
- **技术架构**: Python静态生成 + Cloudflare Pages + GitHub Actions
- **技能框架**: traffic-sentry, pseo-evolver, profit-hunter 三大技能体系

### 核心目标
1. **安全性合规**: 解决凭证泄露问题，符合技能安全规则
2. **内容质量优化**: 达到pseo-evolver的500+字内容标准
3. **收录自动化**: 实现traffic-sentry的每日200上限自动化
4. **变现优化**: 完善profit-hunter的支付流程和广告布局

## 📊 当前与技能规则的符合度分析

### traffic-sentry 规则符合度
| 规则 | 状态 | 问题 |
|------|------|------|
| 6.2 密钥安全隔离 | ❌ 严重违反 | `.env`和JSON私钥直接暴露 |
| 2.1 严禁过载 | ✅ 符合 | 每日提交上限200个已配置 |
| 5.1 账本优先原则 | ✅ 符合 | `indexed_progress.log`维护正常 |
| 6.1 零人工依赖 | ✅ 符合 | GitHub Actions已配置 |

### pseo-evolver 规则符合度
| 规则 | 状态 | 问题 |
|------|------|------|
| 1.1 500字内容红线 | ⚠️ 部分符合 | 部分页面可能不足500字 |
| 1.2 动态州政策隔离 | ✅ 符合 | 州特定内容已实现 |
| 1.3 创始人专家背书 | ✅ 符合 | 创始人资质已注入 |

### profit-hunter 规则符合度
| 规则 | 状态 | 问题 |
|------|------|------|
| 2.1 支付回调守护 | ✅ 符合 | `?status=success`逻辑已实现 |
| 4.1 内容比例控制 | ⚠️ 需验证 | 广告位数量需检查 |

## 🚨 优先级别问题

### 紧急优先级 (P0)
1. **凭证安全泄露** - 违反traffic-sentry 6.2规则
2. **内容字数不足** - 违反pseo-evolver 1.1规则

### 高优先级 (P1)
1. **自动化收录优化** - traffic-sentry配额管理
2. **AdSense合规** - pseo-evolver审核准备

### 中优先级 (P2)
1. **性能优化** - 页面加载速度
2. **监控完善** - 错误追踪和分析

## 🛠️ 分阶段执行计划

### 阶段一：安全修复与凭证管理 (1-3天)

#### 任务1.1：凭证轮换与安全配置
1. **撤销暴露凭证**:
   - 轮换Cloudflare API Key
   - 撤销GitHub Token (已撤销，请使用新的GitHub Secret)
   - 创建新的Google Service Account

2. **配置GitHub Secrets**:
   ```yaml
   # 需要配置的Secrets（请在GitHub仓库Secrets中设置）
   CLOUDFLARE_API_KEY: [新密钥]
   CLOUDFLARE_ACCOUNT_ID: [您的Cloudflare账户ID]
   CLOUDFLARE_ZONE_ID: [您的Cloudflare区域ID]
   GSC_API_JSON: [GSC服务账户JSON凭证]
   GOOGLE_SERVICE_ACCOUNT_JSON: [Indexing API服务账户JSON凭证]
   ```

3. **更新部署脚本**:
   - 修改`.github/workflows/deploy.yml`使用Secrets
   - 更新`.github/workflows/daily_indexing.yml`使用Secrets
   - 移除`.env`文件中的敏感信息

#### 任务1.2：仓库历史清理
1. **从Git历史中清除敏感数据**:
   ```bash
   git filter-repo --force \
     --replace-text <(echo "CLOUDFLARE_API_KEY==>CLOUDFLARE_API_KEY=[REDACTED]") \
     --replace-text <(echo "GH_TOKEN==>GH_TOKEN=[REDACTED]")
   ```

2. **添加.gitignore规则**:
   ```gitignore
   # 在.gitignore中添加
   .env
   *.json
   config/local*.json
   ```

#### 任务1.3：本地开发安全
1. **创建环境模板**:
   ```bash
   # .env.template
   CLOUDFLARE_ACCOUNT_ID=your_account_id
   CLOUDFLARE_ZONE_ID=your_zone_id
   CLOUDFLARE_EMAIL=your_email
   # 其他非敏感配置
   ```

### 阶段二：内容质量与SEO优化 (3-7天)

#### 任务2.1：内容字数合规检查
1. **实施字数检查脚本**:
   ```python
   # content_audit.py
   def check_word_count(html_path):
       # 提取<article>标签内文字
       # 统计字数，确保≥500字
       pass
   ```

2. **自动内容加厚机制**:
   - 集成pseo-evolver的AI生成逻辑
   - 为不足500字的页面自动生成合规报告
   - 确保州特定内容≥150字

3. **批量修复脚本**:
   ```python
   # 扫描所有页面，识别字数不足的
   # 调用DeepSeek API生成补充内容
   # 重新构建受影响页面
   ```

#### 任务2.2：页面模板优化
1. **完善E-E-A-T信号**:
   - 强化创始人专家背书模块
   - 添加"Verified by Michael"标签
   - 增加行业资质展示

2. **结构化数据标记**:
   ```html
   <!-- 添加Schema.org标记 -->
   <script type="application/ld+json">
   {
     "@context": "https://schema.org",
     "@type": "ProfessionalService",
     "name": "Scenro - {{profession}} in {{state}}",
     "description": "合规文档生成工具..."
   }
   </script>
   ```

3. **专业清单增强**:
   - 为每个职业添加"Professional Checklist"
   - 增加交互式元素提升页面价值

#### 任务2.3：AdSense申请准备
1. **全站合规检查**:
   - 确认隐私政策、关于我们、联系我们页面完整
   - 确保无违规内容
   - 广告位布局合理

2. **内容质量提升**:
   - 所有核心页面≥500字
   - 原创内容比例≥70%
   - 图片优化和alt标签

### 阶段三：收录自动化优化 (5-10天)

#### 任务3.1：traffic-sentry配额管理系统
1. **实现智能分批逻辑**:
   ```python
   # daily_indexer.py优化
   class QuotaManager:
       MAX_DAILY_SUBMISSIONS = 200
       COOLDOWN_HOURS = 24
       
       def get_today_quota(self):
           # 从indexed_progress.log读取今日已提交数
           # 计算剩余配额
           pass
   ```

2. **429错误自动熔断**:
   - 检测到429立即停止任务
   - 记录错误时间
   - 进入24小时冷却期

3. **断点续传机制**:
   - 基于`indexed_progress.log`的状态恢复
   - 避免重复提交

#### 任务3.2：零活跃应急机制
1. **实施自动诊断**:
   ```python
   # gsc_status_check.py增强
   def zero_activity_emergency():
       if active_pages == 0 for 7 days:
           # 1. 全站Sitemap健康检查
           # 2. 随机抽检50个页面
           # 3. 生成风险报告
   ```

2. **内容重复度检测**:
   - Jaccard系数计算相似度
   - 识别高重复页面
   - 触发AI重写

#### 任务3.3：末位淘汰制
1. **低价值页面识别**:
   ```python
   # 每周日执行
   def bottom_elimination():
       # 对比indexed_progress.log与GSC展示量
       # 识别上线>30天且Impressions=0的页面
       # 从professions.csv中移除
   ```

2. **配额再分配**:
   - 腾出的名额分配给高潜力行业
   - 优先医疗、法律、教育行业

### 阶段四：变现与性能优化 (7-14天)

#### 任务4.1：profit-hunter支付优化
1. **支付流程测试**:
   - 测试`?status=success`回调
   - 验证`upsellModal`显示逻辑
   - 确保`saveNode()`函数正常工作

2. **广告位优化**:
   - 检查广告位数量合规性
   - 优化布局避免遮挡
   - 实现响应式广告

3. **全球性能优化**:
   - Payhip链接加载速度测试
   - 欧美地区CDN优化

#### 任务4.2：网站性能提升
1. **构建优化**:
   ```python
   # step2_site_builder.py优化
   - 实现增量构建
   - 添加构建缓存
   - 并行生成页面
   ```

2. **前端优化**:
   - 图片懒加载实现
   - CSS/JS最小化
   - 浏览器缓存策略

3. **监控系统**:
   ```yaml
   # 监控配置
   - UptimeRobot: 网站可用性
   - Sentry: 错误追踪
   - Plausible: 用户行为分析
   ```

## 📋 详细执行时间表

### 第1周：安全与基础
| 日期 | 任务 | 负责人 | 交付物 |
|------|------|--------|--------|
| 第1天 | 凭证轮换与Secrets配置 | 开发者 | 安全的部署流水线 |
| 第2天 | 仓库历史清理 | 开发者 | 干净的Git历史 |
| 第3天 | 字数检查脚本开发 | 开发者 | content_audit.py |
| 第4-5天 | 内容批量加厚 | AI+开发者 | 500+字合规页面 |

### 第2周：收录自动化
| 日期 | 任务 | 负责人 | 交付物 |
|------|------|--------|--------|
| 第6-7天 | 配额管理系统 | 开发者 | QuotaManager类 |
| 第8天 | 429熔断机制 | 开发者 | 错误处理逻辑 |
| 第9天 | 零活跃应急 | 开发者 | emergency_protocol.py |
| 第10天 | 末位淘汰制 | 开发者 | bottom_elimination.py |

### 第3周：变现与优化
| 日期 | 任务 | 负责人 | 交付物 |
|------|------|--------|--------|
| 第11-12天 | 支付流程测试 | QA+开发者 | 测试报告 |
| 第13天 | 广告位优化 | 开发者 | 响应式广告布局 |
| 第14天 | 性能监控部署 | 运维 | 监控仪表板 |

## 🎯 成功指标

### 安全性指标
- [ ] 零敏感凭证暴露
- [ ] GitHub Secrets配置率100%
- [ ] 自动化安全扫描通过

### 内容质量指标
- [ ] 所有页面≥500字
- [ ] 州特定内容≥150字
- [ ] 内容重复度<15%

### 收录指标
- [ ] 每日提交≤200个URL
- [ ] 收录率≥60%
- [ ] 零429错误持续7天

### 性能指标
- [ ] 页面加载时间<3秒
- [ ] AdSense审核通过
- [ ] 支付转化率≥2%

## 🔧 技术实施细节

### 安全实施
```python
# 安全凭证加载示例
def load_secure_credentials():
    # 从环境变量读取（GitHub Secrets注入）
    cf_api_key = os.environ.get('CLOUDFLARE_API_KEY')
    google_creds_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
    
    if not cf_api_key:
        raise ValueError("CLOUDFLARE_API_KEY not set in environment")
    
    # 动态创建临时凭证文件
    if google_creds_json:
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(google_creds_json)
            creds_path = f.name
        return creds_path
```

### 内容加厚机制
```python
# AI内容生成集成
def enhance_content(profession, state, current_content):
    """为不足500字的页面生成补充内容"""
    
    if word_count(current_content) >= 500:
        return current_content
    
    # 调用DeepSeek API生成州特定内容
    prompt = f"""
    Generate 300-word professional compliance content for {profession} in {state}.
    Focus on state-specific regulations and best practices.
    """
    
    additional_content = call_deepseek_api(prompt)
    return current_content + "\n\n" + additional_content
```

### 配额管理系统
```python
class TrafficSentryQuota:
    def __init__(self, log_path='indexed_progress.log'):
        self.log_path = log_path
        self.max_daily = 200
    
    def get_available_quota(self):
        today = datetime.now().date()
        today_submissions = self._count_today_submissions(today)
        return max(0, self.max_daily - today_submissions)
    
    def can_submit(self, url_count):
        return self.get_available_quota() >= url_count
```

## 🚀 风险与缓解策略

### 技术风险
| 风险 | 概率 | 影响 | 缓解策略 |
|------|------|------|----------|
| Cloudflare文件限制 | 中 | 高 | 实施增量构建，监控文件数量 |
| GSC API配额超限 | 高 | 中 | 严格的配额管理和429熔断 |
| 内容重复度惩罚 | 中 | 高 | Jaccard检测+AI重写 |

### 业务风险
| 风险 | 概率 | 影响 | 缓解策略 |
|------|------|------|----------|
| AdSense审核失败 | 高 | 高 | 严格的内容质量检查 |
| 支付流程中断 | 低 | 高 | 定期测试+监控告警 |
| 收录率下降 | 中 | 中 | 零活跃应急机制 |

## 📞 沟通与协作

### 团队角色
- **安全负责人**: 凭证管理和安全合规
- **内容负责人**: 质量检查和AI生成
- **SEO负责人**: 收录优化和监控
- **开发负责人**: 代码实现和部署

### 进度报告
- **每日站会**: 15分钟同步进度
- **每周报告**: 进度总结和下周计划
- **风险会议**: 每月风险评审

### 文档要求
- 所有配置变更记录在`CHANGELOG.md`
- API密钥轮换记录在`SECURITY.md`
- 部署流程更新在`DEPLOYMENT.md`

## 🎉 完成标准

### 阶段一完成
- [ ] `.env`文件无敏感信息
- [ ] GitHub Secrets配置完成
- [ ] 部署流水线使用Secrets
- [ ] Git历史清理完成

### 阶段二完成
- [ ] 所有页面≥500字验证通过
- [ ] 结构化数据标记添加完成
- [ ] AdSense申请材料准备就绪

### 阶段三完成
- [ ] 每日200配额系统运行正常
- [ ] 429熔断机制测试通过
- [ ] 末位淘汰制首次执行完成

### 阶段四完成
- [ ] 支付流程端到端测试通过
- [ ] 页面加载时间<3秒达标
- [ ] 监控系统部署完成

## 🔄 持续改进机制

### 自动化检查
```yaml
# GitHub Actions工作流
name: Daily Compliance Check
on:
  schedule:
    - cron: "0 9 * * *"  # 每天北京时间17:00
jobs:
  security_audit:
    runs-on: ubuntu-latest
    steps:
      - name: Check for exposed credentials
        run: python scripts/check_exposed_secrets.py
  
  content_audit:
    runs-on: ubuntu-latest
    steps:
      - name: Check word count compliance
        run: python scripts/content_audit.py
```

### 质量门禁
1. **预提交检查**: 代码质量、安全扫描
2. **预部署检查**: 内容合规、性能测试
3. **生产监控**: 实时警报、自动恢复

## 📚 相关文档参考

1. **技能文档**:
   - [`traffic-sentry/SKILL.md`](.agent/skills/traffic-sentry/SKILL.md)
   - [`pseo-evolver/SKILL.md`](.agent/skills/pseo-evolver/SKILL.md)
   - [`profit-hunter/SKILL.md`](.agent/skills/profit-hunter/SKILL.md)

2. **项目文档**:
   - [`status.md`](status.md) - 当前项目状态
   - [`FINAL_EXECUTION_REPORT_20260201.md`](FINAL_EXECUTION_REPORT_20260201.md) - 执行报告

3. **分析报告**:
   - [`plans/website_health_analysis.md`](plans/website_health_analysis.md) - 网站健康状况分析

## 🎯 最终建议

基于技能规则和项目现状，建议按以下顺序执行：

1. **立即行动**: 安全凭证轮换（违反traffic-sentry 6.2规则）
2. **并行执行**: 内容字数检查和修复（违反pseo-evolver 1.1规则）
3. **系统优化**: 收录自动化完善（符合traffic-sentry规则）
4. **变现增强**: 支付和广告优化（符合profit-hunter规则）

本计划已综合考虑三大技能规则要求，确保项目在安全、内容质量、收录效率和变现能力四个方面全面提升。

---
*计划创建时间: 2026-02-17*
*创建者: Roo (架构师模式)*
*依据: Scenro项目文件 + 三大技能规则*