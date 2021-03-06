# Generated by Django 2.2.7 on 2019-12-22 21:42

import django.db.models.deletion
from django.conf import settings
from django.contrib.auth.models import Permission, Group
from django.db import migrations, models

import gamehoarder_site.models


def add_group_permissions(apps, schema_editor):
    # standard
    Group.objects.get_or_create(name='standard_user')

    # admin
    group, created = Group.objects.get_or_create(name='admin')
    print("HOLA")
    for permission in Permission.objects.all():
        print(permission.name)
    if created:
        group.permissions.add(Permission.objects.get(name="Can change user"))
        group.permissions.add(Permission.objects.get(name="Can delete user"))
        group.permissions.add(Permission.objects.get(name="Can view user"))


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, default='avatars/user.png',
                                             storage=gamehoarder_site.models.MediaFileSystemStorage(),
                                             upload_to='avatars', verbose_name='avatar')),
                ('friends',
                 models.ManyToManyField(related_name='friends', to=settings.AUTH_USER_MODEL, verbose_name='friends')),
                ('user', models.ForeignKey(auto_created=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                           related_name='user', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'Profile',
                'verbose_name_plural': 'Profiles',
            },
        ),
        # migrations.RunPython(add_group_permissions)
    ]
