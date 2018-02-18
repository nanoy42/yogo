from django.shortcuts import render


def home(request):
    active = 1
    return render(request, "home.html", {'active': active})
