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
    path('delete_project/<int:pk>', views.ProjectDelete.as_view(), name="deleteProject"),
    path('<int:pk>/newTag', views.new_tag, name="newTag"),
    path('editTag/<int:tagId>', views.edit_tag, name="editTag"),
    path('deleteTag/<int:tagId>', views.delete_tag, name="deleteTag"),
    path('newTask/<int:pk>', views.new_task, name="newTask"),
    path('changeTaskStatus/<int:taskId>/<str:new_status>', views.change_task_status, name="changeTaskStatus"),
    path('deleteTask/<int:taskId>', views.delete_task, name="deleteTask"),
    path('paps/<int:taskId>', views.paps, name="paps"),
    path('depaps/<int:taskId>', views.depaps, name="depaps"),
    path('change_task/<int:task_id>', views.change_task, name="change_task"),
    path('<int:pk>/addUserToProjectAdmins/<int:user_id>', views.add_user_to_project_admins, name="addUserToProjectAdmins"),
    path('<int:pk>/removeUserFromProjectAdmins/<int:user_id>', views.remove_user_from_project_admins, name="removeUserFromProjectAdmins"),
]
