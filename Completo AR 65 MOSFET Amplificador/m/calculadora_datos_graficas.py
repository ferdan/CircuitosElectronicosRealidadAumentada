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
import math
import statistics
from engineering_notation import EngNumber

class Calculadora_datos_graficas:
    # -------------------------------------------------------
    #           CONSTRUCTOR
    # -------------------------------------------------------
    def __init__(self,modelo,muestras_llaves,lim_max,sel_filtro,ind_corrientes,ind_voltajes,num_curvas_id_vds,num_curvas_parametros,num_curvas_pequena_senal,Rd,Rg):

        print("")
        print(" CONSTRUCTOR:  Clase: Calculadora_datos_graficas")
        self.modelo = modelo
        self.muestras = modelo.vectores_muestras
        self.muestras_llaves = muestras_llaves
        self.lim_max = lim_max
        self.sel_filtro = sel_filtro
        self.ind_corrientes = ind_corrientes
        self.ind_voltajes = ind_voltajes
        self.num_curvas_id_vds = num_curvas_id_vds
        self.num_curvas_parametros = num_curvas_parametros
        self.num_curvas_pequena_senal = num_curvas_pequena_senal
        self.Rd = Rd
        self.Rg = Rg

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
        Rd = self.Rd
        
        ind_min=0;
        id_cambio = [x for x in range(0,len(muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][ind_serie_datos]))]

        for i in range(1,30):
            id_cambio[i] = muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][ind_serie_datos][i] - muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][ind_serie_datos][i-1]
            #print('i='+str(i)+': '+str(muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][ind_serie_datos][i])+' - '+str(muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][ind_serie_datos][i-1])+' = '+str(id_cambio[i]))
            #print('i: '+str(i)+', '+str(id_cambio[i])+': '+str(id_cambio[i] < 0.06))
            if id_cambio[i] < (0.06)/Rd :
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
        
        ind_max=len(muestras[muestras_llaves[ind_voltajes[3]+6*sel_filtro]][ind_serie_datos])-1
        vds_cambio = [x for x in range(0,len(muestras[muestras_llaves[ind_voltajes[3]+6*sel_filtro]][ind_serie_datos]))]
        #print('Vds_cambio len: '+str(len(vds_cambio)))
        for i in range(20,len(muestras[muestras_llaves[ind_voltajes[3]+6*sel_filtro]][ind_serie_datos])):
            vds_cambio[i] = muestras[muestras_llaves[ind_voltajes[3]+6*sel_filtro]][ind_serie_datos][i] - muestras[muestras_llaves[ind_voltajes[3]+6*sel_filtro]][ind_serie_datos][i-1]
            #print('i='+str(i)+': '+str(muestras[muestras_llaves[ind_voltajes[3]+6*sel_filtro]][ind_serie_datos][i])+' - '+str(muestras[muestras_llaves[ind_voltajes[3]+6*sel_filtro]][ind_serie_datos][i-1])+' = '+str(vds_cambio[i]))
            #print('i: '+str(i)+', '+str(vds_cambio[i])+': '+str(vds_cambio[i] < 0.06))
            if vds_cambio[i] <= 0.05 :
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
        num_curvas_id_vds = self.num_curvas_id_vds
        
        #valores_id_vds = self.construir_series_datos()

        # Depuracion con datos leidos de excel
        '''
        for i in range(1,6):
            ind_variables.append('Id'+str(i))
            ind_variables.append('Vds'+str(i))
        
        for i in range(len(ind_variables)):
            df = self.leer_datos_excel(ind_variables, i)
            valores_id_vds[ind_variables[i]] = df.values'''

        ind_min = []
        ind_max = []
        
        #print(valores)
        #print(valores['Id1'][0])
        # --- Calculo de lambda para cada curva ids-vds
        for [ind_serie_datos,i] in zip(num_curvas_id_vds,range(1,len(num_curvas_id_vds)+1)):
            #print('Id'+str(ind_serie_datos)+', '+'Vds'+str(ind_serie_datos))
            #print('muestras[Id][ind_serie_datos]: '+str(len(muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][ind_serie_datos]))+', '+'muestras[Vds][ind_serie_datos]): '+str(len(muestras[muestras_llaves[ind_voltajes[3]+6*sel_filtro]][ind_serie_datos])))
            #print('Id'+str(ind_serie_datos)+': ')
            #print(muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][ind_serie_datos])
            #print('Vds'+str(ind_serie_datos)+': ')
            #print(muestras[muestras_llaves[ind_voltajes[3]+6*sel_filtro]][ind_serie_datos])

            # --- Calculo de indice minimo y maximo para despues realizar regresion lineal y obtener la interseccion con el eje de vds negativo. El resultado es lambda ---

            ind_min.append(muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][ind_serie_datos].index(linea_lim_y[i]))
            print('ind_min: '+str(ind_min[len(ind_min)-1])+': '+'Id'+str(ind_serie_datos)+', '+str(muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][ind_serie_datos][ind_min[len(ind_min)-1]]))
            
            ind_max.append(self.obtener_ind_max(ind_serie_datos,ind_min[len(ind_min)-1]))
            print('ind_max: '+str(ind_max[len(ind_max)-1])+': '+'Vds'+str(ind_serie_datos)+', '+str(muestras[muestras_llaves[ind_voltajes[3]+6*sel_filtro]][ind_serie_datos][ind_max[len(ind_max)-1]]))
            
            MOSFET_lambdas.append(self.regresion_lineal_lambda(ind_serie_datos, ind_min[len(ind_min)-1], ind_max[len(ind_max)-1]))
            print('lambda: '+str(MOSFET_lambdas[ind_serie_datos])+'\n')
        
        print('lambda_promedio: '+str(statistics.mean(MOSFET_lambdas)))
        #return statistics.mean(MOSFET_lambdas)
        return ind_min,ind_max,MOSFET_lambdas

    # -------------------------------------------------------
    # Calcula los parametros Vth, Kn e Idss del transistor MOSFETT
    # Ademas, calcula los indices de ids-vgs que se utilizaron para calcular estos parametros (Vth,Kn,Idss)
    # -------------------------------------------------------
    def calcular_Vth_Kn_Idss(self):
        muestras = self.muestras
        muestras_llaves = self.muestras_llaves
        sel_filtro = self.sel_filtro
        ind_corrientes = self.ind_corrientes
        ind_voltajes = self.ind_voltajes
        num_curvas_parametros = self.num_curvas_parametros

        # --- Se calcula la maxima variacion de ids, entre muestras adyacentes ---
        ind_ids = []
        delta_ids = [0]*50
        for i in range(1,50-1):
            delta_ids[i] = muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][num_curvas_parametros[0]][i] - muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][num_curvas_parametros[0]][i-1]
            #delta_vgs = muestras[muestras_llaves[ind_voltajes[1]+6*sel_filtro]][num_curvas_parametros[0]][i] - muestras[muestras_llaves[ind_voltajes[1]+6*sel_filtro]][num_curvas_parametros[0]][i-1]
            #print('['+str(i)+']' 'delta_ids: '+str(delta_ids[i]))#+', delta_vgs: '+str(delta_vgs))

        # --- Se identifica el indice de la maxima variacion y el indice anterior a esta muestra --- 
        ids_max = np.max(delta_ids)
        ind_ids.append(delta_ids.index(ids_max)-1)
        ind_ids.append(delta_ids.index(ids_max))
        #print('ind_ids: '+str(ind_ids))

        # --- Se calcula la diferencia de vgs y de ids, con los indices anteriores ---
        vgs_1 = muestras[muestras_llaves[ind_voltajes[1]+6*sel_filtro]][num_curvas_parametros[0]][ind_ids[0]]
        vgs_2 = muestras[muestras_llaves[ind_voltajes[1]+6*sel_filtro]][num_curvas_parametros[0]][ind_ids[len(ind_ids)-1]]
        ids_1 = muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][num_curvas_parametros[0]][ind_ids[0]]
        ids_2 = muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][num_curvas_parametros[0]][ind_ids[len(ind_ids)-1]]

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

    # -------------------------------------------------------
    # Ajusta el valor de todas las corrientes, puesto que solo son una diferencia de voltajes (ej. Id=Vdd-Vds ; Ig=Vgg-Vgs)
    # 
    # -------------------------------------------------------   
    def ajustar_id_con_resistencias(self):
        muestras = self.muestras
        muestras_llaves = self.muestras_llaves
        ind_corrientes = self.ind_corrientes
        lim_max = self.lim_max
        Rd = self.Rd
        Rg = self.Rg
        
        for i in range(ind_corrientes[1],lim_max*3,6):
            #print('Serie '+str(muestras_llaves[i])+' por ajustar')
            for j in range(0,lim_max):
                muestras[muestras_llaves[i]][j] = [x / Rd for x in muestras[muestras_llaves[i]][j]]
                muestras[muestras_llaves[i-3]][j] = [x / Rg for x in muestras[muestras_llaves[i-3]][j]]
                #print('Serie '+str(muestras_llaves[i])+' ajustada')

    # -------------------------------------------------------
    # Calcula gm a partir de Kn para cada curva ids-vds
    # Ademas, regresa los calores de corrientes utilizados para cada calculo de gm
    # -------------------------------------------------------
    def calcular_gm(self, Kn):
        muestras = self.muestras
        muestras_llaves = self.muestras_llaves
        sel_filtro = self.sel_filtro
        ind_corrientes = self.ind_corrientes
        num_curvas_id_vds = self.num_curvas_id_vds
        
        gm = [0] * len(num_curvas_id_vds)
        corrientes_gm = [0] * len(num_curvas_id_vds)

        # --- Se calcula gm para cada corriente elegida del conjunto de curvas ids-vds ---
        for i in num_curvas_id_vds:
            corrientes_gm[i] = muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][i][25]
            gm[i] = 2*math.sqrt(Kn*corrientes_gm[i])

        return (gm,corrientes_gm)

    # -------------------------------------------------------
    # Calcula las resistencias rg y rd del modelo hibrido pi del transistor MOSFET
    # 
    # -------------------------------------------------------
    def calcular_resistencias_hibridas(self,MOS_avg_lambda,corrientes_gm):
        num_curvas_id_vds = self.num_curvas_id_vds
        
        rg = float('inf')
        print('rg: '+str(rg))
        
        rd = [0] * len(num_curvas_id_vds)

        # --- Se calcula rd para cada conjunto de curvas ids-vds ---
        for i in num_curvas_id_vds:
            rd[i] = (1/(MOS_avg_lambda*corrientes_gm[i]))
            #print(rd[i])
        print('rd: '+str(rd))
        return (rd,rg)

    # -------------------------------------------------------
    # Calcula los puntos a graficar sobre las curvas vgs-ids
    # Calcula la posicion de tres puntos: vth y dos puntos utilizados para calcular Kn,Vth y Idss
    # -------------------------------------------------------
    def puntos_sobre_grafica_ids_vgs(self, Vth, ind_ids):
        muestras = self.muestras
        muestras_llaves = self.muestras_llaves
        sel_filtro = self.sel_filtro
        ind_corrientes = self.ind_corrientes
        ind_voltajes = self.ind_voltajes
        num_curvas_parametros = self.num_curvas_parametros
        
        markers_on = []

        # --- Se obtiene el indice mas cercano al valor Vth previamente calculado ---
        for i in range(0,50):
            if Vth - muestras[muestras_llaves[ind_voltajes[1]+6*sel_filtro]][num_curvas_parametros[0]][i] <= 0:
                ind_vth = i
                break
        # --- Se arma el arreglo con los tres puntos a graficar sobre la curva ids-vgs ---
        markers_on.append(ind_vth)
        markers_on.append(ind_ids[0])
        markers_on.append(ind_ids[len(ind_ids)-1])

        vgs = []*len(markers_on)
        ids = []*len(markers_on)
        
        print('markers_on: '+str(markers_on))#, ' 1: '+str(markers_on[0]))
        #print('len(markers_on): '+str(len(markers_on)))

        # --- Se obtienen las coordenadas de los puntos anteriores (vgs,ids)--- 
        for (i,j) in zip(markers_on,range(0,len(markers_on))):
            vgs.append(muestras[muestras_llaves[ind_voltajes[1]+6*sel_filtro]][num_curvas_parametros[0]][i])
            ids.append(muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][num_curvas_parametros[0]][i])
            #print('vgs: '+str(vgs[int(j)]))
            #print('ids: '+str(ids[int(j)]))

        return (vgs, ids, markers_on)

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
        num_curvas_id_vds = self.num_curvas_id_vds
        
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

    # -------------------------------------------------------
    # Calcula todos los parametros del punto de operacion del transistor MOSFET cuando funciona como amplificador de pequna senal
    # Calcula Vrd Id gm rd rlac=(Rd||rd) en el punto de operacion (v_op,i_op)
    # Calcula tambien la ganancia teorica esperada
    # -------------------------------------------------------
    def calcular_punto_operacion_y_parametros_hibridos(self,Kn,MOS_avg_lambda):
        muestras = self.muestras
        muestras_llaves = self.muestras_llaves
        sel_filtro = self.sel_filtro
        ind_corrientes = self.ind_corrientes
        ind_voltajes = self.ind_voltajes
        num_curvas_pequena_senal = self.num_curvas_pequena_senal
        Rd = self.Rd

        # --- Se obtiene el punto de operacion del amplificador. Es la primera muestra del conjunto de curvas para pequena senal ---
        v_op = muestras[muestras_llaves[ind_voltajes[3]+6*sel_filtro]][num_curvas_pequena_senal[0]][0]
        i_op = muestras[muestras_llaves[ind_corrientes[1]+6*sel_filtro]][num_curvas_pequena_senal[0]][0]
        print('v_op: '+str(v_op))
        print('i_op: '+str(i_op))

        # --- Se calculan los parametros hibridos en el punto de operacion ---
        Vrdq = muestras[muestras_llaves[ind_voltajes[2]+6*sel_filtro]][num_curvas_pequena_senal[0]][0] - v_op
        Idq = Vrdq/Rd
        gmq = 2*math.sqrt(Kn*Idq)
        rdq = 1/(MOS_avg_lambda*Idq)
        Rlac = 1/((1/Rd)+(1/rdq))
        ganancia_teorica = -gmq*Rlac
        return (v_op,i_op,Vrdq,Idq,gmq,rdq,Rlac,ganancia_teorica)

    # -------------------------------------------------------
    # Calcula la ganancia experimental (vout/vin) de acuerdo a la curva de voltajes en el tiempo cuando el transistor MOSFET funciona como amplificador en pequena senal
    # Regresa tambien los indices correspondientes a los minimos y maximos de las senales de entrada y de salida
    # -------------------------------------------------------
    def calcular_punto_operacion_puntos_min_max_ganancia_experimental(self):
        muestras = self.muestras
        muestras_llaves = self.muestras_llaves
        sel_filtro = self.sel_filtro
        ind_voltajes = self.ind_voltajes
        num_curvas_pequena_senal = self.num_curvas_pequena_senal
        
        v_max_ind = [0]*2
        v_min_ind = [0]*2
        v_max = [0]*2
        v_min = [0]*2
        v_pp = [0]*2
        marker_v = []

        # --- Se calculan los voltajes maximos y minimos de las senales de entrada (vgs) y salida (vds) ---
        for i in [0,1]:
            v_max[i] = np.max(muestras[muestras_llaves[ind_voltajes[1+i*2]+6*sel_filtro]][num_curvas_pequena_senal[0]])
            v_min[i] = np.min(muestras[muestras_llaves[ind_voltajes[1+i*2]+6*sel_filtro]][num_curvas_pequena_senal[0]])

            v_max_ind[i] = muestras[muestras_llaves[ind_voltajes[1+i*2]+6*sel_filtro]][num_curvas_pequena_senal[0]].index(v_max[i])
            v_min_ind[i] = muestras[muestras_llaves[ind_voltajes[1+i*2]+6*sel_filtro]][num_curvas_pequena_senal[0]].index(v_min[i])

            v_pp[i] = v_max[i] - v_min[i]
            
            marker_v.append(v_min_ind[i])
            marker_v.append(v_max_ind[i])

        # --- Se calcula la ganancia experimental como vout/vin ---
        ganancia_experimental = -v_pp[1]/v_pp[0]
        print('ganancia_experimental: '+str(ganancia_experimental))
        
        return (ganancia_experimental,marker_v)

    # -------------------------------------------------------
    # Calcula la posicion de los puntos que delimitan las regiones de operacion sobre las curvas ids-vds
    # Calcula las ecuaciones de la recta de carga estatica y de la parabola que delimita las regiones de operacion del transistor MOSFET
    # Calcula tambien la posicion del punto de operacion sobre la recta de carga estatica
    # Calcula tambien la posicion del punto de maxima variacion simetrica sobre la recta de carga y otras intersecciones
    # -------------------------------------------------------
    def calcular_puntos_limite_y_operacion_sobre_grafica_ids_vds(self,x,y,v_op,i_op):
        muestras = self.muestras
        muestras_llaves = self.muestras_llaves
        sel_filtro = self.sel_filtro
        ind_voltajes = self.ind_voltajes
        num_curvas_pequena_senal = self.num_curvas_pequena_senal
        Rd = self.Rd

        # --- Se hace regresion polinomial al conjunto de puntos que indican el limite entre regiones de operacion ---
        # --- Se observo que una curva de 3er grado predice acertadamente el comportamiento de este conjunto de puntos ---
        parabola_vsat = np.poly1d(np.polyfit(x, y, 3))
        print('parabola inicial: \n'+str(np.poly1d(parabola_vsat)))

        # --- Se resta la ecuacion de la recta de carga estatica a la parabola, esto es restar los coeficientes de los terminos independiente y x (x^2 y x^3 permanecen intactos) ---
        vdd_prom = sum(muestras[muestras_llaves[ind_voltajes[2]+6*sel_filtro]][num_curvas_pequena_senal[0]]) / len(muestras[muestras_llaves[ind_voltajes[2]+6*sel_filtro]][num_curvas_pequena_senal[0]])
        print('vdd_prom: '+str(vdd_prom))
        parabola_vsat[0] = parabola_vsat[0]-(vdd_prom/Rd)
        parabola_vsat[1] = parabola_vsat[1]-(-1/Rd)
        # --- Se obtienen las raices o soluciones de esta ecuacion de 3er grado. Estas soluciones son las intersecciones entre la curva que delimita regiones y la recta de carga estatica ---
        print('intersecciones: \n'+str(parabola_vsat.r))

        interseccion = []

        # --- Las raices validas para este problema (calcular el punto de la maxima variacion simetrica) son las no complejas y positivas ---
        for i in parabola_vsat.r:
            if not np.iscomplex(i) and i>=0:
                interseccion.append(i)
        print('intersecciones reales: '+str(interseccion))

        # --- Se restaura la ecuacion de la curva, puesto que fue modificada anteriormente ---
        parabola_vsat = np.poly1d(np.polyfit(x, y, 3))
        #print('parabola sin modificadar: '+str(np.poly1d(parabola_vsat)))

        # --- Se calcula la ecuacion de la recta estatica ---
        puntos_grafica = np.linspace(0,vdd_prom, 50)
        recta_carga_estatica = np.polynomial.polynomial.Polynomial([vdd_prom/Rd,-1/Rd])

        # --- Se convierten las intersecciones de numeros numpy complejos a numeros python flotantes ---
        inters = np.real(interseccion[0].item())

        # --- Se calcula el punto de la maxima variacion simetrica ---
        v_sim_max = ((vdd_prom - inters) / 2) + inters

        print('Punto de maxima variacion simetrica: '+str(EngNumber(v_sim_max))+'V, '+str(EngNumber(recta_carga_estatica(v_sim_max))))

        # --- Se arma el arreglo de estos tres puntos: punto de operacion, interseccion entre la curva que delimita regiones y la recta estatica y el punto de la maxima variacion simetrica ---
        puntos_x = [v_op,inters,v_sim_max]
        puntos_y = [i_op,recta_carga_estatica(inters),recta_carga_estatica(v_sim_max)]

        return (recta_carga_estatica,parabola_vsat,puntos_x,puntos_y,puntos_grafica)

    # -------------------------------------------------------
    # Calcula la posicion de las etiquetas cuando la forma de onda es una senoidal
    # 
    # -------------------------------------------------------
    def calcular_posiciones_label(self,ind_serie,ind_muestra):
        muestras = self.muestras
        muestras_llaves = self.muestras_llaves
        num_curvas_pequena_senal = self.num_curvas_pequena_senal
        
        position = ''
        xoffset = 0
        yoffset = 0

        # --- Determina la mejor posicion de la etiqueta de datos con respecto al cuadrante de la senal senoidal ---
        if muestras[muestras_llaves[ind_serie]][num_curvas_pequena_senal[0]][ind_muestra] > muestras[muestras_llaves[ind_serie]][num_curvas_pequena_senal[0]][0]:
            if (muestras[muestras_llaves[ind_serie]][num_curvas_pequena_senal[0]][ind_muestra] - muestras[muestras_llaves[ind_serie]][num_curvas_pequena_senal[0]][ind_muestra-1]) < 0:
                #print('mod1')
                position = 'left'
                xoffset = 0
                yoffset = 0
            else:
                #print('mod2')
                position = 'right'
                xoffset = -5
                yoffset = 3
        else:
            if (muestras[muestras_llaves[ind_serie]][num_curvas_pequena_senal[0]][ind_muestra-1] - muestras[muestras_llaves[ind_serie]][num_curvas_pequena_senal[0]][ind_muestra]) < 0:
                #print('mod3')
                position = 'left'
                xoffset = 0
                yoffset = 0
            else:
                #print('mod4')
                position = 'right'
                xoffset = -5
                yoffset = -10

        return (xoffset,yoffset)
