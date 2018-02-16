from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Task, Project, Tag
from .forms import ProjectForm, AddMemberForm, TagForm, TaskForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from yogo.acl import can_edit_project, admin_required, member_required


@login_required
def my_projects(request):
    projects = request.user.membered_projects.all()
    active = 2
    return render(request, 'projects/myprojects.html', {
        'projects': projects,
        'active': active
    })


@login_required
def my_tasks(request):
    active = 3
    todo_tasks = Task.objects.filter(
        userAssigned=request.user).filter(status=Task.State.TODO)
    doing_tasks = Task.objects.filter(
        userAssigned=request.user).filter(status=Task.State.DOING)
    done_tasks = Task.objects.filter(
        userAssigned=request.user).filter(status=Task.State.DONE)
    return render(request, 'projects/mytasks.html', {
        'active': active,
        'todo': todo_tasks,
        'doing': doing_tasks,
        'done': done_tasks
    })


@login_required
def new_project(request):
    active = 2
    form = ProjectForm(request.POST or None)
    if(form.is_valid()):
        form.instance.owner = request.user
        form.save()
        form.instance.users.add(request.user)
        form.save()
        messages.success(request, "Projet créé.")
        return redirect(reverse(
            'projects:project',
            kwargs={'pk': form.instance.pk}
        ))
    return render(request, 'form.html', {
        'form': form,
        'active': active,
        'title': "Nouveau projet",
        'bouton': 'Créer le projet',
        'icon': 'star'
    })


@login_required
@member_required
def project(request, pk, project_form=None, member_form=None):
    project = Project.objects.get(pk=pk)
    task_todo = project.task_set.filter(status=Task.State.TODO)
    task_doing = project.task_set.filter(status=Task.State.DOING)
    task_done = project.task_set.filter(status=Task.State.DONE)
    taken_tasks = []
    for user in project.users.all():
        taken_tasks.append(project.task_set.filter(userAssigned=user).count())
    memberForm = AddMemberForm(request.POST or None, projectId=pk)
    projectForm = ProjectForm(request.POST or None, instance=project)
    return render(request, 'projects/project.html', {
        'active': 2,
        'project': project,
        'todo': task_todo,
        'doing': task_doing,
        'done': task_done,
        'taken_tasks': taken_tasks,
        'addMemberForm': memberForm,
        'projectForm': projectForm
    })


@login_required
@can_edit_project
def update_project_info(request, pk):
    project = Project.objects.get(pk=pk)
    project_form = ProjectForm(request.POST or None, instance=project)
    if project_form.is_valid():
        project_form.save()
        messages.success(request, 'Le projet a bien été modifié')
        return redirect(reverse('projects:project', kwargs={'pk': pk}))
    messages.error(request, 'Erreur dans la modification du projet.')
    return project(request, pk, project_form=project_form)


@login_required
@can_edit_project
def add_user_to_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    member_form = AddMemberForm(request.POST or None, projectId=pk)
    if member_form.is_valid():
        member = member_form.cleaned_data['member']
        if member in project.users.all():
            messages.error(request, 'Cet utilisateur est déjà dans le projet')
        else:
            project.users.add(member)
            messages.success(request, "L'utilisateur a bien été ajouté")
        return redirect(reverse('projects:project', kwargs={'pk': pk}))
    return project(request, pk, member_form=member_form)


@login_required
@can_edit_project
def delete_user_from_project(request, pk, user_id):
    project = Project.objects.get(pk=pk)
    user = User.objects.get(pk=user_id)
    if(user not in project.users.all()):
        messages.error(request, "L'utilisateur n'est pas dans le projet")
    else:
        project.users.remove(user)
        messages.success(request, "L'utilisateur a bien été retiré du projet")
    return redirect(reverse('projects:project', kwargs={'pk': pk}))


@login_required
@admin_required
def manage_projects(request):
    projects = Project.objects.all()
    return render(
        request,
        'projects/manageProjects.html',
        {'projects': projects}
    )


@login_required
@can_edit_project
def change_state(request, pk):
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
    return redirect(redirect('home'))


@login_required
@can_edit_project
def delete_project(request, pk):
    try:
        project = Project.objects.get(pk=pk)
    except DoesNotExist:
        messages.error(request, 'Ce projet n\'existe pas')
        return redirect(reverse('home'))
    project.delete()
    messages.success(request, 'Le projet a bien été supprimé')
    return redirect(request.GET.get('next', reverse('home')))


@login_required
@can_edit_project
def new_tag(request, pk):
    form = TagForm(request.POST or None)
    project = get_object_or_404(Project, pk=pk)
    if(form.is_valid()):
        form.instance.project = project
        form.save()
        messages.success(request, 'Le tag a bien été créé')
        return redirect(reverse('projects:project', kwargs={"pk": pk}))
    return render(request, 'form.html', {
        'form': form,
        'title': 'Nouveau tag',
        'bouton': 'Créer le tag',
        'icon': 'star'
    })


@login_required
@can_edit_project
def edit_tag(request, pk, tagId):
    try:
        tag = Tag.objects.get(pk=tagId)
    except DoesNotExist:
        messages.error(request, 'Ce tag n\'existe pas')
        return redirect(reverse('home'))
    form = TagForm(request.POST or None, instance=tag)
    if(form.is_valid()):
        form.save()
        messages.success(request, 'Le tag a bien été modifié')
        return redirect(reverse('projects:project', kwargs={'pk': pk}))
    return render(request, 'form.html', {
        'form': form,
        'title': 'Modification du tag ' + tag.name,
        'bouton': 'Modifier',
        'icon': 'pencil-alt'
    })


@login_required
@can_edit_project
def delete_tag(request, pk, tagId):
    try:
        tag = Tag.objects.get(pk=tagId)
    except DoesNotExist:
        messages.error(request, "Ce tag n'existe pas")
        return redirect(reverse('home'))
    tag.delete()
    messages.success(request, "Le tag a bien été supprimé")
    return redirect(reverse('projects:project', kwargs={'pk': pk}))


@login_required
@member_required
def new_task(request, pk):
    active = 2
    project = Project.objects.get(pk=pk)
    form = TaskForm(project, request.POST or None)
    if(form.is_valid()):
        form.save()
        messages.success(request, 'La tâche a été créée.')
        return redirect(reverse('projects:project', kwargs={"pk": pk}))
    return render(request, 'form.html', {
        'active': active,
        'form': form,
        'icon': 'star',
        'bouton': 'Créer la tâche',
        'title': 'Nouvelle tâche de '+project.title
    })


@login_required
@can_edit_project
def change_task_status(request, pk, taskId, newStatus):
    cor = {'todo': Task.State.TODO,
           'doing': Task.State.DOING, 'done': Task.State.DONE}
    try:
        task = Task.objects.get(pk=taskId)
    except DoesNotExist:
        messages.error(request, "La tâche n'existe pas")
        return redirect(reverse('home'))
    try:
        task.status = cor[newStatus]
    except IndexError:
        messages.error(request, "Le status demandé n'existe pas")
        return redirect(reverse('home'))
    task.save()
    messages.success(request, "La tâche est passée en " + newStatus)
    url_next = request.GET.get('next', reverse(
        'projects:project', kwargs={'pk': pk}))
    return redirect(url_next)


@login_required
def delete_task(request, taskId):
    try:
        task = Task.objects.get(pk=taskId)
    except DoesNotExist:
        messages.error(request, "La tâche n'existe pas")
        return redirect(reverse('home'))
    task.delete()
    messages.success(request, "La tâche a bien été supprimée")
    next_url = request.GET.get(
        'next',
        reverse('projects:project', kwargs={'pk': task.project.pk})
    )
    return redirect(next_url)


@login_required
def paps(request, taskId):
    try:
        task = Task.objects.get(pk=taskId)
    except DoesNotExist:
        messages.error(request, "La tâche n'existe pas")
        return redirect(reverse('home'))
    task.userAssigned = request.user
    task.save()
    messages.success(request, "Vous avez paspé la tâche. Au boulot !")
    return redirect(reverse(
        'projects:project',
        kwargs={'pk': task.project.pk}
    ))


@login_required
def depaps(request, taskId):
    try:
        task = Task.objects.get(pk=taskId)
    except DoesNotExist:
        messages.error(request, "La tâche n'existe pas")
        return redirect(reverse('home'))
    if(task.userAssigned != request.user):
        messages.error(
            request,
            "Vous ne pouvez pas depaps une tâche que vous n'avez pas papsée"
        )
        return redirect(reverse(
            'projects:project',
            kwargs={'pk': task.project.pk}
        ))
    else:
        task.userAssigned = None
        task.save()
        messages.success(request, "Depaps réussi (flemmard)")
        next_url = request.GET.get(
            'next',
            reverse('projects:project', kwargs={'pk': task.project.pk})
        )
        return redirect(next_url)

@login_required
@member_required
def change_task(request, pk, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except DoesNotExist:
        messages.error(request, "La tâche n'existe pas")
        return redirect(reverse('home'))
    f = TaskForm(task.project, request.POST or None, instance=task)
    if(f.is_valid()):
        f.save()
        messages.success(request, "La tâche a bien été modifiée")
        return redirect(reverse('project', kwargs={'id':task.project.pk}))
    return render(request, 'form.html', {'form': f, 'title': 'Modification de '+task.title, 'bouton': 'Modifier', 'icon': 'pencil-alt'})
