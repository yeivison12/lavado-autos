from django import forms
from .models import Worker

class WorkerForm(forms.ModelForm):
    class Meta:
        model = Worker
        exclude = ['user']
        fields = ['user','bio' ,'avatar']