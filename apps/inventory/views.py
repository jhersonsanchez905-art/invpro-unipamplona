from django.shortcuts import render, redirect
from django.contrib import messages
from apps.accounts.decorators import login_required_custom, admin_required


@admin_required
def vista_dashboard(request):
    return render(request, 'inventory/dashboard.html')


@admin_required
def vista_productos(request):
    from apps.inventory.models import Producto, Categoria
    productos  = Producto.objects.select_related(
        'categoria').filter(is_active=True)
    categorias = Categoria.objects.filter(is_active=True)
    return render(request, 'inventory/productos.html', {
        'productos':  productos,
        'categorias': categorias,
    })


@admin_required
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
            nombre=nombre, sku=sku, categoria=cat,
            stock_minimo=stock_min, precio_unitario=precio,
        )
        messages.success(request, f'Producto {nombre} creado correctamente')
    return redirect('productos')


@admin_required
def editar_producto(request, pk):
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

        try:
            prod = Producto.objects.get(pk=pk, is_active=True)
        except Producto.DoesNotExist:
            messages.error(request, 'Producto no encontrado')
            return redirect('productos')

        if Producto.objects.filter(sku=sku).exclude(pk=pk).exists():
            messages.error(request, f'El SKU {sku} ya está en uso')
            return redirect('productos')

        try:
            cat = Categoria.objects.get(id=categoria_id)
        except Categoria.DoesNotExist:
            messages.error(request, 'Categoría no válida')
            return redirect('productos')

        prod.nombre          = nombre
        prod.sku             = sku
        prod.categoria       = cat
        prod.stock_minimo    = stock_min
        prod.precio_unitario = precio
        prod.save(update_fields=[
            'nombre', 'sku', 'categoria',
            'stock_minimo', 'precio_unitario', 'updated_at'
        ])
        messages.success(request, f'Producto {nombre} actualizado')
    return redirect('productos')


@admin_required
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


@admin_required
def vista_movimientos(request):
    from apps.movements.models import Movimiento
    from apps.inventory.models import Producto
    movimientos = Movimiento.objects.select_related(
        'producto', 'usuario').order_by('-created_at')[:50]
    productos = Producto.objects.filter(is_active=True)
    return render(request, 'inventory/movimientos.html', {
        'movimientos': movimientos,
        'productos':   productos,
    })


@login_required_custom
def registrar_movimiento(request):
    from apps.movements.services import registrar_movimiento as reg_mov
    from django.core.exceptions import ValidationError

    if request.method == 'POST':
        tipo        = request.POST.get('tipo', '')
        producto_id = request.POST.get('producto_id', '')
        cantidad    = request.POST.get('cantidad', 0)
        nota        = request.POST.get('nota', '')

        try:
            mov = reg_mov(
                tipo=tipo,
                producto_id=producto_id,
                cantidad=float(cantidad),
                usuario=request.user,
                nota=nota,
            )
            messages.success(request,
                f'Movimiento {tipo} registrado — {mov.producto.sku}')
        except ValidationError as e:
            messages.error(request, e.message)
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    # Redirige según rol
    if request.user.es_admin():
        return redirect('movimientos')
    elif request.user.es_operador():
        return redirect('dashboard_operador')
    return redirect('dashboard_consultor')


@login_required_custom
def vista_categorias(request):
    from apps.inventory.models import Categoria
    categorias = Categoria.objects.filter(
        is_active=True).prefetch_related('productos')
    return render(request, 'inventory/categorias.html',
        {'categorias': categorias})


@admin_required
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


@admin_required
def editar_categoria(request, pk):
    from apps.inventory.models import Categoria
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        desc   = request.POST.get('descripcion', '').strip()
        if not nombre:
            messages.error(request, 'El nombre es obligatorio')
            return redirect('categorias')
        try:
            cat = Categoria.objects.get(pk=pk)
            cat.nombre      = nombre
            cat.descripcion = desc
            cat.save(update_fields=['nombre', 'descripcion'])
            messages.success(request, f'Categoria {nombre} actualizada')
        except Categoria.DoesNotExist:
            messages.error(request, 'Categoria no encontrada')
    return redirect('categorias')


@admin_required
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