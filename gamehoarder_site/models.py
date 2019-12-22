# Create your models here.
from django.contrib.auth.models import User
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.utils.translation import ugettext_lazy as _

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
    friends = models.ManyToManyField(User, verbose_name=_("friends"), related_name='friends')
    user = models.ForeignKey(User, auto_created=True, verbose_name=_("user"), related_name='user', null=True,
                             on_delete=models.CASCADE)

    avatar = models.ImageField(upload_to='avatars', blank=True, default="avatars/user.png",
                               verbose_name=_("avatar"), storage=MediaFileSystemStorage())

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

    def get_friends(self):
        return self.friends

    def get_avatar(self):
        return self.avatar

    @classmethod
    def make_friend(cls, current_profile, new_friend):
        friends = current_profile.friends
        friends.add(new_friend.user)
        friends = new_friend.friends
        friends.add(current_profile.user)

    @classmethod
    def remove_friend(cls, current_profile, new_friend):
        friends = current_profile.friends
        friends.remove(new_friend.user)
        friends = new_friend.friends
        friends.remove(current_profile.user)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
