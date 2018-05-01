from django.shortcuts import render


def home(request):
    active = 1
    return render(request, "home.html", {'active': active})

def help(request):
    return render(request, "help.html")
