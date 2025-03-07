from django.shortcuts import render
from .models import Profile, Teacher, FAQ
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    return render(request,'home.html')

@login_required
def register(request):
    return render(request, 'register.html')

@login_required
def profile(request):
    return render(request, 'profile.html')

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