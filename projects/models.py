from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Project(models.Model):
    """The Model for a project.

    Attributes:
        title : Title of the project.
        owner : A foreign key towards an owner.
        creationDate : The date of creation of the project.
        users : Members of the project.
        active : Toggle project activity.
        description : A Short description of the project.
    """
    title = models.CharField(max_length=255)
    admins = models.ManyToManyField(User, related_name='administrated_projects')
    creationDate = models.DateField(auto_now_add=True)
    users = models.ManyToManyField(User, related_name='membered_projects')
    active = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

    def is_member(self, user):
        """Check if an user members the project."""
        return user in self.users.all()

    def is_owner(self, user):
        """Check if an user owns the project."""
        return user == self.owner

    def get_project(self):
        """Used for ACL, returns self."""
        return self


class Tag(models.Model):
    """Tag for a Task

    Attributes:
        name : The name of the tag
        color : The color of the tag
        project : A foreign key towards the project
    """
    class Color:
        """Color of a Tag"""
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

    def get_project(self):
        """Used for ACL"""
        return self.project


class Task(models.Model):
    """A Task, linked to a project.

    Attributes:
        project : A foreign key towards the project
        title : The title of the task
        description : A short description of the task
        userAssigned : A foreign key towards an assigned user
        tags : Tags associated to the task
        creationDate : Date of creation of the task
        deadline : Deadline of the task
        status : Status of the task (todo, doing or done)
        prerequisites : prerequisites task
        dependants : Dependants tasks
        active : Toggle task activity
    """
    class State:
        """State of a Task"""
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
    prerequisites = models.ManyToManyField(
        "Task",
        blank=True,
        related_name='prerequisited_by'
    )
    dependants = models.ManyToManyField(
        "Task",
        blank=True,
        related_name='dependanted_by'
    )
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.project.title + ">>" + self.title

    def get_project(self):
        """Used for ACL"""
        return self.project


class Bot(models.Model):
    chatId = models.IntegerField(default=0, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)
    verifyToken = models.TextField(max_length=255, blank=True)

    def get_project(self):
        return self.project
