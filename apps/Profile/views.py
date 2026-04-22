from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from apps.Accounts.models import Student, Teacher

from .forms import EditProfile, EditProfileTeacher

import qrcode
import io
import base64

def is_staff(user):
    return user.is_staff


@login_required
def profile_view(request):
    user = request.user
    teacher_roles = ["TEACHER", "DEAN", "DIRECTOR", "ACADEMIC_OFFICE"]
    
    context = {}
    qr_code_image = None

    # 1. Логика для ПРЕПОДАВАТЕЛЯ и АДМИНИСТРАЦИИ
    if user.role in teacher_roles:
        profile, created = Teacher.objects.get_or_create(
            user=user,
            defaults={
                # "last_name": user.teacher.last_name,
                # "first_name": user.teacher.first_name 
                "department": "Не указана",
                "is_dean": user.role == "DEAN",
            },
        )
        context["profile"] = profile # Используем универсальное имя 'profile'
        # Пропуск и QR для учителей НЕ генерируем по твоему условию

    # 2. Логика для СТУДЕНТА и СТАРОСТЫ
    else:
        profile = Student.objects.filter(user=user).first()
        if not profile:
            return redirect("register")
        
        context["profile"] = profile
        
        # Генерируем QR-код только для студентов/старост
        qr_data = f"STUDENT_PASS:{profile.student_id}"
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        qr_code_image = f"data:image/png;base64,{qr_base64}"

    # Добавляем общие данные в контекст
    context["qr_code_image"] = qr_code_image
    
    return render(request, "profile.html", context)


@login_required
def student_dashboard(request):
    if request.user.role not in ['STUDENT', 'STAROSTA']:
        return redirect("profile")

    student = get_object_or_404(Student, user=request.user)
    # Add dashboard logic: schedule, grades, etc.
    return render(request, "student_dashboard.html", {"student": student})


@login_required
def edit_profile(request):
    # Получаем профиль текущего пользователя
    student = get_object_or_404(Student, user=request.user)

    if request.method == "POST":
        # Передаем данные из запроса и файлы (если есть) в форму
        form = EditProfile(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()  # Сохраняем изменения
            return redirect("profile")  # Перенаправляем на страницу профиля
    else:
        # Если запрос GET, отображаем форму с текущими данными профиля
        form = EditProfile(instance=student)

    return render(request, "edit_profile.html", {"form": form})


# @login_required
# def profile_teacher(request):
#     teacher_roles = ["TEACHER", "DEAN", "DIRECTOR", "ACADEMIC_OFFICE"]
#     if request.user.role not in teacher_roles:
#         return redirect("profile")

#     teacher, created = Teacher.objects.get_or_create(
#         user=request.user,
#         defaults={
#             "department": "",
#             "is_dean": request.user.role == "DEAN",
#         },
#     )
#     return render(request, "profile_teacher.html", {"teacher": teacher})


@login_required
def edit_profile_teacher(request):
    # Исправляем: используем get_or_create, чтобы не вылетала ошибка 404, если профиль еще не создан
    teacher, created = Teacher.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = EditProfileTeacher(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            form.save()
            # После редактирования возвращаем на общую страницу профиля
            return redirect("profile") 
    else:
        form = EditProfileTeacher(instance=teacher)

    return render(request, "edit_profile_teacher.html", {"form": form})


@login_required
def search_user(request):
    search_query = request.GET.get("search", "")  # Получаем поисковый запрос из GET-параметра
    if search_query:  # Проверяем, что поисковый запрос не пустой
        # Используем Q-объекты для поиска по фамилии, имени и отчеству
        students = Student.objects.filter(
            Q(user__first_name__icontains=search_query) | Q(user__last_name__icontains=search_query)
        )
    else:
        students = Student.objects.none()  # Если запрос пустой, возвращаем пустой QuerySet

    return render(
        request,
        "search_user.html",
        {"students": students, "search_query": search_query},
    )
