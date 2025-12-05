"""
Generador de Documentación de Caja Blanca por Criterio
Sistema Plannerio - Algoritmo de Priorización
"""

import os
from datetime import date

class GeneradorDocumentacionCajaBlanca:
    def __init__(self):
        self.criterio_seleccionado = None
        self.datos_entrada = {}
        self.resultado_ejecucion = {}
        self.camino_logico = []
        
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
        
        fecha_inicio_str = input("Fecha de inicio (YYYY-MM-DD, ej: 2025-01-15): ")
        fecha_final_str = input("Fecha final (YYYY-MM-DD, ej: 2025-11-01): ")
        
        fecha_inicio = date.fromisoformat(fecha_inicio_str)
        fecha_final = date.fromisoformat(fecha_final_str)
        hoy = date.today()
        dias_restantes = (fecha_final - fecha_inicio).days
        
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
        
        if presupuesto == 0:
            desviacion = 0
        else:
            desviacion = ((costo_final - presupuesto) / presupuesto) * 100
        
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
        
        promedio_riesgo = sum(riesgos) / len(riesgos)
        
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
        
        fecha_inicio_str = input("Fecha de inicio (YYYY-MM-DD, ej: 2025-01-15): ")
        fecha_final_str = input("Fecha final (YYYY-MM-DD, ej: 2025-12-31): ")
        porcentaje_avance = float(input("Porcentaje de avance real (0-100, ej: 25): "))
        
        fecha_inicio = date.fromisoformat(fecha_inicio_str)
        fecha_final = date.fromisoformat(fecha_final_str)
        hoy = date.today()
        
        duracion_total = (fecha_final - fecha_inicio).days
        if duracion_total <= 0:
            print("❌ Error: La fecha final debe ser posterior a la fecha de inicio")
            return False
        
        tiempo_transcurrido = (hoy - fecha_inicio).days
        porcentaje_tiempo = (tiempo_transcurrido / duracion_total) * 100
        diferencia = porcentaje_tiempo - porcentaje_avance
        
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
        
        self.datos_entrada = {
            'cantidad_recursos': cantidad_recursos
        }
        
        self.criterio_seleccionado = 'recursos'
        
        print(f"\n✅ Datos capturados:")
        print(f"   Cantidad de recursos: {cantidad_recursos}")
        
        return True
    
    def ejecutar_algoritmo(self):
        """Ejecuta el algoritmo y traza el camino lógico"""
        self.camino_logico = []
        
        if self.criterio_seleccionado == 'urgencia_tiempo':
            score = self._ejecutar_urgencia_tiempo()
        elif self.criterio_seleccionado == 'desviacion_presupuesto':
            score = self._ejecutar_desviacion_presupuesto()
        elif self.criterio_seleccionado == 'riesgo':
            score = self._ejecutar_riesgo()
        elif self.criterio_seleccionado == 'avance':
            score = self._ejecutar_avance()
        elif self.criterio_seleccionado == 'recursos':
            score = self._ejecutar_recursos()
        else:
            score = 0
        
        self.resultado_ejecucion = {'score': score}
        return score
    
    def _ejecutar_urgencia_tiempo(self):
        dias = self.datos_entrada['dias_restantes']
        
        self.camino_logico.append(f"Evaluando días_restantes = {dias}")
        
        if dias < 0:
            self.camino_logico.append(f"✓ Condición: dias_restantes < 0 → {dias} < 0 → VERDADERO")
            self.camino_logico.append("  Retorna: 100 (Proyecto vencido)")
            return 100
        elif dias <= 7:
            self.camino_logico.append(f"✓ Condición: dias_restantes <= 7 → {dias} <= 7 → VERDADERO")
            self.camino_logico.append("  Retorna: 90 (Menos de 1 semana)")
            return 90
        elif dias <= 30:
            self.camino_logico.append(f"✓ Condición: dias_restantes <= 30 → {dias} <= 30 → VERDADERO")
            self.camino_logico.append("  Retorna: 70 (Menos de 1 mes)")
            return 70
        elif dias <= 90:
            self.camino_logico.append(f"✓ Condición: dias_restantes <= 90 → {dias} <= 90 → VERDADERO")
            self.camino_logico.append("  Retorna: 50 (Menos de 3 meses)")
            return 50
        else:
            self.camino_logico.append(f"✗ Todas las condiciones anteriores son FALSAS")
            self.camino_logico.append("  Retorna: 20 (Más de 3 meses)")
            return 20
    
    def _ejecutar_desviacion_presupuesto(self):
        presupuesto = self.datos_entrada['presupuesto']
        desviacion = self.datos_entrada['desviacion']
        
        self.camino_logico.append(f"Evaluando presupuesto = {presupuesto}")
        
        if presupuesto == 0:
            self.camino_logico.append(f"✓ Condición: presupuesto == 0 → {presupuesto} == 0 → VERDADERO")
            self.camino_logico.append("  Retorna: 0")
            return 0
        
        self.camino_logico.append(f"Desviación calculada = {desviacion:.2f}%")
        
        if desviacion >= 50:
            self.camino_logico.append(f"✓ Condición: desviacion >= 50 → {desviacion:.2f} >= 50 → VERDADERO")
            self.camino_logico.append("  Retorna: 100 (Sobrecosto >= 50%)")
            return 100
        elif desviacion >= 25:
            self.camino_logico.append(f"✓ Condición: desviacion >= 25 → {desviacion:.2f} >= 25 → VERDADERO")
            self.camino_logico.append("  Retorna: 80 (Sobrecosto 25-50%)")
            return 80
        elif desviacion >= 10:
            self.camino_logico.append(f"✓ Condición: desviacion >= 10 → {desviacion:.2f} >= 10 → VERDADERO")
            self.camino_logico.append("  Retorna: 60 (Sobrecosto 10-25%)")
            return 60
        elif desviacion >= 0:
            self.camino_logico.append(f"✓ Condición: desviacion >= 0 → {desviacion:.2f} >= 0 → VERDADERO")
            self.camino_logico.append("  Retorna: 30 (Dentro del presupuesto)")
            return 30
        else:
            self.camino_logico.append(f"✗ Todas las condiciones anteriores son FALSAS")
            self.camino_logico.append("  Retorna: 10 (Bajo presupuesto)")
            return 10
    
    def _ejecutar_riesgo(self):
        cantidad = self.datos_entrada['cantidad_riesgos']
        
        self.camino_logico.append(f"Evaluando cantidad_riesgos = {cantidad}")
        
        if cantidad == 0:
            self.camino_logico.append(f"✓ Condición: not riesgos.exists() → cantidad == 0 → VERDADERO")
            self.camino_logico.append("  Retorna: 0 (Sin riesgos)")
            return 0
        
        promedio = self.datos_entrada['promedio_riesgo']
        self.camino_logico.append(f"Promedio de riesgo = {promedio:.2f}%")
        self.camino_logico.append(f"Retorna: min({promedio:.2f}, 100) = {min(promedio, 100):.2f}")
        
        return min(promedio, 100)
    
    def _ejecutar_avance(self):
        diferencia = self.datos_entrada['diferencia']
        
        self.camino_logico.append(f"Evaluando diferencia (atraso) = {diferencia:.2f}%")
        
        if diferencia >= 30:
            self.camino_logico.append(f"✓ Condición: diferencia >= 30 → {diferencia:.2f} >= 30 → VERDADERO")
            self.camino_logico.append("  Retorna: 100 (Muy atrasado)")
            return 100
        elif diferencia >= 15:
            self.camino_logico.append(f"✓ Condición: diferencia >= 15 → {diferencia:.2f} >= 15 → VERDADERO")
            self.camino_logico.append("  Retorna: 70 (Atrasado)")
            return 70
        elif diferencia >= 5:
            self.camino_logico.append(f"✓ Condición: diferencia >= 5 → {diferencia:.2f} >= 5 → VERDADERO")
            self.camino_logico.append("  Retorna: 40 (Ligeramente atrasado)")
            return 40
        elif diferencia >= -10:
            self.camino_logico.append(f"✓ Condición: diferencia >= -10 → {diferencia:.2f} >= -10 → VERDADERO")
            self.camino_logico.append("  Retorna: 20 (En tiempo)")
            return 20
        else:
            self.camino_logico.append(f"✗ Todas las condiciones anteriores son FALSAS")
            self.camino_logico.append("  Retorna: 10 (Adelantado)")
            return 10
    
    def _ejecutar_recursos(self):
        cantidad = self.datos_entrada['cantidad_recursos']
        
        self.camino_logico.append(f"Evaluando cantidad_recursos = {cantidad}")
        
        if cantidad == 0:
            self.camino_logico.append(f"✓ Condición: cantidad_recursos == 0 → {cantidad} == 0 → VERDADERO")
            self.camino_logico.append("  Retorna: 0")
            return 0
        elif cantidad >= 10:
            self.camino_logico.append(f"✓ Condición: cantidad_recursos >= 10 → {cantidad} >= 10 → VERDADERO")
            self.camino_logico.append("  Retorna: 80 (Muchos recursos)")
            return 80
        elif cantidad >= 5:
            self.camino_logico.append(f"✓ Condición: cantidad_recursos >= 5 → {cantidad} >= 5 → VERDADERO")
            self.camino_logico.append("  Retorna: 60 (Varios recursos)")
            return 60
        elif cantidad >= 3:
            self.camino_logico.append(f"✓ Condición: cantidad_recursos >= 3 → {cantidad} >= 3 → VERDADERO")
            self.camino_logico.append("  Retorna: 40 (Recursos moderados)")
            return 40
        else:
            self.camino_logico.append(f"✗ Todas las condiciones anteriores son FALSAS")
            self.camino_logico.append("  Retorna: 20 (Pocos recursos)")
            return 20
    
    def generar_documentacion(self):
        """Genera la documentación de caja blanca"""
        score = self.ejecutar_algoritmo()
        
        nombre_criterio = {
            'urgencia_tiempo': 'URGENCIA DE TIEMPO',
            'desviacion_presupuesto': 'DESVIACIÓN DE PRESUPUESTO',
            'riesgo': 'NIVEL DE RIESGO',
            'avance': 'RETRASO EN AVANCE',
            'recursos': 'RECURSOS ASIGNADOS'
        }.get(self.criterio_seleccionado, 'DESCONOCIDO')
        
        doc = []
        doc.append("=" * 80)
        doc.append("  DOCUMENTACIÓN DE CAJA BLANCA")
        doc.append(f"  Criterio: {nombre_criterio}")
        doc.append(f"  Fecha: {date.today()}")
        doc.append("=" * 80)
        doc.append("")
        
        # 1. DATOS DE ENTRADA
        doc.append("1. DATOS DE ENTRADA")
        doc.append("-" * 80)
        for key, value in self.datos_entrada.items():
            doc.append(f"   {key}: {value}")
        doc.append("")
        
        # 2. CÓDIGO FUENTE CON VALORES SUSTITUIDOS
        doc.append("2. CÓDIGO FUENTE CON VALORES SUSTITUIDOS")
        doc.append("-" * 80)
        doc.append(self._generar_codigo_con_valores())
        doc.append("")
        
        # 3. CAMINO LÓGICO EJECUTADO
        doc.append("3. CAMINO LÓGICO EJECUTADO")
        doc.append("-" * 80)
        for paso in self.camino_logico:
            doc.append(f"   {paso}")
        doc.append("")
        
        # 4. RESULTADO
        doc.append("4. RESULTADO/SCORE OBTENIDO")
        doc.append("-" * 80)
        doc.append(f"   Score: {score}")
        doc.append("")
        doc.append("=" * 80)
        
        return "\n".join(doc)
    
    def _generar_codigo_con_valores(self):
        """Genera el código con los valores sustituidos"""
        if self.criterio_seleccionado == 'urgencia_tiempo':
            return self._codigo_urgencia_tiempo()
        elif self.criterio_seleccionado == 'desviacion_presupuesto':
            return self._codigo_desviacion_presupuesto()
        elif self.criterio_seleccionado == 'riesgo':
            return self._codigo_riesgo()
        elif self.criterio_seleccionado == 'avance':
            return self._codigo_avance()
        elif self.criterio_seleccionado == 'recursos':
            return self._codigo_recursos()
        return ""
    
    def _codigo_urgencia_tiempo(self):
        d = self.datos_entrada
        return f"""
   def _calcular_urgencia_tiempo(proyecto):
       hoy = date.today()  # → {d['fecha_hoy']}
       dias_restantes = (proyecto.fecha_final - hoy).days  # → {d['dias_restantes']}
       
       if dias_restantes < 0:  # → {d['dias_restantes']} < 0
           return 100
       elif dias_restantes <= 7:  # → {d['dias_restantes']} <= 7
           return 90
       elif dias_restantes <= 30:  # → {d['dias_restantes']} <= 30
           return 70
       elif dias_restantes <= 90:  # → {d['dias_restantes']} <= 90
           return 50
       else:
           return 20
"""
    
    def _codigo_desviacion_presupuesto(self):
        d = self.datos_entrada
        return f"""
   def _calcular_desviacion_presupuesto(proyecto):
       if proyecto.presupuesto == 0:  # → {d['presupuesto']} == 0
           return 0
       
       desviacion = ((proyecto.costo_final - proyecto.presupuesto) / proyecto.presupuesto) * 100
       # → (({d['costo_final']} - {d['presupuesto']}) / {d['presupuesto']}) * 100 = {d['desviacion']:.2f}
       
       if desviacion >= 50:  # → {d['desviacion']:.2f} >= 50
           return 100
       elif desviacion >= 25:  # → {d['desviacion']:.2f} >= 25
           return 80
       elif desviacion >= 10:  # → {d['desviacion']:.2f} >= 10
           return 60
       elif desviacion >= 0:  # → {d['desviacion']:.2f} >= 0
           return 30
       else:
           return 10
"""
    
    def _codigo_riesgo(self):
        d = self.datos_entrada
        return f"""
   def _calcular_riesgo(proyecto):
       riesgos = proyecto.riesgos.all()  # → {d['cantidad_riesgos']} riesgos
       
       if not riesgos.exists():  # → {d['cantidad_riesgos'] == 0}
           return 0
       
       promedio_riesgo = sum(r.porcentaje_riesgo for r in riesgos) / len(riesgos)
       # → sum({d['riesgos']}) / {d['cantidad_riesgos']} = {d['promedio_riesgo']:.2f}
       
       return min(promedio_riesgo, 100)  # → min({d['promedio_riesgo']:.2f}, 100)
"""
    
    def _codigo_avance(self):
        d = self.datos_entrada
        return f"""
   def _calcular_avance(proyecto):
       hoy = date.today()  # → {d['fecha_hoy']}
       
       duracion_total = (proyecto.fecha_final - proyecto.fecha_inicio).days
       # → {d['duracion_total']} días
       
       if duracion_total <= 0:
           return 0
       
       tiempo_transcurrido = (hoy - proyecto.fecha_inicio).days  # → {d['tiempo_transcurrido']}
       porcentaje_tiempo = (tiempo_transcurrido / duracion_total) * 100
       # → ({d['tiempo_transcurrido']} / {d['duracion_total']}) * 100 = {d['porcentaje_tiempo']:.2f}%
       
       diferencia = porcentaje_tiempo - proyecto.porcentaje
       # → {d['porcentaje_tiempo']:.2f} - {d['porcentaje_avance']} = {d['diferencia']:.2f}
       
       if diferencia >= 30:  # → {d['diferencia']:.2f} >= 30
           return 100
       elif diferencia >= 15:  # → {d['diferencia']:.2f} >= 15
           return 70
       elif diferencia >= 5:  # → {d['diferencia']:.2f} >= 5
           return 40
       elif diferencia >= -10:  # → {d['diferencia']:.2f} >= -10
           return 20
       else:
           return 10
"""
    
    def _codigo_recursos(self):
        d = self.datos_entrada
        return f"""
   def _calcular_recursos(proyecto):
       cantidad_recursos = proyecto.recursos_humanos.count()  # → {d['cantidad_recursos']}
       
       if cantidad_recursos == 0:  # → {d['cantidad_recursos']} == 0
           return 0
       elif cantidad_recursos >= 10:  # → {d['cantidad_recursos']} >= 10
           return 80
       elif cantidad_recursos >= 5:  # → {d['cantidad_recursos']} >= 5
           return 60
       elif cantidad_recursos >= 3:  # → {d['cantidad_recursos']} >= 3
           return 40
       else:
           return 20
"""
    
    def guardar_documentacion(self, contenido):
        """Guarda la documentación en un archivo"""
        os.makedirs('documentacion_caja_blanca', exist_ok=True)
        
        nombre_archivo = f"documentacion_caja_blanca/{self.criterio_seleccionado}_{date.today()}.txt"
        
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        print(f"\n✅ Documentación guardada en: {nombre_archivo}")
        return nombre_archivo
    
    def ejecutar(self):
        """Ejecuta el flujo completo"""
        while True:
            opcion = self.menu_principal()
            
            if opcion == 0:
                print("\n👋 ¡Hasta luego!")
                break
            
            capturado = False
            
            if opcion == 1:
                print("\n📄 Procesando Criterio 1: Urgencia de Tiempo...")
                capturado = self.capturar_datos_urgencia_tiempo()
            elif opcion == 2:
                print("\n📄 Procesando Criterio 2: Desviación de Presupuesto...")
                capturado = self.capturar_datos_desviacion_presupuesto()
            elif opcion == 3:
                print("\n📄 Procesando Criterio 3: Nivel de Riesgo...")
                capturado = self.capturar_datos_riesgo()
            elif opcion == 4:
                print("\n📄 Procesando Criterio 4: Retraso en Avance...")
                capturado = self.capturar_datos_avance()
            elif opcion == 5:
                print("\n📄 Procesando Criterio 5: Recursos Asignados...")
                capturado = self.capturar_datos_recursos()
            
            if capturado:
                print("\n🔄 Generando documentación de caja blanca...")
                documentacion = self.generar_documentacion()
                
                print("\n" + documentacion)
                
                self.guardar_documentacion(documentacion)
                
                input("\n📌 Presiona Enter para continuar...")


if __name__ == "__main__":
    generador = GeneradorDocumentacionCajaBlanca()
    generador.ejecutar()