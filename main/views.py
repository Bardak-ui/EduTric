from django.shortcuts import render, redirect, get_object_or_404
from time import timezone
from .models import Profile, Teacher, FAQ, Schedule, Performance,Groups
from django.contrib.auth.decorators import login_required
from .forms import CustomeUserForm, CreateProfile, CreateProfileTeacher, EditProfile, EditProfileTeacher,ScheduleForm

@login_required
def home(request):
    return render(request,'home.html')

def register(request):
    if request.method == 'POST':
        form_acc = CustomeUserForm(request.POST)
        form_prof = CreateProfile(request.POST)
        if form_acc.is_valid() and form_prof.is_valid():
            user = form_acc.save()  # Создаем пользователя
            profile = form_prof.save(commit=False)
            profile.user = user
            profile.save()  # Обновляем профиль с данными из формы
            return redirect('/')
        else:
            print("Ошибки в форме пользователя:", form_acc.errors)
            print("Ошибки в форме профиля:", form_prof.errors)
    else:
        form_acc = CustomeUserForm()
        form_prof = CreateProfile()
    
    return render(request, 'register.html', {
        'form_acc': form_acc,
        'form_prof': form_prof,
    })

@login_required
def performance_view(request):
    student_performance = Performance.objects.filter(
        student=request.user
    ).select_related('subject')
    
    return render(request, 'performance.html', {'performance': student_performance})

@login_required
def group_info(request):
    group = request.user.student.group
    students = group.student_set.all()
    return render(request, 'group.html', {'group': group, 'students': students})


@login_required
def profile(request):
    profile = get_object_or_404(Profile, user = request.user)
    return render(request, 'profile.html', {'profile':profile})

@login_required
def schedule(request):
    return render(request, 'schedule.html')

@login_required
def search_user(request):
    return render(request, 'search_user.html')

@login_required
def ads(request):
    return render(request, 'ads.html')

@login_required
def FAQ_LIST(request):
    faqs = FAQ.objects.all()
    return render(request, 'faq_list.html', {'faqs': faqs})

@login_required
def pay(request):
    return render(request, 'ads.html')
    
@login_required
def schedule(request, group_id=None):
    # Получаем все группы
    selected_group = None
    schedule = Schedule.objects.all()
    groups = Groups.GROUPS_CHOICES

    # Получаем расписание для выбранной группы
    selected_group = group_id
    schedule = Schedule.objects.all()

    if group_id:
        selected_group = Groups.objects.get(id=group_id)
        schedule = schedule.filter(group=selected_group)

    # Группируем расписание по дням недели
    schedule_by_day = {}
    for day in Schedule.WEEKDAYS:
        schedule_by_day[day[1]] = schedule.filter(weekday=day[0]).order_by('lesson_time__lesson_number')

    return render(request, 'schedule.html', {
        'groups': groups,
        'selected_group': selected_group,
        'schedule_by_day': schedule_by_day,
    })
    
@login_required
def add_schedule(request):
    if request.method == "POST":
        form = ScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("schedule")
    else:
        form = ScheduleForm()

    return render(request, "schedule_form.html", {"form": form})

def edit_evalutions(request):
    return render(request, 'edit_evalutions.html')