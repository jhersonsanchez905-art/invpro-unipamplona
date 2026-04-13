from django.urls import path
from . import views

urlpatterns = [
    path('',              views.vista_dashboard,        name='dashboard'),
    path('cliente/',      views.vista_dashboard,        name='dashboard_cliente'),
    path('productos/',    views.vista_productos,        name='productos'),
    path('movimientos/',  views.vista_movimientos,      name='movimientos'),
    path('categorias/',   views.vista_categorias,       name='categorias'),
    path('categorias/crear/',                views.crear_categoria,    name='crear_categoria'),
    path('categorias/<uuid:pk>/eliminar/',   views.eliminar_categoria, name='eliminar_categoria'),
]