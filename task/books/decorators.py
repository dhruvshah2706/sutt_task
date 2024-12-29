from django.http import HttpResponseForbidden
from functools import wraps
from .models import Borrow

def borrow_user_required(view_func):
    """
    Decorator to check if the user attempting to return a book is the one who borrowed it.
    """
    @wraps(view_func)
    def _wrapped_view(request, pk, *args, **kwargs):
        try:
            borrow_record = Borrow.objects.get(pk=pk)
            if borrow_record.user == request.user:
                return view_func(request, pk, *args, **kwargs)
            return HttpResponseForbidden("You can only return books you have borrowed.")
        except Borrow.DoesNotExist:
            return HttpResponseForbidden("Borrow record does not exist.")
    return _wrapped_view
