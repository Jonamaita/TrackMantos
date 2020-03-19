from django.db import models

# Create your models here.


class Producciones(models.Model):
    orden_produccion = models.CharField(unique=True, max_length=50)
    minera = models.CharField(max_length=50)
    cantidad_mantos = models.PositiveIntegerField()
    comentario = models.CharField(max_length=100, blank=True)
    fecha_inicio = models.DateField(auto_now=False, editable=True, blank=True, null=True)
    hora_inicio = models.TimeField(auto_now=False, editable=True, null=True)
    fecha_finalizacion = models.DateField(auto_now=False, editable=True, blank=True, null=True)
    hora_finalizacion = models.TimeField(auto_now=False, editable=True, blank=True, null=True)
    tope_improductivo_produccion = models.PositiveIntegerField()  # Meta a cumplir de improductivo de producción
    tope_improductivo_mantenimiento = models.PositiveIntegerField()  # Meta a cumplir de improductivo de mantenimiento

    def __str__(self):
        return '{}'.format(self.orden_produccion)
