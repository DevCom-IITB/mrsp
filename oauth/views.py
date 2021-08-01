import base64

import requests
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse
from . import settings

from .decorators import redirect_if_authenticated


@redirect_if_authenticated
def oauth(request):
    url = f"{settings.AUTHORIZATION_URL}?client_id={settings.CLIENT_ID}&response_type=code&scope={settings.SCOPE}" \
          f"&redirect_uri={settings.REDIRECT_URI}"
    return redirect(url)


@redirect_if_authenticated
def login_client(request):
    auth_code = request.GET.get('code')

    client_pass = f'{settings.CLIENT_ID}:{settings.CLIENT_SECRET}'
    auth_token = base64.b64encode(client_pass.encode('utf-8')).decode('utf-8')
    headers = {
        "Authorization": "Basic {}".format(auth_token),
        "Content-type": "application/x-www-form-urlencoded",
    }

    data_uri = f'code={auth_code}&redirect_uri={settings.REDIRECT_URI}&grant_type=authorization_code'
    response = requests.post(settings.SSO_TOKEN_URL, data=data_uri, headers=headers).json()

    profile = requests.get(
        settings.SSO_PROFILE_URL,
        headers={
            "Authorization": "Bearer " + response["access_token"]
        }
    ).json()

    user, _ = User.objects.get_or_create(
        username=profile['roll_number'],
        first_name=profile['first_name'],
        last_name=profile['last_name'],
        email=profile['email']
    )
    user.save()

    login(request, user)
    return redirect(reverse('index'))


@login_required
def logout_client(request):
    logout(request)
    return render(request, 'portal/logged_out.html')


def mock_login(request):
    user, _ = User.objects.get_or_create(
        username=request.GET.get('id'),
        first_name='Ayush',
        last_name='Jangir',
        email='190050025@iitb.ac.in'
    )
    user.save()

    login(request, user)
    return redirect(reverse('index'))
