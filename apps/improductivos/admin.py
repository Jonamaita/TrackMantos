from django.contrib import admin
from apps.improductivos.models import MantosImp, ChoicesLinea
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from import_export.fields import Field
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

# Register your models here.
# Modelo de improductivos, con la app import export to excel


class MantosImpResource(resources.ModelResource):
    lineas = Field()  # Se crea un campo nuevo para exportar todas las lineas

    class Meta:
        model = MantosImp
        fields = ('problema', 'tipo_problema', 'comentario', 'numero_manto',
                  'lineas', 'fecha', 'hora_problema', 'hora_solucion', 'produccion')
        exclude = ('id', )
        export_order = ('problema', 'tipo_problema', 'comentario', 'numero_manto',
                        'lineas', 'fecha', 'hora_problema', 'hora_solucion', 'produccion')

    def dehydrate_lineas(self, obj):  # Metodo para retornar todos los valores de las lineas
        return ",".join([l.linea for l in obj.numero_linea.all()])


@admin.register(MantosImp)
class ViewAdmin(ImportExportModelAdmin):
    list_display = ('problema', 'tipo_problema', 'comentario', 'numero_manto',
                    'get_numero_linea', 'fecha', 'hora_problema', 'hora_solucion', 'produccion')
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
