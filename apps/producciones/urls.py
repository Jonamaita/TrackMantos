from django.urls import path,re_path,include
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required # Solo entra las persona que son parte del staff
from apps.producciones.views import produccion_form,producciones_json,ProduccionesList, ProduccionesUpdate,ProduccionesDelete,ProduccionesListIinitClosed,iniciar_produccion,cerrar_produccion,produccion_delete
app_name="producciones"

urlpatterns = [
	#path('', index, name="index"),
	path('',login_required(produccion_form),name="produccion_form"),
	path('producciones_list/',login_required(ProduccionesList.as_view()),name="producciones_list"),
	path('produccones_edit/<int:pk>/',staff_member_required(ProduccionesUpdate.as_view()),name="producciones_edit"),
	#path('producciones_delete/<int:pk>/',staff_member_required(ProduccionesDelete.as_view()),name="producciones_delete"), # Por vista
	#path('producciones_delete/<int:pk>/',staff_member_required(produccion_delete),name="producciones_delete"),
	path('producciones_list_init_closed/',staff_member_required(ProduccionesListIinitClosed.as_view()),name="producciones_list_init_closed"),
	path('iniciar_produccion/<int:pk>/',staff_member_required(iniciar_produccion),name="iniciar_produccion"), # En la vista, se recibe orden_produccion. La vista debe recibir con el mismo nombre de variable
	path('cerrar_produccion/<int:pk>/',staff_member_required(cerrar_produccion),name="cerrar_produccion"),
	path('producciones_json',login_required(producciones_json),name="producciones_json")


	
]