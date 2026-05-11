from decimal import Decimal

from django.db import models
from django.db.models import CheckConstraint, Q

from core.models import Cliente, Producto


class Pedido(models.Model):
    ESTADOS = [
        ('BORRADOR', 'Borrador'),
        ('CONFIRMADO', 'Confirmado'),
        ('FACTURADO', 'Facturado'),
        ('COBRADO', 'Cobrado'),
        ('CANCELADO', 'Cancelado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.RESTRICT)  # No permite borrar clientes con pedidos asociados
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='BORRADOR')

    # Guarda los totales para optimizar consultas
    total_bruto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_neto = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        # Índices
        indexes = [
            models.Index(fields=['cliente', 'fecha'], name='idx_pedido_cliente_fecha'),
        ]

        # Constraint para asegurar que el total del pedido no sea negativo
        constraints = [
            CheckConstraint(check=Q(total_neto__gte=0), name='total_pedido_positivo')
        ]

    def __str__(self):
        return f"Pedido {self.id} - {self.cliente}"

    def calcular_totales(self):
        """
        Calcula los totales del pedido a partir de sus líneas.

        Base = suma de cantidad x precio_unitario.
        IVA = suma de la base de cada línea x tipo_iva aplicado.
        Total = base + IVA.
        """

        total_bruto = Decimal("0.00")
        total_iva = Decimal("0.00")

        # Recorremos las líneas del pedido de forma explícita,
        # siguiendo el estilo didáctico de los apuntes.
        for linea in self.lineas.all():
            base_linea = linea.precio_unitario * linea.cantidad
            iva_linea = base_linea * linea.tipo_iva

            total_bruto += base_linea
            total_iva += iva_linea

        self.total_bruto = total_bruto
        self.total_iva = total_iva
        self.total_neto = total_bruto + total_iva

        # Guardamos solo los campos calculados.
        self.save(update_fields=['total_bruto', 'total_iva', 'total_neto'])

    def actualizar_totales(self):
        """
        Mantiene compatibilidad con el nombre anterior del método.
        """
        self.calcular_totales()


class LineaPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='lineas')  # Al borrar el pedido, se borran sus líneas
    producto = models.ForeignKey(Producto, on_delete=models.RESTRICT)

    cantidad = models.IntegerField(default=1)

    # SNAPSHOTS: Copias históricas de los datos del producto.
    # Guardan cómo era el producto en el momento de la venta.
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
        # Rellena los campos snapshot solo cuando la línea es nueva.
        if not self.pk:
            self.precio_unitario = self.producto.precio
            self.descripcion = self.producto.nombre
            self.tipo_iva = self.producto.tipo_iva

        # Guarda la línea.
        super().save(*args, **kwargs)

        # Actualiza la cabecera del pedido cada vez que se guarda una línea.
        self.pedido.calcular_totales()

    def delete(self, *args, **kwargs):
        # Guardamos la referencia al pedido antes de borrar la línea.
        pedido_ref = self.pedido

        super().delete(*args, **kwargs)

        # Recalculamos los totales después de borrar la línea.
        pedido_ref.calcular_totales()