from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Profile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('librarian', 'Librarian'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    
    # Fields for both students and librarians
    name = models.CharField(max_length=100)
    psrn_number = models.CharField(max_length=15, blank=True, null=True)

    # Fields for student profile
    room = models.CharField(max_length=50, blank=True, null=True)
    hostel = models.CharField(max_length=50, blank=True, null=True) 
    favorite_books = models.ManyToManyField("books.Book", default=None, blank=True, related_name="favorited_by")

    def __str__(self):
        return f"{self.user.username} Profile"

    def save(self, *args, **kwargs):
        if self.role == 'librarian':
            self.room = None 
            self.hostel = None  
        else:
            self.psrn_number = None
        super().save(*args, **kwargs)


class LateFeeConfig(models.Model):
    days_before_late_fee = models.PositiveIntegerField(default=14, help_text="Number of days before late fee is applied")
    late_fee_per_day = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=1.00, 
        help_text="Late fee per day in currency units (e.g., 1.00 for $1.00)"
    )
    def clean(self):
        if self.late_fee_per_day <= 0:
            raise ValidationError("Late fee per day must be greater than zero.")

    def __str__(self):
        return f"Late Fee: {self.late_fee_per_day} per day, Applied after {self.days_before_late_fee} days"

