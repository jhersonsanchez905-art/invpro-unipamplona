from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from apps.accounts.models import CustomUser
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
            elif user.es_operador():
                return redirect('dashboard_operador')
            else:
                return redirect('dashboard_consultor')
        messages.error(request, 'Usuario o contraseña incorrectos')
    return render(request, 'auth/login.html')


def vista_logout(request):
    logout(request)
    return redirect('login')


def vista_registro(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username  = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '').strip()
        password2 = request.POST.get('password2', '').strip()

        if not username or not password1:
            messages.error(request, 'Usuario y contraseña son obligatorios')
            return redirect('registro')

        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden')
            return redirect('registro')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, f'El usuario {username} ya existe')
            return redirect('registro')

        CustomUser.objects.create_user(
            username=username,
            password=password1,
            rol=CustomUser.OPERADOR,
        )
        messages.success(request,
            'Cuenta creada. Ingresa con tus credenciales.')
        return redirect('login')

    return render(request, 'auth/registro.html')


@login_required_custom
def vista_dashboard_operador(request):
    from apps.inventory.models import Producto
    productos = Producto.objects.select_related(
        'categoria').filter(is_active=True)
    alertas = productos.filter(
        stock_actual__lte=0).count()
    return render(request, 'dashboard/operador.html', {
        'productos':        productos,
        'productos_alerta': alertas,
    })


@login_required_custom
def vista_dashboard_consultor(request):
    from apps.inventory.models import Producto
    productos = Producto.objects.select_related(
        'categoria').filter(is_active=True)
    alertas = productos.filter(
        stock_actual__lte=0).count()
    return render(request, 'dashboard/consultor.html', {
        'productos':        productos,
        'productos_alerta': alertas,
    })