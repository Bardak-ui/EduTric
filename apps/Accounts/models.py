from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.Shedule.models import Groups, Faculti


class Role(models.Model):
    ROLE_CHOICES = [
        ("ADMIN", "Администратор"),
        ("TEACHER", "Преподаватель"),
        ("DEAN", "Декан"),
        ("DIRECTOR", "Директор"),
        ("ACADEMIC", "Ученый отдел"),
        ("STAROSTA", "Староста"),
        ("STUDENT", "Студент"),
    ]

    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"


class CustomRole(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название роли")

    class Meta:
        verbose_name = 'Пользовательская роль'
        verbose_name_plural = 'Пользовательская роли'


    def __str__(self):
        return self.name
    
class User(AbstractUser):
    system_role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Системная роль"
    )

    custome_role = models.ForeignKey(
        CustomRole,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name = "Пользовательская роль"
    )

    class Meta:
        db_table = "users"
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


    @property
    def role_name(self):
        if self.system_role:
            return self.system_role.get_name_display()
        elif self.custome_role:
            return self.custome_role.name
        return "Без роли"
    
    @property
    def is_admin(self):
        return self.system_role and self.system_role.name == "ADMIN"
    
    @property
    def is_teacher(self):
        return self.system_role and self.system_role.name == "TEACHER"
    
    @property
    def is_student(self):
        return self.system_role and self.system_role.name == "STUDENT"
    
    @property
    def is_dean(self):
        return self.system_role and self.system_role.name == "DEAN"
    
    @property
    def is_director(self):
        return self.system_role and self.system_role.name == "DIRECTOR"

    @property
    def is_academic_office(self):
        return self.system_role and self.system_role.name == "ACADEMIC"


class Student(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile",
        verbose_name="Пользователь",
    )
    group = models.ForeignKey(
        Groups,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
        verbose_name="Группа",
    )
    student_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Номер зачетки",
    )
    is_curator = models.BooleanField(
        default=False,
        verbose_name="Староста/Куратор",
        help_text="Отмечайте, если студент является старостой или куратором группы.",
    )
    surname = models.CharField(max_length=100, blank=True, verbose_name="Фамилия")
    name = models.CharField(max_length=100, blank=True, verbose_name="Имя")
    patronymic = models.CharField(max_length=100, blank=True, verbose_name="Отчество")
    faculty = models.CharField(max_length=100, blank=True, verbose_name="Факультет")
    avatar = models.ImageField(upload_to="student_avatars/", blank=True, null=True, verbose_name="Аватар")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    birthday = models.DateField(blank=True, null=True, verbose_name="Дата рождения")

    class Meta:
        db_table = "students"
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"

    def __str__(self):
        return f"{self.surname} {self.name} {self.patronymic}"


class Teacher(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="teacher_profile",
        verbose_name="Пользователь",
    )
    surname = models.CharField(max_length=100, blank=True, verbose_name="Фамилия")
    name = models.CharField(max_length=100, blank=True, verbose_name="Имя")
    patronymic = models.CharField(max_length=100, blank=True, verbose_name="Отчество")
    
    faculty = models.ForeignKey(
        Faculti,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teachers",
        verbose_name="Факультет / Кафедра",
    )
    department_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Конкретная кафедра",
    )
    is_dean = models.BooleanField(
        default=False,
        verbose_name="Декан",
        help_text="Позволяет редактировать оценки по факультету/отделению.",
    )
    curated_group = models.ForeignKey(
        Groups,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="curator_teacher",
        verbose_name="Куратируемая группа",
    )
    subjects = models.ManyToManyField(
        "Shedule.Subject",
        blank=True,
        related_name="teachers",
        verbose_name="Предметы",
        help_text="Выберите предметы, которые преподаватель ведёт.",
    )

    class Meta:
        db_table = "teachers"
        verbose_name = "Преподаватель"
        verbose_name_plural = "Преподаватели"

    def __str__(self):
        return f"{self.surname} {self.name} {self.patronymic} {self.faculty}" 
