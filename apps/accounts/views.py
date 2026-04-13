from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .decorators import admin_required, login_required_custom


def vista_login(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        user = authenticate(request, username=username,
                            password=password)
        if user is not None:
            login(request, user)
            if user.es_admin():
                return redirect("dashboard")
            return redirect("dashboard_cliente")
        messages.error(request, "Usuario o contraseña incorrectos")
    return render(request, "auth/login.html")

def vista_logout(request):
    logout(request)
    return redirect("login")

@admin_required
def vista_dashboard(request):
    return render(request, "dashboard/admin.html")

@login_required_custom
def vista_dashboard_cliente(request):
    return render(request, "dashboard/cliente.html")