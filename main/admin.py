from django.contrib import admin
from .models import Teacher,Kurator,Profile,Role,Groups,Faculti

admin.site.register(Profile)
admin.site.register(Teacher)
admin.site.register(Kurator)
admin.site.register(Role)
admin.site.register(Groups)
admin.site.register(Faculti)