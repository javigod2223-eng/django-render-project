from django import forms
from datetime import date
from django.core.exceptions import ValidationError 
from .models import Fase, Rol, Proyecto, Usuario, RecursoHumano, RecursoMaterial, Documento, Riesgo, RelacionDocumento, Tarea
#La opcion administrador se oculta con javascript en la vista por temas de bugs
class InsertarUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['rol', 'correo', 'nombre_usuario', 'contrasena']
        widgets = {
            'rol': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('Administrador', 'Administrador'),
                ('Usuario', 'Usuario'),
                
            ]),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'nombre_usuario': forms.TextInput(attrs={'class': 'form-control'}),
            'contrasena': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
    
    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        # Si estamos editando, excluir el usuario actual
        if self.instance.pk:
            if Usuario.objects.filter(correo=correo).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Ya existe un usuario con este correo electrónico.')
        else:
            if Usuario.objects.filter(correo=correo).exists():
                raise forms.ValidationError('Ya existe un usuario con este correo electrónico.')
        return correo

class FaseForm(forms.ModelForm):
    class Meta:
        model = Fase
        fields = ['proyecto', 'fase', 'concluido']

#Form para agregar roles
class RolForm(forms.ModelForm):
    class Meta:
        model = Rol  # Especifica el modelo al que pertenece este formulario
        fields = ['nombre_rol', 'descripcion_rol']
        labels = {
            'nombre_rol': 'Nombre del Rol',
            'descripcion_rol': 'Descripción del Rol',
        }
        widgets = {
            'nombre_rol': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre del rol'}),
            'descripcion_rol': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ingrese la descripción del rol'}),
        }

class LoginForm(forms.Form):
    email = forms.EmailField(label='Correo electrónico', max_length=100, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su correo electrónico'}))
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su contraseña'}))

from django import forms
from .models import Proyecto
from datetime import date

class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = [
            'nombre_proyecto', 
            'admin_proyecto_usuario', 
            'porcentaje', 
            'fecha_inicio', 
            'fecha_final', 
            'presupuesto', 
            'costo_final', 
            'descripcion'
        ]
        widgets = {
            'nombre_proyecto': forms.TextInput(attrs={'class': 'form-control'}),
            'admin_proyecto_usuario': forms.Select(attrs={'class': 'form-control'}),
            'porcentaje': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100', 'step': '0.1'}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_final': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'presupuesto': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'costo_final': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'nombre_proyecto': 'Nombre del Proyecto',
            'admin_proyecto_usuario': 'Administrador del Proyecto',
            'porcentaje': 'Porcentaje de Avance (%)',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_final': 'Fecha Final',
            'presupuesto': 'Presupuesto Inicial',
            'costo_final': 'Costo Final',
            'descripcion': 'Descripción del Proyecto',
        }

    def clean_nombre_proyecto(self):
        """Validar que el nombre del proyecto sea único"""
        nombre = self.cleaned_data.get('nombre_proyecto')
        
        # Si es edición, excluir el proyecto actual
        if self.instance.pk:
            existe = Proyecto.objects.filter(nombre_proyecto__iexact=nombre).exclude(pk=self.instance.pk).exists()
        else:
            existe = Proyecto.objects.filter(nombre_proyecto__iexact=nombre).exists()
        
        if existe:
            raise forms.ValidationError(
                f'Ya existe un proyecto con el nombre "{nombre}". Por favor, elige otro nombre.'
            )
        
        return nombre

    def clean_fecha_inicio(self):
        """Validar que la fecha de inicio no sea anterior a hoy (permite hoy)"""
        fecha_inicio = self.cleaned_data.get('fecha_inicio')
        hoy = date.today()
    
        # Solo validar para proyectos nuevos
        if not self.instance.pk and fecha_inicio and fecha_inicio < hoy:
            raise forms.ValidationError(
                f'La fecha de inicio no puede ser anterior a hoy ({hoy.strftime("%d/%m/%Y")}). '
                f'Fecha ingresada: {fecha_inicio.strftime("%d/%m/%Y")}'
            )
    
        return fecha_inicio

    def clean_fecha_final(self):
        """Validar que la fecha final no sea anterior a hoy (permite hoy)"""
        fecha_final = self.cleaned_data.get('fecha_final')
        hoy = date.today()
    
        if fecha_final and fecha_final < hoy:
            raise forms.ValidationError(
                f'La fecha final no puede ser anterior a hoy ({hoy.strftime("%d/%m/%Y")}). '
                f'Fecha ingresada: {fecha_final.strftime("%d/%m/%Y")}'
            )
    
        return fecha_final

    def clean_presupuesto(self):
        """Validar que el presupuesto sea mayor a 0"""
        presupuesto = self.cleaned_data.get('presupuesto')
        
        if presupuesto is not None and presupuesto < 0:
            raise forms.ValidationError(
                'El presupuesto inicial no puede ser negativo. Ingresa un valor mayor o igual a 0.'
            )
        
        if presupuesto is not None and presupuesto == 0:
            raise forms.ValidationError(
                'El presupuesto inicial debe ser mayor a 0.'
            )
        
        return presupuesto

    def clean_costo_final(self):
        """Validar que el costo final no sea negativo"""
        costo_final = self.cleaned_data.get('costo_final')
        
        if costo_final is not None and costo_final < 0:
            raise forms.ValidationError(
                'El costo final no puede ser negativo. Ingresa un valor mayor o igual a 0.'
            )
        
        return costo_final

    def clean_porcentaje(self):
        """Validar que el porcentaje esté entre 0 y 100"""
        porcentaje = self.cleaned_data.get('porcentaje')
        
        if porcentaje is not None and (porcentaje < 0 or porcentaje > 100):
            raise forms.ValidationError(
                'El porcentaje debe estar entre 0 y 100.'
            )
        
        return porcentaje

    def clean(self):
        """Validaciones que requieren múltiples campos"""
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_final = cleaned_data.get('fecha_final')
        presupuesto = cleaned_data.get('presupuesto')
        costo_final = cleaned_data.get('costo_final')
        
        # Validar que fecha final sea posterior o igual a fecha inicio
        if fecha_inicio and fecha_final:
            if fecha_final < fecha_inicio:
                raise forms.ValidationError(
                    'La fecha final no puede ser anterior a la fecha de inicio. '
                    f'Fecha de inicio: {fecha_inicio.strftime("%d/%m/%Y")}, '
                    f'Fecha final: {fecha_final.strftime("%d/%m/%Y")}'
                )
        
        # Validar que el costo final no exceda mucho el presupuesto (opcional)
        if presupuesto and costo_final:
            if costo_final > presupuesto * 2:
                self.add_error('costo_final', 
                    f'Advertencia: El costo final ({costo_final}) es más del doble del presupuesto inicial ({presupuesto}). '
                    'Verifica que los valores sean correctos.'
                )
        
        return cleaned_data

class ProyectoEditarForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = '__all__'
        widgets = {
            'nombre_proyecto': forms.TextInput(attrs={'class': 'form-control'}),
            'admin_proyecto_usuario': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control'}),
            'porcentaje': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_final': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'presupuesto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'costo_final': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_nombre_proyecto(self):
        nombre_proyecto = self.cleaned_data.get('nombre_proyecto')
        if self.instance.pk:
            if Proyecto.objects.filter(nombre_proyecto=nombre_proyecto).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Ya existe un proyecto con este nombre.')
        return nombre_proyecto
    
    def clean_presupuesto(self):
        presupuesto = self.cleaned_data.get('presupuesto')
        if presupuesto and presupuesto <= 0:
            raise forms.ValidationError('El presupuesto debe ser un valor positivo mayor a 0.')
        return presupuesto

    def clean_costo_final(self):
        costo_final = self.cleaned_data.get('costo_final')
        if costo_final and costo_final < 0:
            raise forms.ValidationError('El costo final no puede ser negativo.')
        return costo_final
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_final = cleaned_data.get('fecha_final')
        
        # Validar que las fechas sean del año 2025 en adelante
        if fecha_inicio and fecha_inicio.year < 2025:
            raise forms.ValidationError('La fecha de inicio debe ser del año 2025 en adelante.')
        
        if fecha_final and fecha_final.year < 2025:
            raise forms.ValidationError('La fecha final debe ser del año 2025 en adelante.')
        
        # Validar que fecha inicio no sea posterior a fecha final
        if fecha_inicio and fecha_final and fecha_inicio > fecha_final:
            raise forms.ValidationError('La fecha de inicio no puede ser posterior a la fecha final.')

        return cleaned_data

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['rol', 'correo', 'nombre_usuario', 'contrasena']
        widgets = {
            'rol': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('Administrador', 'Administrador'),
                ('Usuario', 'Usuario'),
            ]),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'nombre_usuario': forms.TextInput(attrs={'class': 'form-control'}),
            'contrasena': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if self.instance.pk:
            if Usuario.objects.filter(correo=correo).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Ya existe un usuario con este correo electrónico.')
        else:
            if Usuario.objects.filter(correo=correo).exists():
                raise forms.ValidationError('Ya existe un usuario con este correo electrónico.')
        return correo

    def clean(self):
        cleaned_data = super().clean()
        contrasena = cleaned_data.get('contrasena')
        return cleaned_data

class AsignarRecursoHumanoForm(forms.ModelForm):
    usuario = forms.ModelChoiceField(
        queryset=Usuario.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Seleccione un usuario"
    )

    class Meta:
        model = RecursoHumano
        fields = ['usuario']

    def __init__(self, proyecto, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['usuario'].queryset = Usuario.objects.filter(rol__nombre_rol__iexact='usuario')
        self.instance.proyecto = proyecto
        self.proyecto = proyecto

    def clean_usuario(self):
        usuario = self.cleaned_data.get('usuario')
    
        if RecursoHumano.objects.filter(proyecto=self.proyecto, usuario=usuario).exists():
            raise ValidationError('El usuario ya está asignado a este proyecto.')
    
    # ✅ Contar proyectos activos (no finalizados)
        proyectos_asignados = RecursoHumano.objects.filter(
            usuario=usuario
        ).exclude(
            proyecto__finalizado=True  # Excluir proyectos finalizados
        ).count()
    
        if proyectos_asignados >= 2:
            raise ValidationError(
                f'El usuario "{usuario.nombre_usuario}" ya tiene el máximo de 2 proyectos activos asignados. '
                f'No se pueden asignar más proyectos.'
            )
    
        return usuario

class AgregarRecursoMaterialForm(forms.ModelForm):
    class Meta:
        model = RecursoMaterial
        fields = ['nombre_recurso', 'cantidad', 'descripcion']
        widgets = {
            'nombre_recurso': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese nombre del recurso'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la cantidad'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ingrese la descripción', 'rows': 3}),
        }

    def __init__(self, proyecto, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.proyecto = proyecto

class AgregarDocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['descripcion', 'url_documento']
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la descripción'}),
            'url_documento': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la URL del documento'}),
        }

    def __init__(self, proyecto, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.proyecto = proyecto

class AgregarDocumentoFormProyecto(forms.ModelForm):
    tarea = forms.ModelChoiceField(
        queryset=Tarea.objects.none(),
        required=False,
        label='Asociar a tarea (opcional)',
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Selecciona la tarea a la que corresponde este entregable'
    )
    
    class Meta:
        model = Documento
        fields = ['proyecto', 'descripcion', 'url_documento', 'archivo_documento', 'tarea']
        widgets = {
            'proyecto': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'url_documento': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'archivo_documento': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }
        labels = {
            'proyecto': 'Proyecto',
            'descripcion': 'Descripción del entregable',
            'url_documento': 'URL del documento (opcional)',
            'archivo_documento': 'O subir archivo PDF (opcional - máx 15MB)',
        }

    def __init__(self, usuario, *args, **kwargs):
        super().__init__(*args, **kwargs)
        proyectos_usuario = Proyecto.objects.filter(
            recursos_humanos__usuario=usuario
        ).distinct()
        self.fields['proyecto'].queryset = proyectos_usuario

        recursos_humanos = RecursoHumano.objects.filter(usuario=usuario)
        self.fields['tarea'].queryset = Tarea.objects.filter(
            recurso_humano__in=recursos_humanos,
            estado__in=['Pendiente', 'En Progreso'],
            documento_entregable__isnull=True
        ).select_related('proyecto', 'fase')
        self.fields['tarea'].label_from_instance = lambda obj: (
            f"{obj.proyecto.nombre_proyecto} - {obj.fase.fase} - {obj.descripcion[:50]}..."
        )

    def clean(self):
        cleaned_data = super().clean()
        url = cleaned_data.get('url_documento')
        archivo = cleaned_data.get('archivo_documento')

        if not url and not archivo:
            raise forms.ValidationError('Debe proporcionar una URL o subir un archivo PDF.')
        return cleaned_data

    def clean_archivo_documento(self):
        archivo = self.cleaned_data.get('archivo_documento')

        if archivo:
            # Forzar conversión del tamaño a entero (por seguridad)
            tamaño = int(archivo.size)

        if tamaño > 15 * 1024 * 1024:
            raise forms.ValidationError('El archivo no puede superar los 15 MB.')

        # Validar extensión
        if not archivo.name.lower().endswith('.pdf'):
            raise forms.ValidationError('Solo se permiten archivos PDF.')

        return archivo


    
class AgregarRiesgoForm(forms.ModelForm):
    class Meta:
        model = Riesgo
        fields = ['porcentaje_riesgo', 'descripcion_riesgo', 'plan_mitigacion_riesgo']
        widgets = {
            'porcentaje_riesgo': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el porcentaje de riesgo'}),
            'descripcion_riesgo': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ingrese la descripción del riesgo', 'rows': 3}),
            'plan_mitigacion_riesgo': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ingrese el plan de mitigación', 'rows': 3}),
        }

    def __init__(self, proyecto, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.proyecto = proyecto

class AgregarFaseForm(forms.ModelForm):
    class Meta:
        model = Fase
        fields = ['fase']  # ✅ QUITAR 'concluido'
        widgets = {
            'fase': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ingrese el nombre de la fase'
            }),
        }
        labels = {
            'fase': 'Nombre de la Fase'
        }

    def __init__(self, proyecto, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.proyecto = proyecto
        self.proyecto = proyecto
        self.instance.concluido = False  # ✅ Establecer por defecto como False

    def clean_fase(self):
        """Validar que el nombre de la fase sea único dentro del proyecto"""
        nombre_fase = self.cleaned_data.get('fase')
        
        if not nombre_fase:
            raise forms.ValidationError('El nombre de la fase es obligatorio.')
        
        # Verificar si ya existe una fase con ese nombre en el mismo proyecto
        if Fase.objects.filter(proyecto=self.proyecto, fase__iexact=nombre_fase).exists():
            raise forms.ValidationError(
                f'Ya existe una fase llamada "{nombre_fase}" en este proyecto. '
                'Por favor, elige otro nombre.'
            )
        
        return nombre_fase

class RelacionarDocumentoForm(forms.ModelForm):
    class Meta:
        model = RelacionDocumento
        fields = ['documento', 'fase']
        widgets = {
            'documento': forms.Select(attrs={'class': 'form-control'}),
            'fase': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'documento': 'Selecciona el documento',
            'fase': 'Selecciona la fase',
        }

    def __init__(self, usuario=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if usuario:
            # Obtener solo proyectos donde el usuario es recurso humano
            proyectos_usuario = Proyecto.objects.filter(
                recursos_humanos__usuario=usuario
            )
            
            # Filtrar solo documentos de los proyectos del usuario
            self.fields['documento'].queryset = Documento.objects.filter(
                proyecto__in=proyectos_usuario
            )
            
            # MEJORAR LA VISUALIZACIÓN DE DOCUMENTOS
            self.fields['documento'].label_from_instance = lambda obj: f"Doc #{obj.id} - {obj.descripcion[:50]}"
            
            # ✅ MODIFICAR: Filtrar solo fases NO concluidas Y que no tengan relación concluida
            fases_disponibles = Fase.objects.filter(
                proyecto__in=proyectos_usuario,
                concluido=False  # Solo fases activas
            )
            
            self.fields['fase'].queryset = fases_disponibles
            
            # MEJORAR LA VISUALIZACIÓN DE FASES
            self.fields['fase'].label_from_instance = lambda obj: f"{obj.proyecto.nombre_proyecto} - {obj.fase}"
        else:
            # Si no hay usuario, no mostrar nada
            self.fields['documento'].queryset = Documento.objects.none()
            self.fields['fase'].queryset = Fase.objects.none()
        
        # Cambiar los labels
        self.fields['documento'].empty_label = "Seleccione un documento"
        self.fields['fase'].empty_label = "Seleccione una fase"
    
    def clean(self):
        """Validación adicional para evitar duplicados y fases concluidas"""
        cleaned_data = super().clean()
        documento = cleaned_data.get('documento')
        fase = cleaned_data.get('fase')
        
        if documento and fase:
            # ✅ VALIDAR: Verificar si ya existe una relación
            relacion_existente = RelacionDocumento.objects.filter(
                documento=documento,
                fase=fase
            ).first()
            
            if relacion_existente:
                # Si existe y está concluida, no permitir
                if relacion_existente.concluido:
                    raise forms.ValidationError(
                        'Este entregable ya fue aprobado y concluido. No se pueden hacer más cambios.'
                    )
                else:
                    raise forms.ValidationError(
                        'Este documento ya está relacionado con esta fase.'
                    )
            
            # ✅ VALIDAR: Verificar si la fase está concluida
            if fase.concluido:
                raise forms.ValidationError(
                    'No puedes subir entregables a una fase que ya está concluida.'
                )
        
        return cleaned_data
    class Meta:
        model = RelacionDocumento
        fields = ['documento', 'fase']
        widgets = {
            'documento': forms.Select(attrs={'class': 'form-control'}),
            'fase': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'documento': 'Selecciona el documento',
            'fase': 'Selecciona la fase',
        }

    def __init__(self, usuario=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if usuario:
            # Obtener solo proyectos donde el usuario es recurso humano
            proyectos_usuario = Proyecto.objects.filter(
                recursos_humanos__usuario=usuario
            )
            
            # Filtrar solo documentos de los proyectos del usuario
            self.fields['documento'].queryset = Documento.objects.filter(
                proyecto__in=proyectos_usuario
            )
            
            # ✅ MEJORAR LA VISUALIZACIÓN DE DOCUMENTOS
            self.fields['documento'].label_from_instance = lambda obj: f"Doc #{obj.id} - {obj.descripcion[:50]}"
            
            # Filtrar solo fases NO concluidas de los proyectos del usuario
            self.fields['fase'].queryset = Fase.objects.filter(
                proyecto__in=proyectos_usuario,
                concluido=False
            )
            
            # ✅ MEJORAR LA VISUALIZACIÓN DE FASES
            self.fields['fase'].label_from_instance = lambda obj: f"{obj.proyecto.nombre_proyecto} - {obj.fase}"
        else:
            # Si no hay usuario, no mostrar nada
            self.fields['documento'].queryset = Documento.objects.none()
            self.fields['fase'].queryset = Fase.objects.none()
        
        # Cambiar los labels
        self.fields['documento'].empty_label = "Seleccione un documento"
        self.fields['fase'].empty_label = "Seleccione una fase"


class AgregarTareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ['fase', 'recurso_humano', 'descripcion', 'fecha_limite']
        widgets = {
            'fase': forms.Select(attrs={'class': 'form-control'}),
            'recurso_humano': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe la tarea o actividad a realizar'}),
            'fecha_limite': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        labels = {
            'fase': 'Fase del proyecto (solo fases activas)',
            'recurso_humano': 'Asignar a recurso humano',
            'descripcion': 'Descripción de la tarea',
            'fecha_limite': 'Fecha límite',
        }

    def __init__(self, proyecto, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.proyecto = proyecto
        self.proyecto = proyecto
        
        # Filtrar solo fases NO concluidas
        self.fields['fase'].queryset = Fase.objects.filter(
            proyecto=proyecto,
            concluido=False
        )
        
        self.fields['recurso_humano'].queryset = RecursoHumano.objects.filter(proyecto=proyecto)
        
        self.fields['recurso_humano'].label_from_instance = lambda obj: f"{obj.usuario.nombre_usuario} ({obj.usuario.correo})"
        self.fields['fase'].label_from_instance = lambda obj: f"{obj.fase} (Activa)"
    
    def clean_fecha_limite(self):
        """Validar fecha límite contra fecha de inicio del proyecto y fecha actual"""
        fecha_limite = self.cleaned_data.get('fecha_limite')
        from datetime import date
        
        # ✅ Validación 1: No puede ser anterior a hoy
        if fecha_limite < date.today():
            raise forms.ValidationError(
                f'❌ La fecha límite no puede ser anterior a hoy ({date.today().strftime("%d/%m/%Y")}). '
                f'Fecha ingresada: {fecha_limite.strftime("%d/%m/%Y")}'
            )
        
        # ✅ Validación 2: No puede ser anterior a la fecha de inicio del proyecto
        if fecha_limite < self.proyecto.fecha_inicio:
            raise forms.ValidationError(
                f'❌ La fecha límite ({fecha_limite.strftime("%d/%m/%Y")}) no puede ser anterior '
                f'a la fecha de inicio del proyecto ({self.proyecto.fecha_inicio.strftime("%d/%m/%Y")}). '
                f'Por favor, elige una fecha posterior al inicio del proyecto.'
            )
        
        # ✅ Validación 3 (Opcional): Advertir si es posterior a la fecha final del proyecto
        if fecha_limite > self.proyecto.fecha_final:
            raise forms.ValidationError(
                f'⚠️ La fecha límite ({fecha_limite.strftime("%d/%m/%Y")}) es posterior '
                f'a la fecha final del proyecto ({self.proyecto.fecha_final.strftime("%d/%m/%Y")}). '
                f'Verifica que la tarea se pueda completar dentro del plazo del proyecto.'
            )
        
        return fecha_limite
    
    def clean_fase(self):
        """Validar que no se asignen tareas a fases concluidas"""
        fase = self.cleaned_data.get('fase')
        if fase and fase.concluido:
            raise forms.ValidationError('❌ No se pueden asignar tareas a fases concluidas.')
        return fase
        