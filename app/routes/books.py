from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

import json

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


# خواندن کتاب‌ها
def load_books():

    with open("books.json", "r") as file:

        return json.load(file)


# ذخیره کتاب‌ها
def save_books(books):

    with open("books.json", "w") as file:

        json.dump(books, file, indent=4)


# نمایش لیست کتاب‌ها + سرچ + مرتب‌سازی + صفحه‌بندی
@router.get("/landing")
def books_landing(
    request: Request,
    search: str = "",
    sort: str = "",
    page: int = 1
):

    books = load_books()

    # SEARCH

    if search:

        books = [

            book for book in books

            if

            search.lower() in book["title"].lower()

            or

            search.lower() in book["author"].lower()

            or

            search.lower() in book["isbn"].lower()

        ]

    # SORT

    if sort == "title":

        books.sort(
            key=lambda x: x["title"]
        )

    elif sort == "author":

        books.sort(
            key=lambda x: x["author"]
        )

    elif sort == "year":

        books.sort(
            key=lambda x: x["year"]
        )

    # PAGINATION

    per_page = 5

    total_books = len(books)

    total_pages = (
        total_books + per_page - 1
    ) // per_page

    start = (page - 1) * per_page

    end = start + per_page

    books = books[start:end]

    # BASE URL

    base_url = (
        f"/books/landing?"
        f"search={search}&sort={sort}"
    )

    return templates.TemplateResponse(

        request=request,

        name="books_landing.html",

        context={

            "books": books,

            "search": search,

            "sort": sort,

            "page": page,

            "total_pages": total_pages,

            "base_url": base_url

        }

    )


# فرم افزودن کتاب
@router.get("/add")
def add_book_form(request: Request):

    return templates.TemplateResponse(

        request=request,

        name="book_form.html",

        context={

            "book": None,
            "error": None

        }

    )


# ذخیره کتاب جدید
@router.post("/")
def create_book(
    request: Request,
    isbn: str = Form(...),
    title: str = Form(...),
    author: str = Form(...),
    year: int = Form(...)
):

    books = load_books()

    # بررسی تکراری نبودن ISBN

    for book in books:

        if book["isbn"] == isbn:

            return templates.TemplateResponse(

                request=request,

                name="book_form.html",

                context={

                    "book": None,

                    "error": "ISBN already exists!"

                }

            )

    new_book = {

        "isbn": isbn,

        "title": title,

        "author": author,

        "year": year,

        "borrowed": False

    }

    books.append(new_book)

    save_books(books)

    return RedirectResponse(
        url="/books/landing",
        status_code=303
    )


# فرم ویرایش کتاب
@router.get("/edit/{isbn}")
def edit_book_form(
    request: Request,
    isbn: str
):

    books = load_books()

    book = next(

        (
            b for b in books
            if b["isbn"] == isbn
        ),

        None

    )

    return templates.TemplateResponse(

        request=request,

        name="book_form.html",

        context={

            "book": book,
            "error": None

        }

    )


# ذخیره ویرایش کتاب
@router.post("/{isbn}")
def update_book(
    isbn: str,
    title: str = Form(...),
    author: str = Form(...),
    year: int = Form(...),
    borrowed: bool = Form(False)
):

    books = load_books()

    for book in books:

        if book["isbn"] == isbn:

            book["title"] = title

            book["author"] = author

            book["year"] = year

            book["borrowed"] = borrowed

    save_books(books)

    return RedirectResponse(
        url="/books/landing",
        status_code=303
    )


# صفحه حذف کتاب
@router.get("/delete/{isbn}")
def delete_book_page(
    request: Request,
    isbn: str
):

    books = load_books()

    book = next(

        (
            b for b in books
            if b["isbn"] == isbn
        ),

        None

    )

    return templates.TemplateResponse(

        request=request,

        name="book_delete.html",

        context={

            "book": book

        }

    )


# حذف نهایی کتاب
@router.post("/delete/{isbn}")
def delete_book(isbn: str):

    books = load_books()

    books = [

        book for book in books

        if book["isbn"] != isbn

    ]

    save_books(books)

    return RedirectResponse(
        url="/books/landing",
        status_code=303
    )