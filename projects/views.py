from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Task, Project
from .forms import ProjectForm, addMemberForm
from django.contrib import messages
from django.contrib.auth.models import User
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


def project(request, id):
    project = Project.objects.get(pk=id)
    count_task_todo = project.task_set.filter(status=Task.State.TODO).count()
    count_task_doing = project.task_set.filter(status=Task.State.DOING).count()
    count_task_done = project.task_set.filter(status=Task.State.DONE).count()
    taken_tasks = []
    for user in project.users.all():
        taken_tasks.append(project.task_set.filter(userAssigned=user).count())
    memberForm = addMemberForm(request.POST or None, projectId=id)
    projectForm = ProjectForm(request.POST or None)
    if(memberForm.is_valid()):
        member = memberForm.cleaned_data['member']
        if member in project.users.all():
            messages.error(request, 'Cet utilisateur est déjà dans le projet')
        else:
            project.users.add(member)
            messages.success(request, "L'utilisateur a bien été ajouté")
    return render(request, 'projects/project.html', {'active': 2, 'project': project, 'todo': count_task_todo, 'doing': count_task_doing, 'done': count_task_done, 'taken_tasks': taken_tasks, 'addMemberForm': memberForm})


def deleteUserFromProject(request, user_id, project_id):
    project = Project.objects.get(pk=project_id)
    user = User.objects.get(pk=user_id)
    if(user not in project.users.all()):
        messages.error(request, "L'utilisateur n'est pas dans le projet")
    else:
        project.users.remove(user)
        messages.success(request, "L'utilisateur a bien été retiré du projet")
    return redirect(reverse('projects:project', kwargs={'id':project_id}))


def manageProjects(request):
    projects = Project.objects.all()
    return render(request, 'projects/manageProjects.html', {'projects': projects})

def changeState(request, projectId):
    project = Project.objects.get(pk=projectId)
    if(project is not None):
        project.active = 1 - project.active
        project.save()
        messages.success(request, 'Le statut du projet a bien été modifié')
    else:
        messages.error(request, 'Ce projet n\'existe pas')
    return redirect(request.META.get('HTTP_REFERER','/'))

def deleteProject(request, projectId, nextUrl):
    project = Project.objects.get(pk=projectId)
    if(project is not None):
        project.delete()
        messages.success(request, 'Le projet a bien été supprimé')
    else:
        messages.error(request, 'Ce projet n\'existe pas')
    return redirect(nextUrl)

