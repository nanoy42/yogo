import secrets

import telepot
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import DeleteView

from yogo.acl import (
    ProjectAdminMixin,
    admin_required,
    member_required,
    project_admin_required,
)
from .forms import AddMemberForm, ProjectForm, TagForm, TaskForm
from .models import Project, Tag, Task


@login_required
def my_projects(request):
    """Display every projects membered by the user."""
    projects = request.user.membered_projects.all()
    active = 2
    return render(
        request, "projects/myprojects.html", {"projects": projects, "active": active}
    )


@login_required
def my_tasks(request):
    """Display every task assigned to the user."""
    active = 3
    todo_tasks = Task.objects.filter(userAssigned=request.user).filter(
        status=Task.State.TODO
    )
    doing_tasks = Task.objects.filter(userAssigned=request.user).filter(
        status=Task.State.DOING
    )
    done_tasks = Task.objects.filter(userAssigned=request.user).filter(
        status=Task.State.DONE
    )
    return render(
        request,
        "projects/mytasks.html",
        {
            "active": active,
            "todo": todo_tasks,
            "doing": doing_tasks,
            "done": done_tasks,
            "next": True,
        },
    )


@login_required
def new_project(request):
    """Creates a new project owned by the user."""
    active = 2
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        form.save()
        form.instance.admins.add(request.user)
        form.instance.users.add(request.user)
        form.save()
        messages.success(request, "Projet créé.")
        return redirect(reverse("projects:project", kwargs={"pk": form.instance.pk}))
    return render(
        request,
        "form.html",
        {
            "form": form,
            "active": active,
            "title": "Nouveau projet",
            "bouton": "Créer le projet",
            "icon": "star",
        },
    )


@login_required
@member_required(Project)
def project(request, pk, project_form=None, member_form=None):
    """Display a project
    Args :
        pk : Primary key of the project.
        project_form : A ProjectForm instance to be used if it is not None.
        member_form : An AddMemberForm instance to be used if it is not None.
    """
    project = Project.objects.get(pk=pk)
    task_todo = project.task_set.filter(status=Task.State.TODO)
    task_doing = project.task_set.filter(status=Task.State.DOING)
    task_done = project.task_set.filter(status=Task.State.DONE)
    taken_tasks = []
    for user in project.users.all():
        taken_tasks.append(project.task_set.filter(userAssigned=user).count())
    member_form = member_form or AddMemberForm(request.POST or None, projectId=pk)
    project_form = project_form or ProjectForm(request.POST or None, instance=project)
    return render(
        request,
        "projects/project.html",
        {
            "active": 2,
            "project": project,
            "todo": task_todo,
            "doing": task_doing,
            "done": task_done,
            "taken_tasks": taken_tasks,
            "addMemberForm": member_form,
            "projectForm": project_form,
        },
    )


@login_required
@project_admin_required(Project)
def update_project_info(request, pk):
    """Updates a project informations.

    Intended to be called from the `project` view.
    Args:
        pk : Primary key of the project.
    """
    project = Project.objects.get(pk=pk)
    project_form = ProjectForm(request.POST or None, instance=project)
    if project_form.is_valid():
        project_form.save()
        messages.success(request, "Le projet a bien été modifié")
        return redirect(reverse("projects:project", kwargs={"pk": pk}))
    messages.error(request, "Erreur dans la modification du projet.")
    return project(request, pk, project_form=project_form)


@login_required
def add_user_to_project(request, pk):
    """Adds an user to a project.

    Intended to be called from the `project` view.
    Args:
        pk : Primary key of the project.
    """
    project = get_object_or_404(Project, pk=pk)
    member_form = AddMemberForm(request.POST or None, projectId=pk)
    if member_form.is_valid():
        member = member_form.cleaned_data["member"]
        if member in project.users.all():
            messages.error(request, "Cet utilisateur est déjà dans le projet")
        else:
            project.users.add(member)
            messages.success(request, "L'utilisateur a bien été ajouté")
    return redirect(reverse("projects:project", kwargs={"pk": pk}))


@login_required
@project_admin_required(Project)
def delete_user_from_project(request, pk, user_id):
    """Remove an user from a project.

    Args:
        pk : The primary key of the project.
        user_id : The primary key of the user.
    """
    project = Project.objects.get(pk=pk)
    user = User.objects.get(pk=user_id)
    if user not in project.users.all():
        messages.error(request, "L'utilisateur n'est pas dans le projet")
    else:
        project.users.remove(user)
        messages.success(request, "L'utilisateur a bien été retiré du projet")
    return redirect(reverse("projects:project", kwargs={"pk": pk}))


@login_required
@admin_required
def manage_projects(request):
    """Show a management view for every project of the site."""
    projects = Project.objects.all()
    return render(request, "projects/manage_projects.html", {"projects": projects})


@login_required
@project_admin_required(Project)
def change_state(request, pk):
    """Change the state of a project.

    Args:
        pk : The primary key of the project.
    """
    project = get_object_or_404(Project, pk=pk)
    if project is not None:
        project.active = 1 - project.active
        project.save()
        messages.success(request, "Le statut du projet a bien été modifié")
    else:
        messages.error(request, "Ce projet n'existe pas")
    return redirect(redirect("home"))


@login_required
@project_admin_required(Project)
def new_tag(request, pk):
    """Create a tag for a project.

    Args:
        pk : The primary key of the project.
    """
    form = TagForm(request.POST or None)
    project = get_object_or_404(Project, pk=pk)
    if form.is_valid():
        form.instance.project = project
        form.save()
        messages.success(request, "Le tag a bien été créé")
        return redirect(reverse("projects:project", kwargs={"pk": pk}))
    return render(
        request,
        "form.html",
        {
            "form": form,
            "title": "Nouveau tag",
            "bouton": "Créer le tag",
            "icon": "star",
        },
    )


@login_required
@project_admin_required(Tag, url_arg="tag_id")
def edit_tag(request, tag_id):
    """Edit the tag of a project.

    Args:
        tag_id : The primary key of the tag.
    """
    tag = get_object_or_404(Tag, pk=tag_id)
    form = TagForm(request.POST or None, instance=tag)
    if form.is_valid():
        form.save()
        messages.success(request, "Le tag a bien été modifié")
        return redirect(reverse("projects:project", kwargs={"pk": tag.project.pk}))
    return render(
        request,
        "form.html",
        {
            "form": form,
            "title": "Modification du tag " + tag.name,
            "bouton": "Modifier",
            "icon": "pencil-alt",
        },
    )


@login_required
@project_admin_required(Tag, url_arg="tag_id")
def delete_tag(request, tag_id):
    """Delete a tag of a project.

    Args:
        tag_id : The primary key of the tag.
    """
    tag = get_object_or_404(Tag, pk=tag_id)
    tag.delete()
    messages.success(request, "Le tag a bien été supprimé")
    return redirect(reverse("projects:project", kwargs={"pk": tag.project.pk}))


@login_required
@member_required(Project)
def new_task(request, pk):
    """Create a task for a project.

    Args:
        pk : The primary key of the project.
    """
    active = 2
    project = Project.objects.get(pk=pk)
    form = TaskForm(project, request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "La tâche a été créée.")
        return redirect(reverse("projects:project", kwargs={"pk": pk}))
    return render(
        request,
        "form.html",
        {
            "active": active,
            "form": form,
            "icon": "star",
            "bouton": "Créer la tâche",
            "title": "Nouvelle tâche de " + project.title,
        },
    )


@login_required
@member_required(Task, url_arg="task_id")
def change_task_status(request, task_id, new_status):
    """Change the status of a task.

    Args:
        task_id : The primary key of the task.
        new_status : The new status for the task
            (must be in {'todo','doing','done'})
    """
    cor = {"todo": Task.State.TODO, "doing": Task.State.DOING, "done": Task.State.DONE}
    task = get_object_or_404(Task, pk=task_id)
    try:
        task.status = cor[new_status]
    except IndexError:
        messages.error(request, "Le status demandé n'existe pas")
        return redirect(reverse("home"))
    task.save()
    messages.success(request, "La tâche est passée en " + new_status)
    url_next = request.GET.get(
        "next", reverse("projects:project", kwargs={"pk": task.get_project().pk})
    )
    return redirect(url_next)


@login_required
@member_required(Task, url_arg="task_id")
def delete_task(request, task_id):
    """Delete a task

    Args:
        task_id : The primary key of the task.
    """
    task = get_object_or_404(Task, pk=task_id)
    task.delete()
    messages.success(request, "La tâche a bien été supprimée")
    next_url = request.GET.get(
        "next", reverse("projects:project", kwargs={"pk": task.project.pk})
    )
    return redirect(next_url)


@login_required
@member_required(Task, url_arg="task_id")
def paps(request, task_id):
    """Assign a task to the current user.

    Args:
        task_id : The primary key of the task.
    """
    task = get_object_or_404(Task, pk=task_id)
    task.userAssigned = request.user
    task.save()
    messages.success(request, "Vous avez paspé la tâche. Au boulot !")
    next_url = request.GET.get(
        "next", reverse("projects:project", kwargs={"pk": task.project.pk})
    )
    return redirect(next_url)


@login_required
@member_required(Project)
def depaps(request, task_id):
    """Deassign a task to the active user.

    Args:
        task_id : The primary key of the task.
    """
    task = get_object_or_404(Task, pk=task_id)
    if task.userAssigned != request.user:
        messages.error(
            request, "Vous ne pouvez pas depaps une tâche que vous n'avez pas papsée"
        )
        return redirect(reverse("projects:project", kwargs={"pk": task.project.pk}))
    else:
        task.userAssigned = None
        task.save()
        messages.success(request, "Depaps réussi (flemmard)")
        next_url = request.GET.get(
            "next", reverse("projects:project", kwargs={"pk": task.project.pk})
        )
        return redirect(next_url)


@login_required
@member_required(Task, url_arg="task_id")
def change_task(request, task_id):
    """Edit a task.

    Args:
        task_id : The primary key of the task.
    """
    task = get_object_or_404(Task, pk=task_id)
    f = TaskForm(task.project, request.POST or None, instance=task)
    if f.is_valid():
        f.save()
        messages.success(request, "La tâche a bien été modifiée")
        return redirect(reverse("projects:project", kwargs={"pk": task.project.pk}))
    return render(
        request,
        "form.html",
        {
            "form": f,
            "title": "Modification de " + task.title,
            "bouton": "Modifier",
            "icon": "pencil-alt",
        },
    )


@login_required
@project_admin_required(Project)
def add_user_to_project_admins(request, pk, user_id):
    project = get_object_or_404(Project, pk=pk)
    user = get_object_or_404(User, pk=user_id)
    project.admins.add(user)
    messages.success(request, "L'utilisateur a reçu les droits admins")
    return redirect(reverse("projects:project", kwargs={"pk": pk}))


@login_required
@project_admin_required(Project)
def remove_user_from_project_admins(request, pk, user_id):
    project = get_object_or_404(Project, pk=pk)
    user = get_object_or_404(User, pk=user_id)
    if user not in project.admins.all():
        messages.error(request, "L'utilisateur ne possède pas les droits admins")
    elif project.admins.all().count() == 1:
        messages.error(request, "Vous ne pouvez pas laisser un projet sans admins")
    else:
        project.admins.remove(user)
        messages.success(
            request, "Les droits admins ont bien été retirés à l'utilisateur"
        )
    return redirect(reverse("projects:project", kwargs={"pk": pk}))


class ProjectDelete(ProjectAdminMixin, LoginRequiredMixin, DeleteView):
    model = Project
    success_url = reverse_lazy("home")
    success_message = "Le projet a bien été supprimé"

    def delete(self, request, *args, **kwargs):
        self.pk = self.get_object().pk
        self.title = self.get_object().title
        messages.success(self.request, self.success_message)
        return super(ProjectDelete, self).delete(request, *args, **kwargs)
