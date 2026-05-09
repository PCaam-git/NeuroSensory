from django.contrib import admin
from .models import Cliente, Producto

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nif', 'razon_social', 'email', 'telefono', 'created_at') # Mostrar campos clave
    search_fields = ('razon_social', 'nif') # Búsqueda por razón social y NIF
    readonly_fields = ('created_at', 'updated_at') # Campos de solo lectura

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('sku', 'nombre', 'precio', 'tipo_iva', 'stock') # Mostrar campos clave
    search_fields = ('sku', 'nombre') # Búsqueda por SKU y nombre
    list_filter = ('tipo_iva',) # Filtro lateral por IVA