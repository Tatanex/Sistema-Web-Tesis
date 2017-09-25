# -*- coding: utf-8 -*-
import codecs
import os
import shutil
# Create your views here.
from subprocess import Popen

from django.core.files.base import File
from django.shortcuts import render, get_object_or_404
from eppy import modeleditor
from eppy.modeleditor import IDF

from .models import Simular, Comparar


def indexView(request):
    return render (request, 'layout.html')


def simularView(request, simulacion_id):
    simulacion = get_object_or_404 (Simular, pk=simulacion_id)
    return render (request, 'simular.html', {'simulacion': simulacion})


# HTTP Error 400
def error_404View(request):
    return render (request, 'page_404.html')


from .forms import CargarArchivosForm, CompararIdfsForm


def cargar_archivo_simulacion_view(request):
    if request.method == 'POST':
        form = CargarArchivosForm (request.POST, request.FILES)
        if form.is_valid ():
            nueva_simulacion = form.save ()
            simulacion = get_object_or_404 (Simular, pk=nueva_simulacion.pk)
            # message = "Archivos cargados satisfactoriamente !"
            return render (request, 'simular.html', {'simulacion': simulacion})
    else:
        form = CargarArchivosForm ()
    return render (request, 'upload.html', locals (), {'form': form})

def submit(request, args):
    if request.method == 'POST':
        WeatherData = '/usr/local/EnergyPlus-8-6-0/WeatherData/'
        simulation = get_object_or_404 (Simular, pk=args)
        b = str (simulation.simular_clima)
        # shutil.move ("media/"+b, WeatherData )
        climapalabra = b.split ("/")
        print (climapalabra)
        clima = climapalabra[1]
        if os.path.isfile ('/usr/local/EnergyPlus-8-6-0/WeatherData/' + clima) == True:
            clima_oficial = WeatherData + clima
        else:
            shutil.copy ('media/' + b, '/usr/local/EnergyPlus-8-6-0/WeatherData/')

            clima_oficial = WeatherData + clima

        a = 'media/' + str (simulation.simular_archivo_idf)
        nueva_carpeta = 'simulaciones/simulacion_' + str (args)
        print (nueva_carpeta)
        if not os.path.exists (nueva_carpeta): os.makedirs (nueva_carpeta)
        p = Popen (['/usr/local/EnergyPlus-8-6-0/runenergyplus', a, clima_oficial, '-d', nueva_carpeta, '-p',
                    str (args)]).wait ()

        shutil.move ("media/idf/Output", "simulaciones/simulacion_" + str (args))
    return render (request, 'simulando.html')


def ver_simulaciones(request):
    lista_simular = Simular.objects.all()
    # for x in lista_simular:
    #     print(x)
    context = {'lista_simular': lista_simular}
    return render (request, 'ver_simulacion.html', context)

def ver(request, args):
    print(args)
    path_archivo_simulacion = ('simulaciones/simulacion_'+str(args)+'/Output/')
    for file in os.listdir(path_archivo_simulacion):
        if file.endswith(".html"):
            print(file)
    # html_data =  codecs.open (str(path_archivo_simulacion+file),"r", encoding='utf-8', errors='ignore').read()
    html_data =  codecs.open (str(path_archivo_simulacion+file),"r", encoding='utf-8', errors='ignore').read()
    f = File(html_data)
    # context = {'some_key': 'some_value'}
    # content = render_to_string (path_archivo_simulacion + file)
    return render (request, 'simulando.html', {'f' : html_data } )


def compararidf(request):
    # from tesisubb.utils.diferencias_idf import Diferencias_idf

    if request.method == 'POST':
        form = CompararIdfsForm (request.POST, request.FILES)
        if form.is_valid ():
            nueva_comparacion = form.save()
            comparacion = get_object_or_404(Comparar, pk=nueva_comparacion.pk)
            iddfile = '/usr/local/EnergyPlus-8-6-0/Energy+.idd'
            try:
                IDF.setiddname (iddfile)
            except modeleditor.IDDAlreadySetError as e:
                pass

            IDF.setiddname(iddfile)

            path_idf1=str(comparacion.comparar_archivo_idf1)

            path_idf2=str(comparacion.comparar_archivo_idf2)

            idf1 = IDF('media/'+path_idf1)
            # print(comparacion.comparar_archivo_idf2)
            idf2 = IDF('media/'+path_idf2)

            # condicion si el archivo mejorado tiene los mismos items que el archivo alternativo
            if (idf1.idfobjects.items ().__eq__ (idf2.idfobjects.items ()) == True):
                print ("ES IGUAL")  # acá seria alternativa5 == alternativa5, por ejemplo.
            else:
                print ("NO ES IGUAL " + idf2.idfname)  # imprime ruta archivo idf (root)
                # Crea e instancia
                resultado_alternativa = diferencias_idf(idf1, idf2, idf2.idfname)
                print(resultado_alternativa)
                # k = (resultado_alternativa.keys())
                # v =(resultado_alternativa.values())
            message = "Archivos cargados satisfactoriamente !"
            return render(request, 'diferencia_comparacion.html', {'resultado_alternativa' : resultado_alternativa, 'message': message, 'id_comparacion' :  nueva_comparacion.pk})
        # {'k': k, 'v': v, 'message': message}
    else:
        form = CompararIdfsForm ()
    return render(request, 'comparar.html', locals (), {'form': form})



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

        c = 1
        # Recorre diferencias de clases en archivos.
        for clase in clasesdistintas:
            listaauxobject = []
            objetos_cm = []
            objetosdelcaso = []
            numeroobjetos = 0
            lista_auxiliares = []
            if (clase == 'MATERIAL'or
                clase == 'MATERIAL:NOMASS' or
                clase == 'WINDOWMATERIAL:GLAZING' or
                clase == 'WINDOWMATERIAL:GAS'or
                clase == 'BUILDINGSURFACE:DETAILED'):
                lista_auxiliares = []
                # Recorre objeto de las clases en lista distinta del caso alternativa.
                for objeto in range (0, len(idf_file2.idfobjects[clase])):  # Cantidad de objetos de la clase.
                    cont = 0
                    if(len(idf_file1.idfobjects[clase]) == 0 ):
                        lista_auxiliares.append (idf_file2.idfobjects[clase][objeto].fieldvalues[1])
                        diccionario_aux[str (clase)] = lista_auxiliares
                        cont += 1
                    else:
                        while (cont < len(idf_file1.idfobjects[clase])):
                               #Condición si el nombre del campo atributo es igual a nombre entonces.
                              if (idf_file2.idfobjects[clase][objeto].fieldnames[1] == 'Name'):
                                  # Compara valor nombre del objeto en la clase actual en los distintos archivos.
                                  existe = ((idf_file2.idfobjects[clase][objeto].fieldvalues[1]).__eq__ (idf_file1.idfobjects[clase][cont].fieldvalues[1]))
                                  # Nombre de objeto existe en archivo del caso inicial.
                                  if (existe == True):
                                      # dif_a = DiferenciaAtributos ()  # instancia objeto de la clase DiferenciaAtributos()
                                      resultado = pos_atributo (idf_file2.idfobjects[clase][objeto],idf_file1.idfobjects[clase][cont])
                                      # Objetos totalmente iguales.
                                      if (resultado == 1):
                                          # Almacena objeto de caso mejorado.
                                          listaauxobject.append (idf_file1.idfobjects[clase][cont])
                                          objetos_cm.append (idf_file1.idfobjects[clase][cont])
                                          cont = 5000
                                      cont=5000
                                  # No es igual el nombre del objeto a comparar.
                                  else:
                                      if (cont == len(idf_file1.idfobjects[clase])-1):
                                          lista_auxiliares.append(idf_file2.idfobjects[clase][objeto].fieldvalues[1])
                                          diccionario_aux[str(clase)] = lista_auxiliares
                                      cont+=1
                c+=1
        return(diccionario_aux)


def pos_atributo(obj1,obj2):
        # Condición si los objetos tienen la misma dimensión.
        if(len(obj1.fieldvalues) == len(obj2.fieldvalues)):
            atributo = 2
            # Mientras no llegue al ultimo atributo del objeto, iterar.
            while (atributo < len(obj2.fieldvalues)):
                # Iterar sobre los objetos.
                resultado = ((obj2.fieldvalues[atributo]).__eq__ (obj1.fieldvalues[atributo]))
                # El atributo actual es igual al atributo del objeto en el caso a comparar.
                if (resultado == True):
                    atributo+=1
                # El atributo actual es distinto al atributo del objeto en el caso a comparar.
                else:
                    atributo=1000
            if( atributo == len(obj2.fieldvalues)):
                return 1
            else:
                return 0
        else:
            return 0

def ver_objeto(request, args_id, args_class, args_name):

    print(args_id)
    print(args_class)
    print (args_name)

    comparacion = get_object_or_404 (Comparar, pk=args_id)
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

    for objeto in idf2.idfobjects[args_class]:
        if objeto.Name == args_name:

           atributos = objeto.fieldnames
           print(atributos)
           valores =    objeto.fieldvalues
           print(valores)

           list = zip (atributos, valores)

           return render (request, 'ver_objeto.html', {'list': list, 'objeto': objeto, 'args_name' : args_name, 'args_class' :  args_class})

        else:
            print("NO EXISTE")




    # return render (request, 'ver_objeto.html', {'args1': args1, 'args2': args2  })



def ver_comparaciones(request):
    lista_comparaciones = Comparar.objects.all()
    # for x in lista_simular:
    #     print(x)
    context = {'lista_comparaciones': lista_comparaciones}
    return render (request, 'ver_comparaciones.html', context)






def diferencia_comparacion(request, args_id ):

    comparacion = get_object_or_404 (Comparar, pk=args_id)
    iddfile = '/usr/local/EnergyPlus-8-6-0/Energy+.idd'
    try:
        IDF.setiddname (iddfile)
    except modeleditor.IDDAlreadySetError as e:
        pass

    IDF.setiddname (iddfile)

    path_idf1 = str (comparacion.comparar_archivo_idf1)
    print(path_idf1)
    path_idf2 = str (comparacion.comparar_archivo_idf2)
    print (path_idf2)
    idf1 = IDF ('media/' + path_idf1)
    # print(comparacion.comparar_archivo_idf2)
    idf2 = IDF ('media/' + path_idf2)
    # condicion si el archivo mejorado tiene los mismos items que el archivo alternativo

    if (idf1.idfobjects.items ().__eq__ (idf2.idfobjects.items ()) == True):
        print ("ES IGUAL")  # acá seria alternativa5 == alternativa5, por ejemplo.
    else:
        print ("NO ES IGUAL " + idf2.idfname)  # imprime ruta archivo idf (root)
        # Crea e instancia
        resultado_alternativa = diferencias_idf (idf1, idf2, idf2.idfname)
        print (resultado_alternativa)
        # k = (resultado_alternativa.keys())
        # v =(resultado_alternativa.values())
    message = "Archivos cargados satisfactoriamente !"
    return render (request, 'diferencia_comparacion.html',
                   {'resultado_alternativa': resultado_alternativa, 'message': message,
                    'id_comparacion': args_id})


def modificar(request):


    return render (request, 'modificar.html')

