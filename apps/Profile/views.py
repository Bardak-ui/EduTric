from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from apps.Accounts.models import Student, Teacher

from .forms import EditProfileStudent, EditProfileTeacher

import qrcode
import io
import base64


@login_required
def profile_view(request):
    user = request.user
    context = {}
    qr_code_image = None

    # 1. Логика для ПРЕПОДАВАТЕЛЯ и АДМИНИСТРАЦИИ
    if user.is_teacher or user.is_dean or user.is_admin or user.is_director or user.is_academic_office:
        profile, created = Teacher.objects.get_or_create(
            user=user,
            defaults={
               "department_name": "Не указана",
               "is_dean": user.is_dean,
            },
        )
        context["profile"] = profile

    # 2. Логика для СТУДЕНТА и СТАРОСТЫ
    else:
        profile = Student.objects.filter(user=user).first()
        if not profile:
            return redirect("register")
        
        context["profile"] = profile
        
        # Генерируем QR-код
        qr_data = f"STUDENT_PASS:{profile.student_id}"
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        qr_code_image = f"data:image/png;base64,{qr_base64}"

    context["qr_code_image"] = qr_code_image
    
    return render(request, "profile.html", context)


@login_required
def student_dashboard(request):
    if not request.user.is_student:
        return redirect("profile")

    student = get_object_or_404(Student, user=request.user)
    return render(request, "student_dashboard.html", {"student": student})


@login_required
def edit_profile(request):
    student = get_object_or_404(Student, user=request.user)

    if request.method == "POST":
        form = EditProfileStudent(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = EditProfileStudent(instance=student)

    return render(request, "edit_profile.html", {"form": form})


@login_required
def edit_profile_teacher(request):
    teacher, created = Teacher.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = EditProfileTeacher(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            form.save()
            return redirect("profile") 
    else:
        form = EditProfileTeacher(instance=teacher)

    return render(request, "edit_profile_teacher.html", {"form": form})


@login_required
def search_user(request):
    search_query = request.GET.get("search", "")
    if search_query:
        students = Student.objects.filter(
            Q(user__first_name__icontains=search_query) | 
            Q(user__last_name__icontains=search_query)
        )
    else:
        students = Student.objects.none()

    return render(
        request,
        "search_user.html",
        {"students": students, "search_query": search_query},
    )