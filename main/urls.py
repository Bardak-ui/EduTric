from django.contrib.auth.views import LoginView
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #path('', views.profile, name='profile'),
    #path('logout/', views.logout_view, name='logout_view'), # Страница выхода
    path('', LoginView.as_view(template_name = 'login.html'), name='login'), # Страница входа
    path('home/', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
    path('schedule/', views.schedule, name='schedule'),
    path('schedule/group/<str:group_id>/', views.schedule, name='schedule_group'),
    path("schedule/add/", views.add_schedule, name="add_schedule"),
    path('search_user/', views.search_user, name='search_user'),
    path('FAQ/', views.FAQ_LIST, name='FAQ_LIST'),
    path('ads/', views.ads, name='ads'),
    path('pay/', views.pay, name='pay'),
    #path('edit_evalutions/', views.edit_evalutions, name='edit_evalutions'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)