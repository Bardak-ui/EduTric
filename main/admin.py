from django.contrib import admin
from .models import Teacher,Kurator,Profile,Role,Groups,Faculti,FAQ,Schedule,Subject,LessonTime,News
from .models import LessonTime

@admin.register(LessonTime)
class LessonTimeAdmin(admin.ModelAdmin):
    list_display = ('lesson_number', 'start_time', 'end_time','start_time_1', 'end_time_1', 'start_time_2', 'end_time_2')
    list_editable = ('start_time', 'end_time','start_time_1', 'end_time_1', 'start_time_2', 'end_time_2')

admin.site.register(Profile)
admin.site.register(Teacher)
admin.site.register(Kurator)
admin.site.register(Role)
admin.site.register(Groups)
admin.site.register(Faculti)
admin.site.register(FAQ)
admin.site.register(Schedule)
admin.site.register(Subject)
admin.site.register(News)