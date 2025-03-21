from django import forms
from .models import Teacher,Profile, Schedule, LessonTime, Groups, Subject, News, FAQ
from django.forms import TextInput, DateInput, Textarea, PasswordInput, IntegerField,CharField,ChoiceField
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class CustomeUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        
        def save(self, commit=True):
            user = super().save(commit=False)
            user.set_password(self.cleaned_data['password1'])  # Хэширование пароля
            if commit:
                user.save()
            return user
        
class CreateProfile(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['familiy','name','otchestvo','faculti','avatar','phone','group','course','birthday']
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),  # Добавляем календарь
        }

class EditProfile(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['familiy','name','otchestvo','faculti','avatar','phone','group','course','birthday']
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),  # Поле для выбора даты
        }
class CreateProfileTeacher(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['fio','avatar','faculti','subjects','group']
        widgets = {
            'subjects': Textarea(attrs={
                'style': 'resize: vertical;', # Inline-стили (запрет изменения размера и цвет границы)
            }),
        }

class EditProfileTeacher(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['fio','avatar','faculti','subjects','group']

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['group', 'subjects', 'teacher', 'weekday', 'lesson_time', 'room']
        widgets = {
            'weekday': forms.Select(attrs={'class': 'form-control'}),
            'lesson_time': forms.Select(attrs={'class': 'form-control'}),
            'room': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Фильтрация lesson_time, чтобы исключить объекты с пустым временем
        self.fields['lesson_time'].queryset = LessonTime.objects.exclude(
            start_time__isnull=True,
            start_time_1__isnull=True,
            start_time_2__isnull=True
        ).order_by('lesson_number')

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'image', 'news']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class AddFAQ(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['question', 'answer']

class EditFAQ(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['question', 'answer']