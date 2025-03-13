from django import forms
from .models import Teacher,Profile, Schedule, LessonTime
from django.forms import TextInput, DateInput, Textarea, PasswordInput, IntegerField,CharField,ChoiceField
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class CustomeUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        # widgets = {
        #     'username': TextInput(attrs={
        #         'placeholder': 'Придумайте логин',
        #     }),
        #     'password1': PasswordInput(attrs={
        #         'placeholder': 'Придумайте пароль',

        #         'autocomplete': 'new-password',  # Отключаем автозаполнение
        #     }),
        #     'password2': PasswordInput(attrs={
        #         'placeholder': 'Подтвердите пароль',
        #         'autocomplete': 'new-password',  # Отключаем автозаполнение
        #     })
        # }
class CreateProfile(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['familiy','name','otchestvo','faculti','avatar','phone','group','course','birthday']
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),  # Добавляем календарь
        }

class CreateProfileTeacher(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['fio','avatar','faculti','subjects','group']

class EditProfile(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['faculti','avatar','phone','kurator','group','course','birthday']

class EditProfileTeacher(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['fio','avatar','faculti','subjects','group']

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['group', 'subjects', 'teacher', 'weekday', 'lesson_time', 'room']
        widgets = {
            "subjects": forms.CheckboxSelectMultiple(),
            "lesson_time": forms.CheckboxSelectMultiple(),
        }

    def init(self, *args, **kwargs):
        super().init(*args, **kwargs)
        self.fields["lesson_time"].queryset = LessonTime.objects.all()