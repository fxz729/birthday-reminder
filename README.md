# 🎂 生日定时提醒

一个功能丰富的生日管理系统，支持公历/农历日期、多种通知方式、智能礼物推荐，通过 QQ 邮箱或 ServerChan 自动发送提醒通知。

## 功能特性

### 核心功能
- ✅ **公历/农历生日** - 支持阴阳历转换，闰月处理
- ✅ **多档提前提醒** - 30天、14天、7天、3天、1天、当天
- ✅ **双重通知渠道** - Email 邮件 + ServerChan 微信推送
- ✅ **用户认证系统** - 注册/登录/会话管理，数据隔离

### 智能功能
- ✅ **干支生肖信息** - 自动计算年柱、月柱、日柱、时柱
- ✅ **节日节气提醒** - 农历节日、阳历节日、二十四节气
- ✅ **星座自动识别** - 根据生日日期计算星座
- ✅ **礼物推荐** - 基于关系和年龄的智能礼物建议
- ✅ **电子贺卡生成** - 精美生日贺卡模板

### 管理功能
- ✅ **分类管理** - 按关系（家人/朋友/同事）分类
- ✅ **导入导出** - CSV/JSON 批量导入导出
- ✅ **数据统计** - 生日概览、即将到来、本月统计
- ✅ **日历同步** - 支持 iCal 格式导出

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
```

编辑 `.env` 文件，配置以下内容：

```env
# 数据库配置
DATABASE_URL=sqlite:///./data/birthdays.db

# QQ 邮箱配置（用于发送邮件）
MAIL_SERVER=smtp.qq.com
MAIL_PORT=587
MAIL_USERNAME=your_qq@qq.com
MAIL_PASSWORD=your_auth_code
MAIL_FROM=your_qq@qq.com
MAIL_STARTTLS=true
MAIL_SSL_TLS=false

# ServerChan 配置（可选，用于微信推送）
SERVERCHAN_SKEY=your_serverchan_sckey
```

> **QQ 邮箱授权码获取**：QQ 邮箱 → 设置 → 账户 → POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务 → 开启 SMTP 服务 → 获取授权码

### 4. 启动应用

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000

## 使用指南

### 1. 注册登录

首次使用需要注册账号：

1. 访问 http://localhost:8000/auth/register
2. 输入用户名、邮箱、密码
3. 点击注册并自动登录

### 2. 添加生日

1. 点击「添加新朋友」按钮
2. 填写信息：
   - **姓名** - 生日人姓名
   - **生日日期** - 选择日期
   - **生日类型** - 公历 ☀️ 或 农历 🌙
   - **提醒邮箱** - 接收提醒的邮箱
   - **礼物想法** - 记录礼物建议（可选）
   - **备注** - 其他备注（可选）
3. 点击「添加生日」保存

### 3. 配置提醒

为每个生日设置提醒通知：

1. 点击生日列表中的「提醒」按钮
2. 选择提醒时机（可多选）：
   - 当天生日
   - 提前 1 天
   - 提前 3 天
   - 提前 7 天
   - 提前 14 天
   - 提前 30 天
3. 选择通知方式：
   - 📧 邮件 - 通过 QQ 邮箱发送
   - 📱 ServerChan - 通过微信推送（需配置 SCKEY）
4. 自定义邮件模板（可选）
5. 点击保存

### 4. 通知模板变量

支持丰富的模板变量：

| 变量 | 说明 | 示例 |
|------|------|------|
| `{{name}}` | 生日人姓名 | 张三 |
| `{{date}}` | 今年生日日期 | 2024-05-15 |
| `{{age}}` | 年龄 | 30 |
| `{{days_left}}` | 距离生日天数 | 7 |
| `{{lunar_date}}` | 农历日期 | 农历四月初八 |
| `{{zodiac}}` | 生肖 | 虎 |
| `{{constellation}}` | 星座 | 金牛座 |
| `{{gz_year}}` | 干支纪年 | 甲子 |
| `{{gz_month}}` | 干支纪月 | 甲寅 |
| `{{gz_day}}` | 干支纪日 | 乙丑 |
| `{{solar_term}}` | 节气 | 谷雨 |
| `{{lunar_festival}}` | 农历节日 | 中秋节 |
| `{{solar_festival}}` | 阳历节日 | 元旦 |
| `{{gift_idea}}` | 礼物建议 | - |
| `{{notes}}` | 备注 | - |

### 5. 分类管理

在「控制台」中管理分类：

1. 创建分类（如：家人、朋友、同事）
2. 为分类选择颜色
3. 在生日详情中添加/移除分类

### 6. 礼物推荐

系统根据生日人信息智能推荐礼物：

- 基于关系（家人/朋友/恋人/同事）
- 基于年龄阶段（儿童/青年/中年/老年）
- 基于预算（平价/轻奢/高端）

### 7. 数据导入导出

**导出数据**：
1. 在控制台点击「导出数据」
2. 选择格式（CSV/JSON）
3. 下载文件

**导入数据**：
1. 点击「导入数据」
2. 上传 CSV 或 JSON 文件
3. 确认导入预览
4. 完成导入

### 8. 统计报表

在「控制台」查看：

- **生日概览** - 总数、分类统计
- **即将到来** - 最近 7 天/30 天的生日
- **本月统计** - 本月生日数量

## 定时任务配置

### GitHub Actions（推荐）

1. 在 GitHub 仓库 Settings → Secrets 添加：
   - `DATABASE_URL`
   - `MAIL_USERNAME`
   - `MAIL_PASSWORD`
   - `MAIL_FROM`
   - `SERVERCHAN_SKEY`（可选）

2. 配置自托管 Runner 或使用 GitHub 托管

3. 自动触发时间：每天北京时间 9:00

### 本地定时任务

使用系统 cron 或 Windows 任务计划程序：

```bash
# 每天 9:00 执行
python -m scheduler.birthday_checker
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 首页 |
| GET | `/auth/login` | 登录页 |
| POST | `/auth/login` | 处理登录 |
| GET | `/auth/register` | 注册页 |
| POST | `/auth/register` | 处理注册 |
| POST | `/auth/logout` | 登出 |
| GET | `/auth/dashboard` | 用户控制台 |
| GET | `/birthdays` | 生日列表 |
| GET | `/birthdays/add` | 添加生日页 |
| POST | `/birthdays/add` | 处理添加 |
| GET | `/birthdays/{id}/edit` | 编辑生日页 |
| POST | `/birthdays/{id}/edit` | 处理编辑 |
| POST | `/birthdays/{id}/delete` | 删除生日 |
| GET | `/birthdays/{id}/reminders` | 提醒配置页 |
| POST | `/birthdays/{id}/reminders` | 保存提醒配置 |
| GET | `/export` | 导出数据 |
| POST | `/import` | 导入数据 |

## 开发

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行单个测试文件
pytest tests/test_crud.py -v

# 运行单个测试函数
pytest tests/test_lunar.py::test_calculate_age -v

# 查看测试覆盖率
pytest tests/ --cov=app --cov-report=html
```

### 项目结构

```
birthday-reminder/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── database.py          # 数据库配置
│   ├── models.py            # SQLAlchemy 模型
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # 数据库 CRUD 操作
│   ├── routes/              # 路由层
│   │   ├── auth.py          # 用户认证
│   │   ├── birthdays.py     # 生日管理
│   │   └── reminders.py     # 提醒配置
│   ├── services/            # 服务层
│   │   ├── lunar.py         # 农历计算
│   │   ├── template.py      # 模板渲染
│   │   ├── email.py         # 邮件发送
│   │   ├── notification/    # 通知工厂
│   │   ├── gift_recommender.py  # 礼物推荐
│   │   ├── greeting_card.py     # 贺卡生成
│   │   ├── import_export.py     # 导入导出
│   │   └── statistics.py        # 统计分析
│   └── templates/           # Jinja2 模板
├── scheduler/               # 定时检查器
│   └── birthday_checker.py
├── tests/                   # 测试文件
├── data/                    # 数据目录
├── config.py               # 配置管理
└── requirements.txt         # 依赖列表
```

## 技术栈

- **后端**：FastAPI + SQLAlchemy + Pydantic
- **前端**：Jinja2 模板 + 原生 CSS/JS
- **数据库**：SQLite（默认）/ PostgreSQL/MySQL
- **定时任务**：APScheduler + GitHub Actions
- **通知**：QQ 邮箱 SMTP + ServerChan

## 许可证

MIT License
