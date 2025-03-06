from django.shortcuts import render
from .models import Profile, Teacher, FAQ

def home(request):
    return render(request,'home.html')

def register(request):
    return render(request, 'register.html')

def profile(request):
    return render(request, 'profile.html')

def schebule(request):
    return render(request, 'schebule.html')

def search_user(request):
    return render(request, 'search_user.html')

def ads(request):
    return render(request, 'ads.html')

def FAQ_LIST(request):
    faqs = FAQ.objects.all()
    return render(request, 'faq_list.html', {'faqs': faqs})

def pay(request):
    return render(request, 'ads.html')