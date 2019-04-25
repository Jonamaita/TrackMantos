from django.contrib import admin
from apps.improductivos.models import MantosImp
from import_export.admin import ImportExportModelAdmin
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

# Register your models here.
# Modelo de improductivos, con la app import export to excel
@admin.register(MantosImp)
class ViewAdmin(ImportExportModelAdmin):
	list_display = ('problema','tipo_problema', 'comentario', 'fecha','hora_problema','hora_solucion','produccion')
	list_filter=(('fecha',DateRangeFilter),'problema','produccion','tipo_problema')

	#fields =('problema', 'comentario', 'fecha',) solo se puede editar estos campos



