# Interprete de SQL: pandaQ

## Descripción
Este proyecto es un interprete de SQL donde la información es enviada por una interfície de Streamlit y es procesada con Pandas.

## Funcionalidades principales

- Evaluación de una query SQL junto a un visualización del resultado.
- Guardado de querys en un formato clave valor.
- Representació gràfica de las querys (únicamente variables numéricas).

## Tecnologies utilitzades

- antlr4 para definir la gramática.
- Python para la implementación del interprete.
- Streamlit para definir la interfície gráfica.
- Pandas para hacer el tratamiento de las querys.

## Dependencias

Assegurate de tener les siguientes dependencias instaladas para un funcionamiento correcto del programa:

- python3.12: Es la versión utilizada por el autor, aunque se pueden utilizar de anteriores siempre que sean python3
- antlr4: Libreria de analisi gramatical parala manipulación de llenguajes formales.
- pip: Gestor de paquetes de Python. Verifica que tengas una versión actualizada instalada.
- Streamlit: Librería que ofrece un entorno gráfico sencillo de utilizar.
- Pandas: Libreria que permite tratamiento de datos tabulares.

## Instalación

1. Navega hasta el directorio donde esta contenido el proyecto.
2. Ejecuta el comando ```bash #antlr4 -Dlanguage=Python3 -no-listener -visitor pandaQ.g4.
3. Ejecuta el comando ```bash #streamlit run pandaQ.py.
4. Escribe en la ventana que se ha creado, la query a evaluar.

## Autor

Nombre del desarrollador: Jeremy Comino Raigón
Correo electrónico: jeremy.comino@estudiantat.upc.edu

