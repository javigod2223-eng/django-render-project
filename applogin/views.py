from django.http import HttpResponse
from .models import Rol, Usuario, Proyecto, Impacto, RecursoMaterial, RecursoHumano, Documento, Fase, Riesgo,RelacionDocumento, Tarea
from .forms import RelacionarDocumentoForm, RolForm, LoginForm,ProyectoForm,UsuarioForm,AsignarRecursoHumanoForm, AgregarRecursoMaterialForm, AgregarDocumentoForm, AgregarRiesgoForm, AgregarFaseForm,ProyectoEditarForm,InsertarUsuarioForm, AgregarTareaForm
from django.core.exceptions import ValidationError
from django.shortcuts import render,redirect,get_object_or_404
from django.views.decorators.http import require_POST,require_GET
from django.contrib.auth.decorators import login_required
from .forms import ProyectoForm
from django.http import JsonResponse
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from datetime import date, timedelta
from .forms import InsertarUsuarioForm
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import date
# Create your views here.

def hello(request):
    return HttpResponse("Hola mundo")
def mi_vista(request):
    return render(request, 'applogin/index.html')

def mostrar_base_datos(request):
    roles = Rol.objects.all()
    usuarios = Usuario.objects.all()
    proyectos = Proyecto.objects.all()
    impactos = Impacto.objects.all()
    recursos_materiales = RecursoMaterial.objects.all()
    recursos_humanos = RecursoHumano.objects.all()
    documentos = Documento.objects.all()
    fases = Fase.objects.all()
    riesgos = Riesgo.objects.all()

    context = {
        'roles': roles,
        'usuarios': usuarios,
        'proyectos': proyectos,
        'impactos': impactos,
        'recursos_materiales': recursos_materiales,
        'recursos_humanos': recursos_humanos,
        'documentos': documentos,
        'fases': fases,
        'riesgos': riesgos,
    }
    return render(request, 'applogin/mostrar_base_datos.html', context)

def agregar_rol(request):
    if request.method == 'POST':
        rol_form = RolForm(request.POST)
        if rol_form.is_valid():
            rol_form.save()  # Guardar el formulario si es válido
            return redirect('mostrar_base_datos')  # Redirigir a una página de éxito o a la lista de roles
    else:
        rol_form = RolForm()  # Crear una instancia de RolForm vacía para mostrar el formulario

    return render(request, 'applogin/AgregarRol.html', {'rol_form': rol_form})
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                usuario = Usuario.objects.get(correo=email)
                if password == usuario.contrasena:
                    # Autenticación exitosa
                    request.session['usuario_id'] = usuario.id
                    request.session['usuario_nombre'] = usuario.nombre_usuario
                    request.session['usuario_rol'] = usuario.rol.nombre_rol
                    if usuario.rol.nombre_rol == 'Administrador':
                        return redirect('admin_dashboard')
                    else:
                        return redirect('admin_dashboard')
                else:
                    form.add_error('password', 'Contraseña incorrecta')
            except Usuario.DoesNotExist:
                form.add_error('email', 'Correo electrónico no registrado')
    else:
        form = LoginForm()

    return render(request, 'applogin/login.html', {'form': form})

from django.db.models import Q

def admin_dashboard(request):
    if request.session.get('usuario_rol') != 'Administrador':
        return redirect('login')

    usuarios = Usuario.objects.all()
    
    # ✅ Filtrar proyectos por administrador actual
    usuario_id = request.session.get('usuario_id')
    usuario_actual = Usuario.objects.get(id=usuario_id)

    # Mostrar solo los proyectos donde el usuario actual es el admin_proyecto_usuario
    proyectos = Proyecto.objects.filter(
    admin_proyecto_usuario=usuario_actual
    ).order_by('-id')

    # Obtener el término de búsqueda
    query = request.GET.get('q')
    if query:
        proyectos = proyectos.filter(
            Q(nombre_proyecto__icontains=query) |
            Q(estado__icontains=query) |
            Q(admin_proyecto_usuario__nombre_usuario__icontains=query)
        )

    # Paginación
    paginator = Paginator(proyectos, 5)  # 5 proyectos por página
    page = request.GET.get('page')
    try:
        proyectos_paginados = paginator.page(page)
    except PageNotAnInteger:
        proyectos_paginados = paginator.page(1)
    except EmptyPage:
        proyectos_paginados = paginator.page(paginator.num_pages)
    roles = Rol.objects.exclude(nombre_rol='Administrador').order_by('nombre_rol')
    contexto = {
        'usuario_nombre': request.session.get('usuario_nombre'),
        'usuario_rol': request.session.get('usuario_rol'),
        'usuarios': usuarios,
        'proyectos': proyectos_paginados,
        'form': ProyectoForm(),
        'form_usuario': InsertarUsuarioForm(),
        'roles': roles,  # ✅ AGREGAR ESTA LÍNEA
    }
    return render(request, 'MenusAdmins/admin_dashboard.html', contexto)


def insertar_usuario(request):
    if request.method == 'POST':
        form = InsertarUsuarioForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo']
            nombre_usuario = form.cleaned_data['nombre_usuario']
            contrasena = form.cleaned_data['contrasena']
            rol = form.cleaned_data['rol']
            
            usuario_existente = Usuario.objects.filter(correo=correo).first()
            
            # Función auxiliar para enviar correo
            def enviar_correo_credenciales(usuario, contrasena, es_nuevo=True):
                try:
                    from django.core.mail import send_mail
                    from django.conf import settings
                    
                    if es_nuevo:
                        asunto = '🎉 Bienvenido al Sistema Plannerio'
                        mensaje = f"""
¡Hola {usuario.nombre_usuario}!

Te damos la bienvenida al Sistema de Gestión de Proyectos Plannerio.

Tus credenciales de acceso son:

📧 Correo: {usuario.correo}
🔑 Contraseña: {contrasena}
👤 Rol: {usuario.rol.nombre_rol}

Puedes iniciar sesión en: https://planneiro.onrender.com

IMPORTANTE: Guarda estas credenciales en un lugar seguro, ya que no podrás cambiar tu contraseña.

---
Sistema de Gestión de Proyectos Plannerio
                        """
                    else:
                        asunto = '🔐 Actualización de credenciales - Sistema Plannerio'
                        mensaje = f"""
Hola {usuario.nombre_usuario},

Tus credenciales de acceso han sido actualizadas en el Sistema Plannerio.

📧 Correo: {usuario.correo}
🔑 Nueva contraseña: {contrasena}
👤 Rol: {usuario.rol.nombre_rol}

Puedes iniciar sesión en: https://planneiro.onrender.com

IMPORTANTE: Guarda estas credenciales en un lugar seguro, ya que no podrás cambiar tu contraseña.

---
Sistema de Gestión de Proyectos Plannerio
                        """
                    
                    send_mail(
                        asunto,
                        mensaje,
                        settings.DEFAULT_FROM_EMAIL,
                        [usuario.correo],
                        fail_silently=False,
                    )
                    return True
                except Exception as e:
                    print(f"Error al enviar correo: {str(e)}")
                    return False
            
            if usuario_existente:
                # Actualizar usuario existente
                usuario_existente.rol = rol
                usuario_existente.nombre_usuario = nombre_usuario
                
                # Solo actualizar contraseña si se proporcionó una nueva
                if contrasena:
                    usuario_existente.contrasena = contrasena
                    usuario_existente.save()
                    
                    # Enviar correo con nueva contraseña
                    if enviar_correo_credenciales(usuario_existente, contrasena, es_nuevo=False):
                        messages.success(request, f'✅ Usuario "{usuario_existente.nombre_usuario}" actualizado y correo enviado exitosamente.')
                    else:
                        messages.warning(request, f'✅ Usuario actualizado, pero hubo un error al enviar el correo.')
                else:
                    usuario_existente.save()
                    messages.success(request, f'✅ Usuario "{usuario_existente.nombre_usuario}" actualizado correctamente.')
            else:
                # Insertar nuevo usuario
                nuevo_usuario = form.save()
                
                # Enviar correo de bienvenida
                if enviar_correo_credenciales(nuevo_usuario, contrasena, es_nuevo=True):
                    messages.success(request, f'✅ Recurso humano "{nuevo_usuario.nombre_usuario}" creado exitosamente y correo enviado.')
                else:
                    messages.warning(request, f'✅ Usuario creado, pero hubo un error al enviar el correo.')
            
            return redirect('gestion_recursos_humanos')
        else:
            # Mostrar errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'❌ {error}')
            return redirect('gestion_recursos_humanos')
    
    return redirect('gestion_recursos_humanos')

def user_dashboard(request):
    if request.session.get('usuario_rol') != 'Usuario':
        return redirect('login')

    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.get(pk=usuario_id)

    # Obtener proyectos y tareas
    proyectos = Proyecto.objects.filter(recursos_humanos__usuario=usuario)
    recursos_humanos = RecursoHumano.objects.filter(usuario=usuario)
    tareas = Tarea.objects.filter(
        recurso_humano__in=recursos_humanos
    ).select_related('proyecto', 'fase', 'documento_entregable').order_by('fecha_limite', 'estado')
    
    tareas_pendientes = tareas.filter(estado='Pendiente').count()
    tareas_vencidas = tareas.filter(estado__in=['Pendiente', 'En Progreso']).filter(fecha_limite__lt=date.today()).count()

    # Búsqueda
    query = request.GET.get('q')
    if query:
        proyectos = proyectos.filter(Q(nombre_proyecto__icontains=query))

    # Procesar formulario de subir entregable
    if request.method == 'POST':
        tarea_id = request.POST.get('tarea_id')
        proyecto_id = request.POST.get('proyecto')
        descripcion = request.POST.get('descripcion')
        url_documento = request.POST.get('url_documento')
        archivo_documento = request.FILES.get('archivo_documento')
        
        print("=== DEBUG SUBIR ENTREGABLE ===")
        print(f"Tarea ID: {tarea_id}")
        print(f"Proyecto ID: {proyecto_id}")
        print(f"Descripción: {descripcion}")
        print(f"URL: {url_documento}")
        print(f"Archivo: {archivo_documento}")
        
        # Validar que tenga al menos URL o archivo
        if not url_documento and not archivo_documento:
            messages.error(request, 'Debes proporcionar una URL o subir un archivo PDF.')
            return redirect('user_dashboard')
        
        try:
            proyecto = Proyecto.objects.get(id=proyecto_id)
    
    # ✅ Crear instancia sin guardar
            documento = Documento(
                proyecto=proyecto,
                descripcion=descripcion,
                url_documento=url_documento if url_documento else None,
            )
    
    # ✅ Asignar archivo si existe
            if archivo_documento:
                documento.archivo_documento = archivo_documento
    
    # ✅ PRIMERO: Guardar el documento (esto activa Cloudinary)
            documento.save()
    
    # ✅ DESPUÉS: Asociar a la tarea y marcar como completada
            if tarea_id:
                tarea = Tarea.objects.get(id=tarea_id)
                tarea.documento_entregable = documento  # Ahora sí existe el documento
                tarea.estado = 'Completada'
                tarea.save()
        
                print(f"Tarea {tarea_id} marcada como completada")
                messages.success(request, f'✅ Entregable subido exitosamente y tarea completada.')
            else:
                messages.success(request, 'Entregable subido exitosamente.')
    
            return redirect('user_dashboard')
    
        except Exception as e:
            messages.error(request, f'Error al subir el entregable: {str(e)}')
            print(f"ERROR: {str(e)}")
            return redirect('user_dashboard')

    contexto = {
        'usuario_nombre': request.session.get('usuario_nombre'),
        'usuario_rol': request.session.get('usuario_rol'),
        'proyectos': proyectos,
        'tareas': tareas,
        'tareas_pendientes': tareas_pendientes,
        'tareas_vencidas': tareas_vencidas,
    }
    return render(request, 'MenusUsuarios/user_dashboard.html', contexto)

@require_GET
def logout_view(request):
    if 'usuario_id' in request.session:
        del request.session['usuario_id']
    if 'usuario_nombre' in request.session:
        del request.session['usuario_nombre']
    if 'usuario_rol' in request.session:
        del request.session['usuario_rol']
    return redirect('login')

def agregar_proyecto(request):
    print("=" * 50)
    print("🔥 VISTA AGREGAR_PROYECTO LLAMADA")
    print(f"Método: {request.method}")
    print("=" * 50)
    
    if request.method == 'POST':
        print(f"📝 POST data recibido: {request.POST}")
        
        form = ProyectoForm(request.POST)
        
        print(f"Form válido: {form.is_valid()}")
        
        if form.is_valid():
            proyecto = form.save(commit=False)
            
            # ✅ Si no se especificó admin, asignar al usuario actual
            if not proyecto.admin_proyecto_usuario_id:
                usuario_id = request.session.get('usuario_id')
                proyecto.admin_proyecto_usuario_id = usuario_id
            
            # Asignar estado manualmente
            if not proyecto.estado:
                proyecto.estado = 'En proceso'
            
            proyecto.save()
            
            print(f"✅ Proyecto guardado con ID: {proyecto.id}")
            print(f"   Nombre: {proyecto.nombre_proyecto}")
            print(f"   Admin: {proyecto.admin_proyecto_usuario.nombre_usuario}")
            print(f"   Estado: {proyecto.estado}")
            
            messages.success(request, f'✅ Proyecto "{proyecto.nombre_proyecto}" creado exitosamente.')
            return redirect('admin_dashboard')
        else:
            print(f"❌ Errores del formulario: {form.errors}")
            for field, errors in form.errors.items():
                print(f"   Campo '{field}': {errors}")
            
            # Filtrar proyectos del usuario actual
            usuario_id = request.session.get('usuario_id')
            usuario_actual = Usuario.objects.get(id=usuario_id)
            
            return render(request, 'MenusAdmins/admin_dashboard.html', {
                'form': form,
                'mostrar_modal': True,
                'proyectos': Proyecto.objects.filter(
                    admin_proyecto_usuario=usuario_actual
                ).order_by('-id')[:5],
                'usuarios': Usuario.objects.all(),
                'form_usuario': InsertarUsuarioForm(),
                'usuario_nombre': request.session.get('usuario_nombre'),
                'usuario_rol': request.session.get('usuario_rol'),
            })
    
    # Si es método GET, redirigir al dashboard
    return redirect('admin_dashboard')

def detalles_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    impactos = Impacto.objects.filter(proyecto=proyecto)
    recursos_materiales = RecursoMaterial.objects.filter(proyecto=proyecto)
    recursos_humanos = RecursoHumano.objects.filter(proyecto=proyecto)
    documentos = Documento.objects.filter(proyecto=proyecto)
    fases = Fase.objects.filter(proyecto=proyecto)
    riesgos = Riesgo.objects.filter(proyecto=proyecto)
    relaciones_documento = RelacionDocumento.objects.filter(fase__proyecto=proyecto).select_related('documento', 'fase')
    tareas = Tarea.objects.filter(proyecto=proyecto).select_related('fase', 'recurso_humano__usuario', 'documento_entregable')  # ✅ AGREGAR
    
    # Inicialización de los formularios con el contexto del proyecto
    agregar_recurso_material_form = AgregarRecursoMaterialForm(proyecto, request.POST or None)
    asignar_recurso_humano_form = AsignarRecursoHumanoForm(proyecto, request.POST or None)
    agregar_documento_form = AgregarDocumentoForm(proyecto, request.POST or None)
    agregar_riesgo_form = AgregarRiesgoForm(proyecto, request.POST or None)
    agregar_fase_form = AgregarFaseForm(proyecto, request.POST or None)
    agregar_tarea_form = AgregarTareaForm(proyecto, request.POST or None)  # ✅ AGREGAR
    editar_proyecto_form = ProyectoEditarForm(instance=proyecto)

    contexto = {
        'proyecto': proyecto,
        'impactos': impactos,
        'recursos_materiales': recursos_materiales,
        'recursos_humanos': recursos_humanos,
        'documentos': documentos,
        'fases': fases,
        'relaciones_documento': relaciones_documento,
        'riesgos': riesgos,
        'tareas': tareas,  # ✅ AGREGAR
        'agregar_recurso_material_form': agregar_recurso_material_form,
        'asignar_recurso_humano_form': asignar_recurso_humano_form,
        'agregar_documento_form': agregar_documento_form,
        'agregar_riesgo_form': agregar_riesgo_form,
        'agregar_fase_form': agregar_fase_form,
        'agregar_tarea_form': agregar_tarea_form,  # ✅ AGREGAR
        'form': editar_proyecto_form,
    }

    return render(request, 'MenusAdmins/detallesproyecto.html', contexto)

def registrar_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()  # Guardar el formulario si es válido
            return redirect('inicio')  # Redireccionar a la página de inicio u otra página deseada después de guardar
    else:
        form = UsuarioForm()

    return render(request, 'MenusAdmins/Modales/AddRecursoHumano.html', {'form': form})

def asignar_recurso_humano(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    if request.method == 'POST':
        form = AsignarRecursoHumanoForm(proyecto, request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, '✅ Recurso humano asignado exitosamente.')
                return redirect('detalles_proyecto', proyecto_id=proyecto_id)
            except ValidationError as e:
                messages.error(request, f'❌ {str(e)}')
        else:
            # Mostrar errores específicos
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'❌ {error}')
        
        # Regresar con el formulario que tiene errores
        return render(request, 'MenusAdmins/detallesproyecto.html', {
            'proyecto': proyecto,
            'asignar_recurso_humano_form': form,
            'mostrar_modal_recurso_humano': True,  # ✅ Para reabrir el modal
            # Agregar todos los demás contextos necesarios
            'impactos': Impacto.objects.filter(proyecto=proyecto),
            'recursos_materiales': RecursoMaterial.objects.filter(proyecto=proyecto),
            'recursos_humanos': RecursoHumano.objects.filter(proyecto=proyecto),
            'documentos': Documento.objects.filter(proyecto=proyecto),
            'fases': Fase.objects.filter(proyecto=proyecto),
            'riesgos': Riesgo.objects.filter(proyecto=proyecto),
            'relaciones_documento': RelacionDocumento.objects.filter(fase__proyecto=proyecto),
            'tareas': Tarea.objects.filter(proyecto=proyecto),
            'agregar_recurso_material_form': AgregarRecursoMaterialForm(proyecto),
            'agregar_documento_form': AgregarDocumentoForm(proyecto),
            'agregar_riesgo_form': AgregarRiesgoForm(proyecto),
            'agregar_fase_form': AgregarFaseForm(proyecto),
            'agregar_tarea_form': AgregarTareaForm(proyecto),
            'form': ProyectoEditarForm(instance=proyecto),
        })
    else:
        form = AsignarRecursoHumanoForm(proyecto)
    
    return render(request, 'MenusAdmins/detallesproyecto.html', {
        'proyecto': proyecto,
        'asignar_recurso_humano_form': form,
    })

def agregar_recurso_material(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    if request.method == 'POST':
        form = AgregarRecursoMaterialForm(proyecto, request.POST)
        if form.is_valid():
            form.save()
            return redirect('detalles_proyecto', proyecto_id=proyecto_id)
    else:
        form = AgregarRecursoMaterialForm(proyecto)
    
    return render(request, 'MenusAdmins/detallesproyecto.html', {'form': form})

def agregar_documento(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)

    if request.method == 'POST':
        # 🔹 Validar el tamaño del archivo ANTES de procesar el formulario
        archivo = request.FILES.get('archivo_documento')
        if archivo and archivo.size > 15 * 1024 * 1024:
            messages.error(request, "❌ El archivo no puede superar los 15 MB.")
            return redirect(request.path_info)

        # 🔹 Aquí sí se deben pasar los archivos al formulario
        form = AgregarDocumentoForm(proyecto, request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Documento agregado correctamente.")
            return redirect('detalles_proyecto', proyecto_id=proyecto_id)
        else:
            messages.error(request, "⚠️ Revisa los errores en el formulario.")
    else:
        form = AgregarDocumentoForm(proyecto)

    return render(request, 'MenusAdmins/detallesproyecto.html', {'form': form})


def agregar_riesgo(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    if request.method == 'POST':
        form = AgregarRiesgoForm(proyecto, request.POST)
        if form.is_valid():
            form.save()
            return redirect('detalles_proyecto', proyecto_id=proyecto_id)
    else:
        form = AgregarRiesgoForm(proyecto)
    
    return render(request, 'MenusAdmins/detallesproyecto.html', {'form': form})

def agregar_fase(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    if request.method == 'POST':
        form = AgregarFaseForm(proyecto, request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Fase "{form.cleaned_data["fase"]}" agregada exitosamente.')
            return redirect('detalles_proyecto', proyecto_id=proyecto_id)
        else:
            # Si hay errores, mostrar mensajes y reabrir el modal
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'❌ {error}')
            
            # Renderizar la página con el formulario que contiene errores
            return render(request, 'MenusAdmins/detallesproyecto.html', {
                'proyecto': proyecto,
                'agregar_fase_form': form,  # ✅ Pasar el formulario con errores
                'mostrar_modal_fase': True,  # ✅ Flag para reabrir el modal
                # Pasar todos los demás contextos necesarios
                'impactos': Impacto.objects.filter(proyecto=proyecto),
                'recursos_materiales': RecursoMaterial.objects.filter(proyecto=proyecto),
                'recursos_humanos': RecursoHumano.objects.filter(proyecto=proyecto),
                'documentos': Documento.objects.filter(proyecto=proyecto),
                'fases': Fase.objects.filter(proyecto=proyecto),
                'riesgos': Riesgo.objects.filter(proyecto=proyecto),
                'relaciones_documento': RelacionDocumento.objects.filter(fase__proyecto=proyecto),
                'tareas': Tarea.objects.filter(proyecto=proyecto),
                'agregar_recurso_material_form': AgregarRecursoMaterialForm(proyecto),
                'asignar_recurso_humano_form': AsignarRecursoHumanoForm(proyecto),
                'agregar_documento_form': AgregarDocumentoForm(proyecto),
                'agregar_riesgo_form': AgregarRiesgoForm(proyecto),
                'agregar_tarea_form': AgregarTareaForm(proyecto),
                'form': ProyectoEditarForm(instance=proyecto),
            })
    
    return redirect('detalles_proyecto', proyecto_id=proyecto_id)

def agregar_tarea(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    if request.method == 'POST':
        form = AgregarTareaForm(proyecto, request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Tarea creada y asignada exitosamente.')
            return redirect('detalles_proyecto', proyecto_id=proyecto_id)
        else:
            # Mostrar errores específicos
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'❌ {error}')
            
            # Renderizar con el formulario que contiene errores
            return render(request, 'MenusAdmins/detallesproyecto.html', {
                'proyecto': proyecto,
                'agregar_tarea_form': form,  # ✅ Formulario con errores
                'mostrar_modal_tarea': True,  # ✅ Flag para reabrir modal
                # Pasar todos los demás contextos
                'impactos': Impacto.objects.filter(proyecto=proyecto),
                'recursos_materiales': RecursoMaterial.objects.filter(proyecto=proyecto),
                'recursos_humanos': RecursoHumano.objects.filter(proyecto=proyecto),
                'documentos': Documento.objects.filter(proyecto=proyecto),
                'fases': Fase.objects.filter(proyecto=proyecto),
                'riesgos': Riesgo.objects.filter(proyecto=proyecto),
                'relaciones_documento': RelacionDocumento.objects.filter(fase__proyecto=proyecto),
                'tareas': Tarea.objects.filter(proyecto=proyecto),
                'agregar_recurso_material_form': AgregarRecursoMaterialForm(proyecto),
                'asignar_recurso_humano_form': AsignarRecursoHumanoForm(proyecto),
                'agregar_documento_form': AgregarDocumentoForm(proyecto),
                'agregar_riesgo_form': AgregarRiesgoForm(proyecto),
                'agregar_fase_form': AgregarFaseForm(proyecto),
                'form': ProyectoEditarForm(instance=proyecto),
            })
    
    return redirect('detalles_proyecto', proyecto_id=proyecto_id)

def marcar_entregable_concluido(request, relacion_id):
    print(f"=== ENTRANDO A marcar_entregable_concluido ===")
    print(f"Método: {request.method}")
    
    relacion = get_object_or_404(RelacionDocumento, id=relacion_id)
    proyecto_id = relacion.fase.proyecto.id
    
    print(f"Proyecto ID: {proyecto_id}")
    
    if request.method == 'POST':
        relacion.concluido = True
        from django.utils import timezone
        relacion.fecha_conclusion = timezone.now()
        relacion.save()
        
        print(f"Guardado. Concluido: {relacion.concluido}")
        messages.success(request, 'Entregable aprobado exitosamente.')
        
    print(f"Redirigiendo a detalles_proyecto/{proyecto_id}")
    return redirect('detalles_proyecto', proyecto_id=proyecto_id)

def desmarcar_entregable_concluido(request, relacion_id):
    print(f"=== ENTRANDO A desmarcar_entregable_concluido ===")
    
    relacion = get_object_or_404(RelacionDocumento, id=relacion_id)
    proyecto_id = relacion.fase.proyecto.id
    
    if request.method == 'POST':
        relacion.concluido = False
        relacion.fecha_conclusion = None
        relacion.save()
        messages.success(request, 'Entregable desmarcado.')
    
    return redirect('detalles_proyecto', proyecto_id=proyecto_id)

def marcar_fase_concluida(request, fase_id):
    print(f"=== ENTRANDO A marcar_fase_concluida ===")
    
    fase = get_object_or_404(Fase, id=fase_id)
    proyecto_id = fase.proyecto.id
    
    if request.method == 'POST':
        fase.concluido = True
        fase.save()
        messages.success(request, f'Fase "{fase.fase}" marcada como concluida.')
    
    return redirect('detalles_proyecto', proyecto_id=proyecto_id)

def desmarcar_fase_concluida(request, fase_id):
    print(f"=== ENTRANDO A desmarcar_fase_concluida ===")
    
    fase = get_object_or_404(Fase, id=fase_id)
    proyecto_id = fase.proyecto.id
    
    if request.method == 'POST':
        fase.concluido = False
        fase.save()
        messages.success(request, f'Fase "{fase.fase}" reactivada.')
    
    return redirect('detalles_proyecto', proyecto_id=proyecto_id)

def editar_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    if request.method == 'POST':
        form = ProyectoEditarForm(request.POST, instance=proyecto)
        if form.is_valid():
            form.save()
            return redirect('detalles_proyecto', proyecto_id=proyecto_id)
    else:
        form = ProyectoEditarForm(instance=proyecto)
    
    context = {
        'form': form,
        'proyecto': proyecto,
    }
    return render(request, 'MenusAdmins/editarproyecto.html', context)


from django.shortcuts import render, redirect
from django.contrib import messages
from .prioridad import actualizar_prioridad_proyecto, actualizar_todas_las_prioridades, obtener_proyectos_priorizados
from .models import Proyecto


def actualizar_prioridades_view(request):
    """
    Vista para actualizar manualmente las prioridades de todos los proyectos
    """
    if request.method == 'POST':
        resultados = actualizar_todas_las_prioridades()
        messages.success(request, f'Se actualizaron las prioridades de {len(resultados)} proyectos.')
        return redirect('dashboard_prioridades')
    
    return redirect('dashboard_prioridades')


def dashboard_prioridades(request):
    """
    Vista del dashboard que muestra proyectos ordenados por prioridad
    """
    # Actualizar prioridades automáticamente al cargar el dashboard
    actualizar_todas_las_prioridades()
    
    # Obtener proyectos ordenados por prioridad
    proyectos = obtener_proyectos_priorizados()
    
    # Separar por nivel de prioridad
    proyectos_criticos = proyectos.filter(prioridad_nivel='Crítica')
    proyectos_altos = proyectos.filter(prioridad_nivel='Alta')
    proyectos_medios = proyectos.filter(prioridad_nivel='Media')
    proyectos_bajos = proyectos.filter(prioridad_nivel='Baja')
    
    context = {
        'proyectos': proyectos,
        'proyectos_criticos': proyectos_criticos,
        'proyectos_altos': proyectos_altos,
        'proyectos_medios': proyectos_medios,
        'proyectos_bajos': proyectos_bajos,
        'total_proyectos': proyectos.count(),
    }
    
    return render(request, 'MenusAdmins/dashboard_prioridades.html', context)


def detalle_prioridad_proyecto(request, proyecto_id):
    """
    Vista para ver detalles de prioridad de un proyecto específico
    """
    from .prioridad import AlgoritmoPrioridad
    
    proyecto = Proyecto.objects.get(id=proyecto_id)
    resultado = AlgoritmoPrioridad.calcular_prioridad(proyecto)
    
    context = {
        'proyecto': proyecto,
        'score': resultado['score'],
        'nivel': resultado['nivel'],
        'detalles': resultado['detalles'],
    }
    
    return render(request, 'MenusAdmins/detalle_prioridad.html', context)

def eliminar_proyecto(request, proyecto_id):
    """
    Vista para eliminar un proyecto
    """
    if request.method == 'POST':
        try:
            proyecto = Proyecto.objects.get(id=proyecto_id)
            nombre_proyecto = proyecto.nombre_proyecto
            proyecto.delete()
            messages.success(request, f'El proyecto "{nombre_proyecto}" ha sido eliminado exitosamente.')
            return redirect('admin_dashboard')
        except Proyecto.DoesNotExist:
            messages.error(request, 'El proyecto no existe.')
            return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, f'Error al eliminar el proyecto: {str(e)}')
            return redirect('detalles_proyecto', proyecto_id=proyecto_id)
    
    return redirect('detalles_proyecto', proyecto_id=proyecto_id)

def verificar_nombre_proyecto(request):
    """Vista AJAX para verificar si un nombre de proyecto ya existe"""
    if request.method == 'GET':
        nombre = request.GET.get('nombre', '').strip()
        proyecto_id = request.GET.get('proyecto_id', None)  # Para edición
        
        if not nombre:
            return JsonResponse({'existe': False})
        
        # Buscar proyectos con ese nombre
        if proyecto_id:
            # Si es edición, excluir el proyecto actual
            existe = Proyecto.objects.filter(nombre_proyecto__iexact=nombre).exclude(id=proyecto_id).exists()
        else:
            existe = Proyecto.objects.filter(nombre_proyecto__iexact=nombre).exists()
        
        return JsonResponse({'existe': existe, 'nombre': nombre})
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def verificar_disponibilidad_usuario(request):
    """Vista AJAX para verificar si un usuario puede ser asignado a más proyectos"""
    if request.method == 'GET':
        usuario_id = request.GET.get('usuario_id', '')
        proyecto_id = request.GET.get('proyecto_id', '')
        
        if not usuario_id:
            return JsonResponse({'disponible': True})
        
        try:
            usuario = Usuario.objects.get(id=usuario_id)
            proyecto = Proyecto.objects.get(id=proyecto_id)
            
            # Verificar si ya está asignado
            if RecursoHumano.objects.filter(proyecto=proyecto, usuario=usuario).exists():
                return JsonResponse({
                    'disponible': False,
                    'mensaje': f'El usuario "{usuario.nombre_usuario}" ya está asignado a este proyecto.'
                })
            
            # Verificar cuántos proyectos tiene
            proyectos_asignados = RecursoHumano.objects.filter(usuario=usuario).count()
            
            if proyectos_asignados >= 2:
                return JsonResponse({
                    'disponible': False,
                    'mensaje': f'El usuario "{usuario.nombre_usuario}" ya tiene el máximo de 2 proyectos asignados. No se pueden asignar más proyectos.'
                })
            
            return JsonResponse({
                'disponible': True,
                'mensaje': f'✓ Usuario disponible ({proyectos_asignados}/2 proyectos asignados)'
            })
            
        except (Usuario.DoesNotExist, Proyecto.DoesNotExist):
            return JsonResponse({'disponible': True})
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def finalizar_proyecto(request, proyecto_id):
    """Vista para finalizar un proyecto y liberar recursos humanos"""
    if request.method == 'POST':
        try:
            proyecto = Proyecto.objects.get(id=proyecto_id)
            
            # Verificar que no esté ya finalizado
            if proyecto.finalizado:
                messages.warning(request, f'El proyecto "{proyecto.nombre_proyecto}" ya está finalizado.')
                return redirect('detalles_proyecto', proyecto_id=proyecto_id)
            
            # Marcar como finalizado
            proyecto.finalizado = True
            proyecto.estado = 'Finalizado'
            proyecto.porcentaje = 100.0
            from django.utils import timezone
            proyecto.fecha_finalizacion = timezone.now()
            proyecto.save()
            
            # Liberar recursos humanos (eliminarlos del proyecto)
            recursos_liberados = RecursoHumano.objects.filter(proyecto=proyecto)
            cantidad_recursos = recursos_liberados.count()
            recursos_liberados.delete()
            
            messages.success(
                request, 
                f'✅ Proyecto "{proyecto.nombre_proyecto}" finalizado exitosamente. '
                f'Se liberaron {cantidad_recursos} recurso(s) humano(s).'
            )
            
            return redirect('detalles_proyecto', proyecto_id=proyecto_id)
            
        except Proyecto.DoesNotExist:
            messages.error(request, 'El proyecto no existe.')
            return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, f'Error al finalizar el proyecto: {str(e)}')
            return redirect('detalles_proyecto', proyecto_id=proyecto_id)
    
    return redirect('detalles_proyecto', proyecto_id=proyecto_id)

def reactivar_proyecto(request, proyecto_id):
    """Vista para reactivar un proyecto finalizado"""
    if request.method == 'POST':
        try:
            proyecto = Proyecto.objects.get(id=proyecto_id)
            
            if not proyecto.finalizado:
                messages.warning(request, f'El proyecto "{proyecto.nombre_proyecto}" no está finalizado.')
                return redirect('detalles_proyecto', proyecto_id=proyecto_id)
            
            # Reactivar proyecto
            proyecto.finalizado = False
            proyecto.estado = 'En proceso'
            proyecto.fecha_finalizacion = None
            proyecto.save()
            
            messages.success(
                request, 
                f'✅ Proyecto "{proyecto.nombre_proyecto}" reactivado. '
                f'Puedes volver a asignar recursos humanos.'
            )
            
            return redirect('detalles_proyecto', proyecto_id=proyecto_id)
            
        except Proyecto.DoesNotExist:
            messages.error(request, 'El proyecto no existe.')
            return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, f'Error al reactivar el proyecto: {str(e)}')
            return redirect('detalles_proyecto', proyecto_id=proyecto_id)
    
    return redirect('detalles_proyecto', proyecto_id=proyecto_id)

def eliminar_recurso_humano(request, recurso_humano_id):
    """Vista para eliminar un recurso humano de un proyecto"""
    if request.method == 'POST':
        try:
            recurso_humano = RecursoHumano.objects.get(id=recurso_humano_id)
            proyecto_id = recurso_humano.proyecto.id
            nombre_usuario = recurso_humano.usuario.nombre_usuario
            nombre_proyecto = recurso_humano.proyecto.nombre_proyecto
            
            # Eliminar el recurso humano
            recurso_humano.delete()
            
            messages.success(
                request, 
                f'✅ El usuario "{nombre_usuario}" ha sido removido del proyecto "{nombre_proyecto}". '
                f'Ahora tiene un espacio disponible para nuevos proyectos.'
            )
            
            return redirect('detalles_proyecto', proyecto_id=proyecto_id)
            
        except RecursoHumano.DoesNotExist:
            messages.error(request, '❌ El recurso humano no existe.')
            return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, f'❌ Error al eliminar el recurso humano: {str(e)}')
            return redirect('admin_dashboard')
    
    return redirect('admin_dashboard')

def gestion_recursos_humanos(request):
    """Vista para gestionar recursos humanos (crear, editar, listar)"""
    if request.session.get('usuario_rol') != 'Administrador':
        return redirect('login')
    
    # Obtener todos los usuarios que NO son administradores
    usuario_actual_id = request.session.get('usuario_id')
    usuarios = Usuario.objects.exclude(id=usuario_actual_id).order_by('nombre_usuario')
    # Contar proyectos asignados para cada usuario
    usuarios_con_proyectos = []
    for usuario in usuarios:
        proyectos_asignados = RecursoHumano.objects.filter(
            usuario=usuario
        ).exclude(
            proyecto__finalizado=True
        ).count()
        
        usuarios_con_proyectos.append({
            'usuario': usuario,
            'proyectos_asignados': proyectos_asignados
        })
    
    contexto = {
        'usuario_nombre': request.session.get('usuario_nombre'),
        'usuario_rol': request.session.get('usuario_rol'),
        'usuarios_con_proyectos': usuarios_con_proyectos,
        'form_crear': InsertarUsuarioForm(),
        'roles': Rol.objects.all(),  # ✅ AÑADIR ESTA LÍNEA
    }
    
    return render(request, 'MenusAdmins/gestion_recursos_humanos.html', contexto)

def editar_recurso_humano(request, usuario_id):
    """Vista para editar un recurso humano"""
    if request.session.get('usuario_rol') != 'Administrador':
        return redirect('login')
    
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre_usuario = request.POST.get('nombre_usuario')
        correo = request.POST.get('correo')
        rol_id = request.POST.get('rol')
        contrasena = request.POST.get('contrasena')
        
        try:
            # Actualizar los datos básicos
            usuario.nombre_usuario = nombre_usuario
            usuario.correo = correo
            usuario.rol = Rol.objects.get(id=rol_id)
            
            # Solo actualizar contraseña si se proporcionó una nueva
            if contrasena and contrasena.strip():
                usuario.contrasena = contrasena
            
            usuario.save()
            
            messages.success(request, f'✅ Usuario "{usuario.nombre_usuario}" actualizado exitosamente.')
            return redirect('gestion_recursos_humanos')
            
        except Rol.DoesNotExist:
            messages.error(request, '❌ El rol seleccionado no existe.')
        except Exception as e:
            messages.error(request, f'❌ Error al actualizar el usuario: {str(e)}')
    
    return redirect('gestion_recursos_humanos')

def eliminar_usuario(request, usuario_id):
    """Vista para eliminar un usuario (recurso humano)"""
    if request.method == 'POST':
        try:
            usuario = Usuario.objects.get(id=usuario_id)
            
            # Verificar que no sea administrador
            if usuario.rol.nombre_rol == 'Administrador':
                messages.error(request, '❌ No se puede eliminar un usuario administrador.')
                return redirect('gestion_recursos_humanos')
            
            # Verificar si tiene proyectos asignados
            proyectos_asignados = RecursoHumano.objects.filter(usuario=usuario).count()
            
            if proyectos_asignados > 0:
                messages.warning(
                    request, 
                    f'⚠️ El usuario "{usuario.nombre_usuario}" tiene {proyectos_asignados} proyecto(s) asignado(s). '
                    f'Se eliminarán todas sus asignaciones.'
                )
                # Eliminar todas las asignaciones
                RecursoHumano.objects.filter(usuario=usuario).delete()
            
            nombre = usuario.nombre_usuario
            usuario.delete()
            
            messages.success(request, f'✅ Usuario "{nombre}" eliminado exitosamente.')
            
        except Usuario.DoesNotExist:
            messages.error(request, '❌ El usuario no existe.')
        except Exception as e:
            messages.error(request, f'❌ Error al eliminar el usuario: {str(e)}')
    
    return redirect('gestion_recursos_humanos')

@require_http_methods(["GET"])
def validar_fecha_tarea(request):
    """Valida que la fecha límite no sea anterior a hoy"""
    fecha_str = request.GET.get('fecha', '')
    
    if not fecha_str:
        return JsonResponse({'valida': True, 'mensaje': ''})
    
    try:
        from datetime import datetime
        fecha_limite = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        fecha_actual = date.today()
        
        if fecha_limite < fecha_actual:
            return JsonResponse({
                'valida': False,
                'mensaje': f'❌ La fecha no puede ser anterior a hoy ({fecha_actual.strftime("%d/%m/%Y")})'
            })
        
        return JsonResponse({
            'valida': True,
            'mensaje': '✓ Fecha válida'
        })
    except ValueError:
        return JsonResponse({
            'valida': False,
            'mensaje': 'Formato de fecha inválido'
        })

def verificar_nombre_fase(request):
    """Vista AJAX para verificar si un nombre de fase ya existe en el proyecto"""
    if request.method == 'GET':
        nombre = request.GET.get('nombre', '').strip()
        proyecto_id = request.GET.get('proyecto_id', None)
        
        if not nombre or not proyecto_id:
            return JsonResponse({'existe': False})
        
        try:
            existe = Fase.objects.filter(
                proyecto_id=proyecto_id, 
                fase__iexact=nombre
            ).exists()
            
            return JsonResponse({
                'existe': existe, 
                'nombre': nombre
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)