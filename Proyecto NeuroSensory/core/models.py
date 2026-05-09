from django.db import models

class Cliente(models.Model):
    nif = models.CharField(max_length=15, unique=True, verbose_name="NIF/CIF")
    razon_social = models.CharField(max_length=100, verbose_name="Razón Social")
    email = models.EmailField(verbose_name="Email de contacto", unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.razon_social} ({self.nif})"

class Producto(models.Model):
    sku = models.CharField(max_length=10, unique=True, verbose_name="SKU / Referencia")
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    
    # Precio base y Tipo IVA
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Base")
    tipo_iva = models.DecimalField(max_digits=4, decimal_places=2, default=0.21, verbose_name="IVA (0.21)")

    stock = models.IntegerField(default=0)
    
    class Meta:
        # Definición de Índices
        indexes = [
            models.Index(fields=['nombre'], name='idx_producto_nombre'),
        ]

    def __str__(self):
        return f"{self.nombre} [{self.sku}]"