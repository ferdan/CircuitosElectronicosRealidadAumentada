# *************************************
#
#   Clase: --> Graficador 
#   Modulo: -> graficador.py
#
# Descripción:
#   - Graficar los datos obtenidos por arduino
#   - Dibujar, mostrar informacion
#
# Fecha: julio 28/2021
#
# ************************************

from m.calculadora_datos_graficas import calculadora_datos_graficas
from m.fsm import fsm

import numpy as np
import cv2

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import EngFormatter

import graphviz as gv

from collections import deque

import os

from engineering_notation import EngNumber
import math
import statistics

graficas = []

class Graficador():

    # -------------------------------------------------------
    #           CONSTRUCTOR
    # -------------------------------------------------------
    def __init__(self,modelo):

        print("")
        print(" CONSTRUCTOR:  Clase: Graficador")
        self.modelo = modelo
        self.vectores_muestras = modelo.vectores_muestras
        self.titulos_vectores_muestras = modelo.titulos_vectores_muestras
        self.titulos_marcadores_display = modelo.titulos_marcadores_display

    def construir_graficas_muestras(self):

        # --- Construccion AUTOMATICA de la graficas ---
        titulos_marcadores = list(self.titulos_marcadores_display)
            
        global graficas
        graficas = []

        muestras = self.vectores_muestras

        for i in range(len(titulos_marcadores)):
            titulo_grafica = self.titulos_marcadores_display[titulos_marcadores[i]]
            nombre_vectores_grafica = self.extraer_informacion_cadena(titulo_grafica)

            # --- Construccion AUTOMATICA de cada GRAFICA, a partir de la
            #     información proporcionada en la clase Modelo en las estructuras:
            #     -> titulos_vectores_muestras   <-- Vector
            #     -> titulos_marcadores_display  <-- Diccionario
            #     Estas estructuras de datos se conectan con los nombres de los
            #     vectores que se encuentran en el Diccionario muestras
            #     -> vectores_muestras <-- Diccionario
            # --------------------------------------------------------------------
            plt.figure(i)
            # --- Graficas VECTOR A vs. muestras ---
            if len(nombre_vectores_grafica) == 1 and len(nombre_vectores_grafica[0]) == 1:
                plt.plot(muestras[nombre_vectores_grafica[0][0]],
                         label = nombre_vectores_grafica[0][0] + ' vs. muestras')
            # --- Graficas VECTOR A vs VECTOR B ---
            if len(nombre_vectores_grafica) == 1 and len(nombre_vectores_grafica[0]) == 2:
                plt.plot(muestras[nombre_vectores_grafica[0][0]],
                         muestras[nombre_vectores_grafica[0][1]],
                         label = nombre_vectores_grafica[0][0] + ' vs. ' +
                         nombre_vectores_grafica[0][1])
            # --- Graficas MULTIPLES tipo: VECTOR A vs VECTOR B ---
            if len(nombre_vectores_grafica) > 2:
                for g in range(len(nombre_vectores_grafica)):
                    plt.plot(muestras[nombre_vectores_grafica[g][0]],
                             muestras[nombre_vectores_grafica[g][1]],
                             label = nombre_vectores_grafica[g][0] + ' vs. ' +
                             nombre_vectores_grafica[g][1])    
            plt.titulo = 'Grafica ' + str(i)
            plt.ylabel = 'y label'
            plt.xlabel = 'x label'
            plt.legend()
            
            # --- Guardado de las gráficas en:
            #     1. "Archivo en disco [*.jpg] para su uso posterior
            #        por parte de la Clase Display
            #     2. El arreglo GLOBAL: 'graficas', elcual contiene
            #        la ruta en donde se guardó la gráfica correspondiente
            # ------------------------------------------------------------
            grafica = 'g/grafica_' + str(i) + ".jpg"
            plt.savefig(grafica)
            graficas.append(grafica)
    
    def extraer_informacion_cadena(self,cadena):

        #print("")
        #print(" cadena original = ",cadena)

        # --- Separa grupos de letras ---
        subcadena = ''
        subtitulos = []
        ignorar_caracter = False
        num_char = 0
        for ch in cadena:
            num_char += 1
            # --- Ignorar los caracteres "espacio" [' '] y "coma" [','] ---
            if ch == ' ' or ch == ',':
                ignorar_caracter = True
                if num_char != 1:
                    subtitulos.append(subcadena)
                subcadena = ''
            else:
                subcadena += ch
            if num_char == len(cadena): subtitulos.append(subcadena)

        # --- Genera tuplas de dos elementos ---
        tupla = []
        arreglo_tuplas = []
        for i in range(len(subtitulos)):
            # --- Detecta conector ['vs'] ó espacio [' '] --
            if subtitulos[i] == 'vs' or subtitulos[i] == '':
                dummy = 0 # <--- No hacer nada ---
            else:
                tupla.append(subtitulos[i])
            if subtitulos[i] == '' or i == (len(subtitulos)-1):
                arreglo_tuplas.append(tupla)
                tupla = []
                
        return arreglo_tuplas

    # Tomado de https://stackoverflow.com/questions/20036161/can-we-draw-digital-waveform-graph-with-pyplot-in-python-or-matlab
    def my_lines(self,ax, pos, *args, **kwargs):
        if ax == 'x':
            for p in pos:
                plt.axvline(p, *args, **kwargs)
        else:
            for p in pos:
                plt.axhline(p, *args, **kwargs)


    def graficar_curvas_FSM(self):

        global graficas
        graficas = []

        muestras = self.vectores_muestras
        muestras_llaves = list(muestras)
        #print('muestras_llaves: '+str(muestras_llaves))
        
        # Se obtiene el numero de series de muestras para cada canal (ej. para 300 muestras hay 6 curvas). 
        lim_max = len(muestras[muestras_llaves[0]])

        fsm1 = fsm()
        calc = calculadora_datos_graficas()
        
        # ---------------------------------------------------------------------------------------------------------------------------------------------
        # Algunas referencias que consulte para realizar el codigo, son las siguientes:
        # Draw digital waveforms
        # https://stackoverflow.com/questions/20036161/can-we-draw-digital-waveform-graph-with-pyplot-in-python-or-matlab
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.step.html
        #
        # Creating a list using range()
        # https://www.kite.com/python/answers/how-to-create-an-array-of-numbers-1-to-n-in-python
        # 
        # Modify axis ticks
        # https://stackoverflow.com/questions/12608788/changing-the-tick-frequency-on-x-or-y-axis-in-matplotlib
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.xticks.html
        #
        # Available colors for matplotlib
        # https://matplotlib.org/stable/gallery/color/named_colors.html
        #
        # Create list of lists
        # https://thispointer.com/how-to-create-and-initialize-a-list-of-lists-in-python/
        # 
        # Find indexes of same list elements
        # https://stackoverflow.com/questions/5419204/index-of-duplicates-items-in-a-python-list
        #
        # Find coordinates form intersections between a circle and a line
        # https://stackoverflow.com/questions/30844482/what-is-most-efficient-way-to-find-the-intersection-of-a-line-and-a-circle-in-py
        # See answer by Peter
        #
        # Python know maximum interger value
        # https://www.delftstack.com/howto/python/python-max-int/
        #
        # Graphviz for Python
        # https://graphviz.readthedocs.io/en/stable/manual.html#basic-usage
        # https://graphviz.readthedocs.io/en/stable/examples.html#fsm-py
        #
        # Python cv2 resize an image, concatenate an image
        # https://www.tutorialkart.com/opencv/python/opencv-python-resize-image/
        # https://www.geeksforgeeks.org/image-resizing-using-opencv-python/
        # https://www.geeksforgeeks.org/concatenate-images-using-opencv-in-python/
        #
        # Delete a file
        # https://careerkarma.com/blog/python-delete-file/
        # https://stackoverflow.com/questions/3430372/how-do-i-get-the-full-path-of-the-current-files-directory
        # ---------------------------------------------------------------------------------------------------------------------------------------------
        
        colores_lineas = ['tab:blue','tab:orange','tab:green']

        # --- Grafica 0 : Entrada, Estado y Salida en el tiempo ---------------------------------------------------------------------------------------
        plt.figure(0)
        for i in range(0,len(muestras_llaves)):
            plt.subplot(3, 1, i+1)
            
            #Se colocan las lineas auxiliares de las graficas. 
            self.my_lines('x', list(range(len(muestras[muestras_llaves[i]])+1)), color='.5', linewidth=0.5)
            self.my_lines('y', list(range(int(max(muestras[muestras_llaves[i]])+1))), color='.5', linewidth=0.5)
            
            # Se grafican entrada, estado y salida. 
            plt.step(range(0,lim_max),muestras[muestras_llaves[i]], linewidth = 2,color=colores_lineas[i], where='post', label=muestras_llaves[i])

            # Se modifican los ejes para que muestren cada numero entero. 
            plt.xticks(np.arange(0,len(muestras[muestras_llaves[i]])+1,step = 1))
            plt.yticks(np.arange(0,max(muestras[muestras_llaves[i]])+1,step = 1))
            
            plt.ylabel(muestras_llaves[i])
            plt.legend()
            
        plt.xlabel('Muestras')
        
        plt.subplot(3, 1, 1)
        plt.title("Señales logicas en el tiempo")
        
        grafica = 'g/00_Senales_binarias_en_el_tiempo' + ".jpg"
        plt.savefig(grafica)
        graficas.append(grafica)

        # --- Grafica 1 : Tabla de estados ------------------------------------------------------------------------------------------------------------
        # --- Generacion de un canvas de w = 240 x h = 180 ---
        canvas2 = np.ones((480,640,3), dtype = "uint8")*255
        
        # --- RECTANGULO ---
        cv2.rectangle(canvas2, (20,20),(620,40),(0,0,0), -1, cv2.LINE_AA)

        # Se colocan los titulos de la tabla. 
        cv2.putText(canvas2,"Tabla de estados de la maquina de estados finitos", (30, 35),cv2.FONT_HERSHEY_SIMPLEX,0.5, (255, 255, 255), 1, cv2.LINE_AA)


        cv2.putText(canvas2,"Estado", (30, 65),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)
        
        cv2.putText(canvas2,"Salida", (140, 65),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)
        
        cv2.putText(canvas2,"Entrada", (250, 65),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(canvas2,":", (320, 65),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(canvas2,"Estado actual", (345, 65),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(canvas2,"->", (465, 65),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(canvas2,"Estado futuro", (500, 65),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)

        # Se dibujan lineas para dividir la tablas. 
        cv2.rectangle(canvas2, (20,50),(620,48),(0,0,0), -1, cv2.LINE_AA)
        cv2.rectangle(canvas2, (20,71),(620,73),(0,0,0), -1, cv2.LINE_AA)
        
        ajuste_espacio = 0
        str_transiciones = [[''] for i in range(0,len(fsm1.tabla_transiciones_estado_futuro))]
        estados_transiciones = [[0] for i in range(0,len(fsm1.tabla_transiciones_estado_futuro))]
        
        for i in range(0,fsm1.num_estados):
            # Se obtiene el estado y salida correspondiente. 
            str_bin_estado = calc.decimal_a_binario(i,math.ceil(math.log(fsm1.num_estados,2)))
            str_bin_salida = calc.decimal_a_binario(fsm1.tabla_output_por_estado[i],fsm1.bits_salida)

            # Se escriben los textos del estado y salida correspondiente. 
            cv2.putText(canvas2,"q"+str(i)+": "+str_bin_estado, (30, 70+(i+ajuste_espacio+1)*20),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(canvas2,str_bin_salida, (140, 70+(i+ajuste_espacio+1)*20),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)

            #print("fsm1.tabla_transiciones_estados["+str(i)+"]: "+str(fsm1.tabla_transiciones_estados[i])+" , len: "+str(len(fsm1.tabla_transiciones_estados[i])))

            j = 0
            
            while j < len(fsm1.tabla_transiciones_estado_futuro[i]):
                # Se obtiene el texto de la transicion correspondiente, si hay mas de una posible, se agregan condiciones de no importa con "X". 
                transiciones = calc.list_duplicates_of(fsm1.tabla_transiciones_estado_futuro[i],fsm1.tabla_transiciones_estado_futuro[i][j])
                diff = calc.obtener_bits_cambiantes(fsm1,transiciones,i)
                str_transicion = calc.obtener_str_de_binario_transicion(fsm1.bits_transicion-1,fsm1.tabla_transiciones_estados[i][transiciones[0]],diff)
                
                y_coor = 70+(i+ajuste_espacio+1)*20

                # Se colocan los textos para la parte de transiciones de estados. 
                cv2.putText(canvas2,str_transicion, (265, y_coor),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)
                cv2.putText(canvas2,":", (320, y_coor),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)
                cv2.putText(canvas2,"q"+str(i), (395, y_coor),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)
                cv2.putText(canvas2,"->", (465, y_coor),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)
                cv2.putText(canvas2,"q"+str(fsm1.tabla_transiciones_estado_futuro[i][transiciones[0]]), (542, y_coor),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)

                # Se guardan los textos transiciones calculadas y los estados a los que cambia.
                str_transiciones[i].append(str_transicion)
                estados_transiciones[i].append(fsm1.tabla_transiciones_estado_futuro[i][j])
                
                j = j+len(transiciones)
                ajuste_espacio += 1
                
                str_transicion = ''

            # Ajuste de las listas, ya que el primer dato no contiene informacion util. 
            str_transiciones[i].pop(0)
            estados_transiciones[i].pop(0)

            # Se colocan lineas que dividen cada estado. 
            cv2.rectangle(canvas2, (238,48),(240,68+(i+ajuste_espacio+1)*20),(0,0,0), -1, cv2.LINE_AA) 
            cv2.rectangle(canvas2, (20,65+(i+ajuste_espacio+1)*20),(620,67+(i+ajuste_espacio+1)*20),(0,0,0), -1, cv2.LINE_AA)

        # Se colocan textos de notas adicionales. 
        cv2.putText(canvas2,"Los estados son: "+str(fsm1.tabla_nombres_estados),(20, 390),cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(canvas2,"Las salidas son: "+str(fsm1.tabla_nombres_salidas),(20, 405),cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(canvas2,"Las entradas son: "+str(fsm1.tabla_nombres_entradas),(20, 420),cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 0, 0), 1, cv2.LINE_AA)
        
        cv2.putText(canvas2,"La tabla de transiciones indica con cual entrada pasa de un estado a otro estado. " ,(20, 445),cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(canvas2,"Si en la entrada hay bits en X, significa que no importa el valor de ese bit para pasar al siguiente estado. " ,(20, 460),cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(canvas2,"Las combinaciones de entrada no incluidas en la tabla indican que el estado no cambia. " ,(20, 475),cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 0, 0), 1, cv2.LINE_AA)

        #print("str_transiciones: "+str(str_transiciones))
        #print("estados_transiciones: "+str(estados_transiciones))
        
        filename = "g/01_Tabla_estados_binarios" + ".jpg"
        cv2.imwrite(filename,canvas2)
        graficas.append(filename)

        # --- Grafica 2 : Diagrama de estados ---------------------------------------------------------------------------------------------------------

        # Opcion 1. Diagrama de estados con funciones desarrolladas en calculadora_datos_graficas.py, sin utilizar la librería graphviz
        # --- Generacion de un canvas de w = 480 x h = 640 ---
        canvas2 = np.ones((480,640,3), dtype = "uint8")*255
        
        # --- RECTANGULO ---
        cv2.rectangle(canvas2, (20,20),(620,40),(0,0,0), -1, cv2.LINE_AA)

        # --- Estados binarios ---

        # Se coloca el titulo. 
        cv2.putText(canvas2,"Diagrama de estados de la maquina de estados finitos", (30, 35),cv2.FONT_HERSHEY_SIMPLEX,0.5, (255, 255, 255), 1, cv2.LINE_AA)

        # Se colocan las coordenadas de los circulos a utilizar, uno por cada estado y otros parametros. 
        xcoords = [int(640/8),int(640*7/8),320,320]
        ycoords = [90,90,220,380]
        length_lineas = 10
        c_radio = [40,58]
        
        for i in range(0,fsm1.num_estados):
            # Se dibuja el circulo del estado actual. 
            #print("estado actual: "+str(i))
            cv2.circle(canvas2, (xcoords[i],ycoords[i]), c_radio[0], (0,0,0), 2)
            #cv2.circle(canvas2, (xcoords[i],ycoords[i]), c_radio[1], (0,0,0), 2)

            # Se obtienen los textos del estado actual y de la salida. 
            estado = calc.decimal_a_binario(i,math.ceil(math.log(fsm1.num_estados,2)))
            salida = calc.decimal_a_binario(fsm1.tabla_output_por_estado[i],fsm1.bits_salida)

            #cv2.line(canvas2,(xcoords[i],ycoords[i]-50),(xcoords[i],ycoords[i]+50),(0,0,0), 3)

            # Se colocan los textos del estado actual y de la salida
            cv2.putText(canvas2,"q"+str(i)+":"+str(estado),(xcoords[i]-25,ycoords[i]-15),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(canvas2,"Salida: ",(xcoords[i]-26,ycoords[i]+7),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(canvas2,str(salida),(xcoords[i]-14,ycoords[i]+22),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)

            # Se escribe un texto adicional para indicar si es el estado inicial. 
            if i == fsm1.estado_inicial:
                cv2.putText(canvas2,"Estado inicial",(xcoords[i]-60,ycoords[i]+c_radio[1]),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)

            # Se itera sobre las transiciones de este estado actual hacia otros. 
            for j in range(0,len(estados_transiciones[i])):
                #print("Estado a actualizar: "+str(j))
                
                coords_labels = 0

                # Se calculan las coordenadas de las flechas para indicar los cambios de estado. 
                lineas_transiciones = calc.obtener_puntos_lineas_transicion(canvas2,xcoords,ycoords,c_radio,length_lineas,i,estados_transiciones[i][j])
                #print("lineas_transiciones : "+str(lineas_transiciones))

                # Se calcula la distancia de las flechas con las coordenadas anteriores. 
                d = calc.distancia_entre_puntos(lineas_transiciones[0],lineas_transiciones[2])
                
                # Se calcula el ajuste para la cabeza de la flecha (para que todas las flechas tengan el mismo tamano de flecha). 
                tip_l = 10 / d
                #print(d)

                # Puesto que se calcularon coordenadas para dos flechas (una de ida y otra de vuelta), se elige alguna de las dos.
                # Si el estado actual es menor que el estado al que cambia, se utiliza la primera flecha, de lo contrario, se utiliza la segunda. 
                # Se dibuja la flecha. 
                if i > estados_transiciones[i][j]:
                    canvas2 = cv2.arrowedLine(canvas2,tuple(lineas_transiciones[0]),tuple(lineas_transiciones[2]),(0,0,0), 3, tipLength = tip_l)
                    coords_labels = 0
                else:
                    canvas2 = cv2.arrowedLine(canvas2,tuple(lineas_transiciones[1]),tuple(lineas_transiciones[3]),(0,0,0), 3, tipLength = tip_l)
                    coords_labels = 1

                # Se coloca el texto correspondiente al numero binario con el que cambia de estado. 
                cv2.putText(canvas2,str_transiciones[i][j],calc.obtener_coordenadas_labels(lineas_transiciones[coords_labels],lineas_transiciones[coords_labels+2]),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)

        # Se escriben textos de notas adicionales. 
        cv2.putText(canvas2,"Cada circulo es un estado. Cada flecha representa un cambio de estado, indicado por el numero adyacente. " ,(20, 445),cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 0, 0), 1, cv2.LINE_AA) 
        cv2.putText(canvas2,"Las combinaciones de transiciones entre estados que no aparecen en el diagrama indica que no hay cambio" ,(20, 460),cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(canvas2,"de estado cuando ocurren.Si hay 'X' en el numero de una flecha significa que no importa el valor de ese bit. " ,(20, 475),cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 0, 0), 1, cv2.LINE_AA)
        
        filename = "g/02_Diagrama_estados_binarios" + ".jpg"
        cv2.imwrite(filename,canvas2)
        graficas.append(filename)

        # --- Grafica 2 : Diagrama de estados ---------------------------------------------------------------------------------------------------------
        # Opcion 2. Diagrama de estados con funciones desarrolladas en calculadora_datos_graficas.py, utilizando la librería graphviz

        # Nombre del diagrama de estados
        g = gv.Digraph('g/diagrama_estados',format='png')

        # Configuracion del nodo inicial
        g.node('ini', shape="point")

        # Configuracion del diagrama de estados, que vaya de izquierda a derecha
        g.graph_attr['rankdir'] = 'LR'

        str_completo = [[''] for i in range(0,fsm1.num_estados)]
        
        for i in range(0,fsm1.num_estados):

            # Calculo de las variables estado y salida en binario
            estado = calc.decimal_a_binario(i,math.ceil(math.log(fsm1.num_estados,2)))
            salida = calc.decimal_a_binario(fsm1.tabla_output_por_estado[i],fsm1.bits_salida)

            # Concatenacion del string completo para cada estado
            str_completo[i] = 'Estado '+str(estado)+'\n'+str(fsm1.tabla_nombres_estados[i])+'\n'+"Salida "+str(salida)

            # Se asignan los nombres de los estados.
            # El estado final tiene forma de doble circulo, mientras que se indica con una flecha con punto para el estado inicial
            if i == fsm1.estado_final:
                g.node(str_completo[i], shape="doublecircle")
            else:
                g.node(str_completo[i])
            if i == fsm1.estado_inicial:
                g.edge('ini',str_completo[i])
        # Se asignan las flechas de transicion entre estados
        for i in range(0,fsm1.num_estados):
            for j in range(0,len(estados_transiciones[i])):
                #print('flecha de A:'+str(fsm1.tabla_nombres_estados[i])+' a B:'+str(fsm1.tabla_nombres_estados[estados_transiciones[i][j]]))
                
                g.edge(str_completo[i],str_completo[estados_transiciones[i][j]],str(str_transiciones[i][j]))

        # Genera el diagrama, pero no lo muestra en el visor de fotos
        g.render(view=False)

        # Se lee la imagen del diagrama de estados generado
        diagrama = cv2.imread('g/diagrama_estados.gv.png')
        #height, width, channels = image.shape
        scale_percent = 0
        dim = 0

        # Se recalculan las dimensiones de la imagen.
        # Se pregunta si se recalculan los limites para que ocupe todo el largo (640) o todo el alto (320) establecidos
        # Se calcula el porcentaje de escalamiento de la imagen
        if(diagrama.shape[1]*320/diagrama.shape[0] <= 640):
            scale_percent = 320/diagrama.shape[0]
            dim = (int(diagrama.shape[1]*scale_percent), 320)
        else:
            scale_percent = 640/diagrama.shape[1]
            dim = (640, int(diagrama.shape[0]*scale_percent))
        
        # Se asignan las nuevas dimensiones de la imagen, de acuerdo al porcentaje de estaca calculado anteriormente
        diagrama_resized = cv2.resize(diagrama, dim, interpolation = cv2.INTER_AREA)
        #print('scale percent: ',scale_percent)
        #print('diagrama_resized Dimensions : ',diagrama_resized.shape)

        # Se guarda la imagen escalada
        filename = "g/diagrama_estados_resized" + ".jpg"
        cv2.imwrite(filename,diagrama_resized)
        
        #cv2.imshow("Resized image", resized)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

        # En caso de requierirlo, se concatenan partes en blanco a la imagen del diagrama de estados a los lados
        if(diagrama_resized.shape[1] < 640):
            canvas2 = np.ones((diagrama_resized.shape[0],int((640-diagrama_resized.shape[1])/2),3), dtype = "uint8")*255
            filename = "g/blanco1" + ".jpg"
            cv2.imwrite(filename,canvas2)

            # Se verifica si se necesitan dos imagenes de igual tamaño, esto es si las dimenciones de la imagen del diagrama de estados es par
            # De lo contrario se crean dos imagenes en blanco de diferente tamano
            if diagrama_resized.shape[1]%2 == 1:
                canvasaux = np.ones((diagrama_resized.shape[0],int((640-diagrama_resized.shape[1])/2)+1,3), dtype = "uint8")*255
                #print("blanco2 = blanco1 + 1")
                filename = "g/blanco2" + ".jpg"
                cv2.imwrite(filename,canvasaux)
            else:
                #print("blanco2 = blanco1")
                filename = "g/blanco2" + ".jpg"
                cv2.imwrite(filename,canvas2)

            img_blanco1 = cv2.imread('g/blanco1.jpg')
            img_blanco2 = cv2.imread('g/blanco2.jpg')
            #print('blanco1 Dimensions : ',img_blanco1.shape)
            #print('blanco2 Dimensions : ',img_blanco2.shape)
            
            im_h = cv2.hconcat([img_blanco1,diagrama_resized,img_blanco2])
            #print('im_h Dimensions : ',im_h.shape)
        else:
            im_h = diagrama_resized.copy()
            #print('im_h Dimensions : ',im_h.shape)

        #cv2.imshow("Resized image", im_h)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

        # Se crea la imagen del titulo del diagrama de estados
        canvas2 = np.ones((60,640,3), dtype = "uint8")*255
        cv2.rectangle(canvas2, (20,20),(620,40),(0,0,0), -1, cv2.LINE_AA)
        cv2.putText(canvas2,"Diagrama de estados de la maquina de estados finitos", (30, 35),cv2.FONT_HERSHEY_SIMPLEX,0.5, (255, 255, 255), 1, cv2.LINE_AA)
        filename = "g/titulo" + ".jpg"
        cv2.imwrite(filename,canvas2)
        img_titulo = cv2.imread('g/titulo.jpg')

        # Se crea la imagen que contiene las anotaciones del diagrama de estados
        canvas2 = np.ones((420-diagrama_resized.shape[0],640,3), dtype = "uint8")*255
        cv2.putText(canvas2,"Los estados son: "+str(fsm1.tabla_nombres_estados),(20, 330-diagrama_resized.shape[0]),cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(canvas2,"Las salidas son: "+str(fsm1.tabla_nombres_salidas),(20, 345-diagrama_resized.shape[0]),cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(canvas2,"Las entradas son: "+str(fsm1.tabla_nombres_entradas),(20, 360-diagrama_resized.shape[0]),cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 0, 0), 1, cv2.LINE_AA)
        
        cv2.putText(canvas2,"Cada circulo es un estado. Cada flecha representa un cambio de estado, indicado por el numero adyacente. ",(20, 385-diagrama_resized.shape[0]),cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(canvas2,"Las combinaciones de transiciones entre estados que no aparecen en el diagrama indica que no hay cambio" ,(20, 400-diagrama_resized.shape[0]),cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(canvas2,"de estado cuando ocurren.Si hay 'X' en el numero de una flecha significa que no importa el valor de ese bit. " ,(20, 415-diagrama_resized.shape[0]),cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 0, 0), 1, cv2.LINE_AA)
        filename = "g/anotaciones" + ".jpg"
        cv2.imwrite(filename,canvas2)

        # Se leen las imagenes de las anotaciones y del titulo
        img_anotaciones = cv2.imread('g/anotaciones.jpg')
        img_titulo = cv2.imread('g/titulo.jpg')

        # Se concatenan las imagenes del diagrama de estados, titulo y anotaciones
        im_v = cv2.vconcat([img_titulo,im_h,img_anotaciones])

        # Se guarda la imagen final
        filename = "g/03_Diagrama_estados_binarios_alternativo" + ".jpg"
        cv2.imwrite(filename,im_v)
        graficas.append(filename)


        # Se obtiene la ruta desde donde se ejecuta el achivo main.py
        path = os.path.abspath(os.getcwd())
        #print(path)

        # Se eliminan las imagenes que ya no se van a usar, utilizando la ruta calculada anteriormente
        for i in ['g/diagrama_estados.gv','g/diagrama_estados.gv.png','g/diagrama_estados_resized.jpg','g/blanco1.jpg','g/blanco2.jpg','g/titulo.jpg','g/anotaciones.jpg']:
            try:
                os.remove(path+'/'+i)
            except:
                #print("Archivo "+i+" no removido")
                pass
            
        #cv2.imshow('g/03_Diagrama_estados_binarios_alternativo.jpg', im_v)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

        # --- Grafica 3 : Voltaje y binario -----------------------------------------------------------------------------------------------------------
        # --- Generacion de un canvas de w = 480 x h = 640 ---
        canvas2 = np.ones((480,640,3), dtype = "uint8")*255
        
        # --- RECTANGULO ---
        cv2.rectangle(canvas2, (20,20),(620,40),(0,0,0), -1, cv2.LINE_AA)

        # --- Estados binarios ---

        # Se escribe el titulo. 
        cv2.putText(canvas2,"Transiciones de estados de acuerdo al vector de transiciones de entrada utilizado", (30, 35),cv2.FONT_HERSHEY_SIMPLEX,0.5, (255, 255, 255), 1, cv2.LINE_AA)
        #cv2.circle(canvas2, (320,260), 215,(255,0,0),2)
        #cv2.circle(canvas2, (320,260), 185,(255,0,0),2)

        angle = np.linspace(0,2*math.pi,int(len(muestras[muestras_llaves[0]])/2+1))
        #print("angle: "+str(angle))
        #print("muestras_llaves[0]: "+str(muestras_llaves[0])+': '+str(muestras[muestras_llaves[0]]))
        #print("muestras_llaves[1]: "+str(muestras_llaves[1])+': '+str(muestras[muestras_llaves[1]]))
        #print("muestras_llaves[2]: "+str(muestras_llaves[2])+': '+str(muestras[muestras_llaves[2]]))
        
        # Dibuja cada uno de los circulos y la informacion del estado correspondiente que va dentro de ella. Tambien dibuja las flechas entre circulos. 
        for i in range(0,int(len(muestras[muestras_llaves[0]])/2)):
            # Se obtienen las coordenadas del circulo
            xcoor = int(320+185*math.cos(angle[i]))
            ycoor = int(260+185*math.sin(angle[i]))

            # Se dibuja el circulo. 
            cv2.circle(canvas2, (xcoor,ycoor), 35, (0,0,0), 2)

            # Se obtienen los textos del estado actual y de la salida a partir del vector de muestras leido. 
            str_bin_estado = calc.decimal_a_binario(int(muestras[muestras_llaves[1]][i]),math.ceil(math.log(fsm1.num_estados,2)))
            str_bin_salida = calc.decimal_a_binario(int(muestras[muestras_llaves[2]][i]),fsm1.bits_salida)

            # Se escriben los textos del estado actual y de la salida. 
            cv2.putText(canvas2,"q"+str(int(muestras[muestras_llaves[1]][i]))+":"+str_bin_estado,(xcoor-24,ycoor-15),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(canvas2,"Salida: ",(xcoor-26,ycoor+7),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(canvas2,str_bin_salida,(xcoor-15,ycoor+22),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)

            # Encuentra las coordenadas de la flecha entre dos circulos. 
            i1 = calc.get_intersections(320,260,180,xcoor,ycoor,40)
            i2 = calc.get_intersections(320,260,180,int(320+185*math.cos(angle[i+1])),int(260+185*math.sin(angle[i+1])),40)
            dist = 100
            flecha_coords = [0]*4
            '''for j in range(0,1):
                if math.dist([i1[j*2],i1[j*2+1]],[i2[j*2],i2[j*2+1]]) < dist:
                    print("1, j="+str(j))
                    dist = math.dist([i1[j*2],i1[j*2+1]],[i2[j*2],i2[j*2+1]])
                    flecha_coords[0] = i1[j*2]
                    flecha_coords[1] = i1[j*2+1]
                    flecha_coords[2] = i2[j*2]
                    flecha_coords[3] = i2[j*2+1]
                if math.dist([i1[(2-j*2)],i1[(2-j*2)+1]],[i2[j*2],i2[j*2+1]]) < dist:
                    print("2, j="+str(j))
                    dist = math.dist([i1[j*2],i1[j*2+1]],[i2[j*2],i2[j*2+1]])
                    flecha_coords[0] = i1[(2-j*2)]
                    flecha_coords[1] = i1[(2-j*2)+1]
                    flecha_coords[2] = i2[j*2]
                    flecha_coords[3] = i2[j*2+1]'''
            # Se puede comprobar con el codigo comentado que esta es la solucion que proporciona las coordenadas correctas. 
            flecha_coords[0] = i1[2]
            flecha_coords[1] = i1[3]
            flecha_coords[2] = i2[0]
            flecha_coords[3] = i2[1]

            # Se calcula un ajuste a las coordenadas de las etiquetas de las flechas. 
            fxcoor = int((flecha_coords[0] + flecha_coords[2])/2 + int(-15+32*math.cos(angle[i])))
            fycoor = int((flecha_coords[1] + flecha_coords[3])/2 + int(7+18*math.sin(angle[i])))
            
            #print('coordenadas de la flecha: '+str(flecha_coords))
            #print('distancia: '+str(dist))

            # Dibuja la flecha y escribe el texto correspondiente. 
            canvas2 = cv2.arrowedLine(canvas2,(int(flecha_coords[0]),int(flecha_coords[1])),(int(flecha_coords[2]),int(flecha_coords[3])),(0,0,0), 3, tipLength = 0.25)
            str_bin_entrada_transicion = calc.decimal_a_binario(int(muestras[muestras_llaves[0]][i+1]),fsm1.bits_salida)
            cv2.putText(canvas2,str_bin_entrada_transicion,(fxcoor,fycoor),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)

            #print("str_bin_estado: "+str(str_bin_estado)+str(str_bin_entrada_transicion))
            # Si es el primer estado el que se dibuja, se anade el texto que indique que es el inicio. 
            if i == 0:
                canvas2 = cv2.arrowedLine(canvas2,(xcoor+40+60,ycoor),(xcoor+40,ycoor),(0,0,0), 3, tipLength = 0.25)
                cv2.putText(canvas2,"Inicio",(xcoor+55,ycoor-7),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)
        
        cv2.putText(canvas2,"Cada circulo es un estado. Cada flecha representa un cambio de estado, indicado por el numero adyacente. " ,(20, 477),cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 0, 0), 1, cv2.LINE_AA)
        
        filename = "g/04_Trancisiones_fsm" + ".jpg"
        cv2.imwrite(filename,canvas2)
        graficas.append(filename)

        # --- Auxiliar para depuracion ---
        plt.show()
    
    @property
    def graficas(self):
        return graficas # --- Nombre de la grafica y ruta donde se guardo ---

    def imprimir_archivos_graficas(self):

        print(" ")
        print(" En CLASE Graficador::")
        print("**************************************************")
        print("   --- Archivos de imagenes de graficas *.jpg ---")
        print("**************************************************")
        for g in graficas:
            print("")
            print(g)
  
    def imprimir_muestras_canal(self):

        print(" ")
        print(" En CLASE Graficador::")
        print("**************************************************")
        print("      --- Vectores de muestras por canal ---")
        print("**************************************************")
        # --- ESTRUCTURA del diccionario:
        #     datos = {canal: i, llaveMuestras[i]: vector de datos}
        # ---------------------------------------------------------
        muestras = self.vectores_muestras
        llaves = list(muestras)
        print(" llaves = ",llaves)
        for k in range(len(llaves)):
            print("")
            print(" --- ",llaves[k],": ",muestras[llaves[k]])

    def imprimir_vectores_muestras(self):

        print(" ")
        print(" En CLASE Graficador::")
        print("**************************************************")
        print(" -- Muestras leidas de la Clase Modelo --")
        print("**************************************************")
        muestras = self.vectores_muestras
        llaves = self.titulos_vectores_muestras
        print(" llaves = ",llaves)
        for k in range(len(llaves)):
            print("")
            print(" --- ",llaves[k],": ",muestras[llaves[k]])
