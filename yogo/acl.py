from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import Group
from .utils import is_admin


class ProjectAdminMixin(object):
    def dispatch(self, request, *args, **kwargs):
        return project_admin_required(self.model)(super().dispatch)(request, *args, **kwargs)

def project_admin_required(model, field='pk', url_arg='pk'):
    def decorator(view):
        def wrapper(request, *args, **kwargs):
            project = get_object_or_404(model, **{field: kwargs[url_arg]}).get_project()
            ok = request.user in project.admins.all() or is_admin(request.user)
            if not ok:
                messages.error(
                    request, "Vous ne pouvez pas modifier ce projet.")
                return redirect(reverse("projects:myprojects"))
            return view(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view):
    def wrapper(request, *args, **kwargs):
        if not is_admin(request.user):
            messages.error(
                request, "Cette action requiert les droits admnistrateurs.")
            return redirect(reverse("projects:myprojects"))
        return view(request, *args, **kwargs)
    return wrapper


def member_required(model, field='pk', url_arg='pk'):
    def decorator(view):
        def wrapper(request, *args, **kwargs):
            project = get_object_or_404(model, **{field: kwargs[url_arg]}).get_project()
            admins, _ = Group.objects.get_or_create(name="admin")
            ok = request.user in project.users.all() or request.user in admins.user_set.all()
            if not ok:
                messages.error(
                    request, "Vous ne pouvez pas accéder à ce projet.")
                return redirect(reverse("projects:myprojects"))
            return view(request, *args, **kwargs)
        return wrapper
    return decorator
