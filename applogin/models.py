from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError 
from cloudinary.models import CloudinaryField 

# Create your models here.
#Usuarios
class Rol(models.Model):
    id = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=50)
    descripcion_rol = models.TextField()

    def __str__(self):
        return self.nombre_rol

class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    correo = models.EmailField(unique=True)
    nombre_usuario = models.CharField(max_length=50, unique=True)
    contrasena = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_usuario

class Proyecto(models.Model):
    id = models.AutoField(primary_key=True)
    nombre_proyecto = models.CharField(max_length=100)
    admin_proyecto_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='proyectos')
    estado = models.CharField(max_length=50, default='En proceso', blank=True)  # ✅ Agregar blank=True
    porcentaje = models.FloatField()
    fecha_inicio = models.DateField()
    fecha_final = models.DateField()
    presupuesto = models.FloatField()
    costo_final = models.FloatField()
    descripcion = models.TextField()
    prioridad_score = models.FloatField(default=0.0, help_text="Puntuación de prioridad calculada automáticamente")
    prioridad_nivel = models.CharField(max_length=20, default='Media', 
                                       choices=[('Crítica', 'Crítica'), 
                                               ('Alta', 'Alta'), 
                                               ('Media', 'Media'), 
                                               ('Baja', 'Baja')])
    ultima_actualizacion_prioridad = models.DateTimeField(null=True, blank=True)
    finalizado = models.BooleanField(default=False, help_text="Indica si el proyecto ha sido finalizado")  # ✅ NUEVO CAMPO
    fecha_finalizacion = models.DateTimeField(null=True, blank=True, help_text="Fecha en que se finalizó el proyecto")  # ✅ NUEVO CAMPO

    def __str__(self):
        return self.nombre_proyecto
    
    class Meta:
        ordering = ['-prioridad_score', 'fecha_final']

    def __str__(self):
        return self.nombre_proyecto


class Impacto(models.Model):
    id = models.AutoField(primary_key=True)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='impactos')
    impacto = models.TextField()
    plan_de_impacto = models.TextField()

    def __str__(self):
        return f'Impacto del proyecto {self.proyecto.nombre_proyecto}'

class RecursoMaterial(models.Model):
    id = models.AutoField(primary_key=True)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='recursos_materiales')
    cantidad = models.IntegerField()
    descripcion = models.TextField()
    nombre_recurso = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre_recurso

class RecursoHumano(models.Model):
    id = models.AutoField(primary_key=True)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='recursos_humanos')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='recursos_humanos')

    def __str__(self):
        return f'{self.usuario.nombre_usuario} en proyecto {self.proyecto.nombre_proyecto}'

class Documento(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.TextField(default='Descripción predeterminada')
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='documentos')
    url_documento = models.URLField(blank=True, null=True)  
    
    # ✅ CAMBIO PRINCIPAL: Usar CloudinaryField en lugar de FileField
    archivo_documento = CloudinaryField(
        'documento',
        resource_type='raw',  # 'raw' es para PDFs y archivos no-imagen
        folder='documentos',  # Carpeta en Cloudinary donde se guardarán
        blank=True,
        null=True,
        help_text='Archivo PDF (máximo 15MB)'
    )

    def __str__(self):
        return f'Documento de proyecto {self.proyecto.nombre_proyecto}'
    
    def clean(self):
        # Validar que tenga URL o archivo, no ambos vacíos
        if not self.url_documento and not self.archivo_documento:
            raise ValidationError('Debe proporcionar una URL o subir un archivo.')
        
        # Validar tamaño del archivo (máximo 15MB)
        if self.archivo_documento:
            # Para CloudinaryField, verificar si tiene contenido antes de validar
            if hasattr(self.archivo_documento, 'file') and self.archivo_documento.file:
                if self.archivo_documento.file.size > 15 * 1024 * 1024:  # 15MB en bytes
                    raise ValidationError('El archivo no puede superar los 15MB.')
                
                # Validar que sea PDF
                if not self.archivo_documento.file.name.endswith('.pdf'):
                    raise ValidationError('Solo se permiten archivos PDF.')

class Fase(models.Model):
    id = models.AutoField(primary_key=True)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='fases')
    fase = models.CharField(max_length=50)
    concluido = models.BooleanField(default=False)  # ✅ Agregar default

    class Meta:
        unique_together = ('proyecto', 'fase')  # ✅ AGREGAR ESTA LÍNEA
        verbose_name = 'Fase'
        verbose_name_plural = 'Fases'

    def __str__(self):
        return f'Fase {self.fase} de proyecto {self.proyecto.nombre_proyecto}'


class Tarea(models.Model):
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('En Progreso', 'En Progreso'),
        ('Completada', 'Completada'),
    ]
    
    id = models.AutoField(primary_key=True)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='tareas')
    fase = models.ForeignKey(Fase, on_delete=models.CASCADE, related_name='tareas')
    recurso_humano = models.ForeignKey(RecursoHumano, on_delete=models.CASCADE, related_name='tareas')
    descripcion = models.TextField(help_text='Descripción de la tarea o actividad a realizar')
    fecha_limite = models.DateField(help_text='Fecha límite para completar la tarea')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    documento_entregable = models.ForeignKey(
        Documento, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='tarea_relacionada',
        help_text='Documento entregable subido por el recurso humano'
    )
    
    class Meta:
        ordering = ['fecha_limite', 'estado']
    
    def __str__(self):
        return f'Tarea: {self.descripcion[:50]} - {self.recurso_humano.usuario.nombre_usuario} ({self.estado})'
    
    def esta_vencida(self):
        """Verifica si la tarea está vencida"""
        from datetime import date
        return self.fecha_limite < date.today() and self.estado != 'Completada'
        
class RelacionDocumento(models.Model):
    id = models.AutoField(primary_key=True)
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE, related_name='relaciones')
    fase = models.ForeignKey(Fase, on_delete=models.CASCADE, related_name='relaciones')
    concluido = models.BooleanField(default=False, help_text='Indica si el entregable ha sido aprobado y concluido')  # ✅ AGREGAR
    fecha_conclusion = models.DateTimeField(null=True, blank=True, help_text='Fecha en que se marcó como concluido')  # ✅ AGREGAR
    
    def __str__(self):
        return f'Relación de Documento {self.documento.id} con Fase {self.fase.id}'
    
    def marcar_concluido(self):
        """Marca la relación como concluida"""
        from django.utils import timezone
        self.concluido = True
        self.fecha_conclusion = timezone.now()
        self.save()
    
    def desmarcar_concluido(self):
        """Desmarca la relación como concluida"""
        self.concluido = False
        self.fecha_conclusion = None
        self.save()

class Riesgo(models.Model):
    id = models.AutoField(primary_key=True)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='riesgos')
    porcentaje_riesgo = models.FloatField()
    descripcion_riesgo = models.TextField()
    plan_mitigacion_riesgo = models.TextField()

    def __str__(self):
        return f'Riesgo del proyecto {self.proyecto.nombre_proyecto}'

