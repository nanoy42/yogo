# Generated by Django 2.0.1 on 2018-01-31 18:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_auto_20180130_2038'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='projet',
            new_name='project',
        ),
    ]