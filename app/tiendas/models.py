from django.db import models
from panel_admin.models import Tienda


class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    descripcion = models.TextField(blank=True, null=True)
    tienda = models.ForeignKey(
        Tienda,
        on_delete=models.CASCADE,
        related_name='productos',
    )

    def __str__(self):
        return f'{self.nombre} - {self.tienda.nombre}'
