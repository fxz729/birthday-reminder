from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import crud
from app.schemas import BirthdayCreate, BirthdayUpdate, BirthdayResponse
from app.middleware.auth import get_optional_user, get_current_user
from app.template_setup import templates
from app.models import User

router = APIRouter(prefix="/birthdays", tags=["birthdays"])


@router.get("/", response_class=HTMLResponse)
async def list_birthdays(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user),
):
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)
    birthdays = crud.get_birthdays(db, user_id=current_user.id)
    return templates.TemplateResponse(
        "birthday_list.html",
        {"request": request, "birthdays": birthdays, "user": current_user},
    )


@router.get("/add", response_class=HTMLResponse)
async def add_birthday_form(
    request: Request,
    current_user: User = Depends(get_optional_user),
):
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)
    return templates.TemplateResponse(
        "birthday_form.html",
        {"request": request, "birthday": None, "errors": None, "user": current_user},
    )


@router.post("/", response_class=HTMLResponse)
async def create_birthday(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user),
):
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)
    form_data = await request.form()

    try:
        birthday_data = BirthdayCreate(
            name=form_data["name"],
            birth_date=form_data["birth_date"],
            is_lunar=form_data.get("is_lunar") == "on",
            email=form_data["email"],
            gift_idea=form_data.get("gift_idea") or None,
            notes=form_data.get("notes") or None,
        )
        crud.create_birthday(db, birthday_data, user_id=current_user.id)
        return RedirectResponse(url="/birthdays", status_code=303)
    except Exception as e:
        return templates.TemplateResponse(
            "birthday_form.html",
            {"request": request, "birthday": None, "errors": str(e), "user": current_user},
            status_code=400,
        )


@router.get("/{birthday_id}/edit", response_class=HTMLResponse)
async def edit_birthday_form(
    request: Request,
    birthday_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user),
):
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)
    birthday = crud.get_birthday(db, birthday_id, user_id=current_user.id)
    if not birthday:
        raise HTTPException(status_code=404, detail="生日不存在")
    return templates.TemplateResponse(
        "birthday_form.html",
        {"request": request, "birthday": birthday, "errors": None, "user": current_user},
    )


@router.post("/{birthday_id}/edit", response_class=HTMLResponse)
async def update_birthday(
    request: Request,
    birthday_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user),
):
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)
    birthday = crud.get_birthday(db, birthday_id, user_id=current_user.id)
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
            notes=form_data.get("notes") or None,
        )
        crud.update_birthday(db, birthday_id, birthday_data, user_id=current_user.id)
        return RedirectResponse(url="/birthdays", status_code=303)
    except Exception as e:
        return templates.TemplateResponse(
            "birthday_form.html",
            {"request": request, "birthday": birthday, "errors": str(e), "user": current_user},
            status_code=400,
        )


@router.post("/{birthday_id}/delete")
async def delete_birthday(
    birthday_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user),
):
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)
    if not crud.delete_birthday(db, birthday_id, user_id=current_user.id):
        raise HTTPException(status_code=404, detail="生日不存在")
    return RedirectResponse(url="/birthdays", status_code=303)


@router.get("/api/", response_model=List[BirthdayResponse])
async def api_list_birthdays(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    search: str = "",
    type: str = "",
):
    birthdays = crud.get_birthdays(db, user_id=current_user.id)
    if search:
        birthdays = [b for b in birthdays if search.lower() in b.name.lower()]
    if type == "lunar":
        birthdays = [b for b in birthdays if b.is_lunar]
    elif type == "solar":
        birthdays = [b for b in birthdays if not b.is_lunar]
    return birthdays
