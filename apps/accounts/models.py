import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ADMIN   = 'admin'
    CLIENTE = 'cliente'
    ROL_CHOICES = [
        (ADMIN,   'Administrador'),
        (CLIENTE, 'Cliente'),
    ]
    id  = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rol = models.CharField(max_length=10, choices=ROL_CHOICES, default=CLIENTE)

    def es_admin(self):
        return self.rol == self.ADMIN or self.is_superuser


    class Meta:
        verbose_name        = 'Usuario'
        verbose_name_plural = 'Usuarios'