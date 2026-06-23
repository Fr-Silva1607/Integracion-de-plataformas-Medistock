from django.contrib import admin

from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'categoria', 'tipo_venta', 'precio', 'cantidad')
    list_filter = ('categoria', 'tipo_venta')
    search_fields = ('nombre', 'descripcion', 'categoria', 'etiqueta_precio')
    ordering = ('nombre',)
    fieldsets = (
        ('Datos del producto', {
            'fields': ('nombre', 'descripcion', 'categoria', 'tipo_venta', 'etiqueta_precio')
        }),
        ('Inventario y precio', {
            'fields': ('precio', 'cantidad', 'imagen_url')
        }),
    )
