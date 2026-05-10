import logging

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Pedido

logger = logging.getLogger(__name__)

# para evitar descontar el stock de nuevo al editar un pedido ya confirmado, realizamos una comparacion del estado del pedido anterior a esta funcion.
#pre_save -> antes de guardar pedido, ejecuta la función
@receiver(pre_save, sender=Pedido)

# La funcion se ejecuta automaticamente. Instance corresponde al pedido que se esta guardando.
def guardar_estado_anterior_pedido(sender, instance, **kwargs):
    
    # comprueba si el pedido ya existe en la bbdd 
    if instance.pk:
        # busca en la bbdd el estado de ese pedido antes de guardar cambios.
        pedido_anterior = Pedido.objects.filter(pk=instance.pk).first()
        instance.estado_anterior = pedido_anterior.estado if pedido_anterior else None
    else:
        # si el pedido no existia, no tiene estado anterior.
        instance.estado_anterior = None


@receiver(post_save, sender=Pedido)
def descontar_stock_al_confirmar_pedido(sender, instance, created, **kwargs):
    
    # Descuenta stock cuando un pedido pasa a estado CONFIRMADO.

    # Solo actúa si el estado ha cambiado a CONFIRMADO desde otro estado diferente.
    estado_anterior = getattr(instance, 'estado_anterior', None)

    if instance.estado != 'CONFIRMADO':
        return

    if estado_anterior == 'CONFIRMADO':
        return

    lineas = instance.lineas.select_related('producto').all()

    # Primero comprobamos todo el stock para evitar descuentos parciales.
    for linea in lineas:
        producto = linea.producto

        if producto.stock < linea.cantidad:
            logger.error(
                "Stock insuficiente para confirmar el pedido %s. Producto: %s. Stock actual: %s. Cantidad solicitada: %s.",
                instance.id,
                producto.sku,
                producto.stock,
                linea.cantidad
            )
            return

    # Si todas las líneas tienen stock suficiente, descontamos.
    for linea in lineas:
        producto = linea.producto
        producto.stock -= linea.cantidad
        producto.save(update_fields=['stock'])

        logger.info(
            "Stock descontado. Pedido: %s. Producto: %s. Cantidad descontada: %s. Stock final: %s.",
            instance.id,
            producto.sku,
            linea.cantidad,
            producto.stock
        )