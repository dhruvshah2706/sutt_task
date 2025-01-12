from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from users.models import LateFeeConfig  
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db.models import Avg, Count

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.PositiveBigIntegerField(unique=True)
    publication_date = models.DateField(blank=True, null=True)
    publisher_name = models.CharField(max_length=255, default=None)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    rating = models.FloatField(default=0.0)
    num_ratings = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        # Ensure available copies are not greater than total copies
        if self.available_copies > self.total_copies:
            raise ValidationError("Available copies cannot be more than total copies")

        # Call the parent's save method to persist data
        super().save(*args, **kwargs)

        # Recalculate ratings if related model exists
        if hasattr(self, 'ratings'):
            ratings = self.ratings.aggregate(avg_rating=Avg('rating'), count=Count('rating'))
            self.rating = ratings['avg_rating'] or 0.0
            self.num_ratings = ratings['count'] or 0
            
            # Save again to update rating and num_ratings
            super().save(update_fields=['rating', 'num_ratings'])

    def __str__(self):
        return f"{self.title}"


    

class Borrow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField(default=now)
    due_date = models.DateField(default=now().date()+timedelta(days=LateFeeConfig.objects.first().days_before_late_fee))
    return_date = models.DateField(blank=True, null=True)
    is_returned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"

    def save(self, *args, **kwargs):
        config = LateFeeConfig.objects.first()
        days_before_due = config.days_before_late_fee if config else 14
        self.due_date = self.borrow_date + timedelta(days=days_before_due)
        super().save(*args, **kwargs)