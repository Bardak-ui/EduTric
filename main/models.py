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
        ('12','12'),
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
    GROUPS_CHOICES= [
        ('21.02.16 Шахтное строительство',
         '21.02.16 Шахтное строительство'),

        ('21.02.17 Подземная разработка месторождений полезных ископаемых',
         '21.02.17 Подземная разработка месторождений полезных ископаемых'),

        ('13.02.03 Электрические станции, сети и системы',
         '13.02.03 Электрические станции, сети и системы'),

        ('13.02.02 Теплоснабжение и теплотехническое оборудование',
         '13.02.02 Теплоснабжение и теплотехническое оборудование'),

        ('13.02.06 Релейная защита и автоматизация электроэнергетических систем',
         '13.02.06 Релейная защита и автоматизация электроэнергетических систем'),

        ('13.02.11 Техническая эксплуатация и обслуживание электрического и электромеханического оборудования (по отраслям)',
         '13.02.11 Техническая эксплуатация и обслуживание электрического и электромеханического оборудования (по отраслям)'),

        ('15.02.12 Монтаж, техническое обслуживание и ремонт промышленного оборудования (по отраслям)',
         '15.02.12 Монтаж, техническое обслуживание и ремонт промышленного оборудования (по отраслям)'),

        ('18.02.09 Переработка нефти и газа','18.02.09 Переработка нефти и газа'),

        ('23.02.01 Организация перевозок и управление на транспорте (автомобильном)',
         '23.02.01 Организация перевозок и управление на транспорте (автомобильном)'),

        ('23.02.07 Техническое обслуживание и ремонт двигателей, систем и агрегатов автомобилей',
         '23.02.07 Техническое обслуживание и ремонт двигателей, систем и агрегатов автомобилей'),

        ('23.02.05 Эксплуатация транспортного электрооборудования и автоматики (автомобильный транспорт)',
         '23.02.05 Эксплуатация транспортного электрооборудования и автоматики (автомобильный транспорт)'),
         
        ('20.02.02 Защита в чрезвычайных ситуациях',
         '20.02.02 Защита в чрезвычайных ситуациях'),

        ('09.02.01 Компьютерные системы и комплексы',
         '09.02.01 Компьютерные системы и комплексы'),

        ('20.02.01 Рациональное использование природохозяйственных комплексов',
         '20.02.01 Рациональное использование природохозяйственных комплексов'),

        ('38.02.01 Экономика и бухгалтерский учет (по отраслям)',
         '38.02.01 Экономика и бухгалтерский учет (по отраслям)'),

        ('38.02.03 Операционная деятельность в логистике',
         '38.02.03 Операционная деятельность в логистике'),

        ('09.02.07 Информационные системы и программирование',
         '09.02.07 Информационные системы и программирование'),

        ('10.02.05 Обеспечение информационной безопасности автоматизированных систем',
         '10.02.05 Обеспечение информационной безопасности автоматизированных систем'),

        ('46.02.01 Документационное обеспечение управления и архивоведение.',
         '46.02.01 Документационное обеспечение управления и архивоведение.'),

        ('09.02.06 Сетевое и системное администрирование',
         '09.02.06 Сетевое и системное администрирование'),

        ('40.02.01 Право и организация социального обеспечения',
         '40.02.01 Право и организация социального обеспечения'),

        ('15.01.05 Сварщик (ручной и частично механизированной сварки (наплавки))',
         '15.01.05 Сварщик (ручной и частично механизированной сварки (наплавки))'),

        ('43.01.09 Повар, кондитер',
         '43.01.09 Повар, кондитер'),
    ]

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
    fio = models.CharField(max_length=255)
    avatar = models.ImageField(upload_to='./teacher_avatars/', blank=True, null=True, default="./static/media/no_avatar.jpeg")
    faculti = models.CharField(max_length=255, choices=Faculti.FACULTI_CHOICES)
    subjects = models.TextField()
    group = models.CharField(max_length=113,choices=Groups.GROUPS_CHOICES)

class Kurator(models.Model):
    KURATOR_CHOICES = [
        ('Власова Маргарита Юрьевна','Власова Маргарита Юрьевна'),
        ('Котелевская Мария Александровна','Котелевская Мария Александровна'),
        ('Исаева Марина Владимировна','Исаева Марина Владимировна'),
        ('Куликова Елена Сергеевна','Куликова Елена Сергеевна'),
    ]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile_user', unique=True)
    familiy = models.CharField(max_length=255,  verbose_name='Фамилия')
    name = models.CharField(max_length=255, verbose_name='Имя')
    otchestvo = models.CharField(max_length=255, verbose_name='Отчество')
    faculti = models.CharField(max_length=255, choices=Faculti.FACULTI_CHOICES, verbose_name='Факультет')
    avatar = models.ImageField(upload_to='./profile_avatars/', blank=True, null=True)
    role = models.CharField(max_length=50, blank=True,null=True, choices=Role.ROLE_CHOICES, default='Student')
    phone = models.CharField(max_length=11, verbose_name='Номер телефона')
    kurator = models.ForeignKey(Teacher, null=True, blank=True,on_delete=models.CASCADE, related_name='profile_kurator_group', verbose_name='Куратор')
    group = models.CharField(max_length=255, choices=Groups.GROUPS_CHOICES, verbose_name='Группа')
    #course = models.CharField(max_length=2,verbose_name='Курс')
    course = models.CharField(max_length=2, choices=Course.COURSE, verbose_name='Курс')
    birthday = models.CharField(max_length=10,verbose_name='Дата рождения')

    def __str__(self):
        return f'{self.familiy} {self.name} {self.otchestvo}'

class FAQ(models.Model):
    question = models.CharField(max_length=255, verbose_name="Вопрос")
    answer = models.TextField(verbose_name="Ответ")
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return self.question

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
    lesson_number = models.CharField(max_length=1 ,verbose_name="Номер пары", unique=True)
    start_time = models.TimeField(blank=True,null=True,verbose_name="Начало пары")
    end_time = models.TimeField(blank=True,null=True,verbose_name="Конец пары")
    start_time_1 = models.TimeField(blank=True,null=True,verbose_name="Начало первой части")
    end_time_1 = models.TimeField(blank=True,null=True,verbose_name="Конец первой части")
    start_time_2 = models.TimeField(blank=True,null=True,verbose_name="Начало второй части")
    end_time_2 = models.TimeField(blank=True,null=True,verbose_name="Конец второй части")

    def __str__(self):
        return f"Пара {self.lesson_number}: {self.start_time_1} - {self.end_time_1}, {self.start_time_2} - {self.end_time_2}"

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

    group = models.CharField(max_length=255, choices=Groups.GROUPS_CHOICES, verbose_name='Группа')
    subjects = models.ManyToManyField(Subject, verbose_name="Предметы", blank=True)
    teacher = models.CharField(max_length=100, verbose_name="Преподаватель")
    weekday = models.IntegerField(choices=WEEKDAYS, verbose_name="День недели")
    lesson_time = models.ForeignKey(LessonTime, on_delete=models.CASCADE, verbose_name="Время пары")
    room = models.CharField(max_length=3, verbose_name="Аудитория")

    def __str__(self):
        return f"Пара: {self.weekday} - {self.group} - ({self.subjects})"

    class Meta:
        verbose_name = "Занятие"
        verbose_name_plural = "Расписание"
        ordering = ["weekday"]
        unique_together = ('group', 'weekday', 'lesson_time')  # Уникальность пары для группы, д
        

