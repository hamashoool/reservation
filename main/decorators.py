from django.core.exceptions import PermissionDenied
from django.http import Http404


def is_person(function):
    def wrap(request, *args, **kwargs):
        if request.user.usertype.who == "P":
            try:
                return function(request, *args, **kwargs)
            except:
                raise Http404
        else:
            raise PermissionDenied
    return wrap


def is_restaurant(function):
    def wrap(request, *args, **kwargs):
        if request.user.usertype.who == "R":
            try:
                return function(request, *args, **kwargs)
            except:
                raise PermissionDenied
        else:
            raise PermissionDenied
    return wrap

