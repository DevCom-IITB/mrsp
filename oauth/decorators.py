from django.shortcuts import redirect
from django.urls import reverse
from decouple import config,Csv

acad_admins = config('ACAD_ADMINS',cast=Csv())
hcu_admins = config('HCU_ADMINS',cast=Csv())
super_admins = config('SUPER_ADMINS',cast=Csv())


def redirect_if_authenticated(fn):
    def check(request):
        if request.user.is_authenticated:
            return redirect(reverse('index'))
        return fn(request)

    return check


def acad_only(fn):
    def check(request):
        if request.user.username not in acad_admins + super_admins:
            return redirect(reverse('index'))
        return fn(request)

    return check


def hcu_only(fn):
    def check(request):
        if request.user.username not in hcu_admins + super_admins:
            return redirect(reverse('index'))
        return fn(request)

    return check


def students_only(fn):
    def check(request):
        if request.user.username in hcu_admins + super_admins:
            return redirect(reverse('admin_hcu'))
        if request.user.username in acad_admins + super_admins:
            return redirect(reverse('admin_acad'))
        return fn(request)

    return check
