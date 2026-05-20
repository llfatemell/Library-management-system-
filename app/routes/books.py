from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

import json

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")
def load_books():
    with open("books.json", "r") as file:
        return json.load(file)

def save_books(books):

    with open("books.json", "w") as file:

        json.dump(
            books,
            file,
            indent=4
        )

@router.get("/landing")
def books_landing(
    request: Request,
    search: str = "",
    sort: str = "",
    page: int = 1
):

    books = load_books()

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

    per_page = 5

    total_books = len(books)

    total_pages = (
        total_books + per_page - 1
    ) // per_page

    start = (page - 1) * per_page

    end = start + per_page

    books = books[start:end]

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
@router.post("/")
def create_book(
    request: Request,
    isbn: str = Form(...),
    title: str = Form(...),
    author: str = Form(...),
    year: int = Form(...),
    borrowed: bool = Form(False),
    loaned_to: str = Form("")
):

    books = load_books()

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

        "borrowed": borrowed,

        "loaned_to": loaned_to

    }

    books.append(new_book)

    save_books(books)

    return RedirectResponse(
        url="/books/landing",
        status_code=303
    )
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

@router.post("/{isbn}")
def update_book(
    isbn: str,
    title: str = Form(...),
    author: str = Form(...),
    year: int = Form(...),
    borrowed: bool = Form(False),
    loaned_to: str = Form("")
):

    books = load_books()

    for book in books:

        if book["isbn"] == isbn:

            book["title"] = title

            book["author"] = author

            book["year"] = year

            book["borrowed"] = borrowed
            book["loaned_to"] = loaned_to

    save_books(books)

    return RedirectResponse(
        url="/books/landing",
        status_code=303
    )

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