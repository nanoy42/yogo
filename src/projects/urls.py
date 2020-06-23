from django.urls import path

from . import views

app_name = "projects"
urlpatterns = [
    path("myprojects", views.my_projects, name="myprojects"),
    path("mytasks", views.my_tasks, name="mytasks"),
    path("newproject", views.new_project, name="newproject"),
    path("<int:pk>", views.project, name="project"),
    path("<int:pk>/add-user", views.add_user_to_project, name="add-user"),
    path("<int:pk>/update", views.update_project_info, name="update"),
    path(
        "<int:pk>/delete-user-from-project/<int:user_id>",
        views.delete_user_from_project,
        name="delete-user-from-project",
    ),
    path("manage-projects", views.manage_projects, name="manage-projects"),
    path("changeState/<int:pk>", views.change_state, name="changeState"),
    path(
        "delete_project/<int:pk>", views.ProjectDelete.as_view(), name="deleteProject"
    ),
    path("<int:pk>/newTag", views.new_tag, name="newTag"),
    path("edit-tag/<int:tag_id>", views.edit_tag, name="edit-tag"),
    path("delete-tag/<int:tag_id>", views.delete_tag, name="delete-tag"),
    path("newTask/<int:pk>", views.new_task, name="newTask"),
    path(
        "changeTaskStatus/<int:task_id>/<str:new_status>",
        views.change_task_status,
        name="changeTaskStatus",
    ),
    path("delete-task/<int:task_id>", views.delete_task, name="delete-task"),
    path("paps/<int:task_id>", views.paps, name="paps"),
    path("depaps/<int:task_id>", views.depaps, name="depaps"),
    path("change_task/<int:task_id>", views.change_task, name="change_task"),
    path(
        "<int:pk>/add-user-project-admins/<int:user_id>",
        views.add_user_to_project_admins,
        name="add-user-project-admins",
    ),
    path(
        "<int:pk>/remove-user-project-admins/<int:user_id>",
        views.remove_user_from_project_admins,
        name="remove-user-project-admins",
    ),
]
