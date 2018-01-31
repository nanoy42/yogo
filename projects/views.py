from django.shortcuts import render

# Create your views here.


def myprojects(request):
    projects = request.user.membered_projects.all()
    active = 2
    return render(request, 'projects/myprojects.html', {'projects': projects, 'active': active})
