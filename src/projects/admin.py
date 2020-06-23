from django.contrib import admin

from .models import Project, Tag, Task


class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "active")


admin.site.register(Project, ProjectAdmin)
admin.site.register(Tag)
admin.site.register(Task)
