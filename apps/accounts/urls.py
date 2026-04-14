from django.urls import path
from . import views

urlpatterns = [
    path('login/',                views.vista_login,               name='login'),
    path('logout/',               views.vista_logout,              name='logout'),
    path('registro/',             views.vista_registro,            name='registro'),
    path('operador/dashboard/',   views.vista_dashboard_operador,  name='dashboard_operador'),
    path('consultor/dashboard/',  views.vista_dashboard_consultor, name='dashboard_consultor'),
]