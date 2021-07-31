from django.shortcuts import redirect
from django.urls import reverse

acad_admins = ['misc.aracad4', 'misc.mlc']
hcu_admins = ['misc.hcu.office', 'misc.mlc']


def redirect_if_authenticated(fn):
    def check(request):
        if request.user.is_authenticated:
            return redirect(reverse('index'))
        return fn(request)

    return check


def acad_only(fn):
    def check(request):
        if request.user.username not in acad_admins:
            return redirect(reverse('index'))
        return fn(request)

    return check


def hcu_only(fn):
    def check(request):
        if request.user.username not in hcu_admins:
            return redirect(reverse('index'))
        return fn(request)

    return check


def students_only(fn):
    def check(request):
        if request.user.username in hcu_admins:
            return redirect(reverse('admin_hcu'))
        if request.user.username in acad_admins:
            return redirect(reverse('admin_acad'))
        return fn(request)

    return check
