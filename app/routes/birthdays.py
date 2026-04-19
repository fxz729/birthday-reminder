from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path

from app.database import get_db
from app import crud
from app.schemas import BirthdayCreate, BirthdayUpdate, BirthdayResponse

router = APIRouter(prefix="/birthdays", tags=["birthdays"])

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@router.get("/", response_class=HTMLResponse)
async def list_birthdays(request: Request, db: Session = Depends(get_db)):
    """生日列表页"""
    birthdays = crud.get_birthdays(db)
    return templates.TemplateResponse(
        "birthday_list.html",
        {"request": request, "birthdays": birthdays}
    )


@router.get("/add", response_class=HTMLResponse)
async def add_birthday_form(request: Request):
    """添加生日表单页"""
    return templates.TemplateResponse(
        "birthday_form.html",
        {"request": request, "birthday": None, "errors": None}
    )


@router.post("/", response_class=HTMLResponse)
async def create_birthday(request: Request, db: Session = Depends(get_db)):
    """创建生日"""
    form_data = await request.form()

    try:
        birthday_data = BirthdayCreate(
            name=form_data["name"],
            birth_date=form_data["birth_date"],
            is_lunar=form_data.get("is_lunar") == "on",
            email=form_data["email"],
            gift_idea=form_data.get("gift_idea") or None,
            notes=form_data.get("notes") or None
        )
        crud.create_birthday(db, birthday_data)
        return RedirectResponse(url="/birthdays", status_code=303)
    except Exception as e:
        return templates.TemplateResponse(
            "birthday_form.html",
            {"request": request, "birthday": None, "errors": str(e)},
            status_code=400
        )


@router.get("/{birthday_id}/edit", response_class=HTMLResponse)
async def edit_birthday_form(request: Request, birthday_id: int, db: Session = Depends(get_db)):
    """编辑生日表单页"""
    birthday = crud.get_birthday(db, birthday_id)
    if not birthday:
        raise HTTPException(status_code=404, detail="生日不存在")
    return templates.TemplateResponse(
        "birthday_form.html",
        {"request": request, "birthday": birthday, "errors": None}
    )


@router.post("/{birthday_id}/edit", response_class=HTMLResponse)
async def update_birthday(request: Request, birthday_id: int, db: Session = Depends(get_db)):
    """更新生日"""
    birthday = crud.get_birthday(db, birthday_id)
    if not birthday:
        raise HTTPException(status_code=404, detail="生日不存在")

    form_data = await request.form()

    try:
        birthday_data = BirthdayUpdate(
            name=form_data["name"],
            birth_date=form_data["birth_date"],
            is_lunar=form_data.get("is_lunar") == "on",
            email=form_data["email"],
            gift_idea=form_data.get("gift_idea") or None,
            notes=form_data.get("notes") or None
        )
        crud.update_birthday(db, birthday_id, birthday_data)
        return RedirectResponse(url="/birthdays", status_code=303)
    except Exception as e:
        return templates.TemplateResponse(
            "birthday_form.html",
            {"request": request, "birthday": birthday, "errors": str(e)},
            status_code=400
        )


@router.post("/{birthday_id}/delete")
async def delete_birthday(birthday_id: int, db: Session = Depends(get_db)):
    """删除生日"""
    if not crud.delete_birthday(db, birthday_id):
        raise HTTPException(status_code=404, detail="生日不存在")
    return RedirectResponse(url="/birthdays", status_code=303)


@router.get("/api/", response_model=List[BirthdayResponse])
async def api_list_birthdays(db: Session = Depends(get_db)):
    """API: 获取所有生日"""
    return crud.get_birthdays(db)
