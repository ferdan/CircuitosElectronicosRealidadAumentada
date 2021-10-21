# *************************************
#
#   Clase: --> Clasifiador 
#   Modulo: -> clasificador.py
#
# Descripción:
#   Clasifica los marcadores de aceurdo a los siguientes criterios:
#    1) En funcion de su coordenada 'x' (ascendente)
#    2) En fucnionn de su coordenada 'y' (ascendente)
#
# Fecha: marzo 27/2021
#
# ************************************

# --- Arreglo de diccionarios asociados a cada marcador ---
diccionario = []

class Clasificador:

    # -------------------------------------------------------
    #           CONSTRUCTOR
    # -------------------------------------------------------
    def __init__(self,datos_diccionario,parametros_display):

        global diccionario
        print("")
        print(" En CLASE Clasificador::")
        print("**************************************************")
        print("CLASE : Clasificador:  CONSTRUCTOR 1 ")
        
        diccionario = datos_diccionario
        self.parametros_display = parametros_display
        self.diccionarioA = {}   # Informacion de marcadores actualizado

        self.ajustar_rectangulo_marcador()
        self.clasificar_marcadores_x()
        self.clasificar_marcadores_y()
        self.clasificar_marcadores_canal()

    def ajustar_rectangulo_marcador(self):

        #*** Calculo Automático para colocar 4 DISPLAYS en linea ***
        w = self.parametros_display['ancho_imagen']
        w_4 = int(w/4)
        ancho_display = w_4 - 10
        self.parametros_display['ancho_display'] = ancho_display
        #************************************************************

        # --- Agrgar a 'diccionario' las coordenadas (superior-izquierda)
        # del 'rectangulo' que ocupará el 'display azul' sobre la imagen
        for d in diccionario:
            esquina_supizq_x = int(d['centro_marcador']['cX'] -
                                   self.parametros_display['ancho_display']/2)
            esquina_supizq_y = int(d['centro_marcador']['cY'] -
                                   self.parametros_display['alto_display']/2)
            d['rectangulo_marcador'] = {'x': esquina_supizq_x,
                                        'y': esquina_supizq_y}

    def clasificar_marcadores_x(self):
        
        # --- Clasificacion en función de la coordenada 'x' ascendente ---
        self.diccionarioA = sorted(diccionario, key = lambda ele: ele['x'])
        
        # --- Agregar a diccionario: 'posicion_x' ---
        #     'posicion_x' es la coordenada que le corresponde al marcador
        #      sobre la imagen
        # ----------------------------------------------------------------
        i = 0
        columna = 0
        for d in self.diccionarioA:
            # --- Calculo de las coordenadas correspondientes a los marcadores
            #     en función de si hay mas de 4 marcadores en la parte superior,
            #     entonces se colocarán en la parte inferior de la imagen
            # -----------------------------------------------------------------
            residuo = i%2
            if not(residuo):
                posicion_x = (self.parametros_display['ancho_display']
                              + self.parametros_display['h_gap_display'])*columna
                + self.parametros_display['offset']
                d['posicion_x'] = posicion_x
                d['posicion_renglon'] = {'x': posicion_x
                                         + self.parametros_display['h_gap_display'],
                                         'y': self.parametros_display['v_gap_display']}
                d['ventana'] = "inferior" # --- Abrir ventana hacia abajo ---
            else:
                posicion_x = (self.parametros_display['ancho_display']
                              + self.parametros_display['h_gap_display'])*columna
                + self.parametros_display['offset']
                d['posicion_x'] = posicion_x
                d['posicion_renglon'] = {'x': posicion_x
                                         + self.parametros_display['h_gap_display'],
                                         'y': self.parametros_display['alto_imagen']
                                         - self.parametros_display['alto_display']
                                         - self.parametros_display['v_gap_display']}
                d['ventana'] = "superior" # --- Abrir ventana hacia arriba ---
            if residuo:
                columna += 1
            i += 1

    def clasificar_marcadores_y(self):

        # --- Clasificacion en función de la coordenada 'y' ascendente ---
        self.diccionarioA = sorted(diccionario, key = lambda ele: ele['y'])
        
        # --- Agregar a diccionario: 'posicion_y' ---
        #     'posicion_y' es la coordenada que le corresponde al marcador
        #      sobre la imagen
        # ----------------------------------------------------------------
        i = 0
        for d in self.diccionarioA:
            posicion_y = (self.parametros_display['alto_display']
                          + self.parametros_display['v_gap_display'])*i
            + self.parametros_display['offset']
            d['posicion_y'] = posicion_y
            d['posicion_columna'] = {'x': self.parametros_display['offset_x'],
                                     'y': posicion_y}
            i += 1

    def clasificar_marcadores_idm(self):

        # --- Clasificacion en función de la coordenada 'idm' ascendente ---
        global diccionario
        diccionario = sorted(diccionario, key = lambda ele: ele['idm'])

    def clasificar_marcadores_canal(self):

        # --- Clasificacion en función del canal de datos 'id' ascendente ---
        global diccionario
        diccionario = sorted(diccionario, key = lambda ele: ele['id'])

    @property
    def diccionario(self):
        return diccionario

    def imprimir_diccionario(self):

        print(" ")
        print(" En CLASE Clasificador::")
        print("************************************************")
        print(" Imprimir diccionario --> ")
        print("       Información del Diccionario ")
        print("************************************************")
        for d in diccionario:
            print("")
            print(" --- id: ",d['id']," ---")
            print(d)

