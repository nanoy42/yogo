from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from .models import Task, Project, Tag, Bot
from .forms import ProjectForm, AddMemberForm, TagForm, TaskForm, BotForm, VerifyForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from yogo.acl import project_admin_required, admin_required, member_required, ProjectAdminMixin
from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from yogo.settings import TELEGRAM_TOKEN
import telepot, secrets

@login_required
def my_projects(request):
    """Display every projects membered by the user."""
    projects = request.user.membered_projects.all()
    active = 2
    return render(request, 'projects/myprojects.html', {
        'projects': projects,
        'active': active
    })


@login_required
def my_tasks(request):
    """Display every task assigned to the user."""
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
        'done': done_tasks,
        'next': True
    })


@login_required
def new_project(request):
    """Creates a new project owned by the user."""
    active = 2
    form = ProjectForm(request.POST or None)
    if(form.is_valid()):
        form.save()
        form.instance.admins.add(request.user)
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
    member_form = member_form or AddMemberForm(
        request.POST or None, projectId=pk)
    project_form = project_form or ProjectForm(
        request.POST or None, instance=project)
    return render(request, 'projects/project.html', {
        'active': 2,
        'project': project,
        'todo': task_todo,
        'doing': task_doing,
        'done': task_done,
        'taken_tasks': taken_tasks,
        'addMemberForm': member_form,
        'projectForm': project_form
    })


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
        tbot = telepot.Bot(TELEGRAM_TOKEN)
        for bot in project_form.instance.bot_set.all():
            if(bot.verified):
                msg = "Modification du projet " + project_form.instance.title + "\nTitre : " + project_form.instance.title + "\nDescription : " + project_form.instance.description + "\n" + request.META['HTTP_HOST'] + "/projects/" + str(project.pk)
                tbot.sendMessage(bot.chatId, msg)
        messages.success(request, 'Le projet a bien été modifié')
        return redirect(reverse('projects:project', kwargs={'pk': pk}))
    messages.error(request, 'Erreur dans la modification du projet.')
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
        member = member_form.cleaned_data['member']
        if member in project.users.all():
            messages.error(request, 'Cet utilisateur est déjà dans le projet')
        else:
            project.users.add(member)
            tbot = telepot.Bot(TELEGRAM_TOKEN)
            for bot in project.bot_set.all():
                if(bot.verified):
                    msg = "Modification du projet " + project.title + "\nL'utilisateur " + member.username + " a été ajouté au projet.\n" + request.META['HTTP_HOST'] + "/projects/" + str(project.pk)
                    tbot.sendMessage(bot.chatId, msg)
            messages.success(request, "L'utilisateur a bien été ajouté")
    return redirect(reverse('projects:project', kwargs={'pk': pk}))


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
    if(user not in project.users.all()):
        messages.error(request, "L'utilisateur n'est pas dans le projet")
    else:
        project.users.remove(user)
        tbot = telepot.Bot(TELEGRAM_TOKEN)
        for bot in project.bot_set.all():
            if(bot.verified):
                msg = "Modification du projet " + project.title + "\nL'utilisateur " + user.username + " a été retiré au projet.\n" + request.META['HTTP_HOST'] + "/projects/" + str(project.pk)
                tbot.sendMessage(bot.chatId, msg)
        messages.success(request, "L'utilisateur a bien été retiré du projet")
    return redirect(reverse('projects:project', kwargs={'pk': pk}))


@login_required
@admin_required
def manage_projects(request):
    """Show a management view for every project of the site."""
    projects = Project.objects.all()
    return render(
        request,
        'projects/manageProjects.html',
        {'projects': projects}
    )


@login_required
@project_admin_required(Project)
def change_state(request, pk):
    """Change the state of a project.

    Args:
        pk : The primary key of the project.
    """
    try:
        project = Project.objects.get(pk=pk)
    except DoesNotExist:
        project = None
    if(project is not None):
        project.active = 1 - project.active
        project.save()
        messages.success(request, 'Le statut du projet a bien été modifié')
    else:
        messages.error(request, 'Ce projet n\'existe pas')
    return redirect(redirect('home'))


@login_required
@project_admin_required(Project)
def new_tag(request, pk):
    """Create a tag for a project.

    Args:
        pk : The primary key of the project.
    """
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
@project_admin_required(Tag, url_arg='tagId')
def edit_tag(request, tagId):
    """Edit the tag of a project.

    Args:
        tagId : The primary key of the tag.
    """
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
@project_admin_required(Tag, url_arg='tagId')
def delete_tag(request, tagId):
    """Delete a tag of a project.

    Args:
        tagId : The primary key of the tag.
    """
    try:
        tag = Tag.objects.get(pk=tagId)
    except DoesNotExist:
        messages.error(request, "Ce tag n'existe pas")
        return redirect(reverse('home'))
    tag.delete()
    messages.success(request, "Le tag a bien été supprimé")
    return redirect(reverse('projects:project', kwargs={'pk': pk}))


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
    if(form.is_valid()):
        form.save()
        tbot = telepot.Bot(TELEGRAM_TOKEN)
        for bot in project.bot_set.all():
            if(bot.verified):
                msg = "Création de la tache " + form.instance.title + " du projet " + form.instance.project.title + "\nTitre : " + form.instance.title + "\n Description : " + form.instance.description + "\n Papsée par : " + str(form.instance.userAssigned) + "\n" + request.META['HTTP_HOST'] + "/projects/" + str(form.instance.project.pk)
                tbot.sendMessage(bot.chatId, msg)
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
@member_required(Task, url_arg='taskId')
def change_task_status(request, taskId, new_status):
    """Change the status of a task.

    Args:
        taskId : The primary key of the task.
        new_status : The new status for the task
            (must be in {'todo','doing','done'})
    """
    cor = {
        'todo': Task.State.TODO,
        'doing': Task.State.DOING,
        'done': Task.State.DONE
    }
    try:
        task = Task.objects.get(pk=taskId)
    except DoesNotExist:
        messages.error(request, "La tâche n'existe pas")
        return redirect(reverse('home'))
    try:
        task.status = cor[new_status]
    except IndexError:
        messages.error(request, "Le status demandé n'existe pas")
        return redirect(reverse('home'))
    task.save()
    tbot = telepot.Bot(TELEGRAM_TOKEN)
    for bot in task.project.bot_set.all():
        if(bot.verified):
            msg = "La tache " + task.title + " du projet " + task.project.title + " est passée en " + new_status + "\n" + request.META['HTTP_HOST'] + "/projects/" + str(task.project.pk)
            tbot.sendMessage(bot.chatId, msg)
    messages.success(request, "La tâche est passée en " + new_status)
    url_next = request.GET.get('next', reverse(
        'projects:project', kwargs={'pk': task.get_project().pk}))
    return redirect(url_next)


@login_required
@member_required(Task, url_arg="taskId")
def delete_task(request, taskId):
    """Delete a task

    Args:
        taskId : The primary key of the task.
    """
    try:
        task = Task.objects.get(pk=taskId)
    except DoesNotExist:
        messages.error(request, "La tâche n'existe pas")
        return redirect(reverse('home'))
    tbot = telepot.Bot(TELEGRAM_TOKEN)
    for bot in task.project.bot_set.all():
        if(bot.verified):
            msg = "La tâche " + task.title + " a été supprimée du projet " + task.project.title + "\n" + request.META['HTTP_HOST'] + "/projects/" + str(task.project.pk)
            tbot.sendMessage(bot.chatId, msg)
    task.delete()
    messages.success(request, "La tâche a bien été supprimée")
    next_url = request.GET.get(
        'next',
        reverse('projects:project', kwargs={'pk': task.project.pk})
    )
    return redirect(next_url)


@login_required
@member_required(Task, url_arg="taskId")
def paps(request, taskId):
    """Assign a task to the current user.

    Args:
        taskId : The primary key of the task.
    """
    try:
        task = Task.objects.get(pk=taskId)
    except DoesNotExist:
        messages.error(request, "La tâche n'existe pas")
        return redirect(reverse('home'))
    task.userAssigned = request.user
    task.save()
    tbot = telepot.Bot(TELEGRAM_TOKEN)
    for bot in task.project.bot_set.all():
        if(bot.verified):
            msg = "La tache " + task.title + " du projet " + task.project.title + " a été papsée par " + request.user.username + "\n" + request.META['HTTP_HOST'] + "/projects/" + str(task.project.pk)
            tbot.sendMessage(bot.chatId, msg)
    messages.success(request, "Vous avez paspé la tâche. Au boulot !")
    next_url = request.GET.get(
            'next',
            reverse('projects:project', kwargs={'pk': task.project.pk})
    )
    return redirect(next_url)


@login_required
@member_required(Project)
def depaps(request, taskId):
    """Deassign a task to the active user.

    Args:
        taskId : The primary key of the task.
    """
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
        tbot = telepot.Bot(TELEGRAM_TOKEN)
        for bot in task.project.bot_set.all():
            if(bot.verified):
                msg = request.user.username + " a dépaps la tache " + task.title + " du projet" + task.project.title + "\n" + request.META['HTTP_HOST'] + "/projects/" + str(task.project.pk)
                tbot.sendMessage(bot.chatId, msg)
        messages.success(request, "Depaps réussi (flemmard)")
        next_url = request.GET.get(
            'next',
            reverse('projects:project', kwargs={'pk': task.project.pk})
        )
        return redirect(next_url)

@login_required
@member_required(Task, url_arg='task_id')
def change_task(request, task_id):
    """Edit a task.

    Args:
        task_id : The primary key of the task.
    """
    try:
        task = Task.objects.get(pk=task_id)
    except DoesNotExist:
        messages.error(request, "La tâche n'existe pas")
        return redirect(reverse('home'))
    f = TaskForm(task.project, request.POST or None, instance=task)
    if(f.is_valid()):
        f.save()
        tbot = telepot.Bot(TELEGRAM_TOKEN)
        for bot in f.instance.project.bot_set.all():
            if(bot.verified):
                msg = "Modification de la tache " + f.instance.title + " du projet " + f.instance.project.title + "\nTitre : " + f.instance.title + "\n Description : " + f.instance.description + "\n Papsée par : " + str(f.instance.userAssigned) + "\n" + request.META['HTTP_HOST'] + "/projects/" + str(f.instance.project.pk)
                tbot.sendMessage(bot.chatId, msg)
        messages.success(request, "La tâche a bien été modifiée")
        return redirect(reverse('projects:project', kwargs={'pk':task.project.pk}))
    return render(request, 'form.html', {'form': f, 'title': 'Modification de '+task.title, 'bouton': 'Modifier', 'icon': 'pencil-alt'})



@login_required
@project_admin_required(Project)
def add_user_to_project_admins(request, pk, user_id):
    try:
        project = Project.objects.get(pk=pk)
        user = User.objects.get(pk=user_id)
    except DoesNotExist:
        messages.error(request, "Le projet ou l'utilisateur n'existe pas")
        return redirect(reverse('home'))
    project.admins.add(user)
    tbot = telepot.Bot(TELEGRAM_TOKEN)
    for bot in project.bot_set.all():
        if(bot.verified):
            msg = "Modification du projet " + project.title + "\nL'utilisateur " + user.username + " a été ajouté au admins du projet.\n" + request.META['HTTP_HOST'] + "/projects/" + str(project.pk)
            tbot.sendMessage(bot.chatId, msg)
    messages.success(request, "L'utilisateur a reçu les droits admins")
    return redirect(reverse(
        'projects:project',
        kwargs={'pk': pk}
    ))


@login_required
@project_admin_required(Project)
def remove_user_from_project_admins(request, pk, user_id):
    try:
        project = Project.objects.get(pk=pk)
        user = User.objects.get(pk=user_id)
    except DoesNotExist:
        messages.error(request, "Le projet ou l'utilisateur n'existe pas")
        return redirect(reverse('home'))
    if(user not in project.admins.all()):
        messages.error(request, "L'utilisateur ne possède pas les droits admins")
    elif(project.admins.all().count() == 1):
        messages.error(request, "Vous ne pouvez pas laisser un projet sans admins")
    else:
        project.admins.remove(user)
        tbot = telepot.Bot(TELEGRAM_TOKEN)
        for bot in project.bot_set.all():
            if(bot.verified):
                msg = "Modification du projet " + project.title + "\nL'utilisateur " + user.username + " a été retiré des admins du projet.\n" + request.META['HTTP_HOST'] + "/projects/" + str(project.pk)
                tbot.sendMessage(bot.chatId, msg)
        messages.success(request, "Les droits admins ont bien été retirés à l'utilisateur")
    return redirect(reverse('projects:project', kwargs={'pk':pk}))

class ProjectDelete(ProjectAdminMixin, LoginRequiredMixin, DeleteView):
    model = Project
    success_url = reverse_lazy('home')
    success_message = "Le projet a bien été supprimé"

    def delete(self, request, *args, **kwargs):
        self.pk = self.get_object().pk
        self.title = self.get_object().title
        self.bots = self.get_object().bot_set.all()
        tbot = telepot.Bot(TELEGRAM_TOKEN)
        for bot in self.bots:
            if(bot.verified):
                msg = "Supression du projet " + self.title
                tbot.sendMessage(bot.chatId, msg)
        messages.success(self.request, self.success_message)
        return super(ProjectDelete, self).delete(request, *args, **kwargs)


@login_required
@project_admin_required(Project)
def addBotToProject(request, pk):
    project = get_object_or_404(Project, pk=pk)
    form = BotForm(request.POST or None)
    if(form.is_valid()):
        form.instance.verified = False
        form.instance.verifyToken = secrets.token_urlsafe(20)
        form.instance.project = project
        form.save()
        bot = telepot.Bot(TELEGRAM_TOKEN)
        try:
            bot.sendMessage(form.instance.chatId, "Veuillez vérifier votre identifiant avec ce token : " + form.instance.verifyToken)
            messages.success(request, "Le bot a bien été créé")
            messages.warning(request, "Vous devez vérifier le bot avant qu'il ne devienne actif")
        except:
            form.instance.delete()
            messages.error(request, "L'id du chat est incorrect")
        return redirect(reverse('projects:project', kwargs={'pk':pk}))
    return render(request, 'form.html', {'form': form, 'title': 'Nouveau bot pour le projet ' + project.title, 'bouton': 'Créer', 'icon': 'star'})


@login_required
@project_admin_required(Bot)
def verifyBot(request, pk):
    bot = get_object_or_404(Bot, pk=pk)
    form = VerifyForm(request.POST or None)
    if(form.is_valid()):
        if(form.data['token'] == bot.verifyToken):
            bot.verified = True
            bot.save()
            tbot = telepot.Bot(TELEGRAM_TOKEN)
            tbot.sendMessage(bot.chatId, "Le bot a bien été vérifié")
            messages.success(request, "Le bot a bien été vérifié")
            return redirect(reverse('projects:project', kwargs={'pk':bot.project.pk}))
        else:
            messages.error(request, "Impossible de vérifier le bot")
    return render(request, "form.html", {
        'form': form,
        'title': 'Vérication d\'un bot',
        'bouton': 'Vérifier',
        'icon': 'check-circle',
    })


@login_required
@project_admin_required(Bot)
def deleteBot(request, pk):
    bot = get_object_or_404(Bot, pk=pk)
    projectId = bot.project.pk
    if(bot.verified):
        tbot = telepot.Bot(TELEGRAM_TOKEN)
        tbot.sendMessage(bot.chatId, "Adieu")
    bot.delete()
    messages.success(request, "Le bot a bien été supprimé")
    return redirect(reverse('projects:project', kwargs={'pk':projectId}))
