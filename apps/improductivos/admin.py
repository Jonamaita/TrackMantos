from django.contrib import admin
from apps.improductivos.models import MantosImp, ChoicesLinea
from apps.producciones.models import Producciones
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from import_export.fields import Field
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from import_export.widgets import ForeignKeyWidget

# Register your models here.
# Modelo de improductivos, con la app import export to excel


class MantosImpResource(resources.ModelResource):
    lineas = Field()  # Se crea un campo nuevo para exportar todas las lineas

    # Se crea un campo produccion para expotar las producciones como clave foranea 'orden_produccion'.
    # Ya que sino exportaria la ID de la producción, ya que, es la PK de ese modelo
    produccion = Field(column_name='produccion', attribute='produccion', widget=ForeignKeyWidget(
        Producciones, 'orden_produccion'))

    class Meta:
        model = MantosImp
        fields = ('problema', 'tipo_problema', 'comentario', 'numero_manto',
                  'lineas', 'fecha', 'hora_problema', 'hora_solucion', 'tiempo_improductivo', 'produccion')
        exclude = ('id', )
        export_order = ('problema', 'tipo_problema', 'comentario', 'numero_manto',
                        'lineas', 'fecha', 'hora_problema', 'hora_solucion', 'tiempo_improductivo', 'produccion')

    def dehydrate_lineas(self, obj):  # Metodo para retornar todos los valores de las lineas
        return ",".join([l.linea for l in obj.numero_linea.all()])

    # def dehydrate_produccion(self, obj):  # Metodo opcional para retornar la orden de produccion o clave foranea
    #    return obj.produccion.orden_produccion


@admin.register(MantosImp)
class ViewAdmin(ImportExportModelAdmin):
    list_display = ('problema', 'tipo_problema', 'comentario', 'numero_manto',
                    'get_numero_linea', 'fecha', 'hora_problema', 'hora_solucion', 'tiempo_improductivo', 'produccion')
    list_filter = (('fecha', DateRangeFilter), 'problema',
                   'produccion', 'tipo_problema')
    # fields =('problema', 'comentario', 'fecha',) solo se puede editar estos
    # campos
    resource_class = MantosImpResource  # Personalizando Import/Export

    def get_numero_linea(self, obj):  # Metodo para retornar el campo many to many
        return ",".join([l.linea for l in obj.numero_linea.all()])
    # le cambio la descripción para que en admin se muestra como Lineas
    get_numero_linea.short_description = "Lineas"


@admin.register(ChoicesLinea)
class ChoicesLineaAdmin(admin.ModelAdmin):
    list_display = ('linea',)
