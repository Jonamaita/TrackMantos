from apps.improductivos.models import MantosImp
from apps.producciones.models import Producciones
from io import BytesIO
from datetime import datetime
from django.conf import settings
#Librerias de reportlab
#from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, BaseDocTemplate, PageTemplate, Frame, Spacer, Paragraph, NextPageTemplate, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.colors import HexColor


class ImproductivoReportPDF:
	# Colores para las barras de los graficos
	chart_colors = [HexColor("#0000e5"), HexColor("#246de3"), HexColor(
		"#9898fa"), HexColor("#fa7f7f"), HexColor("#f54545"), HexColor("#f20f0f"), ]

	def __init__(self, op:str,fecha_gte:str,fecha_lte:str,usuario:str):
		self.op = op
		self.fecha_gte = fecha_gte
		self.fecha_lte = fecha_lte
		self.usuario = usuario

	# Función para colorear todas las barras de diferentes colores (colores
	# definidos en chart_colors)
	def _set_colors_bars(self,n, obj, attr, values):
		m = len(values)  # Calcula el largo del arreglo chart_colors
		# Divide el largo del arreglo chart_colors entre la cantidad de barras a
		# graficar, para luego usarlo en el seteo de colores "values[j*i % m]" y
		# dependiendo el caloculo de la canitdad de barras se le dara un degradado
		# o colores diferentes a cada barra
		i = m // n
		for j in range(n):
			# Setea el atributo 'fillColor' al obtejo que "bc.bars"
			setattr(obj[0, j], attr, values[j * i % m])

	# Función para colorear barra de improductivo total con respecto al
	# promedio, solo retorna el color que va tomar la barra
	def _color_bar_imp_total(self,promedio):

		if promedio < 70:
			return '#32a836'

		elif promedio > 69 and promedio < 100:
			return '#ff7f24'
		else:
			return '#ff0000'

	#-------------------------------------- Metodos parar generar el PDF --------------------------------#

	"""Los metodos de cabecera y pie de pagina, son metodos llamado en el parametro onpage y endpage. Estos metodos se llaman especificamente desde
	doc.addPageTemplates, implicitamente los parametros canvas y doc son pasados al metodo, por ende, cuando se llama el metodo no se envía los parametros, pero,
	en el metodo se deben recibir los parametros. Es decr en "OnPage = _cabecera_1" no se pasan los parametros canvas, doc. Pero en se deben recibir donde
	se defina el metodo o función.
	"""
	def _cabecera_1(self,canvas, doc):
		now = datetime.now()
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
		canvas.drawString(105, 760, str(self.usuario))
		canvas.drawString(75, 745, str(fecha))
		canvas.drawString(75, 730, str(time))
		canvas.drawString(145, 715, str(self.op))
		canvas.line(40, 700, 555, 700)
		#return canvas

	def _cabecera_contenido(self,canvas, doc):
		now = datetime.now()
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
		canvas.drawString(145, 760, str(self.op))
		canvas.line(40, 750, 555, 750)
		#return canvas

	def _pie_pagina(self,canvas, doc):
		canvas.setFont("Helvetica-Bold", 8)
		canvas.line(40, 40, 555, 40)
		canvas.drawString(280, 20, u"Página %d" % doc.page)

	# Tabla de improductivos de producción modular
	def _tabla_produccion(self):
		# Datos
		improductivo_ruedas = self._get_improductivo(self.query_imp_ruedas, True)
		improductivo_goteros = self._get_improductivo(self.query_imp_goteros, True)
		improductivo_troquelado = self._get_improductivo(self.query_imp_troquelado, True)
		improductivo_film = self._get_improductivo(self.query_imp_film, True)
		improductivo_regulaciones = self._get_improductivo(self.query_imp_regulaciones, True)
		improductivo_total = self._get_improductivo(self.query_imp_ruedas, False) + \
			self._get_improductivo(self.query_imp_goteros, False) + self._get_improductivo(self.query_imp_troquelado, False) + \
			self._get_improductivo(self.query_imp_film, False) + \
			self._get_improductivo(self.query_imp_regulaciones, False)
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

	def _tabla_mantenimiento(self):
		# Datos
		improductivo_mecanico = self._get_improductivo(self.query_imp_mecanico, True)
		improductivo_electrico = self._get_improductivo(self.query_imp_electrico, True)
		improductivo_total = self._get_improductivo(self.query_imp_electrico, False) + \
			self._get_improductivo(self.query_imp_mecanico, False)
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
	def _grafica_produccion(self):
		# Datos de improductivos para graficar
		ruedas = self._get_improductivo(self.query_imp_ruedas, False)
		goteros = self._get_improductivo(self.query_imp_goteros, False)
		troquelado = self._get_improductivo(self.query_imp_troquelado, False)
		film = self._get_improductivo(self.query_imp_film, False)
		regulaciones = self._get_improductivo(self.query_imp_regulaciones, False)
		# Coordenadas para empezar a dibujar el grafico
		drawing = Drawing(400, 320)
		# Data para graficar, la data es una lista de tuplas, cada tupla es un grupo de barras o graficas
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
		# los colores van de 0 a 256 en RGB, sin embargo, en la libreria hay que pasarlo en numeros del 0 al 1
		bc.barLabels.fillColor = colors.Color(31 / 256, 54 / 256, 138 / 256)
		bc.barLabelFormat = '%.3f hrs'  # Dar formato de 3 decimales al valor o etiqueta que estara arriba de cada barra
		bc.barLabels.nudge = 7  # Dar espacio entre la barra y la etiqueta o valor que estara arriba de cada barra
		# bc.barWidth=7 # Ancho de la barra
		# bc.strokeColor = colors.black # Dibuja un borde alrededor del grafico
		# bc.fillColor = colors.green # Fondo del grafico
		# bc.groupSpacing = 10  # Espaciado entre grupos de barras
		bc.valueAxis.valueMin = 0  # Valor minimo del eje Y
		bc.valueAxis.rangeRound = 'both'  # Darle un valor rendondeado o cercado al valor mas alto al eje 'Y'
		bc.valueAxis.valueMax = None  # Valor maximo del eje Y
		# bc.valueAxis.valueStep = 5 # Divisiones del eje
		bc.categoryAxis.labels.boxAnchor = 'ne'
		bc.categoryAxis.labels.dx = 8  # Posición de la etiqueta en el sentido X (Horizontal)
		bc.categoryAxis.labels.dy = -3  # Posicion de la etiqueta en el snetido Y (Vertical)
		bc.categoryAxis.labels.angle = 45  # Angulo de laetiqueta
		# Nombre de la etiqueta de cada barra
		bc.categoryAxis.categoryNames = ['Ruedas', 'Goteros', 'Troquelado',
										 'Film', 'Regulaciones', ]
		n = len(bc.data[0])  # Cantidad de barras en el indice '0' o de la tupla del indice '0'
		self._set_colors_bars(n, bc.bars, 'fillColor', self.chart_colors)
		# bc.categoryAxis.strokeColor=colors.Color(36/256,41/256,35/256) # Cambiar color eje x
		drawing.add(bc)  # le paso el objeto a drwaing, definido a inicio de la función
		return drawing

	# Grafica de producción de los improductivos totalizados
	def _grafica_produccion_total(self):
		# Datos de improductivos para graficar
		ruedas = self._get_improductivo(self.query_imp_ruedas, False)
		goteros = self._get_improductivo(self.query_imp_goteros, False)
		troquelado = self._get_improductivo(self.query_imp_troquelado, False)
		film = self._get_improductivo(self.query_imp_film, False)
		regulaciones = self._get_improductivo(self.query_imp_regulaciones, False)
		improductivo_total = ruedas + goteros + troquelado + film + regulaciones
		tope_improductivo = Producciones.objects.get(
			orden_produccion=self.op).tope_improductivo_produccion  # Query meta improductivo_produccion
		promedio_improductivo = (improductivo_total * 100) / tope_improductivo
		# Coordenadas para empezar a dibujar el grafico
		drawing = Drawing(400, 320)
		data = [
			(improductivo_total, tope_improductivo),

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
		# Color de fondo de la segunda. el indice [i,j], el indice 'i' indica el
		# grupo de barras y el indice 'j' la barra de grupo
		bc.bars[0, 1].fillColor = colors.Color(66 / 256, 99 / 256, 245 / 256)
		# la función retorna el color dependiendo el promedio del improductivo
		bc.bars[0, 0].fillColor = HexColor(self._color_bar_imp_total(promedio_improductivo))
		# bc.strokeColor = colors.black # Dibuja un borde alrededor del grafico
		# bc.fillColor = colors.green # Fondo del grafico
		# bc.barSpacing =2.5 # Espacio entre barras
		# bc.groupSpacing = 10  # Espaciado entre grupos de barras
		bc.valueAxis.valueMin = 0
		bc.valueAxis.rangeRound = 'both'  # Darle un valor rendondeado o cercado al valor mas alto al eje 'Y'
		bc.valueAxis.valueMax = None  # Valor maximo del eje
		#bc.valueAxis.valueStep = 5
		bc.categoryAxis.labels.boxAnchor = 'ne'
		bc.categoryAxis.labels.dx = 8
		bc.categoryAxis.labels.dy = -3
		bc.categoryAxis.labels.angle = 45
		bc.categoryAxis.categoryNames = ['Improductivo', 'Tope Improductivo']
		# bc.categoryAxis.strokeColor=colors.Color(36/256,41/256,35/256) # Cambiar color eje x
		drawing.add(bc)
		return drawing

	# Grafica de improductivos de mantenimiento
	def _grafica_mantenimiento(self):
		# Datos de improductivos para graficar
		mecanico = self._get_improductivo(self.query_imp_mecanico, False)
		electrico = self._get_improductivo(self.query_imp_electrico, False)
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
		bc.valueAxis.valueMin = 0
		bc.valueAxis.rangeRound = 'both'  # Darle un valor rendondeado o cercado al valor mas alto al eje 'Y'
		bc.valueAxis.valueMax = None  # Valor maximo del eje
		#bc.valueAxis.valueStep = 5
		# bc.valueAxis.tickRight=5 # Grid hacia la derecha
		bc.categoryAxis.labels.boxAnchor = 'ne'
		bc.categoryAxis.labels.dx = 8
		bc.categoryAxis.labels.dy = -3
		bc.categoryAxis.labels.angle = 45
		bc.categoryAxis.categoryNames = ['Mecánico', 'Eléctrico', ]
		n = len(bc.data[0])  # Cantidad de barras en el indice '0' o de la tupla del indice '0'
		self._set_colors_bars(n, bc.bars, 'fillColor', self.chart_colors)
		# bc.categoryAxis.strokeColor=colors.Color(36/256,41/256,35/256) # Cambiar color eje x
		drawing.add(bc)
		return drawing

	def _grafica_mantenimiento_total(self):
		# Datos de improductivos para graficar
		mecanico = self._get_improductivo(self.query_imp_mecanico, False)
		electrico = self._get_improductivo(self.query_imp_electrico, False)
		improductivo_total = mecanico + electrico
		tope_improductivo = Producciones.objects.get(orden_produccion=self.op).tope_improductivo_mantenimiento
		promedio_improductivo = (improductivo_total * 100) / (tope_improductivo)
		# Coordenadas para empezar a dibujar el grafico
		drawing = Drawing(400, 200)
		data = [
			(improductivo_total, tope_improductivo),

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
		# Color de fondo de la segunda. el indice [i,j], el indice 'i' indica el
		# grupo de barras y el indice 'j' la barra de grupo
		bc.bars[0, 1].fillColor = colors.Color(66 / 256, 99 / 256, 245 / 256)
		# la función retorna el color dependiendo el promedio del improductivo
		bc.bars[0, 0].fillColor = HexColor(self._color_bar_imp_total(promedio_improductivo))
		# bc.strokeColor = colors.black # Dibuja un borde alrededor del grafico
		# bc.fillColor = colors.green # Fondo del grafico
		# bc.groupSpacing = 10  # Espaciado entre grupos de barras
		bc.valueAxis.valueMin = 0
		bc.valueAxis.rangeRound = 'both'  # Darle un valor rendondeado o cercado al valor mas alto al eje 'Y'
		bc.valueAxis.valueMax = None  # Valor maximo del eje
		#bc.valueAxis.valueStep = 5
		bc.categoryAxis.labels.boxAnchor = 'ne'
		bc.categoryAxis.labels.dx = 8
		bc.categoryAxis.labels.dy = -3
		bc.categoryAxis.labels.angle = 45
		bc.categoryAxis.categoryNames = ['Improductivo', 'Tope Improductivo']
		# bc.categoryAxis.strokeColor=colors.Color(36/256,41/256,35/256) # Cambiar color eje x
		drawing.add(bc)
		return drawing

	# Metodo para calcular el total de improductivos, si hms es True retorna formato Horas Minutos y Segundos en String
	# si es falso retorna el total en horas
	def _get_improductivo(self,query_imp:object, hms:bool):
		segundos = 0
		if hms:
			for x in query_imp:
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
			for x in query_imp:
				segundos += (int(x.tiempo_improductivo.hour) * 3600) + \
					(int(x.tiempo_improductivo.minute) * 60) + int(x.tiempo_improductivo.second)

			horas = (segundos) / (3600)
			return (horas)

	# Metodo para obtener todos los datos
	def _query_data(self,op:str,fecha_gte:str,fecha_lte:str):
		# Query Sets de uso general para Improductivos
		self.query_imp_ruedas = MantosImp.objects.filter(
				problema='ruedas', produccion__orden_produccion=op, fecha__gte=fecha_gte, fecha__lte=fecha_lte).exclude(hora_solucion=None)
		self.query_imp_goteros = MantosImp.objects.filter(
				problema='goteros', produccion__orden_produccion=op, fecha__gte=fecha_gte, fecha__lte=fecha_lte).exclude(hora_solucion=None)
		self.query_imp_troquelado = MantosImp.objects.filter(
				problema='troquelado', produccion__orden_produccion=op, fecha__gte=fecha_gte, fecha__lte=fecha_lte).exclude(hora_solucion=None)
		self.query_imp_film = MantosImp.objects.filter(
				problema='film', produccion__orden_produccion=op, fecha__gte=fecha_gte, fecha__lte=fecha_lte).exclude(hora_solucion=None)
		self.query_imp_regulaciones = MantosImp.objects.filter(
				problema='regulaciones', produccion__orden_produccion=op, fecha__gte=fecha_gte, fecha__lte=fecha_lte).exclude(hora_solucion=None)
		self.query_imp_electrico = MantosImp.objects.filter(
				problema='electrico', produccion__orden_produccion=op, fecha__gte=fecha_gte, fecha__lte=fecha_lte).exclude(hora_solucion=None)
		self.query_imp_mecanico = MantosImp.objects.filter(
				problema='mecanico', produccion__orden_produccion=op, fecha__gte=fecha_gte, fecha__lte=fecha_lte).exclude(hora_solucion=None)
		# calculos de improductivos
		#self.improductivo_electrico = self._get_improductivo(query_imp_electrico, True)
		#self.improductivo_mecanico = self._get_improductivo(query_imp_mecanico, True)

	#---------------------------------- METODOS PARA ARMAR EL PDF ----------------------------------------------#

	#Metodo para hacer las tablas y graficos
	def _make_table_graphics(self,estilo) -> dict:
		kargs: Dictionary = dict()
		# Texto, tabla y graficas de produccion
		texto_tabla_produccion = Paragraph(
			u"En la siguiente tabla se presentan los improductivos de producción asociados a la orden de producción " + str(self.op) + ":", estilo['texto'])
		titulo_tabla_produccion = Paragraph(
			u"Improductivos de Producción", estilo['titulo_tablas_graficas'])
		tabla_produccion = self._tabla_produccion()
		texto_grafica_produccion = Paragraph(
		u"En la siguientes graficas se presentan los improductivos de producción asociados a la orden de producción " + str(self.op) + ":", estilo['texto'])
		titulo_grafica_produccion = Paragraph(
			u"Grafica de Improductivos de Producción", estilo['titulo_tablas_graficas'])
		grafica_produccion = self._grafica_produccion()
		titulo_grafica_produccion_total = Paragraph(
			u"Grafica de improductivos de producción totalizados", estilo['titulo_tablas_graficas'])
		grafica_produccion_total = self._grafica_produccion_total()
		# Texto, tabla y graficas de mantenimiento
		texto_tabla_mantenimiento = Paragraph(
			u"En la siguiente tabla se presentan los improductivos de mantenimiento asociados de la orden de producción " + str(self.op) + ":", estilo['texto'])
		titulo_tabla_mantenimiento = Paragraph(
			u"Improductivos de Mantenimiento", estilo['titulo_tablas_graficas'])
		tabla_mantenimiento = self._tabla_mantenimiento()
		texto_grafica_mantenimiento = Paragraph(
			u"En la siguientes graficas se presentan los improductivos de mantenimiento asociados a la orden de producción " + str(self.op) + ":", estilo['texto'])
		titulo_grafica_mantenimiento = Paragraph(
			u"Grafica de Improductivos de Mantenimiento", estilo['titulo_tablas_graficas'])
		grafica_mantenimiento = self._grafica_mantenimiento()
		titulo_grafica_mantenimiento_total = Paragraph(
			u"Grafica de improductivos de mantenimiento totalizados", estilo['titulo_tablas_graficas'])
		grafica_mantenimiento_total = self._grafica_mantenimiento_total()
		#Diccionario para pasarla a la función y retorna una lista con la historia
		kargs ={'texto_tabla_produccion':texto_tabla_produccion,
				'titulo_tabla_produccion':titulo_tabla_produccion,
				'tabla_produccion':tabla_produccion,
				'texto_grafica_produccion':texto_grafica_produccion,
				'titulo_grafica_produccion':titulo_grafica_produccion,
				'grafica_produccion':grafica_produccion,
				'titulo_grafica_produccion_total':titulo_grafica_produccion_total,
				'grafica_produccion_total':grafica_produccion_total,
				'texto_tabla_mantenimiento':texto_tabla_mantenimiento,
				'titulo_tabla_mantenimiento':titulo_tabla_mantenimiento,
				'tabla_mantenimiento':tabla_mantenimiento,
				'texto_grafica_mantenimiento':texto_grafica_mantenimiento,
				'titulo_grafica_mantenimiento':titulo_grafica_mantenimiento,
				'grafica_mantenimiento':grafica_mantenimiento,
				'titulo_grafica_mantenimiento_total':titulo_grafica_mantenimiento_total,
				'grafica_mantenimiento_total':grafica_mantenimiento_total}
		return kargs

	#Metodo para armar el array que contendra todo el contenido	
	def _make_story(self,*args,**kargs):
		# Construyendo el PDF con los valores del diccionario
		story:List =[]
		story.append(Spacer(0, 100))
		story.append(kargs['texto_tabla_produccion'])
		story.append(Spacer(0, 0.5 * cm))
		story.append(kargs['titulo_tabla_produccion'])
		story.append(Spacer(0, 0.5 * cm))
		story.append(kargs['tabla_produccion'])
		story.append(Spacer(0, 1 * cm))
		story.append(kargs['texto_grafica_produccion'])
		story.append(Spacer(0, 0.5 * cm))
		story.append(kargs['titulo_grafica_produccion'])
		story.append(Spacer(0, 0.5 * cm))
		story.append(kargs['grafica_produccion'])
		story.append(NextPageTemplate('contenido'))
		story.append(PageBreak())  # Salto de pagina
		story.append(Spacer(0, 40))
		story.append(kargs['titulo_grafica_produccion_total'])
		story.append(Spacer(0, 0.5 * cm))
		story.append(kargs['grafica_produccion_total'])
		story.append(Spacer(0, 0.6 * cm))
		story.append(kargs['texto_tabla_mantenimiento'])
		story.append(Spacer(0, 1 * cm))
		story.append(kargs['titulo_tabla_mantenimiento'])
		story.append(Spacer(0, 0.6 * cm))
		story.append(kargs['tabla_mantenimiento'])
		story.append(PageBreak())
		story.append(Spacer(0, 40))
		story.append(kargs['texto_grafica_mantenimiento'])
		story.append(Spacer(0, 0.5 * cm))
		story.append(kargs['titulo_grafica_mantenimiento'])
		story.append(Spacer(0, 0.5 * cm))
		story.append(kargs['grafica_mantenimiento'])
		# story.append(Spacer(0,0.3*cm))
		story.append(kargs['titulo_grafica_mantenimiento_total'])
		story.append(Spacer(0, 1.5 * cm))
		story.append(kargs['grafica_mantenimiento_total'])
		return story


	# Metodo para emsamblar el pdf
	def _make_pdf(self):
		# La clase io.BytesIO permite tratar un array de bytes como un fichero
		# binario, se utiliza como almacenamiento temporal dentro de python, para luego ser descargado todo el dato como pdf
		# Se debe pasar el pdf_buffer al BaseDocTemplate
		pdf_buffer = BytesIO()
		#c = canvas.Canvas(buffer)
		doc = BaseDocTemplate(pdf_buffer, pagesize=A4)
		frame0 = Frame(doc.leftMargin, doc.bottomMargin,doc.width, doc.height, showBoundary=0, id='normalBorde') # Frames o marcos de la pagina
		# Plantillas de las hojas, cabecera, pie de pagina, marco de la pagina. Se
		# puede tener varias plantillas. Siempre partira de la primera plantilla
		doc.addPageTemplates([PageTemplate(id='primera_hoja', frames=frame0,onPage=self._cabecera_1, onPageEnd=self._pie_pagina),
							  PageTemplate(id='contenido', frames=frame0, onPage=self._cabecera_contenido, onPageEnd=self._pie_pagina)])
		# Creamos las hojas de Estilos
		estilo = getSampleStyleSheet()
		estilo.add(ParagraphStyle(name="titulo_tablas_graficas",  alignment=TA_CENTER, fontSize=15,
								  fontName="Helvetica-Bold", textColor=colors.Color(0.0390625, 0.4921875, 0.69140625)))
		estilo.add(ParagraphStyle(name="texto",  alignment=TA_LEFT, fontSize=12, fontName="Helvetica", textColor=colors.Color(0, 0, 0)))
		kargs = self._make_table_graphics(estilo) # Dicionario con las tablas y graficas para el story
		story=self._make_story(**kargs)
		doc.build(story) # Se construye el pdf con el array story
		#Descargando todo el buffer
		pdf = pdf_buffer.getvalue()
		pdf_buffer.close()
		return pdf


	def make_report(self) -> object:
			# ejecuando el query para obtener los datos.
			self._query_data(op=self.op,fecha_gte=self.fecha_gte,fecha_lte=self.fecha_lte)
			pdf = self._make_pdf()
			return pdf	