from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


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
def crear_producto(request):
    from apps.inventory.models import Producto, Categoria
    if request.method == 'POST':
        nombre       = request.POST.get('nombre', '').strip()
        sku          = request.POST.get('sku', '').strip()
        categoria_id = request.POST.get('categoria_id', '')
        stock_min    = request.POST.get('stock_minimo', 0)
        precio       = request.POST.get('precio_unitario', 0)

        if not nombre or not sku:
            messages.error(request, 'Nombre y SKU son obligatorios')
            return redirect('productos')

        if Producto.objects.filter(sku=sku).exists():
            messages.error(request, f'Ya existe un producto con SKU {sku}')
            return redirect('productos')

        try:
            cat = Categoria.objects.get(id=categoria_id)
        except Categoria.DoesNotExist:
            messages.error(request, 'Categoria no valida')
            return redirect('productos')

        Producto.objects.create(
            nombre=nombre,
            sku=sku,
            categoria=cat,
            stock_minimo=stock_min,
            precio_unitario=precio,
        )
        messages.success(request, f'Producto {nombre} creado correctamente')
    return redirect('productos')


@login_required
def eliminar_producto(request, pk):
    from apps.inventory.models import Producto
    try:
        p = Producto.objects.get(pk=pk)
        p.is_active = False
        p.save(update_fields=['is_active'])
        messages.success(request, f'Producto {p.nombre} eliminado')
    except Producto.DoesNotExist:
        messages.error(request, 'Producto no encontrado')
    return redirect('productos')


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
    categorias = Categoria.objects.filter(
        is_active=True
    ).prefetch_related('productos')
    return render(request, 'inventory/categorias.html',
        {'categorias': categorias})


@login_required
def crear_categoria(request):
    from apps.inventory.models import Categoria
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        desc   = request.POST.get('descripcion', '').strip()
        if not nombre:
            messages.error(request, 'El nombre es obligatorio')
            return redirect('categorias')
        if Categoria.objects.filter(nombre=nombre).exists():
            messages.error(request, f'La categoria {nombre} ya existe')
            return redirect('categorias')
        Categoria.objects.create(nombre=nombre, descripcion=desc)
        messages.success(request, f'Categoria {nombre} creada correctamente')
    return redirect('categorias')


@login_required
def eliminar_categoria(request, pk):
    from apps.inventory.models import Categoria
    try:
        cat = Categoria.objects.get(pk=pk)
        cat.is_active = False
        cat.save()
        messages.success(request, f'Categoria {cat.nombre} eliminada')
    except Categoria.DoesNotExist:
        messages.error(request, 'Categoria no encontrada')
    return redirect('categorias')