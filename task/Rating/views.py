from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import FeedbackForm, RatingForm
from .models import Feedback, Rating
from users.decorators import role_required
from books.models import Book, Borrow

@login_required
@role_required(['student',])
def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            messages.success(request, "Your feedback has been submitted successfully.")
            return redirect('student_dashboard')  # Redirect to student dashboard after submitting feedback
    else:
        form = FeedbackForm()
    return render(request, 'Rating/submit_feedback.html', {'form': form})


@login_required
@role_required(['librarian',])
def view_feedback(request):
    feedbacks = Feedback.objects.select_related('user').order_by('-submitted_at')
    return render(request, 'Rating/view_feedback.html', {'feedbacks': feedbacks})

@login_required
def rate_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    borrow_record = Borrow.objects.filter(user=request.user, book=book).first()

    # Ensure the student has borrowed the book before rating
    if not borrow_record:
        messages.error(request, "You can only rate books you have borrowed.")
        return redirect('student_dashboard')

    # Fetch the existing rating if it exists
    rating = Rating.objects.filter(user=request.user, book=book).first()

    if request.method == 'POST':
        form = RatingForm(request.POST, instance=rating)
        if form.is_valid():
            # Save the rating
            rating = form.save(commit=False)
            rating.user = request.user
            rating.book = book
            rating.save()

            # Save the book to update its aggregate rating
            book.save()

            messages.success(request, "Your rating has been submitted.")
            return redirect('student_dashboard')
    else:
        # Pre-fill the form with the existing rating, if available
        form = RatingForm(instance=rating)

    return render(request, 'Rating/rate_book.html', {
        'book': book,
        'form': form,
    })