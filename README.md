# Track Mantos	

Track Mantos es una aplicación desarrollada con el framework Django 2.1.4 , python 3.7.0 y Motor de base de datos PostgreSQL.  

La aplicación fue desarrollada con el fin de automatizar la trazabilidad de improductivo causados por fallas en la línea de producción de Mantos Irrigadores, ya que, anteriormente se registraban los tiempos de improductivos de manera manual (en una hoja) y la trazabilidad de improductivos causados por fallas era lenta e imprecisa.

Los improductivos generados puede ser por las siguientes causas:

* Fallas Eléctricas.
* Fallas Mecánicas.
* Fallas de Regulaciones o calibración de la línea de producción.

Con la aplicación se registran los tiempos de cada falla y además puede generar un Excel con los tiempos de improductivos de cada falla, de igual manera, se puede generar un pequeño reporte grafico de los tiempos totales de improductivos. Con la generación de reportes y datos de manera oportuna, se puede dar trazabilidad a cada falla y así realizar un análisis mas profundo para tomar acciones concisas para realizar mejoras en la línea de producción y bajar los tiempos de improductivos causados por fallas.