from django.urls import path
from . import views

app_name = "users"
urlpatterns = [path('logout', views.logout_view, name="logout"),
    path('login', views.login_view, name="login"),
    path('manageUsers', views.manageUsers, name="manageUsers"),
    path('profile', views.profile, name="profile"),
    path('addAdmin/<int:user_id>', views.add_admin, name="addAdmin"),
    path('removeAdmin/<int:user_id>', views.remove_admin, name="removeAdmin"),
    path('removeUser/<int:user_id>', views.remove_user, name="removeUser"),
    path('updateTelegramInfos', views.update_telegram_infos, name="updateTelegramInfos"),
    path('verifyToken', views.verifyToken, name="verifyToken"),
]

