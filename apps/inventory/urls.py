from django.urls import path
from . import views

urlpatterns = [
    path('',             views.vista_dashboard,   name='dashboard'),
    path('productos/',   views.vista_productos,    name='productos'),
    path('movimientos/', views.vista_movimientos,  name='movimientos'),
    path('categorias/',  views.vista_categorias,   name='categorias'),
]