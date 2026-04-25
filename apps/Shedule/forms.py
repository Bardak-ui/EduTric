from django import forms
from django.db.models import Case, When, Value, IntegerField
from apps.Accounts.models import Teacher
from .models import LessonTime, Schedule, Subject

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ["group", "subject", "teacher", "weekday", "lesson_time", "room", "is_even_week", "merged_groups"]
        widgets = {
            "group": forms.Select(attrs={"class": "form-control", "id": "id_group"}),
            "subject": forms.Select(attrs={"class": "form-control", "id": "id_subject"}),
            "teacher": forms.Select(attrs={"class": "form-control", "id": "id_teacher"}),
            "weekday": forms.Select(attrs={"class": "form-control"}),
            "lesson_time": forms.Select(attrs={"class": "form-control"}),
            "room": forms.TextInput(attrs={"class": "form-control"}),
            "is_even_week": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "merged_groups": forms.SelectMultiple(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, group=None, **kwargs):
        super().__init__(*args, **kwargs) 
    
        target_group = group or (self.instance.group if self.instance and self.instance.pk else None)

        # 1. Фильтрация времени
        self.fields["lesson_time"].queryset = LessonTime.objects.exclude(
            start_time__isnull=True,
        ).order_by("lesson_number")

        # 2. Базовые QuerySet-ы
        subjects_qs = Subject.objects.all().select_related('teacher__user')
        teachers_qs = Teacher.objects.all().select_related('user')

        if target_group:
            # Предметы только этой группы
            subjects_qs = target_group.subjects.all().select_related('teacher__user')
            
            # Умная сортировка преподавателей по факультету
            group_faculty = target_group.faculty
            if group_faculty:
                teachers_qs = teachers_qs.annotate(
                    is_same_fac=Case(
                        When(faculty=group_faculty, then=Value(1)),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                ).order_by("-is_same_fac", "user__last-name")
            
            # Ограничиваем список учителей теми, кто ведет предметы у этой группы
            teachers_qs = teachers_qs.filter(subjects__in=subjects_qs).distinct()

        # Применяем QuerySet-ы
        self.fields["subject"].queryset = subjects_qs
        self.fields["teacher"].queryset = teachers_qs

        # Если мы редактируем и предмет уже есть, фиксируем учителя
        if self.instance and self.instance.pk and self.instance.subject:
            self.fields["teacher"].initial = self.instance.subject.teacher_id