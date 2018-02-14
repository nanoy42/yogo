from django.contrib.auth.models import Group

def is_admin(user):
    admins,_ = Group.objects.get_or_create(name="admin")
    return user in admins.user_set.all()
