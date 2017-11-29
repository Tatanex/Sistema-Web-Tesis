# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import codecs
import os
import shutil
# Create your views here.
import string
from lxml import etree
from subprocess import Popen

import collections

from bs4 import BeautifulSoup, NavigableString
from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.encoding import smart_str
from eppy import modeleditor
from eppy.modeleditor import IDF
from readhtml import NotSimpleTable


from .models import Simular, Comparar, Modificar, Material, Combinar
def indexView(request):
    simulacion = Simular.objects.all ()
    cantidad_simulacion = len (simulacion)

    modificacion = Modificar.objects.all ()
    cantidad_modificacion = len (modificacion)

    comparacion = Comparar.objects.all ()
    cantidad_comparacion = len (comparacion)



    combinacion = Combinar.objects.all ()
    cantidad_combinacion = len (combinacion)

    return render (request, 'layout.html', {'simulacion': cantidad_simulacion, 'modificacion': cantidad_modificacion,
                                            'comparacion': cantidad_comparacion,  'combinacion': cantidad_combinacion})


def simularView(request, simulacion_id):
    simulacion = get_object_or_404 (Simular, pk=simulacion_id)
    return render (request, 'simular.html', {'simulacion': simulacion})


# HTTP Error 400
def error_404View(request):
    return render (request, 'page_404.html')


from .forms import CargarArchivosForm, CompararIdfsForm, ModificarIdfsForm, MaterialForm


def cargar_archivo_simulacion_view(request):
    if request.method == 'POST':
        form = CargarArchivosForm (request.POST, request.FILES)
        if form.is_valid ():
            nueva_simulacion = form.save ()
            simulacion = get_object_or_404 (Simular, pk=nueva_simulacion.pk)
            message = "Archivos cargados satisfactoriamente !"
            return render (request, 'simular.html', {'simulacion': simulacion, 'message': message})
    else:
        form = CargarArchivosForm ()
    return render (request, 'upload.html', locals (), {'form': form})


def submit(request, args):
    if request.method == 'POST':
        WeatherData = '/usr/local/EnergyPlus-8-6-0/WeatherData/'
        iddfile = '/usr/local/EnergyPlus-8-6-0/Energy+.idd'
        try:
            IDF.setiddname(iddfile)
        except modeleditor.IDDAlreadySetError as e:
            pass

        IDF.setiddname(iddfile)
        simulation = get_object_or_404 (Simular, pk=args)
        b = str (simulation.simular_clima)
        # print (b)
        climapalabra = b.split ("/")
        # print (climapalabra)
        clima = climapalabra[1]
        if os.path.isfile ('/usr/local/EnergyPlus-8-6-0/WeatherData/' + clima) == True:
            clima_oficial = WeatherData + clima
        else:
            shutil.copy ('media/' + b, '/usr/local/EnergyPlus-8-6-0/WeatherData/')

            clima_oficial = WeatherData + clima

        a = 'media/' + str (simulation.simular_archivo_idf)
        nueva_carpeta = 'simulaciones/simulacion_' + str (args)
        # print (nueva_carpeta)
        if not os.path.exists (nueva_carpeta): os.makedirs (nueva_carpeta)
        p = Popen (['/usr/local/EnergyPlus-8-6-0/runenergyplus', a, clima, '-d', nueva_carpeta, '-p',
                    str (args)]).wait ()

        shutil.move ("media/idf/Output", "simulaciones/simulacion_" + str (args))

        path_archivo_simulacion = ('simulaciones/simulacion_' + str (args) + '/Output/')
        for file in os.listdir (path_archivo_simulacion):
            if file.endswith (".html"):
                # print (file)
                html_data = codecs.open (str (path_archivo_simulacion + file), "r", encoding='utf-8',
                                         errors='ignore').read ()
                content = (path_archivo_simulacion + file)
                # print (content)

        return render (request, 'simulando.html', {'f': html_data, 'path': content})


def ver_simulaciones(request):
    lista_simular = Simular.objects.all ()
    # for x in lista_simular:
    #     print(x)
    context = {'lista_simular': lista_simular}
    return render (request, 'ver_simulacion.html', context)


def ver(request, args):
    # print (args)
    path_archivo_simulacion = ('simulaciones/simulacion_' + str (args) + '/Output/')
    for reporte in os.listdir (path_archivo_simulacion):
        if reporte.endswith ("html"):
            # print (reporte)
            # html_data =  codecs.open (str(path_archivo_simulacion+file),"r", encoding='utf-8', errors='ignore').read()
            html_data = codecs.open (str (path_archivo_simulacion + reporte), "r", encoding='utf-8',
                                     errors='ignore').read ()

            # context = {'some_key': 'some_value'}
            content = (path_archivo_simulacion + reporte)
            # print (content)
    return render (request, 'simulando.html', {'f': html_data, 'path': content})


def ver_demanda(request, args):
    # print (args)

    lista_de_valores = []
    path_archivo_simulacion = ('simulaciones/simulacion_' + str (args) + '/Output/')
    for reporte in os.listdir (path_archivo_simulacion):
        if reporte.endswith ("html"):
            # print (reporte)
            html_data = codecs.open(str (path_archivo_simulacion + reporte), "r", encoding='utf-8',
                                     errors='ignore').read ()
            # html_data = codecs.open(str (path_archivo_simulacion + reporte), "r", encoding='utf-8',
            #                          errors='ignore').read()


            htables = titletable(html_data)

            header = []
            # TITLE Total Energy (kWh) / Total Site Energy
            attrib = (str (htables[0][1][0][1]) + '/' + str (htables[0][1][1][0]))
            header.append (attrib)
            # TITLE Total Energy (kWh) / Total Source Energy
            attrib1 = (str (htables[0][1][0][1]) + '/' + str (htables[0][1][3][0]))
            header.append (attrib1)
            # TITLE End_Uses

            attrib2 = (str (htables[17][1][0][5]) + '/' + str (htables[17][1][2][0]))
            header.append (attrib2)

            attrib3 = (str (htables[17][1][0][4]) + '/' + str (htables[17][1][3][0]))
            header.append (attrib3)

            # TITLE Facility(Hours) / Time Setpoint Not met  during occupied heating.
            attrib4 = (str (htables[11][1][0][1]) + '/' + str (htables[11][1][1][0]))
            header.append (attrib4)
            # TITLE HVAC / District Heating Intensity [kWh/m2]
            attrib5 = (str (htables[6][1][0][5]) + '/' + str (htables[6][1][2][0]))
            header.append (attrib5)

            Site_and_Source_Energy = htables[0]
            Site_to_Source_Energy_Conversion_Factors = htables[1]
            Building_Area = htables[2]
            End_Uses = htables[3]
            Comfort_and_Setpoint_Not_Met_Summary = htables[11]
            Utility_Use_Per_Conditioned_Floor_Area = htables[6]

            valores = []
            valores.append (htables[0][1][1][1])
            valores.append (htables[0][1][3][1])
            valores.append (htables[17][1][2][5])
            valores.append (htables[17][1][3][4])
            valores.append (htables[11][1][1][1])
            valores.append (htables[6][1][2][5])

            return render (request, 'valores_simulacion.html', {'html': header, 'valores':valores, 'args' : args})


def is_simpletable(table):
    """test if the table has only strings in the cells"""
    tds = table ('td')
    for td in tds:
        if td.contents != []:
            if len (td.contents) == 1:
                if not isinstance (td.contents[0], NavigableString):
                    return False
            else:
                return False
    return True


def table2matrix(table):
    """convert a table to a list of lists - a 2D matrix"""

    if not is_simpletable (table):
        raise NotSimpleTable ("Not able read a cell in the table as a string")
    rows = []
    for tr in table ('tr'):
        row = []
        for td in tr ('td'):
            try:
                row.append (td.contents[0])
            except IndexError:
                row.append ('')
        rows.append (row)
    return rows


def table2val_matrix(table):
    """convert a table to a list of lists - a 2D matrix
    Converts numbers to float"""
    if not is_simpletable (table):
        raise NotSimpleTable ("Not able read a cell in the table as a string")
    rows = []
    for tr in table ('tr'):
        row = []
        for td in tr ('td'):
            try:
                val = td.contents[0]
            except IndexError:
                row.append ('')
            else:
                try:
                    val = float (val)
                    row.append (val)
                except ValueError:
                    row.append (val)
        rows.append (row)
    return rows


def titletable(html_doc, tofloat=True):
    """return a list of [(title, table), .....]

    title = previous item with a <b> tag
    table = rows -> [[cell1, cell2, ..], [cell1, cell2, ..], ..]"""
    soup = BeautifulSoup (html_doc, "html.parser")
    btables = soup.find_all (['b', 'table'])  # find all the <b> and <table>
    titletables = []
    for i, item in enumerate (btables):
        if item.name == 'table':
            for j in range (i + 1):
                if btables[i - j].name == 'b':  # step back to find a <b>
                    break
            titletables.append ((btables[i - j], item))
    if tofloat:
        t2m = table2val_matrix
    else:
        t2m = table2matrix
    titlerows = [(tl.contents[0], t2m (tb)) for tl, tb in titletables]
    return titlerows


def _has_name(soup_obj):
    """checks if soup_obj is really a soup object or just a string
    If it has a name it is a soup object"""
    try:
        name = soup_obj.name
        if name == None:
            return False
        return True
    except AttributeError:
        return False


def lines_table(html_doc, tofloat=True):
    """return a list of [(lines, table), .....]

    lines = all the significant lines before the table.
        These are lines between this table and
        the previous table or 'hr' tag
    table = rows -> [[cell1, cell2, ..], [cell1, cell2, ..], ..]

    The lines act as a description for what is in the table
    """
    soup = BeautifulSoup (html_doc, "html.parser")
    linestables = []
    elements = soup.p.next_elements  # start after the first para
    for element in elements:
        tabletup = []
        if not _has_name (element):
            continue
        if element.name == 'table':  # hit the first table
            beforetable = []
            prev_elements = element.previous_elements  # walk back and get the lines
            for prev_element in prev_elements:
                if not _has_name (prev_element):
                    continue
                if prev_element.name not in ('br', None):  # no lines here
                    if prev_element.name in ('table', 'hr', 'tr', 'td'):
                        # just hit the previous table. You got all the lines
                        break
                    if prev_element.parent.name == "p":
                        # if the parent is "p", you will get it's text anyways from the parent
                        pass
                    else:
                        if prev_element.get_text ():  # skip blank lines
                            beforetable.append (prev_element.get_text ())
            beforetable.reverse ()
            tabletup.append (beforetable)
            function_selector = {True: table2val_matrix, False: table2matrix}
            function = function_selector[tofloat]
            tabletup.append (function (element))
        if tabletup:
            linestables.append (tabletup)
    return linestables


def _asciidigits(s):
    """if s is not ascii or digit, return an '_' """
    if s not in string.ascii_letters + string.digits:
        s = '_'
    return s


def _nospace(s):
    """replace all non-ascii, non_digit or space with '_' """
    return ''.join ([_asciidigits (i) for i in s])


def _transpose(arr):
    return list (map (list, list (zip (*arr))))


def _make_ntgrid(grid):
    """make a named tuple grid

    [["",  "a b", "b c", "c d"],
     ["x y", 1,     2,     3 ],
     ["y z", 4,     5,     6 ],
     ["z z", 7,     8,     9 ],]
    will return
    ntcol(x_y=ntrow(a_b=1, b_c=2, c_d=3),
          y_z=ntrow(a_b=4, b_c=5, c_d=6),
          z_z=ntrow(a_b=7, b_c=8, c_d=9))"""
    hnames = [_nospace (n) for n in grid[0][1:]]
    vnames = [_nospace (row[0]) for row in grid[1:]]
    vnames_s = " ".join (vnames)
    hnames_s = " ".join (hnames)
    ntcol = collections.namedtuple ('ntcol', vnames_s)
    ntrow = collections.namedtuple ('ntrow', hnames_s)
    rdict = [dict (list (zip (hnames, row[1:]))) for row in grid[1:]]
    ntrows = [ntrow (**rdict[i]) for i, name in enumerate (vnames)]
    ntcols = ntcol (**dict (list (zip (vnames, ntrows))))
    return ntcols


def named_grid_h(grid):
    """make a horizontal named grid"""
    return _make_ntgrid (grid)


def named_grid_v(grid):
    """make a vertical named grid"""
    return _make_ntgrid (_transpose (grid))

def compararidf(request):

    if request.method == 'POST':

        form = CompararIdfsForm (request.POST, request.FILES)
        file1 = str(request.FILES['comparar_archivo_idf1'])
        file2 = str(request.FILES['comparar_archivo_idf2'])



        if( file1 == file2):
            message = "LOS ARCHIVOS SON IGUALES, NO EXISTE DIFERENCIAS. INGRESE LOS ARCHIVOS NUEVAMENTE."
            form = CompararIdfsForm ()
            return render (request, 'comparar.html', locals (), {'form': form, 'message': message})

        else:
            message = "LOS ARCHIVOS FUERON EXITOSAMENTE CARGADOS."
            if form.is_valid():


                nueva_comparacion = form.save ()
                comparacion = get_object_or_404 (Comparar, pk=nueva_comparacion.pk)

                iddfile = '/usr/local/EnergyPlus-8-6-0/Energy+.idd'
                try:
                    IDF.setiddname (iddfile)
                except modeleditor.IDDAlreadySetError as e:
                    pass
                IDF.setiddname (iddfile)
                path_idf1 = str('media/comparacion_idf/'+file1)
                path_idf2 = str('media/comparacion_idf/'+file2)
                idf1 = IDF(path_idf1)
                idf2 = IDF(path_idf2)

                # condicion si el archivo mejorado tiene los mismos items que el archivo alternativo
                if (idf1.idfobjects.items().__eq__ (idf2.idfobjects.items()) == True):
                    message = "LOS ARCHIVOS SON IGUALES, NO EXISTE DIFERENCIAS. INGRESE LOS ARCHIVOS NUEVAMENTE."
                    form = CompararIdfsForm ()
                    return render (request, 'comparar.html', locals (), {'form': form, 'message': message})

                else:

                    message = "LOS ARCHIVOS FUERON EXITOSAMENTE CARGADOS."
                    # Crea e instancia
                    resultado_alternativa_idf1 = diferencias_idf (idf2, idf1, idf1.idfname)
                    # print(resultado_alternativa_idf1)
                    diccionario_idf1_1 = {}
                    diccionario_idf2_1 = {}
                    k_1 = (resultado_alternativa_idf1.keys ())
                    for cantidad_clases in range (0, len (k_1)):
                        clases1 = idf1.idfobjects[k_1[cantidad_clases]]
                        diccionario_idf1_1[k_1[cantidad_clases]] = clases1

                    # **********************************************************************


                        # Crea e instancia
                resultado_alternativa_idf2 = diferencias_idf (idf1, idf2, idf2.idfname)

                diccionario_idf1_2 = {}
                diccionario_idf2_2 = {}
                k_2 = (resultado_alternativa_idf2.keys ())
                for cantidad_clases in range (0, len (k_2)):
                    clases2 = idf2.idfobjects[k_2[cantidad_clases]]
                    diccionario_idf2_2[k_2[cantidad_clases]] = clases2

                source = 'media/data_materiales1.xml'
                doc = etree.parse (source)
                raiz = doc.getroot ()
                materiales = doc.findall ("Material")
                diccionario_materiales = {}
                for m in materiales:
                    diccionario_materiales[m.attrib['Id']] = m.attrib['Name']

                lista_construccion = []
                lista_construccion2 = []

                clase_construccion = {}
                clase_construccion2 = {}

                tag_construcction = 'CONSTRUCTION'

                objetos_construccion = idf1.idfobjects[tag_construcction]
                objetos_construccion2 = idf2.idfobjects[tag_construcction]

                for t in objetos_construccion:
                    lista_construccion.append (t)

                for t2 in objetos_construccion2:
                    lista_construccion2.append (t2)

                clase_construccion[tag_construcction] = lista_construccion
                clase_construccion2[tag_construcction] = lista_construccion2

                construccion_diff_2 = clases_distintas_construcciones (idf2, idf1, idf2.idfname)
                construccion_diff_1 = clases_distintas_construcciones (idf1, idf2, idf1.idfname)

                # KEY IDF1
                c_diff_keys_1 = []
                for x in construccion_diff_2.values ():
                    for t in x:
                        for m in t:
                            c_diff_keys_1.append (m)

                # VALUES IDF1
                c_diff_values_1 = []
                for x in construccion_diff_2.values ():
                    for t in x:
                        for z in (t.values ()):
                            for y in z:
                                c_diff_values_1.append (y)

                # KEY IDF2
                c_diff_keys_2 = []
                for w in construccion_diff_1.values ():
                    for o in w:
                        for b in o:
                            c_diff_keys_2.append (b)

                return render (request, 'test2.html',
                               {'resultado_alternativa_idf1': resultado_alternativa_idf1,
                                'resultado_alternativa_idf2': resultado_alternativa_idf2,
                                'id_comparacion': comparacion.comparar_id,
                                'ruta_idf1': file1, 'ruta_idf2': file2,
                                'diccionario_idf1': diccionario_idf1_1,
                                'diccionario_idf2': diccionario_idf2_2,
                                'construccion_diff_1': construccion_diff_1,
                                'construccion_diff_2': construccion_diff_2, 'tag_construcction': tag_construcction,
                                'clase_construccion': clase_construccion,
                                'diccionario_materiales': diccionario_materiales,
                                'clase_construccion2': clase_construccion2, 'c_diff_keys_1': c_diff_keys_1,
                                'c_diff_keys_2': c_diff_keys_2, 'objetos_construccion': objetos_construccion,
                                'objetos_construccion2': objetos_construccion2,
                                'c_diff_values_1': c_diff_values_1, 'message' : message})

    else:
        form = CompararIdfsForm ()
    return render (request, 'comparar.html', locals (), {'form': form})


def ver_comparaciones(request):
    lista_comparaciones = Comparar.objects.all ()

    context = {'lista_comparaciones': lista_comparaciones}
    return render (request, 'ver_comparaciones.html', context)


def detalle_comparacion(request, args_id):
    # print (args_id)
    comparacion = get_object_or_404 (Comparar, pk=args_id)
    iddfile = '/usr/local/EnergyPlus-8-6-0/Energy+.idd'
    try:
        IDF.setiddname (iddfile)
    except modeleditor.IDDAlreadySetError as e:
        pass
    IDF.setiddname (iddfile)
    path_idf1 = str(comparacion.comparar_archivo_idf1)
    ruta_idf1 = path_idf1.split ('/')

    path_idf2 = str(comparacion.comparar_archivo_idf2)
    ruta_idf2 = path_idf2.split ('/')

    idf1 = IDF ('media/' + path_idf1)
    # print(comparacion.comparar_archivo_idf2)
    idf2 = IDF ('media/' + path_idf2)
    # condicion si el archivo mejorado tiene los mismos items que el archivo alternativo
    if (idf1.idfobjects.items ().__eq__ (idf2.idfobjects.items ()) == True):
        message = "Los archivos son iguales, no existe diferencias.!"
        form = CompararIdfsForm ()
        return render (request, 'comparar.html', locals (), {'form': form})

    else:

        message = "Los archivos son iguales, no existe diferencias.!"

        # Crea e instancia
        resultado_alternativa_idf1 = diferencias_idf (idf2, idf1, idf1.idfname)
        # print(resultado_alternativa_idf1)
        diccionario_idf1_1 = {}
        diccionario_idf2_1 = {}
        k_1 = (resultado_alternativa_idf1.keys ())
        for cantidad_clases in range (0, len (k_1)):
            clases1 = idf1.idfobjects[k_1[cantidad_clases]]
            diccionario_idf1_1[k_1[cantidad_clases]] = clases1


        # **********************************************************************

            # Crea e instancia
        resultado_alternativa_idf2 = diferencias_idf (idf1, idf2, idf2.idfname)

        diccionario_idf1_2 = {}
        diccionario_idf2_2 = {}
        k_2 = (resultado_alternativa_idf2.keys ())
        for cantidad_clases in range (0, len (k_2)):
            clases2 = idf2.idfobjects[k_2[cantidad_clases]]
            diccionario_idf2_2[k_2[cantidad_clases]] = clases2

        source = 'media/data_materiales1.xml'
        doc = etree.parse (source)
        raiz = doc.getroot ()
        materiales = doc.findall ("Material")
        diccionario_materiales = {}
        for m in materiales:
            diccionario_materiales[m.attrib['Id']] = m.attrib['Name']

        lista_construccion = []
        lista_construccion2 = []

        clase_construccion = {}
        clase_construccion2 = {}

        tag_construcction = 'CONSTRUCTION'

        objetos_construccion = idf1.idfobjects[tag_construcction]
        objetos_construccion2 = idf2.idfobjects[tag_construcction]

        for t in objetos_construccion:
            lista_construccion.append (t)

        for t2 in objetos_construccion2:
            lista_construccion2.append (t2)

        clase_construccion[tag_construcction] = lista_construccion
        clase_construccion2[tag_construcction] = lista_construccion2

        construccion_diff_2 = clases_distintas_construcciones(idf2, idf1, idf2.idfname)
        construccion_diff_1 = clases_distintas_construcciones(idf1, idf2, idf1.idfname)

        # KEY IDF1
        c_diff_keys_1 = []
        for x in construccion_diff_2.values():
            for t in x:
                for m in t:
                    c_diff_keys_1.append(m)

        # VALUES IDF1
        c_diff_values_1 = []
        for x in construccion_diff_2.values():
            for t in x:
                for z in (t.values()):
                    for y in z:
                        c_diff_values_1.append(y)






        #KEY IDF2
        c_diff_keys_2 = []
        for w in construccion_diff_1.values ():
            for o in w:
                for b in o:
                    c_diff_keys_2.append (b)



        return render (request, 'test2.html',
                           {'resultado_alternativa_idf1': resultado_alternativa_idf1,
                            'resultado_alternativa_idf2': resultado_alternativa_idf2,
                            'id_comparacion': comparacion.comparar_id,
                            'ruta_idf1': ruta_idf1[1], 'ruta_idf2': ruta_idf2[1],
                            'diccionario_idf1': diccionario_idf1_1,
                            'diccionario_idf2': diccionario_idf2_2,
                            'construccion_diff_1': construccion_diff_1,
                            'construccion_diff_2': construccion_diff_2, 'tag_construcction': tag_construcction,
                            'clase_construccion': clase_construccion,
                            'diccionario_materiales': diccionario_materiales,
                            'clase_construccion2': clase_construccion2, 'c_diff_keys_1': c_diff_keys_1,
                            'c_diff_keys_2':c_diff_keys_2, 'objetos_construccion':objetos_construccion,
                            'objetos_construccion2' : objetos_construccion2,
                            'c_diff_values_1' : c_diff_values_1,'message' : message})

    # return render (request, 'test2.html',
    #                    {'resultado_alternativa_idf1': resultado_alternativa_idf1,
    #                     'resultado_alternativa_idf2': resultado_alternativa_idf2, 'id_comparacion': comparacion.comparar_id,
    #                     'ruta_idf1': ruta_idf1[1], 'ruta_idf2': ruta_idf2[1], 'diccionario_idf1': diccionario_idf1_1,
    #                     'diccionario_idf2': diccionario_idf2_2,
    #                     'construccion_diff_1': construccion_diff_1,
    #                     'construccion_diff_2': construccion_diff_2.values(), 'tag_construcction': tag_construcction,
    #                     'clase_construccion': clase_construccion, 'diccionario_materiales':diccionario_materiales,
    #                     'clase_construccion2' : clase_construccion2,
    #                     'lista_llave_diff2' : lista_llave_diff2, 'lista_llave_diff1' : lista_llave_diff1,
    #                     'lista_valor_diff1' : lista_valor_diff1, 'lista_valor_diff2' : lista_valor_diff2})


# METODOS SCRIPTS PYTHON
def diferencias_idf(idf_file1, idf_file2, nombreIDF):
    clasesdistintas = []
    diccionario_aux = {}
    diccionario_casos = {}
    # Recorrer clases del archivo IDF.
    for objname1, objname2 in zip (idf_file1.model.dtls, idf_file2.model.dtls):
        # Comparación de igualdad entre objetos de los archivos IDF'S.
        result = (idf_file1.idfobjects[objname1]).__eq__ (idf_file2.idfobjects[objname1])
        # Condición pregunta si las clases son distintas en los archivos IDF'S.
        if (result != True):
            # Guarda las clases distintas entre los archivos IDF'S.
            clasesdistintas.append (objname1)
            # Genera diccionario de datos con el nombre del archivo IDF y las clases distintas con respecto al IDF mejorado.
            diccionario_casos[nombreIDF] = clasesdistintas

    # print(diccionario_casos)
    c = 1
    # Recorre diferencias de clases en archivos.
    for clase in clasesdistintas:
        listaauxobject = []
        objetos_cm = []
        objetosdelcaso = []
        numeroobjetos = 0
        lista_auxiliares = []
        if (clase == 'MATERIAL' or
                    clase == 'MATERIAL:NOMASS' or
                    clase == 'WINDOWMATERIAL:GLAZING' or
                    clase == 'WINDOWMATERIAL:GAS' or
                    clase == 'CONSTRUCTION' or
                    clase == 'BUILDINGSURFACE:DETAILED'):
            lista_auxiliares = []
            # Recorre objeto de las clases en lista distinta del caso alternativa.
            for objeto in range (0, len (idf_file2.idfobjects[clase])):  # Cantidad de objetos de la clase.
                cont = 0
                if (len (idf_file1.idfobjects[clase]) == 0):
                    lista_auxiliares.append (idf_file2.idfobjects[clase][objeto].fieldvalues[1])
                    diccionario_aux[str (clase)] = lista_auxiliares
                    cont += 1
                else:
                    while (cont < len (idf_file1.idfobjects[clase])):
                        # Condición si el nombre del campo atributo es igual a nombre entonces.
                        if (idf_file2.idfobjects[clase][objeto].fieldnames[1] == 'Name'):
                            # Compara valor nombre del objeto en la clase actual en los distintos archivos.
                            existe = ((idf_file2.idfobjects[clase][objeto].fieldvalues[1]).__eq__ (
                                idf_file1.idfobjects[clase][cont].fieldvalues[1]))
                            # Nombre de objeto existe en archivo del caso inicial.
                            if (existe == True):
                                # dif_a = DiferenciaAtributos ()  # instancia objeto de la clase DiferenciaAtributos()
                                resultado = pos_atributo (idf_file2.idfobjects[clase][objeto],
                                                          idf_file1.idfobjects[clase][cont])
                                # Objetos totalmente iguales.
                                if (resultado == 1):
                                    # Almacena objeto de caso mejorado.
                                    listaauxobject.append (idf_file1.idfobjects[clase][cont])
                                    objetos_cm.append (idf_file1.idfobjects[clase][cont])
                                    cont = 5000
                                cont = 5000
                            # No es igual el nombre del objeto a comparar.
                            else:
                                if (cont == len (idf_file1.idfobjects[clase]) - 1):
                                    lista_auxiliares.append (idf_file2.idfobjects[clase][objeto].fieldvalues[1])
                                    diccionario_aux[str (clase)] = lista_auxiliares
                                cont += 1
            c += 1
    return (diccionario_aux)


def pos_atributo(obj1, obj2):
    # Condición si los objetos tienen la misma dimensión.
    if (len (obj1.fieldvalues) == len (obj2.fieldvalues)):
        atributo = 2
        # Mientras no llegue al ultimo atributo del objeto, iterar.
        while (atributo < len (obj2.fieldvalues)):
            # Iterar sobre los objetos.
            resultado = ((obj2.fieldvalues[atributo]).__eq__ (obj1.fieldvalues[atributo]))
            # El atributo actual es igual al atributo del objeto en el caso a comparar.
            if (resultado == True):
                atributo += 1
            # El atributo actual es distinto al atributo del objeto en el caso a comparar.
            else:
                atributo = 1000
        if (atributo == len (obj2.fieldvalues)):
            return 1
        else:
            return 0
    else:
        return 0


def ver_objeto(request, idf, args_id, args_class, args_name):
    # print (idf)
    # print (args_id)
    # print (args_class)
    # print (args_name)
    comparacion = get_object_or_404 (Comparar, pk=args_id)
    materials = Material.objects.all ()
    iddfile = '/usr/local/EnergyPlus-8-6-0/Energy+.idd'
    try:
        IDF.setiddname (iddfile)
    except modeleditor.IDDAlreadySetError as e:
        pass
    IDF.setiddname (iddfile)
    path_idf1 = str (comparacion.comparar_archivo_idf1)
    path_idf2 = str (comparacion.comparar_archivo_idf2)

    idf1 = IDF ('media/' + path_idf1)
    # print(comparacion.comparar_archivo_idf2)
    idf2 = IDF ('media/' + path_idf2)

    list = []
    if idf == 'idf_1':
        for objeto in idf1.idfobjects[args_class]:
            if objeto.Name == args_name:
                atributos = objeto.fieldnames
                print (atributos)
                valores = objeto.fieldvalues
                print (valores)
                list = zip (atributos, valores)
                return render (request, 'ver_objeto.html',
                               {'list': list, 'objeto': objeto, 'args_name': args_name, 'args_class': args_class,
                                'materials': materials})

    if idf == 'idf_2':
        for objeto in idf2.idfobjects[args_class]:
            if objeto.Name == args_name:
                atributos = objeto.fieldnames
                print (atributos)
                valores = objeto.fieldvalues
                print (valores)
                list = zip (atributos, valores)
                return render (request, 'ver_objeto.html',
                               {'list': list, 'objeto': objeto, 'args_name': args_name, 'args_class': args_class,
                                'materials': materials})


                #
                # else:
                #     print ("NO EXISTE")

                # return render (request, 'ver_objeto.html', {'args1': args1, 'args2': args2  })


def clases_distintas(idf_file1, idf_file2, nombreIDF):
    clasesdistintas = []
    # print("TOTAL DE OBJETOS CASO BASE: "+ str(len(idf_casobase.model.dtls)))
    # print("TOTAL DE OBJETOS ALTERNATIVA 1: "+str(len(idf_file2.model.dtls)))
    # print("")
    diccionario_casos = {}
    diccionario_diff = {}
    vector_diff = []
    # print (str(c)+ " CLASE: " + clase) #EJEMPLO: 1 CLASE: MATERIAL
    # print (len(idf_file2.idfobjects[clase]))
    listaauxobject = []
    objetos_cm = []
    objetosdelcaso = []
    # print ("CANTIDAD OBJETOS CASO MEJORADO: " +str(len(idf_file1.idfobjects[clase])))  # TOTAL DE ELEMENTOS INCLUYENDO VACIOS
    # print ("CANTIDAD OBJETOS CASO 1: " + str(len(idf_file2.idfobjects[clase])))  # ELEMENTOS NO VACIOS DE UN OBJETO
    clase = 'CONSTRUCTION'
    # print (str (c) + " CLASE: " + clase)  # EJEMPLO: 1 CLASE: MATERIAL
    # RECORRE OBJETO DE LAS CLASE EN LISTA DISTINTA DEL CASO ALTERNATIVO.
    for objeto in range (0, len (idf_file2.idfobjects[clase])):  # CANTIDAD DE OBJETOS DE LA CLASE CASOS.
        # print(len(idf_file2.idfobjects[clase][objeto].fieldnames))  #TOTAL DE ELEMENTOS INCLUYENDO VACIOS
        # print(len(idf_file2.idfobjects[clase][objeto].fieldvalues)) #ELEMENTOS NO VACIOS DE UN OBJETO
        cont = 0
        # MIENTRAS CONTADOR SEA MENOR A NUMERO TOTAL DE OBJETOS EN CASO MEJORADO.
        while (cont < len (idf_file1.idfobjects[clase])):
            a_aux = 0
            # RECORRE ATRIBUTOS DEL OBJETOS.
            while (a_aux < 2):
                # CONDICION SI EL NOMBRE DEL CAMPO ATRIBUTO ES IGUAL A NOMBRE ENTONCES.
                if (idf_file2.idfobjects[clase][objeto].fieldnames[a_aux] == 'Name'):
                    # COMPARA VALOR NOMBRE DEL OBJETOS EN LA CLASE ACTUAL EN LOS DISTINTOS ARCHIVOS.
                    existe = ((idf_file2.idfobjects[clase][objeto].fieldvalues[a_aux]).__eq__ (
                        idf_file1.idfobjects[clase][cont].fieldvalues[a_aux]))
                    # NOMBRE DE OBJETO EXISTE EN ARCHIVO DEL CASO MEJORADO
                    if (existe == True):
                        resultado = pos_atributo (idf_file2.idfobjects[clase][objeto],
                                                  idf_file1.idfobjects[clase][cont])

                        if (resultado == 1):  # OBJETOS IGUALES TOTALMENTE.

                            listaauxobject.append (idf_file1.idfobjects[clase][cont])  # GUARDO OBJETO DE CASO MEJORADO
                            objetos_cm.append (idf_file1.idfobjects[clase][cont])
                            a_aux = 1000
                        else:  # OBJETO DISTINTO ENTRE ARCHIVOS IDF'S
                            print ("OBJETOS DISTINTOS EN SUS ATRIBUTOS :" +
                                   idf_file2.idfobjects[clase][objeto].fieldvalues[a_aux] + "  -  " +
                                   idf_file1.idfobjects[clase][cont].fieldvalues[a_aux])

                            objetosdelcaso.append (idf_file1.idfobjects[clase])
                            listaauxobject.append (idf_file1.idfobjects[clase][cont])  # GUARDO OBJETO DE CASO MEJORADO
                            vector_diff.append (idf_file2.idfobjects[clase][objeto].fieldvalues[a_aux])
                            a_aux = 5000
                    else:  # NO ES IGUAL EL NOMBRE DEL OBJETO A COMPRAR
                        if ((cont == len (idf_file1.idfobjects[clase]) - 1) and (
                                        idf_file1.idfobjects[clase][cont] in objetos_cm == False)):
                            print ("llege al objeto final")
                            a_aux = 1000
                        # #AVANZAR DE OBJETO.
                        else:
                            a_aux = 1000
                else:  # EL CAMPO DEL OBJETO NO ES NOMBRE, AUMENTO EN 1 PARA LLEGAR AL CAMPO 'Name' del OBJETO.
                    a_aux += 1
            cont += 1
    # distinto = dif_o.dif_objetos(idf_file1.idfobjects[clase],listaauxobject)
    distinto1 = dif_objetos (idf_file1.idfobjects[clase], idf_file2.idfobjects[clase])
    # print(distinto1)
    diccionario_diff[clase] = vector_diff
    if ((len (idf_file1.idfobjects[clase]) == 0)):
        for h in range (0, len (idf_file2.idfobjects[clase])):
            print ("OBJETO DIFERENTES :" + str (idf_file2.idfobjects[clase][h].fieldvalues[1]))
            # print(str(idf_file1.idfobjects[clase][h].fieldvalues[1]))
    print (" ")
    return (diccionario_diff)


def dif_objetos(idf_class1, idf_class2):  # RECIBE CLASE COMPLETA
    # print("DIMENSION ARREGLO CLASE X EN CM "+ str(len(idf_class1)))
    # print("DIMENSION ARREGLO CLASE Y EN CASOX "+ str(len(idf_class2)))
    lista_aux = []
    for x in range (0, len (idf_class1)):
        lista_aux = []
        y = 0
        while (y < len (idf_class2)):
            if (idf_class1[x].fieldvalues[1] == idf_class2[y].fieldvalues[1]):  # SI SON IGUALES
                # print (idf_class1[x].fieldvalues[1] + " - " + idf_class2[y].fieldvalues[1])
                y = 5000  # AUMENTA EL CONTADOR PARA OTRO OBJETO EN X
            else:  # SI NO ES IGUAL
                # print (idf_class1[x].fieldvalues[1] + " - " + idf_class2[y].fieldvalues[1])
                # print(str(y) + "  -  "+ str(len(idf_class    2)))
                if (y == len (idf_class2) - 1):
                    # print("RETORNO :" + str(idf_class1[x]))
                    # print(str(idf_class1[x]))
                    lista_aux.append (idf_class1[x].fieldvalues[1])
                    # print ("OBJETO DIFERENTES :" +idf_class1[x].fieldvalues[1] )
                    # print(idf_class1[x].fieldvalues[1])
                    y = 1000
                    # return(idf_class1[x])
                else:
                    y += 1
    return lista_aux


def clases_distintas_construcciones(idf_file1, idf_file2, nombreIDF):
    clasesdistintas = []
    diccionario_casos = {}
    diccionario_diff = {}
    diccionario_objeto = {}
    vector_diff = []
    listaauxobject = []
    objetos_cm = []
    objetosdelcaso = []

    clase = 'CONSTRUCTION'
    # print(nombreIDF)
    # RECORRE OBJETO DE LAS CLASE EN LISTA DISTINTA DEL CASO ALTERNATIVO.
    for objeto in range (0, len (idf_file2.idfobjects[clase])):  # CANTIDAD DE OBJETOS DE LA CLASE CASOS.
        cont = 0
        # MIENTRAS CONTADOR SEA MENOR A NUMERO TOTAL DE OBJETOS EN CASO MEJORADO.
        while (cont < len (idf_file1.idfobjects[clase])):
            a_aux = 0
            # RECORRE ATRIBUTOS DEL OBJETOS.
            while (a_aux < 2):
                # CONDICION SI EL NOMBRE DEL CAMPO ATRIBUTO ES IGUAL A NOMBRE ENTONCES.
                if (idf_file2.idfobjects[clase][objeto].fieldnames[a_aux] == 'Name'):
                    # COMPARA VALOR NOMBRE DEL OBJETOS EN LA CLASE ACTUAL EN LOS DISTINTOS ARCHIVOS.
                    existe = ((idf_file2.idfobjects[clase][objeto].fieldvalues[a_aux]).__eq__ (
                        idf_file1.idfobjects[clase][cont].fieldvalues[a_aux]))
                    # NOMBRE DE OBJETO EXISTE EN ARCHIVO DEL CASO MEJORADO
                    if (existe == True):
                        resultado = pos_atributo_construccion(idf_file2.idfobjects[clase][objeto],idf_file1.idfobjects[clase][cont])

                        if (resultado == 1):  # OBJETOS IGUALES TOTALMENTE.
                            listaauxobject.append (idf_file1.idfobjects[clase][cont])  # GUARDO OBJETO DE CASO MEJORADO
                            objetos_cm.append (idf_file1.idfobjects[clase][cont])
                            a_aux = 1000
                        else:  # OBJETO DISTINTO ENTRE ARCHIVOS IDF'S
                            for h in resultado.values():
                                if (len(h) > 0):
                                    vector_diff.append(resultado)
                            objetosdelcaso.append (idf_file1.idfobjects[clase])
                            listaauxobject.append (idf_file1.idfobjects[clase][cont])  # GUARDO OBJETO DE CASO MEJORADO
                            diccionario_objeto[idf_file2.idfobjects[clase][objeto].fieldvalues[a_aux]] = 'Hola'
                            a_aux = 5000
                    else:  # NO ES IGUAL EL NOMBRE DEL OBJETO A COMPRAR
                        if ((cont == len (idf_file1.idfobjects[clase]) - 1) and (
                                        idf_file1.idfobjects[clase][cont] in objetos_cm == False)):
                            a_aux = 1000
                        # #AVANZAR DE OBJETO.
                        else:
                            a_aux = 1000
                else:  # EL CAMPO DEL OBJETO NO ES NOMBRE, AUMENTO EN 1 PARA LLEGAR AL CAMPO 'Name' del OBJETO.
                    a_aux += 1
            cont += 1
    diccionario_diff[clase] = vector_diff
    # print (" ")
    return ((diccionario_diff))


def pos_atributo_construccion(obj1, obj2):
    diccionario = {}
    diccionario_idf1 = {}
    lista1 = []
    # CONDICION SI LOS OBJETOS TIENEN LA MISMA DIMENSION.
    if (len (obj1.fieldvalues) == len (obj2.fieldvalues)):
        atributo = 2
        # MIENTRAS NO LLEGUE AL ULTIMO ATRIBUTO DEL OBJETO.
        while (atributo < len (obj2.fieldvalues)):  # ITERAR EN ATRIBUTOS CON VALOR DEL OBJETO
            # ITERAR SOBRE LOS OBJETOS
            resultado = ((obj2.fieldvalues[atributo]).__eq__ (obj1.fieldvalues[atributo]))
            # EL ATRIBUTO ACTUAL ES IGUAL AL ALTRIBUTO DEL OBJETO EN EL CASO MEJORADO
            if (resultado == True):
                atributo += 1
            else:

                lista1.append (obj1.fieldvalues[atributo])
                atributo = 1000
            diccionario_idf1[obj1.fieldvalues[1]] = lista1

        # OBJETOS IGUALES
        if (atributo == len (obj2.fieldvalues)):
            return 1

    else:

        lista = []
        atributo2 = 2
        while (atributo2 < len (obj1.fieldvalues)):  # ITERAR EN ATRIBUTOS CON VALOR DEL OBJETO
            result = obj1.fieldvalues[atributo2] in obj2.fieldvalues
            if result == False:
                lista_idf1 = {}
                lista.append (obj1.fieldvalues[atributo2])
            atributo2 += 1
        diccionario_idf1[obj1.fieldvalues[1]] = lista
    # print(diccionario_idf1)
    return (diccionario_idf1)


def cargar_modificacion(request):
    if request.method == 'POST':
        form = ModificarIdfsForm (request.POST, request.FILES)
        if form.is_valid ():
            nueva_modificacion = form.save ()
            modificacion = get_object_or_404 (Modificar, pk=nueva_modificacion.pk)

            iddfile = '/usr/local/EnergyPlus-8-6-0/Energy+.idd'
            try:
                IDF.setiddname (iddfile)
            except modeleditor.IDDAlreadySetError as e:
                pass

            IDF.setiddname (iddfile)
            path_idf = str (modificacion.modificar_archivo_idf)
            idf_file = IDF ('media/' + path_idf)

            clase_material = idf_file.idfobjects['MATERIAL']
            material_nomass = 'MATERIAL_NOMASS'
            materials = 'MATERIAL'
            clase_material_nomass = idf_file.idfobjects['MATERIAL:NOMASS']
            return redirect ('/modificar/' + str (modificacion.modificar_id))
    else:
        form = ModificarIdfsForm ()
    return render (request, 'modificar_upload.html', locals (), {'form': form})


def modificar_objeto(request, args_id, args_class, args_name):
    modificacion = get_object_or_404 (Modificar, pk=args_id)

    materials = Material.objects.all ()

    iddfile = '/usr/local/EnergyPlus-8-6-0/Energy+.idd'
    try:
        IDF.setiddname (iddfile)
    except modeleditor.IDDAlreadySetError as e:
        pass
    IDF.setiddname (iddfile)
    path_idf1 = str (modificacion.modificar_archivo_idf)

    idf1 = IDF ('media/' + path_idf1)

    source = 'media/data_materiales1.xml'
    doc = etree.parse (source)
    raiz = doc.getroot ()

    if args_class == 'MATERIAL_NOMASS':

        materiales = doc.findall ("Material")
        diccionario_materiales = {}
        for m in materiales:
            diccionario_materiales[m.attrib['Id']] = m.attrib['Name']

        for objeto in idf1.idfobjects['MATERIAL:NOMASS']:
            if objeto.Name == args_name:

                atributos = objeto.fieldnames
                # print(atributos)
                valores = objeto.fieldvalues
                # print(valores)
                list = zip (atributos, valores)
                return render (request, 'editar_objeto.html',
                               {'list': list, 'objeto': objeto, 'args_name': args_name, 'args_class': args_class,
                                'args_id': args_id, 'materials': materials, 'diccionario_materiales' : diccionario_materiales})
            else:
                print ("NO EXISTE")
    else:

        windows_material = doc.findall ("WindowMaterialGlazing")
        diccionario_windows_material = {}
        for w in windows_material:
            diccionario_windows_material[w.attrib['Id']] = w.attrib['Name']

        if args_class == 'WINDOWMATERIAL_GLAZING':
            for objeto in idf1.idfobjects['WINDOWMATERIAL:GLAZING']:
                if objeto.Name == args_name:

                    atributos = objeto.fieldnames
                    # print(atributos)
                    valores = objeto.fieldvalues
                    # print(valores)
                    list = zip (atributos, valores)
                    return render (request, 'editar_objeto.html',
                                   {'list': list, 'objeto': objeto, 'args_name': args_name, 'args_class': args_class,
                                    'args_id': args_id, 'materials': materials, 'diccionario_windows_material' : diccionario_windows_material})
                else:
                    print ("NO EXISTE")

        else:

            windows_material_gas = doc.findall ("WindowMaterialGas")
            diccionario_windows_material_gas = {}
            for g in windows_material_gas:
                diccionario_windows_material_gas[g.attrib['Id']] = g.attrib['Name']

            if args_class == 'WINDOWMATERIAL_GAS':
                for objeto in idf1.idfobjects['WINDOWMATERIAL:GAS']:
                    if objeto.Name == args_name:

                        atributos = objeto.fieldnames
                        # print(atributos)
                        valores = objeto.fieldvalues
                        # print(valores)
                        list = zip (atributos, valores)
                        return render (request, 'editar_objeto.html',
                                       {'list': list, 'objeto': objeto, 'args_name': args_name,
                                        'args_class': args_class,
                                        'args_id': args_id, 'materials': materials,
                                        'diccionario_windows_material_gas': diccionario_windows_material_gas})
                    else:
                        print ("NO EXISTE")
            else:
                materiales = doc.findall ("Material")
                diccionario_materiales = {}
                for m in materiales:
                    diccionario_materiales[m.attrib['Id']] = m.attrib['Name']

                for objeto in idf1.idfobjects[args_class]:
                    if objeto.Name == args_name:

                        atributos = objeto.fieldnames
                        # print (atributos)
                        valores = objeto.fieldvalues
                        # print (valores)
                        list = zip (atributos, valores)
                        return render (request, 'editar_objeto.html',
                                       {'list': list, 'objeto': objeto, 'args_name': args_name, 'args_class': args_class,
                                        'args_id': args_id, 'materials': materials, 'diccionario_materiales' : diccionario_materiales})
                    else:
                        print ("NO EXISTE")


def modificar_submit(request, args_id, args_class, args_name, args_id2):
    llave = request.POST.get ('key')

    modificacion = get_object_or_404 (Modificar, pk=args_id)
    iddfile = '/usr/local/EnergyPlus-8-6-0/Energy+.idd'
    try:
        IDF.setiddname (iddfile)
    except modeleditor.IDDAlreadySetError as e:
        pass
    IDF.setiddname (iddfile)
    path_idf1 = str (modificacion.modificar_archivo_idf)
    # file_now =  codecs.EncodedFile('media/' + path_idf1, 'utf-8', errors='ignore')
    sourceFile = codecs.open ('media/' + path_idf1, "r", "ascii", "ignore")
    destino = open ('media/modificacion_idf/root.idf', "w")
    destino.write (sourceFile.read ().decode ('US-ASCII', 'ignore').encode ('utf-8'))
    idf_file = IDF ('media/modificacion_idf/root.idf')
    clase_material = idf_file.idfobjects['MATERIAL']
    material_ = 'MATERIAL'

    clase_material_nomass = idf_file.idfobjects['MATERIAL:NOMASS']
    material_nomass = 'MATERIAL_NOMASS'

    if (llave == 'Material'):
        material = request.POST
        key = material.get ('key')
        name = material.get ('name')
        Roughness = material.get ('Roughness')
        Thickness = material.get ('Thickness')
        Conductivity = material.get ('Conductivity')
        Density = material.get ('Density')
        Specific_Heat = material.get ('Specific_Heat')
        Thermal_Absorptance = material.get ('Thermal_Absorptance')
        Solar_Absorptance = material.get ('Solar_Absorptance')
        Visible_Absorptance = material.get ('Visible_Absorptance')

        for objeto in idf_file.idfobjects['MATERIAL']:
            if (objeto.Name == name):
                objeto.Name = name
                objeto.Roughness = Roughness
                objeto.Thickness = Thickness
                objeto.Conductivity = Conductivity
                objeto.Density = Density
                objeto.Specific_Heat = Specific_Heat
                objeto.Thermal_Absorptance = Thermal_Absorptance
                objeto.Solar_Absorptance = Solar_Absorptance
                objeto.Visible_Absorptance = Visible_Absorptance
        idf_file.saveas ('media/' + path_idf1, 'default', 'utf-8')

    else:
        if (llave == 'Material:NoMass'):
            material = request.POST
            key = material.get ('key')
            name = material.get ('name')
            Roughness = material.get ('Roughness')
            Thermal_Resistance = material.get ('Thermal_Resistance')
            Thermal_Absorptance = material.get ('Thermal_Absorptance')
            Solar_Absorptance = material.get ('Solar_Absorptance')
            Visible_Absorptance = material.get ('Visible_Absorptance')

            for objeto in idf_file.idfobjects['MATERIAL:NOMASS']:
                if (objeto.Name == name):
                    objeto.Name = name
                    objeto.Roughness = Roughness
                    objeto.Thermal_Resistance = Thermal_Resistance
                    objeto.Thermal_Absorptance = Thermal_Absorptance
                    objeto.Solar_Absorptance = Solar_Absorptance
                    objeto.Visible_Absorptance = Visible_Absorptance

            idf_file.saveas ('media/' + path_idf1, 'default', 'utf-8')

    return redirect ('/modificar/' + args_id)


def detalle_modificacion(request, args_id):
    materiales = Material.objects.all ()

    llave = request.POST.get ('key')
    modificacion = get_object_or_404 (Modificar, pk=args_id)
    iddfile = '/usr/local/EnergyPlus-8-6-0/Energy+.idd'
    try:
        IDF.setiddname (iddfile)
    except modeleditor.IDDAlreadySetError as e:
        pass
    IDF.setiddname (iddfile)
    path_idf1 = str (modificacion.modificar_archivo_idf)
    # file_now =  codecs.EncodedFile('media/' + path_idf1, 'utf-8', errors='ignore')
    sourceFile = codecs.open ('media/' + path_idf1, "r", "ascii", "ignore")
    destino = open ('media/modificacion_idf/root.idf', "w")
    destino.write (sourceFile.read ().decode ('US-ASCII', 'ignore').encode ('utf-8'))
    idf_file = IDF ('media/modificacion_idf/root.idf')

    clase_material = idf_file.idfobjects['MATERIAL']
    material_tag = 'MATERIAL'

    clase_material_nomass = idf_file.idfobjects['MATERIAL:NOMASS']
    material_nomass_tag = 'MATERIAL_NOMASS'

    clase_windows_glazing = idf_file.idfobjects['WINDOWMATERIAL:GLAZING']
    windowsmaterial_glazing_tag = 'WINDOWMATERIAL_GLAZING'

    clase_windows_gas = idf_file.idfobjects['WINDOWMATERIAL:GAS']
    windowsmaterial_gas_tag = 'WINDOWMATERIAL_GAS'




    source = 'media/data_materiales1.xml'
    doc = etree.parse (source)
    raiz = doc.getroot ()
    materiales = doc.findall ("Material")
    diccionario_materiales = {}
    for m in materiales:
        diccionario_materiales[m.attrib['Id']] = m.attrib['Name']


    windows_material = doc.findall ("WindowMaterialGlazing")
    diccionario_windows_material = {}
    for w in windows_material:
        diccionario_windows_material[w.attrib['Id']] = w.attrib['Name']


    windows_material_gas = doc.findall ("WindowMaterialGas")
    diccionario_windows_material_gas = {}
    for g in windows_material_gas:
        diccionario_windows_material_gas[g.attrib['Id']] = g.attrib['Name']

    return render(request, 'test.html', {'args_id': args_id, 'modificacion': modificacion, 'hola': llave,
                                              'clase_material': clase_material,
                                              'clase_material_nomass': clase_material_nomass,
                                              'material_nomass_tag': material_nomass_tag, 'material_tag': material_tag,
                                              'materiales': materiales, 'diccionario_materiales':  diccionario_materiales,
                                             'clase_windows_glazing': clase_windows_glazing, 'windowsmaterial_glazing_tag':windowsmaterial_glazing_tag,
                                             'diccionario_windows_material':diccionario_windows_material, 'clase_windows_gas' : clase_windows_gas,
                                             'windowsmaterial_gas_tag' : windowsmaterial_gas_tag,
                                            'diccionario_windows_material_gas' : diccionario_windows_material_gas})


def ver_modificaciones(request):
    lista_modificaciones = Modificar.objects.all ()
    context = {'lista_modificaciones': lista_modificaciones}
    return render (request, 'ver_modificaciones.html', context)


def crear_materials(request):
    if request.method == 'POST':
        form = MaterialForm (request.POST, request.FILES)
        if form.is_valid ():
            nuevo_materials = form.save ()
            materials = get_object_or_404 (Material, pk=nuevo_materials.pk)
            lista_materials = Material.objects.all ()
            context = {'lista_materials': lista_materials}
            message = "Material agregado satisfactoriamente !"
            return render (request, 'ver_materiales.html', {'message': message})
    else:
        form = MaterialForm ()
    return render (request, 'crear_materials.html', locals (), {'form': form})


def ver_materials(request):
    lista_materials = Material.objects.all ()
    context = {'lista_materials': lista_materials}
    return render (request, 'ver_materiales.html', context)


def request_combinar(request):
    lista = []
    if request.method == 'POST':
        print(request)
        aa = request.POST.getlist('alternativa')
        for i in aa:
            lista.append (str (i))
        #     print (i)
        # print(lista)
        id_combinacion = combinar(lista)
        print(id_combinacion)

        detalle_combinacion = get_object_or_404 (Combinar, pk=id_combinacion)
        ruta_output = []
        # print(detalle_combinacion.combinar_alternativas)
        # for m in detalle_combinacion.combinar_alternativas:
        # print ("".join ([x for x in detalle_combinacion.combinar_alternativas if x.isdigit ()]))
        ruta_output.append ("_".join ([x for x in detalle_combinacion.combinar_alternativas if x.isdigit ()]))
        # print(ruta_output)
        for m in ruta_output:
            print (m)
        path_archivo_combinacion = ('media/combinar/combinacion/combinacion_' + str (m) + '/Output/')
        for reporte in os.listdir (path_archivo_combinacion):
            if reporte.endswith ("html"):
                # print (reporte)
                # html_data =  codecs.open (str(path_archivo_simulacion+file),"r", encoding='utf-8', errors='ignore').read()
                html_data = codecs.open (str (path_archivo_combinacion + reporte), "r", encoding='utf-8',
                                         errors='ignore').read ()

                # context = {'some_key': 'some_value'}
                content = (path_archivo_combinacion + reporte)
                # print (content)
        return render (request, 'reporte_combinacion.html', {'f': html_data, 'path': content})





        # return render (request, 'reporte_combinacion.html', {'lista': lista})
    else:
        return render (request, 'combinar.html', locals ())


def combinar(lista_alternativas):
    combinar = Combinar(combinar_alternativas=str(lista_alternativas))
    combinar.save ()
    pathnameto_eppy = "/usr/lib/python3.5/site-packages/eppy/"
    os.path.dirname (pathnameto_eppy)
    mejorado = 'media/combinar/Idf_caso_mejorado_remodelado/caso_mejorado_agosto.idf'
    casobase = 'media/combinar/Idf_caso_inicial_remodelado/caso_base_agosto.idf'
    casoalternativa = 'media/combinar//Idf_alternativas_remodelado/alternativa1.idf'
    pathAlterCases = 'media/combinar/Idf_alternativas_remodelado/'
    directorioMotor = os.path.dirname (os.path.dirname (os.path.abspath (__file__)))
    iddfile = '/usr/local/EnergyPlus-8-6-0/Energy+.idd'
    try:
        IDF.setiddname (iddfile)
    except modeleditor.IDDAlreadySetError as e:
        pass
    IDF.setiddname (iddfile)
    idf_mejorado = modeleditor.IDF (mejorado)
    idf_inicial = modeleditor.IDF (casobase)
    list_file_idf = []
    list_class_diff = []
    dtls = idf_mejorado.model.dtls  # todas las clases del fichero idf
    dt = idf_mejorado.model.dt  # modelo idf
    idd_info = idf_mejorado.idd_info  # todos los datos idd / estructura con objetos
    diccionario_alternativas = {}
    # Recorre arhivo idf en directorio con los casos idf
    for root in os.listdir (pathAlterCases):
        # Condicion si el archivo empieza con nombre "alternativa"
        if root.startswith ("alternativa"):
            # Se guarda nombre en una lista
            list_file_idf.append (root)
            # Toma el archivo del directorio y instancia como IDF
            idf_alternativa = modeleditor.IDF (pathAlterCases + root)
            print (" ")
            # Condicion si el archivo mejorado tiene los mismos items que el archivo alternativo
            if (idf_inicial.idfobjects.items ().__eq__ (idf_alternativa.idfobjects.items ()) == True):
                # acá seria alternativa5 == alternativa5, por ejemplo.
                print ("ES IGUAL")
            else:
                # Crea e instancia
                resultado_alternativa = diferencias_idf (idf_inicial, idf_alternativa, root)
                diccionario_alternativas[root] = resultado_alternativa
    print (" ")
    combinacion (diccionario_alternativas, casobase, lista_alternativas)


    return combinar.pk


def combinacion(diccionario_diferencias, idf_base, lista_alternativas):
    ruta_alternativas = 'media/combinar/Idf_alternativas_remodelado/'
    contador_de_combinaciones = 1
    lista_repetidos = []
    ruta_simulacion = []

    nueva_carpeta = []
    pathbase = 'media/combinar/combinacion/'
    pathAlterCases = 'media/combinar/Idf_alternativas_remodelado/'
    tag = "combinacion"
    tag_folder = "combinacion"
    tag_combinacion = []
    clima_simulacion = 'media/combinar/clima_simular/Concepcion.epw'

    for f in range (0, len (lista_alternativas)):
        tag_folder = tag_folder + "_" + str (lista_alternativas[f])
        if (f == len (lista_alternativas) - 1):
            print (" SE CREO CARPETA DE COMBINACION :" + str (tag_folder))
            path = "media/combinar/combinacion/" + str (tag_folder)
            tag_combinacion = path
            if not os.path.exists (path): os.makedirs (path)
            sourceFile = codecs.open (idf_base, "r", "ascii", "ignore")
            destino = open ('media/modificacion_idf/caso.idf', "w")
            destino.write (sourceFile.read ().decode ('US-ASCII', 'ignore').encode ('utf-8'))
            caso_nuevo = IDF ('media/modificacion_idf/root.idf')
            # caso_nuevo = IDF ()
            # caso_nuevo = deepcopy (idf_base)
            caso_nuevo.save (path + "/" + tag_folder + '.idf', 'r', 'UTF-8')

    for a in range (0, len (lista_alternativas)):
        pathbase = 'media/combinar/combinacion/'

        tag = tag + "_" + str (lista_alternativas[a])
        # '/media/combinar/combinacion/' +
        # print (tag)
        ruta_caso_nuevo = tag_combinacion + "/" + tag_folder + '.idf'
        ruta_simulacion.append (ruta_caso_nuevo)
        # print (ruta_simulacion[0])
        idf_hibrido = IDF (ruta_caso_nuevo)
        idf_alternativa = IDF (pathAlterCases + "alternativa" + str (lista_alternativas[a]) + ".idf")
        resultado_alternativa = aislar_alternativa (diccionario_diferencias, lista_alternativas[a])
        root = "alternativa"
        for clase in idf_alternativa.model.dtls:
            for llave, valor in zip (resultado_alternativa.keys (), resultado_alternativa.values ()):
                # PREGUNTA SI LA CLASE DEL IDF ALTERNATIVA ES IGUAL A LA LLAVE DEL DICCIONARIO DE DIFERENCIAS
                if llave == clase:
                    for objeto in idf_alternativa.idfobjects[clase]:
                        for v in valor:
                            # COMPARA EL NOMBRE DEL OBJETO EN EL DICCIONARIO CON LA EXISTENCIA EN EL MODELO.
                            # LO HACE PARA RECUPERAR EL OBJETO COMPLETO Y TRANSFERIRLO AL NUEVO IDF.
                            if (objeto.Name == v):
                                resultado = objeto_en_lista (objeto, clase, idf_hibrido, idf_alternativa)
                                # PREGUNTA SI EL OBJETO DEL DICCIONARIO ESTA EN EL MODELO
                                if resultado == 0:
                                    print (True)
                                    print (" EL OBJETO ESTA")
                                else:
                                    if resultado == 1:
                                        idf_hibrido.newidfobject (clase)
                                        for atributo in range (1,
                                                               len (idf_alternativa.idfobjects[clase][-1].fieldvalues)):
                                            attr = idf_hibrido.idfobjects[clase][-1].fieldnames[atributo]
                                            # GENERA NUEVO OBJETO COMPLETO EN EL BASE
                                            idf_hibrido.idfobjects[clase][-1][attr] = objeto.fieldvalues[atributo]
        for i in range (0, len (idf_hibrido.idfobjects['CONSTRUCTION'])):
            idf_hibrido.idfobjects['CONSTRUCTION'].pop (-1)
        for c in idf_alternativa.idfobjects['CONSTRUCTION']:
            idf_hibrido.newidfobject ('CONSTRUCTION')
            for m in range (1, len (c.fieldvalues)):
                atrib = c.fieldnames[m]
                idf_hibrido.idfobjects['CONSTRUCTION'][-1][atrib] = c.fieldvalues[m]
        idf_hibrido.save (encoding='utf8')
        nueva_carpeta = pathbase + tag + "/"
        # print (nueva_carpeta)
    p = Popen (
        ['/usr/local/EnergyPlus-8-6-0/runenergyplus', ruta_simulacion[0], 'Concepcion', '-d', nueva_carpeta, '-p',
         str (tag_folder)]).wait ()
    # p = Popen (['/usr/local/EnergyPlus-8-6-0/runenergyplus', ruta_simulacion, 'Concepcion', '-d', nueva_carpeta, '-p',str (args)]).wait ()


def limites_alternativas(lista_de_alternativas, ruta_de_alternativas):
    lista_fuera_de_limites = []
    cont = 0
    for root in os.listdir (ruta_de_alternativas):
        if root.startswith ("alternativa"):
            cont += 1
    for i in lista_de_alternativas:
        if (i < 1) or (i > cont):
            lista_fuera_de_limites.append (i)
    return lista_fuera_de_limites


def aislar_alternativa(diccionario, alternativa):
    for nombre_alternativa, valor_alternativa in zip (diccionario.keys (), diccionario.values ()):
        if nombre_alternativa == "alternativa" + str (alternativa) + ".idf":
            return (valor_alternativa)


def objeto_en_lista(objeto, clase, idf_hibrido, idf_alternativo):
    n = 0
    while n < len (idf_hibrido.idfobjects[clase]):
        for obj in idf_hibrido.idfobjects[clase]:
            if objeto.Name == obj.Name:
                n = 1000
            else:
                n += 1
    if (n == len (idf_hibrido.idfobjects[clase])):
        # objeto no esta y hay que agregarlo
        return 1
    else:
        if n == 1000:
            # objeto ya esta en la lista de la clase
            return 0


def combinar_submit(request):
    lista_checkbox = request.POST.getlist ('alternativa')
    return render (request, 'combinar_submit.html', {'lista_checkbox': lista_checkbox})


def ver_combinaciones(request):
    lista_combinaciones = Combinar.objects.all ()
    context = {'lista_combinaciones': lista_combinaciones}
    return render (request, 'ver_combinaciones.html', context)


def ver_combinacion(request, args_id):
    detalle_combinacion = get_object_or_404 (Combinar, pk=args_id)
    ruta_output = []
    # print(detalle_combinacion.combinar_alternativas)
    # for m in detalle_combinacion.combinar_alternativas:
    # print ("".join ([x for x in detalle_combinacion.combinar_alternativas if x.isdigit ()]))
    ruta_output.append ("_".join ([x for x in detalle_combinacion.combinar_alternativas if x.isdigit ()]))
    # print(ruta_output)
    for m in ruta_output:
        print(m)
    path_archivo_combinacion = ('media/combinar/combinacion/combinacion_' + str (m) + '/Output/')
    for reporte in os.listdir (path_archivo_combinacion):
        if reporte.endswith ("html"):
            # print (reporte)
            # html_data =  codecs.open (str(path_archivo_simulacion+file),"r", encoding='utf-8', errors='ignore').read()
            html_data = codecs.open (str (path_archivo_combinacion + reporte), "r", encoding='utf-8',
                                     errors='ignore').read ()

            # context = {'some_key': 'some_value'}
            content = (path_archivo_combinacion + reporte)
            # print (content)
    return render (request, 'reporte_combinacion.html', {'f': html_data, 'path': content})


def xsendfile(request, path):

    if path.startswith("modificacion_idf/"):
        # print(path)
        tag = path.split("/")
        # print(tag[1])
        data = open ('media/' + path, 'rb')
        bdata = data.read ()
        response = HttpResponse ()
        response['Content-Type'] = 'text/plain'
        response.write (bdata)
        response['Content-Disposition'] = "attachment;  filename=" + tag[1]
        response['X-Sendfile'] = smart_str(tag[1])
        return response
    else:

        string = "_".join ([x for x in path if x.isdigit ()])
        string1 = "_" + string
        # print(string1)
        data = open ('media/combinar/combinacion/combinacion' + string1 +'/combinacion'+string1+'.idf', 'rb')
        bdata = data.read ()
        response = HttpResponse ()
        response['Content-Type'] = 'text/plain'
        response.write (bdata)
        response['Content-Disposition'] = "attachment;  filename=" + "combinacion"+string1+'.idf'
        response['X-Sendfile'] = smart_str ("combinacion"+string1+'.idf')
        return response




def leer_xml(request):
    source = 'media/data_materiales1.xml'
    from lxml import etree

    doc = etree.parse(source)
    raiz = doc.getroot()


    # materiales = raiz[0].tag
    materiales = doc.findall("Material")
    diccionario_materiales = {}

    for m in materiales:
        diccionario_materiales[m.attrib['Id']] = m.attrib['Name']
        # for y in m:
        #    print(y)



    return render (request, 'leer_xml.html', {'doc': diccionario_materiales})
