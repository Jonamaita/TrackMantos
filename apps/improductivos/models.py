from django.db import models
from apps.producciones.models import Producciones

# Create your models here.


class ChoicesLinea(models.Model):

    linea = models.CharField(max_length=50, unique=True, editable=True,)

    def __str__(self):
        return '{}'.format(self.linea)


class MantosImp(models.Model):  # Declaro modelo de la base de datos
    problema = models.CharField(max_length=50)
    tipo_problema = models.CharField(max_length=50, editable=True)
    numero_manto = models.PositiveIntegerField(blank=True, null=True)
    numero_linea = models.ManyToManyField(ChoicesLinea)  # Relationship Fields
    comentario = models.CharField(max_length=100)
    fecha = models.DateField(auto_now=False, null=True, editable=True, blank=True)
    hora_problema = models.TimeField(auto_now=False, null=True, editable=True, blank=True)
    hora_solucion = models.TimeField(auto_now=False, null=True, editable=True, blank=True)
    tiempo_improductivo = models.TimeField(auto_now=False, null=True, editable=True, blank=True)
    produccion = models.ForeignKey(Producciones, null=True, blank=True,
                                   on_delete=models.CASCADE)  # Relationship Fields

    #def __str__(self):
    # return 'Problema: {},Comentario: {},Fecha: {},Hora del Problema: {},Hora
    # de Solución: {}'.format(self.problema,self.comentario, self.fecha,
    # self.hora_problema, self.hora_solucion)
