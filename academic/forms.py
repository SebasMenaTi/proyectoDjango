# apps/academic/forms.py

from django import forms
from .models import Student, AcademicRecord

class StudentForm(forms.ModelForm):
    """Formulario para crear/editar estudiantes"""
    
    class Meta:
        model = Student
        fields = ['name', 'email']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nombre completo'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'correo@ejemplo.com'
            }),
        }
        labels = {
            'name': 'Nombre completo',
            'email': 'Correo electrónico',
        }


class AcademicRecordForm(forms.ModelForm):
    """Formulario para ingresar registros académicos"""
    
    class Meta:
        model = AcademicRecord
        fields = ['student', 'date', 'study_hours', 'tasks_delivered', 'attendance', 
                  'sleep_hours', 'delivery_delays', 'academic_activity_time']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'study_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0', 'max': '24'}),
            'tasks_delivered': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'attendance': forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '0', 'max': '100'}),
            'sleep_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0', 'max': '24'}),
            'delivery_delays': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'academic_activity_time': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0'}),
        }
        labels = {
            'student': 'Estudiante',
            'date': 'Fecha',
            'study_hours': 'Horas de estudio',
            'tasks_delivered': 'Tareas entregadas',
            'attendance': 'Asistencia (%)',
            'sleep_hours': 'Horas de sueño',
            'delivery_delays': 'Retrasos en entregas',
            'academic_activity_time': 'Tiempo actividad académica (horas)',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        study_hours = cleaned_data.get('study_hours')
        sleep_hours = cleaned_data.get('sleep_hours')
        
        if study_hours and sleep_hours and (study_hours + sleep_hours > 24):
            raise forms.ValidationError("La suma de horas de estudio y sueño no puede exceder 24 horas.")
        
        return cleaned_data