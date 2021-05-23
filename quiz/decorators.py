from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _

from rest_framework import exceptions


# Check if user is Admin staff(Teacher)
def is_staff(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.user.is_staff:
            raise exceptions.PermissionDenied(_('Not authorized'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func


# Check if user is not staff(Student)
def is_normal(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if request.user.is_staff:
            raise exceptions.PermissionDenied(_('Not authorized'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func


# Check if user not anonymous
def is_auth_user(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func
