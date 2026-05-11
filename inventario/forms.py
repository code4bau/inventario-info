from django import forms
from .models import Transaction, Item

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['item', 'tipo', 'persona', 'area', 'observaciones', 'firma']
        widgets = {
            'firma': forms.HiddenInput(),
        }

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['nombre', 'codigo_patrimonial', 'categoria', 'responsable', 'area', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_patrimonial': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'responsable': forms.Select(attrs={'class': 'form-control'}),
            'area': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
