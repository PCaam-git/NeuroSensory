from rest_framework import serializers
from .models import Producto

class ProductoSerializer(serializers.ModelSerializer):

    # Serializador para el modelo Producto
    # El campo stock solo se muestra si el usuario esta autenticado.

    class Meta:
        model = Producto
        fields = ['id', 'sku', 'nombre', 'descripcion', 'precio', 'tipo_iva', 'stock']
    
    def to_representation(self, instance):
        # Si el usuario no esta autenticado, no se muestra el campo stock

        data = super().to_representation(instance)

        request = self.context.get('request')

        if not request or not request.user.is_authenticated:
            data.pop('stock', None)

        return data