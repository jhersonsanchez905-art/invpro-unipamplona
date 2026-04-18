from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from apps.accounts.models import CustomUser
from .decorators import login_required_custom, operador_required, consultor_required


def vista_login(request):
    """
    Autentica al usuario con username y password.

    Flujo con 2FA activo:
      1. Valida credenciales con authenticate().
      2. Si el usuario tiene TOTPDevice confirmado, almacena su PK en sesión
         y redirige a /2fa/verify/ SIN llamar login() todavía.
      3. En /2fa/verify/ se valida el token y solo entonces se llama login().
      Este orden garantiza que la sesión nunca queda abierta antes de
      completar el segundo factor.

    Flujo sin 2FA:
      Llama login() directamente y redirige según el rol.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)

        if user is not None:
            from django_otp.plugins.otp_totp.models import TOTPDevice
            tiene_2fa = TOTPDevice.objects.filter(
                user=user, confirmed=True).exists()

            if tiene_2fa:
                # Guarda el PK en sesión temporal — NO llama login() aún.
                # La sesión queda sin usuario autenticado hasta pasar el 2FA.
                request.session['pre_2fa_user_pk'] = str(user.pk)
                request.session['pre_2fa_backend'] = \
                    'django.contrib.auth.backends.ModelBackend'
                return redirect('2fa_verify')

            # Sin 2FA — autenticación completa directa
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
    """
    Cierra la sesión activa y redirige al login.
    """
    logout(request)
    return redirect('login')


def vista_registro(request):
    """
    Crea una nueva cuenta de usuario con rol CONSULTOR (solo lectura).
    Los roles operador y admin solo pueden ser asignados por un administrador
    desde el panel de Django Admin.

    Validaciones:
      - username y password1 no pueden estar vacíos.
      - password1 debe coincidir con password2.
      - El username no debe existir previamente en la base de datos.
    """
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

        # El autoregistro público asigna siempre rol CONSULTOR (solo lectura).
        # Para otorgar roles operador o admin, usar Django Admin.
        CustomUser.objects.create_user(
            username=username,
            password=password1,
            rol=CustomUser.CONSULTOR,
        )
        messages.success(request,
            'Cuenta creada. Ingresa con tus credenciales.')
        return redirect('login')

    return render(request, 'auth/registro.html')


@operador_required
def vista_dashboard_operador(request):
    """
    Panel principal para usuarios con rol operador.
    Muestra el inventario activo y el conteo de productos con stock en cero.
    Requiere rol operador o superior (decorator: operador_required).
    """
    from apps.inventory.models import Producto

    productos = Producto.objects.select_related(
        'categoria').filter(is_active=True)
    alertas = productos.filter(stock_actual__lte=0).count()

    return render(request, 'dashboard/operador.html', {
        'productos':        productos,
        'productos_alerta': alertas,
    })


@consultor_required
def vista_dashboard_consultor(request):
    """
    Panel principal para usuarios con rol consultor (solo lectura).
    Muestra el inventario activo y el conteo de productos con stock en cero.
    No expone acciones de escritura en la plantilla.
    Requiere autenticación (decorator: consultor_required).
    """
    from apps.inventory.models import Producto

    productos = Producto.objects.select_related(
        'categoria').filter(is_active=True)
    alertas = productos.filter(stock_actual__lte=0).count()

    return render(request, 'dashboard/consultor.html', {
        'productos':        productos,
        'productos_alerta': alertas,
    })


@login_required_custom
def vista_2fa_setup(request):
    from django_otp.plugins.otp_totp.models import TOTPDevice
    import qrcode, qrcode.image.svg, io, base64

    # Elimina dispositivos previos no confirmados
    TOTPDevice.objects.filter(user=request.user, confirmed=False).delete()

    device, created = TOTPDevice.objects.get_or_create(
        user=request.user,
        confirmed=False,
        defaults={'name': 'InvPro Unipamplona'}
    )

    # Genera QR
    uri = device.config_url
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    qr_b64 = base64.b64encode(buf.getvalue()).decode()

    return render(request, 'auth/2fa_setup.html', {
        'qr_b64':  qr_b64,
        'secret':  device.bin_key.hex(),
        'device':  device,
    })


def vista_2fa_verify(request):
    """
    Verifica el token TOTP en dos escenarios:

    A) Confirmación inicial (setup):
       El usuario ya está autenticado (login_required_custom) y confirma
       su nuevo dispositivo por primera vez.

    B) Verificación en login:
       El usuario NO está autenticado aún. Su PK está en
       request.session['pre_2fa_user_pk']. Si el token es válido,
       se llama login() y se limpia la sesión temporal.
    """
    from django_otp.plugins.otp_totp.models import TOTPDevice
    import django_otp

    if request.method == 'POST':
        token = request.POST.get('token', '').strip().replace(' ', '')

        # ── Escenario A: confirmación de setup (usuario ya autenticado) ──────
        if request.user.is_authenticated:
            device = TOTPDevice.objects.filter(
                user=request.user, confirmed=False).first()

            if device:
                if device.verify_token(token):
                    device.confirmed = True
                    device.save()
                    django_otp.login(request, device)
                    messages.success(request,
                        '2FA activado correctamente en tu cuenta')
                    return redirect('dashboard')
                else:
                    messages.error(request,
                        'Código incorrecto. Intenta de nuevo')
                    return redirect('2fa_setup')

            # Usuario autenticado sin device pendiente: verifica login normal
            device = TOTPDevice.objects.filter(
                user=request.user, confirmed=True).first()
            if device and device.verify_token(token):
                django_otp.login(request, device)
                return _redirigir_por_rol(request.user)

            messages.error(request, 'Código incorrecto')
            return render(request, 'auth/2fa_verify.html')

        # ── Escenario B: segundo factor en flujo de login ────────────────────
        user_pk = request.session.get('pre_2fa_user_pk')
        if not user_pk:
            # Sesión temporal expirada o acceso directo a la URL — vuelve al login
            messages.error(request,
                'Sesión expirada. Inicia sesión nuevamente.')
            return redirect('login')

        try:
            user = CustomUser.objects.get(pk=user_pk)
        except CustomUser.DoesNotExist:
            messages.error(request, 'Usuario no encontrado')
            return redirect('login')

        device = TOTPDevice.objects.filter(
            user=user, confirmed=True).first()

        if device and device.verify_token(token):
            # Token válido — ahora sí se establece la sesión completa
            backend = request.session.get(
                'pre_2fa_backend',
                'django.contrib.auth.backends.ModelBackend')
            user.backend = backend
            login(request, user)
            django_otp.login(request, device)
            # Limpia datos temporales de sesión
            request.session.pop('pre_2fa_user_pk', None)
            request.session.pop('pre_2fa_backend', None)
            return _redirigir_por_rol(user)

        messages.error(request, 'Código incorrecto. Intenta de nuevo')

    return render(request, 'auth/2fa_verify.html')


def _redirigir_por_rol(user):
    """Helper interno — centraliza la redirección por rol para evitar
    duplicar la misma lógica en vista_login y vista_2fa_verify."""
    if user.es_admin():
        return redirect('dashboard')
    elif user.es_operador():
        return redirect('dashboard_operador')
    else:
        return redirect('dashboard_consultor')


@login_required_custom
def vista_2fa_disable(request):
    from django_otp.plugins.otp_totp.models import TOTPDevice
    if request.method == 'POST':
        TOTPDevice.objects.filter(user=request.user).delete()
        messages.success(request, '2FA desactivado')
    return redirect('dashboard')