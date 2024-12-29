import os
import pandas as pd
from django.http import FileResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Book, Borrow
from django.contrib.auth.decorators import login_required
from .forms import BookForm, BookUpdateForm
from datetime import timedelta
from django.utils.timezone import now
from users.models import LateFeeConfig
from users.decorators import role_required
from .decorators import borrow_user_required

@login_required
@role_required(['librarian',])
def upload_books(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        if not file.name.endswith('.xlsx'):
            messages.error(request, 'Please upload a valid .xlsx file.')
            return render(request, 'books/upload_books.html')

        try:
            # Read the uploaded Excel file using openpyxl engine
            data = pd.read_excel(file, engine='openpyxl')
            for _, row in data.iterrows():
                # Add book details to the database
                Book.objects.create(
                    title=row['Title'],
                    author=row['Author'],
                    isbn=row['ISBN'],
                    publisher_name = row['Name of Publisher'],
                    publication_date = row.get('Publication Date', None),
                    total_copies = row.get['Total number of books'],
                )
            messages.success(request, 'Books successfully uploaded!')
        except Exception as e:
            messages.error(request, f"Error processing the file: {e}")
    return render(request, 'books/upload_books.html')


@login_required
@role_required(['librarian',])
def download_template(request):
    # Generate an Excel template
    template_data = {
        'Title': ['Sample Book'],
        'Author': ['Sample Author'],
        'ISBN': ['1234567890123'],
        'Name of Publisher': ['Sample Publisher'],
        'Publication Date': ['2024-01-01'],  # Example date
        'Total number of books': [1],
    }
    template_file = pd.DataFrame(template_data)
    file_path = '/tmp/book_template.xlsx'
    template_file.to_excel(file_path, index=False)

    response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename='book_template.xlsx')
    os.remove(file_path)  # Clean up the temporary file
    return response

@login_required
@role_required(['librarian',])
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.available_copies = book.total_copies
            book.save()
            messages.success(request, 'Book added successfully!')
            return redirect('student_dashboard')  # Redirect to the same page
    else:
        form = BookForm()
    return render(request, 'books/add_book.html', {'form': form})


@login_required
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    profile = request.user.profile  # Get user profile to determine role

    if request.method == 'POST' and profile.role == 'librarian':
        form = BookUpdateForm(request.POST, request.FILES, instance=book)  # Librarians can edit
        if form.is_valid():
            form.save()
            return redirect('librarian_dashboard')
    else:
        form = BookUpdateForm(instance=book)
        # If the user is a student, disable all the fields in the form
        if profile.role == 'student':
            for field in form.fields.values():
                field.disabled = True  # Disable the input fields for students

    return render(request, 'books/book_detail.html', {'form': form, 'book': book, 'role': profile.role})


@login_required
@role_required(['student',])
def borrow_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        if book.available_copies > 0:
            # Create Borrow record
            
            record = Borrow.objects.create(
                user=request.user,
                book=book
            )
            # Update available copies
            book.available_copies -= 1
            book.save()
            
            messages.success(request, f"You have borrowed '{book.title}'. Please return it by {record.due_date.strftime('%B %d, %Y')}.")
            return redirect('student_dashboard')  # Redirect to student's dashboard
        else:
            messages.error(request, f"'{book.title}' is currently unavailable.")
    
    return render(request, 'books/borrow_book.html', {'book': book})


@login_required
@role_required(['student',])
@borrow_user_required
def return_book(request, pk):
    # Get the borrow record for the user and book
    borrow_record = get_object_or_404(Borrow, pk=pk, user=request.user, is_returned=False)

    if request.method == 'POST':
        # Update the borrow record
        borrow_record.is_returned = True
        borrow_record.return_date = now().date()
        borrow_record.save()

        # Update the available copies for the book
        book = borrow_record.book
        book.available_copies += 1
        book.save()

        messages.success(request, f'You have successfully returned "{book.title}".')
        if (now().date() - borrow_record.due_date) > timedelta(0):
            config = LateFeeConfig.objects.first()
            days_before_due = config.days_before_late_fee

            # Calculate the number of overdue days
            overdue_days = (now().date() - borrow_record.due_date).days
            # Calculate the late fees
            late_fees = LateFeeConfig.objects.first().late_fee_per_day * overdue_days
            messages.success(request, f'Late fees applicable {late_fees}')
        return redirect('student_dashboard')  # Redirect to an appropriate page

    return render(request, 'books/return_book.html', {'borrow_record': borrow_record})


@login_required
@role_required(['librarian',])
def borrowed_copies(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    borrowed_records = Borrow.objects.filter(book=book, is_returned=False).select_related('user')

    return render(request, 'books/borrowed_copies.html', {'book': book, 'borrowed_records': borrowed_records})


@login_required
@role_required(['student',])
def student_borrowing_history(request):
    borrows = Borrow.objects.filter(user=request.user).select_related('book').order_by('-borrow_date')

    return render(request, 'books/issuing_history.html', {'borrows': borrows})
