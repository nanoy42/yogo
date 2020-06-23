from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
    path("logout", views.logout_view, name="logout"),
    path("login", views.login_view, name="login"),
    path("manage-users", views.manage_users, name="manage-users"),
    path("profile", views.profile, name="profile"),
    path("add-admin/<int:user_id>", views.add_admin, name="add-admin"),
    path("remove-admin/<int:user_id>", views.remove_admin, name="remove-admin"),
    path("remove-user/<int:user_id>", views.remove_user, name="remove-user"),
]
