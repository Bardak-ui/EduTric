from django.contrib.auth.views import LoginView
from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile, name='profile'),
    #path('logout/', views.logout_view, name='logout_view'), # Страница выхода
    path('login/', LoginView.as_view(template_name = 'login.html'), name='login'), # Страница входа
    path('home/', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
    path('schebule/', views.schebule, name='schebule'),
    path('search_user/', views.search_user, name='search_user'),
    path('FAQ/', views.FAQ_LIST, name='FAQ_LIST'),
    path('ads/', views.ads, name='ads'),
    path('pay/', views.pay, name='pay'),
]