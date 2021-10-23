# *************************************
#
# Clase: --> Modelo 
# Modulo: -> modelo.py
#
# Descripción:
#   Genera el modelo utilizado para Realidad Aumentada
#
#   Clases de apoyo:
#
#       - Clase: Comunicación <-- Comunicacion Serial con ARDUINO
#       - Clase: Muestras     <-- Lectura de muestras procedentes de ARDUINO
#       - Clase: Marcadores   <-- Detección de marcadores ArUco
#       - Clase: Clasificador <-- Clasificador de marcadores
#       - Clase: Display      <-- Genera "ventanas" para cada marcador [display+grafica]
#       - Clase: Graficador   <-- Genera las gráficas para cada marcador
#
# Fecha: julio 28/2021
#
# ************************************

import imutils

from m.comunicacion import Comunicacion
from m.muestras import Muestras
from m.marcadores import Marcadores
from m.clasificador import Clasificador
from m.graficador import Graficador
from m.display import Display as disp
from m.asignador import Asignador

ventanas = []
vectores_muestras = {}
titulos_vectores_muestras = {}
titulos_marcadores_display = {}
graficas = []

class Modelo:

    # -------------------------------------------------------
    #           CONSTRUCTOR
    # -------------------------------------------------------
    def __init__(self,imagen):

        print(" CONSTRUCTOR: Clase: Modelo")
        self.image = imagen
        self.inicializar_objetos_modelo()

    def inicializar_objetos_modelo(self):

        h, w, channels = self.image.shape
        print(" Modelo: --> self.image.shape = ",self.image.shape)

        # --- 1 - Comunicacion con ARDUINO ---
        arduino = Comunicacion()
        conexionSerial = arduino.iniciar_conexion_arduino()

        # --- 2 - Lectura de valores enviados por ARDUINO
        global titulos_vectores_muestras
        #titulos_vectores_muestras = ["A0","A1","A2","A3"]
        titulos_vectores_muestras = ["Vgg","Vgs","Ig","Vdd","Vds","Id"]
        param_muestras = {'numMuestras': 300, 'numCanales': len(titulos_vectores_muestras),
                          'llave': titulos_vectores_muestras}
        muestras = Muestras(conexionSerial,param_muestras)
        global vectores_muestras
        vectores_muestras = muestras.muestras
        # --- Imprimir diccionario 'muestras' ---
        #muestras.imprimir_valores_recibidos()
        #muestras.imprimir_valores_procesados()

        # --- 3 - Manejo de marcadores ArUco ---
        aruco = Marcadores(self.image)
        #aruco.dibujar_cuadros_marcadores()
        # --- Imprimir dicionario ---
        #aruco.imprimir_diccionario()
        # --- diccionario --> Arreglo de marcadores ArUco ---
        diccionario = aruco.diccionario

        # --- 4 - Clasificar marcadores ArUCo ---
        # --- Constantes DISPLAY: Estructura de Datos ---
        parametros_display = {
            'ancho_display':  240, # AUTOMATICO
            'alto_display':   30,
            'h_gap_display':   5,
            'offset_x':        5, # 65 Offset en X debido al movimiento 'easing'
            'v_gap_display':   5,
            'offset':         20,
            'alto_imagen':     h,
            'ancho_imagen':    w,
            }
        c = Clasificador(diccionario,parametros_display)
        diccionario = c.diccionario
        # --- Imprimir diccionario ---
        #c.imprimir_diccionario()

        # --- 5 - Manejo de ventanas: display + gráfica ---
        global ventanas
        global titulos_marcadores_display
        titulos_marcadores_display = {'m0': "Voltajes",
                              'm1': "Ig vs Vgs",
                              'm2': "Id vs Vgs",
                              'm3': "Id vs Vds",
                              'm4': "gm vs Id",
                              'm5': "rd vs Id",
                              'm6': "Parametros hibridos"}
        
        # --- Titulos MARCADORES ---
        print("")
        print(" list(titulos_marcadores_display): ",list(titulos_marcadores_display))

        for i in range(len(diccionario)):
            # --- Crear Display --
            ventana = disp(self,self.image,diccionario[i],
                           titulos_marcadores_display,parametros_display)
            ventanas.append(ventana)
            
        # --- 6 - Genera graficas con muestras leidas ---
        graf = Graficador(self)

        # --- Trazador de curvas para MOSFET: 2N7000
        #     En el programa de ARDUINO se debe seleccionar:
        #     'Transistor = false'
        # -------------------------------------------------------
        graf.graficar_curvas_MOSFET()    # 8 marcadores y 8 graficas

        # --- Servicios de impresion ---
        #graf.imprimir_archivos_graficas()
        #graf.imprimir_muestras_canal()
        #graf.imprimir_vectores_muestras()

        # --- Obtener graficas ---
        global graficas
        graficas = graf.graficas

        # --- 7 - Asgignar gráficas a cada ventana ---
        for i in range(len(ventanas)):
            ventanas[i].asignar_imagen_sobrepuesta(graf.graficas[i])

    def solicitud_permiso_usoAreaImagen(self,canal):
        
        # --- Se activa desde la clase Display 
        #     metodo:  actualizar_imagen_display(self,img)
        # ------------------------------------------------------------------
        for v in ventanas:
            if v.diccionario['id'] == canal:
                v.permitir_ocupar_areaImagen = True
            else:
                v.permitir_abrir_ventana = False
                v.permitir_ocupar_areaImagen = False

    def solicitud_liberar_usoAreaImagen(self):

        # --- Se activa desde la clase Display 
        #     metodo:  actualizar_imagen_display(self,img)
        # ------------------------------------------------------------------
        for v in ventanas:
            v.permitir_abrir_ventana = True
            v.permitir_ocupar_areaImagen = True

    @property
    def ventanas(self):
        return ventanas

    @property
    def vectores_muestras(self):
        return vectores_muestras

    @property
    def titulos_vectores_muestras(self):
        return titulos_vectores_muestras

    @property
    def titulos_marcadores_display(self):
        return titulos_marcadores_display

    @property
    def graficas(self):
        return graficas
