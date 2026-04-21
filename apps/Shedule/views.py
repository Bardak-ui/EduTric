from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.Accounts.models import Teacher
from .forms import ScheduleForm
from .models import Groups, Schedule, Subject

User = get_user_model()


def is_academic_office(user):
    if not user.is_authenticated:
        return False
    return user.role == User.Roles.ACADEMIC_OFFICE


@login_required
def schedule(request, group_id=None):
    groups = Groups.objects.all()

    if not group_id and groups.exists():
        selected_group = groups.first()
    elif group_id:
        selected_group = get_object_or_404(Groups, id=group_id)
    else:
        selected_group = None

    schedule_by_day = {}

    if selected_group:
        # Предзагружаем данные, чтобы не было 100500 запросов к БД
        schedule_qs = Schedule.objects.filter(group=selected_group).select_related("lesson_time", "subject")

        # Проходим по списку WEEKDAYS из модели
        for day_num, day_name in Schedule.WEEKDAYS:
            # Важно: фильтруем по числу (day_num), так как в модели weekday = IntegerField
            lessons = schedule_qs.filter(weekday=day_num).order_by("lesson_time__lesson_number")

            # Сохраняем в словарь под читаемым именем (Понедельник, Вторник...)
            schedule_by_day[day_name] = lessons

    return render(
        request,
        "schedule.html",
        {
            "groups": groups,
            "selected_group": selected_group,
            "schedule_by_day": schedule_by_day,
        },
    )


@login_required
@user_passes_test(is_academic_office)
def add_schedule(request, group_id):
    group = get_object_or_404(Groups, id=group_id)
    weekday = request.GET.get("weekday")

    if request.method == "POST":
        form = ScheduleForm(request.POST, group=group)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.group = group
            instance.save()
            return redirect("schedule_group", group_id=group.id)
    else:
        initial = {"group": group}
        if weekday and weekday.isdigit():
            initial["weekday"] = int(weekday)
        form = ScheduleForm(initial=initial, group=group)

    return render(request, "schedule_form.html", {"form": form, "action": "edit", "group": group})


@login_required
@user_passes_test(is_academic_office)
def edit_schedule(request, schedule_id):
    # 1. Достаем объект пары
    schedule_obj = get_object_or_404(Schedule, id=schedule_id)

    # 2. Берем объект группы из пары
    group = schedule_obj.group

    if request.method == "POST":
        form = ScheduleForm(request.POST, instance=schedule_obj, group=group)
        if form.is_valid():
            form.save()
            # 3. Редирект по правильному имени пути
            return redirect("schedule_group", group_id=group.id)
    else:
        form = ScheduleForm(instance=schedule_obj, group=group)

    # 4. Передаем 'group' в контекст, чтобы кнопка "Отмена" сработала
    return render(request, "schedule_form.html", {"form": form, "action": "edit", "group": group})


@login_required
@user_passes_test(is_academic_office)
def delete_schedule(request, schedule_id):
    schedule_obj = get_object_or_404(Schedule, id=schedule_id)
    group = schedule_obj.group
    if request.method == "POST":
        schedule_obj.delete()
        return redirect("schedule_group", group_id=group.id)
    return render(request, "confirm_delete.html", {"schedule": schedule_obj, "group": group})


def edit_evalutions(request):
    return render(request, "edit_evalutions.html")


def get_schedule_or_404(schedule_id):
    return get_object_or_404(Schedule, id=schedule_id)


@login_required
def api_get_teachers_by_subject(request, subject_id):
    from django.http import JsonResponse
    from .models import Subject
    from apps.Accounts.models import Teacher

    try:
        subject = Subject.objects.get(pk=subject_id)
        # Получаем данные преподавателей, привязанных к предмету
        # Обрати внимание: теперь мы берем поля прямо из Teacher
        teachers_data = Teacher.objects.filter(subjects=subject).values(
            'id', 'last_name', 'first_name', 'patronymic'
        )

        results = []
        for t in teachers_data:
            fio = f"{t['last_name']} {t['first_name']} {t['patronymic']}".strip()
            results.append({
                'id': t['id'],
                'full_name': fio if fio else "Имя не указано"
            })

        return JsonResponse({'teachers': results})
    except Subject.DoesNotExist:
        return JsonResponse({'teachers': [], 'error': 'Subject not found'}, status=404)

