# 🎂 生日定时提醒

一个功能丰富的生日管理系统，支持公历/农历日期、多种通知方式、智能礼物推荐，通过 QQ 邮箱或 ServerChan 自动发送提醒通知。

## 功能特性

### 核心功能
- ✅ **公历/农历生日** - 支持阴阳历转换，闰月处理
- ✅ **多档提前提醒** - 30天、7天、3天、1天、当天
- ✅ **双重通知渠道** - Email 邮件 + ServerChan 微信推送
- ✅ **JWT 用户认证** - 安全令牌认证，数据隔离

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
- ✅ **个人资料管理** - 修改密码、更新邮箱
- ✅ **密码重置** - 邮箱验证重置密码

### 界面特性
- ✅ **暗色模式** - 支持明暗主题切换，持久化保存
- ✅ **响应式设计** - 桌面/平板/移动端自适应
- ✅ **实时搜索** - 客户端生日搜索过滤
- ✅ **自定义模态框** - 删除确认等交互组件

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

# ServerChan 配置（可选，用于微信推送）
SERVERCHAN_SCKEY=your_serverchan_key

# JWT 配置
SECRET_KEY=change-to-a-random-string
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24

# 应用配置
BASE_URL=http://localhost:8000
```

> **QQ 邮箱授权码获取**：QQ 邮箱 → 设置 → 账户 → POP3/IMAP/SMTP 服务 → 开启 → 获取授权码

### 4. 启动应用

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000

## 使用指南

### 1. 注册登录

1. 访问 `/auth/register` 注册账号
2. 访问 `/auth/login` 登录系统

### 2. 添加生日

1. 点击「添加新朋友」按钮
2. 填写姓名、生日日期、类型（公历/农历）、邮箱
3. 可选：礼物想法、备注
4. 点击保存

### 3. 配置提醒

1. 点击生日列表中的「提醒」按钮
2. 开关选择提醒时机：当天、提前1天、3天、7天、30天
3. 选择通知方式：📧 邮件 / 📱 ServerChan
4. 自定义邮件模板（可选）
5. 点击保存

### 4. 通知模板变量

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
| `{{lunar_festival}}` | 农历节日 | 中秋节 |
| `{{solar_term}}` | 节气 | 谷雨 |

## API 路由

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/auth/login` | 登录页 | - |
| POST | `/auth/login` | 处理登录 | - |
| GET | `/auth/register` | 注册页 | - |
| POST | `/auth/register` | 处理注册 | - |
| POST | `/auth/logout` | 登出 | - |
| GET | `/auth/dashboard` | 控制台 | ✅ |
| GET | `/auth/profile` | 个人设置 | ✅ |
| POST | `/auth/profile` | 更新设置 | ✅ |
| GET | `/auth/reset-password` | 重置密码页 | - |
| POST | `/auth/reset-password` | 发送重置邮件 | - |
| GET/POST | `/auth/reset-password/{token}` | 设置新密码 | - |
| GET | `/birthdays` | 生日列表 | ✅ |
| GET | `/birthdays/add` | 添加生日页 | ✅ |
| POST | `/birthdays` | 创建生日 | ✅ |
| GET | `/birthdays/{id}/edit` | 编辑生日页 | ✅ |
| POST | `/birthdays/{id}/edit` | 更新生日 | ✅ |
| POST | `/birthdays/{id}/delete` | 删除生日 | ✅ |
| GET | `/birthdays/api` | 生日 JSON API | ✅ |
| GET | `/birthdays/{id}/reminders` | 提醒配置页 | ✅ |
| POST | `/birthdays/{id}/reminders` | 保存提醒 | ✅ |
| POST | `/birthdays/{id}/reminders/test` | 测试提醒 | ✅ |
| GET | `/birthdays/api/{id}/reminders` | 提醒 JSON API | ✅ |

## 定时任务

### GitHub Actions（推荐）

每天北京时间 9:00 自动执行，需配置仓库 Secrets。

### 本地执行

```bash
python -m scheduler.birthday_checker
```

## 技术栈

- **后端**: FastAPI + SQLAlchemy + Pydantic + JWT
- **前端**: Jinja2 + Tailwind CSS + Alpine.js（CDN，无构建步骤）
- **数据库**: SQLite / PostgreSQL / MySQL
- **通知**: QQ 邮箱 SMTP + ServerChan
- **测试**: pytest (143 个测试用例)

## 项目结构

```
birthday-reminder/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── database.py          # 数据库配置
│   ├── models.py            # SQLAlchemy 模型
│   ├── schemas.py           # Pydantic 校验
│   ├── crud.py              # CRUD 操作
│   ├── logging_config.py    # 集中日志配置
│   ├── template_setup.py    # 共享模板引擎
│   ├── middleware/          # 中间件层
│   │   ├── auth.py          # JWT 认证依赖
│   │   ├── error_handler.py # 全局异常处理
│   │   └── rate_limit.py    # 速率限制
│   ├── routes/              # 路由层
│   │   ├── auth.py          # 认证/设置/重置密码
│   │   ├── birthdays.py     # 生日 CRUD
│   │   └── reminders.py     # 提醒配置
│   ├── services/            # 业务服务层
│   │   ├── auth.py          # JWT 签发/验证
│   │   ├── lunar.py         # 农历计算
│   │   ├── template.py      # 通知模板渲染
│   │   ├── notification/    # 通知工厂
│   │   ├── statistics.py    # 统计分析
│   │   ├── gift_recommender.py
│   │   ├── greeting_card.py
│   │   └── import_export.py
│   ├── static/              # 静态资源
│   │   ├── css/app.css      # 自定义样式
│   │   └── js/main.js       # 交互脚本
│   └── templates/           # Jinja2 模板
│       ├── base.html        # 基础布局
│       ├── login.html       # 登录（Tailwind）
│       ├── register.html    # 注册（含密码强度）
│       ├── dashboard.html   # 控制台（含统计）
│       ├── birthday_list.html
│       ├── birthday_form.html
│       ├── reminder_form.html
│       ├── profile.html
│       ├── reset_password.html
│       └── components/      # 可复用组件
│           ├── toast.html
│           ├── confirm_modal.html
│           └── empty_state.html
├── scheduler/               # 定时检查器
│   └── birthday_checker.py
├── tests/                   # 测试（143 个）
├── config.py                # 配置管理
└── requirements.txt
```

## 开发

```bash
# 运行所有测试
pytest tests/ -v

# 运行单个测试
pytest tests/test_auth.py -v

# 代码检查
python -m app.main  # 验证启动
```

## 许可证

MIT License
