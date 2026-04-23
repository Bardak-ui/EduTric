from django.db import models


class Faculty(models.Model):
    # Убираем choices, чтобы любой колледж мог вписать свои факультеты
    name = models.CharField(max_length=255, unique=True, verbose_name="Название факультета")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Shedule_faculty'
        verbose_name = "Факультет"
        verbose_name_plural = "Факультеты"


class Kurator(models.Model):
    name = models.CharField(max_length=255, verbose_name="Куратор")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Куратор"
        verbose_name_plural = "Кураторы"


class Course(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название курса (напр. 1 курс или 11)")
    sort_order = models.PositiveIntegerField(default=1, verbose_name="Порядок сортировки")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ['sort_order']

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name="Предмет")
    teacher = models.ForeignKey(
        'Accounts.Teacher', 
        on_delete=models.CASCADE, 
        related_name='subject_list',
        verbose_name="Преподаватель",
        null=True,
        blank=True
    )

    def __str__(self):
        if self.teacher and hasattr(self.teacher, 'user') and self.teacher.user:
            return f"{self.name} — {self.teacher.user.get_full_name()}"
        return f"{self.name} (Преподаватель не назначен)"

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"

class Groups(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название группы")
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="groups", null=True, blank=True)
    
    # ЗАМЕНЯЕМ CharField на ForeignKey к нашей новой модели
    course = models.ForeignKey(
        Course, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name="Курс"
    )
    
    subjects = models.ManyToManyField(
        Subject,
        related_name="groups",
        blank=True,
        verbose_name="Учебный план группы",
    )

    def __str__(self):
        return f"{self.name}-{self.course}"

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class LessonTime(models.Model):
    lesson_number = models.CharField(max_length=2, verbose_name="Номер пары")
    start_time = models.TimeField(null=True, blank=True, verbose_name="Начало пары")
    end_time = models.TimeField(null=True, blank=True, verbose_name="Конец пары")

    def __str__(self):
        if self.start_time and self.end_time:
            return f"Пара {self.lesson_number}: {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
        return f"Пара {self.lesson_number}"

    class Meta:
        db_table = "lesson_time"
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

    group = models.ForeignKey(Groups, on_delete=models.CASCADE, verbose_name="Группа")
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Предмет",
    )
    teacher = models.ForeignKey(
        "Accounts.Teacher",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Преподаватель",
        related_name="schedules",
    )
    weekday = models.IntegerField(choices=WEEKDAYS, verbose_name="День недели")
    lesson_time = models.ForeignKey(
        LessonTime,
        on_delete=models.CASCADE,
        verbose_name="Время пары",
    )
    room = models.CharField(max_length=255, verbose_name="Аудитория")
    is_even_week = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Четная неделя",
        help_text="Если установлено, занятие идет только в четную или нечетную неделю.",
    )
    merged_groups = models.ManyToManyField(
        Groups,
        blank=True,
        related_name="merged_schedules",
        verbose_name="Объединенные группы",
        help_text="Выберите группы, которые также участвуют в этом занятии.",
    )

    def __str__(self):
        day_name = dict(self.WEEKDAYS).get(self.weekday, "?")
        subject_name = self.subject.name if self.subject else "Без предмета"
        teacher_name = self.teacher.user.get_full_name() if self.teacher else "Без преподавателя"
        merged = ", ".join([group.name for group in self.merged_groups.all()])
        merged_part = f"; объединены: {merged}" if merged else ""
        return f"{day_name} | {self.group} | {subject_name} | {teacher_name}{merged_part}"

    class Meta:
        db_table = "schedule"
        verbose_name = "Расписание"
        verbose_name_plural = "Расписания"
        ordering = ["weekday", "lesson_time__lesson_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["group", "weekday", "lesson_time", "is_even_week"],
                name="unique_schedule_slot",
            )
        ]
