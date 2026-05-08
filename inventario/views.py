from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count, Q
from .models import Item, Transaction, Area, Persona
from django.http import HttpResponse
from fpdf import FPDF
from datetime import datetime

class DashboardView(TemplateView):
    template_name = 'inventario/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = Item.objects.all()
        
        # Calcular stocks
        total_items = items.count()
        critical_items = 0
        
        inventory_status = []
        for item in items:
            entradas = item.transactions.filter(tipo='ENTRADA').count()
            salidas = item.transactions.filter(tipo='SALIDA').count()
            stock = entradas - salidas
            if stock <= 0:
                critical_items += 1
        
        context['total_items'] = total_items
        context['critical_items'] = critical_items
        context['recent_transactions'] = Transaction.objects.all()[:10]
        context['total_areas'] = Area.objects.count()
        return context

class ItemListView(ListView):
    model = Item
    template_name = 'inventario/item_list.html'
    context_object_name = 'items'

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(nombre__icontains=query) | 
                Q(codigo_patrimonial__icontains=query) |
                Q(categoria__icontains=query)
            )
        return queryset

class TransactionCreateView(CreateView):
    model = Transaction
    template_name = 'inventario/transaction_form.html'
    fields = ['item', 'tipo', 'persona', 'area', 'observaciones']
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        # Validar stock en caso de salida
        if form.cleaned_data['tipo'] == 'SALIDA':
            item = form.cleaned_data['item']
            entradas = item.transactions.filter(tipo='ENTRADA').count()
            salidas = item.transactions.filter(tipo='SALIDA').count()
            if (entradas - salidas) <= 0:
                messages.error(self.request, f"Error: No hay stock disponible para {item.nombre}")
                return self.form_invalid(form)
        
        messages.success(self.request, "Movimiento registrado con éxito")
        return super().form_valid(form)

# Mantener reporte PDF
def generate_report(request):
    items = Item.objects.all()
    inventory = []
    for item in items:
        entradas = item.transactions.filter(tipo='ENTRADA').count()
        salidas = item.transactions.filter(tipo='SALIDA').count()
        stock = entradas - salidas
        
        # Obtener último movimiento (aprovechando ordering=['-timestamp'] en el modelo)
        last_tx = item.transactions.first()
        
        inventory.append({
            'nombre': item.nombre,
            'codigo': item.codigo_patrimonial,
            'categoria': item.categoria,
            'stock': stock,
            'last_tipo': last_tx.get_tipo_display() if last_tx else '-',
            'last_persona': last_tx.persona.nombre_completo if last_tx else '-',
            'last_area': last_tx.area.nombre if last_tx else '-',
            'last_fecha': last_tx.timestamp.strftime('%d/%m/%Y %H:%M') if last_tx else '-'
        })

    pdf = FPDF(orientation='L')
    pdf.add_page()
    def clean(txt): return str(txt).encode('latin-1', 'replace').decode('latin-1')
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, clean("Reporte de Inventario Informática - FOLP"), ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 10, clean(f"Fecha de reporte: {datetime.now().strftime('%d/%m/%Y %H:%M')}"), ln=True, align="C")
    pdf.ln(10)
    
    # Encabezados - Total ancho: 277mm (A4 Landscape con márgenes)
    pdf.set_fill_color(28, 112, 91)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(60, 10, clean(" Item / Activo"), border=1, fill=True)
    pdf.cell(30, 10, clean(" Código"), border=1, fill=True)
    pdf.cell(30, 10, clean(" Categoría"), border=1, fill=True)
    pdf.cell(15, 10, clean(" Stock"), border=1, fill=True, align="C")
    pdf.cell(25, 10, clean(" Mov."), border=1, fill=True, align="C")
    pdf.cell(50, 10, clean(" Responsable"), border=1, fill=True)
    pdf.cell(40, 10, clean(" Área/Ubicación"), border=1, fill=True)
    pdf.cell(27, 10, clean(" Fecha/Hora"), border=1, fill=True, align="C")
    pdf.ln()
    
    # Filas
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 8)
    for i in inventory:
        pdf.cell(60, 8, clean(f" {i['nombre']}"), border=1)
        pdf.cell(30, 8, clean(f" {i['codigo']}"), border=1)
        pdf.cell(30, 8, clean(f" {i['categoria']}"), border=1)
        pdf.cell(15, 8, clean(f"{i['stock']}"), border=1, align="C")
        pdf.cell(25, 8, clean(f" {i['last_tipo']}"), border=1, align="C")
        pdf.cell(50, 8, clean(f" {i['last_persona']}"), border=1)
        pdf.cell(40, 8, clean(f" {i['last_area']}"), border=1)
        pdf.cell(27, 8, clean(f"{i['last_fecha']}"), border=1, align="C")
        pdf.ln()
    
    response = HttpResponse(bytes(pdf.output()), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_inventario.pdf"'
    return response
