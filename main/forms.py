from django import forms
from .models import Teacher,Profile, Schedule, LessonTime, Groups, Subject
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
            'subjects': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'weekday': forms.Select(attrs={'class': 'form-control'}),
            'lesson_time': forms.Select(attrs={'class': 'form-control'}),  # Исправлено на Select
            'room': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Фильтрация учителей по группе
        if 'group' in self.data:
            try:
                group_name = self.data.get('group')
                self.fields['teacher'].queryset = Teacher.objects.filter(group=group_name)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.group:
            self.fields['teacher'].queryset = Teacher.objects.filter(group=self.instance.group)

        # Фильтрация предметов по учителю
        if 'teacher' in self.data:
            try:
                teacher_name = self.data.get('teacher')
                self.fields['subjects'].queryset = Subject.objects.filter(teacher=teacher_name)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.teacher:
            self.fields['subjects'].queryset = Subject.objects.filter(teacher=self.instance.teacher)

        # Упорядочиваем lesson_time
        self.fields['lesson_time'].queryset = LessonTime.objects.all().order_by('lesson_number')

    def clean(self):
        cleaned_data = super().clean()

        return cleaned_data