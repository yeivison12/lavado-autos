from django.contrib import admin
from .models import Reserva, HorarioDisponible
from django import forms

# Register your models here.
class HorarioDisponibleAdminForm(forms.ModelForm):
    class Meta:
        model = HorarioDisponible
        fields = '__all__'
        widgets = {
            'hora': forms.TimeInput(format='%I:%M %p', attrs={'type': 'time'}),
        }

class HorarioDisponibleAdmin(admin.ModelAdmin):
    form = HorarioDisponibleAdminForm
    list_display = ('fecha', 'hora', 'disponible')
    list_filter = ('fecha', 'disponible')
    search_fields = ('fecha', 'hora')
admin.site.register(Reserva)
admin.site.register(HorarioDisponible,HorarioDisponibleAdmin)


