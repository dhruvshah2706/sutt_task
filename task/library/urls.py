from django.contrib import admin
from django.urls import path,  include
from books.views import student_borrowing_history
from users.views import custom_login, home, student_dashboard, create_profile, custom_logout, librarian_dashboard, profile, update_late_fee_config
from django.conf import settings
from Rating.views import submit_feedback, view_feedback
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', custom_login, name = 'login'),
    # path('accounts/login/',  RedirectView.as_view(url='/login/',  permanent=False)),
    path("accounts/", include("allauth.urls")),
    path('', home, name='home'),
    path('student_dashboard/', student_dashboard, name = 'student_dashboard'),
    path('librarian_dashboard/', librarian_dashboard, name = 'librarian_dashboard'),
    path('profile/', profile, name = 'profile'),
    path('profile/create/', create_profile, name = 'create_profile'),
    path('logout/', custom_logout,  name='logout'), 
    path('book/', include('books.urls')),
    path('update_late_fee_config/', update_late_fee_config, name='update_late_fee_config'),
    path('borrowing_history/', student_borrowing_history, name='student_borrowing_history'),
    path('feedback/submit/', submit_feedback, name='submit_feedback'),
    path('feedback/view/', view_feedback, name='view_feedback'),
    path('rating/', include('Rating.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)