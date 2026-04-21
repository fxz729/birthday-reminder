# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working on code in this repository.

## 项目概述

生日定时提醒系统，支持公历/农历生日、多档提醒、Web 管理界面、邮件和 ServerChan 推送通知。

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 运行所有测试
pytest tests/ -v

# 运行单个测试文件
pytest tests/test_crud.py -v

# 运行单个测试函数
pytest tests/test_lunar.py::test_calculate_age -v

# 运行定时检查器
python -m scheduler.birthday_checker
```

## 架构概览

### 三层架构

```
routes/ (路由层) → services/ (服务层) → models.py (数据层)
```

- **路由层** (`app/routes/`): 处理 HTTP 请求，返回 Jinja2 模板渲染的 HTML
- **服务层** (`app/services/`): 核心业务逻辑（农历转换、模板渲染、通知发送）
- **数据层** (`app/models.py`): SQLAlchemy ORM 模型定义

### 核心模块

| 模块 | 职责 |
|------|------|
| `app/models.py` | User、Birthday 和 Reminder 模型定义 |
| `app/crud.py` | 数据库 CRUD 操作（含用户数据隔离） |
| `app/routes/auth.py` | 用户认证路由（登录/注册/登出） |
| `app/services/lunar.py` | 农历转换、干支/生肖/节气计算 |
| `app/services/notification/` | 通知发送器工厂模式 |
| `scheduler/birthday_checker.py` | 定时检查生日并发送通知 |

### 数据模型关系

```
User (1) ───< Birthday (1) ───< Reminder (N)
```

- 删除 Birthday 会级联删除关联的 Reminder
- Birthday 属于 User，数据按 user_id 隔离

### 用户认证

- Session + Cookie 认证
- 密码使用 bcrypt 加密
- 路由前缀: `/auth/`
  - `GET /auth/login` - 登录页
  - `POST /auth/login` - 处理登录
  - `GET /auth/register` - 注册页
  - `POST /auth/register` - 处理注册
  - `POST /auth/logout` - 登出
  - `GET /auth/dashboard` - 用户主界面

### 通知扩展模式

新增通知渠道（如钉钉、企业微信）：
1. 在 `app/services/notification/` 创建新的 sender 文件
2. 继承 `NotificationBase` 抽象类
3. 在 `NotificationFactory.create()` 中注册新类型
4. `notification_type` 字段可选值会自动扩展

## 配置管理

使用 `pydantic-settings`，配置通过 `.env` 文件读取：
- 数据库连接
- QQ 邮箱 SMTP 配置
- ServerChan 推送密钥

## 定时任务

通过 GitHub Actions 触发 `.github/workflows/check_birthdays.yml`：
- 每天北京时间 9:00 执行
- 或手动 `workflow_dispatch` 触发
- 运行 `python -m scheduler.birthday_checker`

## 模板变量

通知模板支持的变量：
- 基础: `name`, `date`, `age`, `days_left`
- 农历: `lunar_date`, `lunar_month`, `lunar_day`
- 干支: `gz_year`, `gz_month`, `gz_day`, `gz_hour`
- 生肖/星座: `zodiac`, `constellation`
- 节日/节气: `lunar_festival`, `solar_festival`, `solar_term`
