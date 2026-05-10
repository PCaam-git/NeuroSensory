from rest_framework import generics
from rest_framework.authentication import BasicAuthentication, SessionAuthentication

from .models import Producto
from .permissions import SoloLecturaProductos
from .serializers import ProductoSerializer


class ProductoListAPIView(generics.ListAPIView):
    
    # GET /api/productos/ → devuelve el listado de productos en JSON.
    # El campo stock solo aparece si el usuario está autenticado.

    queryset = Producto.objects.all().order_by('nombre')
    serializer_class = ProductoSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [SoloLecturaProductos]