from django import forms
from .models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['item', 'tipo', 'persona', 'area', 'observaciones', 'firma']
        widgets = {
            'firma': forms.HiddenInput(),
        }
