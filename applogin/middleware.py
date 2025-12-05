from django.shortcuts import redirect
from django.urls import reverse

class RoleBasedRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # ✅ EXCLUIR archivos estáticos y media (CRÍTICO)
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return self.get_response(request)
        
        # ✅ EXCLUIR admin de Django
        if request.path.startswith('/admin/'):
            return self.get_response(request)
        
        # ✅ EXCLUIR logout
        if request.path.startswith('/logout/'):
            return self.get_response(request)
        
        # Lógica de redirección por rol
        if 'usuario_id' in request.session:
            usuario_rol = request.session.get('usuario_rol')
            
            if usuario_rol == 'Administrador':
                # Rutas permitidas para admin
                rutas_admin = [
                    '/admin_dashboard/',
                    '/agregar_proyecto/',
                    '/proyecto/',
                    '/insertar_usuario/',
                    '/editar_proyecto/',
                    '/prioridades/',
                    '/relacion-documento/',  # ✅ AGREGAR ESTA
                    '/fase/',  # ✅ AGREGAR ESTA
                    '/verificar-nombre-proyecto/',
                    '/verificar-disponibilidad-usuario/',
                    '/recurso-humano/',
                    '/gestion-recursos-humanos/',  # ✅ AGREGAR ESTA
                    '/usuario/',  # ✅ AGREGAR ESTA
                ]
                if not any(request.path.startswith(ruta) for ruta in rutas_admin):
                    return redirect(reverse('admin_dashboard'))
            
            elif usuario_rol == 'Usuario':
                # Rutas permitidas para usuario
                rutas_usuario = [
                    '/user_dashboard/',
                    '/agregar_proyecto/',
                    '/proyecto/',
                    '/relacionar_documentousuario/',
                    '/insertar_usuario/',
                    '/prioridades/'

                ]
                if not any(request.path.startswith(ruta) for ruta in rutas_usuario):
                    return redirect(reverse('user_dashboard'))
        
        response = self.get_response(request)
        return response