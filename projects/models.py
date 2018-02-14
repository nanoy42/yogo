from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Project(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='owned_projects')
    creationDate = models.DateField(auto_now_add=True)
    users = models.ManyToManyField(User, related_name='membered_projects')
    active = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

    def is_member(self, user):
        return user in self.users.all()

    def is_owner(self, user):
        return user == self.owner


class Tag(models.Model):
    class Color:
        BLUE = 'primary'
        GREY = 'secondary'
        GREEN = 'success'
        RED = 'danger'
        YELLOW = 'warning'
        LIGHTBLUE = 'info'
        WHITE = 'light'
        BLACK = 'DARK'
    COLOR_CHOICES = (
        (Color.BLUE, 'Bleu'),
        (Color.GREY, 'Gris'),
        (Color.GREEN, 'Vert'),
        (Color.RED, 'Rouge'),
        (Color.YELLOW, 'Jaune'),
        (Color.LIGHTBLUE, 'Bleu ciel'),
        (Color.WHITE, 'Clair'),
        (Color.BLACK, 'Sombre'),
    )
    name = models.CharField(max_length=255)
    color = models.CharField(choices=COLOR_CHOICES, max_length=20)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Task(models.Model):
    class State:
        TODO = 'todo'
        DOING = 'doin'
        DONE = 'done'

    STATUS_CHOICES = (
        (State.TODO, 'To Do'),
        (State.DOING, 'Doing'),
        (State.DONE, 'Done')
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    userAssigned = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    creationDate = models.DateField(auto_now_add=True)
    statusChangeDate = models.DateField(auto_now_add=True)
    deadline = models.DateField(blank=True, null=True)
    status = models.CharField(choices=STATUS_CHOICES,
                              default=State.TODO, max_length=4)
    prerequisites = models.ManyToManyField("Task", blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.project.title + ">>" + self.title
