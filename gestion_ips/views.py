from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from .models import DireccionIP
from .forms import IPForm

class IPListView(ListView):
    model = DireccionIP
    template_name = 'gestion_ips/ip_list.html'
    context_object_name = 'ips'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return DireccionIP.objects.filter(direccion_ip__icontains=query) | DireccionIP.objects.filter(descripcion__icontains=query)
        return DireccionIP.objects.all()

class IPCreateView(CreateView):
    model = DireccionIP
    form_class = IPForm
    template_name = 'gestion_ips/ip_form.html'
    success_url = reverse_lazy('ip_list')

    def form_valid(self, form):
        messages.success(self.request, "IP registrada exitosamente.")
        return super().form_valid(form)

class IPUpdateView(UpdateView):
    model = DireccionIP
    form_class = IPForm
    template_name = 'gestion_ips/ip_form.html'
    success_url = reverse_lazy('ip_list')

    def form_valid(self, form):
        messages.success(self.request, "IP actualizada exitosamente.")
        return super().form_valid(form)

class IPDeleteView(DeleteView):
    model = DireccionIP
    template_name = 'gestion_ips/ip_confirm_delete.html'
    success_url = reverse_lazy('ip_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "IP eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)

from django.shortcuts import get_object_or_404, redirect

def toggle_ip_status(request, pk):
    ip = get_object_or_404(DireccionIP, pk=pk)
    if ip.estado == 'ACTIVA':
        ip.estado = 'INACTIVA'
        messages.warning(request, f"Ping: La IP {ip.direccion_ip} ahora está Inactiva.")
    else:
        ip.estado = 'ACTIVA'
        messages.success(request, f"Ping: La IP {ip.direccion_ip} ahora está Activa.")
    ip.save()
    return redirect('ip_list')
