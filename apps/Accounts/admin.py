from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import Role, Student, Teacher, User


class StudentInline(admin.StackedInline):
    model = Student
    can_delete = False
    verbose_name = "Студент"
    verbose_name_plural = "Студенты"


class TeacherInline(admin.StackedInline):
    model = Teacher
    can_delete = False
    verbose_name = "Преподаватель"
    verbose_name_plural = "Преподаватели"


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = (
        "username",
        "email",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "surname", "name")
    inlines = [StudentInline, TeacherInline]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("user", "group", "student_id", "is_curator")
    search_fields = ("user__username", "student_id", "group__name")
    list_filter = ("group", "is_curator")


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("user", "surname", "name", "faculty", "is_dean", "curated_group", "get_subjects")
    search_fields = ("user__username", "surname", "name", "faculty__name")
    list_filter = ("faculty", "is_dean", "subjects")
    filter_horizontal = ("subjects",)
    
    def get_subjects(self, obj):
        return ", ".join([s.name for s in obj.subjects.all()])
    get_subjects.short_description = "Предметы"


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name",)
