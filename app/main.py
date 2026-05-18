from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.routes import books

import json

app = FastAPI()

# اتصال فایل‌های استاتیک
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# اتصال templates
templates = Jinja2Templates(directory="app/templates")

app.include_router(
    books.router,
    prefix="/books"
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

    years = [book["year"] for book in books]

    oldest_book = min(years) if years else "N/A"
    newest_book = max(years) if years else "N/A"

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