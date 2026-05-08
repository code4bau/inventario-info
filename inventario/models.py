from django.db import models

class Area(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Área")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Área"
        verbose_name_plural = "Áreas"

class Persona(models.Model):
    nombre_completo = models.CharField(max_length=200)
    rol = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.nombre_completo

    class Meta:
        verbose_name = "Persona"
        verbose_name_plural = "Personas"

class Item(models.Model):
    CATEGORIES = [
        ('Hardware', 'Hardware'),
        ('Periférico', 'Periférico'),
        ('Redes', 'Redes'),
        ('Otro', 'Otro'),
    ]
    nombre = models.CharField(max_length=200)
    codigo_patrimonial = models.CharField(max_length=100, unique=True)
    categoria = models.CharField(max_length=50, choices=CATEGORIES, default='Hardware')
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.codigo_patrimonial})"

    class Meta:
        verbose_name = "Ítem"
        verbose_name_plural = "Ítems"

class Transaction(models.Model):
    TYPES = [
        ('ENTRADA', 'ENTRADA (+)'),
        ('SALIDA', 'SALIDA (-)'),
    ]
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='transactions')
    tipo = models.CharField(max_length=10, choices=TYPES, verbose_name="Tipo de Movimiento")
    persona = models.ForeignKey(Persona, on_delete=models.PROTECT, verbose_name="Responsable")
    area = models.ForeignKey(Area, on_delete=models.PROTECT, verbose_name="Ubicación/Área")
    observaciones = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - {self.item.nombre} ({self.timestamp.strftime('%d/%m/%Y')})"

    class Meta:
        verbose_name = "Transacción"
        verbose_name_plural = "Transacciones"
        ordering = ['-timestamp']
