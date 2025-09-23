"""
Sistema de Recomendación Inteligente de Técnicos
Para Grinding Perú - Mantenimiento Predictivo
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import json
import logging

logger = logging.getLogger(__name__)

class TechnicianRecommendationSystem:
    """
    Sistema inteligente para recomendar técnicos basado en:
    - Especialidad técnica
    - Carga de trabajo actual
    - Disponibilidad
    - Historial de rendimiento
    - Ubicación geográfica
    - Experiencia con equipos específicos
    """
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        self.scaler = StandardScaler()
        
    def get_technician_recommendations(
        self, 
        incident_data: Dict,
        limit: int = 5
    ) -> List[Dict]:
        """
        Obtiene recomendaciones de técnicos para una incidencia específica
        
        Args:
            incident_data: Datos de la incidencia
            limit: Número máximo de recomendaciones
            
        Returns:
            Lista de técnicos recomendados con scores
        """
        try:
            # 1. Obtener técnicos disponibles
            available_technicians = self._get_available_technicians()
            
            if not available_technicians:
                return []
            
            # 2. Calcular scores para cada técnico
            technician_scores = []
            
            for tech in available_technicians:
                score = self._calculate_technician_score(tech, incident_data)
                technician_scores.append({
                    'technician': tech,
                    'score': score,
                    'reasons': self._get_recommendation_reasons(tech, incident_data)
                })
            
            # 3. Ordenar por score y retornar top N
            technician_scores.sort(key=lambda x: x['score'], reverse=True)
            
            return technician_scores[:limit]
            
        except Exception as e:
            logger.error(f"Error en recomendación de técnicos: {e}")
            return []
    
    def _get_available_technicians(self) -> List[Dict]:
        """Obtiene técnicos disponibles"""
        try:
            # Consulta SQL para obtener técnicos disponibles
            query = """
            SELECT 
                u.id,
                u.name,
                u.email,
                u.specialty,
                u.experience_years,
                u.location,
                u.availability_status,
                u.skill_level,
                u.certifications,
                u.preferred_equipment_types,
                COUNT(i.id) as current_workload
            FROM users u
            LEFT JOIN incidents i ON u.id = i.assigned_technician_id 
                AND i.status IN ('pending', 'in_progress')
            WHERE u.role = 'technician' 
                AND u.availability_status = 'available'
            GROUP BY u.id, u.name, u.email, u.specialty, u.experience_years, 
                     u.location, u.availability_status, u.skill_level, 
                     u.certifications, u.preferred_equipment_types
            ORDER BY current_workload ASC, u.skill_level DESC
            """
            
            # Ejecutar consulta (adaptar según tu ORM/DB)
            technicians = self.db.execute_query(query)
            return technicians
            
        except Exception as e:
            logger.error(f"Error obteniendo técnicos disponibles: {e}")
            return []
    
    def _calculate_technician_score(
        self, 
        technician: Dict, 
        incident_data: Dict
    ) -> float:
        """
        Calcula score de compatibilidad técnico-incidencia
        
        Scoring basado en:
        - Especialidad (40%)
        - Experiencia (25%)
        - Carga de trabajo (20%)
        - Ubicación (10%)
        - Historial de rendimiento (5%)
        """
        try:
            score = 0.0
            
            # 1. Especialidad (40% del score)
            specialty_score = self._calculate_specialty_match(
                technician['specialty'], 
                incident_data.get('equipment_type', ''),
                incident_data.get('failure_type', '')
            )
            score += specialty_score * 0.4
            
            # 2. Experiencia (25% del score)
            experience_score = self._calculate_experience_score(
                technician['experience_years'],
                technician['skill_level'],
                incident_data.get('priority', 'medium')
            )
            score += experience_score * 0.25
            
            # 3. Carga de trabajo (20% del score)
            workload_score = self._calculate_workload_score(
                technician['current_workload']
            )
            score += workload_score * 0.2
            
            # 4. Ubicación (10% del score)
            location_score = self._calculate_location_score(
                technician['location'],
                incident_data.get('location', '')
            )
            score += location_score * 0.1
            
            # 5. Historial de rendimiento (5% del score)
            performance_score = self._calculate_performance_score(technician['id'])
            score += performance_score * 0.05
            
            return min(score, 1.0)  # Normalizar a 0-1
            
        except Exception as e:
            logger.error(f"Error calculando score técnico: {e}")
            return 0.0
    
    def _calculate_specialty_match(
        self, 
        technician_specialty: str, 
        equipment_type: str, 
        failure_type: str
    ) -> float:
        """Calcula compatibilidad de especialidad"""
        try:
            # Mapeo de especialidades a equipos
            specialty_equipment_map = {
                'mecanico': ['motor', 'bomba', 'compresor', 'generador'],
                'electrico': ['motor', 'generador', 'transformador', 'panel'],
                'electronico': ['sensor', 'controlador', 'plc', 'hmi'],
                'hidraulico': ['bomba', 'valvula', 'cilindro', 'actuador'],
                'neumatico': ['compresor', 'valvula', 'cilindro', 'actuador']
            }
            
            # Mapeo de fallas a especialidades
            failure_specialty_map = {
                'mecanica': ['mecanico'],
                'electrica': ['electrico', 'electronico'],
                'hidraulica': ['hidraulico', 'mecanico'],
                'neumatica': ['neumatico', 'mecanico'],
                'vibracion': ['mecanico', 'electrico'],
                'temperatura': ['mecanico', 'electrico']
            }
            
            score = 0.0
            
            # Verificar compatibilidad con tipo de equipo
            if equipment_type.lower() in specialty_equipment_map.get(
                technician_specialty.lower(), []
            ):
                score += 0.5
            
            # Verificar compatibilidad con tipo de falla
            if failure_type.lower() in failure_specialty_map:
                if technician_specialty.lower() in failure_specialty_map[failure_type.lower()]:
                    score += 0.5
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculando match de especialidad: {e}")
            return 0.0
    
    def _calculate_experience_score(
        self, 
        experience_years: int, 
        skill_level: str, 
        priority: str
    ) -> float:
        """Calcula score basado en experiencia"""
        try:
            # Score base por años de experiencia
            years_score = min(experience_years / 10, 1.0)
            
            # Multiplicador por nivel de habilidad
            skill_multiplier = {
                'junior': 0.6,
                'intermediate': 0.8,
                'senior': 1.0,
                'expert': 1.2
            }.get(skill_level.lower(), 0.8)
            
            # Ajuste por prioridad
            priority_multiplier = {
                'low': 0.8,
                'medium': 1.0,
                'high': 1.2,
                'critical': 1.4
            }.get(priority.lower(), 1.0)
            
            return years_score * skill_multiplier * priority_multiplier
            
        except Exception as e:
            logger.error(f"Error calculando score de experiencia: {e}")
            return 0.0
    
    def _calculate_workload_score(self, current_workload: int) -> float:
        """Calcula score basado en carga de trabajo"""
        try:
            # Score inverso: menos carga = mayor score
            if current_workload == 0:
                return 1.0
            elif current_workload <= 2:
                return 0.8
            elif current_workload <= 4:
                return 0.6
            else:
                return 0.4
                
        except Exception as e:
            logger.error(f"Error calculando score de carga: {e}")
            return 0.5
    
    def _calculate_location_score(self, tech_location: str, incident_location: str) -> float:
        """Calcula score basado en proximidad geográfica"""
        try:
            if not tech_location or not incident_location:
                return 0.5
            
            # Lógica simple de proximidad (implementar geocoding real)
            if tech_location.lower() == incident_location.lower():
                return 1.0
            elif any(word in tech_location.lower() for word in incident_location.lower().split()):
                return 0.8
            else:
                return 0.6
                
        except Exception as e:
            logger.error(f"Error calculando score de ubicación: {e}")
            return 0.5
    
    def _calculate_performance_score(self, technician_id: int) -> float:
        """Calcula score basado en historial de rendimiento"""
        try:
            # Consulta para obtener métricas de rendimiento
            query = """
            SELECT 
                AVG(CASE WHEN i.status = 'completed' THEN 1 ELSE 0 END) as completion_rate,
                AVG(EXTRACT(EPOCH FROM (i.resolved_at - i.created_at))/3600) as avg_resolution_time,
                COUNT(CASE WHEN i.priority = 'critical' AND i.status = 'completed' THEN 1 END) as critical_resolved
            FROM incidents i
            WHERE i.assigned_technician_id = %s
                AND i.created_at >= NOW() - INTERVAL '6 months'
            """
            
            result = self.db.execute_query(query, (technician_id,))
            
            if not result:
                return 0.5
            
            completion_rate = result[0]['completion_rate'] or 0
            avg_time = result[0]['avg_resolution_time'] or 24
            critical_resolved = result[0]['critical_resolved'] or 0
            
            # Score basado en tasa de completación
            completion_score = completion_rate
            
            # Score basado en tiempo promedio (menos tiempo = mejor score)
            time_score = max(0, 1 - (avg_time / 48))  # Normalizar a 48 horas
            
            # Score basado en resolución de críticos
            critical_score = min(critical_resolved / 5, 1.0)  # Normalizar a 5 críticos
            
            return (completion_score * 0.5 + time_score * 0.3 + critical_score * 0.2)
            
        except Exception as e:
            logger.error(f"Error calculando score de rendimiento: {e}")
            return 0.5
    
    def _get_recommendation_reasons(
        self, 
        technician: Dict, 
        incident_data: Dict
    ) -> List[str]:
        """Genera razones para la recomendación"""
        reasons = []
        
        try:
            # Razón por especialidad
            if technician['specialty'].lower() in ['mecanico', 'electrico']:
                reasons.append(f"Especialidad en {technician['specialty']} ideal para este tipo de falla")
            
            # Razón por experiencia
            if technician['experience_years'] >= 5:
                reasons.append(f"Experiencia sólida de {technician['experience_years']} años")
            
            # Razón por disponibilidad
            if technician['current_workload'] <= 2:
                reasons.append("Disponibilidad inmediata")
            
            # Razón por ubicación
            if technician['location'] and incident_data.get('location'):
                if technician['location'].lower() == incident_data['location'].lower():
                    reasons.append("Ubicación cercana al incidente")
            
            # Razón por certificaciones
            if technician.get('certifications'):
                reasons.append("Certificaciones técnicas relevantes")
            
            return reasons[:3]  # Máximo 3 razones
            
        except Exception as e:
            logger.error(f"Error generando razones: {e}")
            return ["Técnico calificado disponible"]
    
    def get_team_recommendations(
        self, 
        incident_data: Dict,
        team_size: int = 3
    ) -> List[Dict]:
        """
        Recomienda un equipo de técnicos para incidencias complejas
        
        Args:
            incident_data: Datos de la incidencia
            team_size: Tamaño del equipo recomendado
            
        Returns:
            Lista de equipos recomendados
        """
        try:
            # Obtener recomendaciones individuales
            individual_recommendations = self.get_technician_recommendations(
                incident_data, 
                limit=team_size * 2
            )
            
            if len(individual_recommendations) < team_size:
                return individual_recommendations
            
            # Combinar técnicos para formar equipos
            teams = []
            
            # Estrategia: Combinar especialidades complementarias
            specialties_needed = self._get_required_specialties(incident_data)
            
            for i in range(len(individual_recommendations) - team_size + 1):
                team = individual_recommendations[i:i + team_size]
                
                # Verificar diversidad de especialidades
                team_specialties = [t['technician']['specialty'] for t in team]
                diversity_score = len(set(team_specialties)) / len(team_specialties)
                
                # Calcular score promedio del equipo
                avg_score = sum(t['score'] for t in team) / len(team)
                
                teams.append({
                    'team': team,
                    'diversity_score': diversity_score,
                    'avg_score': avg_score,
                    'total_score': avg_score * diversity_score
                })
            
            # Ordenar por score total
            teams.sort(key=lambda x: x['total_score'], reverse=True)
            
            return teams[:3]  # Top 3 equipos
            
        except Exception as e:
            logger.error(f"Error en recomendación de equipos: {e}")
            return []
    
    def _get_required_specialties(self, incident_data: Dict) -> List[str]:
        """Determina especialidades requeridas para la incidencia"""
        equipment_type = incident_data.get('equipment_type', '').lower()
        failure_type = incident_data.get('failure_type', '').lower()
        
        specialties = []
        
        # Lógica para determinar especialidades necesarias
        if 'motor' in equipment_type or 'bomba' in equipment_type:
            specialties.extend(['mecanico', 'electrico'])
        
        if 'sensor' in equipment_type or 'controlador' in equipment_type:
            specialties.append('electronico')
        
        if 'hidraulico' in failure_type:
            specialties.append('hidraulico')
        
        if 'neumatico' in failure_type:
            specialties.append('neumatico')
        
        return list(set(specialties))  # Eliminar duplicados
