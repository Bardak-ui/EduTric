from django.urls import path

from . import views
app_name = "journal"

urlpatterns = [
    path("group/<int:group_id>/", 
        views.group_info,
        name="group_info"
    ),
    path("performance/", 
        views.performance_view, 
        name="performance"
    ),
    path(
        "edit-grade/<int:student_id>/<int:subject_id>/",
        views.edit_grade,
        name="edit_grade",
    ),
    path('my-record-book/', 
         views.record_book_view, 
         name='record_book_view'
    ),
    path(
        "group/<int:group_id>/subject/<int:subject_id>/mass/",
        views.mass_performance_update,
        name="mass_grade",
    ),
    path(
        "group/<int:group_id>/subject/<int:subject_id>/edit-pair/", 
        views.edit_evaluations, 
        name="edit_evaluations"
    ),
    path("confirm-record/<int:student_id>/<int:subject_id>/<int:semester>/", 
        views.confirm_grades, 
        name="confirm_grades"
    ),
    path('grade/add/<int:student_id>/<int:subject_id>/', 
        views.add_grade, 
        name='add_grade_page'
    ),
    path('grade/edit/<int:grade_id>/', 
        views.edit_specific_grade, 
        name='edit_specific_grade'
    ),
]
