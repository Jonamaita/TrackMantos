from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.core import serializers
from apps.improductivos.forms import ImproductivosForm, ImproductivosFormEdit, ImproductivosFormQr, ImproductivosFormReport  # Importar formulario
from datetime import datetime  # importar time
from apps.improductivos.models import MantosImp
from apps.producciones.models import Producciones
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.conf import settings
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, BaseDocTemplate, PageTemplate, Frame, Spacer, Paragraph, NextPageTemplate, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.colors import HexColor
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


# Generar Reporte PDF ReportLab


def improductivos_report(request):
    # Colores para las barras de los graficos
    chart_colors = [HexColor("#0000e5"), HexColor("#246de3"), HexColor(
        "#9898fa"), HexColor("#fa7f7f"), HexColor("#f54545"), HexColor("#f20f0f"), ]

    # Función para colorear todas las barras de diferentes colores (colores
    # definidos en chart_colors)
    def set_colors_bars(n, obj, attr, values):
        m = len(values)  # Calcula el largo del arreglo chart_colors
        # Divide el largo del arreglo chart_colors entre la cantidad de barras a
        # graficar, para luego usarlo en el seteo de colores "values[j*i % m]" y
        # dependiendo el caloculo de la canitdad de barras se le dara un degradado
        # o colores diferentes a cada barra
        i = m // n
        for j in range(n):
            # Setea el atributo 'fillColor' al obtejo que "bc.bars"
            setattr(obj[0, j], attr, values[j * i % m])

    # Metodos parar generar el PDF
    def cabecera_1(canvas, doc):
        fecha = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")
        # Utilizamos el archivo logo_django.png que está guardado en la carpeta media/imagenes
        logo = settings.STATIC_ROOT + '/imgs/logo_mantos_pdf.png'
        # Definimos el tamaño de la imagen a cargar y las coordenadas correspondientes
        canvas.drawImage(logo, 40, 760, 70, 70, preserveAspectRatio=True)
        # Establecemos el tamaño de letra en 20, el tipo de letra Helvetica y el color
        canvas.setFont("Helvetica-Bold", 18)
        # Cambiar color, el codigo RGB deseado  se debe dividir entre 256 cada valor
        canvas.setFillColorRGB(0.0390625, 0.4921875, 0.69140625)
        # Dibujamos una cadena en la ubicación X,Y especificada
        canvas.drawString(230, 790, u"Reporte de Improductivos")
        canvas.setFont("Helvetica-Bold", 10)
        canvas.setFillColorRGB(0, 0, 0)
        canvas.drawString(40, 760, u"Estimado(a): ")
        canvas.drawString(40, 745, u"Fecha: ")
        canvas.drawString(40, 730, u"Hora: ")
        canvas.drawString(40, 715, u"Orden de producción: ")
        canvas.setFont("Helvetica", 10)
        canvas.drawString(105, 760, str(request.user.first_name + " " + request.user.last_name))
        canvas.drawString(75, 745, str(fecha))
        canvas.drawString(75, 730, str(time))
        canvas.drawString(145, 715, str(op))
        canvas.line(40, 700, 555, 700)
        return canvas

    def cabecera_contenido(canvas, doc):
        fecha = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")
        # Utilizamos el archivo logo_django.png que está guardado en la carpeta media/imagenes
        logo = settings.STATIC_ROOT + '/imgs/logo_mantos_pdf.png'
        # Definimos el tamaño de la imagen a cargar y las coordenadas correspondientes
        canvas.drawImage(logo, 280, 750, 70, 70, preserveAspectRatio=True)
        canvas.setFillColorRGB(0, 0, 0)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(40, 790, u"Fecha: ")
        canvas.drawString(40, 775, u"Hora: ")
        canvas.drawString(40, 760, u"Orden de producción: ")
        canvas.setFont("Helvetica", 10)
        canvas.drawString(75, 790, str(fecha))
        canvas.drawString(75, 775, str(time))
        canvas.drawString(145, 760, str(op))
        canvas.line(40, 750, 555, 750)
        return canvas

    def pie_pagina(canvas, doc):
        canvas.setFont("Helvetica-Bold", 8)
        canvas.line(40, 40, 555, 40)
        canvas.drawString(280, 20, u"Página %d" % doc.page)

    # Tabla de improductivos de producción modular
    def tabla_produccion():
        # Datos
        improductivo_ruedas = get_improductivo(query_imp_ruedas, True)
        improductivo_goteros = get_improductivo(query_imp_goteros, True)
        improductivo_troquelado = get_improductivo(query_imp_troquelado, True)
        improductivo_film = get_improductivo(query_imp_film, True)
        improductivo_regulaciones = get_improductivo(query_imp_regulaciones, True)
        improductivo_total = get_improductivo(query_imp_ruedas, False) + \
            get_improductivo(query_imp_goteros, False) + get_improductivo(query_imp_troquelado, False) + \
            get_improductivo(query_imp_film, False) + \
            get_improductivo(query_imp_regulaciones, False)
        improductivo_total = '%.3f hrs' % improductivo_total
        # Creamos una lista de tuplas que van a contener los improductivos
        datos = [["Ruedas", improductivo_ruedas], ["Goteros", improductivo_goteros], ["Troquelado", improductivo_troquelado],
                 ["Film", improductivo_film], ["Regulaciones", improductivo_regulaciones], ["TOTAL", improductivo_total]]
        # Establecemos el tamaño de cada una de las columnas de la tabla alto y ancho
        tabla = Table(datos, colWidths=[7 * cm, 6 * cm])
        # Aplicamos estilos a las celdas de la tabla, las cordenadas de las celdas es  [i][j]
        tabla.setStyle(TableStyle(
            [
                # Toda la tabla va a estar centrada
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                # Los bordes de todas las celdas serán de color negro y con un grosor de 1
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                # El tamaño de las letras de cada una de las celdas será de 12
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (0, -1), (1, -1), colors.orange),
            ]
        ))
        return tabla

    def tabla_mantenimiento():
        # Datos
        improductivo_mecanico = get_improductivo(query_imp_mecanico, True)
        improductivo_electrico = get_improductivo(query_imp_electrico, True)
        improductivo_total = get_improductivo(query_imp_electrico, False) + \
            get_improductivo(query_imp_mecanico, False)
        improductivo_total = '%.3f hrs' % improductivo_total
        # Creamos una lista de tuplas que van a contener los improductivos
        datos = [["Mecánico", improductivo_mecanico], ["Eléctrico",
                                                       improductivo_electrico], ["TOTAL", improductivo_total]]
        # Establecemos el tamaño de cada una de las columnas de la tabla alto y ancho
        tabla = Table(datos, colWidths=[7 * cm, 6 * cm])
        # Aplicamos estilos a las celdas de la tabla, las cordenadas de las celdas
        # es  [i][j] ->[columna][fila]
        tabla.setStyle(TableStyle(
            [
                # Toda la tabla va a estar centrada
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                # Los bordes de todas las celdas serán de color negro y con un grosor de 1
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                # El tamaño de las letras de cada una de las celdas será de 12
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (0, -1), (1, -1), colors.orange),
            ]
        ))
        return tabla

    # Grafica de improductivos de producción
    def grafica_produccion():
        # Datos de improductivos para graficar
        ruedas = get_improductivo(query_imp_ruedas, False)
        goteros = get_improductivo(query_imp_goteros, False)
        troquelado = get_improductivo(query_imp_troquelado, False)
        film = get_improductivo(query_imp_film, False)
        regulaciones = get_improductivo(query_imp_regulaciones, False)
        # Coordenadas para empezar a dibujar el grafico
        drawing = Drawing(400, 320)
        data = [
            (ruedas, goteros, troquelado, film, regulaciones),

        ]
        bc = VerticalBarChart()
        # Centrar el grafico
        bc.x = 35
        bc.y = 50
        # Tamaño del grafico
        bc.height = 250
        bc.width = 365
        bc.data = data  # Datos para graficar
        # Tipo de letra para la etiqueta o valor que estara arriba de cada barra
        bc.barLabels.fontName = "Helvetica-Bold"
        bc.barLabels.fontSize = 8  # Tamaño de letra para la etiqueta o valor que estara arriba de cada barra
        # Color de letra para la etiqueta o valor que estara arriba de cada barra
        bc.barLabels.fillColor = colors.Color(31 / 256, 54 / 256, 138 / 256)
        bc.barLabelFormat = '%.3f hrs'  # Dar formato de 3 decimales al valor o etiqueta que estara arriba de cada barra
        bc.barLabels.nudge = 7  # Dar espacio entre la barra y la etiqueta o valor que estara arriba de cada barra
        # bc.barWidth=7 # Ancho de la barra
        # bc.strokeColor = colors.black # Dibuja un borde alrededor del grafico
        # bc.fillColor = colors.green # Fondo del grafico
        # bc.groupSpacing = 10  # Espaciado entre grupos de barras
        bc.valueAxis.valueMin = 0
        bc.valueAxis.rangeRound = 'both' # Darle un valor rendondeado o cercado al valor mas alto al eje y
        bc.valueAxis.valueMax = None  # Valor maximo del eje
        # bc.valueAxis.valueStep = 5 # Divisiones del eje
        bc.categoryAxis.labels.boxAnchor = 'ne'
        bc.categoryAxis.labels.dx = 8
        bc.categoryAxis.labels.dy = -3
        bc.categoryAxis.labels.angle = 45
        bc.categoryAxis.categoryNames = ['Ruedas', 'Goteros', 'Troquelado',
                                         'Film', 'Regulaciones', ]
        n = len(bc.data[0])
        set_colors_bars(n, bc.bars, 'fillColor', chart_colors)
        # bc.categoryAxis.strokeColor=colors.Color(36/256,41/256,35/256) # Cambiar color eje x
        drawing.add(bc)
        return drawing

    # Grafica de producción de los improductivos totalizados
    def grafica_produccion_total():
        # Datos de improductivos para graficar
        ruedas = get_improductivo(query_imp_ruedas, False)
        goteros = get_improductivo(query_imp_goteros, False)
        troquelado = get_improductivo(query_imp_troquelado, False)
        film = get_improductivo(query_imp_film, False)
        regulaciones = get_improductivo(query_imp_regulaciones, False)
        improductivo_total = ruedas + goteros + troquelado + film + regulaciones
        # Coordenadas para empezar a dibujar el grafico
        drawing = Drawing(400, 320)
        data = [
            (improductivo_total,),

        ]
        bc = VerticalBarChart()
        # Centrar el grafico
        bc.x = 60
        bc.y = 100
        # Tamaño del grafico
        bc.height = 190
        bc.width = 300
        bc.data = data  # Datos para graficar
        # Tipo de letra para la etiqueta o valor que estara arriba de cada barra
        bc.barLabels.fontName = "Helvetica-Bold"
        bc.barLabels.fontSize = 8  # Tamaño de letra para la etiqueta o valor que estara arriba de cada barra
        # Color de letra para la etiqueta o valor que estara arriba de cada barra
        bc.barLabels.fillColor = colors.Color(31 / 256, 54 / 256, 138 / 256)
        bc.barLabelFormat = '%.3f hrs'  # Dar formato de 3 decimales al valor o etiqueta que estara arriba de cada barra
        bc.barLabels.nudge = 7  # Dar espacio entre la barra y la etiqueta o valor que estara arriba de cada barra
        bc.barWidth = 1  # Ancho de la barra
        # bc.strokeColor = colors.black # Dibuja un borde alrededor del grafico
        # bc.fillColor = colors.green # Fondo del grafico
        # bc.groupSpacing = 10  # Espaciado entre grupos de barras
        bc.valueAxis.valueMin = 0
        bc.valueAxis.rangeRound = 'both'
        bc.valueAxis.valueMax = None  # Valor maximo del eje
        #bc.valueAxis.valueStep = 5
        bc.categoryAxis.labels.boxAnchor = 'ne'
        bc.categoryAxis.labels.dx = 8
        bc.categoryAxis.labels.dy = -3
        bc.categoryAxis.labels.angle = 45
        bc.categoryAxis.categoryNames = ['Improductivo', ]
        # bc.categoryAxis.strokeColor=colors.Color(36/256,41/256,35/256) # Cambiar color eje x
        drawing.add(bc)
        return drawing

    # Grafica de improductivos de mantenimiento
    def grafica_mantenimiento():
        # Datos de improductivos para graficar
        mecanico = get_improductivo(query_imp_mecanico, False)
        electrico = get_improductivo(query_imp_electrico, False)
        # Coordenadas para empezar a dibujar el grafico
        drawing = Drawing(400, 300)
        data = [
            (mecanico, electrico),

        ]
        bc = VerticalBarChart()
        # Centrar el grafico
        bc.x = 80
        bc.y = 90
        # Tamaño del grafico
        bc.height = 200
        bc.width = 315
        bc.data = data  # Datos para graficar
        # Tipo de letra para la etiqueta o valor que estara arriba de cada barra
        bc.barLabels.fontName = "Helvetica-Bold"
        bc.barLabels.fontSize = 8  # Tamaño de letra para la etiqueta o valor que estara arriba de cada barra
        # Color de letra para la etiqueta o valor que estara arriba de cada barra
        bc.barLabels.fillColor = colors.Color(31 / 256, 54 / 256, 138 / 256)
        bc.barLabelFormat = '%.3f hrs'  # Dar formato de 3 decimales al valor o etiqueta que estara arriba de cada barra
        bc.barLabels.nudge = 7  # Dar espacio entre la barra y la etiqueta o valor que estara arriba de cada barra
        bc.barWidth = 2  # Ancho de la barra
        # bc.strokeColor = colors.black # Dibuja un borde alrededor del grafico
        # bc.fillColor = colors.green # Fondo del grafico
        # bc.groupSpacing = 10  # Espaciado entre grupos de barras
        bc.valueAxis.rangeRound = 'both'
        bc.valueAxis.valueMax = None  # Valor maximo del eje
        #bc.valueAxis.valueStep = 5
        # bc.valueAxis.tickRight=5 # Grid hacia la derecha
        bc.categoryAxis.labels.boxAnchor = 'ne'
        bc.categoryAxis.labels.dx = 8
        bc.categoryAxis.labels.dy = -3
        bc.categoryAxis.labels.angle = 45
        bc.categoryAxis.categoryNames = ['Mecánico', 'Eléctrico', ]
        n = len(bc.data[0])
        set_colors_bars(n, bc.bars, 'fillColor', chart_colors)

        # bc.categoryAxis.strokeColor=colors.Color(36/256,41/256,35/256) # Cambiar color eje x
        drawing.add(bc)
        return drawing

    def grafica_mantenimiento_total():
        # Datos de improductivos para graficar
        mecanico = get_improductivo(query_imp_mecanico, False)
        electrico = get_improductivo(query_imp_electrico, False)
        improductivo_total = mecanico + electrico
        # Coordenadas para empezar a dibujar el grafico
        drawing = Drawing(400, 200)
        data = [
            (improductivo_total,),

        ]
        bc = VerticalBarChart()
        # Centrar el grafico
        bc.x = 80
        bc.y = 10
        # Tamaño del grafico
        bc.height = 190
        bc.width = 300
        bc.data = data  # Datos para graficar
        # Tipo de letra para la etiqueta o valor que estara arriba de cada barra
        bc.barLabels.fontName = "Helvetica-Bold"
        bc.barLabels.fontSize = 8  # Tamaño de letra para la etiqueta o valor que estara arriba de cada barra
        # Color de letra para la etiqueta o valor que estara arriba de cada barra
        bc.barLabels.fillColor = colors.Color(31 / 256, 54 / 256, 138 / 256)
        bc.barLabelFormat = '%.3f hrs'  # Dar formato de 3 decimales al valor o etiqueta que estara arriba de cada barra
        bc.barLabels.nudge = 7  # Dar espacio entre la barra y la etiqueta o valor que estara arriba de cada barra
        bc.barWidth = 1  # Ancho de la barra
        # bc.strokeColor = colors.black # Dibuja un borde alrededor del grafico
        # bc.fillColor = colors.green # Fondo del grafico
        # bc.groupSpacing = 10  # Espaciado entre grupos de barras
        bc.valueAxis.rangeRound = 'both'
        bc.valueAxis.valueMax = None  # Valor maximo del eje
        #bc.valueAxis.valueStep = 5
        bc.categoryAxis.labels.boxAnchor = 'ne'
        bc.categoryAxis.labels.dx = 8
        bc.categoryAxis.labels.dy = -3
        bc.categoryAxis.labels.angle = 45
        bc.categoryAxis.categoryNames = ['Improductivo', ]

        # bc.categoryAxis.strokeColor=colors.Color(36/256,41/256,35/256) # Cambiar color eje x
        drawing.add(bc)
        return drawing

    # Metodo para calcular el total de improductivos, si hms es True retorna formato Horas Minutos y Segundos en String
    # si es falso retorna el total en horas
    def get_improductivo(tiempo_improductivo, hms):
        segundos = 0
        if hms:
            for x in tiempo_improductivo:
                segundos += (int(x.tiempo_improductivo.hour) * 3600) + \
                    (int(x.tiempo_improductivo.minute) * 60) + int(x.tiempo_improductivo.second)
            horas = (segundos // 3600)  # Calculo de hora del improductivo
            minutos = (segundos // 60) % 60  # Calculo de los minutos del improductivo
            segundos = segundos % 60  # Calculo de los segundos del improductivo
            if horas < 10:  # Agregar un 0 a la izquierda si es menor a 10
                horas = '0' + str(horas)
            if minutos < 10:
                minutos = '0' + str(minutos)
            if segundos < 10:
                segundos = '0' + str(segundos)
            return ('{}:{}:{}'.format(horas, minutos, segundos))
        else:
            for x in tiempo_improductivo:
                segundos += (int(x.tiempo_improductivo.hour) * 3600) + \
                    (int(x.tiempo_improductivo.minute) * 60) + int(x.tiempo_improductivo.second)

            horas = (segundos) / (3600)
            return (horas)

    if request.method == "POST":
        form = ImproductivosFormReport(request.POST)
        if form.is_valid():
            now = datetime.now()
            op = (form.cleaned_data['produccion'])
            fecha_gte = (form.cleaned_data['fecha_gte'])
            fecha_lte = (form.cleaned_data['fecha_lte'])
            usuario = request.user.get_full_name
            # Query Sets
            query_imp_ruedas = MantosImp.objects.filter(
                problema='ruedas', produccion__orden_produccion=op, fecha__gte=fecha_gte, fecha__lte=fecha_lte).exclude(hora_solucion=None)
            query_imp_goteros = MantosImp.objects.filter(
                problema='goteros', produccion__orden_produccion=op, fecha__gte=fecha_gte, fecha__lte=fecha_lte).exclude(hora_solucion=None)
            query_imp_troquelado = MantosImp.objects.filter(
                problema='troquelado', produccion__orden_produccion=op, fecha__gte=fecha_gte, fecha__lte=fecha_lte).exclude(hora_solucion=None)
            query_imp_film = MantosImp.objects.filter(
                problema='film', produccion__orden_produccion=op, fecha__gte=fecha_gte, fecha__lte=fecha_lte).exclude(hora_solucion=None)
            query_imp_regulaciones = MantosImp.objects.filter(
                problema='regulaciones', produccion__orden_produccion=op, fecha__gte=fecha_gte, fecha__lte=fecha_lte).exclude(hora_solucion=None)
            query_imp_electrico = MantosImp.objects.filter(
                problema='electrico', produccion__orden_produccion=op, fecha__gte=fecha_gte, fecha__lte=fecha_lte).exclude(hora_solucion=None)
            query_imp_mecanico = MantosImp.objects.filter(
                problema='mecanico', produccion__orden_produccion=op, fecha__gte=fecha_gte, fecha__lte=fecha_lte).exclude(hora_solucion=None)
            # calculos de improductivos
            improductivo_electrico = get_improductivo(query_imp_electrico, True)
            improductivo_mecanico = get_improductivo(query_imp_mecanico, True)
            # La clase io.BytesIO permite tratar un array de bytes como un fichero
            # binario, se utiliza como almacenamiento temporal
            buffer = BytesIO()
            c = canvas.Canvas(buffer)
            doc = BaseDocTemplate(buffer, pagesize=A4)
            # Frames o marcos
            frame0 = Frame(doc.leftMargin, doc.bottomMargin,
                           doc.width, doc.height, showBoundary=0, id='normalBorde')
            # Plantillas
            doc.addPageTemplates([PageTemplate(id='primera_hoja', frames=frame0,
                                               onPage=cabecera_1, onPageEnd=pie_pagina),
                                  PageTemplate(id='contenido', frames=frame0, onPage=cabecera_contenido, onPageEnd=pie_pagina)])
            # Creamos la hoja de Estilo
            estilo = getSampleStyleSheet()
            estilo.add(ParagraphStyle(name="titulo_tablas_graficas",  alignment=TA_CENTER, fontSize=15,
                                      fontName="Helvetica-Bold", textColor=colors.Color(0.0390625, 0.4921875, 0.69140625)))
            estilo.add(ParagraphStyle(name="texto",  alignment=TA_LEFT, fontSize=12,
                                      fontName="Helvetica", textColor=colors.Color(0, 0, 0)))
            # Construimos el pdf
            story = []  # Se declara el arreglo para construir el pdf
            # Texto, tabla y graficas de produccion
            texto_tabla_produccion = Paragraph(
                u"En la siguiente tabla se presentan los improductivos de producción asociados a la orden de producción " + str(op) + ":", estilo['texto'])
            titulo_tabla_produccion = Paragraph(
                u"Improductivos de Producción", estilo['titulo_tablas_graficas'])
            tabla_produccion = tabla_produccion()
            texto_grafica_produccion = Paragraph(
                u"En la siguientes graficas se presentan los improductivos de producción asociados a la orden de producción " + str(op) + ":", estilo['texto'])
            titulo_grafica_produccion = Paragraph(
                u"Grafica de Improductivos de Producción", estilo['titulo_tablas_graficas'])
            grafica_produccion = grafica_produccion()
            titulo_grafica_produccion_total = Paragraph(
                u"Grafica de improductivos de producción totalizados", estilo['titulo_tablas_graficas'])
            grafica_produccion_total = grafica_produccion_total()

            # Texto, tabla y graficas de mantenimiento
            texto_tabla_mantenimiento = Paragraph(
                u"En la siguiente tabla se presentan los improductivos de mantenimiento asociados de la orden de producción " + str(op) + ":", estilo['texto'])
            titulo_tabla_mantenimiento = Paragraph(
                u"Improductivos de Mantenimiento", estilo['titulo_tablas_graficas'])
            tabla_mantenimiento = tabla_mantenimiento()
            texto_grafica_mantenimiento = Paragraph(
                u"En la siguientes graficas se presentan los improductivos de mantenimiento asociados a la orden de producción " + str(op) + ":", estilo['texto'])
            titulo_grafica_mantenimiento = Paragraph(
                u"Grafica de Improductivos de Mantenimiento", estilo['titulo_tablas_graficas'])
            grafica_mantenimiento = grafica_mantenimiento()
            titulo_grafica_mantenimiento_total = Paragraph(
                u"Grafica de improductivos de mantenimiento totalizados", estilo['titulo_tablas_graficas'])
            grafica_mantenimiento_total = grafica_mantenimiento_total()
            # Construyendo el PDF con los valores antes declarado
            story.append(Spacer(0, 100))
            story.append(texto_tabla_produccion)
            story.append(Spacer(0, 0.5 * cm))
            story.append(titulo_tabla_produccion)
            story.append(Spacer(0, 0.5 * cm))
            story.append(tabla_produccion)
            story.append(Spacer(0, 1 * cm))
            story.append(texto_grafica_produccion)
            story.append(Spacer(0, 0.5 * cm))
            story.append(titulo_grafica_produccion)
            story.append(Spacer(0, 0.5 * cm))
            story.append(grafica_produccion)
            story.append(NextPageTemplate('contenido'))
            story.append(PageBreak())  # Salto de pagina
            story.append(Spacer(0, 40))
            story.append(titulo_grafica_produccion_total)
            story.append(Spacer(0, 0.5 * cm))
            story.append(grafica_produccion_total)
            story.append(Spacer(0, 0.6 * cm))
            story.append(texto_tabla_mantenimiento)
            story.append(Spacer(0, 1 * cm))
            story.append(titulo_tabla_mantenimiento)
            story.append(Spacer(0, 0.6 * cm))
            story.append(tabla_mantenimiento)
            story.append(PageBreak())
            story.append(Spacer(0, 40))
            story.append(texto_grafica_mantenimiento)
            story.append(Spacer(0, 0.5 * cm))
            story.append(titulo_grafica_mantenimiento)
            story.append(Spacer(0, 0.5 * cm))
            story.append(grafica_mantenimiento)
            # story.append(Spacer(0,0.3*cm))
            story.append(titulo_grafica_mantenimiento_total)
            story.append(Spacer(0, 1.5 * cm))
            story.append(grafica_mantenimiento_total)
            doc.build(story)
            pdf = buffer.getvalue()
            buffer.close()
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
    else:
        form = ImproductivosFormReport()

    return render(request, 'improductivos/improductivos_form_report.html', {'form': form, })


# Generar Reporte PDF xhtml2PDF
"""def improductivos_report_pdf(request):

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
                filename = "Reporte_improductivo_%s_%s.pdf" % (op, datetime.now())
                content = "attachment; filename=%s" % (filename)
                response['Content-Disposition'] = content
                return response

            return HttpResponse("Error! =(")
    else:
        form = ImproductivosFormReport()

    return render(request, 'improductivos/improductivos_form_report.html', {'form': form})"""


#################################################################


def handler404(request):
    return render(request, '404.html', status=404)


def handler500(request):

    return render(request, '500.html', status=500)
