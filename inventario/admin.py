from django.contrib import admin
from .models import Area, Persona, Item, Transaction

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'rol')
    search_fields = ('nombre_completo', 'rol')

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo_patrimonial', 'categoria', 'responsable', 'area', 'get_ip', 'get_stock')
    list_filter = ('categoria', 'area', 'responsable')
    search_fields = ('nombre', 'codigo_patrimonial')

    def get_stock(self, obj):
        # Cálculo simple de stock
        entradas = obj.transactions.filter(tipo='ENTRADA').count()
        salidas = obj.transactions.filter(tipo='SALIDA').count()
        return entradas - salidas
    get_stock.short_description = 'Stock Actual'

    def get_ip(self, obj):
        return obj.ip_asignada.direccion_ip if hasattr(obj, 'ip_asignada') and obj.ip_asignada else '-'
    get_ip.short_description = 'IP Asignada'

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'item', 'tipo', 'persona', 'area')
    list_filter = ('tipo', 'area', 'timestamp')
    search_fields = ('item__nombre', 'persona__nombre_completo', 'observaciones')
    date_hierarchy = 'timestamp'
