# 🎂 生日定时提醒

一个简单的生日定时提醒系统，支持公历/农历日期，通过 QQ 邮箱自动发送提醒通知。

## 功能特性

- ✅ 公历/农历生日支持
- ✅ 多档提前提醒（30天、7天、3天、1天、当天）
- ✅ 自定义提醒时间和邮件模板
- ✅ Web 管理界面
- ✅ 定时自动检查并发送邮件

## 快速开始

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd birthday-reminder
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入 QQ 邮箱配置
```

### 4. 启动应用

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000

### 5. 配置 GitHub Actions (可选)

1. 在 GitHub 仓库设置中添加 Secrets:
   - `DATABASE_URL`: 数据库连接字符串
   - `MAIL_USERNAME`: QQ 邮箱
   - `MAIL_PASSWORD`: QQ 邮箱授权码
   - `MAIL_FROM`: 发件人邮箱

2. 注册自托管 Runner 并配置

## 开发

### 运行测试

```bash
pytest tests/ -v
```

### 项目结构

```
birthday-reminder/
├── app/
│   ├── main.py          # FastAPI 入口
│   ├── database.py      # 数据库配置
│   ├── models.py        # 数据模型
│   ├── schemas.py       # Pydantic schemas
│   ├── crud.py          # CRUD 操作
│   ├── routes/          # API 路由
│   ├── services/        # 核心服务
│   └── templates/        # 前端模板
├── scheduler/           # 定时检查器
├── tests/               # 测试
└── data/                # 数据目录
```

## 许可证

MIT
