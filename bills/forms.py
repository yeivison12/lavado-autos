from django import forms
from .models import Recibo  

class ReciboForm(forms.ModelForm):
    class Meta:
        model = Recibo
        fields = ['monto', 'comentario']
        widgets = {
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el precio'}),
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Motivo del cambio de precio (opcional)'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['monto'].required = False
        self.fields['comentario'].required = False