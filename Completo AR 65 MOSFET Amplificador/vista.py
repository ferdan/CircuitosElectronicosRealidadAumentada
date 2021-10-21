# *************************************
#
# Clase: --> Vista 
# Modulo: -> avista.py
#
# Descripción:
#   Crea un LOOP infinito para:
#       - Generar animación incial: movimientos de ventanas [display]
#       - Estar a la "escucha" de eventos de mouse
#
# Fecha: marzo 30/2021
#
# ************************************

import cv2
import time

class Vista:

    def __init__(self,imagen,eventos_mouse):
        
        print(" CONSTRUCTOR:  Clase: Vista")
        self.img = imagen
        self.evento_mouse = eventos_mouse
        self.delay = 0.02
        self.iniciar_animacion_ventanas()

    def iniciar_animacion_ventanas(self):

        while True:
            img = self.img.copy()
            self.evento_mouse.mover_objetos(img)
            cv2.imshow("Objetos",img)
            time.sleep(self.delay)
            # --- Presionar "ESC" para salir de animacion ---
            if cv2.waitKey(1) == 27:  
                break

        
        
