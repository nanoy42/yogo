from django.urls import path
from . import views

app_name = "projects"
urlpatterns = [
    path('myprojects', views.myprojects, name="myprojects"),
    path('mytasks', views.mytasks, name="mytasks"),
    path('newproject', views.newProject, name="newproject"),
    path('project/<int:id>', views.project, name="project"),
]
