# apps/academic/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Count, Avg
from django.contrib.auth.decorators import login_required
from .models import Student, AcademicRecord, HMMPrediction, AnalysisHistory
from .forms import StudentForm, AcademicRecordForm
from .hmm_model import AcademicStressHMM, prepare_observations_from_records
import numpy as np
from datetime import datetime

# Instancia global del HMM
hmm_model = AcademicStressHMM()

@login_required
def dashboard(request):
    """Dashboard principal con estadísticas"""
    total_students = Student.objects.count()
    total_records = AcademicRecord.objects.count()
    total_predictions = HMMPrediction.objects.count()
    stress_alerts = HMMPrediction.objects.filter(is_stressed=True).count()
    
    # Predicciones recientes
    recent_predictions = HMMPrediction.objects.select_related('student').order_by('-date')[:10]
    
    # Estadísticas por estado
    state_stats = {}
    for state_code, state_name in HMMPrediction.ESTADO_CHOICES:
        count = HMMPrediction.objects.filter(hidden_state=state_code).count()
        state_stats[state_name] = count
    
    context = {
        'total_students': total_students,
        'total_records': total_records,
        'total_predictions': total_predictions,
        'stress_alerts': stress_alerts,
        'recent_predictions': recent_predictions,
        'state_stats': state_stats,
    }
    return render(request, 'academic/dashboard.html', context)

@login_required
def student_list(request):
    """Lista de estudiantes con CRUD"""
    students = Student.objects.all().prefetch_related('records')
    return render(request, 'academic/student_list.html', {'students': students})

@login_required
def student_create(request):
    """Crear nuevo estudiante"""
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, ' Estudiante creado exitosamente.')
            return redirect('academic:student_list')
    else:
        form = StudentForm()
    return render(request, 'academic/student_form.html', {'form': form, 'title': 'Crear Estudiante'})

@login_required
def student_update(request, pk):
    """Editar estudiante existente"""
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, ' Estudiante actualizado correctamente.')
            return redirect('academic:student_list')
    else:
        form = StudentForm(instance=student)
    return render(request, 'academic/student_form.html', {'form': form, 'title': 'Editar Estudiante'})

@login_required
def student_delete(request, pk):
    """Eliminar estudiante"""
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student_name = student.name
        student.delete()
        messages.success(request, f' Estudiante "{student_name}" eliminado.')
        return redirect('academic:student_list')
    return render(request, 'academic/student_confirm_delete.html', {'student': student})

@login_required
def record_create(request):
    """Crear registro académico y ejecutar predicción HMM"""
    if request.method == 'POST':
        form = AcademicRecordForm(request.POST)
        if form.is_valid():
            record = form.save()
            
            # Ejecutar predicción HMM
            predict_student_state(record.student, record.date)
            
            messages.success(request, ' Registro creado y análisis HMM completado.')
            return redirect('academic:student_list')
    else:
        form = AcademicRecordForm()
    return render(request, 'academic/record_form.html', {'form': form})

def predict_student_state(student, target_date):
    """
    Función principal que utiliza el HMM para predecir estado de un estudiante.
    """
    # Obtener registros históricos
    historical_records = AcademicRecord.objects.filter(
        student=student, 
        date__lte=target_date
    ).order_by('date')
    
    if historical_records.count() < 1:
        return None
    
    # Preparar observaciones
    observations = []
    for record in historical_records:
        obs = [
            record.study_hours,
            record.tasks_delivered,
            record.attendance,
            record.sleep_hours,
            record.delivery_delays,
            record.academic_activity_time
        ]
        observations.append(obs)
    
    # Entrenar modelo con datos históricos de todos los estudiantes
    all_sequences = []
    all_students = Student.objects.all()
    for s in all_students:
        seq = AcademicRecord.objects.filter(student=s).order_by('date')
        if seq.count() >= 1:
            obs_seq = []
            for rec in seq:
                obs_seq.append([
                    rec.study_hours, rec.tasks_delivered, rec.attendance,
                    rec.sleep_hours, rec.delivery_delays, rec.academic_activity_time
                ])
            if len(obs_seq) > 0:
                all_sequences.append(np.array(obs_seq))
    
    if len(all_sequences) > 0:
        hmm_model.train(all_sequences)
    
    # Predecir estado
    states, probabilities = hmm_model.predict(observations)
    
    # Último estado
    last_state = states[-1] if len(states) > 0 else 0
    state_name = hmm_model.get_state_name(last_state)
    is_stressed = hmm_model.is_stressed(last_state)
    
    # Guardar predicción
    prediction, created = HMMPrediction.objects.update_or_create(
        student=student,
        date=target_date,
        defaults={
            'hidden_state': state_name.lower(),
            'probability': float(probabilities[-1][last_state]) if len(probabilities) > 0 else 0.5,
            'is_stressed': is_stressed
        }
    )
    
    return prediction

@login_required
def run_batch_analysis(request):
    """Ejecutar análisis batch para todos los estudiantes"""
    students = Student.objects.all()
    total_alerts = 0
    
    for student in students:
        last_record = student.records.order_by('-date').first()
        if last_record:
            prediction = predict_student_state(student, last_record.date)
            if prediction and prediction.is_stressed:
                total_alerts += 1
    
    # Registrar en historial
    AnalysisHistory.objects.create(
        students_analyzed=students.count(),
        records_processed=AcademicRecord.objects.count(),
        stress_alerts_count=total_alerts,
        details=f"Análisis completado el {datetime.now()}"
    )
    
    messages.success(request, f' Análisis completado. Se generaron {total_alerts} alertas de estrés.')
    return redirect('academic:dashboard')

@login_required
def stress_alerts(request):
    """Vista de alertas de estrés académico"""
    alerts = HMMPrediction.objects.filter(is_stressed=True).select_related('student').order_by('-date')
    return render(request, 'academic/stress_alert.html', {'alerts': alerts})

@login_required
def prediction_list(request):
    """Lista todas las predicciones realizadas"""
    predictions = HMMPrediction.objects.select_related('student').order_by('-date')
    return render(request, 'academic/prediction_list.html', {'predictions': predictions})
    # academic/views.py - Agregar al final

@login_required
def all_records(request):
    """
    Vista para mostrar todos los registros académicos con filtros
    """
    # Obtener todos los registros con relaciones
    records = AcademicRecord.objects.select_related('student').all().order_by('-date')
    
    # Filtrar por estudiante si se proporciona
    student_id = request.GET.get('student')
    if student_id:
        records = records.filter(student_id=student_id)
    
    # Filtrar por fecha desde
    date_from = request.GET.get('date_from')
    if date_from:
        records = records.filter(date__gte=date_from)
    
    # Filtrar por fecha hasta
    date_to = request.GET.get('date_to')
    if date_to:
        records = records.filter(date__lte=date_to)
    
    # Filtrar por estado (si existe predicción)
    state = request.GET.get('state')
    if state:
        records = records.filter(predictions__hidden_state=state)
    
    # Obtener lista de estudiantes para el filtro
    students = Student.objects.all()
    
    # Estadísticas
    total_records = records.count()
    avg_study_hours = records.aggregate(Avg('study_hours'))['study_hours__avg'] or 0
    avg_attendance = records.aggregate(Avg('attendance'))['attendance__avg'] or 0
    
    context = {
        'records': records,
        'students': students,
        'total_records': total_records,
        'avg_study_hours': round(avg_study_hours, 1),
        'avg_attendance': round(avg_attendance, 1),
        'selected_student': student_id,
        'selected_date_from': date_from,
        'selected_date_to': date_to,
        'selected_state': state,
    }
    return render(request, 'academic/all_records.html', context)


@login_required
def record_detail(request, pk):
    """
    Vista para ver el detalle de un registro específico
    """
    record = get_object_or_404(AcademicRecord.objects.select_related('student'), pk=pk)
    
    # Obtener la predicción asociada si existe
    prediction = HMMPrediction.objects.filter(student=record.student, date=record.date).first()
    
    context = {
        'record': record,
        'prediction': prediction,
    }
    return render(request, 'academic/record_detail.html', context)


@login_required
def record_delete(request, pk):
    """
    Eliminar un registro académico
    """
    record = get_object_or_404(AcademicRecord, pk=pk)
    student_name = record.student.name
    record_date = record.date
    
    if request.method == 'POST':
        record.delete()
        messages.success(request, f' Registro del {record_date} para {student_name} eliminado.')
        return redirect('academic:all_records')
    
    return render(request, 'academic/record_confirm_delete.html', {
        'record': record,
        'student_name': student_name,
        'record_date': record_date
    })