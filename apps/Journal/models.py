from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from apps.Shedule.models import Subject

User = get_user_model()

class RecordBook(models.Model):
    TYPE_CHOICES = [
        ("Зачет", "Зачет"),
        ("Экзамен", "Экзамен"),
        ("Курсовая", "Курсовая работа"),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="record_entries")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    grade = models.IntegerField(verbose_name="Итоговая оценка")
    test_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="Экзамен")
    semester = models.IntegerField(default=1)
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="signed_grades",
    )
    date_signed = models.DateField(auto_now_add=True)
    time_signed = models.TimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name = "Запись в зачетке"
        verbose_name_plural = "Зачетная книжка"
        unique_together = ("student", "subject", "semester")

    def __str__(self):
        return f"{self.student.username} - {self.subject.name} ({self.grade})"

    @classmethod # Используем classmethod для операций создания
    def confirm_grades(cls, student, subject, semester, teacher):
        # Получаем все строковые оценки студента по предмету
        performances = Performance.objects.filter(student=student, subject=subject)
        
        grades_list = []
        for p in performances:
            if p.grade.isdigit(): # Берем только цифры
                grades_list.append(int(p.grade))
        
        if grades_list:
            avg_grade = sum(grades_list) / len(grades_list)
            final_grade = round(avg_grade)
            
            from django.utils import timezone # Импортируем для точности
            
            obj, created = cls.objects.update_or_create(
                student=student,
                subject=subject,
                semester=semester,
                defaults={
                    'grade': final_grade, 
                    'teacher': teacher,
                    # Даты обновятся автоматически благодаря auto_now_add, 
                    # но если нужно обновить время при пересдаче:
                }
            )
            return obj
        return None

class Performance(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="performance_student")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    grade = models.CharField(max_length=2, verbose_name="Оценка или Н")
    date = models.DateField(default=timezone.now, verbose_name="Дата урока")

    class Meta:
        ordering = ["-date"]
        verbose_name = "Успеваемость"
        verbose_name_plural = "Успеваемость" # Добавил для красоты в админке

    def __str__(self):
        return f"{self.student.username} - {self.subject} - {self.grade} ({self.date})"