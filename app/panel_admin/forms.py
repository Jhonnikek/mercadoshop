from django import forms
from .models import Tienda


class TiendaForm(forms.ModelForm):
    class Meta:
        model = Tienda
        fields = ['nombre', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nombre de la tienda',
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Dirección de la tienda',
            }),
        }
