# academic/tests.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Student, AcademicRecord, HMMPrediction
from .hmm_model import AcademicStressHMM, prepare_observations_from_records
import numpy as np
from datetime import date, timedelta

class ModelTests(TestCase):
    """Pruebas para los modelos"""
    
    def setUp(self):
        self.student = Student.objects.create(
            name="Juan Pérez",
            email="juan@test.com"
        )
    
    def test_student_creation(self):
        """Prueba creación de estudiante"""
        self.assertEqual(self.student.name, "Juan Pérez")
        self.assertEqual(str(self.student), "Juan Pérez")
        self.assertEqual(Student.objects.count(), 1)
    
    def test_academic_record_creation(self):
        """Prueba creación de registro académico"""
        record = AcademicRecord.objects.create(
            student=self.student,
            date=date.today(),
            study_hours=5,
            tasks_delivered=3,
            attendance=85,
            sleep_hours=7,
            delivery_delays=0,
            academic_activity_time=6
        )
        self.assertEqual(record.study_hours, 5)
        self.assertEqual(record.student.name, "Juan Pérez")
    
    def test_prediction_creation(self):
        """Prueba creación de predicción"""
        prediction = HMMPrediction.objects.create(
            student=self.student,
            date=date.today(),
            hidden_state='motivado',
            probability=0.85,
            is_stressed=False
        )
        self.assertEqual(prediction.hidden_state, 'motivado')
        self.assertFalse(prediction.is_stressed)

class HMMTests(TestCase):
    """Pruebas para el modelo HMM"""
    
    def setUp(self):
        self.hmm = AcademicStressHMM()
    
    def test_hmm_initialization(self):
        """Prueba inicialización del HMM"""
        self.assertIsNotNone(self.hmm)
        self.assertEqual(self.hmm.n_states, 4)
    
    def test_hmm_prediction(self):
        """Prueba predicción del HMM"""
        observations = np.array([[5, 3, 85, 7, 0, 6]])
        states, probs = self.hmm.predict(observations)
        self.assertEqual(len(states), 1)
        self.assertIn(states[0], [0, 1, 2, 3])
    
    def test_state_names(self):
        """Prueba nombres de estados"""
        self.assertEqual(self.hmm.get_state_name(0), "Motivado")
        self.assertEqual(self.hmm.get_state_name(1), "Cansado")
        self.assertEqual(self.hmm.get_state_name(2), "Estresado")
        self.assertEqual(self.hmm.get_state_name(3), "Desmotivado")
    
    def test_stress_detection(self):
        """Prueba detección de estrés"""
        self.assertFalse(self.hmm.is_stressed(0))
        self.assertFalse(self.hmm.is_stressed(1))
        self.assertTrue(self.hmm.is_stressed(2))
        self.assertFalse(self.hmm.is_stressed(3))

class ViewTests(TestCase):
    """Pruebas para las vistas"""
    
    def setUp(self):
        # Crear usuario para autenticación
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
        
        self.student = Student.objects.create(
            name="Ana García",
            email="ana@test.com"
        )
    
    def test_dashboard_view(self):
        """Prueba vista dashboard"""
        response = self.client.get(reverse('academic:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'academic/dashboard.html')
    
    def test_student_list_view(self):
        """Prueba lista de estudiantes"""
        response = self.client.get(reverse('academic:student_list'))
        self.assertEqual(response.status_code, 200)
        # Verificar que el nombre del estudiante está en la respuesta
        # Usar encode porque la respuesta puede estar en bytes
        content = response.content.decode('utf-8')
        self.assertIn("Ana García", content)
    
    def test_student_create_view(self):
        """Prueba creación de estudiante vía vista"""
        response = self.client.post(reverse('academic:student_create'), {
            'name': 'Carlos López',
            'email': 'carlos@test.com'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertEqual(Student.objects.count(), 2)
    
    def test_student_update_view(self):
        """Prueba actualización de estudiante"""
        response = self.client.post(reverse('academic:student_update', args=[self.student.id]), {
            'name': 'Ana García Actualizada',
            'email': 'ana.actualizada@test.com'
        })
        self.assertEqual(response.status_code, 302)
        self.student.refresh_from_db()
        self.assertEqual(self.student.name, 'Ana García Actualizada')
    
    def test_student_delete_view(self):
        """Prueba eliminación de estudiante"""
        response = self.client.post(reverse('academic:student_delete', args=[self.student.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Student.objects.count(), 0)
    
    def test_stress_alerts_view(self):
        """Prueba vista de alertas"""
        response = self.client.get(reverse('academic:stress_alerts'))
        self.assertEqual(response.status_code, 200)
    
    def test_batch_analysis_view(self):
        """Prueba análisis batch"""
        response = self.client.get(reverse('academic:batch_analysis'))
        self.assertEqual(response.status_code, 302)

class FormTests(TestCase):
    """Pruebas para formularios"""
    
    def test_student_form_valid(self):
        """Prueba formulario estudiante válido"""
        from .forms import StudentForm
        form = StudentForm(data={
            'name': 'María Pérez',
            'email': 'maria@test.com'
        })
        self.assertTrue(form.is_valid())
    
    def test_student_form_invalid(self):
        """Prueba formulario estudiante inválido"""
        from .forms import StudentForm
        form = StudentForm(data={
            'name': '',
            'email': 'invalid-email'
        })
        self.assertFalse(form.is_valid())