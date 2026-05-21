# apps/academic/models.py

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Student(models.Model):
    """
    Modelo para representar a un estudiante.
    """
    name = models.CharField(max_length=100, verbose_name="Nombre completo")
    email = models.EmailField(unique=True, verbose_name="Correo electrónico")
    enrollment_date = models.DateField(auto_now_add=True, verbose_name="Fecha de registro")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"


class AcademicRecord(models.Model):
    """
    Registro académico diario/semanal de un estudiante.
    Estos datos serán las observaciones para el HMM.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="records")
    date = models.DateField(verbose_name="Fecha del registro")

    # Observaciones visibles
    study_hours = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(24)],
        verbose_name="Horas de estudio"
    )
    tasks_delivered = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="Tareas entregadas"
    )
    attendance = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Asistencia (%)"
    )
    sleep_hours = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(24)],
        verbose_name="Horas de sueño"
    )
    delivery_delays = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="Retrasos en entregas"
    )
    academic_activity_time = models.FloatField(
        validators=[MinValueValidator(0)],
        verbose_name="Tiempo de actividad académica (horas)"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date']
        verbose_name = "Registro académico"
        verbose_name_plural = "Registros académicos"
    def get_prediction(self):
        """Obtener la predicción asociada a este registro"""
        return self.student.predictions.filter(date=self.date).first()
    def __str__(self):
        return f"{self.student.name} - {self.date}"


class HMMPrediction(models.Model):
    """
    Almacena el resultado de la predicción del HMM para un estudiante en una fecha específica.
    """
    ESTADO_CHOICES = [
        ('motivado', 'Motivado'),
        ('cansado', 'Cansado'),
        ('estresado', 'Estresado'),
        ('desmotivado', 'Desmotivado'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="predictions")
    date = models.DateField(verbose_name="Fecha de predicción")
    hidden_state = models.CharField(max_length=20, choices=ESTADO_CHOICES, verbose_name="Estado oculto")
    probability = models.FloatField(verbose_name="Probabilidad asociada")
    is_stressed = models.BooleanField(default=False, verbose_name="Alerta de estrés")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = "Predicción HMM"
        verbose_name_plural = "Predicciones HMM"

    def __str__(self):
        return f"{self.student.name} - {self.date}: {self.get_hidden_state_display()}"


class AnalysisHistory(models.Model):
    """
    Historial de análisis ejecutados por el HMM.
    """
    execution_date = models.DateTimeField(auto_now_add=True)
    students_analyzed = models.IntegerField()
    records_processed = models.IntegerField()
    stress_alerts_count = models.IntegerField()
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Análisis del {self.execution_date.strftime('%Y-%m-%d %H:%M')}"