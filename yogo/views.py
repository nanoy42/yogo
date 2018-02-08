from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import logout, login, authenticate
from .forms import LoginForm
from django.contrib import messages
from django.contrib.auth.models import User
from projects.models import Project


def home(request):
    active = 1
    return render(request, "home.html", {'active': active})


def login_view(request):
    form = LoginForm(request.POST or None)
    if(form.is_valid()):
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if(user is not None):
            login(request, user)
            messages.success(request, "Bienvenue " + user.username)
            return redirect(reverse('home'))
        else:
            messages.error(request, "Nom d'utilisateur et/ou mot de passe incorrect")
    return render(request, 'form.html', {'title': 'Connexion', 'form': form, 'bouton':' Se connecter', 'icon': 'sign-in-alt', 'active': 4})


def logout_view(request):
    logout(request)
    return redirect(reverse('home'))

def manageUsers(request):
    users = User.objects.all()
    return render(request, 'yogo/manageUsers.html',{'users':users})

def profile(request):
    createdProjects = Project.objects.filter(owner=request.user).count()
    return render(request, 'yogo/profile.html', {'createdProjects':createdProjects})
