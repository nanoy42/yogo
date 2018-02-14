from django.urls import path
from . import views

app_name = "projects"
urlpatterns = [
    path('myprojects', views.myprojects, name="myprojects"),
    path('mytasks', views.mytasks, name="mytasks"),
    path('newproject', views.newProject, name="newproject"),
    path('project/<int:id>', views.project, name="project"),
    path('deleteUserFromProject/<int:project_id>/<int:user_id>', views.deleteUserFromProject, name="deleteUserFromProject"),
    path('manageProjects', views.manageProjects, name="manageProjects"),
    path('changeState/<int:projectId>', views.changeState, name="changeState"),
    path('deleteProject/<int:projectId>/<str:nextUrl>', views.deleteProject, name="deleteProject"),
    path('manageTags', views.manageTags, name="manageTags"),
    path('newTag', views.newTag, name="newTag"),
    path('editTag/<int:tagId>', views.editTag, name="editTag"),
    path('deleteTag/<int:tagId>', views.deleteTag, name="deleteTag"),
    path('newTask/<int:projectId>', views.newTask, name="newTask"),
    path('changeTaskStatus/<int:taskId>/<str:newStatus>', views.changeTaskStatus, name="changeTaskStatus"),
    path('deleteTask/<int:taskId>', views.deleteTask, name="deleteTask"),
    path('paps/<int:taskId>', views.paps, name="paps"),
    path('depaps/<int:taskId>', views.depaps, name="depaps"),
]
