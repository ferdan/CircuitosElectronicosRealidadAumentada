#----------------------------------------------------------------------------------------
#
#   Clase: --> Calculadora_datos_graficas 
#   Modulo: -> calculadora_datos_graficas.py
#
# Descripción:
#   Auxiliar de graficador.py que calcula los datos de las series de datos de las graficas a mostrar
#
# Fecha: julio 28/2021
#
# ************************************

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
import math
import statistics

class Calculadora_datos_graficas:
    # -------------------------------------------------------
    #           CONSTRUCTOR
    # -------------------------------------------------------
    def __init__(self,modelo,muestras_llaves,lim_max,sel_filtro,ind_corrientes,ind_voltajes):

        print("")
        print(" CONSTRUCTOR:  Clase: Calculadora_datos_graficas")
        self.modelo = modelo
        self.muestras = modelo.vectores_muestras
        self.muestras_llaves = muestras_llaves
        self.lim_max = lim_max
        self.sel_filtro = sel_filtro
        self.ind_corrientes = ind_corrientes
        self.ind_voltajes = ind_voltajes


    # -------------------------------------------------------
    # Calcula los coeficientes b0 y b1 del método de regresión lineal simple
    # Tomado de https://www.geeksforgeeks.org/linear-regression-python-implementation/
    # -------------------------------------------------------
    def estimate_coef(self, x, y):
        # number of observations/points
        n = np.size(x)
     
        # mean of x and y vector
        m_x = np.mean(x)
        m_y = np.mean(y)
     
        # calculating cross-deviation and deviation about x
        SS_xy = np.sum(y*x) - n*m_y*m_x
        SS_xx = np.sum(x*x) - n*m_x*m_x
     
        # calculating regression coefficients
        b_1 = SS_xy / SS_xx
        b_0 = m_y - b_1*m_x
     
        return (b_0, b_1)

    # -------------------------------------------------------
    # Grafica el resultado de la regresión lineal simple
    # Tomado de https://www.geeksforgeeks.org/linear-regression-python-implementation/
    # -------------------------------------------------------
    def plot_regression_line(self, x, y, b):
        # plotting the actual points as scatter plot
        plt.scatter(x, y, color = "m",
                   marker = "o", s = 30)
     
        # predicted response vector
        y_pred = b[0] + b[1]*x
     
        # plotting the regression line
        plt.plot(x, y_pred, color = "g")
     
        # putting labels
        plt.xlabel('x')
        plt.ylabel('y')
     
        # function to show plot
        plt.show()

    # -------------------------------------------------------
    # Construye las series de datos de las diferentes curvas Id vs Vds (ej. Id1, Vd1, Id2, Vds2, Id3, Vds3 ...)
    #
    # -------------------------------------------------------
    def construir_series_datos(self):
        
        muestras = self.muestras
        ind_variables = self.ind_variables
        writer = self.inicializar_excel_datos()
        
        valores_id_vds = {i:[] for i in ind_variables}

        #print(ind_variables)
        #print('\n')
        #print(valores_id_vds)

        for i in range(0,int(len(ind_variables)),2):
            i_min = 50*int(i/2)
            i_max = 50*(int(i/2)+1)
            
            #print('valores_id_vds['+str(ind_variables[i])+'] = muestras[Id]['+str(i_min)+':'+str(i_max)+']')
            #print('valores_id_vds['+str(ind_variables[i+1])+'] = muestras[Vds]['+str(i_min)+':'+str(i_max)+']')
            
            valores_id_vds[ind_variables[i]] = muestras['Id'][i_min:i_max]
            valores_id_vds[ind_variables[i+1]] = muestras['Vds'][i_min:i_max]

            self.guardar_datos_excel(writer,ind_variables[i+1],ind_variables[i],valores_id_vds[ind_variables[i]],valores_id_vds[ind_variables[i+1]])
            #print(valores_id_vds[ind_variables[i]])
            #print(valores_id_vds[ind_variables[i+1]])
            #print('\n')

        self.finalizar_excel_datos(writer)

        return valores_id_vds

    # -------------------------------------------------------
    # Obtiene el límite mínimo en donde se considera recta la parte de la curva correspondiente Id# vs Vds# a partir de los valores de corriente Id
    # Esto es la primera muestra cuya diferencia con la anterior es menor a 0.06 y que el índice de esa muestra sea mayor a la muestra número 2
    # -------------------------------------------------------
    def obtener_ind_min(self,ind_serie_datos):
        muestras = self.muestras
        muestras_llaves = self.muestras_llaves
        sel_filtro = self.sel_filtro
        ind_corrientes = self.ind_corrientes
        
        ind_min = 0;
        id_cambio = [x for x in range(0,len(muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][ind_serie_datos]))]

        for i in range(1,30):
            id_cambio[i] = muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][ind_serie_datos][i] - muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][ind_serie_datos][i-1]
            #print('i='+str(i)+': '+str(muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][ind_serie_datos][i])+' - '+str(muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][ind_serie_datos][i-1])+' = '+str(id_cambio[i]))
            #print('i: '+str(i)+', '+str(id_cambio[i])+': '+str(id_cambio[i] < 0.06))
            if id_cambio[i] < (0.06)/1000 :
                #print('i: '+str(i)+', '+str(id_cambio[i])+': '+str(id_cambio[i] < 0.06))
                if i > (2+int(ind_serie_datos/2)+1) :
                    ind_min = i
                    break
        
        #print('ind_min: id_cambio['+str(ind_min)+']: '+str(id_cambio[ind_min]))
        
        return ind_min

    # -------------------------------------------------------
    # Obtiene el límite máximo en donde se considera recta la parte de la curva correspondiente Id# vs Vds# a partir de los valores de voltaje Vds
    # Esto es la primera muestra cuya diferencia con la anterior es mayor a 0.05 y que el índice de esa muestra sea mayor a la muestra número 20
    # -------------------------------------------------------
    def obtener_ind_max(self,ind_serie_datos,ind_min):
        muestras = self.muestras
        muestras_llaves = self.muestras_llaves
        sel_filtro = self.sel_filtro
        ind_voltajes = self.ind_voltajes
        
        ind_max = len(muestras[muestras_llaves[ind_voltajes[3]+6*sel_filtro]][ind_serie_datos])-2
        vds_cambio = [x for x in range(0,len(muestras[muestras_llaves[ind_voltajes[3]+6*sel_filtro]][ind_serie_datos]))]
        #print('Vds_cambio len: '+str(len(vds_cambio)))
        for i in range(20,len(muestras[muestras_llaves[ind_voltajes[3]+6*sel_filtro]][ind_serie_datos])):
            vds_cambio[i] = muestras[muestras_llaves[ind_voltajes[3]+6*sel_filtro]][ind_serie_datos][i] - muestras[muestras_llaves[ind_voltajes[3]+6*sel_filtro]][ind_serie_datos][i-1]
            #print('i='+str(i)+': '+str(muestras[muestras_llaves[ind_voltajes[3]+6*sel_filtro]][ind_serie_datos][i])+' - '+str(muestras[muestras_llaves[ind_voltajes[3]+6*sel_filtro]][ind_serie_datos][i-1])+' = '+str(vds_cambio[i]))
            #print('i: '+str(i)+', '+str(vds_cambio[i])+': '+str(vds_cambio[i] < 0.06))
            if vds_cambio[i] < 0.05 :
                #print('i: '+str(i)+', '+str(vds_cambio[i])+': '+str(vds_cambio[i] < 0.05))
                if i > ind_min :
                    ind_max = i-1
                    break

        #print('ind_max: vds_cambio['+str(ind_max)+']: '+str(vds_cambio[ind_max]))
        
        return ind_max

    # -------------------------------------------------------
    # Funcion que obtiene lambda para un transistor mosfet
    # Tomado de https://www.geeksforgeeks.org/linear-regression-python-implementation/
    # -------------------------------------------------------
    def regresion_lineal_lambda(self, ind_serie_datos, ind_min, ind_max):
        muestras = self.muestras
        muestras_llaves = self.muestras_llaves
        sel_filtro = self.sel_filtro
        ind_corrientes = self.ind_corrientes
        ind_voltajes = self.ind_voltajes
        
        #print(valores_id_vds[ind_variables[ind_serie_datos+1]][ind_min:ind_max])
        #print(valores_id_vds[ind_variables[ind_serie_datos]][ind_min:ind_max])
        
        x = np.array(muestras[muestras_llaves[ind_voltajes[3]+6*sel_filtro]][ind_serie_datos][ind_min:ind_max]).reshape(-1)
        y = np.array(muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][ind_serie_datos][ind_min:ind_max]).reshape(-1)

        #print(x)
        #print(y)

        b = self.estimate_coef(x,y)
        #print("Estimated coefficients: b_0 = {}  b_1 = {}".format(b[0], b[1]))
        #plot_regression_line(x, y, b)
        
        return -b[0] / b[1]

    # --- Para depuracion
    # -------------------------------------------------------
    # Inicializa la escritura de datos en Excel
    # 
    # -------------------------------------------------------
    def inicializar_excel_datos(self):
        writer = pd.ExcelWriter('mediciones_promedio.xlsx', engine='xlsxwriter')
        return writer

    # -------------------------------------------------------
    # Guarda los valores de Id y Vds en Excel en Excel
    # 
    # -------------------------------------------------------
    def guardar_datos_excel(self,writer, nombre_hoja_id, nombre_hoja_vds, corrienteId, voltajeVds):
        muestras_seriesId = pd.Series(corrienteId)
        muestras_seriesVds = pd.Series(voltajeVds)
        
        muestras_seriesId.to_excel(writer, sheet_name=nombre_hoja_id)
        muestras_seriesVds.to_excel(writer, sheet_name=nombre_hoja_vds)

    # -------------------------------------------------------
    # Finaliza la escritura de datos de Excel
    # 
    # -------------------------------------------------------
    def finalizar_excel_datos(self,writer):
        writer.save()

    # -------------------------------------------------------
    # Lee datos de Excel
    # 
    # -------------------------------------------------------
    def leer_datos_excel(self,ind_variables, i):
        df = pd.read_excel (r'C:\Users\ferda\Desktop\Material del profe 100421\3 Sistema Completo Realidad Aumentada\AR_multiples_graficas_Fernando_120421\Completo AR 20\mediciones_promedio_10.xlsx', sheet_name=ind_variables[i], usecols=[ind_variables[i]])
        return df

    #----------------------------------------------------------------------------------------
    # -------------------------------------------------------
    # FUNCION PRINCIPAL que calcula lambda de un transistor mos
    # Obtiene primero los índices mínimos y máximos en donde se considera "recta" a la curva Id vs Vds
    # Calcula lambda para esa curva
    # Obtiene el promedio de todas las lambdas calculadas
    # -------------------------------------------------------
    def calcular_lambda(self,linea_lim_y):

        MOSFET_lambdas = []
        muestras = self.muestras
        lim_max = self.lim_max
        muestras_llaves = self.muestras_llaves
        sel_filtro = self.sel_filtro
        ind_corrientes = self.ind_corrientes
        ind_voltajes = self.ind_voltajes
        
        #valores_id_vds = self.construir_series_datos()

        # Depuracion con datos leidos de excel
        '''
        for i in range(1,6):
            ind_variables.append('Id'+str(i))
            ind_variables.append('Vds'+str(i))
        
        for i in range(len(ind_variables)):
            df = self.leer_datos_excel(ind_variables, i)
            valores_id_vds[ind_variables[i]] = df.values'''

        ind_min = 0
        ind_max = 0
        #print(valores)
        #print(valores['Id1'][0])

        for [ind_serie_datos,i] in zip(range(0,lim_max-1),range(1,lim_max)):
            #print('Id'+str(ind_serie_datos)+', '+'Vds'+str(ind_serie_datos))
            #print('muestras[Id][ind_serie_datos]: '+str(len(muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][ind_serie_datos]))+', '+'muestras[Vds][ind_serie_datos]): '+str(len(muestras[muestras_llaves[ind_voltajes[3]+6*sel_filtro]][ind_serie_datos])))
            #print('Id'+str(ind_serie_datos)+': ')
            #print(muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][ind_serie_datos])
            #print('Vds'+str(ind_serie_datos)+': ')
            #print(muestras[muestras_llaves[ind_voltajes[3]+6*sel_filtro]][ind_serie_datos])

            ind_min = muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][ind_serie_datos].index(linea_lim_y[i])
            #ind_min = self.obtener_ind_min(ind_serie_datos)
            print('ind_min: '+str(ind_min)+': '+'Id'+str(ind_serie_datos)+', '+str(muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][ind_serie_datos][ind_min]))
            
            ind_max = self.obtener_ind_max(ind_serie_datos,ind_min)
            print('ind_max: '+str(ind_max)+': '+'Vds'+str(ind_serie_datos)+', '+str(muestras[muestras_llaves[ind_voltajes[3]+6*sel_filtro]][ind_serie_datos][ind_max]))
            
            MOSFET_lambdas.append(self.regresion_lineal_lambda(ind_serie_datos, ind_min, ind_max))
            print('lambda: '+str(MOSFET_lambdas[ind_serie_datos])+'\n')
        
        print('lambda_promedio: '+str(statistics.mean(MOSFET_lambdas)))
        #return statistics.mean(MOSFET_lambdas)
        return MOSFET_lambdas

    # -------------------------------------------------------
    # Calcula los parametros Vth, Kn e Idss del transistor MOSFETT
    # Ademas, calcula los indices de ids-vgs que se utilizaron para calcular estos parametros (Vth,Kn,Idss)
    # -------------------------------------------------------
    def calcular_Vth_Kn_Idss(self):
        muestras = self.muestras
        muestras_llaves = self.muestras_llaves
        sel_filtro = self.sel_filtro
        lim_max = self.lim_max
        ind_corrientes = self.ind_corrientes
        ind_voltajes = self.ind_voltajes

        # --- Se calcula la maxima variacion de ids, entre muestras adyacentes ---
        ind_ids = []
        delta_ids = [0]*50
        for i in range(1,50-1):
            delta_ids[i] = muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][lim_max-1][i] - muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][lim_max-1][i-1]
            #delta_vgs = muestras[muestras_llaves[ind_voltajes[1]+6*sel_filtro]][lim_max-1][i] - muestras[muestras_llaves[ind_voltajes[1]+6*sel_filtro]][lim_max-1][i-1]
            #print('['+str(i)+']' 'delta_ids: '+str(delta_ids[i]))#+', delta_vgs: '+str(delta_vgs))

        # --- Se identifica el indice de la maxima variacion y el indice anterior a esta muestra --- 
        ids_max = np.max(delta_ids)
        ind_ids.append(delta_ids.index(ids_max)-1)
        ind_ids.append(delta_ids.index(ids_max))
        #print('ind_ids: '+str(ind_ids))

        # --- Se calcula la diferencia de vgs y de ids, con los indices anteriores ---
        vgs_1 = muestras[muestras_llaves[ind_voltajes[1]+6*sel_filtro]][lim_max-1][ind_ids[0]]
        vgs_2 = muestras[muestras_llaves[ind_voltajes[1]+6*sel_filtro]][lim_max-1][ind_ids[len(ind_ids)-1]]
        ids_1 = muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][lim_max-1][ind_ids[0]]
        ids_2 = muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][lim_max-1][ind_ids[len(ind_ids)-1]]

        #print('ids_1: '+str(ids_1))
        #print('ids_2: '+str(ids_2))
        #print('vgs_1: '+str(vgs_1))
        #print('vgs_2: '+str(vgs_2))

        # --- Se calcula vth, kn e idss ---
        Vth = (vgs_1-vgs_2*math.sqrt((ids_1)/(ids_2)))/(1-math.sqrt((ids_1)/(ids_2)))
        Kn = (ids_1)/((vgs_1-Vth)**2)
        Idss = Kn * Vth**2
        
        print('Vth_calculado: '+str(Vth))
        print('Kn_calculada: '+str(Kn))
        print('Idss_calculada: '+str(Idss))
        
        return (Vth, Kn, Idss, ind_ids)
    
    '''def calcular_vth(self, lim_max):
        Vth = 0
        muestras = self.muestras
        muestras_llaves = self.muestras_llaves
        sel_filtro = self.sel_filtro
        ind_corrientes = self.ind_corrientes
        ind_voltajes = self.ind_voltajes
        
        for i in range(0,50):
            if muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][lim_max-1][i] > 0.0001 and muestras[muestras_llaves[ind_voltajes[1]+6*sel_filtro]][lim_max-1][i] > 1.7:
                Vth = muestras[muestras_llaves[ind_voltajes[1]+6*sel_filtro]][lim_max-1][i-1]
                print('Vth calculado = '+str(Vth))
                return Vth
        return 0
            
    def calcular_kn(self, Idss, Vth):
        return Idss/(Vth**2)'''
    # -------------------------------------------------------
    # Calcula los puntos a graficar sobre las curvas vds-ids
    # Se calcula la posicion de la curva que delimita las regiones ohmica y de saturacion de un transistor MOSFET
    # Regresa tambien el valor promedio vgs al cual se grafico esa curva
    # -------------------------------------------------------
    def calcular_puntos_limite_grafica_ids_vds(self, Vth):
        muestras = self.muestras
        muestras_llaves = self.muestras_llaves
        sel_filtro = self.sel_filtro
        ind_corrientes = self.ind_corrientes
        ind_voltajes = self.ind_voltajes
        num_curvas_id_vds = [0,1,2,3,4]
        
        linea_lim_x = [0] * (len(num_curvas_id_vds)+1)
        linea_lim_y = [0] * (len(num_curvas_id_vds)+1)
        Vgs_prom = [0] * (len(num_curvas_id_vds))

        # --- Se calcula la posicion de los puntos que delimitan las regiones de operacion sobre el conjunto de curvas ids-vds ---
        for i in num_curvas_id_vds:
            Vgs_prom[i] = round(np.average(muestras[muestras_llaves[ind_voltajes[1]+6*sel_filtro]][i]),3)
            # --- Se obtiene el voltaje de saturacion vds_sat ---
            linea_lim_x[i+1] = Vgs_prom[i]-Vth
            for j in range(0,len(muestras[muestras_llaves[ind_voltajes[3]+6*sel_filtro]][i])):
                if abs((Vgs_prom[i]-Vth) - muestras[muestras_llaves[ind_voltajes[3]+6*sel_filtro]][i][j]) < 0.05:
                    # --- Se obtiene la muestra mas cercana de ids correspondiente al voltaje vds_sat ---
                    linea_lim_y[i+1] = muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][i][j]
                    #print('lim_curva_'+str(i)+' (temp):  '+str(linea_lim_x[i+1])+'V,'+str(linea_lim_y[i+1])+'A, dif='+str(abs((Vgs_prom-Vth) - muestras[muestras_llaves[ind_voltajes[3]+6*sel_filtro]][i][j])/220))
            print('lim_curva_'+str(i)+': '+str(linea_lim_x[i+1])+'V,'+str(linea_lim_y[i+1])+'A')

        return (linea_lim_x,linea_lim_y,Vgs_prom)
