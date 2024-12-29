from django.http import HttpResponseForbidden
from functools import wraps

def role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request,  *args,  **kwargs):
            if request.user.is_authenticated and request.user.profile.role in role:
                return view_func(request,  *args,  **kwargs)
            return HttpResponseForbidden("You don't have access to this page.")
        return _wrapped_view
    return decorator
