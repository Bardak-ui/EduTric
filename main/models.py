from django.db import models
from django.contrib.auth.models import User 
from datetime import datetime, timedelta

class Role(models.Model):
    ROLE_CHOICES = [
        ('Администратор','Administrator'),
        ('Учитель','Teacher'),
        ('Ученик','Student')
    ]

class Course(models.Model):
    COURSE = [
        ('11','11'),
        ('11','12'),
        ('21','21'),
        ('22','22'),
        ('31','31'),
        ('32','32'),
        ('41','41'),
        ('42','42'),
        ('51','51'),
        ('52','52'),
    ]

class Groups(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название группы", default='')
    course = models.CharField(max_length=2,choices=Course.COURSE, verbose_name="Курс", default='11')

    def __str__(self):
        return f"{self.name}-{self.course}"

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

class Faculti(models.Model):
    FACULTI_CHOICES = [
        ('Факультет топлива и экологии',
         'Факультет топлива и экологии'),

        ('Механический факультет',
         'Механический факультет'),

        ('Факультет информационных технологий и экономики',
         'Факультет информационных технологий и экономики'),
         
        ('Энергетический факультет',
         'Энергетический факультет'),

        ('Заочный факультет','Заочный факультет'),

        ('Факультет сервиса','Факультет сервиса'),

        ('Факультет техносферной безопасности и права',
         'Факультет техносферной безопасности и права'),
    ]
    
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_user', unique=True)
    fio = models.CharField(max_length=255, verbose_name='ФИО')
    avatar = models.ImageField(upload_to='./teacher_avatars/', blank=True, null=True, default="./static/media/no_avatar.jpeg")
    faculti = models.CharField(max_length=255, choices=Faculti.FACULTI_CHOICES, verbose_name='Факультет')
    subjects = models.TextField(verbose_name='Ведущие предметы')
    group = models.ForeignKey(Groups, on_delete=models.CASCADE,verbose_name='Группа')
    role = models.CharField(max_length=50, choices=Role.ROLE_CHOICES, default='Teacher')

    def __str__(self):
        return self.fio

class Kurator(models.Model):
    KURATOR_CHOICES = [
        ('Власова Маргарита Юрьевна','Власова Маргарита Юрьевна'),
        ('Котелевская Мария Александровна','Котелевская Мария Александровна'),
        ('Исаева Марина Владимировна','Исаева Марина Владимировна'),
        ('Куликова Елена Сергеевна','Куликова Елена Сергеевна'),
    ]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile_user', unique=True)
    familiy = models.CharField(max_length=255,verbose_name='Фамилия')
    name = models.CharField(max_length=255, verbose_name='Имя')
    otchestvo = models.CharField(max_length=255, verbose_name='Отчество')
    faculti = models.CharField(max_length=255, choices=Faculti.FACULTI_CHOICES, verbose_name='Факультет')
    avatar = models.ImageField(upload_to='./profile_avatars/', blank=True, null=True)
    role = models.CharField(max_length=50, blank=True,null=True, choices=Role.ROLE_CHOICES, default='Student')
    phone = models.CharField(max_length=12, verbose_name='Номер телефона')
    kurator = models.ForeignKey(Teacher, null=True, blank=True,on_delete=models.CASCADE, related_name='profile_kurator_group', verbose_name='Куратор')
    group = models.ForeignKey(Groups,on_delete=models.CASCADE,verbose_name='Группа')
    course = models.CharField(max_length=2, choices=Course.COURSE, verbose_name='Курс')
    birthday = models.CharField(max_length=10,verbose_name='Дата рождения')

    def __str__(self):
        return f'{self.familiy} {self.name} {self.otchestvo} {self.group}'

class FAQ(models.Model):
    question = models.CharField(max_length=255, verbose_name="Вопрос")
    answer = models.TextField(verbose_name="Ответ")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Вопрос: {self.question}"

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name="Предмет")
    teacher = models.CharField(max_length=100, verbose_name="Преподаватель")

    def __str__(self):
        return f'Предмет: {self.name} | Преподаватель: {self.teacher}'

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"

class Performance(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    grade = models.IntegerField(verbose_name="Оценка")
    date = models.DateField(auto_now_add=True)


class LessonTime(models.Model):
    lesson_number = models.CharField(max_length=1, verbose_name="Номер пары")
    start_time = models.TimeField(blank=True, null=True, verbose_name="Начало пары")
    end_time = models.TimeField(blank=True, null=True, verbose_name="Конец пары")
    start_time_1 = models.TimeField(blank=True, null=True, verbose_name="Начало первой части")
    end_time_1 = models.TimeField(blank=True, null=True, verbose_name="Конец первой части")
    start_time_2 = models.TimeField(blank=True, null=True, verbose_name="Начало второй части")
    end_time_2 = models.TimeField(blank=True, null=True, verbose_name="Конец второй части")

    def __str__(self):
        return f"Пара {self.lesson_number}: {self.get_formatted_time()}"

    def get_formatted_time(self):
        if self.start_time_1 and self.end_time_1 and self.start_time_2 and self.end_time_2:
            # Если есть время для пар с перерывом
            return (
                f"{self.start_time_1.strftime('%H:%M')} - {self.end_time_1.strftime('%H:%M')}, "
                f"{self.start_time_2.strftime('%H:%M')} - {self.end_time_2.strftime('%H:%M')}"
            )
        elif self.start_time and self.end_time:
            # Если есть время для пар без перерыва
            return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
        else:
            # Если время не указано
            return "Время не указано"

    class Meta:
        ordering = ["lesson_number"]
        verbose_name = "Время пары"
        verbose_name_plural = "Времена пар"

class Schedule(models.Model):
    WEEKDAYS = [
        (1, "Понедельник"),
        (2, "Вторник"),
        (3, "Среда"),
        (4, "Четверг"),
        (5, "Пятница"),
        (6, "Суббота"),
    ]

    group = models.ForeignKey(Groups, on_delete=models.CASCADE,verbose_name='Группа')
    subjects = models.CharField(max_length=255,verbose_name="Предметы", default="Не указано")
    teacher = models.CharField(max_length=100, verbose_name="Преподаватель")
    weekday = models.IntegerField(choices=WEEKDAYS, verbose_name="День недели")
    lesson_time = models.ForeignKey(LessonTime, on_delete=models.CASCADE, verbose_name="Время пары")
    room = models.CharField(max_length=255, verbose_name="Аудитория")

    def __str__(self):
        return f"Пара: {self.weekday} - {self.group} - ({self.subjects})"

    class Meta:
        verbose_name = "Занятие"
        verbose_name_plural = "Расписание"
        ordering = ["weekday"]
        unique_together = ('group', 'weekday', 'lesson_time')  # Уникальность пары для группы, д
        

class News(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    news = models.TextField(verbose_name="Новость")

    def __str__(self):
        return self.title
    
    