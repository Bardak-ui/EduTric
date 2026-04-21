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
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Роль пользователя", {"fields": ("role",)}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("Роль пользователя", {"fields": ("role",)}),
    )
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_staff",
        "is_active",
    )
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    inlines = [StudentInline, TeacherInline]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("user", "group", "student_id", "is_curator")
    search_fields = ("user__username", "student_id", "group__name")
    list_filter = ("group", "is_curator")


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    # Исправляем отображение в списке
    list_display = ("user", "faculti", "is_dean", "curated_group")
    
    # Исправляем поиск (теперь ищем по названию связанного факультета)
    search_fields = ("user__username", "user__last_name", "faculti__name")
    
    # Исправляем фильтры в правой колонке
    list_filter = ("faculti", "is_dean")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name",)
