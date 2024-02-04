from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("user", views.user, name="user"),
    path("book", views.book, name="book"),
    path("book/edit", views.edit, name="edit"),
    path("search", views.search, name="search"),
    path("results", views.results, name="results"),
    path("book/add", views.add, name="add"),
    path("book/remove", views.remove, name="remove")
]