from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.routes import books
from app.routes import members

import json

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(
    books.router,
    prefix="/books"
)

app.include_router(
    members.router,
    prefix="/members"
)


def load_books():
    with open("books.json", "r") as file:
        return json.load(file)


def load_members():
    with open("members.json", "r") as file:
        return json.load(file)


@app.get("/")
def dashboard(request: Request):

    books = load_books()
    members = load_members()

    total_books = len(books)

    borrowed_books = len(
        [book for book in books if book["borrowed"]]
    )

    available_books = total_books - borrowed_books

    total_members = len(members)

    oldest_book = min(
    books,
    key=lambda x: x["year"]
    )if books else None


    newest_book = max(
    books,
    key=lambda x: x["year"]
    )if books else None
    


    unique_authors = len(
        set(book["author"] for book in books)
    )

    return templates.TemplateResponse(
    request=request,
    name="landing.html",
    context={
        "total_books": total_books,
        "borrowed_books": borrowed_books,
        "available_books": available_books,
        "total_members": total_members,
        "oldest_book": oldest_book,
        "newest_book": newest_book,
        "unique_authors": unique_authors
    }
)