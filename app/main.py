# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
#
# Distributed under terms of the GPLv3+ license.

"""

"""
from flask import Flask, render_template,\
    send_from_directory, url_for, redirect
from flask_babel import Babel
from flask_babel import gettext as _

from settings import RUTA_BASE_LIBROS
from utils.utils_libro import normalizar_libros
from utils.utils_url import urlencode, urldecode
from conector.dbprovider import instanciar_conector

app = Flask('__name__')
# Levantamos la config
app.config.from_object("settings")
babel = Babel(app)


# Filtros


def obtener_filtros():
    """Filtros para la barra izquierda"""
    filtros = (
        {'url': url_for('vista_autores'),
         'nombre': _("Authors")},
        {'url': url_for('vista_etiquetas'),
         'nombre': _("Categories")},
        # {'url': url_for('idiomas'),
        # 'nombre': "Idiomas"},
        {'url': url_for('vista_series'),
         'nombre': _("Series")},
    )
    return filtros


def filtrar_por_autor(autor):
    conector = instanciar_conector()
    conector.conectar()
    # obtenemos los libros sin procesar
    libros = conector.obtener_por_autor(autor)
    # Normalizamos la lista de libros
    libros = normalizar_libros(libros, conector)
    conector.desconectar()
    return libros


def filtrar_por_etiqueta(etiqueta):
    conector = instanciar_conector()
    conector.conectar()
    # obtenemos los libros sin procesar
    libros = conector.obtener_por_etiqueta(etiqueta)
    # Normalizamos la lista de libros
    libros = normalizar_libros(libros, conector)
    conector.desconectar()
    return libros


def filtrar_por_serie(serie):
    conector = instanciar_conector()
    conector.conectar()
    serie = urldecode(serie)
    # obtenemos los libros sin procesar
    libros = conector.obtener_por_serie(serie)
    # Normalizamos la lista de libros
    libros = normalizar_libros(libros, conector)
    conector.desconectar()
    return libros


def filtrar_por_nombre(nombre_libro):
    """Filtra por el nombre del libro"""
    conector = instanciar_conector()
    conector.conectar()
    # obtenemos los libros sin procesar
    libros = conector.obtener_por_nombre(nombre_libro)
    # Normalizamos la lista de libros
    libros = normalizar_libros(libros, conector)
    conector.desconectar()
    return libros


def obtener_series_con_url():
    """Devuelve una lista con todos los series"""
    series = []

    conector = instanciar_conector()
    conector.conectar()
    # obtenemos los series sin procesar
    series_crudo = conector.obtener_series()
    for serie in series_crudo:
        serie_safe = urlencode(serie)
        url = url_for('vista_serie_especificada', nombre_serie=serie_safe)
        series.append({'url': url, 'elemento': serie})

    conector.desconectar()
    return series


def obtener_etiquetas_con_url():
    """Devuelve una lista con todos los etiquetas"""
    etiquetas = []

    conector = instanciar_conector()
    conector.conectar()
    # obtenemos los etiquetas sin procesar
    etiquetas_crudo = conector.obtener_etiquetas()
    for etiqueta in etiquetas_crudo:
        etiqueta_safe = urlencode(etiqueta)
        url = url_for(
            'vista_etiqueta_especificada',
            nombre_etiqueta=etiqueta_safe)
        etiquetas.append({'url': url, 'elemento': etiqueta})

    conector.desconectar()
    return etiquetas


def obtener_autores_con_url():
    """Devuelve una lista con todos los autores"""
    autores = []

    conector = instanciar_conector()
    conector.conectar()
    # obtenemos los autores sin procesar
    autores_crudo = conector.obtener_autores()
    for autor in autores_crudo:
        autor_safe = urlencode(autor)
        url = url_for(
            'vista_autor_especificado',
            nombre_autor=autor_safe)
        autores.append({'url': url, 'elemento': autor})

    conector.desconectar()
    return autores


def formatear_elementos_para_template(elementos):
    """Genero un diccionario con clave la primer letra y todos los elementos que
    comiencen con ella en una lista como item"""

    diccionario = {}
    for elemento in elementos:
        # Dentro del elemento hay dos items, 'url' y 'elemento'
        primera_letra = elemento.get('elemento')[0].upper()
        if diccionario.get(primera_letra, None) is None:
            diccionario[primera_letra] = []

        diccionario[primera_letra].append(elemento)
    return diccionario

# Vistas


@app.route('/')
def index():
    return render_template('index.html',
                           titulo="",
                           filtros_generales=obtener_filtros()
                           )


@app.route('/autor/<path:nombre_autor>/')
def vista_autor_especificado(nombre_autor):
    """Muestra los libros de un autor"""
    if not nombre_autor:
        return redirect(url_for('vista_autores'))

    nombre_autor = urldecode(nombre_autor)
    libros = filtrar_por_autor(nombre_autor)

    return render_template("listado_de_libros.html",
                           libros=libros,
                           titulo=nombre_autor,
                           filtros_generales=obtener_filtros()
                           )


@app.route('/autor/')
def redirect_autor():
    return redirect(url_for('vista_autores'))


@app.route('/serie/<path:nombre_serie>/')
def vista_serie_especificada(nombre_serie):
    """Muestra los libros de una etiquea"""
    if not nombre_serie:
        return redirect(url_for('vista_series'))

    nombre_serie = urldecode(nombre_serie)
    libros = filtrar_por_serie(nombre_serie)

    return render_template("listado_de_libros.html",
                           libros=libros,
                           titulo=nombre_serie,
                           filtros_generales=obtener_filtros()
                           )


@app.route('/serie/')
def redirect_serie():
    return redirect(url_for('vista_series'))


@app.route('/etiqueta/<path:nombre_etiqueta>/')
def vista_etiqueta_especificada(nombre_etiqueta):
    """Muestra los libros de una etiquea"""
    if not nombre_etiqueta:
        return redirect(url_for('vista_etiquetas'))

    nombre_etiqueta = urldecode(nombre_etiqueta)
    libros = filtrar_por_etiqueta(nombre_etiqueta)

    return render_template("listado_de_libros.html",
                           libros=libros,
                           titulo=nombre_etiqueta,
                           filtros_generales=obtener_filtros(),
                           )


@app.route('/etiqueta/')
def redirect_etiqueta():
    return redirect(url_for('vista_etiquetas'))


@app.route('/libro/<path:nombre_libro>/')
def vista_libro_especificado(nombre_libro):
    """Muestra el libro pedido"""
    nombre_libro = urldecode(nombre_libro)
    libros = filtrar_por_nombre(nombre_libro)

    return render_template("libro.html",
                           libro=libros[0],
                           titulo=nombre_libro,
                           filtros_generales=obtener_filtros()
                           )


@app.route('/libro/')
def redirect_libro():
    return redirect(url_for('index'))


@app.route('/autores/')
def vista_autores():
    """Lista los autores """
    autores = obtener_autores_con_url()
    autores = formatear_elementos_para_template(autores)

    return render_template("listado_de_entradas.html",
                           entradas=autores,
                           titulo="Autores",
                           filtros_generales=obtener_filtros(),
                           path='autor'
                           )


@app.route('/etiquetas/')
def vista_etiquetas():
    """Lista las etiquetas"""
    etiquetas = obtener_etiquetas_con_url()
    etiquetas = formatear_elementos_para_template(etiquetas)

    return render_template("listado_de_entradas.html",
                           entradas=etiquetas,
                           titulo="Categorias",
                           filtros_generales=obtener_filtros(),
                           path='etiquetas'
                           )


@app.route('/series/')
def vista_series():
    """Lista las series"""
    series = obtener_series_con_url()
    series = formatear_elementos_para_template(series)

    return render_template("listado_de_entradas.html",
                           entradas=series,
                           titulo="Series",
                           filtros_generales=obtener_filtros(),
                           path='series'
                           )


@app.route('/tapas/<path:ruta>')
def devolver_tapa(ruta):
    ruta_safe = urldecode(ruta)
    return send_from_directory(RUTA_BASE_LIBROS, ruta_safe)


@app.route('/archivo/<path:ruta>')
def devolver_libro_descarga(ruta):
    ruta_safe = urldecode(ruta)
    return send_from_directory(RUTA_BASE_LIBROS, ruta_safe)


# Habilita a usar esta funcion desde los templates
@app.context_processor
def utility_processor():
    return dict(urlencode=urlencode)
