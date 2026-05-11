from django import forms
from .models import DireccionIP

class IPForm(forms.ModelForm):
    class Meta:
        model = DireccionIP
        fields = ['direccion_ip', 'area', 'dispositivo', 'estado', 'descripcion']
        widgets = {
            'direccion_ip': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 192.168.1.50'}),
            'area': forms.Select(attrs={'class': 'form-control'}),
            'dispositivo': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. PC Recepción (Opcional)'}),
        }
