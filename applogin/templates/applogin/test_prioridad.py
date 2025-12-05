import pytest
from datetime import date, timedelta
from applogin.models import Proyecto, Usuario, Rol, Riesgo, RecursoHumano
from applogin.prioridad import AlgoritmoPrioridad

@pytest.mark.django_db
class TestAlgoritmoPrioridad:
    """
    Pruebas de caja blanca para el Algoritmo de Priorización
    """
    
    @pytest.fixture
    def rol_admin(self):
        """Fixture para crear un rol de administrador"""
        return Rol.objects.create(
            nombre_rol='Administrador',
            descripcion_rol='Rol de prueba'
        )
    
    @pytest.fixture
    def usuario_admin(self, rol_admin):
        """Fixture para crear un usuario administrador"""
        return Usuario.objects.create(
            rol=rol_admin,
            correo='admin@test.com',
            nombre_usuario='admin_test',
            contrasena='test123'
        )
    
    @pytest.fixture
    def proyecto_base(self, usuario_admin):
        """Fixture para crear un proyecto base de prueba"""
        return Proyecto.objects.create(
            nombre_proyecto='Proyecto Test',
            admin_proyecto_usuario=usuario_admin,
            estado='En Progreso',
            porcentaje=50.0,
            fecha_inicio=date.today() - timedelta(days=30),
            fecha_final=date.today() + timedelta(days=30),
            presupuesto=100000.0,
            costo_final=100000.0,
            descripcion='Proyecto de prueba'
        )
    
    # ==================== PRUEBA 1: calcular_urgencia_tiempo ====================
    
    def test_urgencia_proyecto_vencido(self, proyecto_base):
        """
        Prueba de caja blanca: Camino 1 - Proyecto vencido
        Verifica que un proyecto con fecha límite pasada retorne 100 puntos
        """
        proyecto_base.fecha_final = date.today() - timedelta(days=5)
        proyecto_base.save()
        
        score = AlgoritmoPrioridad._calcular_urgencia_tiempo(proyecto_base)
        
        assert score == 100, "Proyecto vencido debe tener urgencia de 100"
    
    def test_urgencia_menos_semana(self, proyecto_base):
        """
        Prueba de caja blanca: Camino 2 - Menos de 1 semana
        Verifica el camino cuando quedan 5 días
        """
        proyecto_base.fecha_final = date.today() + timedelta(days=5)
        proyecto_base.save()
        
        score = AlgoritmoPrioridad._calcular_urgencia_tiempo(proyecto_base)
        
        assert score == 90, "Proyecto con menos de 1 semana debe tener urgencia de 90"
    
    def test_urgencia_menos_mes(self, proyecto_base):
        """
        Prueba de caja blanca: Camino 3 - Menos de 1 mes
        Verifica el camino cuando quedan 20 días
        """
        proyecto_base.fecha_final = date.today() + timedelta(days=20)
        proyecto_base.save()
        
        score = AlgoritmoPrioridad._calcular_urgencia_tiempo(proyecto_base)
        
        assert score == 70, "Proyecto con menos de 1 mes debe tener urgencia de 70"
    
    def test_urgencia_menos_tres_meses(self, proyecto_base):
        """
        Prueba de caja blanca: Camino 4 - Menos de 3 meses
        Verifica el camino cuando quedan 60 días
        """
        proyecto_base.fecha_final = date.today() + timedelta(days=60)
        proyecto_base.save()
        
        score = AlgoritmoPrioridad._calcular_urgencia_tiempo(proyecto_base)
        
        assert score == 50, "Proyecto con menos de 3 meses debe tener urgencia de 50"
    
    def test_urgencia_mas_tres_meses(self, proyecto_base):
        """
        Prueba de caja blanca: Camino 5 - Más de 3 meses
        Verifica el camino cuando quedan 120 días
        """
        proyecto_base.fecha_final = date.today() + timedelta(days=120)
        proyecto_base.save()
        
        score = AlgoritmoPrioridad._calcular_urgencia_tiempo(proyecto_base)
        
        assert score == 20, "Proyecto con más de 3 meses debe tener urgencia de 20"
    
    # ==================== PRUEBA 2: calcular_desviacion_presupuesto ====================
    
    def test_desviacion_presupuesto_cero(self, proyecto_base):
        """
        Prueba de caja blanca: Presupuesto en cero
        Verifica el camino cuando el presupuesto es 0
        """
        proyecto_base.presupuesto = 0
        proyecto_base.save()
        
        score = AlgoritmoPrioridad._calcular_desviacion_presupuesto(proyecto_base)
        
        assert score == 0, "Presupuesto en 0 debe retornar 0"
    
    def test_desviacion_sobrecosto_50_mas(self, proyecto_base):
        """
        Prueba de caja blanca: Camino 1 - Sobrecosto >= 50%
        """
        proyecto_base.presupuesto = 100000
        proyecto_base.costo_final = 200000  # 100% de sobrecosto
        proyecto_base.save()
        
        score = AlgoritmoPrioridad._calcular_desviacion_presupuesto(proyecto_base)
        
        assert score == 100, "Sobrecosto >= 50% debe retornar 100"
    
    def test_desviacion_sobrecosto_25_50(self, proyecto_base):
        """
        Prueba de caja blanca: Camino 2 - Sobrecosto entre 25-50%
        """
        proyecto_base.presupuesto = 100000
        proyecto_base.costo_final = 135000  # 35% de sobrecosto
        proyecto_base.save()
        
        score = AlgoritmoPrioridad._calcular_desviacion_presupuesto(proyecto_base)
        
        assert score == 80, "Sobrecosto 25-50% debe retornar 80"
    
    def test_desviacion_sobrecosto_10_25(self, proyecto_base):
        """
        Prueba de caja blanca: Camino 3 - Sobrecosto entre 10-25%
        """
        proyecto_base.presupuesto = 100000
        proyecto_base.costo_final = 115000  # 15% de sobrecosto
        proyecto_base.save()
        
        score = AlgoritmoPrioridad._calcular_desviacion_presupuesto(proyecto_base)
        
        assert score == 60, "Sobrecosto 10-25% debe retornar 60"
    
    def test_desviacion_dentro_presupuesto(self, proyecto_base):
        """
        Prueba de caja blanca: Camino 4 - Dentro del presupuesto
        """
        proyecto_base.presupuesto = 100000
        proyecto_base.costo_final = 105000  # 5% de sobrecosto
        proyecto_base.save()
        
        score = AlgoritmoPrioridad._calcular_desviacion_presupuesto(proyecto_base)
        
        assert score == 30, "Dentro del presupuesto debe retornar 30"
    
    def test_desviacion_bajo_presupuesto(self, proyecto_base):
        """
        Prueba de caja blanca: Camino 5 - Bajo presupuesto
        """
        proyecto_base.presupuesto = 100000
        proyecto_base.costo_final = 80000  # -20% (bajo presupuesto)
        proyecto_base.save()
        
        score = AlgoritmoPrioridad._calcular_desviacion_presupuesto(proyecto_base)
        
        assert score == 10, "Bajo presupuesto debe retornar 10"
    
    # ==================== PRUEBA 3: calcular_riesgo ====================
    
    def test_riesgo_sin_riesgos(self, proyecto_base):
        """
        Prueba de caja blanca: Camino 1 - Sin riesgos registrados
        """
        score = AlgoritmoPrioridad._calcular_riesgo(proyecto_base)
        
        assert score == 0, "Sin riesgos debe retornar 0"
    
    def test_riesgo_con_un_riesgo(self, proyecto_base):
        """
        Prueba de caja blanca: Camino 2 - Con un riesgo
        """
        Riesgo.objects.create(
            proyecto=proyecto_base,
            porcentaje_riesgo=75.0,
            descripcion_riesgo='Riesgo de prueba',
            plan_mitigacion_riesgo='Plan de prueba'
        )
        
        score = AlgoritmoPrioridad._calcular_riesgo(proyecto_base)
        
        assert score == 75.0, "Con un riesgo del 75% debe retornar 75"
    
    def test_riesgo_con_varios_riesgos(self, proyecto_base):
        """
        Prueba de caja blanca: Camino 3 - Con múltiples riesgos (promedio)
        """
        Riesgo.objects.create(
            proyecto=proyecto_base,
            porcentaje_riesgo=60.0,
            descripcion_riesgo='Riesgo 1',
            plan_mitigacion_riesgo='Plan 1'
        )
        Riesgo.objects.create(
            proyecto=proyecto_base,
            porcentaje_riesgo=80.0,
            descripcion_riesgo='Riesgo 2',
            plan_mitigacion_riesgo='Plan 2'
        )
        Riesgo.objects.create(
            proyecto=proyecto_base,
            porcentaje_riesgo=90.0,
            descripcion_riesgo='Riesgo 3',
            plan_mitigacion_riesgo='Plan 3'
        )
        
        score = AlgoritmoPrioridad._calcular_riesgo(proyecto_base)
        
        # Promedio: (60 + 80 + 90) / 3 = 76.67
        assert 76.0 <= score <= 77.0, "Promedio de riesgos debe ser ~76.67"
    
    # ==================== PRUEBA 4: calcular_avance ====================
    
    def test_avance_duracion_cero(self, proyecto_base):
        """
        Prueba de caja blanca: Camino especial - Duración del proyecto es 0
        """
        proyecto_base.fecha_inicio = date.today()
        proyecto_base.fecha_final = date.today()
        proyecto_base.save()
        
        score = AlgoritmoPrioridad._calcular_avance(proyecto_base)
        
        assert score == 0, "Duración 0 debe retornar 0"
    
    def test_avance_muy_atrasado(self, proyecto_base):
        """
        Prueba de caja blanca: Camino 1 - Muy atrasado (diferencia >= 30%)
        """
        # Proyecto con 90% del tiempo transcurrido pero solo 10% de avance
        proyecto_base.fecha_inicio = date.today() - timedelta(days=90)
        proyecto_base.fecha_final = date.today() + timedelta(days=10)
        proyecto_base.porcentaje = 10.0
        proyecto_base.save()
        
        score = AlgoritmoPrioridad._calcular_avance(proyecto_base)
        
        assert score == 100, "Muy atrasado debe retornar 100"
    
    def test_avance_atrasado(self, proyecto_base):
        """
        Prueba de caja blanca: Camino 2 - Atrasado (diferencia 15-30%)
        """
        # 60% del tiempo pero solo 40% de avance (diferencia 20%)
        proyecto_base.fecha_inicio = date.today() - timedelta(days=60)
        proyecto_base.fecha_final = date.today() + timedelta(days=40)
        proyecto_base.porcentaje = 40.0
        proyecto_base.save()
        
        score = AlgoritmoPrioridad._calcular_avance(proyecto_base)
        
        assert score == 70, "Atrasado debe retornar 70"
    
    def test_avance_ligero_retraso(self, proyecto_base):
        """
        Prueba de caja blanca: Camino 3 - Ligero retraso (diferencia 5-15%)
        """
        # 50% del tiempo y 40% de avance (diferencia 10%)
        proyecto_base.fecha_inicio = date.today() - timedelta(days=50)
        proyecto_base.fecha_final = date.today() + timedelta(days=50)
        proyecto_base.porcentaje = 40.0
        proyecto_base.save()
        
        score = AlgoritmoPrioridad._calcular_avance(proyecto_base)
        
        assert score == 40, "Ligero retraso debe retornar 40"
    
    def test_avance_en_tiempo(self, proyecto_base):
        """
        Prueba de caja blanca: Camino 4 - En tiempo (diferencia -10% a 5%)
        """
        # 50% del tiempo y 50% de avance (diferencia 0%)
        proyecto_base.fecha_inicio = date.today() - timedelta(days=50)
        proyecto_base.fecha_final = date.today() + timedelta(days=50)
        proyecto_base.porcentaje = 50.0
        proyecto_base.save()
        
        score = AlgoritmoPrioridad._calcular_avance(proyecto_base)
        
        assert score == 20, "En tiempo debe retornar 20"
    
    def test_avance_adelantado(self, proyecto_base):
        """
        Prueba de caja blanca: Camino 5 - Adelantado (diferencia < -10%)
        """
        # 30% del tiempo pero 50% de avance (diferencia -20%)
        proyecto_base.fecha_inicio = date.today() - timedelta(days=30)
        proyecto_base.fecha_final = date.today() + timedelta(days=70)
        proyecto_base.porcentaje = 50.0
        proyecto_base.save()
        
        score = AlgoritmoPrioridad._calcular_avance(proyecto_base)
        
        assert score == 10, "Adelantado debe retornar 10"
    
    # ==================== PRUEBA 5: calcular_recursos ====================
    
    def test_recursos_cero(self, proyecto_base):
        """
        Prueba de caja blanca: Camino 1 - Sin recursos
        """
        score = AlgoritmoPrioridad._calcular_recursos(proyecto_base)
        
        assert score == 0, "Sin recursos debe retornar 0"
    
    def test_recursos_10_o_mas(self, proyecto_base, usuario_admin):
        """
        Prueba de caja blanca: Camino 2 - 10 o más recursos
        """
        for i in range(12):
            RecursoHumano.objects.create(
                proyecto=proyecto_base,
                usuario=usuario_admin
            )
        
        score = AlgoritmoPrioridad._calcular_recursos(proyecto_base)
        
        assert score == 80, "10 o más recursos debe retornar 80"
    
    def test_recursos_5_a_9(self, proyecto_base, usuario_admin):
        """
        Prueba de caja blanca: Camino 3 - 5 a 9 recursos
        """
        for i in range(7):
            RecursoHumano.objects.create(
                proyecto=proyecto_base,
                usuario=usuario_admin
            )
        
        score = AlgoritmoPrioridad._calcular_recursos(proyecto_base)
        
        assert score == 60, "5-9 recursos debe retornar 60"
    
    def test_recursos_3_a_4(self, proyecto_base, usuario_admin):
        """
        Prueba de caja blanca: Camino 4 - 3 a 4 recursos
        """
        for i in range(3):
            RecursoHumano.objects.create(
                proyecto=proyecto_base,
                usuario=usuario_admin
            )
        
        score = AlgoritmoPrioridad._calcular_recursos(proyecto_base)
        
        assert score == 40, "3-4 recursos debe retornar 40"
    
    def test_recursos_1_a_2(self, proyecto_base, usuario_admin):
        """
        Prueba de caja blanca: Camino 5 - 1 a 2 recursos
        """
        RecursoHumano.objects.create(
            proyecto=proyecto_base,
            usuario=usuario_admin
        )
        
        score = AlgoritmoPrioridad._calcular_recursos(proyecto_base)
        
        assert score == 20, "1-2 recursos debe retornar 20"
    
    # ==================== PRUEBA 6: determinar_nivel ====================
    
    def test_nivel_critico(self):
        """
        Prueba de caja blanca: Camino 1 - Nivel Crítico (>= 75)
        """
        nivel = AlgoritmoPrioridad._determinar_nivel(80)
        assert nivel == 'Crítica', "Score >= 75 debe ser Crítica"
    
    def test_nivel_alto(self):
        """
        Prueba de caja blanca: Camino 2 - Nivel Alto (50-74)
        """
        nivel = AlgoritmoPrioridad._determinar_nivel(60)
        assert nivel == 'Alta', "Score 50-74 debe ser Alta"
    
    def test_nivel_medio(self):
        """
        Prueba de caja blanca: Camino 3 - Nivel Medio (25-49)
        """
        nivel = AlgoritmoPrioridad._determinar_nivel(35)
        assert nivel == 'Media', "Score 25-49 debe ser Media"
    
    def test_nivel_bajo(self):
        """
        Prueba de caja blanca: Camino 4 - Nivel Bajo (< 25)
        """
        nivel = AlgoritmoPrioridad._determinar_nivel(15)
        assert nivel == 'Baja', "Score < 25 debe ser Baja"
    
    # ==================== PRUEBA 7: calcular_prioridad (integración) ====================
    
    def test_calcular_prioridad_completa(self, proyecto_base, usuario_admin):
        """
        Prueba de caja blanca: Integración completa del algoritmo
        Verifica que todos los componentes trabajen juntos correctamente
        """
        # Configurar proyecto con valores conocidos
        proyecto_base.fecha_final = date.today() + timedelta(days=5)  # Urgencia: 90
        proyecto_base.presupuesto = 100000
        proyecto_base.costo_final = 150000  # Desviación: 100
        proyecto_base.porcentaje = 20.0
        proyecto_base.fecha_inicio = date.today() - timedelta(days=80)  # Avance: 100
        proyecto_base.save()
        
        # Agregar riesgos
        Riesgo.objects.create(
            proyecto=proyecto_base,
            porcentaje_riesgo=70.0,
            descripcion_riesgo='Riesgo',
            plan_mitigacion_riesgo='Plan'
        )
        
        # Agregar recursos
        for i in range(5):
            RecursoHumano.objects.create(
                proyecto=proyecto_base,
                usuario=usuario_admin
            )
        
        resultado = AlgoritmoPrioridad.calcular_prioridad(proyecto_base)
        
        # Verificar estructura del resultado
        assert 'score' in resultado
        assert 'nivel' in resultado
        assert 'detalles' in resultado
        
        # Verificar que el score esté en el rango válido
        assert 0 <= resultado['score'] <= 100
        
        # Verificar que el nivel sea válido
        assert resultado['nivel'] in ['Crítica', 'Alta', 'Media', 'Baja']
        
        # Verificar que todos los detalles estén presentes
        assert 'urgencia_tiempo' in resultado['detalles']
        assert 'desviacion_presupuesto' in resultado['detalles']
        assert 'riesgo' in resultado['detalles']
        assert 'avance' in resultado['detalles']
        assert 'recursos' in resultado['detalles']