from collections import defaultdict
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.db import models 
from apps.Accounts.models import Student
from apps.Shedule.models import Groups, Subject
from .forms import GradeForm
from .models import Performance, RecordBook
from django.core.exceptions import PermissionDenied
from django import template

User = get_user_model()
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key) or dictionary.get(str(key))

def is_teacher(user):
    if not user.is_authenticated:
        return False
    # УЧЕБНЫЙ ОТДЕЛ (ACADEMIC_OFFICE) ИСКЛЮЧЕН ИЗ ЖУРНАЛА
    allowed = [
        User.Roles.TEACHER, 
        User.Roles.DEAN, 
        User.Roles.DIRECTOR, 
    ]
    return user.role in allowed

@login_required
def performance_view(request):
    user = request.user
    
    # 1. ЗАПРЕТ ДЛЯ УЧЕБНОГО ОТДЕЛА
    if user.role == User.Roles.ACADEMIC_OFFICE:
        messages.error(request, "У учебного отдела доступ только к расписанию.")
        return redirect('profile')

    is_teacher_flag = is_teacher(user)

    # 2. Проверка прав
    if not hasattr(user, 'student_profile') and not is_teacher_flag:
        return redirect("register")

    if is_teacher_flag:
        teacher = getattr(user, 'teacher_profile', None)
        
        # Директор видит всё
        if user.role == User.Roles.DIRECTOR:
            first_group = Groups.objects.first()
            if first_group:
                return redirect("journal:group_info", group_id=first_group.id)
            return redirect("profile")

        # Декан по факультету
        if user.role == User.Roles.DEAN:
            if teacher and teacher.faculti:
                first_fac_group = Groups.objects.filter(faculti=teacher.faculti).first()
                if first_fac_group:
                    return redirect("journal:group_info", group_id=first_fac_group.id)

        # Преподаватель по расписанию
        if teacher:
            assigned_groups = Groups.objects.filter(
                models.Q(schedule__teacher=teacher) | 
                models.Q(merged_schedules__teacher=teacher)
            ).distinct()

            if assigned_groups.exists():
                return redirect("journal:group_info", group_id=assigned_groups.first().id)
            
            if teacher.curated_group:
                return redirect("journal:group_info", group_id=teacher.curated_group.id)

        return redirect("profile")

    # Студент / Староста
    if hasattr(user, 'student_profile') and user.student_profile.group:
        return redirect("journal:group_info", group_id=user.student_profile.group.id)

    return redirect("profile")

@login_required
def confirm_grades(request, student_id, subject_id, semester):
    user = request.user
    
    # Проверка прав: только TEACHER, DEAN или DIRECTOR. 
    # Учебный отдел и Студенты — мимо.
    if user.role not in [User.Roles.TEACHER, User.Roles.DEAN, User.Roles.DIRECTOR]:
        messages.error(request, "У вас нет прав для подтверждения оценок.")
        return redirect('journal:performance')

    student_user = get_object_or_404(User, id=student_id)
    subject = get_object_or_404(Subject, id=subject_id)
    
    # Вызываем метод модели (убедись, что в RecordBook есть этот метод)
    record = RecordBook.confirm_grades(
        student=student_user,
        subject=subject,
        semester=semester,
        teacher=user
    )
    
    if record:
        messages.success(request, f"Оценка по предмету {subject.name} выставлена в зачетку.")
    else:
        messages.error(request, "Не удалось рассчитать оценку. Проверьте наличие цифровых баллов в журнале.")
    
    return redirect(request.META.get('HTTP_REFERER', 'journal:performance'))

@login_required
def add_grade(request, student_id, subject_id):
    user = request.user 
    
    # СТУДЕНТ НЕ МОЖЕТ ДОБАВЛЯТЬ (кроме Старосты для "Н")
    if user.role == User.Roles.STUDENT or user.role == User.Roles.ACADEMIC_OFFICE:
        messages.error(request, "У вас нет прав для добавления оценок.")
        return redirect('journal:performance')

    student_user = get_object_or_404(User, id=student_id)
    subject = get_object_or_404(Subject, id=subject_id)
    student_profile = getattr(student_user, 'student_profile', None)
    target_group_id = student_profile.group.id if student_profile else None

    if request.method == "POST":
        # Директор и Декан — только просмотр
        if user.role in [User.Roles.DIRECTOR, User.Roles.DEAN]:
            messages.error(request, "Вы в режиме просмотра.")
            return redirect("journal:group_info", group_id=target_group_id)

        grade_val = request.POST.get('grade')
        selected_date = request.POST.get('date') or timezone.now().date()

        if user.role == User.Roles.STAROSTA and grade_val != "Н":
            messages.error(request, "Староста отмечает только отсутствие.")
            return redirect("journal:group_info", group_id=target_group_id)

        Performance.objects.create(student=student_user, subject=subject, date=selected_date, grade=grade_val)
        messages.success(request, "Запись добавлена.")
        return redirect("journal:group_info", group_id=target_group_id)

    return render(request, "add_grade_form.html", {
        "student": student_profile, "subject": subject,
        "current_date": timezone.now().date().isoformat(), "group_id": target_group_id
    })

@login_required
def edit_specific_grade(request, grade_id):
    grade_obj = get_object_or_404(Performance, id=grade_id)
    user = request.user

    # ЗАЩИТА: Только препод или староста. Директор, Декан, Студент, Учебный отдел — НЕТ.
    if user.role in [User.Roles.STUDENT, User.Roles.DIRECTOR, User.Roles.DEAN, User.Roles.ACADEMIC_OFFICE]:
        messages.error(request, "Редактирование запрещено.")
        return redirect("journal:group_info", group_id=grade_obj.student.student_profile.group.id)

    if request.method == "POST":
        if "delete" in request.POST:
            grade_obj.delete()
            return redirect("journal:group_info", group_id=grade_obj.student.student_profile.group.id)

        new_val = request.POST.get('grade')
        if user.role == User.Roles.STAROSTA and new_val != "Н":
            messages.error(request, "Староста может ставить только 'Н'")
            return redirect(request.META.get('HTTP_REFERER'))

        grade_obj.grade = new_val
        grade_obj.save()
        return redirect("journal:group_info", group_id=grade_obj.student.student_profile.group.id)

    return render(request, "edit_grade_form.html", {
        "grade_obj": grade_obj, "student": grade_obj.student.student_profile, "subject": grade_obj.subject,
    })

@login_required
def record_book_view(request):
    if request.user.role == User.Roles.ACADEMIC_OFFICE:
        messages.error(request, "Доступ к зачеткам запрещен.")
        return redirect('profile')
        
    student_profile = getattr(request.user, 'student_profile', None)
    records = request.user.record_entries.select_related("subject", "teacher").order_by("semester")
    
    semesters_data = []
    existing_semesters = records.values_list("semester", flat=True).distinct().order_by("semester")

    for sem_num in existing_semesters:
        sem_records = records.filter(semester=sem_num)
        grades_list = [r.grade for r in sem_records if r.grade]
        avg = sum(grades_list) / len(grades_list) if grades_list else 0
        semesters_data.append({"number": sem_num, "grades": sem_records, "avg": round(avg, 2)})

    return render(request, "record_book.html", {"semesters_data": semesters_data, "profile": student_profile})

@login_required
def edit_evaluations(request, group_id, subject_id):
    user = request.user
    # Только TEACHER или STAROSTA. Все остальные роли — в сад.
    if user.role not in [User.Roles.TEACHER, User.Roles.STAROSTA]:
        messages.error(request, "У вас нет прав на массовое редактирование.")
        return redirect('journal:group_info', group_id=group_id)

    group = get_object_or_404(Groups, id=group_id)
    subject = get_object_or_404(Subject, id=subject_id)
    date_str = request.GET.get('date', timezone.now().date().isoformat())
    students_list = group.students.all().select_related('user')

    if request.method == "POST":
        selected_date = request.POST.get("selected_date") or date_str
        for student_profile in students_list:
            raw_grades = request.POST.get(f"grade_{student_profile.user.id}", "").strip()
            Performance.objects.filter(student=student_profile.user, subject=subject, date=selected_date).delete()

            if raw_grades:
                grades_list = [g.strip() for g in raw_grades.split(',') if g.strip()]
                for grade_val in grades_list:
                    if user.role == User.Roles.STAROSTA and grade_val != "Н":
                        continue 
                    Performance.objects.create(student=student_profile.user, subject=subject, date=selected_date, grade=grade_val)
        
        messages.success(request, "Журнал обновлен.")
        return redirect("journal:group_info", group_id=group.id)

    existing_marks = Performance.objects.filter(subject=subject, date=date_str, student__student_profile__group=group)
    marks_map = defaultdict(list)
    for m in existing_marks:
        marks_map[m.student.id].append(str(m.grade))
    
    formatted_marks_map = {s_id: ", ".join(m_list) for s_id, m_list in marks_map.items()}
    
    return render(request, "edit_evalutions.html", {
        "group": group, "subject": subject, "students": students_list, "marks_map": formatted_marks_map, "current_date": date_str,
    })

@login_required
def group_info(request, group_id):
    current_group = get_object_or_404(Groups, id=group_id)
    subjects = current_group.subjects.all()
    user = request.user
    
    date_filter = request.GET.get('date_filter')
    
    is_teacher_flag = is_teacher(user)
    is_student_flag = user.role in [User.Roles.STUDENT, User.Roles.STAROSTA]

    # --- УЛУЧШЕННАЯ ПРОВЕРКА ДОСТУПА ---
    has_access = False
    
    if is_teacher_flag:
        teacher_profile = getattr(user, 'teacher_profile', None)
        
        # 1. Супер-роли (Директор и Учебная часть) видят вообще всё
        if user.role in [User.Roles.DIRECTOR, User.Roles.ACADEMIC_OFFICE]:
            has_access = True
            
        # 2. Декан видит только группы своего факультета
        elif user.role == User.Roles.DEAN:
            if teacher_profile and teacher_profile.faculti == current_group.faculti:
                has_access = True
                
        # 3. Куратор видит свою группу
        elif teacher_profile and teacher_profile.curated_group == current_group:
            has_access = True
            
        # 4. Преподаватель видит группы, в которых ведет пары по расписанию
        else:
            from apps.Shedule.models import Schedule
            has_access = Schedule.objects.filter(
                models.Q(group=current_group) | models.Q(merged_groups=current_group),
                teacher=teacher_profile
            ).exists()
            
    # 5. Студент видит только свою группу
    else:
        if hasattr(user, 'student_profile') and user.student_profile.group == current_group:
            has_access = True

    if not has_access:
        messages.error(request, "У вас нет прав для просмотра журнала этой группы.")
        return redirect("profile")

    # --- ОСТАЛЬНАЯ ЛОГИКА (БЕЗ ИЗМЕНЕНИЙ) ---
    merged_with_me = Groups.objects.filter(
        models.Q(merged_schedules__group=current_group) | 
        models.Q(schedule__merged_groups=current_group)
    ).distinct().exclude(id=current_group.id)

    students = Student.objects.filter(group=current_group).select_related("user")
    student_ids = [s.user.id for s in students]

    performance_queryset = Performance.objects.filter(
        student_id__in=student_ids, 
        subject__in=subjects
    )
    
    if date_filter:
        performance_queryset = performance_queryset.filter(date=date_filter)

    all_grades = performance_queryset.order_by("date")

    performance_map = defaultdict(lambda: defaultdict(list))
    for g in all_grades:
        performance_map[g.student_id][g.subject.id].append({
            "val": g.grade, 
            "id": g.id,      
            "date": g.date
        })

    performance_data = []
    for s in students:
        grades_dict = performance_map[s.user.id]
        subj_data = {}
        total_absences = 0
        all_numeric_grades = []

        for subj in subjects:
            marks = grades_dict.get(subj.id, [])
            for m in marks:
                if m["val"] == "Н":
                    total_absences += 1
                elif str(m["val"]).isdigit():
                    all_numeric_grades.append(int(m["val"]))
            subj_data[subj.id] = marks

        avg = sum(all_numeric_grades) / len(all_numeric_grades) if all_numeric_grades else 0

        performance_data.append({
            "student": s,
            "student_user": s.user,
            "subjects_marks": subj_data,
            "average_grade": round(avg, 2),
            "total_absences": total_absences,
        })

    return render(request, "group_performance.html", {
        "group": current_group,
        "merged_groups": merged_with_me,
        "subjects": subjects,
        "performance_data": performance_data,
        "is_teacher_flag": is_teacher_flag,
        "is_student_flag": is_student_flag,
        "user_profile": getattr(user, 'student_profile', None),
        "groups": Groups.objects.all(),
        "date_filter": date_filter,
    })

@login_required
def edit_grade(request, student_id, subject_id):
    if request.user.role not in ['DEAN', 'DIRECTOR']:
        messages.error(request, "У вас нет прав для выполнения этого действия.")
        return redirect('journal:performance')
    student_user = get_object_or_404(User, id=student_id)
    subject = get_object_or_404(Subject, id=subject_id)
    user = request.user

    # Проверка доступа: только учитель или староста ЭТОЙ группы
    is_teacher_val = is_teacher(user)
    is_starosta = (user.role == User.Roles.STAROSTA and 
                   hasattr(user, 'student_profile') and 
                   user.student_profile.group == student_user.student_profile.group)

    if not (is_teacher_val or is_starosta):
        messages.error(request, "У вас нет прав для редактирования этой оценки.")
        return redirect("journal:group_info", group_id=student_user.student_profile.group.id)

    grade_instance = Performance.objects.filter(student=student_user, subject=subject).last()

    if request.method == "POST":
        form = GradeForm(request.POST, instance=grade_instance)
        if form.is_valid():
            grade_obj = form.save(commit=False)
            
            # ГЛАВНАЯ ЗАЩИТА: Если староста пытается сохранить что-то, кроме "Н"
            if not is_teacher_val and user.role == User.Roles.STAROSTA:
                if grade_obj.grade not in ["Н", "", None]:
                    messages.error(request, "Староста может только отмечать отсутствие (Н)!")
                    return render(request, "edit_grade.html", {
                        "form": form, "student": student_user.student_profile, "subject": subject, "is_teacher_flag": False
                    })

            grade_obj.student = student_user
            grade_obj.subject = subject
            grade_obj.save()
            messages.success(request, "Данные обновлены")
            return redirect("journal:group_info", group_id=student_user.student_profile.group.id)
    else:
        form = GradeForm(instance=grade_instance)

    return render(request, "edit_grade.html", {
        "form": form, 
        "student": student_user.student_profile,
        "subject": subject,
        "is_teacher_flag": is_teacher_val # Передаем флаг в шаблон
    })

@login_required
def record_book_view(request):
    # Пытаемся получить профиль студента
    student_profile = getattr(request.user, 'student_profile', None)
    
    # Получаем оценки
    records = request.user.record_entries.select_related("subject", "teacher").order_by("semester")
    
    semesters_data = []
    existing_semesters = records.values_list("semester", flat=True).distinct().order_by("semester")

    for sem_num in existing_semesters:
        sem_records = records.filter(semester=sem_num)
        grades_list = [r.grade for r in sem_records if r.grade]
        avg = sum(grades_list) / len(grades_list) if grades_list else 0

        semesters_data.append({
            "number": sem_num,
            "grades": sem_records,
            "avg": round(avg, 2),
        })

    return render(request, "record_book.html", {
        "semesters_data": semesters_data,
        "profile": student_profile, # Теперь тут объект Student с полями familiy, name и group
    })

@login_required
def mass_performance_update(request, group_id, subject_id):
    if request.user.role not in ['DIRECTOR']:
        messages.error(request, "У вас нет прав для выполнения этого действия.")
        return redirect('journal:performance')
    group = get_object_or_404(Groups, id=group_id)
    subject = get_object_or_404(Subject, id=subject_id)
    user = request.user
    
    # Определяем роли
    is_teacher_val = is_teacher(user)
    # Проверяем, является ли пользователь старостой ИМЕННО ЭТОЙ группы
    is_starosta_of_group = (user.role == User.Roles.STAROSTA and 
                            hasattr(user, 'student_profile') and 
                            user.student_profile.group == group)

    # Если не препод и не староста этой группы — выгоняем
    if not (is_teacher_val or is_starosta_of_group):
        messages.error(request, "У вас нет прав для редактирования этого журнала.")
        return redirect("journal:group_info", group_id=group.id)

    students = group.students.all().select_related('user')
    date_str = request.GET.get('date', timezone.now().date().isoformat())

    if request.method == "POST":
        selected_date = request.POST.get("selected_date") or date_str
        
        for student_profile in students:
            grade_value = request.POST.get(f"grade_{student_profile.user.id}")

            # ЗАЩИТА: Если это староста, разрешаем только "Н" или пустоту
            if not is_teacher_val and user.role == User.Roles.STAROSTA:
                if grade_value not in ["Н", "", None]:
                    # Если староста хитрит и шлет цифру — сбрасываем её
                    grade_value = None 

            if grade_value:
                Performance.objects.update_or_create(
                    student=student_profile.user,
                    subject=subject,
                    date=selected_date,
                    defaults={'grade': grade_value}
                )
            else:
                # Если поле пустое — удаляем запись за этот день
                Performance.objects.filter(
                    student=student_profile.user, 
                    subject=subject, 
                    date=selected_date
                ).delete()
        
        messages.success(request, f"Данные за {selected_date} сохранены")
        return redirect("journal:group_info", group_id=group.id)

    # Данные для отображения (GET)
    existing_marks = Performance.objects.filter(
        subject=subject, 
        date=date_str, 
        student__student_profile__group=group
    )
    marks_map = {m.student.id: m.grade for m in existing_marks}
    
    return render(request, "edit_evaluations.html", {
        "group": group,
        "subject": subject,
        "students": students,
        "marks_map": marks_map,
        "current_date": date_str,
        "is_teacher_flag": is_teacher_val, # Чтобы шаблон знал, показывать ли оценки
    })

@login_required
def edit_evaluations(request, group_id, subject_id):
    if request.user.role not in ['DIRECTOR']:
        messages.error(request, "У вас нет прав для выполнения этого действия.")
        return redirect('journal:performance')
    group = get_object_or_404(Groups, id=group_id)
    subject = get_object_or_404(Subject, id=subject_id)
    user = request.user
    
    # Защита: Декан не может править оценки
    if user.role == "DEKAN":
        raise PermissionDenied

    date_str = request.GET.get('date', timezone.now().date().isoformat())
    students_list = group.students.all().select_related('user')

    if request.method == "POST":
        selected_date = request.POST.get("selected_date") or date_str
        
        for student_profile in students_list:
            # Получаем строку из инпута (например, "5, 4, Н")
            raw_grades = request.POST.get(f"grade_{student_profile.user.id}", "").strip()
            
            # 1. Удаляем все старые записи за этот конкретный день по этому предмету, 
            # чтобы перезаписать их актуальным набором.
            Performance.objects.filter(
                student=student_profile.user,
                subject=subject,
                date=selected_date
            ).delete()

            if raw_grades:
                # 2. Разбиваем строку по запятой и убираем лишние пробелы
                # Из "5,  4 , 5" получим ['5', '4', '5']
                grades_list = [g.strip() for g in raw_grades.split(',') if g.strip()]

                for grade_val in grades_list:
                    # 3. Валидация для старосты (только "Н")
                    final_val = grade_val
                    if user.role == User.Roles.STAROSTA and grade_val != "Н":
                        continue # Староста не может ставить цифры, пропускаем

                    # 4. Создаем новую запись для каждой оценки
                    Performance.objects.create(
                        student=student_profile.user,
                        subject=subject,
                        date=selected_date,
                        grade=final_val
                    )
        
        messages.success(request, "Оценки успешно обновлены.")
        return redirect("journal:group_info", group_id=group.id)

    # Собираем оценки для отображения
    existing_marks = Performance.objects.filter(
        subject=subject,
        date=date_str,
        student__student_profile__group=group
    )
    
    # Группируем оценки по студентам: {student_id: "5, 4, 5"}
    marks_map = defaultdict(list)
    for m in existing_marks:
        marks_map[m.student.id].append(str(m.grade))
    
    # Преобразуем списки в строки через запятую для вывода в инпуты
    formatted_marks_map = {s_id: ", ".join(m_list) for s_id, m_list in marks_map.items()}
    
    context = {
        "group": group,
        "subject": subject,
        "students": students_list,
        "marks_map": formatted_marks_map,
        "current_date": date_str,
    }
    return render(request, "edit_evalutions.html", context)