from django.shortcuts import render, redirect, get_object_or_404
from time import timezone
from .models import Profile, Teacher, FAQ, Schedule, Performance,Groups, News
from django.contrib.auth.decorators import login_required,  user_passes_test
from .forms import CustomeUserForm, CreateProfile, CreateProfileTeacher, EditProfile, EditProfileTeacher,ScheduleForm, NewsForm, AddFAQ, EditFAQ
from django.db.models import Q  # Импортируем Q для сложных запросов
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def is_staff(user):
    return user.is_staff

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
def search_user(request):
    search_query = request.GET.get('search', '')  # Получаем поисковый запрос из GET-параметра
    if search_query:  # Проверяем, что поисковый запрос не пустой
        # Используем Q-объекты для поиска по фамилии, имени и отчеству
        profiles = Profile.objects.filter(
            Q(familiy__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(otchestvo__icontains=search_query)
        )
    else:
        profiles = Profile.objects.none()  # Если запрос пустой, возвращаем пустой QuerySet

    return render(request, 'search_user.html', {'profiles': profiles, 'search_query': search_query})
@login_required
def FAQ_LIST(request):
    faqs = FAQ.objects.all()
    return render(request, 'faq_list.html', {'faqs': faqs})

@login_required
def pay(request):
    return render(request, 'pay.html')

@login_required
def schedule(request, group_id=None):
    groups = Groups.objects.all()
    selected_group = None
    schedule = Schedule.objects.all()

    if group_id:
        selected_group = get_object_or_404(Groups, id=group_id)
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
@user_passes_test(is_staff)
def add_schedule(request):
    if request.method == "POST":
        form = ScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("schedule")
    else:
        form = ScheduleForm()

    return render(request, "schedule_form.html", {"form": form, "action": "add"})

def edit_evalutions(request):
    return render(request, 'edit_evalutions.html')

@login_required
def news(request):
    news_list = News.objects.all()
    paginator = Paginator(news_list, 10)  # 10 новостей на страницу
    page = request.GET.get('page')

    try:
        news = paginator.page(page)
    except PageNotAnInteger:
        news = paginator.page(1)
    except EmptyPage:
        news = paginator.page(paginator.num_pages)

    profile = Profile.objects.filter(user=request.user).first()
    return render(request, 'news.html', {'news_list': news, 'profile': profile})

@login_required
def profile(request):
    profile = Profile.objects.filter(user=request.user).first()  # Оптимизированный запрос
    if not profile:
        return redirect('register')  # Перенаправляем, если профиль не существует
    return render(request, 'profile.html', {'profile': profile})

@login_required
def edit_profile(request):
    # Получаем профиль текущего пользователя
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        # Передаем данные из запроса и файлы (если есть) в форму
        form = EditProfile(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()  # Сохраняем изменения
            return redirect('profile')  # Перенаправляем на страницу профиля
    else:
        # Если запрос GET, отображаем форму с текущими данными профиля
        form = EditProfile(instance=profile)

    return render(request, 'edit_profile.html', {'form': form})

@login_required
@user_passes_test(is_staff)
def add_news(request):
    if request.method == "POST":
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("news")
    else:
        form = NewsForm()
    return render(request, "news_form.html", {'form': form}) 
def get_schedule_or_404(schedule_id):
    return get_object_or_404(Schedule, id=schedule_id)

@login_required
@user_passes_test(is_staff)
def edit_schedule(request, schedule_id):
    schedule = get_schedule_or_404(schedule_id)
    if request.method == "POST":
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            return redirect("schedule")
    else:
        form = ScheduleForm(instance=schedule)

    return render(request, "schedule_form.html", {"form": form, "action": "edit"})

@login_required
@user_passes_test(is_staff)
def delete_schedule(request, schedule_id):
    schedule = get_schedule_or_404(schedule_id)
    if request.method == "POST":
        schedule.delete()
        return redirect("schedule")
    return render(request, "confirm_delete.html", {"schedule": schedule})

def get_faq_or_404(faq_id):
    return get_object_or_404(FAQ, id=faq_id)

@login_required
@user_passes_test(is_staff)
def add_faq(request):
    if request.method == 'POST':
        # Передаем данные из запроса и файлы (если есть) в форму
        form = AddFAQ(request.POST)
        if form.is_valid():
            form.save()  # Сохраняем изменения
            return redirect('FAQ_LIST')  # Перенаправляем на страницу профиля
    else:
        # Если запрос GET, отображаем форму с текущими данными профиля
        form = AddFAQ()

    return render(request, 'add_faq.html', {'form': form})

@login_required
@user_passes_test(is_staff)
def delete_faq(request, faq_id):
    faq = get_faq_or_404(faq_id)
    if request.method == "POST":
        faq.delete()
        return redirect("FAQ_LIST")
    return render(request, "delete_faq.html", {"faq": faq})

@login_required
@user_passes_test(is_staff)
def edit_faq(request, faq_id):
    faq = get_faq_or_404(faq_id)
    if request.method == "POST":
        form = EditFAQ(request.POST, instance=faq)
        if form.is_valid():
            form.save()
            return redirect("FAQ_LIST")
    else:
        form = EditFAQ(instance=faq)

    return render(request, "edit_faq.html", {"form": form, 'faq':faq,"action": "edit"})