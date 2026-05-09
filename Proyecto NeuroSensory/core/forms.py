from django import forms
from .models import Cliente, Producto

class ProductoForm(forms.ModelForm):

    # Forumulario para crear o editar productos
    # Valida stock >= 0 

    class Meta:
        model = Producto
        fields = ['sku', 'nombre', 'descripcion', 'precio', 'tipo_iva', 'stock']
  
        help_texts = {
        'sku': 'Código único del producto.',
        'precio': 'Introduce el precio base del producto (sin IVA).',
        'tipo_iva': 'Tipo de IVA aplicable (ej. 0.21 para 21%).',
        'stock': 'El stock debe ser mayor o igual a 0.',
        }

    def clean_stock(self):
        #Valida que el stock no sea negativo

        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise forms.ValidationError("El stock no puede ser inferior a 0.")
        return stock
    
class ClienteForm(forms.ModelForm):

    # Formulario para crear o editar clientes
    # Se valida que el NIF/CIF sea único porque NeuroSensory vende tanto a empresas como a particulares.

    class Meta:
        model = Cliente
        fields = ['nif', 'razon_social', 'email', 'telefono']
  
        help_texts = {
        'nif': 'Introduce el NIF o CIF del cliente. Debe ser único.',
        'razon_social': 'Introduce la razón social o nombre del cliente.',
        'email': 'Introduce una dirección de correo electrónico válida.',
        'telefono': 'Introduce un número de teléfono de contacto (opcional).',
        }

    def clean_nif(self):
        # Valida que el NIF/CIF sea único

        nif = self.cleaned_data.get('nif')

# Si el NIF ya existe en la base de datos devuelve error de validación, excepto si se está editando un cliente existente.
        if nif and Cliente.objects.filter(nif=nif).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ya existe un cliente con este NIF/CIF.')
        return nif