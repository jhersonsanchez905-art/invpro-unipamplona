from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def vista_dashboard(request):
    return render(request, 'inventory/dashboard.html')

@login_required
def vista_productos(request):
    from apps.inventory.models import Producto, Categoria
    productos  = Producto.objects.select_related(
        'categoria').filter(is_active=True)
    categorias = Categoria.objects.filter(is_active=True)
    return render(request, 'inventory/productos.html', {
        'productos':  productos,
        'categorias': categorias,
    })

@login_required
def vista_movimientos(request):
    from apps.movements.models import Movimiento
    movimientos = Movimiento.objects.select_related(
        'producto', 'usuario').order_by('-created_at')[:50]
    return render(request, 'inventory/movimientos.html', {
        'movimientos': movimientos,
    })

@login_required
def vista_categorias(request):
    from apps.inventory.models import Categoria
    categorias = Categoria.objects.filter(is_active=True)
    return render(request, 'inventory/categorias.html', {
        'categorias': categorias,
    })