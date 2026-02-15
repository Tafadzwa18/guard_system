from django.contrib.auth.decorators import user_passes_test

def guard_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and getattr(u, "is_guard", lambda: False)())(view_func)

def supervisor_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and (getattr(u, "is_supervisor", lambda: False)() or getattr(u, "is_admin", lambda: False)()))(view_func)
