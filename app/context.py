"""模板上下文处理器 - 向所有模板注入用户信息"""
from fastapi import Request
from fastapi.templating import Jinja2Templates


def register_template_context(templates: Jinja2Templates) -> None:
    """注册模板全局变量，使所有模板可访问 current_user"""

    def get_current_user(request: Request):
        return getattr(request.state, "user", None)

    templates.env.globals["current_user"] = get_current_user
