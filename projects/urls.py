from django.urls import path
from . import views

app_name = "projects"
urlpatterns = [
    path('myprojects', views.myprojects, name="myprojects"),
    path('mytasks', views.mytasks, name="mytasks"),
    path('newproject', views.newProject, name="newproject"),
    path('project/<int:id>', views.project, name="project"),
    path('deleteUserFromProject/<int:project_id>/<int:user_id>', views.deleteUserFromProject, name="deleteUserFromProject"),
]
