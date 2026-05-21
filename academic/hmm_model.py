# academic/hmm_model.py

import numpy as np
from .hmm_custom import CustomHMM
import joblib

class AcademicStressHMM:
    """
    Modelo Oculto de Markov personalizado para detección de estrés académico.
    Usa implementación propia sin hmmlearn.
    """
    
    def __init__(self, n_states=4, n_observations=6):
        self.n_states = n_states
        self.n_observations = n_observations
        self.model = CustomHMM(n_states, n_observations)
        
        # Mapeo de estados
        self.state_names = {
            0: "Motivado",
            1: "Cansado", 
            2: "Estresado",
            3: "Desmotivado"
        }
        
    def initialize_model(self):
        """Inicializa el modelo HMM personalizado"""
        if self.model is None:
            self.model = CustomHMM(self.n_states, self.n_observations)
        
    def train(self, observations_sequences):
        """
        Entrena el modelo con secuencias de observaciones.
        """
        if self.model is None:
            self.initialize_model()
            
        if len(observations_sequences) > 0:
            self.model.fit(observations_sequences)
        return self.model
    
    def predict(self, observation_sequence):
        """
        Predice los estados ocultos para una secuencia de observaciones.
        """
        if self.model is None:
            self.initialize_model()
            
        if len(observation_sequence) == 0:
            return np.array([]), np.array([])
        
        X = np.array(observation_sequence)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        states, posteriors = self.model.predict(X)
        return states, posteriors
    
    def get_state_name(self, state_id):
        """Retorna el nombre del estado dado su ID"""
        return self.state_names.get(state_id, "Desconocido")
    
    def is_stressed(self, state_id):
        """Determina si el estado implica estrés académico"""
        return state_id == 2  # Estado 2 = Estresado


def prepare_observations_from_records(academic_records):
    """
    Convierte registros académicos de Django en array numpy para HMM.
    
    Args:
        academic_records: QuerySet de AcademicRecord objects
        
    Returns:
        numpy array con las observaciones
    """
    observations = []
    for record in academic_records:
        obs = [
            float(record.study_hours),
            float(record.tasks_delivered),
            float(record.attendance),
            float(record.sleep_hours),
            float(record.delivery_delays),
            float(record.academic_activity_time)
        ]
        observations.append(obs)
    
    if len(observations) == 0:
        return np.array([])
    
    return np.array(observations)