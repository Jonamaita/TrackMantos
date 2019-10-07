from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from apps.improductivos.forms import ImproductivosForm, ImproductivosFormEdit, ImproductivosFormQr, ImproductivosFormReport  # Importar formulario
from datetime import datetime  # importar time
from apps.improductivos.models import MantosImp
from apps.producciones.models import Producciones
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from noob.utils import render_to_pdf  # imp
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

# 3

#####################vistas basadas en clases###################

 # Listar improductivos


class ImproductivosList(ListView):
    model = MantosImp  # le paso el modelo
    ordering = ['-fecha']
    template_name = 'improductivos/improductivos_list.html'  # plantilla a utilizar
    paginate_by = 10  # paginar la base de datos o objetos
    context_url = False
    # Sobreescribir el query_set

    def get_queryset(self):
        now = datetime.now()
        fecha = now.strftime("%Y-%m-%d")
        queryset = MantosImp.objects.all().order_by('-fecha', '-hora_problema')

        if self.request.GET:  # Si hay una petición request GET intentar realizar un queryset
            a = self.request.GET
            try:
                # Desempacar el el diccionario enviado por el GET y hacer el
                # queryset
                queryset = MantosImp.objects.filter(
                    **a.dict()).order_by('-fecha', '-hora_problema')
                # Bandera para indicar que la petición enviada por el url es
                # correcta y utilizarla en los filtros
                self.context_url = True
            except Exception as err:
                print(err)
                self.context_url = False  # Bandera para indicar que la petición realizada por el url no es correcta y no reliza el self request para enviar el contexto a los filtros

        return queryset

    # Enviarle el contexto al html
    def get_context_data(self, **kwargs):
        now = datetime.now()
        fecha_1 = tiempo.timedelta(days=1)
        delta = now - fecha_1
        delta = delta.strftime("%Y-%m-%d")  # Fecha anterior a la actual
        fecha = now.strftime("%Y-%m-%d")  # Fecha actual
        context = super(ImproductivosList, self).get_context_data(**kwargs)
        # toma el valor fecha__gte en ese momento (si hay un request con
        # fecha__gte) si no lo tiene le asigna el valor delta
        context['context_fecha_gte'] = self.request.GET.get(
            'fecha__gte', delta)
        context['context_fecha_lte'] = self.request.GET.get(
            'fecha__lte', fecha)
        # Enviar en el contexto todos los problemas que estan en la base de
        # datos
        context['context_problema'] = MantosImp.objects.values(
            'problema').distinct()
        # Enviar en el contexto todas las producciones que estan en la base de
        # datos
        context['context_produccion'] = MantosImp.objects.all().distinct('produccion')
        # Enviar en el contexto los tipos de problemas que estan en la base de
        # datos
        context['context_tipo_problema'] = MantosImp.objects.values(
            'tipo_problema').distinct()

        # Al metodo se le pasa  la url como diccionario y los elementos a
        # quitar del diccionario y devuelve el contexto de forma de url con las
        # claves eliminadas
        def get_context_url(*args):
            # El primer argumentoe es la url que se pasa como diccionario
            dic_url = args[0]
            # El segundo argumento son las claves que se dese elimiar de la
            # url, para luego enviarlo como contexto
            del_key = args[1::]
            for x in del_key:
                # Si existe la clave a eliminar en dic_url se elimina, si no
                # esta la palabra a eliminar devuelve el contexto (url)
                # original
                if x in dic_url:
                    try:
                        del dic_url[x]
                    except Exception as err:
                        print(err)
                    # Construye el contexto como una url a partir del
                    # diccionario final
                    context = urllib.parse.urlencode(dic_url)
                else:
                    context = urllib.parse.urlencode(dic_url)
            return context

        # Si hay un request y que sea valida la petición solicitada se envia en
        # el contexto los filtros correspondientes
        if self.request.GET and self.context_url:
            # Contexto filtro_fecha_query_string, para filtrar por fecha y
            # problema,producción,etc. # Nota: En el html se realiza un append
            # en javascript de toda la petición del form
            context['filtro_fecha_query_string'] = get_context_url(
                self.request.GET.dict(), 'fecha__gte', 'fecha__lte')
            # Llama al metodo para eliminar de la url tipo_problema y enviarlo como contexto como filtro al HTML
            # si la url es "tipo_problema=produccion&problema=goteros", el metodo elimina de la URL tipo_problema, para que cuando el usuario vaya a filtrar por tipo_problema tambien filtre por problema
            # en este caso quedaria problema=goteros&tipo_problema="lo que el usuario elija".
            # Se tiene que eliminar de la URL tipo_problema, ya que, se
            # repetiria por la combinación de las variables en el HTML.
            context['filtro_tipo_problema'] = get_context_url(
                self.request.GET.dict(), 'tipo_problema')
            context['filtro_problema'] = get_context_url(
                self.request.GET.dict(), 'problema')
            context['filtro_produccion'] = get_context_url(
                self.request.GET.dict(), 'produccion')

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


# Generar Reporte PDF xhtml2PDF
def improductivos_report_pdf(request):

    def get_improductivo(tiempo_improductivo):
        segundos = 0
        for x in tiempo_improductivo:
            segundos += (int(x.tiempo_improductivo.hour) * 3600) + \
                (int(x.tiempo_improductivo.minute) * 60) + int(x.tiempo_improductivo.second)

        horas = (segundos // 3600)  # Calculo de hora del improductivo
        minutos = (segundos // 60) % 60  # Calculo de los minutos del improductivo
        segundos = segundos % 60  # Calculo de los segundos del improductivo
        return ('{}:{}:{}'.format(horas, minutos, segundos))

    if request.method == "POST":
        form = ImproductivosFormReport(request.POST)
        if form.is_valid():
            op = (form.cleaned_data['produccion'])
            fecha_gte = (form.cleaned_data['fecha_gte'])
            fecha_lte = (form.cleaned_data['fecha_lte'])
            usuario = request.user.get_full_name
            # Query Sets
            query_imp_ruedas = MantosImp.objects.filter(
                problema='ruedas', produccion__orden_produccion=op)
            query_imp_goteros = MantosImp.objects.filter(
                problema='goteros', produccion__orden_produccion=op)
            query_imp_troquelado = MantosImp.objects.filter(
                problema='troquelado', produccion__orden_produccion=op)
            query_imp_film = MantosImp.objects.filter(
                problema='film', produccion__orden_produccion=op)
            query_imp_regulaciones = MantosImp.objects.filter(
                problema='regulaciones', produccion__orden_produccion=op)
            query_imp_electrico = MantosImp.objects.filter(
                problema='electrico', produccion__orden_produccion=op)
            query_imp_mecanico = MantosImp.objects.filter(
                problema='mecanico', produccion__orden_produccion=op)
            # calculos de improductivos
            improductivo_ruedas = get_improductivo(query_imp_ruedas)
            improductivo_goteros = get_improductivo(query_imp_goteros)
            improductivo_troquelado = get_improductivo(query_imp_troquelado)
            improductivo_film = get_improductivo(query_imp_film)
            improductivo_regulaciones = get_improductivo(query_imp_regulaciones)
            improductivo_electrico = get_improductivo(query_imp_electrico)
            improductivo_mecanico = get_improductivo(query_imp_mecanico)

            # Contexto al HTML
            data = {
                'today': datetime.now(),
                'usuario': usuario,
                'orden_produccion': op,
                'improductivo_ruedas': improductivo_ruedas,
                'improductivo_goteros': improductivo_goteros,
                'improductivo_troquelado': improductivo_troquelado,
                'improductivo_film': improductivo_film,
                'improductivo_regulaciones': improductivo_regulaciones,
                'improductivo_electrico': improductivo_electrico,
                'improductivo_mecanico': improductivo_mecanico,

            }
            pdf = render_to_pdf('improductivos/improductivos_report_pdf.html', data)
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                filename = "Reporte_improductivo_%s_%s.pdf" %(op,datetime.now())
                content = "attachment; filename=%s" %(filename)
                response['Content-Disposition'] = content
            return response


            return HttpResponse("Error! =(")
    else:
        form = ImproductivosFormReport()

    return render(request, 'improductivos/improductivos_form_report.html', {'form': form})


#################################################################


def handler404(request):
    return render(request, '404.html', status=404)


def handler500(request):

    return render(request, '500.html', status=500)
