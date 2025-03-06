from django import forms
from .models import Teacher,Profile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class CustomeUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
    
class CreateProfile(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['fio','faculti','avatar','phone','kurator','group','course','birthday']

class CreateProfileTeacher(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['fio','avatar','faculti','subjects','group']

class EditProfile(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['fio','faculti','avatar','phone','kurator','group','course','birthday']

class EditProfileTeacher(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['fio','avatar','faculti','subjects','group']