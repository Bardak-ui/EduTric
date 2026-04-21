from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path("", views.profile_view, name="profile"),
    # path("teacher/", views.profile_teacher, name="profile_teacher"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("edit-profile/teacher/", views.edit_profile_teacher, name="edit_profile_teacher"),
    path("search_user/", views.search_user, name="search_user"),
    path("student-dashboard/", views.student_dashboard, name="student_dashboard"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
