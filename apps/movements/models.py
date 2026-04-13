import uuid
from django.db import models
from django.conf import settings


class Movimiento(models.Model):
    ENTRADA = 'entrada'
    SALIDA  = 'salida'
    AJUSTE  = 'ajuste'
    TIPO_CHOICES = [
        (ENTRADA, 'Entrada'),
        (SALIDA,  'Salida'),
        (AJUSTE,  'Ajuste'),
    ]

    id       = models.UUIDField(primary_key=True,
                 default=uuid.uuid4, editable=False)
    tipo     = models.CharField(max_length=10, choices=TIPO_CHOICES)
    producto = models.ForeignKey(
                 'inventory.Producto',
                 on_delete=models.PROTECT,
                 related_name='movimientos')
    cantidad = models.DecimalField(max_digits=12, decimal_places=2)
    nota     = models.TextField(blank=True, default='')
    usuario  = models.ForeignKey(
                 settings.AUTH_USER_MODEL,
                 on_delete=models.PROTECT,
                 related_name='movimientos')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Movimiento'
        verbose_name_plural = 'Movimientos'
        ordering            = ['-created_at']
        indexes = [
            models.Index(fields=['producto', 'created_at']),
            models.Index(fields=['tipo']),
        ]

    def __str__(self):
        return f'{self.tipo.upper()} | {self.producto.sku} | {self.cantidad}'