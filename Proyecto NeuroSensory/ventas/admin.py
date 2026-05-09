from django.contrib import admin
from .models import Pedido, LineaPedido

class LineaPedidoInline(admin.TabularInline):
    model = LineaPedido
    extra = 1
    # Mostrar campos clave en la línea del pedido
    fields = ('producto', 'cantidad', 'precio_unitario', 'tipo_iva', 'descripcion')

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    # Mostrar campos clave en la lista de pedidos
    list_display = ('id', 'cliente', 'fecha', 'estado', 'total_neto')
    
    list_filter = ('estado', 'fecha')
    search_fields = ('cliente__razon_social',)
    
    # Campos de solo lectura para totales calculados
    readonly_fields = ('total_bruto', 'total_iva', 'total_neto')
    
    inlines = [LineaPedidoInline]
    