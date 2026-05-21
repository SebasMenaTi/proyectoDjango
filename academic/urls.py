# apps/academic/urls.py

from django.urls import path
from . import views

app_name = 'academic'

urlpatterns = [
    # Dashboard y vistas principales
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # CRUD de Estudiantes
    path('students/', views.student_list, name='student_list'),
    path('students/create/', views.student_create, name='student_create'),
    path('students/<int:pk>/update/', views.student_update, name='student_update'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
    
    # Registros académicos
    path('records/create/', views.record_create, name='record_create'),
    
    # Análisis y predicciones
    path('analysis/batch/', views.run_batch_analysis, name='batch_analysis'),
    path('alerts/', views.stress_alerts, name='stress_alerts'),
    path('predictions/', views.prediction_list, name='prediction_list'),
    # Ver Registros
    path('records/', views.all_records, name='all_records'),
    path('records/<int:pk>/', views.record_detail, name='record_detail'),
    path('records/<int:pk>/delete/', views.record_delete, name='record_delete'),
]