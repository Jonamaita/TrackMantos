from django import forms
from apps.producciones.models import Producciones
from django.contrib.auth import authenticate
import re
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


def validate_orden_produccio(value):
    val = RegexValidator(
        regex=r'^[\w-]+$', message='Ingrese una OC valida, solo con el siguiente caracter especial valido "-" y sin espacios.')
    val(value)


class ProduccionesForm(forms.ModelForm):
    orden_produccion = forms.CharField(validators=[validate_orden_produccio], label='orden_produccion', max_length=20, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'orden_produccion', 'style': 'color:black', 'autocomplete': 'off', 'autofocus': '', 'placeholder': 'OC1234'}))
    minera = forms.CharField(label='minera', max_length=20, required=True, widget=forms.TextInput(attrs={
                             'class': 'form-control', 'id': 'minera', 'style': 'color:black', 'autocomplete': 'on', 'placeholder': 'Escondida'}))
    comentario = forms.CharField(label='comentario', max_length=100, required=False, widget=forms.Textarea(
        attrs={'class': 'form-control', 'id': 'comentario', 'style': 'color:black', 'rows': '3'}))

    class Meta():
        model = Producciones
        fields = ['orden_produccion', 'minera', 'comentario']


class ProduccionesFormEdit(forms.ModelForm):
    orden_produccion = forms.CharField(validators=[validate_orden_produccio], label='orden_produccion', max_length=20, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'orden_produccion_producciones', 'style': 'color:black', 'autocomplete': 'off', 'autofocus': '', 'placeholder': 'OC1234'}))
    minera = forms.CharField(label='minera', max_length=20, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control', 'id': 'minera_producciones', 'style': 'color:black', 'autocomplete': 'on', 'placeholder': 'Escondida'}))
    comentario = forms.CharField(label='comentario', max_length=100, required=False, widget=forms.Textarea(
        attrs={'class': 'form-control', 'id': 'comentario_producciones', 'style': 'color:black', 'rows': '3'}))
    fecha_inicio = forms.DateField(label='fecha_incio', required=False, widget=forms.SelectDateWidget(
        attrs={'class': 'form-control', 'style': 'color:black', 'title': 'Edite fecha de inicio de la producción', 'id': 'fecha_inicio_producciones'}))
    hora_inicio = forms.TimeField(label='fecha_incio', required=False, widget=forms.TimeInput(format='%H:%M:%S', attrs={
        'class': 'form-control', 'style': 'color:black', 'title': 'Edite hora de inicio de la producción', 'id': 'hora_inicio_producciones'}))
    fecha_finalizacion = forms.DateField(label='fecha_incio', required=False, widget=forms.SelectDateWidget(
        attrs={'class': 'form-control', 'style': 'color:black', 'title': 'Edite fecha de finalización de la producción', 'id': 'fecha_finalizacion_producciones'}))
    hora_finalizacion = forms.TimeField(label='fecha_incio', required=False, widget=forms.TimeInput(format='%H:%M:%S', attrs={
        'class': 'form-control', 'style': 'color:black', 'title': 'Edite hora de finalización de la producción', 'id': 'hora_finalizacion_producciones'}))

    class Meta():
        model = Producciones
        fields = ['orden_produccion', 'minera', 'comentario', 'fecha_inicio',
                  'hora_inicio', 'fecha_finalizacion', 'hora_finalizacion']


# Formulario para eliminar producción con contraseña
class DeleteConfirmForm(forms.Form):
    password = forms.CharField(label='password', widget=forms.PasswordInput(
        attrs={'class': 'form-control is-invalid', 'id': 'password_confirm', 'style': 'color:black', 'autocomplete': 'password_confirm'}))

    def __init__(self, *args, **kwargs):  # sobre escribir el metodo init para tomar las palabras claves y tomar el request
        # se debe pasar el request cuando se llama el  form.
        # form=DeleteConfirmForm(request.POST,request=request)
        self.request = kwargs.pop('request', None)
        super(DeleteConfirmForm, self).__init__(*args, **kwargs)

    def clean(self):
        password = self.cleaned_data.get('password')
        if self.request.user.is_authenticated:  # Indentifico el usuario que esta en la sesión
            username = self.request.user.username
        else:
            username = None
        user = authenticate(username=username, password=password)
        if user == None:
            self._errors['password'] = 'Clave Invalida'
        elif not self.request.user.is_active:
            self._errors['password'] = 'Usuario Inactivo'
        return self.cleaned_data
