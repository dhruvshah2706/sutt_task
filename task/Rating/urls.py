from .views import rate_book
from django.urls import path

urlpatterns = [
    path('<int:book_id>/', rate_book, name='rate_book'),
]
