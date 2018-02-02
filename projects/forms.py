from django.forms import ModelForm
from .models import Project


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'active']
        labels = {
            'title': 'Titre du projet',
            'active': 'Projet actif ?',
        }
