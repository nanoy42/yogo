from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import logout


def home(request):
    active = 1
    return render(request, "home.html", {'active': active})


def logout_view(request):
    logout(request)
    return redirect(reverse('home'))
