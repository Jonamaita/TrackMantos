from django.urls import path,re_path,include
from django.contrib.auth.decorators import login_required
from apps.producciones.views import produccion_form,ProduccionesList, ProduccionesUpdate,ProduccionesDelete,ProduccionesListIinitClosed,iniciar_produccion,cerrar_produccion
from django_filters.views import FilterView
app_name="producciones"

urlpatterns = [
	#path('', index, name="index"),
	path('',login_required(produccion_form),name="produccion_form"),
	path('producciones_list/',login_required(ProduccionesList.as_view()),name="producciones_list"),
	path('produccones_edit/<slug:pk>/',login_required(ProduccionesUpdate.as_view()),name="producciones_edit"),
	path('producciones_delete/<slug:pk>/',login_required(ProduccionesDelete.as_view()),name="producciones_delete"),
	path('producciones_list_init_closed/',login_required(ProduccionesListIinitClosed.as_view()),name="producciones_list_init_closed"),
	path('iniciar_produccion/<slug:orden_produccion>/',login_required(iniciar_produccion),name="iniciar_produccion"), # En la vista, se recibe orden_produccion. La vista debe recibir con el mismo nombre de variable
	path('cerrar_produccion/<slug:orden_produccion>/',login_required(cerrar_produccion),name="cerrar_produccion")


	
]