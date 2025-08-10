from django import forms
from datetime import datetime
from django.utils.timezone import make_aware, localtime, get_current_timezone

from babel.dates import format_datetime


from django import forms
from .models import Reserva, HorarioDisponible

class ReservaForm(forms.ModelForm):
    horario = forms.ModelChoiceField(
        queryset=HorarioDisponible.objects.filter(disponible=True),
        widget=forms.Select(attrs={
            'class': 'form-select mb-3',
            'id': 'horario',
            'required': True
        }),
        empty_label=" Selecciona un horario disponible"
    )

    class Meta:
        model = Reserva
        fields = ['nombre', 'email', 'telefono', 'servicio', 'horario']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control mb-3',
                'id': 'nombre',
                'placeholder': 'Ingresa tu nombre completo',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control mb-3',
                'id': 'email',
                'placeholder': 'Ingresa tu correo electrónico',
                'required': True
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control mb-3',
                'id': 'telefono',
                'placeholder': 'Ingresa tu número de teléfono',
                'required': True
            }),
            'servicio': forms.Select(attrs={
                'class': 'form-select mb-3',
                'id': 'servicio',
                'required': True
            }, choices=[
                ('', ' Selecciona un servicio'),
                ('basico', ' Lavado Básico - $10.00'),
                ('premium', ' Lavado Premium - $20.00'),
                ('completo', ' Lavado Completo - $30.00'),
            ]),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Poblar el campo `fecha_hora` con los horarios disponibles
        horarios_disponibles = HorarioDisponible.objects.filter(disponible=True)
        if not horarios_disponibles.exists():
            self.fields['horario'].choices = [('', ' No hay horarios disponibles')]
        else:
            timezone = get_current_timezone()
            self.fields['horario'].choices = [
                (
                    f"{horario.id}",
                    format_datetime(
                        localtime(
                            make_aware(datetime.combine(horario.fecha, horario.hora), timezone)
                        ),
                        "EEEE, d 'de' MMMM 'del' y 'a las' h:mm a",
                        locale='es'
                    )
                )
                for horario in horarios_disponibles
            ]

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']
        telefono = ''.join(filter(lambda x: x in '+0123456789', telefono))
        
        if not telefono.startswith('+57'):
            telefono = '+57' + telefono.lstrip('+')
        if len(telefono) < 10:
            raise forms.ValidationError("Teléfono demasiado corto.")


        return telefono
