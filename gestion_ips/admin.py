from django.contrib import admin
from .models import DireccionIP

@admin.register(DireccionIP)
class DireccionIPAdmin(admin.ModelAdmin):
    list_display = ('direccion_ip', 'area', 'estado', 'descripcion', 'fecha_actualizacion')
    list_filter = ('estado', 'area')
    search_fields = ('direccion_ip', 'descripcion')
    ordering = ('direccion_ip',)
