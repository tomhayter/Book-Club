from django.contrib import admin
from .models import Book, User, BookRating

# Register your models here.

admin.site.register(Book)
admin.site.register(BookRating)
admin.site.register(User)