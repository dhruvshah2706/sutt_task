from django.urls import path,  include
from .views import upload_books, download_template, add_book, book_detail, borrow_book, return_book, borrowed_copies

urlpatterns = [
    path('upload/', upload_books, name = 'upload_book'),
    path('download_template', download_template, name = 'download_template'),
    path('add', add_book, name='add_book'),
    path('detail/<int:pk>', book_detail, name='book_detail'),
    path('borrow/<int:pk>', borrow_book, name='borrow'),
    path('return/<int:pk>/', return_book, name='return'),
     path('<int:book_id>/borrowed_copies/', borrowed_copies, name='borrowed_copies'),
]