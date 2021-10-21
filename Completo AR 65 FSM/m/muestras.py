# *************************************
#
#   Clase: --> Muestras 
#   Modulo: -> muestras.py
#
# Descripción:
#   Solicita el envío de valores capturados por Arduino:
#
# Fecha: junio 8/2021
#
# ************************************

import serial
import collections

from matplotlib.lines import Line2D
from collections import deque

muestras = {}   # Diccionario de muestras: ['{canal': ch, datos: []}]

class Muestras:

    # -------------------------------------------------------
    #           CONSTRUCTOR
    # -------------------------------------------------------
    def __init__(self,conexionSerial,param_muestras):

        self.conexionSerial = conexionSerial
        self.param_muestras = param_muestras
        
        self.inicializar_variables_adquisicion()
        self.inicializar_arreglos_valores()
        if self.iniciar_recepcion_datos():
            # --- Leer datos procedentes de Arduino ---
            self.muestrear_datos_arduino()
            # --- Separar muestras en grupo de 'paquetes de muestras'
            #     Actualizar dicionario 'muestras'
            #-------------------------------------------
            self.separar_muestras_canal()
            # --- Filtrar muestras 'circular' 'lowpass':
            #     Actualizar dicionario 'muestras'
            #-------------------------------------------
            #self.filtrar_muestras_obtenidas()
            
            # --- Imprimir diccionario 'muestras' ---
            #self.imprimir_valores_recibidos()
            #self.imprimir_valores_procesados()

    def inicializar_variables_adquisicion(self):
        
        # -------------------------------------------------------
        #         Definicion de variables de muestreo
        # -------------------------------------------------------
        global numMuestras
        global numCanales
        global llaveMuestras
        global contadorMuestra
        global valores          # Arreglo
        global lineas           # Arreglo
        numMuestras = self.param_muestras['numMuestras'] # Número de numMuestra
        numCanales = self.param_muestras['numCanales']   # Numero de canales (arduino)
        llaveMuestras = self.param_muestras['llave']     # "llave" de las nuestras
        contadorMuestra = numMuestras-1    # Contador de numMuestra
        lineas = []             # Arreglo de lineas de graficación
        valores = []            # Arreglo numCanalesXnumMuestras.
                                # Almacen de valores recibidos tipo COLA
        
    def inicializar_arreglos_valores(self):
        
        # --- Inicializacion con ceros "0" de los vectores de cada canal de
        #     de valores recibidos de Arduino, almacenados en el arragelo "valores[]"
        #     Cantidad de valores por canal: "numMuestra"
        #     Numero de canales: "numCanales"
        # ----------------------------------------------------------------
       for i in range(numCanales):
            valores.append(collections.deque([0]*numMuestras, maxlen = numMuestras))
            lineas.append(Line2D([], [], color='blue'))
            
    def iniciar_recepcion_datos(self):
        
        # --- En est METODO, Python recibe los datos evniados por ARDUINO y
        #     espera hasta recibir la plabra 'inicio', la cual es la clave
        #     para comenzar a recibir datos válidos de ARDUINO
        #     Esto es así porque ARDUINO tiene un BUFFER da datos de transmisión
        #     de aproximadamente 64 bytes de longitud. Puede ser que el buffer
        #     contenga 'basura' de trasnmisiones anteriores y es por ésto,
        #     que este método intenta leer el contendios del buffer hasta 64
        #     veces. Si después de 64 inentos no encuentra la palabra 'inicio'
        #     se reporatrá un problema de NO-SINCRONIZACION con ARDUINO
        # -- --------------------------------------------------------------
        print("")
        print(" En CLASE Muestras:: ")
        print("")
        print("******************************************************")
        print(" --- INICIANDO SINCRONIZACION DE DATOS CON ARDUINO ---")
        print("******************************************************")
        print("")
        numero_maximo_intentos = 64
        inmensaje_recibido_arduino = ""

        contador_intentos = 0
        while (inmensaje_recibido_arduino != b'inicio'):
            inmensaje_recibido_arduino = self.conexionSerial.readline().strip()
            #print(" inmensaje_recibido_arduino = ",inmensaje_recibido_arduino)
            contador_intentos += 1
            #print("     contador_intentos = ",contador_intentos)
            if (contador_intentos >= numero_maximo_intentos):
                print("")
                print(" *** NO ES POSIBLE ESTABLECER UNA COMUNICACION ***")
                print("            SINCRONIZADA CON ARDUINO: ")
                print("      SE EXCDIO EL NUMERO DE INTENTOS -> 64 <-")
                print("**************************************************")
                return False

        print("")
        print("************************************************")
        print(" --- SINCRONIZACION ETABLECIDA CON ARDUINO ---")
        print("************************************************")
        print("")
        return True

    def muestrear_datos_arduino(self):
        
        # --- Recepcion de los valores enviados por Arduino, correspondientes
        #     a cada canal. Almacenados en el arragelo "valores[]"
        #     Cantidad de valores por canal: "numMuestra"
        #     Numero de canales: "numCanales"
        # ----------------------------------------------------------------
        global contadorMuestra
        for n in range(numMuestras):
            self.leer_muestras_arduino(numMuestras,numCanales,
                                       self.conexionSerial, lineas, n)
            contadorMuestra = contadorMuestra -1

    def leer_muestras_arduino(self,numMuestras,numCanales,conexionSerial,
                              lineas,n):
    
        # -----------------------------------------------------
        #     Función de adquisición de valores MULTICANAL
        # -----------------------------------------------------
        for i in range(numCanales):
            # --- Lectura de cada canal de datos enviado por Arduino ---
            valor = float(conexionSerial.readline().strip())
            # --- Guardado de lecturas en la última posicion de datos[i] ---
            valores[i].append(valor)
            # --- Guardado de lineas de graficacion [NO SE USA] ---
            lineas[i].set_data(range(numMuestras),valores[i])
            # --- Imprimir datos recibidos --
            #print(" valores[",i,"][numMuestras]= ",valores[i][numMuestras-1])
            print(" ---> muestra: ",n,"  canal: ",i,"  valor: ",valor)

    def separar_muestras_canal(self):

        paquete_muestras_barrido = 50
        datos = {}  # Diccionario parcial
        
        for i in range(len(valores)):
            renglon = []
            for j in range(len(valores[i])):
                renglon.append(int(1000*valores[i][j])/1000)
            datos = {llaveMuestras[i]: renglon}
            # --- Actualización del Diccionario principal: "muestras"
            muestras.update(datos)
            
            # --- Si el numero de muestras es mayor al tamaño del paquete 
            #     de muestras (50) definido en la Clase Modelo, se procede
            #     a separar las muestras de cada renglon en paquetes de
            #     50 muestras en 'arreglo'
            # ------------------------------------------------------------
            if len(renglon) > paquete_muestras_barrido:
                arreglo = []
                longitud_renglon = len(renglon)
                for j in range(0,int((longitud_renglon/paquete_muestras_barrido))):
                    j_min = paquete_muestras_barrido*j
                    j_max = paquete_muestras_barrido*(j+1) - 1
                    arreglo.append(renglon[j_min:j_max])
                # --- Se catualiza nuevamente el diccionario 'muestras' ---
                datos = {llaveMuestras[i]: arreglo}
                muestras.update(datos)

    def filtrar_muestras_obtenidas(self):

        # --- LLaves actuales del diccionario 'muestras' ---
        llaves = list(muestras)

        # --- FILTRO DE PROMEDIO CIRCULAR ---
        #     'num_muestras_promediar' 
        #     'pc' -> Promedio circular 
        # -----------------------------
        # --- Numero de muestras a promediar en el filtro circular ---
        num_muestras_promediar = 4

        for k in range(len(llaves)):
            # --- Construccion de la nueva 'pc' para el dicionario 'muestras' 
            #     pc = llaves[k] + '_pc'
            # ----------------------------------------------------------------------
            pc = llaves[k] + '_pc'
            # --- Arreglo para el guardado de paquetes de muestras del filtro circular ---
            arreglo = []

            for r in range(len(muestras[llaves[k]])):
                # --- Promediador de datos circular ---
                arreglo.append(self.promediador_datos_circular(muestras[llaves[k]][r],
                                                                     num_muestras_promediar))
            # --- Actualizacion del diccionario 'muestras' 
            muestras.update({pc:arreglo})

        # --- FILTRO PASA BAJAS ---
        #     'alpha' -> Peso asignado al promedio de muestras pasadas 
        #     'lp' -> Filtro Pasa Bajas
        # ------------------------------------------------------------
        # --- Peso asignado al promedio de muestras pasadas ---
        alpha = 0.5

        for k in range(len(llaves)):
            # --- Construccion de la nueva 'pc' para el dicionario 'muestras' 
            #     lp = llaves[k] + '_lp'
            # ----------------------------------------------------------------------
            lp = llaves[k] + '_lp'
            # --- Arreglo para el guardado de paquetes de muestras del filtro circular ---
            arreglo = []

            for r in range(len(muestras[llaves[k]])):
                # --- Promediado y actualizacion del diccionario 'muestras' ---
                arreglo.append(self.promediador_datos_lowpass(muestras[llaves[k]][r],
                                                                     alpha))
            # --- Actualizacion del diccionario 'muestras' 
            muestras.update({lp:arreglo})

    def promediador_datos_circular(self, vector_muestras, numero_muestras_promediar):

        # --- Promediar "vector_muestras" mediante un buffer circular de
        #                  "numero_muestras_promediar"
        # -------------------------------------------------------------
        
        # --- Definicion del buffer on estructura 'FIFO' ---
        buffer = deque(maxlen = numero_muestras_promediar)
        # --- Inicializacion del buffer ---
        for n in range(numero_muestras_promediar):
            buffer.append(vector_muestras[0])
        
        prom = []

        for d in range(len(vector_muestras)):
            buffer.append(vector_muestras[d])
            prom.append(self.promediar_circular(buffer))
        return prom

    def promediar_circular(self,buffer):
        
        suma = 0
        for b in list(buffer):
            suma += b           
        return int(1000*suma/len(buffer))/1000

    def promediador_datos_lowpass(self, vector_muestras, alpha):

        # --- Definicion del vector de salida ---
        prom = []
        # --- Definicion del valor promediado ---
        valor_promediado = vector_muestras[0]
        # --- Generacion del vector promediado ---
        for n in range(len(vector_muestras)):
            valor_promediado = alpha*valor_promediado+(1 - alpha)*vector_muestras[n]
            prom.append(int(1000*valor_promediado)/1000)
        return prom  
    
    @property
    def muestras(self):
        return muestras   # Diccionario

    @property
    def valores(self):
        return valores    # Array
 
    def imprimir_valores_recibidos(self):

        print(" ")
        print(" En CLASE Muestras::")
        print("**************************************************")
        print(" -- Muestras recibidas de Arduino por cada canal --")
        print("**************************************************")
        llaves = list(muestras)
        print(" llaves = ",llaves)
        for k in range(len(llaves)):
            print("")
            print(" --- ",llaves[k],": ",muestras[llaves[k]])

    def imprimir_valores_procesados(self):

        print(" ")
        print(" En CLASE Muestras::")
        print("**************************************************")
        print("    -- Muestras procesadas por cada canal --")
        print("**************************************************")
        llaves = list(muestras)
        print(" llaves = ",llaves)
        for k in range(len(llaves)):
            grupo = 0
            print("")
            print(" === ",llaves[k]," ========================================================")
            for m in muestras[llaves[k]]:
                print("")
                print(" --- ",llaves[k],"[",grupo,"] = ",m)
                grupo += 1

        print(" ")
        print(" En CLASE Muestras::")
        print("**************************************************")
        print("    -- Muestras ACCESADAS COMO ARREGLOS --")
        print("**************************************************")
        for k in range(len(llaves)):
            print("")
            print(" === ",llaves[k]," ========================================================")
            for r in range(len(muestras[llaves[k]])):
                print("")
                print(" --- ",llaves[k],"[",r,"] = ",muestras[llaves[k]][r])
                
                           


            

         
