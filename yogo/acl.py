from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import Group

from projects.models import Project

def can_edit_project(view):
    def wrapper(request, pk, *args, **kwargs):
        project = get_object_or_404(Project, pk=pk)
        admins,_ = Group.objects.get_or_create(name="admin")
        ok = request.user == project.owner or request.user in admins.user_set.all()
        if not ok:
            messages.error(request, "Vous ne pouvez pas modifier ce projet.")
            return redirect(reverse("projects:myprojects"))
        return view(request, pk, *args, **kwargs)
    return wrapper

def admin_required(view):
    def wrapper(request, *args, **kwargs):
        admins,_ = Group.objects.get_or_create(name="admin")
        if not request.user in admins.user_set.all():
            messages.error(request, "Cette action requiert les droits admnistrateurs.")
            return redirect(reverse("projects:myprojects"))
        return view(request, *args, **kwargs)
    return wrapper

def member_required(view):
    def test(request, pk, *args, **kwargs):
        project = get_object_or_404(Project, pk=pk)
        admins,_ = Group.objects.get_or_create(name="admin")
        ok = request.user in project.users.all() or request.user in admins.user_set.all()
        if not ok:
            messages.error(request, "Vous ne pouvez pas accéder à ce projet.")
            return redirect(reverse("projects:myprojects"))
        return view(request, pk, *args, **kwargs)
    return test
