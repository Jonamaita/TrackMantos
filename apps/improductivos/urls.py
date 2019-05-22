from django.urls import path,re_path,include
from apps.improductivos.views import index,improductivos_form,ImproductivosList,ImproductivosListSolve,ImproductivosUpdate,ImproductivosDelete, improductivos_qr,improductivo_solve
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required # Solo entra las persona que son parte del staff
app_name="improductivos" # Esto es para darle un nombre a la vista de la amplicación y manejar las rutas desde python a apartir de nombres

urlpatterns = [
    path('', index, name="index"),
    path('improductivos/',login_required(improductivos_form),name="improductivos_form"),#si fuera vista basada en clases, se le pasa el parametro ImproductivoCreate, como esta definida en las vistas basadas en clases
    path('improductivos_list/',login_required(ImproductivosList.as_view()),name="improductivos_list"), # si fuera vista basada en funciones, se le pasa el parametro improductivos_list, como esta definida en las vistas
    path('improductivos_edit/<int:pk>/',staff_member_required(ImproductivosUpdate.as_view()),name="improductivos_edit"), #paso primary key, ya que, es por vista basada en clases.
   	path('improductivos_delete/<int:pk>/',staff_member_required(ImproductivosDelete.as_view()),name="improductivos_delete"),
   	path('improductivos_qr/',login_required(improductivos_qr),name="improductivos_get"),
   	path('improductivos_list_solve/',login_required(ImproductivosListSolve.as_view()),name="improductivos_list_solve"),
   	path('improductivo_solve/<int:id_imp>/',login_required(improductivo_solve),name="improductivo_solve"), # En la vista recibe id_imp, en la vista debe tener el mismo nombre de variable
  
]
