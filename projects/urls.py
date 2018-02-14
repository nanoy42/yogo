from django.urls import path
from . import views

app_name = "projects"
urlpatterns = [
    path('myprojects', views.myprojects, name="myprojects"),
    path('mytasks', views.mytasks, name="mytasks"),
    path('newproject', views.newProject, name="newproject"),
    path('<int:pk>', views.project, name="project"),
    path('deleteUserFromProject/<int:pk>/<int:user_id>', views.deleteUserFromProject, name="deleteUserFromProject"),
    path('manageProjects', views.manageProjects, name="manageProjects"),
    path('changeState/<int:pk>', views.changeState, name="changeState"),
    path('deleteProject/<int:pk>', views.deleteProject, name="deleteProject"),
    path('<int:pk>/newTag', views.newTag, name="newTag"),
    path('<int:pk>/editTag/<int:tagId>', views.editTag, name="editTag"),
    path('<int:pk>/deleteTag/<int:tagId>', views.deleteTag, name="deleteTag"),
    path('newTask/<int:pk>', views.newTask, name="newTask"),
    path('<int:pk>/changeTaskStatus/<int:taskId>/<str:newStatus>', views.changeTaskStatus, name="changeTaskStatus"),
    path('deleteTask/<int:taskId>', views.deleteTask, name="deleteTask"),
    path('paps/<int:taskId>', views.paps, name="paps"),
    path('depaps/<int:taskId>', views.depaps, name="depaps"),
]
