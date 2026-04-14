from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .decorators import login_required_custom


def vista_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.es_admin():
                return redirect('dashboard')
            return redirect('dashboard_cliente')
        messages.error(request, 'Usuario o contraseña incorrectos')
    return render(request, 'auth/login.html')


def vista_logout(request):
    logout(request)
    return redirect('login')


@login_required_custom
def vista_dashboard_cliente(request):
    from apps.inventory.models import Producto
    productos = Producto.objects.select_related(
        'categoria').filter(is_active=True)
    alertas = productos.filter(stock_actual__lte=0).count()
    return render(request, 'dashboard/cliente.html', {
        'productos':        productos,
        'productos_alerta': alertas,
    })