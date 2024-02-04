from django.db import models

class Book(models.Model):
    googleID = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    publishDate = models.CharField(max_length=50, null=True)
    pages = models.IntegerField(null=True)
    cover = models.CharField(max_length=500)
    description = models.CharField(max_length=10000, null=True)

    def __str__(self):
        return f"{self.title} - {self.author}"


class User(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class BookRating(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(null=True)
    readDate = models.DateField(null=True)

    def __str__(self):
        return f"{self.book.title} - {self.user.name}"