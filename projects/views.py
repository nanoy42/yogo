from django.shortcuts import render

# Create your views here.


def myprojects(request):
    projects = request.user.membered_projects.all()
    for project in projects:
        projects.taskCount = project.task_set.count()
    return render(request, 'projects/myprojects.html', {'projects': projects})
