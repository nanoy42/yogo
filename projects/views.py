from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Task
from .forms import ProjectForm
# Create your views here.


def myprojects(request):
    projects = request.user.membered_projects.all()
    active = 2
    return render(request, 'projects/myprojects.html', {'projects': projects, 'active': active})


def mytasks(request):
    active = 3
    todo_tasks = Task.objects.filter(
        userAssigned=request.user).filter(status=Task.State.TODO)
    doing_tasks = Task.objects.filter(
        userAssigned=request.user).filter(status=Task.State.DOING)
    done_tasks = Task.objects.filter(
        userAssigned=request.user).filter(status=Task.State.DONE)
    return render(request, 'projects/mytasks.html', {'active': active, 'todo': todo_tasks, 'doing': doing_tasks, 'done': done_tasks})


def newProject(request):
    active = 2
    form = ProjectForm(request.POST or None)
    if(form.is_valid()):
        form.instance.owner = request.user
        form.save()
        form.instance.users.add(request.user)
        form.save()
        return redirect(reverse('home'))
    return render(request, 'form.html', {'form': form, 'active': active, 'title': "Nouveau projet", 'bouton': 'Créer le projet', 'icon': 'star'})
