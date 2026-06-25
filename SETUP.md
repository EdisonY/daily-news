# Daily News - 每日新鲜事自动化抓取系统

## 项目概述

这是一个基于 GitHub Actions 的每日新闻自动化抓取系统，包含四个模块：

1. **GitHub 热门项目** - 昨日新增 star 最多的 10 个项目
2. **创业投资新闻** - 创业投资领域最新 10 条新闻
3. **小成本创业机会** - 低成本创业相关 10 条内容
4. **游戏设计灵感** - 游戏设计相关内容 10 条（侧重玩法创新）

## 核心特性

- **智能去重**：TF-IDF + SimHash 双重去重，避免重复推送
- **相关性排序**：按时间、来源、关键词权重排序
- **自动推送**：企业微信机器人 Webhook 推送
- **GitHub Pages**：自动生成 HTML 报告
- **历史记录**：保留 30 天历史，避免重复

## 快速开始

### 1. 创建 GitHub 仓库

在 GitHub 上创建新仓库：`daily-news`

### 2. 推送代码

```bash
cd F:\DailyNews
git push -u origin main
```

### 3. 配置 GitHub Secrets

在仓库 Settings > Secrets and variables > Actions 中添加：

| Secret 名称 | 说明 |
|-------------|------|
| `WECOM_WEBHOOK_URL` | 企业微信机器人 Webhook URL |

### 4. 启用 GitHub Pages

在仓库 Settings > Pages 中：
- Source: Deploy from a branch
- Branch: `gh-pages` / `/ (root)`

### 5. 手动触发测试

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
│   ├── generate_index.py           # 生成首页
│   ├── main.py                     # 主脚本
│   └── utils.py                    # 工具函数
├── data/
│   ├── history/
│   │   └── news_history.json       # 历史记录（30天）
│   └── YYYY-MM-DD/                 # 每日报告
├── requirements.txt                # Python 依赖
├── README.md                       # 项目说明
└── CONFIG.md                       # 配置说明
```

## 技术架构

```
触发层 (GitHub Actions)
    │
    ▼
数据抓取层 (Python 脚本)
    │
    ▼
去重处理层 (TF-IDF + SimHash)
    │
    ▼
报告生成层 (Markdown + HTML)
    │
    ▼
存储层 (GitHub Pages)
    │
    ▼
推送层 (企业微信 Webhook)
```

## 去重机制

### 标题去重
- 使用 TF-IDF 向量化
- 计算余弦相似度
- 阈值：0.7（70% 相似度）

### 内容去重
- 使用 SimHash 算法
- 计算汉明距离
- 阈值：3

### 历史记录去重
- 保留 30 天历史
- 使用 SimHash 对比
- 避免重复推送

## 推送格式

```markdown
# 📰 每日新鲜事 - 2026-06-25

今日共收集 **40** 条内容

---

## 🔥 GitHub 热门项目
1. [project-name](url) - ⭐ 1.2K stars
2. [project-name](url) - ⭐ 800 stars
...

## 💼 创业投资新闻
1. [新闻标题](url)
2. [新闻标题](url)
...

## 💰 小成本创业机会
1. [机会标题](url)
2. [机会标题](url)
...

## 🎮 游戏设计灵感
1. 🎮 [设计文章](url)
2. 🎨 [美术风格](url)
...

---

📊 [查看完整报告](https://edisony.github.io/daily-news/2026-06-25/)
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

## 下一步

1. 在 GitHub 上创建 `daily-news` 仓库
2. 推送代码到仓库
3. 配置 `WECOM_WEBHOOK_URL` Secret
4. 启用 GitHub Pages
5. 手动触发测试
6. 等待每日自动执行

## 许可证

MIT License
