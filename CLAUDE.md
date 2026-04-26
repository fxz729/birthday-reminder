# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working on code in this repository.

## 项目概述

生日定时提醒系统，支持公历/农历生日、多档提醒、Web 管理界面、邮件和 ServerChan 推送通知。前端使用 Tailwind CSS + Alpine.js（CDN，无构建步骤），支持暗色模式和响应式设计。

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 运行所有测试（143 个）
pytest tests/ -v

# 运行单个测试文件
pytest tests/test_auth.py -v

# 运行单个测试函数
pytest tests/test_lunar.py::test_calculate_age -v

# 运行定时检查器
python -m scheduler.birthday_checker
```

## 架构概览

### 四层架构

```
middleware/ (中间件) → routes/ (路由层) → services/ (服务层) → models.py (数据层)
```

### 核心模块

| 模块 | 职责 |
|------|------|
| `app/models.py` | User、Birthday、Reminder、NotificationLog 模型 |
| `app/crud.py` | 数据库 CRUD 操作（含用户数据隔离） |
| `app/middleware/auth.py` | JWT 认证依赖（get_current_user / get_optional_user） |
| `app/middleware/rate_limit.py` | 基于 IP 的请求频率限制 |
| `app/middleware/error_handler.py` | 全局异常处理（区分 API/页面请求） |
| `app/services/auth.py` | JWT 签发/验证 + 密码哈希 |
| `app/template_setup.py` | 共享 Jinja2 模板引擎实例（含 current_user 全局函数） |
| `app/logging_config.py` | 集中日志配置（控制台 + 文件） |
| `app/routes/auth.py` | 用户认证 + 个人设置 + 密码重置 |
| `app/services/lunar.py` | 农历转换、干支/生肖/节气计算 |
| `app/services/notification/` | 通知发送器工厂模式 |
| `app/static/js/main.js` | 暗色模式、Toast、模态框、密码强度 |
| `app/static/css/app.css` | 粒子动画、渐变、毛玻璃等自定义样式 |
| `scheduler/birthday_checker.py` | 定时检查生日并发送通知 |

### 用户认证

- JWT 令牌认证（PyJWT + `SECRET_KEY`）
- 令牌通过 `session_token` cookie 传递，httponly
- 密码使用 bcrypt(passlib) 加密
- 两个快速依赖项:
  - `get_current_user` — 必需认证（API 端点返回 401）
  - `get_optional_user` — 可选认证（页面路由重定向到登录）
- `UserContextMiddleware` 将用户信息注入 `request.state.user`（仅解码 JWT，无需 DB）
- 模板中通过 `current_user(request)` 获取用户信息

### 路由端点

| 路由 | 认证 | 说明 |
|------|------|------|
| `GET/POST /auth/login` | - | 登录 |
| `GET/POST /auth/register` | - | 注册 |
| `POST /auth/logout` | - | 登出 |
| `GET /auth/dashboard` | ✅ | 控制台（含统计数据） |
| `GET/POST /auth/profile` | ✅ | 个人设置 |
| `GET/POST /auth/reset-password` | - | 密码重置 |
| `GET/POST /auth/reset-password/{token}` | - | 设置新密码 |
| `GET /birthdays` | ✅ | 生日列表 |
| `GET/POST /birthdays/add` | ✅ | 添加生日 |
| `GET/POST /birthdays/{id}/edit` | ✅ | 编辑生日 |
| `POST /birthdays/{id}/delete` | ✅ | 删除生日 |
| `GET /birthdays/api/` | ✅ | 生日 JSON API（支持 ?search=&type=） |
| `GET/POST /birthdays/{id}/reminders` | ✅ | 提醒配置 |
| `POST /birthdays/{id}/reminders/test` | ✅ | 测试提醒发送 |
| `GET /birthdays/api/{id}/reminders` | ✅ | 提醒 JSON API |

### 数据模型关系

```
User (1) ───< Birthday (1) ───< Reminder (N)
  │            │
  │            +──< NotificationLog
  +──< Category (M) ──< birthday_categories >── Birthday
```

- NotificationLog 记录每次通知发送历史（user_id 关联用户）

### 前端设计

- **Tailwind CSS**（Play CDN）— 实用优先的样式框架
- **Alpine.js**（CDN）— 轻量交互（表单验证、搜索、暗色切换、折叠面板）
- **Google Fonts**: Cormorant Garamond（标题）+ Quicksand（正文）+ Noto Sans SC（中文字体）
- **Lucide Icons**（CDN）— SVG 图标替代所有 emoji
- **canvas-confetti**（CDN）— 页面加载、添加生日时的庆祝彩纸效果
- **暗色模式**: `class="dark"` 策略 + localStorage 持久化
- **配色**: 珊瑚红(#FF6B6B)、蜜桃(#FFA07A)、香槟金(#FFD700)、玫瑰红(#FF4D6D)、青色(#3EC1D3)、紫色(#6C5CE7)
- **设计主题**: "Golden Hour Celebration" — 温暖金色夕阳氛围，毛玻璃卡片，装饰性粒子背景
- 无构建步骤，`pip install` 即可运行

### 通知扩展模式

新增通知渠道（如钉钉、企业微信）：
1. 在 `app/services/notification/` 创建新的 sender 文件
2. 继承 `NotificationBase` 抽象类
3. 在 `NotificationFactory.create()` 中注册新类型

## 配置管理

`config.py` 使用 `pydantic-settings`，通过 `.env` 文件读取：
- 数据库连接
- QQ 邮箱 SMTP 配置
- ServerChan 推送密钥
- JWT 密钥和算法
- CORS 允许来源

## 定时任务

通过 GitHub Actions 触发 `.github/workflows/check_birthdays.yml`：
- 每天北京时间 9:00 执行
- 运行 `python -m scheduler.birthday_checker`

## 服务器部署

### 百度云 BCC 服务器

| 项目 | 值 |
|------|-----|
| 公网 IP | 106.12.70.228 |
| SSH 用户 | root |
| SSH 密钥路径 | `D:\HuaweiMoveData\Users\11075\Desktop\个人开发\生日定时提醒\cc-k-jFxZbLqu.txt` |

### 部署命令

```bash
# 连接服务器
ssh -i "D:\HuaweiMoveData\Users\11075\Desktop\个人开发\生日定时提醒\cc-k-jFxZbLqu.txt" root@106.12.70.228

# 在服务器上执行
cd /root/birthday-reminder
git pull origin master
pip3 install --break-system-packages -r requirements.txt

# 重启服务（先杀旧进程，再启动新进程）
pkill -f "uvicorn app.main"
nohup uvicorn app.main:app --host 0.0.0.0 --port 80 > /var/log/birthday-reminder.log 2>&1 &
```

### 当前线上状态

- 服务目录：`/root/birthday-reminder`
- 当前监听端口：`80`
- 当前公网访问地址：`http://106.12.70.228/birthdays/`
- 如用户说"连接服务器""去服务器上操作""在线上机器执行"，默认指这台百度云服务器

---

## 模板变量

通知模板支持的变量：
- 基础: `name`, `date`, `age`, `days_left`
- 农历: `lunar_date`, `lunar_month`, `lunar_day`
- 干支: `gz_year`, `gz_month`, `gz_day`, `gz_hour`
- 生肖/星座: `zodiac`, `constellation`
- 节日/节气: `lunar_festival`, `solar_festival`, `solar_term`
