from django import forms
from django.contrib.auth.models import User
from .models import TelegramPreferences

class LoginForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=254)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)

class verifyForm(forms.Form):
    token = forms.CharField(label="Token", max_length=255)

class MailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

class TelegramPreferencesForm(forms.ModelForm):
    class Meta:
        model = TelegramPreferences
        fields = ['chatId', 'notifyProject', 'notifyTask', 'notifyProfile']
        labels = {
            'chatId': 'Identifiant du chat',
            'notifyProject': 'Notifier les modifications de projets',
            'notifyTask': 'Notifier les modifications de taches',
            'notifyProfile': 'Notifier les modifications du profil'
        }
