import re
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import Student, Teacher
from apps.Shedule.models import Groups, Faculti

User = get_user_model()

def validate_username(value):
    if not re.match(r"^[a-zA-Z0-9_@+\-\.]+$", value):
        raise ValidationError(
            "Имя пользователя может содержать только латинские буквы, цифры и символы @/./+/-/_."
        )

class CustomeUserForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        validators=[validate_username],
        help_text="Только латинские буквы, цифры и символы @/./+/-/_.",
    )

    class Meta:
        model = User
        fields = ["username"] # Пароли UserCreationForm добавит сама

class ExtendedRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.Roles.choices, initial=User.Roles.STUDENT, label="Роль")
    secure_code = forms.CharField(required=False, label="Секретный код")
    
    # Поля Студента
    familiy = forms.CharField(max_length=100, required=False, label="Фамилия")
    name = forms.CharField(max_length=100, required=False, label="Имя")
    otchestvo = forms.CharField(max_length=100, required=False, label="Отчество")
    faculti = forms.CharField(max_length=100, required=False, label="Факультет") # Текстовое для студента
    phone = forms.CharField(max_length=20, required=False, label="Телефон")
    group = forms.ModelChoiceField(queryset=Groups.objects.all(), required=False, label="Группа")
    birthday = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label="Дата рождения")
    
    # Поля Преподавателя / Декана (используем те же имена, что в HTML)
    department = forms.ModelChoiceField(queryset=Faculti.objects.all(), required=False, label="Факультет / Кафедра")
    is_dean = forms.BooleanField(required=False, label="Декан")
    curated_group = forms.ModelChoiceField(queryset=Groups.objects.all(), required=False, label="Куратируемая группа")
    subjects = forms.ModelMultipleChoiceField(
        queryset=None, 
        required=False,
        widget=forms.SelectMultiple(attrs={'size': 5}),
        label="Предметы"
    )

    class Meta:
        model = User
        fields = ["username", "role"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.Shedule.models import Subject
        self.fields['subjects'].queryset = Subject.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        code = cleaned_data.get('secure_code')

        staff_roles = [User.Roles.TEACHER, User.Roles.DEAN, User.Roles.DIRECTOR, User.Roles.ACADEMIC_OFFICE]
        
        # Валидация кода
        if role in staff_roles and code != "Gt$0X1hS%_":
            self.add_error('secure_code', "Неверный секретный код для регистрации персонала")

        # Проверка обязательных полей для преподавателя
        if role == User.Roles.TEACHER and not cleaned_data.get('faculti'):
            self.add_error('faculti', "Выберите факультет")

        return cleaned_data

class CreateStudent(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "familiy", "name", "otchestvo", "faculti", 
            "avatar", "phone", "group", "birthday", 
            "student_id", "is_curator",
        ]
        widgets = {
            "birthday": forms.DateInput(attrs={"type": "date"}),
        }

class CreateProfileTeacher(forms.ModelForm):
    class Meta:
        model = Teacher
        # ЗАМЕНЯЕМ "department" на "faculti"
        fields = ["faculti", "is_dean", "curated_group", "subjects"]
        widgets = {
            "faculti": forms.Select(attrs={'class': 'form-control'}),
            "curated_group": forms.Select(attrs={'class': 'form-control'}),
            "subjects": forms.SelectMultiple(attrs={'size': 5, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.Shedule.models import Subject, Groups
        # Настраиваем кверисеты
        self.fields['subjects'].queryset = Subject.objects.all()
        self.fields['curated_group'].queryset = Groups.objects.all()
        
        # Опционально: можно добавить подпись, чтобы в выпадающем списке 
        # было понятно, что это выбор факультета
        self.fields['faculti'].empty_label = "Выберите факультет/отделение"