from django.contrib.auth.views import LoginView
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', LoginView.as_view(template_name = 'login.html'), name='login'), # Страница входа
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('register/', views.register, name='register'),
    path('schedule/', views.schedule, name='schedule'),  # Без group_id
    path('schedule/group/<int:group_id>/', views.schedule, name='schedule_group'),
    path("schedule/add/", views.add_schedule, name="add_schedule"),
    path('search_user/', views.search_user, name='search_user'),
    path('FAQ/', views.FAQ_LIST, name='FAQ_LIST'),
    path('FAQ/add/', views.add_faq, name='add_faq'),
    path('FAQ/edit/<int:faq_id>/', views.edit_faq, name='edit_faq'),
    path('FAQ/delete/<int:faq_id>/', views.delete_faq, name='delete_faq'),
    path('news/', views.news, name='news'),
    path('news/add/', views.add_news, name='add_news'),
    path('schedule/edit/<int:schedule_id>/', views.edit_schedule, name='edit_schedule'),
    path('schedule/delete/<int:schedule_id>/', views.delete_schedule, name='delete_schedule'),


# НА РАССМОТРЕНИИ
    #path('logout/', views.logout_view, name='logout_view'), # Страница выхода
    # path('pay/', views.pay, name='pay'),
    #path('home/', views.home, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)