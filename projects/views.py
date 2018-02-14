from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Task, Project, Tag
from .forms import ProjectForm, addMemberForm, TagForm, TaskForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from yogo.acl import can_edit_project, admin_required, member_required


@login_required
def myprojects(request):
    projects = request.user.membered_projects.all()
    active = 2
    return render(request, 'projects/myprojects.html', {'projects': projects, 'active': active})


@login_required
def mytasks(request):
    active = 3
    todo_tasks = Task.objects.filter(
        userAssigned=request.user).filter(status=Task.State.TODO)
    doing_tasks = Task.objects.filter(
        userAssigned=request.user).filter(status=Task.State.DOING)
    done_tasks = Task.objects.filter(
        userAssigned=request.user).filter(status=Task.State.DONE)
    return render(request, 'projects/mytasks.html', {'active': active, 'todo': todo_tasks, 'doing': doing_tasks, 'done': done_tasks})


@login_required
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


@login_required
@member_required
def project(request, pk):
    project = Project.objects.get(pk=pk)
    task_todo = project.task_set.filter(status=Task.State.TODO)
    task_doing = project.task_set.filter(status=Task.State.DOING)
    task_done = project.task_set.filter(status=Task.State.DONE)
    taken_tasks = []
    for user in project.users.all():
        taken_tasks.append(project.task_set.filter(userAssigned=user).count())
    memberForm = addMemberForm(request.POST or None, projectId=pk)
    projectForm = ProjectForm(request.POST or None, instance=project)
    if(memberForm.is_valid()):
        member = memberForm.cleaned_data['member']
        if member in project.users.all():
            messages.error(request, 'Cet utilisateur est déjà dans le projet')
        else:
            project.users.add(member)
            messages.success(request, "L'utilisateur a bien été ajouté")
    if(projectForm.is_valid()):
        projectForm.save()
        messages.success(request, 'Le projet a bien été modifié')
        return redirect(reverse('projects:project', kwargs={'id':id}))
    return render(request, 'projects/project.html', {'active': 2, 'project': project, 'todo': task_todo, 'doing': task_doing, 'done': task_done, 'taken_tasks': taken_tasks, 'addMemberForm': memberForm, 'projectForm': projectForm})


@login_required
@can_edit_project
def deleteUserFromProject(request, pk, user_id):
    project = Project.objects.get(pk=pk)
    user = User.objects.get(pk=user_id)
    if(user not in project.users.all()):
        messages.error(request, "L'utilisateur n'est pas dans le projet")
    else:
        project.users.remove(user)
        messages.success(request, "L'utilisateur a bien été retiré du projet")
    return redirect(reverse('projects:project', kwargs={'id': pk}))


@login_required
@admin_required
def manageProjects(request):
    projects = Project.objects.all()
    return render(request, 'projects/manageProjects.html', {'projects': projects})


@login_required
@can_edit_project
def changeState(request, pk):
    try:
        project = Project.objects.get(pk=pk)
    except:
        project = None
    if(project is not None):
        project.active = 1 - project.active
        project.save()
        messages.success(request, 'Le statut du projet a bien été modifié')
    else:
        messages.error(request, 'Ce projet n\'existe pas')
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@can_edit_project
def deleteProject(request, pk):
    try:
        project = Project.objects.get(pk=pk)
    except:
        messages.error(request, 'Ce projet n\'existe pas')
        return redirect(reverse('home'))
    project.delete()
    messages.success(request, 'Le projet a bien été supprimé')
    return redirect(request.GET.get('next', reverse('home')))


@login_required
@admin_required
def manageTags(request):
    tags = Tag.objects.all()
    return render(request, 'projects/manageTags.html', {'tags': tags})


@login_required
@admin_required
def newTag(request):
    form = TagForm(request.POST or None)
    if(form.is_valid()):
        form.save()
        messages.success(request, 'Le tag a bien été créé')
        return redirect(reverse('projects:manageTags'))
    return render(request, 'form.html', {'form': form, 'title': 'Nouveau tag', 'bouton': 'Créer le tag', 'icon': 'star'})


@login_required
@admin_required
def editTag(request, tagId):
    try:
        tag = Tag.objects.get(pk=tagId)
    except:
        messages.error(request, 'Ce tag n\'existe pas')
        return redirect(reverse('home'))
    form = TagForm(request.POST or None, instance=tag)
    if(form.is_valid()):
        form.save()
        messages.success(request, 'Le tag a bien été modifié')
        return redirect(reverse('projects:manageTags'))
    return render(request, 'form.html', {'form': form, 'title': 'Modification du tag ' + tag.name, 'bouton': 'Modifier', 'icon': 'pencil-alt'})


@login_required
@admin_required
def deleteTag(request, tagId):
    try:
        tag = Tag.objects.get(pk=tagId)
    except:
        messages.error(request, "Ce tag n'existe pas")
        return redirect(reverse('home'))
    tag.delete()
    messages.success(request, "Le tag a bien été supprimé")
    return redirect(reverse('projects:manageTags'))


@login_required
@member_required
def newTask(request, pk):
    active = 2
    project = Project.objects.get(pk=pk)
    form = TaskForm(request.POST or None)
    if(form.is_valid()):
        pass
    return render(request, 'form.html', {'active': active, 'form': form, 'icon': 'star', 'bouton': 'Créer la tâche', 'title': 'Nouvelle tâche de '+project.title})


@login_required
def changeTaskStatus(request, taskId, newStatus, nextUrl):
    cor = {'todo': Task.State.TODO, 'doing': Task.State.DOING, 'done': Task.State.DONE}
    try:
        task = Task.objects.get(pk=taskId)
    except:
        messages.error(request, "La tâche n'existe pas")
        return redirect(reverse('home'))
    try:
        task.status = cor[newStatus]
    except:
        messages.error(request, "Le status demandé n'existe pas")
        return redirect(reverse('home'))
    task.save()
    messages.success(request, "La tâche est passée en " + newStatus)
    if(nextUrl == "project"):
        return redirect(reverse('projects:project', kwargs={'pk': task.project.pk}))
    else:
        return redirect(reverse('projects:'+nextUrl))


@login_required
def deleteTask(request, taskId, nextUrl):
    try:
        task = Task.objects.get(pk=taskId)
    except:
        messages.error(request, "La tâche n'existe pas")
        return redirect(reverse('home'))
    task.delete()
    messages.success(request, "La tâche a bien été supprimée")
    if(nextUrl == "project"):
        return redirect(reverse('projects:project', kwargs={'id': task.project.pk}))
    else:
        return redirect(reverse('projects:'+nextUrl))


@login_required
def paps(request, taskId):
    try:
        task = Task.objects.get(pk=taskId)
    except:
        messages.error(request, "La tâche n'existe pas")
        return redirect(reverse('home'))
    task.userAssigned = request.user
    task.save()
    messages.success(request, "Vous avez paspé la tâche. Au boulot !")
    return redirect(reverse('projects:project', kwargs={'id': task.project.pk}))


@login_required
def depaps(request, taskId, nextUrl):
    try:
        task = Task.objects.get(pk=taskId)
    except:
        messages.error(request, "La tâche n'existe pas")
        return redirect(reverse('home'))
    if(task.userAssigned != request.user):
        messages.error(request, "Vous ne pouvez pas depaps une tâche que vous n'avez pas papsée")
        return redirect(reverse('projects:project', kwargs={'id': task.project.pk}))
    else:
        task.userAssigned = None
        task.save()
        messages.success(request, "Depaps réussi (flemmard)")
        if(nextUrl == "project"):
            return redirect(reverse('projects:project', kwargs={'id': task.project.pk}))
        else:
            return redirect(reverse('projects:'+nextUrl))
