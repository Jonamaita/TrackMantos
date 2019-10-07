from django import forms
from apps.improductivos.models import MantosImp
from apps.producciones.models import Producciones

PROBLEMA_PRODUCCION_CHOICES = (
    ('ruedas', 'Ruedas'), ('goteros', 'Goteros'), ('troquelado', 'Troquelado'), ('film', 'Film'), ('regulaciones', 'Regulaciones'))
PROBLEMAS_CHOICES = (('electrico', 'Eléctrico',), ('mecanico',
                                                   'Mecánico',), ('PRODUCCIÓN', PROBLEMA_PRODUCCION_CHOICES))
TIPO_PROBLEMA = (('mantenimiento', 'Mantenimiento'),
                 ('produccion', 'Producción'))


class ImproductivosForm(forms.ModelForm):

    produccion = forms.ModelChoiceField(queryset=Producciones.objects.filter(fecha_finalizacion=None).exclude(
        fecha_inicio=None), empty_label=None, widget=forms.Select(attrs={'class': 'form-control', 'style': 'color:black', 'id': 'producciones', 'required': False}))

    numero_manto = forms.IntegerField(min_value=1, required=True, widget=forms.NumberInput(
        attrs={'class': 'form-control', 'title': 'Indique el numero de manto', 'style': 'color:black', 'id': 'numero_manto'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['produccion'].queryset

    class Meta:
        model = MantosImp  # Utilizamos nuestro modelo
        fields = ['problema',  # Campos del modelo
                  'comentario',
                  'numero_manto',
                  'numero_linea',
                  #'fecha'.
                  'produccion'
                  ]
        labels = {'problema': 'Problema',  # Etiquetas para los compos del formulario
                  'comentario': 'Comentario',
                  'numero_manto': 'Numero de Manto',
                  'numero_linea': 'Numero de Lineas',
                  #'fecha': 'Fecha',
                  'produccion': 'Produccion'
                  }
        widgets = {'problema': forms.RadioSelect(choices=PROBLEMAS_CHOICES, attrs={'title': 'Seleccione un problema', 'required': True}),  # Para dar diseño a los campos
                   'comentario': forms.Textarea(attrs={'class': 'form-control', 'title': 'Escriba un comentario', 'rows': '3', 'style': 'color:black', 'id': 'comentario'}),
                   'numero_linea': forms.CheckboxSelectMultiple(attrs={'title': 'Indique lineas afectadas'}),
                   #'fecha': forms.SelectDateWidget(attrs={'class':'form-control '})

                   }


class ImproductivosFormEdit(forms.ModelForm):
    numero_manto = forms.IntegerField(min_value=1, required=True, widget=forms.NumberInput(
        attrs={'class': 'form-control', 'title': 'Indique el numero de manto', 'style': 'color:black', 'id': 'numero_manto'}))

    class Meta:
        model = MantosImp
        fields = ['tipo_problema',  # Campos del modelo
                  'problema',
                  'comentario',
                  'numero_manto',
                  'numero_linea',
                  'fecha',
                  'hora_problema',
                  'hora_solucion',
                  'tiempo_improductivo',
                  'produccion'
                  ]
        # Etiquetas para los compos del formulario
        labels = {'tipo_problema': 'Tipo de problema',
                  'problema': 'Problema',
                  'comentario': 'Comentario',
                  'numero_manto': 'Numero de Manto',
                  'numero_linea': 'Numero de Lineas',
                  'fecha': 'Fecha',
                  'hora_problema': 'Hora del problema',
                  'hora_solucion': 'Hora de la solución',
                  'tiempo_improductivo': 'Tiempo improductivo'
                  }
        # Para dar diseño a los campos
        widgets = {'tipo_problema': forms.Select(choices=TIPO_PROBLEMA, attrs={'class': 'form-control', 'title': 'Seleccione un tipo de problema', 'required': True, 'style': 'color:black'}),
                   'problema': forms.RadioSelect(choices=PROBLEMAS_CHOICES, attrs={'title': 'Seleccione un problema', 'required': True}),
                   'comentario': forms.Textarea(attrs={'class': 'form-control', 'title': 'Escriba un comentario', 'rows': '3', 'style': 'color:black', 'id': 'comentario'}),
                   'numero_linea': forms.CheckboxSelectMultiple(attrs={'title': 'Indique lineas afectadas', }),
                   'fecha': forms.SelectDateWidget(attrs={'class': 'form-control', 'title': 'Edite fecha', 'style': 'color:black', }),
                   'hora_problema': forms.TimeInput(format='%H:%M:%S', attrs={'class': 'form-control', 'style': 'color:black', 'title': 'Edite la hora del problema', 'id': 'hora_problema'}),
                   'hora_solucion': forms.TimeInput(format='%H:%M:%S', attrs={'class': 'form-control', 'style': 'color:black', 'title': 'Edite la hora de solución', 'id': 'hora_solucion'}),
                   'tiempo_improductivo': forms.TimeInput(format='%H:%M:%S', attrs={'class': 'form-control', 'style': 'color:black', 'title': 'Edite el tiempo de improductivo', 'id': 'tiempo_improductivo'}),
                   'produccion': forms.Select(attrs={'class': 'form-control', 'style': 'color:black'})


                   }


class ImproductivosFormQr(forms.ModelForm):
    # produccion, realiza un queryset, el cual, trae todas la producciones que
    # no sean finalizados y que se hallan iniciado (exclude fehca_inicio=None)
    produccion = forms.ModelChoiceField(queryset=Producciones.objects.filter(fecha_finalizacion=None).exclude(
        fecha_inicio=None), empty_label=None, widget=forms.Select(attrs={'class': 'form-control', 'style': 'color:black', 'id': 'producciones', 'required': True}))
    numero_manto = forms.IntegerField(min_value=1, required=True, widget=forms.NumberInput(
        attrs={'class': 'form-control', 'title': 'Indique el numero de manto', 'style': 'color:black', 'id': 'numero_manto'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['produccion'].queryset

    class Meta:
        model = MantosImp  # Utilizamos nuestro modelo
        fields = ['problema',  # Campos del modelo
                  'comentario',
                  'numero_manto',
                  'numero_linea',
                  'produccion'
                  ]
        labels = {'problema': 'Problema',  # Etiquetas para los compos del formulario
                  'comentario': 'Comentario',
                  'numero_manto': 'Numero de Manto',
                  'numero_linea': 'Numero de Lineas',
                  'produccion': 'Produccion'
                  }
        widgets = {'comentario': forms.Textarea(attrs={'class': 'form-control', 'title': 'Escriba un comentario', 'rows': '3', 'style': 'color:black', 'id': 'comentario'}),
                   'numero_linea': forms.CheckboxSelectMultiple(attrs={'title': 'Indique lineas afectadas', }),
                   'problema': forms.Select(choices=PROBLEMAS_CHOICES, attrs={'class': 'form-control', 'title': 'Seleccione un problema', 'style': 'color:black', 'required': True}), }


class ImproductivosFormReport(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['produccion'].queryset

    produccion = forms.ModelChoiceField(queryset=Producciones.objects.all(), empty_label=None, widget=forms.Select(
        attrs={'class': 'form-control', 'style': 'color:black', 'id': 'producciones', 'required': True}))
    fecha_gte = forms.DateField(input_formats=['%d-%m-%Y'], widget=forms.DateInput(
        attrs={'class': 'form-control', 'data-target': '#datepicker1', 'title': 'Indique fecha', 'style': 'color:black', 'id': 'fecha_gte', 'placeholder': 'introduzca fecha dd-mm-yyyy'}))
    fecha_lte = forms.DateField(input_formats=['%d-%m-%Y'], widget=forms.DateInput(
        attrs={'class': 'form-control', 'data-target': '#datepicker1', 'title': 'Indique fecha', 'style': 'color:black', 'id': 'fecha_lte', 'placeholder': 'introduzca fecha dd-mm-yyyy'}))
