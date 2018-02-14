from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import logout, login, authenticate
from .forms import LoginForm
from django.contrib import messages
from django.contrib.auth.models import User, Group
from projects.models import Project

from yogo.acl import admin_required


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

@admin_required
def manageUsers(request):
    users = User.objects.all()
    admin, _ = Group.objects.get_or_create(name="admin")
    return render(request, 'yogo/manageUsers.html',{'users': users, 'admin':admin})

def profile(request):
    createdProjects = Project.objects.filter(owner=request.user).count()
    return render(request, 'yogo/profile.html', {'createdProjects':createdProjects})

@admin_required
def add_admin(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except:
        messages.error(request, "L'utilisateur n'existe pas")
        return redirect(reverse('home'))
    admin, _ = Group.objects.get_or_create(name="admin")
    if(admin in user.groups.all()):
        messages.error(request, "L'utilisateur est dejà admin")
        return redirect(reverse('home'))
    user.groups.add(admin)
    messages.success(request, user.username + " a été passé administrateur")
    return redirect(reverse('manageUsers'))

@admin_required
def remove_admin(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except:
        messages.error(request, "L'utilisateur n'existe pas")
        return redirect(reverse('home'))
    admin, _ = Group.objects.get_or_create(name="admin")
    if(admin not in user.groups.all()):
        messages.error(request, "L'utilisateur n'est pas admin")
        return redirect(reverse('home'))
    user.groups.remove(admin)
    messages.success(request, "Les droits admin ont bien été retirés")
    return redirect(reverse('manageUsers'))


@admin_required
def remove_user(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except:
        messages.error(request, "L'utilisateur n'existe pas")
        return redirect(reverse('home'))
    user.delete()
    messages.success(request, "L'utilisateur a été supprimé")
    return redirect(reverse('manageUsers'))
