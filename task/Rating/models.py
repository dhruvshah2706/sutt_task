from django.db import models
from django.contrib.auth.models import User
from books.models import Book

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    image = models.ImageField(upload_to='feedback_images/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.subject}"
    
class Rating(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='ratings')  # Specify a unique related name
    rating = models.PositiveSmallIntegerField()  # Rating from 1 to 5

    class Meta:
        unique_together = ('user', 'book')  # Prevent multiple ratings for the same book by one user


