from django.urls import path
from . import views

urlpatterns = [
    path('',             views.vista_dashboard,       name='dashboard'),
    path('productos/',   views.vista_productos,        name='productos'),
    path('productos/crear/',              views.crear_producto,     name='crear_producto'),
    path('productos/<uuid:pk>/eliminar/', views.eliminar_producto,  name='eliminar_producto'),
    path('movimientos/', views.vista_movimientos,      name='movimientos'),
    path('categorias/',  views.vista_categorias,       name='categorias'),
    path('categorias/crear/',                views.crear_categoria,    name='crear_categoria'),
    path('categorias/<uuid:pk>/eliminar/',   views.eliminar_categoria, name='eliminar_categoria'),
    path('movimientos/registrar/', views.registrar_movimiento, name='registrar_movimiento'),
]