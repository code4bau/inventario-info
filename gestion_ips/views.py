from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import DireccionIP
from .forms import IPForm

class IPListView(LoginRequiredMixin, ListView):
    model = DireccionIP
    template_name = 'gestion_ips/ip_list.html'
    context_object_name = 'ips'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return DireccionIP.objects.filter(direccion_ip__icontains=query) | DireccionIP.objects.filter(descripcion__icontains=query)
        return DireccionIP.objects.all()

class IPCreateView(LoginRequiredMixin, CreateView):
    model = DireccionIP
    form_class = IPForm
    template_name = 'gestion_ips/ip_form.html'
    success_url = reverse_lazy('ip_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        ip = self.object
        if ip.dispositivo and ip.area:
            ip.dispositivo.area = ip.area
            ip.dispositivo.save()
        messages.success(self.request, "IP registrada exitosamente.")
        return response

class IPUpdateView(LoginRequiredMixin, UpdateView):
    model = DireccionIP
    form_class = IPForm
    template_name = 'gestion_ips/ip_form.html'
    success_url = reverse_lazy('ip_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        ip = self.object
        if ip.dispositivo and ip.area:
            ip.dispositivo.area = ip.area
            ip.dispositivo.save()
        messages.success(self.request, "IP actualizada exitosamente.")
        return response

class IPDeleteView(LoginRequiredMixin, DeleteView):
    model = DireccionIP
    template_name = 'gestion_ips/ip_confirm_delete.html'
    success_url = reverse_lazy('ip_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "IP eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)

from django.shortcuts import get_object_or_404, redirect
import subprocess

@login_required
def toggle_ip_status(request, pk):
    ip = get_object_or_404(DireccionIP, pk=pk)
    
    try:
        # Ejecutar ping nativo (-c 1 paquete, -W 1 segundo de timeout)
        result = subprocess.run(['ping', '-c', '1', '-W', '1', ip.direccion_ip], capture_output=True, text=True)
        if result.returncode == 0:
            ip.estado = 'ACTIVA'
            messages.success(request, f"Ping exitoso: La IP {ip.direccion_ip} está respondiendo (ACTIVA).")
        else:
            ip.estado = 'INACTIVA'
            messages.warning(request, f"Ping fallido: La IP {ip.direccion_ip} no responde (INACTIVA).")
    except Exception as e:
        ip.estado = 'INACTIVA'
        messages.error(request, f"Error al hacer ping a la IP {ip.direccion_ip}: {str(e)}")
        
    ip.save()
    return redirect('ip_list')
