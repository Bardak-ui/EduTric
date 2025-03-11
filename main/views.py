from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Teacher, FAQ
from django.contrib.auth.decorators import login_required
from .forms import CustomeUserForm, CreateProfile, CreateProfileTeacher, EditProfile, EditProfileTeacher

@login_required
def home(request):
    return render(request,'home.html')

def register(request):
    if request.method == 'POST':
        form = CustomeUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = CustomeUserForm()
    return render(request, 'register.html', {'form':form})

@login_required
def profile(request):
    profile = get_object_or_404(Profile, user = request.user)
    return render(request, 'profile.html', {'profile':profile})

@login_required
def schebule(request):
    return render(request, 'schebule.html')

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