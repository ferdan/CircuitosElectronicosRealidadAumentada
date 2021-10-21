# *************************************
#
#   Clase: --> Graficador 
#   Modulo: -> graficador.py
#
# Descripción:
#   - Graficar los datos obtenidos por arduino
#   - Dibuar, mostrar informacion
#   - Calcular algunos parametros
#
# Fecha: julio 28/2021
#
# ************************************

import numpy as np
import cv2

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import EngFormatter

from collections import deque

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

    def graficar_curvas_DDS(self):

        global graficas
        graficas = []

        muestras = self.vectores_muestras
        titulos_vectores_muestras = self.titulos_vectores_muestras
        muestras_llaves = list(muestras)
        lim_max = len(muestras[muestras_llaves[0]])
        sel_filtro = 1

        # ------------------------------------------------------------
        # Useful links:
        # Mark some points on data:
        # https://stackoverflow.com/questions/8409095/set-markers-for-individual-points-on-a-line-in-matplotlib
        # ------------------------------------------------------------
        
        # --- Grafica 0 : Voltaje y binario 1 ---
        plt.figure(0)
        
        ax = plt.gca()
        formatter0 = EngFormatter(unit='V')
        ax.yaxis.set_major_formatter(formatter0)

        plt.subplot(2, 1, 1)
        plt.title("Voltaje en el tiempo")
        plt.plot(muestras['Voltaje'][0], label='Voltaje')
        plt.ylabel('Voltaje')
        
        plt.subplot(2, 1, 2)
        plt.plot(muestras['Binario'][0], label='Binario')
        plt.xlabel('Muestras')
        plt.ylabel('Binario')

        plt.legend()
        grafica = 'g/00_Voltaje_Binario_1' + ".jpg"
        plt.savefig(grafica)
        graficas.append(grafica)

        # --- Grafica 1 : Voltaje y binario 2 ---
        # --- Generacion de un canvas de w = 240 x h = 180 ---
        canvas2 = np.ones((480,640,3), dtype = "uint8")*255
        
        # --- RECTANGULO ---
        cv2.rectangle(canvas2, (20,20),(620,40),(0,0,0), -1, cv2.LINE_AA)

        # --- Estados binarios ---
        
        cv2.putText(canvas2,"Tabla de estados binarios. Circuito DDS con PCF8591", (30, 70),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(canvas2,"Numero binario (0-255)", (30, 100),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(canvas2,"Voltaje ", (250, 100),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)

        # Generar tabla de valores voltaje-binario
        for i in range(0,50,4):
            cv2.putText(canvas2,hex(int(muestras['Binario'][0][i])), (30, 100+(int(i/4)+1)*20),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(canvas2,str(muestras['Voltaje'][0][i]), (250, 100+(int(i/4)+1)*20),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)

        filename = "g/01_Voltaje_Binario_2" + ".jpg"
        cv2.imwrite(filename,canvas2)
        graficas.append(filename)

        # --- Grafica 2 : Voltaje y binario 3 ---
        plt.figure(2)
        ax = plt.gca()
        formatter0 = EngFormatter(unit='V')
        ax.yaxis.set_major_formatter(formatter0)
        plt.title("Voltajes en el tiempo")

        # Generar arreglo con indices de muestras a marcar
        markers_on = []
        for i in range(0,len(muestras['Voltaje'][0]),4):
            markers_on.append(  i)
        #print('markers_on=' +str(markers_on))
        plt.plot(muestras['Voltaje'][0],'o-', markevery=markers_on, label='Voltaje')

        # Colocar la etiqueta correspondiente segun se comporte la grafica
        for i in range(1,len(muestras['Voltaje'][0]),4):
            position = ''
            xoffset = 0
            yoffset = 0
            if muestras['Voltaje'][0][i] > 2.5:
                if (muestras['Voltaje'][0][i] - muestras['Voltaje'][0][i-1]) < 0:
                    #print('mod1')
                    position = 'left'
                    xoffset = 0
                    yoffset = 0
                else:
                    #print('mod2')
                    position = 'right'
                    xoffset = -12
                    yoffset = 0
            else:
                if (muestras['Voltaje'][0][i-1] - muestras['Voltaje'][0][i]) < 0:
                    #print('mod3')
                    position = 'left'
                    xoffset = 0
                    yoffset = 0
                else:
                    #print('mod4')
                    position = 'right'
                    xoffset = -10
                    yoffset = -10

            plt.annotate(str(muestras['Voltaje'][0][i-1])+'V, '+hex(int(muestras['Binario'][0][i])),(i,muestras['Voltaje'][0][i-1]),textcoords="offset points",xytext=(xoffset,yoffset),ha=position)
        
        x1,x2,y1,y2=plt.axis()
        plt.axis([-10,x2+3*x2/8,y1,5.5])
        plt.ylabel('Voltaje')
        plt.xlabel('Muestras')
        plt.legend(['Voltaje, Binario'])
        grafica = 'g/02_Voltaje_Binario_3' + ".jpg"
        plt.savefig(grafica)
        graficas.append(grafica)

        # --- Grafica 3 : Voltaje y binario 4 ---
        # --- Generacion de un canvas de w = 240 x h = 180 ---
        canvas2 = np.ones((480,640,3), dtype = "uint8")*255
        
        # --- RECTANGULO ---
        cv2.rectangle(canvas2, (20,20),(620,40),(0,0,0), -1, cv2.LINE_AA)

        # --- Estados binarios ---
        
        cv2.putText(canvas2,"Diagrama de numeros binarios con valores de voltaje analogicos", (30, 35),cv2.FONT_HERSHEY_SIMPLEX,0.5, (255, 255, 255), 1, cv2.LINE_AA)
        #cv2.circle(canvas2, (320,260), 215,(255,0,0),2)
        #cv2.circle(canvas2, (320,260), 185,(255,0,0),2)

        angle = np.linspace(0,2*math.pi,16)

        # Dibuja cada uno de los circulos y la informacion voltaje-binario que va dentro de ella. Tambien dibuja las flechas entre circulos
        for i in range(0,15):
            # Dibuja el circulo            
            xcoor = int(320+185*math.cos(angle[i]))
            ycoor = int(260+185*math.sin(angle[i]))
            cv2.circle(canvas2, (xcoor,ycoor), 30, (0,0,0), 2)
            cv2.putText(canvas2,hex(int((muestras['Binario'][0][int((50/16)*i)]))),(xcoor-22,ycoor-5),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(canvas2,str(muestras['Voltaje'][0][int((50/16)*i)])+'V',(xcoor-22,ycoor+15),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)

            # Encuentra las coordenadas de la flecha entre dos circulos
            i1 = self.get_intersections(320,260,185,xcoor,ycoor,30)
            i2 = self.get_intersections(320,260,185,int(320+185*math.cos(angle[i+1])),int(260+185*math.sin(angle[i+1])),30)
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
            # Se puede comprobar con el codigo comentado que esta es la solucion que proporciona las coordenadas correctas
            flecha_coords[0] = i1[2]
            flecha_coords[1] = i1[3]
            flecha_coords[2] = i2[0]
            flecha_coords[3] = i2[1]
            
            #print('coordenadas de la flecha: '+str(flecha_coords))
            #print('distancia: '+str(dist))

            # Dibuja la flecha
            canvas2 = cv2.arrowedLine(canvas2,(int(flecha_coords[0]),int(flecha_coords[1])),(int(flecha_coords[2]),int(flecha_coords[3])),(0,0,0), 3, tipLength = 0.5)

        filename = "g/03_Voltaje_Binario_4" + ".jpg"
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

    # -------------------------------------------------------
    # Obtiene las intersecciones dadas dos circunferencias, coordenadas de su centro y radio. 
    # Tomado de https://stackoverflow.com/questions/55816902/finding-the-intersection-of-two-circles
    # -------------------------------------------------------
    def get_intersections(self, x0, y0, r0, x1, y1, r1):
        # circle 1: (x0, y0), radius r0
        # circle 2: (x1, y1), radius r1

        d = math.sqrt((x1-x0)**2 + (y1-y0)**2)
        
        # non intersecting
        if d > r0 + r1 :
            return None
        # One circle within other
        if d < abs(r0-r1):
            return None
        # coincident circles
        if d == 0 and r0 == r1:
            return None
        else:
            a=(r0**2-r1**2+d**2)/(2*d)
            h=math.sqrt(r0**2-a**2)
            x2=x0+a*(x1-x0)/d   
            y2=y0+a*(y1-y0)/d   
            x3=x2+h*(y1-y0)/d     
            y3=y2-h*(x1-x0)/d 

            x4=x2-h*(y1-y0)/d
            y4=y2+h*(x1-x0)/d
            
            return (x3, y3, x4, y4)
