# apps/academic/admin.py

from django.contrib import admin
from .models import Student, AcademicRecord, HMMPrediction, AnalysisHistory

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'enrollment_date')
    search_fields = ('name', 'email')
    list_filter = ('enrollment_date',)
    ordering = ('-enrollment_date',)

@admin.register(AcademicRecord)
class AcademicRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'study_hours', 'attendance', 'sleep_hours')
    list_filter = ('date', 'student')
    search_fields = ('student__name',)
    date_hierarchy = 'date'

@admin.register(HMMPrediction)
class HMMPredictionAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'hidden_state', 'is_stressed', 'probability')
    list_filter = ('hidden_state', 'is_stressed', 'date')
    search_fields = ('student__name',)
    readonly_fields = ('created_at',)

@admin.register(AnalysisHistory)
class AnalysisHistoryAdmin(admin.ModelAdmin):
    list_display = ('execution_date', 'students_analyzed', 'stress_alerts_count')
    list_filter = ('execution_date',)
    readonly_fields = ('execution_date',)