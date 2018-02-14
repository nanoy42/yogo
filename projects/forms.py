from django import forms
from .models import Project, Tag, Task
from django.contrib.auth.models import User


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'active']
        labels = {
            'title': 'Titre du projet',
            'active': 'Projet actif ?',
        }


class addMemberForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.projectId = kwargs.pop('projectId')
        super(addMemberForm, self).__init__(*args, **kwargs)
        self.fields['member'].queryset = User.objects.exclude(pk__in=Project.objects.get(pk=self.projectId).users.all())
    member = forms.ModelChoiceField(queryset=User.objects.all(), label="")


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name', 'color']
        labels = {
            'name': 'Nom du tag',
            'color': 'Couleur',
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        exclude = ('project',)
        labels = {
            'title': 'Titre',
            'userAssigned': 'Qui dit paps ?',
            'status': 'Statut',
            'prerequisites': 'Prérequis',
            'active': 'Actif'
        }
    def __init__(self, project, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.project = project
        self.fields['tags'].queryset = project.tag_set.all()
