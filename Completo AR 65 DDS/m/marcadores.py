# *************************************
#
#   Clase: --> Marcadores 
#   Modulo: -> marcadores.py
#
# Descripción:
#   Identifica los marcadores ArUco colocados sobre la imagen
#   obteniendo las coordenadas de éste y su identificador "id"
#
# Fecha: marzo 25/2021
#
# ************************************

import cv2

# ------------------------------------------------------------
#           Propiedades de la clase Marcadores
# ------------------------------------------------------------
# --- Del diccionario completo de marcadores ArUco, sólo se
#           utiliza el tipo: "DICT_4X4_50" 
ARUCO_DICT = {
	"DICT_4X4_50": cv2.aruco.DICT_4X4_50
}

# --- # Array de diccionarios: {id:(id-10), idm: -, x: -, y: -}] ---
# --- Arreglo de diccionarios asociados a cada marcador ---
diccionario = []

class Marcadores:

    # ------------------------------------------------------------
    #           CONSTRUCTOR
    # ------------------------------------------------------------
    def __init__(self, image):
        
        self.image = image
        # --- Diccionario GLOBAL de marcadores ---
        #self.dg = {}
        self.detectar_marcadores_aruco()
        self.generar_parametros_marcadores()

    def detectar_marcadores_aruco(self):
        
        arucoDict = cv2.aruco.Dictionary_get(ARUCO_DICT["DICT_4X4_50"])
        arucoParams = cv2.aruco.DetectorParameters_create()
        (self.corners, self.ids, self.rejected) = cv2.aruco.detectMarkers(self.image, arucoDict,
            parameters=arucoParams)

    def generar_parametros_marcadores(self):

        if len(self.corners) > 0:
            # flatten the ArUco IDs list
            self.ids = self.ids.flatten()
            
            # --- Loop sobre las esquinas de los marcadores ArUCo detectados ---
            for (markerCorner, markerID) in zip(self.corners, self.ids):
                
                    # extract the marker corners (which are always returned in
                    # top-left, top-right, bottom-right, and bottom-left order)
                    corners = markerCorner.reshape((4, 2))
                    (topLeft, topRight, bottomRight, bottomLeft) = corners
                    # --- Esquinas del 'CUADRADO' alrededor del centro del marcador ---
                    topRight = (int(topRight[0]), int(topRight[1]))
                    bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
                    bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
                    topLeft = (int(topLeft[0]), int(topLeft[1]))                  
                    # --- Coordenadas del centro del marcador ---
                    cX = int((topLeft[0] + bottomRight[0]) / 2.0)
                    cY = int((topLeft[1] + bottomRight[1]) / 2.0)
                    
                    # --- Llenado del dicionario --
                    # --- Array de diccionarios "diccionario" ---
                    cuadrado_marcador = {'topRight': topRight, 'bottomRight': bottomRight,
                                'bottomLeft': bottomLeft, 'topLeft': topLeft}
                    centro_marcador = {'cX':cX, 'cY':cY}
                    diccionario.append({'id':(markerID-10), 'idm':markerID,
                                        'centro_marcador': centro_marcador,
                                        'x':cX, 'y':cY,
                                        'cuadrado_marcador': cuadrado_marcador})

    @property              
    def diccionario(self):
        
        return diccionario

    def dibujar_cuadros_marcadores(self):
        
        for d in diccionario:
            # --- Extraer información del diccionario "diccionario" ---
            topLeft = d['cuadrado_marcador']['topLeft']
            topRight = d['cuadrado_marcador']['topRight']
            bottomLeft = d['cuadrado_marcador']['bottomLeft']
            bottomRight = d['cuadrado_marcador']['bottomRight']
            cX = d['centro_marcador']['cX']
            cY = d['centro_marcador']['cY']
            markerID = d['idm']
            markerID10 = d['id']
            # --- Dibuja una caja alrededor del marcador detectado ---
            cv2.line(self.image, topLeft, topRight, (0, 255, 0), 2)
            cv2.line(self.image, topRight, bottomRight, (0, 255, 0), 2)
            cv2.line(self.image, bottomRight, bottomLeft, (0, 255, 0), 2)
            cv2.line(self.image, bottomLeft, topLeft, (0, 255, 0), 2)
            cv2.circle(self.image, (cX, cY), 4, (0, 0, 255), -1)
            # --- Escribir el "idm" del marcador ---
            cv2.putText(self.image, str(markerID10),
                    (topLeft[0], topLeft[1] - 15), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 2)
       
    def imprimir_diccionario(self):

        print(" ")
        print(" En CLASE Marcadores::")
        print("************************************************")
        print(" Imprimir diccionario --> ")
        print(" Información de los marcadores ArUCo detectados ")
        print("************************************************")
        for d in diccionario:
            print("")
            print(" --- id: ",d['id']," ---")
            print(d)



        
