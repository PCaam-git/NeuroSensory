from django.contrib import admin

from .models import Oportunidad


@admin.register(Oportunidad)
class OportunidadAdmin(admin.ModelAdmin):
    # Campos principales que aparecen en el listado del admin.
    list_display = (
        'titulo',
        'cliente',
        'valor_estimado',
        'etapa',
        'fecha_creacion',
        'fecha_cierre',
        'dias_abierta',
    )

    # Filtros laterales.
    list_filter = (
        'etapa',
        'fecha_creacion',
        'fecha_cierre',
    )

    # Búsqueda por título de la oportunidad y por cliente.
    search_fields = (
        'titulo',
        'cliente__razon_social',
        'cliente__nif',
    )

    # Fecha de creacion. Se genera automáticamente al crear la oportunidad, no se puede editar.
    readonly_fields = (
        'fecha_creacion',
        'dias_abierta',
    )