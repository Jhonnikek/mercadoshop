from django.db import models
from django.contrib.auth.models import User


class Tienda(models.Model):
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
