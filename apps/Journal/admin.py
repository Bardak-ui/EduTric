from django.contrib import admin
from .models import Performance, RecordBook

@admin.register(RecordBook)
class RecordBookAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'grade', 'semester', 'test_type')
    list_filter = ('semester', 'test_type')
    search_fields = ('student__username', 'subject__name')

admin.site.register(Performance)
