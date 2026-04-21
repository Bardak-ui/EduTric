from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.Shedule.models import Groups, Faculti


class Role(models.Model):
    ROLE_CHOICES = [
        ("Администратор", "Администратор"),
        ("Преподаватель", "Преподаватель"),
        ("Студент", "Студент"),
    ]

    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"


class User(AbstractUser):
    class Roles(models.TextChoices):
        STUDENT = "STUDENT", "Студент"
        STAROSTA = "STAROSTA", "Староста"
        TEACHER = "TEACHER", "Преподаватель"
        DEAN = "DEAN", "Декан"
        DIRECTOR = "DIRECTOR", "Директор"
        ACADEMIC_OFFICE = "ACADEMIC_OFFICE", "Ученый отдел"

    role = models.CharField(
        max_length=32,
        choices=Roles.choices,
        default=Roles.STUDENT,
        verbose_name="Роль пользователя",
    )

    class Meta:
        db_table = "users"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.get_full_name() or self.username


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
    familiy = models.CharField(max_length=100, blank=True, verbose_name="Фамилия")
    name = models.CharField(max_length=100, blank=True, verbose_name="Имя")
    otchestvo = models.CharField(max_length=100, blank=True, verbose_name="Отчество")
    faculti = models.CharField(max_length=100, blank=True, verbose_name="Факультет")
    avatar = models.ImageField(upload_to="student_avatars/", blank=True, null=True, verbose_name="Аватар")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    birthday = models.DateField(blank=True, null=True, verbose_name="Дата рождения")

    class Meta:
        db_table = "students"
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"

    def __str__(self):
        return f"{self.familiy} {self.name} {self.otchestvo}"


class Teacher(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="teacher_profile",
        verbose_name="Пользователь",
    )
    # Добавляем эти поля:
    last_name = models.CharField(max_length=100, blank=True, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, blank=True, verbose_name="Имя")
    patronymic = models.CharField(max_length=100, blank=True, verbose_name="Отчество")
    
    faculti = models.ForeignKey(
        Faculti,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teachers",
        verbose_name="Факультет / Кафедра",
    )
    # Оставляем текстовое поле как "Кафедра" внутри факультета (опционально)
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
        # Теперь выводим ФИО прямо из модели преподавателя
        fio = f"{self.last_name} {self.first_name} {self.patronymic}".strip()
        display_name = fio if fio else self.user.username
        facult_name = self.faculti.name if self.faculti else 'Без факультета'
        return f"{display_name} — {facult_name}"
