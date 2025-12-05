from django.utils import timezone
from datetime import date, timedelta

class AlgoritmoPrioridad:
    """
    Algoritmo de Priorización Inteligente de Proyectos
    Calcula un score de 0-100 basándose en múltiples criterios
    """
    
    # Pesos de cada criterio (deben sumar 1.0)
    PESO_URGENCIA_TIEMPO = 0.30      # 30%
    PESO_DESVIACION_PRESUPUESTO = 0.25  # 25%
    PESO_RIESGO = 0.20               # 20%
    PESO_AVANCE = 0.15               # 15%
    PESO_RECURSOS = 0.10             # 10%
    
    @staticmethod
    def calcular_prioridad(proyecto):
        """
        Calcula la prioridad de un proyecto
        Returns: dict con score, nivel y detalles
        """
        scores = {
            'urgencia_tiempo': AlgoritmoPrioridad._calcular_urgencia_tiempo(proyecto),
            'desviacion_presupuesto': AlgoritmoPrioridad._calcular_desviacion_presupuesto(proyecto),
            'riesgo': AlgoritmoPrioridad._calcular_riesgo(proyecto),
            'avance': AlgoritmoPrioridad._calcular_avance(proyecto),
            'recursos': AlgoritmoPrioridad._calcular_recursos(proyecto),
        }
        
        # Calcular score total ponderado
        score_total = (
            scores['urgencia_tiempo'] * AlgoritmoPrioridad.PESO_URGENCIA_TIEMPO +
            scores['desviacion_presupuesto'] * AlgoritmoPrioridad.PESO_DESVIACION_PRESUPUESTO +
            scores['riesgo'] * AlgoritmoPrioridad.PESO_RIESGO +
            scores['avance'] * AlgoritmoPrioridad.PESO_AVANCE +
            scores['recursos'] * AlgoritmoPrioridad.PESO_RECURSOS
        )
        
        # Determinar nivel de prioridad
        nivel = AlgoritmoPrioridad._determinar_nivel(score_total)
        
        return {
            'score': round(score_total, 2),
            'nivel': nivel,
            'detalles': scores
        }
    
    @staticmethod
    def _calcular_urgencia_tiempo(proyecto):
        """
        Calcula urgencia basándose en días restantes
        Score: 0-100 (más alto = más urgente)
        """
        hoy = date.today()
        dias_restantes = (proyecto.fecha_final - hoy).days
        
        if dias_restantes < 0:
            return 100  # Proyecto vencido = máxima urgencia
        elif dias_restantes <= 7:
            return 90   # Menos de 1 semana
        elif dias_restantes <= 30:
            return 70   # Menos de 1 mes
        elif dias_restantes <= 90:
            return 50   # Menos de 3 meses
        else:
            return 20   # Más de 3 meses
    
    @staticmethod
    def _calcular_desviacion_presupuesto(proyecto):
        """
        Calcula desviación del presupuesto
        Score: 0-100 (más alto = mayor desviación)
        """
        if proyecto.presupuesto == 0:
            return 0
        
        desviacion = ((proyecto.costo_final - proyecto.presupuesto) / proyecto.presupuesto) * 100
        
        if desviacion >= 50:
            return 100  # Sobrecosto de 50% o más
        elif desviacion >= 25:
            return 80   # Sobrecosto de 25-50%
        elif desviacion >= 10:
            return 60   # Sobrecosto de 10-25%
        elif desviacion >= 0:
            return 30   # Dentro del presupuesto o ligero sobrecosto
        else:
            return 10   # Bajo presupuesto
    
    @staticmethod
    def _calcular_riesgo(proyecto):
        """
        Calcula score basado en riesgos del proyecto
        Score: 0-100 (más alto = mayor riesgo)
        """
        riesgos = proyecto.riesgos.all()
        
        if not riesgos.exists():
            return 0  # Sin riesgos registrados
        
        # Promedio de porcentajes de riesgo
        promedio_riesgo = sum(r.porcentaje_riesgo for r in riesgos) / len(riesgos)
        
        return min(promedio_riesgo, 100)  # Máximo 100
    
    @staticmethod
    def _calcular_avance(proyecto):
        """
        Calcula score basado en avance vs tiempo transcurrido
        Score: 0-100 (más alto = mayor atraso)
        """
        hoy = date.today()
    
    # Calcular duración total
        duracion_total = (proyecto.fecha_final - proyecto.fecha_inicio).days
        if duracion_total <= 0:
            return 20
    
        tiempo_transcurrido = (hoy - proyecto.fecha_inicio).days
        porcentaje_tiempo = (tiempo_transcurrido / duracion_total) * 100
    
    # VALIDACIÓN: Si el proyecto aún no ha iniciado
        if porcentaje_tiempo <= 0:
            return 20  # Consideramos "en tiempo" porque aún no debería tener avance
    
    # Comparar con avance real (solo para proyectos que ya iniciaron)
        diferencia = porcentaje_tiempo - proyecto.porcentaje
    
        if diferencia >= 30:
            return 100  # Muy atrasado
        elif diferencia >= 15:
            return 70   # Atrasado
        elif diferencia >= 5:
            return 40   # Ligeramente atrasado
        elif diferencia >= -10:
            return 20   # En tiempo
        else:
            return 10   # Adelantado
    
    @staticmethod
    def _calcular_recursos(proyecto):
        """
        Calcula score basado en cantidad de recursos humanos
        Score: 0-100 (más alto = más recursos asignados = más crítico)
        """
        cantidad_recursos = proyecto.recursos_humanos.count()
        
        if cantidad_recursos == 0:
            return 0
        elif cantidad_recursos >= 10:
            return 80   # Muchos recursos involucrados
        elif cantidad_recursos >= 5:
            return 60   # Varios recursos
        elif cantidad_recursos >= 3:
            return 40   # Recursos moderados
        else:
            return 20   # Pocos recursos
    
    @staticmethod
    def _determinar_nivel(score):
        """
        Determina el nivel de prioridad basándose en el score
        """
        if score >= 75:
            return 'Crítica'
        elif score >= 50:
            return 'Alta'
        elif score >= 25:
            return 'Media'
        else:
            return 'Baja'

def actualizar_prioridad_proyecto(proyecto):
    """
    Actualiza la prioridad de un proyecto específico
    """ 
    resultado = AlgoritmoPrioridad.calcular_prioridad(proyecto)
    
    proyecto.prioridad_score = resultado['score']
    proyecto.prioridad_nivel = resultado['nivel']
    proyecto.ultima_actualizacion_prioridad = timezone.now()
    proyecto.save()
    
    return resultado


def actualizar_todas_las_prioridades():
    """
    Actualiza la prioridad de todos los proyectos activos
    """
    from .models import Proyecto
    
    proyectos = Proyecto.objects.exclude(estado__iexact='finalizado')
    resultados = []
    
    for proyecto in proyectos:
        resultado = actualizar_prioridad_proyecto(proyecto)
        resultados.append({
            'proyecto': proyecto.nombre_proyecto,
            'score': resultado['score'],
            'nivel': resultado['nivel']
        })
    
    return resultados


def obtener_proyectos_priorizados(limite=None):
    """
    Obtiene proyectos ordenados por prioridad
    """
    from .models import Proyecto
    
    proyectos = Proyecto.objects.exclude(estado__iexact='finalizado').order_by('-prioridad_score')
    
    if limite:
        proyectos = proyectos[:limite]
    
    return proyectos