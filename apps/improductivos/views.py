from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.core import serializers
from apps.improductivos.forms import ImproductivosForm, ImproductivosFormEdit, ImproductivosFormQr, ImproductivosFormReport  # Importar formulario
from datetime import datetime  # importar time
from apps.improductivos.models import MantosImp
from apps.producciones.models import Producciones
from .report import ImproductivoReportPDF
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from .filter import OrderFilter
# from noob.utils import render_to_pdf  # imp
import datetime as tiempo
import urllib.parse

# Create your views here.
# Vistas basadas en funciones


def index(request):  # Declaro la vistas y renderizo las mismas, llamando a las plantillas de cada vistas
	return render(request, "improductivos/index.html")


def improductivos_form(request):
	if request.method == "POST":  # Si la petición es un POST
		# Se invoca el modelo, mediante peticicón post
		form = ImproductivosForm(request.POST)
		now = datetime.now()
		fecha = now.strftime("%Y-%m-%d")
		time = now.strftime("%H:%M:%S")
		if form.is_valid():
			# Limpiando la variable problema
			problema = (form.cleaned_data['problema'])
			if problema == "electrico" or problema == "mecanico":  # Definir el tipo del de problema
				tipo_problema = "mantenimiento"
			else:
				tipo_problema = "produccion"
			# Pasamos form.save(commit=False), con esto le decimos que no
			# queremos guardar el formulario aún,  pasando el formulario a otra
			# variable podemos agregar la fecha y otras variables
			formulario = form.save(commit=False)
			formulario.tipo_problema = tipo_problema
			formulario.fecha = fecha
			formulario.hora_problema = time
			"""lineas = ChoicesLinea.objects.filter(lineas__in=numero_linea) # Otra Manera de guardar campos ManyToMany
			#formulario = form.save(commit=True)
			#formulario.numero_linea.set(lineas)"""
			formulario = form.save(commit=True)  # Se prepara el formulario para ser guardado
			formulario.save()
			# le paso el nombre de la app y el name de la url
			return redirect('improductivos:improductivos_form')
		else:
			print("Usuario envío formulario no valido")
	else:
		form = ImproductivosForm()

	return render(request, 'improductivos/improductivos_form.html', {'form': form})


def improductivos_qr(request):  # por codigo QR
	if request.method == "POST":  # Si la petición es un GET
		# Se invoca el modelo, mediante peticicón GET
		form = ImproductivosFormQr(request.POST)
		now = datetime.now()
		fecha = now.strftime("%Y-%m-%d")
		time = now.strftime("%H:%M:%S")
		if form.is_valid():
			problema = (form.cleaned_data['problema'])
			if problema == "electrico" or problema == "mecanico":  # Definir el tipo de problema
				tipo_problema = "mantenimiento"
			else:
				tipo_problema = "produccion"
			formulario = form.save(commit=False)
			formulario.tipo_problema = tipo_problema
			formulario.fecha = fecha
			formulario.hora_problema = time
			formulario = form.save(commit=True)
			formulario.save()
			# le paso el nombre de la app y el name de la url
			return redirect('improductivos:improductivos_list')
		else:
			print("Envio de datos no valido")
	else:
		form = ImproductivosFormQr(request.GET)
	return render(request, 'improductivos/improductivos_form_qr.html', {'form': form})


def improductivo_solve(request, id_imp):
	now = datetime.now()
	fecha = now.date()
	time = now.strftime("%H:%M:%S")
	improductivo_solve = MantosImp.objects.filter(
		id=id_imp)  # Filtrar el improductivo resuelto
	# Obtener la fecha,hora de dicho problema para calcular el improductivo
	hora_problema = MantosImp.objects.get(id=id_imp).hora_problema
	fecha_problema = MantosImp.objects.get(id=id_imp).fecha
	# Combinar fecha y hora, obtenida de la base de datos
	fecha_hora_problema = datetime.combine(fecha_problema, hora_problema)
	improductivo = now - fecha_hora_problema  # Calculo del improductivo
	improductivo_H = (improductivo.days * 24 + improductivo.seconds //
					  3600)  # Calculo de hora del improductivo
	improductivo_M = (improductivo.seconds // 60) % 60  # Calculo de los minutos del improductivo
	improductivo_S = improductivo.seconds % 60  # Calculo de los segundos del improductivo
	# Concatenar el total del improductivo
	improductivo_total = '{}:{}:{}'.format(improductivo_H, improductivo_M, improductivo_S)
	try:
		improductivo_solve.update(hora_solucion=time, tiempo_improductivo=improductivo_total)
		return redirect('improductivos:improductivos_list_solve')
	except Exception as err:
		print(err)
		return redirect('improductivos:improductivos_list_solve')
	# Otra forma de actualizar
	# improductivo_solve=MantosImp.objects.get(id=id_imp)
	# improductivo_solve.hora_solucion=time
	# improductivo_solve.save()

#####################vistas basadas en clases###################

 # Listar improductivos


class ImproductivosList(ListView):
	ordering = ['-fecha']
	template_name = 'improductivos/improductivos_list.html'  # plantilla a utilizar
	paginate_by = 20  # paginar la base de datos o objetos
	context_url = False
	# Sobreescribir el query_set

	def get_queryset(self):
		now = datetime.now()
		fecha = now.strftime("%Y-%m-%d")
		self.myFilter = OrderFilter(self.request.GET,queryset=MantosImp.objects.all().order_by('-fecha', '-hora_problema'))
		queryset = self.myFilter.qs
		return queryset

	# Enviarle el contexto al html
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['myFilter'] = self.myFilter
		if self.request.GET: # Enviar contexto para cambiar de pagina
			q = self.request.GET
			if 'page' in q:
				a = q.copy()
				del a['page']
				context['page'] = a.urlencode()
			else:
				context['page'] = q.urlencode()

		return context


# Listar improductivos a resolver
class ImproductivosListSolve(ListView):
	queryset = MantosImp.objects.filter(hora_solucion=None)
	model = queryset
	ordering = ['-fecha']
	template_name = 'improductivos/improductivos_list_solve.html'
	paginate_by = 10

# Actualizar o editar improductivo


class ImproductivosUpdate(UpdateView):
	model = MantosImp
	form_class = ImproductivosFormEdit  # le pasa al html el form como contexto
	template_name = 'improductivos/improductivos_form_edit.html'
	success_url = reverse_lazy('improductivos:improductivos_list')


# le pasa al html el obejeto, es decir, object.id,obeject.fecha
class ImproductivosDelete(DeleteView):
	model = MantosImp
	template_name = 'improductivos/improductivos_form_delete.html'
	success_url = reverse_lazy('improductivos:improductivos_list')


# Generar Reporte PDF ReportLab


class ImproductivosReport(View):
	def get(self,request):
		form = ImproductivosFormReport()
		return render(request, 'improductivos/improductivos_form_report.html', {'form': form, })

	def post(self,request):
		form = ImproductivosFormReport(request.POST)
		if form.is_valid():
			op = (form.cleaned_data['produccion'])
			fecha_gte = (form.cleaned_data['fecha_gte'])
			fecha_lte = (form.cleaned_data['fecha_lte'])
			usuario = str(request.user.first_name + " " + request.user.last_name)
			improductivos_report = ImproductivoReportPDF(op=op,fecha_gte=fecha_gte,fecha_lte=fecha_lte,usuario=usuario)
			pdf = improductivos_report.make_report()
			if pdf:
				# Indicamos el tipo de contenido a devolver, en este caso un pdf
				response = HttpResponse(content_type='application/pdf')
				filename = "Reporte_improductivo_%s_%s.pdf" % (op, datetime.now())
				content = "attachment; filename=%s" % (filename)
				response['Content-Disposition'] = content
				response.write(pdf)
				return response
			else:
				return HttpResponse("Error! =(")
			
#################################################################


def handler404(request):
	return render(request, '404.html', status=404)


def handler500(request):

	return render(request, '500.html', status=500)
