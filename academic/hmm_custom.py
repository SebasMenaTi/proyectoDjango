# apps/academic/hmm_custom.py

import numpy as np

class CustomHMM:
    """
    Implementación personalizada de Hidden Markov Model
    usando el algoritmo de Viterbi.
    
    Estados ocultos:
        0: Motivado
        1: Cansado  
        2: Estresado
        3: Desmotivado
    """
    
    def __init__(self, n_states=4, n_observations=6):
        self.n_states = n_states
        self.n_observations = n_observations
        
        # Probabilidades iniciales (π)
        self.startprob = np.array([0.7, 0.1, 0.1, 0.1])
        
        # Matriz de transición (A) - basada en investigación académica
        self.transmat = np.array([
            [0.6, 0.2, 0.1, 0.1],  # Motivado -> 
            [0.1, 0.5, 0.3, 0.1],  # Cansado ->
            [0.05, 0.15, 0.6, 0.2], # Estresado ->
            [0.1, 0.1, 0.2, 0.6]    # Desmotivado ->
        ])
        
        # Medias para emisiones gaussianas por estado
        self.means = np.array([
            [6, 4, 90, 7, 0, 8],    # Motivado: estudio, tareas, asistencia, sueño, retrasos, actividad
            [3, 2, 65, 5, 2, 5],    # Cansado
            [2, 1, 50, 4, 5, 4],    # Estresado
            [1, 0, 40, 6, 3, 3]     # Desmotivado
        ])
        
        # Varianzas (diagonales de covarianza)
        self.variances = np.array([
            [1, 0.5, 5, 0.5, 0.2, 1],
            [0.8, 0.3, 8, 0.5, 0.5, 0.8],
            [0.5, 0.2, 10, 0.3, 1, 0.5],
            [0.7, 0.1, 12, 0.8, 0.8, 0.7]
        ])
        
        self.state_names = {
            0: "Motivado",
            1: "Cansado",
            2: "Estresado",
            3: "Desmotivado"
        }
    
    def _gaussian_probability(self, observation, mean, variance):
        """
        Calcula la probabilidad de una observación bajo distribución Gaussiana
        """
        d = len(observation)
        prob = 1.0
        
        for i in range(d):
            # Añadir pequeño valor para evitar división por cero
            var = max(variance[i], 0.001)
            exponent = -((observation[i] - mean[i]) ** 2) / (2 * var)
            coefficient = 1.0 / np.sqrt(2 * np.pi * var)
            prob *= coefficient * np.exp(exponent)
        
        return max(prob, 1e-10)  # Evitar probabilidades cero
    
    def _compute_emission_matrix(self, observations):
        """
        Calcula la matriz de probabilidades de emisión B
        """
        n_samples = len(observations)
        emission_probs = np.zeros((n_samples, self.n_states))
        
        for t in range(n_samples):
            for s in range(self.n_states):
                emission_probs[t, s] = self._gaussian_probability(
                    observations[t], 
                    self.means[s], 
                    self.variances[s]
                )
        
        return emission_probs
    
    def viterbi(self, observations):
        """
        Algoritmo de Viterbi para encontrar la secuencia de estados más probable
        """
        if len(observations) == 0:
            return np.array([]), np.array([])
        
        # Calcular probabilidades de emisión
        B = self._compute_emission_matrix(observations)
        T = len(observations)
        N = self.n_states
        
        # Inicialización
        delta = np.zeros((T, N))
        psi = np.zeros((T, N), dtype=int)
        
        # Primer paso
        for j in range(N):
            delta[0, j] = np.log(self.startprob[j]) + np.log(B[0, j])
        
        # Recursión
        for t in range(1, T):
            for j in range(N):
                max_prob = -np.inf
                max_state = 0
                
                for i in range(N):
                    prob = delta[t-1, i] + np.log(self.transmat[i, j]) + np.log(B[t, j])
                    if prob > max_prob:
                        max_prob = prob
                        max_state = i
                
                delta[t, j] = max_prob
                psi[t, j] = max_state
        
        # Terminación
        states = np.zeros(T, dtype=int)
        states[-1] = np.argmax(delta[-1])
        
        # Backtracking
        for t in range(T-2, -1, -1):
            states[t] = psi[t+1, states[t+1]]
        
        # Calcular probabilidades posteriores
        posteriors = np.exp(delta - np.max(delta, axis=1, keepdims=True))
        posteriors = posteriors / posteriors.sum(axis=1, keepdims=True)
        
        return states, posteriors
    
    def predict(self, observations):
        """
        Predice los estados ocultos para una secuencia de observaciones
        """
        observations = np.array(observations)
        
        # Asegurar formato correcto
        if observations.ndim == 1:
            observations = observations.reshape(1, -1)
        
        # Normalizar observaciones
        normalized_obs = self._normalize_observations(observations)
        
        # Aplicar Viterbi
        states, posteriors = self.viterbi(normalized_obs)
        
        return states, posteriors
    
    def _normalize_observations(self, observations):
        """
        Normaliza las observaciones a rangos comparables
        """
        normalized = observations.copy()
        
        # Definir rangos máximos para cada característica
        max_ranges = [24, 10, 100, 24, 10, 24]
        
        for i in range(observations.shape[1]):
            if i < len(max_ranges):
                normalized[:, i] = observations[:, i] / max_ranges[i]
        
        return normalized
    
    def get_state_name(self, state_id):
        """Retorna el nombre del estado"""
        return self.state_names.get(state_id, "Desconocido")
    
    def is_stressed(self, state_id):
        """Determina si el estado indica estrés académico"""
        return state_id == 2  # Estado estresado
    
    def fit(self, observations_sequences):
        """
        Método simple de entrenamiento - actualiza medias basado en datos
        """
        all_obs = np.concatenate(observations_sequences)
        states, _ = self.predict(all_obs)
        
        # Actualizar medias por estado
        for s in range(self.n_states):
            mask = states == s
            if np.any(mask):
                self.means[s] = np.mean(all_obs[mask], axis=0)
                self.variances[s] = np.var(all_obs[mask], axis=0) + 0.1
        
        return self