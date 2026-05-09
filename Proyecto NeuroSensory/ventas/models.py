from django.db import models
from core.models import Cliente, Producto
from django.db.models import CheckConstraint, Q, Sum, F

class Pedido(models.Model):
    ESTADOS = [
        ('BORRADOR', 'Borrador'),
        ('CONFIRMADO', 'Confirmado'),
        ('FACTURADO', 'Facturado'),
        ('COBRADO', 'Cobrado'),
        ('CANCELADO', 'Cancelado'),
    ]

    
    cliente = models.ForeignKey(Cliente, on_delete=models.RESTRICT) #No permite borrar clientes con pedidos asociados
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='BORRADOR')

    # Guarda los totales para optimizar consultas
    total_bruto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_neto = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        # Indices
        indexes = [
            models.Index(fields=['cliente', 'fecha'], name='idx_pedido_cliente_fecha'),
        ]
        # Constraints para asegurar totales no negativos
        constraints = [
            CheckConstraint(check=Q(total_neto__gte=0), name='total_pedido_positivo')
        ]

    def __str__(self):
        return f"Pedido {self.id} - {self.cliente}"

    def actualizar_totales(self):

        # Calcula la suma de todas las líneas asociadas
        totales = self.lineas.aggregate(
            sum_bruto=Sum(F('cantidad') * F('precio_unitario')),
            sum_iva=Sum(F('cantidad') * F('precio_unitario') * F('tipo_iva'))
        )

        self.total_bruto = totales['sum_bruto'] or 0
        self.total_iva = totales['sum_iva'] or 0
        self.total_neto = self.total_bruto + self.total_iva
        
        # Guarda solo los campos numéricos 
        self.save(update_fields=['total_bruto', 'total_iva', 'total_neto'])


class LineaPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='lineas') # Al borrar el pedido, se borran sus líneas
    producto = models.ForeignKey(Producto, on_delete=models.RESTRICT)
    
    cantidad = models.IntegerField(default=1)

    # SNAPSHOTS: Copias históricas de los datos del producto. Guardan cómo era el producto en el momento de la venta.
    descripcion = models.CharField(max_length=255, blank=True, verbose_name="Descripción (Snapshot)")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    tipo_iva = models.DecimalField(max_digits=4, decimal_places=2, blank=True, verbose_name="IVA Aplicado")

    class Meta:
        constraints = [
            CheckConstraint(check=Q(cantidad__gt=0), name='cantidad_linea_positiva')
        ]

    def __str__(self):
        return f"{self.cantidad}x {self.producto.sku}"

    def save(self, *args, **kwargs):
        # Lógica para rellenar los campos snapshot al crear la línea. Solo si es una línea nueva (no tiene PK aún)
        if not self.pk: 
            self.precio_unitario = self.producto.precio
            self.descripcion = self.producto.nombre  # Copia nombre como descripción 
            self.tipo_iva = self.producto.tipo_iva   # Copia el IVA 

        # 2. Guarda la línea
        super().save(*args, **kwargs)
        
        # 3. Actualiza la cabecera del Pedido
        self.pedido.actualizar_totales()

    def delete(self, *args, **kwargs):
        # Al borrar una línea, actualizales del pedido
        pedido_ref = self.pedido
        super().delete(*args, **kwargs)
        pedido_ref.actualizar_totales()