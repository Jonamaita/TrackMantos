import django_filters
from .models import MantosImp
from apps.producciones.models import Producciones
from django import forms


class OrderFilter(django_filters.FilterSet):
	produccion = django_filters.ModelChoiceFilter(field_name='produccion',queryset= Producciones.objects.all().distinct(),widget=forms.Select(attrs={'class':'form-control','style':'font-size: 13px'}))
	problema = django_filters.ModelChoiceFilter(field_name='problema',to_field_name='problema',queryset= MantosImp.objects.values_list('problema',flat=True).distinct(), widget=forms.Select(attrs={'class':'form-control','style':'font-size: 13px'}))
	tipo_problema = django_filters.ModelChoiceFilter(to_field_name='tipo_problema',queryset= MantosImp.objects.values_list('tipo_problema',flat=True).distinct(),widget=forms.Select(attrs={'class':'form-control','style':'font-size: 13px'}))
	start_date = django_filters.DateFilter(field_name='fecha',lookup_expr='gte', widget=forms.DateInput(attrs={'type':'date','id':'start_date','class':'form-control','style':'font-size: 13px'}))
	end_date = django_filters.DateFilter(field_name='fecha',lookup_expr='lte',widget=forms.DateInput(attrs={'type':'date','id':'end_date','class':'form-control','style':'font-size: 13px'}))
	class Meta:
		model = MantosImp
		labels = {'problema','Problema'}
		fields = ['problema','tipo_problema']