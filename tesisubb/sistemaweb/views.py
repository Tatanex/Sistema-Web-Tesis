# -*- coding: utf-8 -*-
import codecs
import os
import shutil
# Create your views here.
from subprocess import Popen

from django.core.files.base import File
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from eppy import modeleditor
from eppy.modeleditor import IDF

from .models import Simular, Comparar, Modificar, Materials


def indexView(request):

    simulacion = Simular.objects.all ()
    cantidad_simulacion  = len(simulacion)

    modificacion = Modificar.objects.all ()
    cantidad_modificacion = len (modificacion)

    comparacion = Comparar.objects.all ()
    cantidad_comparacion = len (comparacion)




    return render (request, 'layout.html', {'simulacion' : cantidad_simulacion, 'modificacion' : cantidad_modificacion,
                                            'comparacion' : cantidad_comparacion} )


def simularView(request, simulacion_id):
    simulacion = get_object_or_404 (Simular, pk=simulacion_id)
    return render (request, 'simular.html', {'simulacion': simulacion})


# HTTP Error 400
def error_404View(request):
    return render (request, 'page_404.html')


from .forms import CargarArchivosForm, CompararIdfsForm, ModificarIdfsForm, MaterialsForm


def cargar_archivo_simulacion_view(request):
    if request.method == 'POST':
        form = CargarArchivosForm (request.POST, request.FILES)
        if form.is_valid ():
            nueva_simulacion = form.save ()
            simulacion = get_object_or_404 (Simular, pk=nueva_simulacion.pk)
            message = "Archivos cargados satisfactoriamente !"
            return render (request, 'simular.html', {'simulacion': simulacion, 'message' : message})
    else:
        form = CargarArchivosForm ()
    return render (request, 'upload.html', locals (), {'form': form})


def submit(request, args):
    if request.method == 'POST':
        WeatherData = '/usr/local/EnergyPlus-8-6-0/WeatherData/'
        iddfile = '/usr/local/EnergyPlus-8-6-0/Energy+.idd'
        try:
            IDF.setiddname (iddfile)
        except modeleditor.IDDAlreadySetError as e:
            pass

        IDF.setiddname(iddfile)
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
        p = Popen (['/usr/local/EnergyPlus-8-6-0/runenergyplus', a, 'Concepcion', '-d', nueva_carpeta, '-p',
                    str (args)]).wait ()

        shutil.move ("media/idf/Output", "simulaciones/simulacion_" + str (args))

        path_archivo_simulacion = ('simulaciones/simulacion_' + str (args) + '/Output/')
        for file in os.listdir (path_archivo_simulacion):
            if file.endswith (".html"):
                print (file)
        html_data = codecs.open(str (path_archivo_simulacion + file), "r", encoding='utf-8',
                                       errors='ignore').read ()
        f = File(html_data)

    return render (request, 'simulando.html', {'f': html_data, 'path': path_archivo_simulacion})


def ver_simulaciones(request):
    lista_simular = Simular.objects.all ()
    # for x in lista_simular:
    #     print(x)
    context = {'lista_simular': lista_simular}
    return render (request, 'ver_simulacion.html', context)


def ver(request, args):
    print (args)
    path_archivo_simulacion = ('simulaciones/simulacion_' + str(args) + '/Output/')
    for reporte in os.listdir(path_archivo_simulacion):
        if reporte.endswith("html"):
            print(reporte)
    # html_data =  codecs.open (str(path_archivo_simulacion+file),"r", encoding='utf-8', errors='ignore').read()
            html_data = codecs.open(str(path_archivo_simulacion + reporte), "r", encoding='utf-8', errors='ignore').read ()



    # context = {'some_key': 'some_value'}
            content = (path_archivo_simulacion + reporte)
            print(content)
    return render (request, 'simulando.html', {'f': html_data, 'path': content})


def compararidf(request):
    # from tesisubb.utils.diferencias_idf import Diferencias_idf

    if request.method == 'POST':
        form = CompararIdfsForm (request.POST, request.FILES)
        if form.is_valid ():
            nueva_comparacion = form.save ()
            comparacion = get_object_or_404 (Comparar, pk=nueva_comparacion.pk)
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

            # condicion si el archivo mejorado tiene los mismos items que el archivo alternativo
            if (idf1.idfobjects.items ().__eq__ (idf2.idfobjects.items ()) == True):
                print ("ES IGUAL")  # acá seria alternativa5 == alternativa5, por ejemplo.
            else:
                print ("NO ES IGUAL " + idf2.idfname)  # imprime ruta archivo idf (root)
                # Crea e instancia
                resultado_alternativa = diferencias_idf(idf1, idf2, idf2.idfname)
                print (resultado_alternativa)
                # k = (resultado_alternativa.keys())
                # v =(resultado_alternativa.values())
            message = "Archivos cargados satisfactoriamente !"
            return render (request, 'diferencia_comparacion.html',
                           {'resultado_alternativa': resultado_alternativa, 'message': message,
                            'id_comparacion': nueva_comparacion.pk})
            # {'k': k, 'v': v, 'message': message}
    else:
        form = CompararIdfsForm ()
    return render (request, 'comparar.html', locals (), {'form': form})

def ver_comparaciones(request):
    lista_comparaciones = Comparar.objects.all ()
    # for x in lista_simular:
    #     print(x)
    context = {'lista_comparaciones': lista_comparaciones}
    return render (request, 'ver_comparaciones.html', context)


def detalle_comparacion(request, args_id):

    print(args_id)
    comparacion = get_object_or_404(Comparar, pk=args_id)
    iddfile = '/usr/local/EnergyPlus-8-6-0/Energy+.idd'
    try:
        IDF.setiddname (iddfile)
    except modeleditor.IDDAlreadySetError as e:
        pass

    IDF.setiddname (iddfile)
    path_idf1 = str (comparacion.comparar_archivo_idf1)
    print (path_idf1)
    path_idf2 = str (comparacion.comparar_archivo_idf2)
    print (path_idf2)
    idf1 = IDF ('media/' + path_idf1)
    # print(comparacion.comparar_archivo_idf2)
    idf2 = IDF ('media/' + path_idf2)
    # condicion si el archivo mejorado tiene los mismos items que el archivo alternativo
    if (idf1.idfobjects.items ().__eq__ (idf2.idfobjects.items ()) == True):
        message = "Los archivos son iguales, no existe diferencias.!"
        form = CompararIdfsForm ()
        return render(request, 'comparar.html', locals (), {'form': form})

    else:
        print ("NO ES IGUAL " + idf2.idfname)  # imprime ruta archivo idf (root)
        # Crea e instancia
        resultado_alternativa1 = diferencias_idf(idf1, idf2, idf2.idfname)
        # print (resultado_alternativa)
        # k = (resultado_alternativa.keys())
        # v =(resultado_alternativa.values())
    return render(request, 'diferencia_comparacion.html', {'resultado_alternativa1': resultado_alternativa1,'id_comparacion': args_id})




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
        if (clase == 'MATERIAL' or
                    clase == 'MATERIAL:NOMASS' or
                    clase == 'WINDOWMATERIAL:GLAZING' or
                    clase == 'WINDOWMATERIAL:GAS' or
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


def ver_objeto(request, args_id, args_class, args_name):
    print (args_id)
    print (args_class)
    print (args_name)
    comparacion = get_object_or_404 (Comparar, pk=args_id)
    materials = Materials.objects.all()
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
            print (atributos)
            valores = objeto.fieldvalues
            print (valores)
            list = zip (atributos, valores)
            return render (request, 'ver_objeto.html',
                           {'list': list, 'objeto': objeto, 'args_name': args_name, 'args_class': args_class, 'materials' : materials})
        else:
            print ("NO EXISTE")

            # return render (request, 'ver_objeto.html', {'args1': args1, 'args2': args2  })

def cargar_modificacion(request):
    if request.method == 'POST':
        form = ModificarIdfsForm (request.POST, request.FILES)
        if form.is_valid ():
            nueva_modificacion = form.save ()
            modificacion = get_object_or_404 (Modificar, pk=nueva_modificacion.pk)
            # message = "Archivos cargados satisfactoriamente !"

            print (modificacion.modificar_archivo_idf)

            iddfile = '/usr/local/EnergyPlus-8-6-0/Energy+.idd'
            try:
                IDF.setiddname (iddfile)
            except modeleditor.IDDAlreadySetError as e:
                pass

            IDF.setiddname (iddfile)
            path_idf = str (modificacion.modificar_archivo_idf)
            # print (path_idf)
            idf_file = IDF ('media/' + path_idf)

            clase_material = idf_file.idfobjects['MATERIAL']
            # print(clase_material)
            # if idf_file.idfobjects['MATERIAL'] == 'MATERIAL:NOMASS':
            #     material_nomass = 'MATERIAL:NOMASS'
            material_nomass = 'MATERIAL_NOMASS'
            materials = 'MATERIAL'
            clase_material_nomass = idf_file.idfobjects['MATERIAL:NOMASS']
            # print(clase_material)
            return render (request, 'modificar.html', {'modificacion': modificacion, 'clase_material': clase_material,
                                                       'clase_material_nomass': clase_material_nomass,
                                                       'material_nomass': material_nomass, 'materials': materials})
    else:
        form = ModificarIdfsForm ()
    return render (request, 'modificar_upload.html', locals (), {'form': form})


def modificar_objeto(request, args_id, args_class, args_name):
    print (args_id)
    # print(args_class)
    # print (args_name)
    modificacion = get_object_or_404(Modificar, pk=args_id)

    materials = Materials.objects.all()

    iddfile = '/usr/local/EnergyPlus-8-6-0/Energy+.idd'
    try:
        IDF.setiddname (iddfile)
    except modeleditor.IDDAlreadySetError as e:
        pass
    IDF.setiddname (iddfile)
    path_idf1 = str (modificacion.modificar_archivo_idf)

    idf1 = IDF ('media/' + path_idf1)

    if args_class == 'MATERIAL_NOMASS':
        for objeto in idf1.idfobjects['MATERIAL:NOMASS']:
            if objeto.Name == args_name:

                atributos = objeto.fieldnames
                # print(atributos)
                valores = objeto.fieldvalues
                # print(valores)
                list = zip (atributos, valores)
                return render (request, 'editar_objeto.html',
                               {'list': list, 'objeto': objeto, 'args_name': args_name, 'args_class': args_class,
                                'args_id': args_id, 'materials' :  materials})
            else:
                print ("NO EXISTE")
    else:
        for objeto in idf1.idfobjects[args_class]:
            if objeto.Name == args_name:

                atributos = objeto.fieldnames
                # print (atributos)
                valores = objeto.fieldvalues
                # print (valores)
                list = zip (atributos, valores)
                return render (request, 'editar_objeto.html',
                               {'list': list, 'objeto': objeto, 'args_name': args_name, 'args_class': args_class,
                                'args_id': args_id,  'materials' :  materials})
            else:
                print ("NO EXISTE")


def modificar_submit(request, args_id):
    llave = request.POST.get ('key')
    modificacion = get_object_or_404 (Modificar, pk=args_id)
    iddfile = '/usr/local/EnergyPlus-8-6-0/Energy+.idd'
    try:
        IDF.setiddname (iddfile)
    except modeleditor.IDDAlreadySetError as e:
        pass
    IDF.setiddname(iddfile)
    path_idf1 = str (modificacion.modificar_archivo_idf)
    # file_now =  codecs.EncodedFile('media/' + path_idf1, 'utf-8', errors='ignore')
    sourceFile = codecs.open ('media/' + path_idf1, "r", "ascii", "ignore")
    destino = open ('media/modificacion_idf/root.idf', "w")
    destino.write(sourceFile.read().decode('US-ASCII','ignore').encode('utf-8'))
    idf_file = IDF('media/modificacion_idf/root.idf')
    clase_material = idf_file.idfobjects['MATERIAL']
    material_nomass = 'MATERIAL_NOMASS'
    material_ = 'MATERIAL'
    clase_material_nomass = idf_file.idfobjects['MATERIAL:NOMASS']

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

        idf_file.saveas('media/' + path_idf1,'default','utf-8')

        return render (request, 'test.html', {'args_id': args_id, 'modificacion' : modificacion, 'hola': llave, 'clase_material': clase_material,
                                                       'clase_material_nomass': clase_material_nomass,
                                                       'material_nomass': material_nomass, 'materials': material_})
    # 'key' : key, 'name' : name,
    # 'Roughness': Roughness, 'Thickness': Thickness, 'Conductivity': Conductivity,
    # 'Density': Density, 'Specific_Heat': Specific_Heat, 'Thermal_Absorptance': Thermal_Absorptance,
    # 'Solar_Absorptance': Solar_Absorptance, 'Visible_Absorptance': Visible_Absorptance
    else:
        return render (request, 'test.html', {'args_id': args_id, 'modificacion' : modificacion, 'hola': llave, 'clase_material': clase_material,
                                                       'clase_material_nomass': clase_material_nomass,
                                                       'material_nomass': material_nomass, 'materials': materials})
def detalle_modificacion(request, args_id ):
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
    material_nomass = 'MATERIAL_NOMASS'
    materials = 'MATERIAL'
    clase_material_nomass = idf_file.idfobjects['MATERIAL:NOMASS']

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

        return render (request, 'test.html', {'args_id': args_id, 'modificacion': modificacion, 'hola': llave,
                                              'clase_material': clase_material,
                                              'clase_material_nomass': clase_material_nomass,
                                              'material_nomass': material_nomass, 'materials': materials})
    # 'key' : key, 'name' : name,
    # 'Roughness': Roughness, 'Thickness': Thickness, 'Conductivity': Conductivity,
    # 'Density': Density, 'Specific_Heat': Specific_Heat, 'Thermal_Absorptance': Thermal_Absorptance,
    # 'Solar_Absorptance': Solar_Absorptance, 'Visible_Absorptance': Visible_Absorptance
    else:
        return render (request, 'test.html', {'args_id': args_id, 'modificacion': modificacion, 'hola': llave,
                                              'clase_material': clase_material,
                                              'clase_material_nomass': clase_material_nomass,
                                              'material_nomass': material_nomass, 'materials': materials})





def ver_modificaciones(request):
    lista_modificaciones = Modificar.objects.all ()
    context = {'lista_modificaciones': lista_modificaciones}
    return render (request, 'ver_modificaciones.html', context)



def crear_materials(request):
    if request.method == 'POST':
        form = MaterialsForm(request.POST, request.FILES)
        if form.is_valid ():
            nuevo_materials = form.save ()
            materials = get_object_or_404 (Materials, pk=nuevo_materials.pk)
            lista_materials = Materials.objects.all ()
            context = {'lista_materials': lista_materials}
            message = "Material agregado satisfactoriamente !"
            return render (request, 'ver_materiales.html', {'materials': context})
    else:
        form = MaterialsForm()
    return render (request, 'crear_materials.html', locals (), {'form': form})



def ver_materials(request):
    lista_materials = Materials.objects.all ()
    context = {'lista_materials': lista_materials}
    return render (request, 'ver_materiales.html', context)












