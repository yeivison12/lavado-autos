from django import forms
from bills.models import Tarifa
from orders.models import Reserva, HorarioDisponible
from django.utils.timezone import now
class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['nombre', 'email', 'telefono', 'servicio','horario', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'servicio': forms.Select(attrs={'class': 'form-select'}),
            'horario': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
class ReservaFormUpdate(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['nombre', 'email', 'telefono', 'servicio', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'servicio': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']
        telefono = ''.join(filter(lambda x: x in '+0123456789', telefono))
        
        if not telefono.startswith('+57'):
            telefono = '+57' + telefono.lstrip('+')
        return telefono

class HorarioDisponibleForm(forms.ModelForm):
    class Meta:
        model = HorarioDisponible
        fields = ['fecha', 'hora', 'disponible']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')

    
        if fecha and fecha < now().date():
            raise forms.ValidationError("No se puede seleccionar una fecha en el pasado.")
        if HorarioDisponible.objects.filter(fecha=fecha, hora=hora).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe un horario disponible con esta fecha y hora.")

class CrearTarifaForm(forms.ModelForm):
    class Meta:
        model = Tarifa
        fields = ['nombre', 'monto', 'descripcion', 'imagen', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
