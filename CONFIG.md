# Daily News 项目配置

## 项目信息
- **项目名称**: Daily News - 每日新鲜事自动化抓取
- **项目路径**: F:\DailyNews
- **GitHub 仓库**: 需要创建
- **部署方式**: GitHub Pages + GitHub Actions

## 功能模块

### 1. GitHub 热门项目 (10个)
- **数据源**: GitHub Trending API
- **筛选条件**: 昨日新增 star 数 top 10
- **输出**: 项目名、描述、语言、star 数、链接

### 2. 创业投资新闻 (10条)
- **数据源**: 36氪、IT桔子、创业邦、投资界
- **筛选条件**: 最新 10 条创业/融资相关新闻
- **输出**: 标题、来源、摘要、链接

### 3. 小成本创业机会 (10条)
- **数据源**: 36氪、知乎、小红书、IndieHackers
- **筛选条件**: 低成本、轻创业相关
- **输出**: 项目类型、启动成本、市场需求、成功案例

### 4. 游戏设计灵感 (10条)
- **数据源**: GameDev.net、Gamasutra、IndieDB、Steam、触乐、游研社
- **筛选条件**: 玩法创新、游戏设计相关内容
- **输出**: 标题、类型标签、摘要、链接

## 技术特性

### 去重机制
- **标题去重**: TF-IDF + 余弦相似度 (阈值: 0.7)
- **内容去重**: SimHash (汉明距离阈值: 3)
- **历史记录**: 保留 30 天

### 相关性排序
- **时间权重**: 越新越好
- **来源权重**: 36氪、IT桔子等权重更高
- **关键词权重**: 融资、投资、创业等关键词加权

### 推送方式
- **企业微信机器人 Webhook**
- **格式**: Markdown
- **内容**: 摘要 + 完整报告链接

## 配置说明

### GitHub Secrets
需要在仓库 Settings > Secrets and variables > Actions 中添加：

| Secret 名称 | 说明 |
|-------------|------|
| `WECOM_WEBHOOK_URL` | 企业微信机器人 Webhook URL |

### 定时任务
- **触发时间**: 每天北京时间 08:00 (UTC 00:00)
- **Cron 表达式**: `0 0 * * *`

## 文件结构

```
DailyNews/
├── .github/
│   └── workflows/
│       └── daily-news.yml          # GitHub Actions 工作流
├── scripts/
│   ├── fetch_github.py             # GitHub 热门项目抓取
│   ├── fetch_startup.py            # 创业投资新闻抓取
│   ├── fetch_opportunities.py      # 小成本创业机会抓取
│   ├── fetch_game.py               # 游戏设计灵感抓取
│   ├── deduplicator.py             # 去重模块
│   ├── report_generator.py         # 报告生成
│   ├── wecom_notifier.py           # 企业微信推送
│   ├── generate_index.py           # 生成首页
│   ├── main.py                     # 主脚本
│   └── utils.py                    # 工具函数
├── data/
│   ├── history/
│   │   └── news_history.json       # 历史记录（30天）
│   └── YYYY-MM-DD/                 # 每日报告
│       ├── github-trending.md
│       ├── startup-news.md
│       ├── startup-opportunities.md
│       ├── game-design.md
│       ├── summary.md
│       └── index.html
├── index.html                      # GitHub Pages 主页
├── requirements.txt                # Python 依赖
└── README.md                       # 项目说明
```

## 使用说明

### 1. 创建 GitHub 仓库
```bash
# 在 GitHub 上创建新仓库
# 仓库名: daily-news (或你喜欢的名字)
```

### 2. 推送代码
```bash
cd F:\DailyNews
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/daily-news.git
git push -u origin main
```

### 3. 配置 GitHub Secrets
1. 进入仓库 Settings > Secrets and variables > Actions
2. 添加 `WECOM_WEBHOOK_URL`，值为你的企业微信机器人 Webhook URL

### 4. 启用 GitHub Pages
1. 进入仓库 Settings > Pages
2. Source: Deploy from a branch
3. Branch: `gh-pages` / `/ (root)`
4. 保存

### 5. 手动触发测试
1. 进入仓库 Actions 页面
2. 选择 "Daily News Workflow"
3. 点击 "Run workflow"
4. 等待运行完成

## 常见问题

### Q: 为什么电脑不开机也能收到推送？
A: 使用 GitHub Actions 云端定时触发，不依赖本地电脑。

### Q: 如何避免重复新闻？
A: 使用 TF-IDF + SimHash 双重去重，并保留 30 天历史记录。

### Q: 如何自定义新闻来源？
A: 修改对应的 `scripts/fetch_*.py` 文件，添加或删除数据源。

### Q: 推送失败怎么办？
A: 检查 GitHub Secrets 中的 `WECOM_WEBHOOK_URL` 是否正确。

### Q: 如何调整去重阈值？
A: 修改 `scripts/deduplicator.py` 中的 `TITLE_THRESHOLD` 和 `CONTENT_THRESHOLD`。

## 维护说明

### 更新依赖
```bash
pip install -r requirements.txt --upgrade
```

### 清理历史记录
历史记录自动保留 30 天，无需手动清理。

### 查看日志
在 GitHub Actions 页面查看运行日志。

## 注意事项

1. **企业微信 Webhook URL** 需要妥善保管，不要泄露
2. **GitHub API 限制** 未认证请求每小时 60 次，建议配置 Personal Access Token
3. **网站反爬** 部分网站可能有反爬机制，需要调整抓取策略
4. **时区问题** GitHub Actions 使用 UTC 时间，北京时间 08:00 对应 UTC 00:00

## 下一步

- [ ] 创建 GitHub 仓库
- [ ] 推送代码
- [ ] 配置 GitHub Secrets
- [ ] 启用 GitHub Pages
- [ ] 测试运行
- [ ] 配置 WorkBuddy 本地自动化任务（可选）
