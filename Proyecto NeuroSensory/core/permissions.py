from rest_framework.permissions import BasePermission

class SoloLecturaProductos(BasePermission):
    
    # Solo permite lectura en la API de productos.
    # El campo stock se controla en serializers.py, no se muestra si el usuario no esta autenticado.

    METODOS_SEGUROS = ('GET', 'HEAD', 'OPTIONS')

    def has_permission(self, request, view):
            return request.method in self.METODOS_SEGUROS
        