# Generated by Django 2.2.7 on 2019-12-03 11:45

from django.db import migrations, models
import gamehoarder_site.models


class Migration(migrations.Migration):

    dependencies = [
        ('gamehoarder_site', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, default='avatars/user.png', storage=gamehoarder_site.models.MediaFileSystemStorage(), upload_to='avatars'),
        ),
    ]
