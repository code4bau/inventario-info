from django import forms
from .models import Transaction, Item

class TransactionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['persona'].empty_label = "Otro (Escribir nombre ↓)"
        self.fields['persona'].required = False

    class Meta:
        model = Transaction
        fields = ['item', 'tipo', 'persona', 'responsable_otro', 'area', 'observaciones', 'firma']
        widgets = {
            'firma': forms.HiddenInput(),
            'persona': forms.Select(attrs={'class': 'form-control'}),
            'responsable_otro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del responsable'}),
        }

class ItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['responsable'].empty_label = "Otro (Escribir nombre ↓)"
        self.fields['responsable'].required = False

    class Meta:
        model = Item
        fields = ['nombre', 'categoria', 'responsable', 'responsable_otro', 'area', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'responsable': forms.Select(attrs={'class': 'form-control'}),
            'responsable_otro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del responsable'}),
            'area': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
