from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from apps.producciones.forms import ProduccionesForm, ProduccionesFormEdit, DeleteConfirmForm
from django.contrib.auth import authenticate
from datetime import datetime, timedelta  # importar time
from django.views.generic import ListView, UpdateView, DeleteView
from apps.producciones.models import Producciones
import urllib.parse


# Create your views here.

# Agregar datos de producción


def produccion_form(request):
    if request.method == "POST":
        form = ProduccionesForm(request.POST)
        #now = datetime.now()
        #fecha = now.strftime("%Y-%m-%d")
        #time = now.strftime("%H:%M:%S")
        if form.is_valid():
            # Pasamos form.save(commit=False), con esto le decimos que no
            # queremos guardar el formulario aún,  pasando el formulario a otra
            # variable podemos llenar otros campos del formulario
            orden_produccion = form.cleaned_data['orden_produccion']
            orden_produccion = orden_produccion.replace(" ", "").replace("/", "-")
            orden_produccion = orden_produccion.upper()  # Llevar el numero de orden produccion a mayuscula
            minera = form.cleaned_data['minera']
            minera = minera.replace(" ", "")
            minera = minera.title()  # Llevar el nombre de la minera a tipo titulo
            # Calculo de meta improductivo producción y mantenimiento
            cantidad_mantos = form.cleaned_data['cantidad_mantos']
            tope_improductivo_produccion = round((cantidad_mantos * 0.82) / 60)  # formula KPI produccón
            tope_improductivo_mantenimiento = round((cantidad_mantos * 0.30) / 60)  # formula KPI mantenimiento
            formulario = form.save(commit=False)
            formulario.orden_produccion = orden_produccion
            formulario.minera = minera
            formulario.tope_improductivo_produccion = tope_improductivo_produccion
            formulario.tope_improductivo_mantenimiento = tope_improductivo_mantenimiento
            formulario = form.save(commit=True)
            formulario.save()
            return redirect('producciones:produccion_form')
        else:
            print("Usuario envío formulario no valido")
    else:
        form = ProduccionesForm()

    return render(request, 'producciones/produccion_form.html', {'form': form})

# Lstar


class ProduccionesList(ListView):
    model = Producciones
    ordering = ['-fecha_inicio']
    template_name = 'producciones/producciones_list.html'
    paginate_by = 10
    context_url = False
    # Sobre escribir queryset

    def get_queryset(self):
        queryset = Producciones.objects.all().order_by('-fecha_inicio')
        if self.request.GET:
            try:
                a = self.request.GET
                queryset = Producciones.objects.filter(**a.dict()).order_by('-fecha_inicio')
                self.context_url = True
            except Exception as err:
                print(err)
                self.context_url = False
        return queryset

    # Enviar contexto html
    def get_context_data(self, **kwargs):
        now = datetime.now()
        fecha_1 = timedelta(days=1)
        delta = now - fecha_1
        delta = delta.strftime("%Y-%m-%d")
        fecha = now.strftime("%Y-%m-%d")
        context = super(ProduccionesList, self).get_context_data(**kwargs)
        # toma el valor date__gte en ese momento, si no lo tiene le asigna el valor delta
        context['context_fecha_gte'] = self.request.GET.get('fecha__gte', delta)
        context['context_fecha_lte'] = self.request.GET.get('fecha__lte', fecha)
        context['context_minera'] = Producciones.objects.values('minera').distinct()

        def get_context_url(*args):
            dic = args[0]
            del_key = args[1::]
            for x in del_key:
                if x in dic:
                    try:
                        del dic[x]
                    except Exception as err:
                        print(err)
                    context = urllib.parse.urlencode(dic)
                else:
                    context = urllib.parse.urlencode(dic)

            return context

        if self.request.GET and self.context_url == True:
            context['filtro_fecha_query_string'] = get_context_url(
                self.request.GET.dict(), 'fecha_inicio__gte', 'fecha_inicio__lte')
            context['filtro_minera'] = get_context_url(self.request.GET.dict(), 'minera') + "&"

        return context

# Editar


class ProduccionesUpdate(UpdateView):
    model = Producciones
    form_class = ProduccionesFormEdit  # le pasa al html el form como contexto
    template_name = 'producciones/producciones_edit.html'
    success_url = reverse_lazy('producciones:producciones_list')

# Eliminar con contraseña


def produccion_delete(request, pk):
    produccion_delete = Producciones.objects.get(pk=pk)  # Objeto a borrar
    if request.method == "POST":
        # llamo al formulario de confirmación con el parametro request. (la
        # validación esta realizada en el form)
        form = DeleteConfirmForm(request.POST, request=request)
        if form.is_valid():  # Si el usuario y el password esta OK, procede a borrar el objeto. La logica se realizó de forma manual en el form
            produccion_delete.delete()
            return redirect('producciones:producciones_list')
        # return render(request, 'producciones/producciones_delete.html',
        # {'produccion': produccion_delete,'produccion_delete_confirm':form})
    else:
        form = DeleteConfirmForm()
    return render(request, 'producciones/producciones_delete.html', {'produccion': produccion_delete, 'produccion_delete_confirm': form})


class ProduccionesDelete(DeleteView):
    model = Producciones
    template_name = 'producciones/producciones_delete.html'
    success_url = reverse_lazy('producciones:producciones_list')

# Listar producciones para iniciarlas o cerrarlas


class ProduccionesListIinitClosed(ListView):
    queryset = Producciones.objects.filter(
        fecha_inicio=None) | Producciones.objects.filter(fecha_finalizacion=None)
    model = queryset
    template_name = 'producciones/producciones_list_init_closed.html'
    paginate_by = 10
    ordering = ['-fecha_inicio']

# Iniciar orden de producción


def iniciar_produccion(request, pk):
    now = datetime.now()
    fecha = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    op_iniciar = Producciones.objects.filter(
        pk=pk)  # Filtrar la orden de producción a iniciar por la pk
    if op_iniciar.update(fecha_inicio=fecha, hora_inicio=time):
        return redirect('producciones:producciones_list')
    else:
        return redirect('producciones:producciones_list_init_closed')

# Cerrar orden orden de producción


def cerrar_produccion(request, pk):
    now = datetime.now()
    fecha = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    op_cerrar = Producciones.objects.filter(
        pk=pk)  # Filtrar la orden de producción a iniciar por la pk
    if op_cerrar.update(fecha_finalizacion=fecha, hora_finalizacion=time):
        return redirect('producciones:producciones_list')
    else:
        return redirect('producciones:producciones_list_init_closed')

# Json de producciones


def producciones_json(request):
    data = serializers.serialize("json", Producciones.objects.all(), fields=[
                                 'orden_produccion', 'pk', 'fecha_inicio', 'fecha_finalizacion'])
    return HttpResponse(data, content_type='application/json')
