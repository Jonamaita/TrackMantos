from django.contrib import admin
from apps.producciones.models import Producciones
from import_export.admin import ImportExportModelAdmin
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

# Register your models here.


@admin.register(Producciones)
class ViewAdmin(ImportExportModelAdmin):
    list_display = ('orden_produccion', 'minera', 'comentario', 'fecha_inicio',
                    'hora_inicio', 'fecha_finalizacion', 'hora_finalizacion',)
    list_filter = (('fecha_inicio', DateRangeFilter), 'minera')
