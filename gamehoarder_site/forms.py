from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import *
from django import forms
from betterforms.multiform import MultiModelForm

class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2',)


class AvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar', )

    def clean_avatar(self):
        avatar = self.cleaned_data['avatar']
        try:
            main, sub = avatar.content_type.split('/')
            if not (main == 'image' and sub in ['jpeg', 'pjpeg', 'gif', 'png']):
                raise forms.ValidationError(u'Please use a JPEG, '
                    'GIF or PNG image.')
        except AttributeError:
            pass
        return avatar


class User_Avatar_Form(MultiModelForm):
    form_classes = {
        'user':UserForm,
        'avatar': AvatarForm,
    }