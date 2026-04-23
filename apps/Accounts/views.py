from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from .forms import CreateStudent, CreateProfileTeacher, CustomeUserForm, ExtendedRegistrationForm
from .models import Student, Teacher, User
from apps.Profile.signals import generate_unique_id

@login_required
def redirect_after_login(request):
    return redirect("profile")

@transaction.atomic
def register(request):
    if request.method == "POST":
        form = ExtendedRegistrationForm(request.POST)
        secure_code = request.POST.get("secure_code")
        
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data.get('role')
            staff_roles = ['TEACHER', 'DEAN', 'DIRECTOR', 'ACADEMIC']

            if role in staff_roles:
                # ПРОВЕРКА КОДА
                if secure_code != "Gt$0X1hS%_":
                    form.add_error('secure_code', "Неверный код доступа")
                    return render(request, "register.html", {"form": form})

                # СОЗДАЕМ Преподавателя
                teacher = Teacher.objects.create(
                    user=user,
                    faculti=form.cleaned_data.get('department'), # ForeignKey Faculti
                    is_dean=form.cleaned_data.get('is_dean', False),
                    curated_group=form.cleaned_data.get('curated_group')
                )
                if form.cleaned_data.get('subjects'):
                    teacher.subjects.set(form.cleaned_data['subjects'])
                user.is_staff = True
                user.save()
            else:
                # СОЗДАЕМ СТУДЕНТА
                Student.objects.create(
                    user=user,
                    student_id=generate_unique_id(),
                    surname=form.cleaned_data.get('surname'),
                    name=form.cleaned_data.get('name'),
                    patronymic=form.cleaned_data.get('patronymic'),
                    faculty=form.cleaned_data.get('faculti'), # CharField
                    phone=form.cleaned_data.get('phone'),
                    group=form.cleaned_data.get('group'),
                    birthday=form.cleaned_data.get('birthday'),
                    is_curator=(role == "STAROSTA")
                )

            login(request, user)
            return redirect("profile")
    else:
        form = ExtendedRegistrationForm()
    return render(request, "register.html", {"form": form})