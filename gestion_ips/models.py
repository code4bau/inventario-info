from django.db import models
from inventario.models import Area

class DireccionIP(models.Model):
    ESTADOS = [
        ('ACTIVA', 'Activa'),
        ('INACTIVA', 'Inactiva'),
        ('RESERVADA', 'Reservada'),
    ]
    
    direccion_ip = models.GenericIPAddressField(unique=True, verbose_name="Dirección IP")
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Área Asignada", related_name="ips")
    descripcion = models.CharField(max_length=200, blank=True, null=True, verbose_name="Descripción / Equipo")
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ACTIVA', verbose_name="Estado")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    def __str__(self):
        return f"{self.direccion_ip} - {self.area.nombre if self.area else 'Sin área'}"

    class Meta:
        verbose_name = "Dirección IP"
        verbose_name_plural = "Direcciones IP"
        ordering = ['direccion_ip']
