from django.urls import path

from . import views

urlpatterns = [
    path("schedule/", views.schedule, name="schedule"),  # Без group_id
    path("schedule/add/<int:group_id>/", views.add_schedule, name="add_schedule"),
    path("schedule/group/<int:group_id>/", views.schedule, name="schedule_group"),
    path("schedule/edit/<int:schedule_id>/", views.edit_schedule, name="edit_schedule"),
    path(
        "schedule/delete/<int:schedule_id>/",
        views.delete_schedule,
        name="delete_schedule",
    ),
    path("api/teachers-by-subject/<int:subject_id>/", views.api_get_teachers_by_subject, name="api_get_teachers_by_subject"),
]
