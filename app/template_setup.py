"""共享模板引擎实例"""
from pathlib import Path
from fastapi import Request
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def get_current_user(request: Request):
    return getattr(request.state, "user", None)


templates.env.globals["current_user"] = get_current_user
