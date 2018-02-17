from django.urls import path
from . import views

app_name = "projects"
urlpatterns = [
    path('myprojects', views.my_projects, name="myprojects"),
    path('mytasks', views.my_tasks, name="mytasks"),
    path('newproject', views.new_project, name="newproject"),
    path('<int:pk>', views.project, name="project"),
    path('<int:pk>/add-user', views.add_user_to_project, name="add-user"),
    path('<int:pk>/update', views.update_project_info, name="update"),
    path('<int:pk>/deleteUserFromProject/<int:user_id>', views.delete_user_from_project, name="deleteUserFromProject"),
    path('manageProjects', views.manage_projects, name="manageProjects"),
    path('changeState/<int:pk>', views.change_state, name="changeState"),
    path('<int:pk>/delete_project', views.delete_project, name="deleteProject"),
    path('<int:pk>/newTag', views.new_tag, name="newTag"),
    path('<int:pk>/editTag/<int:tagId>', views.edit_tag, name="editTag"),
    path('<int:pk>/deleteTag/<int:tagId>', views.delete_tag, name="deleteTag"),
    path('newTask/<int:pk>', views.new_task, name="newTask"),
    path('<int:pk>/changeTaskStatus/<int:taskId>/<str:newStatus>', views.change_task_status, name="changeTaskStatus"),
    path('deleteTask/<int:taskId>', views.delete_task, name="deleteTask"),
    path('paps/<int:taskId>', views.paps, name="paps"),
    path('depaps/<int:taskId>', views.depaps, name="depaps"),
    path('<int:pk>/change_task/<int:task_id>', views.change_task, name="change_task"),
]
