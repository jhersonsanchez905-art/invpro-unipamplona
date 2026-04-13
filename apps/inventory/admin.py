from django.contrib import admin
from .models import Categoria, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display   = ('nombre', 'is_active', 'created_at')
    list_filter    = ('is_active',)
    search_fields  = ('nombre',)
    ordering       = ('nombre',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display   = ('sku', 'nombre', 'categoria',
                      'stock_actual', 'stock_minimo',
                      'tiene_alerta', 'is_active')
    list_filter    = ('categoria', 'is_active')
    search_fields  = ('nombre', 'sku')
    readonly_fields = ('id', 'created_at', 'updated_at',
                       'tiene_alerta')
    ordering       = ('nombre',)