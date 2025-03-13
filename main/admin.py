from django.contrib import admin
from .models import Teacher,Kurator,Profile,Role,Groups,Faculti,FAQ,Schedule,Subject,LessonTime

admin.site.register(Profile)
admin.site.register(Teacher)
admin.site.register(Kurator)
admin.site.register(Role)
admin.site.register(Groups)
admin.site.register(Faculti)
admin.site.register(FAQ)
admin.site.register(Schedule)
admin.site.register(Subject)
admin.site.register(LessonTime)