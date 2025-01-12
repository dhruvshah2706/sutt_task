from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,  login,  logout
from .forms import CustomAuthenticationForm, GoogleLoginProfileForm, ManualRegistrationProfileForm, ProfileUpdateForm, LateFeeConfigForm
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile, LateFeeConfig
from django.contrib.auth.decorators import login_required
from books.models import Book, Borrow  # Import the Book model
from django.db.models import Q
from allauth.socialaccount.models import SocialAccount
from .decorators import role_required
from fuzzywuzzy import fuzz
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def custom_login(request):
    # return redirect('student_dashboard')
    if request.user.is_authenticated:
        return redirect('student_dashboard')
    form = CustomAuthenticationForm()  # Instantiate the form for GET requests
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)  # Pass data to form
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username,  password=password)
            if user is not None:
                login(request,  user)
                return redirect('student_dashboard')
            else:
                form.add_error(None,  "Invalid username or password.")  # Add error for invalid credentials
    return render(request,  'users/login.html',  {'form': form})

def home(request):
    return redirect('student_dashboard')


@login_required
def student_dashboard(request):
    try:
        profile = request.user.profile
        if profile.role == 'librarian':
            return redirect('librarian_dashboard')
    except Profile.DoesNotExist:
        return redirect('create_profile')

    query = request.GET.get('q', '')  # Get the search query
    books = Book.objects.all()  # Fetch all books

    if query:
        # Perform fuzzy matching for multiple fields
        book_choices = []
        for book in books:
            book_choices.append({
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'publisher_name': book.publisher_name,
                'isbn': str(book.isbn),  # Convert ISBN to string for matching
                'publication_date': book.publication_date.strftime('%Y-%m-%d'),
            })

        matched_books = []
        for choice in book_choices:
            match_score = 0
            list = ['title', 'author', 'publisher_name', 'isbn']

            for item in list:
                if fuzz.partial_ratio(query, choice[item]) > 60:
                    matched_books.append(choice['id'])
                    break

        # Filter books by matched IDs
        books = books.filter(id__in=matched_books)

    # Pagination for books
    paginator = Paginator(books, 2)  # Show 10 books per page
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)

    # Pagination for borrow records
    borrow_records = Borrow.objects.filter(user=request.user, is_returned=False)
    borrow_paginator = Paginator(borrow_records, 2)  # Show 5 borrowed books per page
    borrow_page_number = request.GET.get('borrow_page')
    borrow_records = borrow_paginator.get_page(borrow_page_number)

    return render(request, 'users/student_dashboard.html', {
        'books': books,
        'query': query,
        'borrow_records': borrow_records
    })




@login_required
@role_required(['librarian',])
def librarian_dashboard(request):
    books = Book.objects.all()
    query = request.GET.get('q', '')

    if query:
        # Perform fuzzy matching for multiple fields
        book_choices = []
        for book in books:
            book_choices.append({
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'publisher_name': book.publisher_name,
                'isbn': str(book.isbn),  # Convert ISBN to string for matching
                'publication_date': book.publication_date.strftime('%Y-%m-%d'),
            })

        matched_books = []
        for choice in book_choices:
            match_score = 0
            list = ['title', 'author', 'publisher_name', 'isbn']

            for item in list:
                if fuzz.partial_ratio(query, choice[item]) > 60:
                    matched_books.append(choice['id'])
                    break

        # Filter books by matched IDs
        books = books.filter(id__in=matched_books)

    paginator = Paginator(books, 2)  # Show 10 books per page
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
        
        
    return render(request, 'users/librarian_dashboard.html', {'books': books, 'query': query})

@login_required
def create_profile(request):
    """View to create a new profile."""
    # Check if user is authenticated through Google
    if request.user.is_authenticated and request.user.socialaccount_set.exists():
        # Handle Google Login profile creation
        if not request.user.email.endswith('@pilani.bits-pilani.ac.in'):
            messages.error(request, "Access denied: Your email must be a bits email")
            
            social_account = SocialAccount.objects.filter(user=request.user).first()
            if social_account:
                social_account.delete()
            return redirect('logout')
        if request.method == 'POST':
            form = GoogleLoginProfileForm(request.POST)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user  # Link profile to the existing user
                profile.role = 'student'  # Automatically set role to 'student'
                profile.save()
                messages.success(request, 'Profile created successfully for Student!')
                return redirect('student_dashboard')
        else:
            form = GoogleLoginProfileForm()
    else:
        # Handle manual registration (username-password)
        if request.method == 'POST':
            form = ManualRegistrationProfileForm(request.POST)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.role = 'librarian'
                profile.user = request.user
                request.user.email = form.cleaned_data['email']
                request.user.save()
                profile.save()
                messages.success(request, 'Profile created for Librarian!')
                return redirect('login')  # Redirect to login page
        else:
            form = ManualRegistrationProfileForm()
    
    return render(request, 'users/create_profile.html', {'form': form})

@login_required
def profile(request):
    profile = request.user.profile  # Access the user's profile
    if request.method == 'POST':
        # Pass the profile as the instance and the user as an argument
        form = ProfileUpdateForm(request.POST, instance=profile, user=request.user)  
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=profile, user=request.user)  # Pass user and instance correctly
    return render(request, 'users/profile.html', {'form': form})


@login_required
def custom_logout(request):
    logout(request)
    return redirect('login')


@login_required
@role_required(['librarian'])
def update_late_fee_config(request):
    if request.user.profile.role != 'librarian':
        return redirect('student_dashboard')  # Restrict access to librarians only

    # Get the existing config or create a default one
    config, created = LateFeeConfig.objects.get_or_create(id=1)

    if request.method == 'POST':
        form = LateFeeConfigForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Late fee configuration updated successfully!")
            return redirect('librarian_dashboard')
    else:
        form = LateFeeConfigForm(instance=config)

    return render(request, 'users/update_late_fee_config.html', {'form': form})