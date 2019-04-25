from django.db import models

# Create your models here.
class Producciones(models.Model):
	orden_produccion= models.CharField(primary_key=True,max_length=50)
	minera= models.CharField(max_length=50)
	comentario=models.CharField(max_length=100,blank=True)
	fecha_inicio=models.DateField(auto_now=False,editable=True,blank=True,null=True)
	hora_inicio=models.TimeField(auto_now=False,editable=True,null=True)
	fecha_finalizacion=models.DateField(auto_now=False,editable=True,blank=True,null=True)	
	hora_finalizacion=models.TimeField(auto_now=False,editable=True,blank=True,null=True)
	
	def __str__(self):
		return '{} - Fecha de Inicio: {}'.format(self.orden_produccion, self.fecha_inicio)
	