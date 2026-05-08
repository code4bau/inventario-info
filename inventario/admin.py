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
    list_display = ('nombre', 'codigo_patrimonial', 'categoria', 'get_stock')
    list_filter = ('categoria',)
    search_fields = ('nombre', 'codigo_patrimonial')

    def get_stock(self, obj):
        # Cálculo simple de stock
        entradas = obj.transactions.filter(tipo='ENTRADA').count()
        salidas = obj.transactions.filter(tipo='SALIDA').count()
        return entradas - salidas
    get_stock.short_description = 'Stock Actual'

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'item', 'tipo', 'persona', 'area')
    list_filter = ('tipo', 'area', 'timestamp')
    search_fields = ('item__nombre', 'persona__nombre_completo', 'observaciones')
    date_hierarchy = 'timestamp'
