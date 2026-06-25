# Daily News - 每日新鲜事自动化抓取

每日自动抓取 GitHub 热门项目、创业投资新闻、小成本创业机会和游戏设计灵感，并推送到企业微信。

## 功能模块

| 模块 | 数量 | 数据源 |
|------|------|--------|
| GitHub 热门项目 | 10 个 | GitHub Trending API |
| 创业投资新闻 | 10 条 | 36氪、IT桔子、创业邦、投资界 |
| 小成本创业机会 | 10 条 | 36氪、知乎、小红书、IndieHackers |
| 游戏设计灵感 | 10 条 | GameDev.net、Gamasutra、触乐、游研社 |

## 技术特性

- **智能去重**：TF-IDF + 余弦相似度（标题）+ SimHash（内容）
- **相关性排序**：按时间、来源、关键词权重排序
- **历史记录**：保留 30 天历史，避免重复推送
- **自动推送**：企业微信 Webhook 推送
- **GitHub Pages**：自动生成 HTML 报告

## 快速开始

### 1. 配置 GitHub Secrets

在仓库 Settings > Secrets and variables > Actions 中添加：

| Secret 名称 | 说明 |
|-------------|------|
| `WECOM_WEBHOOK_URL` | 企业微信机器人 Webhook URL |

### 2. 启用 GitHub Pages

在仓库 Settings > Pages 中：
- Source: Deploy from a branch
- Branch: `gh-pages` / `/ (root)`

### 3. 手动触发

在 Actions 页面选择 "Daily News Workflow"，点击 "Run workflow"。

## 项目结构

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
│   └── utils.py                    # 工具函数
├── data/
│   ├── history/
│   │   └── news_history.json       # 历史记录（30天）
│   └── YYYY-MM-DD/                 # 每日报告
│       ├── github-trending.md
│       ├── startup-news.md
│       ├── startup-opportunities.md
│       ├── game-design.md
│       └── summary.md
├── index.html                      # GitHub Pages 主页
├── requirements.txt                # Python 依赖
└── README.md                       # 项目说明
```

## 工作流程

```
每日 08:00 (北京时间)
    │
    ▼
GitHub Actions 定时触发
    │
    ▼
抓取新闻 (4个模块 × 10条)
    │
    ▼
去重处理 (标题 + 内容 + 历史)
    │
    ▼
相关性排序
    │
    ▼
生成报告 (Markdown + HTML)
    │
    ▼
部署到 GitHub Pages
    │
    ▼
推送企业微信通知
```

## 配置说明

### 去重阈值

在 `scripts/deduplicator.py` 中调整：

```python
# 标题去重阈值（0.7 = 70% 相似度）
TITLE_THRESHOLD = 0.7

# 内容去重阈值（汉明距离 <= 3）
CONTENT_THRESHOLD = 3
```

### 推送时间

在 `.github/workflows/daily-news.yml` 中调整：

```yaml
schedule:
  # 北京时间 08:00 (UTC 00:00)
  - cron: '0 0 * * *'
```

## 常见问题

**Q: 为什么电脑不开机也能收到推送？**
A: 使用 GitHub Actions 云端定时触发，不依赖本地电脑。

**Q: 如何避免重复新闻？**
A: 使用 TF-IDF + SimHash 双重去重，并保留 30 天历史记录。

**Q: 如何自定义新闻来源？**
A: 修改对应的 `scripts/fetch_*.py` 文件，添加或删除数据源。

**Q: 推送失败怎么办？**
A: 检查 GitHub Secrets 中的 `WECOM_WEBHOOK_URL` 是否正确。

## 许可证

MIT License
