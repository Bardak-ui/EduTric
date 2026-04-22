from django import forms
from django.contrib.auth import get_user_model
from apps.Accounts.models import Student, Teacher
from apps.Shedule.models import Faculti  # Импортируем модель факультетов

User = get_user_model()

class EditProfile(forms.ModelForm):
    # Вручную меняем текстовое поле на выбор из списка
    faculti = forms.ModelChoiceField(
        queryset=Faculti.objects.all(),
        label="Факультет",
        required=False,
        to_field_name="name",  # Важно: сохраняем имя факультета как текст в базу студента
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Student
        fields = [
            "familiy", "name", "otchestvo", "faculti",
            "avatar", "phone", "group", "birthday",
        ]
        widgets = {
            "birthday": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "group" in self.fields:
            self.fields["group"].disabled = True
            self.fields["group"].required = False

class EditProfileTeacher(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ["faculti", "is_dean", "curated_group"]
        # Добавим виджет для faculti, чтобы был красивый селект
        widgets = {
            "faculti": forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.Shedule.models import Groups # Для подгрузки групп
        
        # Настраиваем queryset для групп
        if "curated_group" in self.fields:
            self.fields["curated_group"].queryset = Groups.objects.all()

        role = None
        if self.instance and hasattr(self.instance, 'user'):
            role = self.instance.user.role

        if role != User.Roles.DEAN:
            for field in ["is_dean", "curated_group"]:
                if field in self.fields:
                    self.fields[field].widget = forms.HiddenInput()
                    self.fields[field].required = False

        if role in [User.Roles.DIRECTOR, User.Roles.ACADEMIC_OFFICE]:
            if "faculti" in self.fields:
                self.fields["faculti"].widget = forms.HiddenInput()
                self.fields["faculti"].required = False