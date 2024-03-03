from django.shortcuts import render, redirect
from .models import Book, BookRating, User
from .forms import BookRatingForm
import requests


class LocalBook:
    def __init__(self, googleID, title, author, publishDate, pages, cover, description):
        self.googleID = googleID
        self.title = title
        self.author = author
        self.pubDate = publishDate
        self.pages = pages
        self.cover = cover
        self.description = description

        self.exists = Book.objects.filter(googleID=googleID).exists()

class Cache:
    def __init__(self):
        self.books = {}

    def add_book(self, book):
        self.books[book.googleID] = book
    
    def get_book(self, id):
        return self.books[id]
    
    def get_ids(self):
        return self.books.keys()


CACHE = Cache()

def get_other_user(user):
    if user == "Tom":
        return "Frances"
    return "Tom"

def get_books_from_google(query):
    url =f"https://www.googleapis.com/books/v1/volumes?q={query}&langRestrict=en" 

    r = requests.get(url)
    data = r.json()
    results = []
    for i in data["items"]:
        try:
            imagefile = i["volumeInfo"]["imageLinks"]["thumbnail"]
        except:
            imagefile = ""

        try: 
            author = i["volumeInfo"]["authors"][0]
        except:
            author = ""

        try:
            description = i["volumeInfo"]["description"]
        except:
            description = None

        try:
            pages = int(i["volumeInfo"]["pageCount"])
        except:
            pages = None

        try:
            pubDate = i["volumeInfo"]["publishedDate"]
        except:
            pubDate = None
        b = LocalBook(googleID=i["id"],
                            title=i["volumeInfo"]["title"],
                            author=author,
                            publishDate=pubDate,
                            pages=pages,
                            cover=imagefile,
                            description=description)
        results.append(b)
    return results

def get_book_from_google(id):
    if id in CACHE.get_ids():
        return CACHE.get_book(id)

    url =f"https://www.googleapis.com/books/v1/volumes/{id}" 

    r = requests.get(url)
    data = r.json()
    try:
        imagefile = data["volumeInfo"]["imageLinks"]["thumbnail"]
    except:
        imagefile = ""

    try: 
        author = data["volumeInfo"]["authors"][0]
    except:
        author = ""

    try:
        description = data["volumeInfo"]["description"]
    except:
        description = None

    try:
        pages = int(data["volumeInfo"]["pageCount"])
    except:
        pages = None

    try:
        pubDate = data["volumeInfo"]["publishedDate"]
    except:
        pubDate = None
    b = Book(googleID=data["id"],
                        title=data["volumeInfo"]["title"],
                        author=author,
                        publishDate=pubDate,
                        pages=pages,
                        cover=imagefile,
                        description=description)
    CACHE.add_book(b)
    return b

def home(request):
    tom_books = BookRating.objects.filter(user__name="Tom")
    frances_books = BookRating.objects.filter(user__name="Frances")
    tom_read = [i for i in tom_books if i.readDate is not None]
    frances_read = [i for i in frances_books if i.readDate is not None]
    tom_recent = sorted(tom_read, key=lambda x: x.readDate, reverse=True)
    frances_recent = sorted(frances_read, key=lambda x: x.readDate, reverse=True)
    tom_top_rated = sorted(tom_read, key=lambda x: x.rating, reverse=True)
    frances_top_rated = sorted(frances_read, key=lambda x: x.rating, reverse=True)

    class MixedBook:
        def __init__(self, book, tom_stars, frances_stars, combined_rating):
            self.book = book
            self.tom_stars = tom_stars
            self.frances_stars = frances_stars
            self.combined_rating = combined_rating

    mixed_rankings = {}
    for b in tom_read:
        mixed_rankings[b.book.googleID] = MixedBook(book=b.book, 
                                           tom_stars=b.stars,
                                           frances_stars="0.0_stars.html",
                                           combined_rating=b.rating)
    
    for b in frances_read:
        if b.book.googleID in mixed_rankings.keys():
            mixed_rankings[b.book.googleID].combined_rating += b.rating
            mixed_rankings[b.book.googleID].frances_stars = b.stars
        else:
            mixed_rankings[b.book.googleID] = MixedBook(book=b.book,
                                               tom_stars="0.0_stars.html",
                                               frances_stars=b.stars,
                                               combined_rating=b.rating)
    mixed_ranking_books = sorted(mixed_rankings, key=lambda x: mixed_rankings[x].combined_rating, reverse=True)
    detailed_mixed_rankings = [mixed_rankings[i] for i in mixed_ranking_books]

    context = {
        "tom_recent": tom_recent[:3],
        "frances_recent": frances_recent[:3],
        "tom_top_rated": tom_top_rated[:3],
        "frances_top_rated": frances_top_rated[:3],
        "mixed_rankings": detailed_mixed_rankings[:9]
        }
    return render(request, "books/home.html", context)

def user(request):
    user = request.GET.get("name")
    book_ratings = BookRating.objects.filter(user__name=user)
    books = [i for i in book_ratings if i.readDate is not None]
    books = sorted(books, key=lambda x: x.readDate, reverse=True)
    my_books = [i.book for i in books]

    other_user = get_other_user(user)
    other_user_book_ratings = BookRating.objects.filter(user__name=other_user)

    to_read = [i for i in other_user_book_ratings if i.book not in my_books]
    to_read = sorted(to_read, key=lambda x: x.rating, reverse=True)

    context = {
        "user": user,
        "books": books,
        "to_read": to_read
        }
    return render(request, "books/user.html", context)

def search(request):

    return render(request, "books/search.html")

def results(request):
    query = request.GET.get("q")
    if query == "":
        return redirect("/books/search")
    results = get_books_from_google(query)
    context = {
        "results" : results
    }
    return render(request, "books/results.html", context)

def book(request):
    id = request.GET.get("id")
    book = Book.objects.get(googleID=id)

    tom_book = BookRating.objects.get(book__googleID=id, user__name="Tom")
    frances_book = BookRating.objects.get(book__googleID=id, user__name="Frances")

    context = {
        "book": book,
        "tom_book": tom_book,
        "frances_book": frances_book
    }
    return render(request, "books/book.html", context)

def add(request):
    id = request.GET.get("id")
    try:
        Book.objects.get(googleID=id)
    except:
        b = get_book_from_google(id)
        b.save()
        for u in User.objects.all():
            rating = BookRating(book=b,
                                user=u,
                                rating=None,
                                stars="0.0_stars.html",
                                readDate=None)
            rating.save()
    return redirect(f"/books/book?id={id}")

def edit(request):
    id = request.GET.get("id")
    b = Book.objects.get(googleID=id)
    if request.method == "GET":
        tomRating = BookRating.objects.get(book__googleID=id, user__name="Tom")
        francesRating = BookRating.objects.get(book__googleID=id, user__name="Frances")
        tom_form = BookRatingForm(initial={"rating": tomRating.rating, "readDate": tomRating.readDate})
        frances_form = BookRatingForm(initial={"rating": francesRating.rating, "readDate": francesRating.readDate})
        context = {
            "book": b,
            "tom_form": tom_form,
            "frances_form": frances_form
        }
        return render(request, "books/edit.html", context)
    if request.method == "POST":
        form = BookRatingForm(request.POST)
        if form.is_valid():
            if "tom_rating" in request.POST:
                bookRating = BookRating.objects.get(book__googleID=id, user__name="Tom")
            elif "frances_rating" in request.POST:
                bookRating = BookRating.objects.get(book__googleID=id, user__name="Frances")
            bookRating.rating = form.cleaned_data["rating"]
            bookRating.stars = f"{bookRating.rating/2}_stars.html"
            bookRating.readDate = form.cleaned_data["readDate"]
            bookRating.save()
            return redirect(f"/books/book?id={id}")
        
def remove(request):
    id = request.GET.get("id")
    Book.objects.filter(googleID=id).delete()

    return redirect("/books/")