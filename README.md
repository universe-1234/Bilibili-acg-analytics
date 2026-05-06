# B站ACG视频数据统计分析系统

## 技术架构

### 前端
- **Vue 3** (Composition API) + **Vite** 构建
- **Element Plus** UI 组件库
- **ECharts** 数据可视化图表
- **Pinia** 状态管理 + 持久化
- **Vue Router** 路由管理
- **TailwindCSS** 样式开发
- **Axios** HTTP 请求

### 后端
- **Python 3.8+** + **FastAPI**
- **SQLAlchemy** ORM
- **PyJWT** 身份认证
- **bcrypt** 密码加密
- **MySQL 8.0+** 主数据库
- **Redis 6.0+** 缓存

### 爬虫
- **Scrapy** 爬虫框架
- **Requests** HTTP 请求
- **Fake-UserAgent** UA 池
- **B站 API** 数据源

## 功能模块

| 模块 | 功能 |
|------|------|
| 用户系统 | 注册、登录、JWT 认证、个人信息 |
| 视频浏览 | 分页列表、搜索、分类筛选、多维排序 |
| 视频详情 | 信息展示、跳转B站播放、数据统计、相关推荐 |
| 评论系统 | 用户评论、评论列表、分页 |
| 用户收藏 | 收藏/取消收藏、收藏列表 |
| 数据看板 | 分类分布、热门排行、趋势分析、UP主排行、标签统计 |
| 可视化大屏 | 全屏数据大屏、核心指标、多维度图表、雷达图 |
| 数据爬取 | 自动爬取B站ACG频道800+视频数据 |

## 快速启动

### 1. 环境准备

- Node.js 18+
- Python 3.8+
- MySQL 8.0+
- Redis 6.0+ (可选)

### 2. 数据库初始化

```sql
CREATE DATABASE bilibili_acg CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

修改 `backend/.env` 中的数据库配置。

### 3. 后端启动

```bash
cd backend
pip install -r requirements.txt

# 生成模拟数据（800条视频 + 2000条评论）
python seed_data.py

# 启动后端服务 (http://localhost:8000)
python run.py
```

### 4. 爬虫启动（可选，需先启动后端）

```bash
cd backend
python crawler/run_crawler.py 800
```

### 5. 前端启动

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

### 6. 测试账号

- 用户名: `admin` 密码: `admin123`
- 用户名: `user1` 密码: `user123`

## API 接口

### 认证
- `POST /api/auth/register` - 注册
- `POST /api/auth/login` - 登录
- `GET /api/auth/me` - 当前用户信息

### 视频
- `GET /api/videos` - 视频列表（分页、搜索、筛选、排序）
- `GET /api/videos/categories` - 分类列表
- `GET /api/videos/{id}` - 视频详情
- `POST /api/videos/{id}/favorite` - 收藏/取消收藏

### 评论
- `GET /api/videos/{id}/comments` - 评论列表
- `POST /api/videos/{id}/comments` - 发表评论
- `GET /api/videos/{id}/comments/{cid}/replies` - 回复列表

### 数据看板
- `GET /api/dashboard/overview` - 概览统计
- `GET /api/dashboard/category-stats` - 分类统计
- `GET /api/dashboard/top-videos` - 热门视频
- `GET /api/dashboard/daily-trends` - 每日趋势
- `GET /api/dashboard/tag-cloud` - 标签云
- `GET /api/dashboard/author-ranking` - UP主排行
- `GET /api/dashboard/publish-trends` - 发布趋势
- `GET /api/dashboard/video-engagement` - 互动数据

### 收藏
- `GET /api/user/favorites` - 收藏列表

## 项目结构

```
bilibili-acg-analytics/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口
│   │   ├── config.py            # 配置管理
│   │   ├── database.py          # 数据库连接
│   │   ├── models/              # 数据模型
│   │   │   ├── user.py
│   │   │   ├── video.py
│   │   │   └── comment.py
│   │   ├── schemas/             # Pydantic 模型
│   │   ├── routers/             # API 路由
│   │   │   ├── auth.py
│   │   │   ├── videos.py
│   │   │   ├── comments.py
│   │   │   ├── dashboard.py
│   │   │   └── favorites.py
│   │   ├── services/            # 业务逻辑
│   │   └── middleware/          # 中间件
│   ├── crawler/                 # 爬虫模块
│   │   ├── bilibili_crawler/
│   │   │   ├── spiders/acg_spider.py
│   │   │   ├── items.py
│   │   │   ├── pipelines.py
│   │   │   ├── middlewares.py
│   │   │   └── settings.py
│   │   └── run_crawler.py
│   ├── seed_data.py             # 模拟数据生成
│   ├── run.py                   # 启动脚本
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── main.js              # Vue 入口
│       ├── App.vue              # 根组件
│       ├── router/index.js      # 路由配置
│       ├── stores/auth.js       # 认证状态
│       ├── api/index.js         # API 封装
│       └── views/               # 页面视图
│           ├── LayoutView.vue       # 主布局
│           ├── LoginView.vue        # 登录页
│           ├── RegisterView.vue     # 注册页
│           ├── HomeView.vue         # 视频列表首页
│           ├── VideoDetailView.vue  # 视频详情页
│           ├── DashboardView.vue    # 数据看板
│           ├── LargeScreenView.vue  # 可视化大屏
│           └── FavoritesView.vue    # 收藏页
└── README.md
```
