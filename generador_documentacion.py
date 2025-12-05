"""
Generador de Documentación de Caja Blanca por Criterio
Sistema Plannerio - Algoritmo de Priorización
"""

import os
import json
from datetime import date, timedelta
from pathlib import Path

class GeneradorDocumentacionCajaBlanca:
    def __init__(self):
        self.codigo_fuente = self._cargar_codigo_fuente()
        self.criterio_seleccionado = None
        self.datos_entrada = {}
        self.resultado_ejecucion = {}
        
    def _cargar_codigo_fuente(self):
        """Carga el código fuente del archivo prioridad.py"""
        try:
            with open('applogin/prioridad.py', 'r', encoding='utf-8') as f:
                return f.readlines()
        except Exception as e:
            print(f"Error al cargar código fuente: {e}")
            return []
    
    def menu_principal(self):
        """Muestra el menú de selección de criterio"""
        print("\n" + "="*70)
        print("  GENERADOR DE DOCUMENTACIÓN DE CAJA BLANCA")
        print("  Sistema Plannerio - Por Criterio Individual")
        print("="*70)
        print("\nSelecciona el CRITERIO a documentar:")
        print("\n  1. Urgencia de Tiempo")
        print("  2. Desviación de Presupuesto")
        print("  3. Nivel de Riesgo")
        print("  4. Retraso en Avance")
        print("  5. Recursos Asignados")
        print("\n  0. Salir")
        print("="*70)
        
        while True:
            try:
                opcion = int(input("\nIngresa el número del criterio (0-5): "))
                if 0 <= opcion <= 5:
                    return opcion
                else:
                    print("❌ Opción inválida. Ingresa un número entre 0 y 5.")
            except ValueError:
                print("❌ Ingresa un número válido.")
    
    def capturar_datos_urgencia_tiempo(self):
        """Captura datos para el criterio de Urgencia de Tiempo"""
        print("\n" + "="*70)
        print("CRITERIO: URGENCIA DE TIEMPO")
        print("="*70)
        print("\n📋 Ingresa los datos del proyecto:\n")
        
        # Capturar fechas
        fecha_inicio_str = input("Fecha de inicio (YYYY-MM-DD, ej: 2025-01-15): ")
        fecha_final_str = input("Fecha final (YYYY-MM-DD, ej: 2025-11-01): ")
        
        # Convertir a objetos date
        fecha_inicio = date.fromisoformat(fecha_inicio_str)
        fecha_final = date.fromisoformat(fecha_final_str)
        
        # Calcular días restantes
        hoy = date.today()
        dias_restantes = (fecha_final - fecha_inicio).days
        
        # Guardar datos
        self.datos_entrada = {
            'fecha_inicio': fecha_inicio,
            'fecha_final': fecha_final,
            'fecha_hoy': hoy,
            'dias_restantes': dias_restantes
        }
        
        self.criterio_seleccionado = 'urgencia_tiempo'
        
        print(f"\n✅ Datos capturados:")
        print(f"   Fecha inicio: {fecha_inicio}")
        print(f"   Fecha final: {fecha_final}")
        print(f"   Fecha hoy: {hoy}")
        print(f"   Días restantes: {dias_restantes}")
        
        return True
    
    def capturar_datos_desviacion_presupuesto(self):
        """Captura datos para el criterio de Desviación de Presupuesto"""
        print("\n" + "="*70)
        print("CRITERIO: DESVIACIÓN DE PRESUPUESTO")
        print("="*70)
        print("\n📋 Ingresa los datos del proyecto:\n")
        
        presupuesto = float(input("Presupuesto planeado (ej: 100000): "))
        costo_final = float(input("Costo final real (ej: 150000): "))
        
        # Calcular desviación
        if presupuesto == 0:
            desviacion = 0
        else:
            desviacion = ((costo_final - presupuesto) / presupuesto) * 100
        
        # Guardar datos
        self.datos_entrada = {
            'presupuesto': presupuesto,
            'costo_final': costo_final,
            'desviacion': desviacion
        }
        
        self.criterio_seleccionado = 'desviacion_presupuesto'
        
        print(f"\n✅ Datos capturados:")
        print(f"   Presupuesto: ${presupuesto:,.2f}")
        print(f"   Costo final: ${costo_final:,.2f}")
        print(f"   Desviación: {desviacion:.2f}%")
        
        return True
    
    def capturar_datos_riesgo(self):
        """Captura datos para el criterio de Nivel de Riesgo"""
        print("\n" + "="*70)
        print("CRITERIO: NIVEL DE RIESGO")
        print("="*70)
        print("\n📋 Ingresa los datos de riesgos del proyecto:\n")
        
        cantidad_riesgos = int(input("¿Cuántos riesgos tiene el proyecto? (ej: 3): "))
        
        if cantidad_riesgos == 0:
            self.datos_entrada = {
                'cantidad_riesgos': 0,
                'riesgos': [],
                'promedio_riesgo': 0
            }
            self.criterio_seleccionado = 'riesgo'
            print(f"\n✅ Sin riesgos registrados")
            return True
        
        riesgos = []
        print("\nIngresa el porcentaje de riesgo para cada uno:")
        for i in range(cantidad_riesgos):
            porcentaje = float(input(f"  Riesgo {i+1} - Porcentaje (0-100, ej: 75): "))
            riesgos.append(porcentaje)
        
        # Calcular promedio
        promedio_riesgo = sum(riesgos) / len(riesgos)
        
        # Guardar datos
        self.datos_entrada = {
            'cantidad_riesgos': cantidad_riesgos,
            'riesgos': riesgos,
            'promedio_riesgo': promedio_riesgo
        }
        
        self.criterio_seleccionado = 'riesgo'
        
        print(f"\n✅ Datos capturados:")
        print(f"   Cantidad de riesgos: {cantidad_riesgos}")
        print(f"   Riesgos: {riesgos}")
        print(f"   Promedio de riesgo: {promedio_riesgo:.2f}%")
        
        return True
    
    def capturar_datos_avance(self):
        """Captura datos para el criterio de Retraso en Avance"""
        print("\n" + "="*70)
        print("CRITERIO: RETRASO EN AVANCE")
        print("="*70)
        print("\n📋 Ingresa los datos del proyecto:\n")
        
        # Capturar fechas
        fecha_inicio_str = input("Fecha de inicio (YYYY-MM-DD, ej: 2025-01-15): ")
        fecha_final_str = input("Fecha final (YYYY-MM-DD, ej: 2025-12-31): ")
        porcentaje_avance = float(input("Porcentaje de avance real (0-100, ej: 25): "))
        
        # Convertir a objetos date
        fecha_inicio = date.fromisoformat(fecha_inicio_str)
        fecha_final = date.fromisoformat(fecha_final_str)
        hoy = date.today()
        
        # Calcular % de tiempo transcurrido
        duracion_total = (fecha_final - fecha_inicio).days
        if duracion_total <= 0:
            print("❌ Error: La fecha final debe ser posterior a la fecha de inicio")
            return False
        
        tiempo_transcurrido = (hoy - fecha_inicio).days
        porcentaje_tiempo = (tiempo_transcurrido / duracion_total) * 100
        
        # Calcular diferencia (atraso)
        diferencia = porcentaje_tiempo - porcentaje_avance
        
        # Guardar datos
        self.datos_entrada = {
            'fecha_inicio': fecha_inicio,
            'fecha_final': fecha_final,
            'fecha_hoy': hoy,
            'duracion_total': duracion_total,
            'tiempo_transcurrido': tiempo_transcurrido,
            'porcentaje_tiempo': porcentaje_tiempo,
            'porcentaje_avance': porcentaje_avance,
            'diferencia': diferencia
        }
        
        self.criterio_seleccionado = 'avance'
        
        print(f"\n✅ Datos capturados:")
        print(f"   Fecha inicio: {fecha_inicio}")
        print(f"   Fecha final: {fecha_final}")
        print(f"   Fecha hoy: {hoy}")
        print(f"   Duración total: {duracion_total} días")
        print(f"   Tiempo transcurrido: {tiempo_transcurrido} días ({porcentaje_tiempo:.2f}%)")
        print(f"   Avance real: {porcentaje_avance}%")
        print(f"   Diferencia (atraso): {diferencia:.2f}%")
        
        return True
    
    def capturar_datos_recursos(self):
        """Captura datos para el criterio de Recursos Asignados"""
        print("\n" + "="*70)
        print("CRITERIO: RECURSOS ASIGNADOS")
        print("="*70)
        print("\n📋 Ingresa los datos del proyecto:\n")
        
        cantidad_recursos = int(input("¿Cuántos recursos humanos tiene asignados el proyecto? (ej: 5): "))
        
        # Guardar datos
        self.datos_entrada = {
            'cantidad_recursos': cantidad_recursos
        }
        
        self.criterio_seleccionado = 'recursos'
        
        print(f"\n✅ Datos capturados:")
        print(f"   Cantidad de recursos: {cantidad_recursos}")
        
        return True
    
    def ejecutar(self):
        """Ejecuta el flujo completo"""
        while True:
            opcion = self.menu_principal()
            
            if opcion == 0:
                print("\n👋 ¡Hasta luego!")
                break
            elif opcion == 1:
                print("\n🔄 Procesando Criterio 1: Urgencia de Tiempo...")
                if self.capturar_datos_urgencia_tiempo():
                    print("\n✅ Datos listos. Continuando...")
                    input("\nPresiona Enter para continuar...")
            elif opcion == 2:
                print("\n🔄 Procesando Criterio 2: Desviación de Presupuesto...")
                if self.capturar_datos_desviacion_presupuesto():
                    print("\n✅ Datos listos. Continuando...")
                    input("\nPresiona Enter para continuar...")
            elif opcion == 3:
                print("\n🔄 Procesando Criterio 3: Nivel de Riesgo...")
                if self.capturar_datos_riesgo():
                    print("\n✅ Datos listos. Continuando...")
                    input("\nPresiona Enter para continuar...")
            elif opcion == 4:
                print("\n🔄 Procesando Criterio 4: Retraso en Avance...")
                if self.capturar_datos_avance():
                    print("\n✅ Datos listos. Continuando...")
                    input("\nPresiona Enter para continuar...")
            elif opcion == 5:
                print("\n🔄 Procesando Criterio 5: Recursos Asignados...")
                if self.capturar_datos_recursos():
                    print("\n✅ Datos listos. Continuando...")
                    input("\nPresiona Enter para continuar...")


if __name__ == "__main__":
    generador = GeneradorDocumentacionCajaBlanca()
    generador.ejecutar()