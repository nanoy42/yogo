from django.shortcuts import render, redirect
from .forms import LoginForm, MailForm, TelegramPreferencesForm, verifyForm
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth import logout, login, authenticate
from projects.models import Project
from django.urls import reverse
import telepot, secrets
from yogo.acl import admin_required
from yogo.settings import TELEGRAM_TOKEN

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
    return render(request, 'users/manageUsers.html',{'users': users, 'admin':admin})

def profile(request):
    form = MailForm(request.POST or None, instance=request.user)
    form2 = TelegramPreferencesForm(None, instance=request.user.telegrampreferences)
    form3 = verifyForm(None)
    if(form.is_valid()):
        form.save()
        messages.success(request, "L'adresse mail a bien été modifiée")
        return redirect(reverse('users:profile'))
    return render(request, 'users/profile.html', {'form':form, 'form2':form2, 'form3':form3})

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
    if(user.telegrampreferences.verified and user.telegrampreferences.notifyProject):
        msg = "Vous venez d'être nommé administrateur sur Yogo"
        bot = telepot.Bot(TELEGRAM_TOKEN)
        bot.sendMessage(user.telegrampreferences.chatId, msg)
    messages.success(request, user.username + " a été passé administrateur")
    return redirect(reverse('users:manageUsers'))

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
    if(user.telegrampreferences.verified and user.telegrampreferences.notifyProject):
        msg = "Les droits administrateurs vous ont été retirés sur Yogo"
        bot = telepot.Bot(TELEGRAM_TOKEN)
        bot.sendMessage(user.telegrampreferences.chatId, msg)
    messages.success(request, "Les droits admin ont bien été retirés")
    return redirect(reverse('users:manageUsers'))


@admin_required
def remove_user(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except:
        messages.error(request, "L'utilisateur n'existe pas")
        return redirect(reverse('home'))
    user.delete()
    messages.success(request, "L'utilisateur a été supprimé")
    return redirect(reverse('users:manageUsers'))


def update_telegram_infos(request):
    form = TelegramPreferencesForm(request.POST, instance=request.user.telegrampreferences)
    if(form.is_valid()):
        if('chatId'in form.changed_data):
            form.instance.verified = False
            form.instance.verifyToken = secrets.token_urlsafe(20)
            if(form.instance.chatId != "" and form.instance.chatId is not None):
                bot = telepot.Bot(TELEGRAM_TOKEN)
                bot.sendMessage(form.instance.chatId, "Veuillez vérifier votre identifiant avec ce token : " + form.instance.verifyToken + "\n" +  "/profile")
                messages.warning(request, "Votre identifiant de chat a changé. Vous devez le vérifier")
        form.save()
        messages.success(request, "Les informations ont bien été enregistrées")
    return redirect(reverse('users:profile'))

def verifyToken(request):
    form = verifyForm(request.POST)
    print(form.data['token'])
    print("\n" + request.user.telegrampreferences.verifyToken)
    if(form.data['token'] == request.user.telegrampreferences.verifyToken):
        tp = request.user.telegrampreferences
        tp.verified = True
        tp.save()
        messages.success(request, "Le chat a été bien été vérifié")
    else:
        messages.error(request, "La vérification a échouée")
    return redirect(reverse('users:profile'))
