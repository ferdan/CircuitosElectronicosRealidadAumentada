# *************************************
#
#   Clase: --> Graficador 
#   Modulo: -> graficador.py
#
# Descripción:
#   - Graficar los datos obtenidos por arduino
#   - Dibuar, mostrar informacion
#
# Fecha: julio 28/2021
#
# ************************************

from m.calculadora_datos_graficas import Calculadora_datos_graficas

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

    def graficar_curvas_MOSFET(self):

        global graficas
        graficas = []

        muestras = self.vectores_muestras

        muestras_llaves = list(muestras)

        # Son los indices de los canales de muestras recibidos como se difnio en la clase modelo
        ind_voltajes = [0,1,3,4] #Vgg, Vgs, Vdd, Vds
        ind_corrientes = [2,5] # Ig, Id

        # Se obtiene el numero de series de muestras para cada canal (ej. para 300 muestras hay 6 curvas)
        lim_max = len(muestras['Id'])
        #print('lim_max: '+str(lim_max))
        #print('muestras_llaves: '+str(len(muestras_llaves)))

        # Seleccion entre las series de muestras sin filtro, con filtro circuilar o con filtro pasa-bajas
        # 0 = sin filtro
        # 1 = con filtro circular cp
        # 2 = con filtro pasa bajas lp
        
        sel_filtro = 1

        # Ajuste de Id con Rd = 220 ohm y de Ig con Rg = 100 Kohm
        
        for i in range(ind_corrientes[1],lim_max*3,6):
            #print('Serie '+str(muestras_llaves[i])+' por ajustar')
            for j in range(0,lim_max):
                muestras[muestras_llaves[i]][j] = [x / 2200 for x in muestras[muestras_llaves[i]][j]]
                muestras[muestras_llaves[i-3]][j] = [x / 100000 for x in muestras[muestras_llaves[i-3]][j]]
                #print('Serie '+str(muestras_llaves[i])+' ajustada')


        # Se obtienen los parametros lambda, Vth, Kn y gm. 
        calc = Calculadora_datos_graficas(self.modelo,muestras_llaves,lim_max,sel_filtro,ind_corrientes,ind_voltajes)

        Vth, Kn, Idss, ind_ids = calc.calcular_Vth_Kn_Idss()
        linea_lim_x,linea_lim_y,Vgs_prom = calc.calcular_puntos_limite_grafica_ids_vds(Vth)
        MOS_lambdas = calc.calcular_lambda(linea_lim_y)
        MOS_avg_lambda = -(1/statistics.mean(MOS_lambdas))
        #print(MOS_avg_lambda)
        
        gm = [0] * (lim_max-1)
        corrientes_gm = [0] * (lim_max-1)

        for i in range(0,lim_max-1):
            corrientes_gm[i] = muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][i][25]
            gm[i] = 2*math.sqrt(Kn*corrientes_gm[i])

        #print('corriente: '+str(corrientes_gm)+', gm: '+str(gm))

        #print('Parametros Híbridos')
        # --- Parametros adicionales: rg, rd ----------------------------------------------------------------------------------------------------------

        rg = float('inf')
        #print(rg)
        
        rd = [0] * (lim_max-1)
        
        for i in range(0,lim_max-1):
            rd[i] = (1/(MOS_avg_lambda*corrientes_gm[i]))
            #print(rd[i])
        
        # ---------------------------------------------------------------------------------------------------------------------------------------------
        # Algunas referencias que consulte para realizar el codigo, son las siguientes:
        #        
        # Python matplotlib data labels (plt.annotate())
        # https://queirozf.com/entries/add-labels-and-text-to-matplotlib-plots-annotation-examples
        #
        # Python matplotlib change axis limits (see first two answers)
        # https://stackoverflow.com/questions/3777861/setting-y-axis-limit-in-matplotlib
        #
        # Python engineering format (EngNumber())
        # https://pypi.org/project/engineering-notation/
        #
        # Python insert greek symbols
        # https://pythonforundergradengineers.com/unicode-characters-in-python.html
        #
        # Utilizar parentesis en vez de iguales
        # ej. plt.xlabel('Vds (V)')    en vez de     plt.xlabel = 'Vds (V)'
        #
        # Engineering format en axis labels (plt.gca(), EngFormatter(), ax.xaxis.set_major_formatter() y ax.yaxis.set_major_formatter())
        # https://matplotlib.org/stable/gallery/text_labels_and_annotations/engineering_formatter.html
        # https://www.geeksforgeeks.org/formatting-axes-in-python-matplotlib/
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.gca.html
        # ---------------------------------------------------------------------------------------------------------------------------------------------
        
        print('Grafica 0')
        # --- Grafica 0 : Voltajes en el tiempo -------------------------------------------------------------------------------------------------------
        # --- Esta grafica es para observar el comportamiento de los voltajes en el tiempo
        # --- Se observan los voltajes Vgg, Vgs, Vdd, Vds
        plt.figure(0)
        
        ax = plt.gca()
        formatter0 = EngFormatter(unit='V')
        ax.yaxis.set_major_formatter(formatter0)

        for i in ind_voltajes:
            arr = []
            for j in range(0,lim_max):
                arr = arr+muestras[muestras_llaves[i+6*sel_filtro]][j]
            plt.plot(arr, label=muestras_llaves[i+6*sel_filtro])

        plt.xlabel('Muestras')
        plt.ylabel('Voltaje')
        plt.title("Voltajes en el tiempo")
        plt.legend()
        grafica = 'g/00_Voltajes' + ".jpg"
        plt.savefig(grafica)
        graficas.append(grafica)

        print('Grafica 1')
        # --- Grafica 1: Ig vs Vgs --------------------------------------------------------------------------------------------------------------------
        plt.figure(1)
        plt.plot(muestras[muestras_llaves[ind_voltajes[1]+6*sel_filtro]][lim_max-1],muestras[muestras_llaves[ind_corrientes[0]+6*sel_filtro]][lim_max-1], label='Ig vs Vgs')

        ax = plt.gca()
        formatter0 = EngFormatter(unit='A')
        ax.yaxis.set_major_formatter(formatter0)
        formatter0 = EngFormatter(unit='V')
        ax.xaxis.set_major_formatter(formatter0)
        
        x1,x2,y1,y2=plt.axis()
        plt.xlim(0,4)
        plt.ylim(y1-y2*10,y2*1000)
        plt.xlabel('Vgs')
        plt.ylabel('Ig')
        plt.subplots_adjust(left=0.15)
        plt.title("Ig vs Vgs")
        plt.legend()
        grafica = 'g/01_Ig_vs_Vgs' + ".jpg"
        plt.savefig(grafica)
        graficas.append(grafica)

        print('Grafica 2')
        # --- Grafica 2: Id vs Vgs --------------------------------------------------------------------------------------------------------------------
        plt.figure(2)

        ax = plt.gca()
        formatter0 = EngFormatter(unit='A')
        ax.yaxis.set_major_formatter(formatter0)
        formatter0 = EngFormatter(unit='V')
        ax.xaxis.set_major_formatter(formatter0)
        
        plt.plot(muestras[muestras_llaves[ind_voltajes[1]+6*sel_filtro]][lim_max-1][0:ind_ids[len(ind_ids)-1]],muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][lim_max-1][0:ind_ids[len(ind_ids)-1]], label='Id vs Vgs')
        x1,x2,y1,y2=plt.axis()
        plt.axis([0,x2,y1,y2])
        plt.xlabel('Vgs')
        plt.ylabel('Id')
        plt.title("Id vs Vgs")
        plt.legend()
        grafica = 'g/02_Id_vs_Vgs' + ".jpg"
        plt.savefig(grafica)
        graficas.append(grafica)


        print('Grafica 3')
        # --- Grafica 3: Id vs Vds (Cinco curvas) ------------------------------------------------------------------------------------------------------
        plt.figure(3)

        ax = plt.gca()
        formatter0 = EngFormatter(unit='A')
        ax.yaxis.set_major_formatter(formatter0)
        formatter0 = EngFormatter(unit='V')
        ax.xaxis.set_major_formatter(formatter0)
        
        for i in range(0,lim_max-1):
            plt.plot(muestras[muestras_llaves[ind_voltajes[3]+6*sel_filtro]][i],muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][i], label='Vgs = '+str(round(np.average(muestras[muestras_llaves[ind_voltajes[1]+6*sel_filtro]][i]),3)))

        plt.xlabel('Vds')
        plt.ylabel('Id')
        plt.title("Id vs Vds")
        plt.legend()
        grafica = 'g/03_Id_vs_Vds' + ".jpg"
        plt.savefig(grafica)
        graficas.append(grafica)


        print('Grafica 4')
        # --- Grafica 4: gm vs Id ---------------------------------------------------------------------------------------------------------------------
        
        plt.figure(4)

        ax = plt.gca()
        formatter0 = EngFormatter(unit='\u03C3')
        ax.yaxis.set_major_formatter(formatter0)
        formatter0 = EngFormatter(unit='A')
        ax.xaxis.set_major_formatter(formatter0)
        
        plt.plot(corrientes_gm,gm,'o-', label='gm vs Id')
        
        for i in range(0,len(gm)):
            plt.annotate(str(EngNumber(gm[i]))+'\u03C3',(corrientes_gm[i],gm[i]),textcoords="offset points",xytext=(0,10),ha='center')
        x1,x2,y1,y2=plt.axis()
        plt.axis([x1-x1/8,x2+x2/8,y1,y2+y2/16])
        plt.xlabel('Id')
        plt.ylabel('gm')
        plt.title("gm vs Id")
        plt.legend() 
        grafica = 'g/04_gm_vs_Id' + ".jpg"
        plt.savefig(grafica)
        graficas.append(grafica)


        print('Grafica 5')
        # --- Grafica 5: rd vs Id ---------------------------------------------------------------------------------------------------------------------
        
        plt.figure(5)

        ax = plt.gca()
        formatter0 = EngFormatter(unit='\u03A9')
        ax.yaxis.set_major_formatter(formatter0)
        formatter0 = EngFormatter(unit='A')
        ax.xaxis.set_major_formatter(formatter0)
        
        plt.plot(corrientes_gm,rd,'o-', label='rd vs Id')
        for i in range(0,len(rd)):
            plt.annotate(str(EngNumber(rd[i]))+'\u03A9',(corrientes_gm[i],rd[i]),textcoords="offset points",xytext=(0,10),ha='left')
        x1,x2,y1,y2 = plt.axis()
        plt.axis([x1,x2+x2/4,y1,y2+y2/4])
        plt.xlabel('Id')
        plt.ylabel('rd')
        plt.title("rd vs Id")
        plt.legend() 
        grafica = 'g/05_rd_vs_Id' + ".jpg" 
        plt.savefig(grafica)
        graficas.append(grafica)

        print('Grafica 6')
        # --- Grafica 6 Resumen parametros hibridos---------------------------------------------------------------------------------------------------
        
        # --- Generacion de un canvas de w = 240 x h = 180 ---
        canvas2 = np.ones((480,640,3), dtype = "uint8")*255
        
        # --- RECTANGULO ---
        cv2.rectangle(canvas2, (20,20),(620,40),(0,0,0), -1, cv2.LINE_AA)

        # --- RESUMEN PARAMETROS HIBRIDOS ---
        
        cv2.putText(canvas2,"Transistor MOSFET 2N7000", (30, 70),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(canvas2,"PARAMETROS HIBRIDOS", (30, 100),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(canvas2,"Lambda : " + str(EngNumber(MOS_avg_lambda)) + 'V^-1', (30, 130),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(canvas2,"Voltaje de umbral de encendido : " + str(EngNumber(Vth)) + 'V', (30, 150),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(canvas2,"Idss : " + str(EngNumber(Idss)) + 'A', (30, 170),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(canvas2,"Kn : " + str(EngNumber(Kn)) + 'A/V^2', (30, 190),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(canvas2,"rg : " + str(rg), (30, 210),cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 1, cv2.LINE_AA)

        filename = "g/06_parametros_hibridos" + ".jpg"
        cv2.imwrite(filename,canvas2)
        graficas.append(filename)

        # --- Auxiliar para depuracion ---
        #cv2.imshow("Canvas",canvas2)
        #cv2.waitKey(0)
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
