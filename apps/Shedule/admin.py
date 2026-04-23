from django.contrib import admin

from .models import Faculty, Groups, Kurator, LessonTime, Schedule, Subject, Course


@admin.register(LessonTime)
class LessonTimeAdmin(admin.ModelAdmin):
    list_display = ("lesson_number", "start_time", "end_time")
    list_editable = ("start_time", "end_time")
    search_fields = ("lesson_number",)
    ordering = ("lesson_number",)


@admin.register(Groups)
class GroupsAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'faculty']
    list_filter = ['faculty', 'course']
    filter_horizontal = ['subjects'] # Удобный выбор учебного плана
    search_fields = ['name']

# Создаем "встройку" групп для факультета
class GroupsInline(admin.TabularInline):
    model = Groups
    extra = 1  # Количество пустых строк для добавления новых групп
    fields = ['name', 'course', 'subjects']
    filter_horizontal = ['subjects'] # Делает выбор предметов удобным (два окна)

@admin.register(Faculty)
class FacultiAdmin(admin.ModelAdmin):
    list_display = ['name']
    inlines = [GroupsInline] # Добавляем группы внутрь страницы факультета


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "weekday",
        "group",
        "subject",
        "teacher",
        "lesson_time",
        "room",
        "is_even_week",
    )
    list_filter = ("weekday", "group", "teacher", "is_even_week")
    search_fields = ("group__name", "subject__name", "teacher__user__username", "room")
    filter_horizontal = ("merged_groups",)
    ordering = ("weekday", "lesson_time__lesson_number")


admin.site.register(Kurator)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "teacher")
    search_fields = ("name",)

admin.site.register(Course)
