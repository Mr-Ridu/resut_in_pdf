from django.contrib import admin
from .models import SchoolSettings, ResultHistory

@admin.register(SchoolSettings)
class SchoolSettingsAdmin(admin.ModelAdmin):
    list_display = ['school_name', 'user', 'paper_size', 'orientation', 'font_style']
    search_fields = ['school_name', 'user__username']
    list_filter = ['paper_size', 'orientation', 'font_style']

@admin.register(ResultHistory)
class ResultHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_students', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at']