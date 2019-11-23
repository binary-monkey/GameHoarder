# Create your models here.
from django.contrib.auth.models import User
from django.db import models
from django.core.files.storage import FileSystemStorage

''' Avoids saving again existing files
'''
class MediaFileSystemStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if max_length and len(name) > max_length:
            raise (Exception("The file is bigger than supported"))
        return name

    def _save(self, name, content):
        if self.exists(name):
            return name
        return super(MediaFileSystemStorage, self)._save(name, content)


class Profile(models.Model):
    user = models.OneToOneField(User, auto_created=True, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='polls/static/images', blank=True, default="polls/static/images/user.png",
                               storage=MediaFileSystemStorage())

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        return self.user
