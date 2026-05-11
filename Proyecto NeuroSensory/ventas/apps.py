from django.apps import AppConfig


class VentasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ventas'

    def ready(self):
        # Importar señales para actualizar stock de productos al crear una venta
        import ventas.signals
