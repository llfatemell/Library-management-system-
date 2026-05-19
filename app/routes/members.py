from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

import json

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


# خواندن اعضا
def load_members():

    with open("members.json", "r") as file:

        return json.load(file)


# ذخیره اعضا
def save_members(members):

    with open("members.json", "w") as file:

        json.dump(members, file, indent=4)


# تولید خودکار Member ID
def generate_member_id(members):

    if not members:

        return "M001"

    last_member = members[-1]

    last_id = last_member["member_id"]

    number = int(last_id[1:])

    new_number = number + 1

    return f"M{new_number:03d}"


# نمایش لیست اعضا
@router.get("/landing")
def members_landing(
    request: Request,
    search: str = "",
    sort: str = "",
    page: int = 1
):

    members = load_members()

    # SEARCH

    if search:

        members = [

            member for member in members

            if

            search.lower() in member["name"].lower()

            or

            search.lower() in member["email"].lower()

            or

            search.lower() in member["member_id"].lower()

        ]

    # SORT

    if sort == "name":

        members.sort(
            key=lambda x: x["name"]
        )

    elif sort == "email":

        members.sort(
            key=lambda x: x["email"]
        )

    # PAGINATION

    per_page = 5

    total_members = len(members)

    total_pages = (
        total_members + per_page - 1
    ) // per_page

    start = (page - 1) * per_page

    end = start + per_page

    members = members[start:end]

    # BASE URL

    base_url = (
        f"/members/landing?"
        f"search={search}&sort={sort}"
    )

    return templates.TemplateResponse(

        request=request,

        name="members_landing.html",

        context={

            "members": members,

            "search": search,

            "sort": sort,

            "page": page,

            "total_pages": total_pages,

            "base_url": base_url

        }

    )


# فرم افزودن عضو
@router.get("/add")
def add_member_form(request: Request):

    return templates.TemplateResponse(

        request=request,

        name="member_form.html",

        context={

            "member": None

        }

    )


# ذخیره عضو جدید
@router.post("/")
def create_member(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...)
):

    members = load_members()

    member_id = generate_member_id(members)

    new_member = {

        "member_id": member_id,

        "name": name,

        "email": email,

        "phone": phone

    }

    members.append(new_member)

    save_members(members)

    return RedirectResponse(
        url="/members/landing",
        status_code=303
    )


# فرم ویرایش عضو
@router.get("/edit/{member_id}")
def edit_member_form(
    request: Request,
    member_id: str
):

    members = load_members()

    member = next(

        (
            m for m in members
            if m["member_id"] == member_id
        ),

        None

    )

    return templates.TemplateResponse(

        request=request,

        name="member_form.html",

        context={

            "member": member

        }

    )


# ذخیره ویرایش عضو
@router.post("/{member_id}")
def update_member(
    member_id: str,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...)
):

    members = load_members()

    for member in members:

        if member["member_id"] == member_id:

            member["name"] = name

            member["email"] = email

            member["phone"] = phone

    save_members(members)

    return RedirectResponse(
        url="/members/landing",
        status_code=303
    )


# صفحه حذف عضو
@router.get("/delete/{member_id}")
def delete_member_page(
    request: Request,
    member_id: str
):

    members = load_members()

    member = next(

        (
            m for m in members
            if m["member_id"] == member_id
        ),None

    )

    return templates.TemplateResponse(

        request=request,

        name="member_delete.html",

        context={

            "member": member

        }

    )


# حذف نهایی عضو
@router.post("/delete/{member_id}")
def delete_member(member_id: str):

    members = load_members()

    members = [

        member for member in members

        if member["member_id"] != member_id

    ]

    save_members(members)

    return RedirectResponse(
        url="/members/landing",
        status_code=303
    )