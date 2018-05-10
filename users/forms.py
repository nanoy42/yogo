from django import forms
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=254)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)

class MailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

