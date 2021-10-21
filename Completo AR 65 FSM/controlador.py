# *************************************
#
# Clase: --> Controlador 
# Modulo: -> controlador.py
#
# Descripción:
#   Control de eventos de mouse para Realidad Aumentada
#
# Fecha: marzo 30/2021
#
# *************************************

import cv2
from c.eventomouse import EventoMouse

class Controlador:

    # -------------------------------------------------------
    #           CONSTRUCTOR
    # -------------------------------------------------------
    def __init__(self,imagen,modelo):

        print(" CONSTRUCTOR: Clase: Controlador")
        self.image = imagen
        self.modelo = modelo
        self.inicializar_objetos_controlador()
        
    def inicializar_objetos_controlador(self):

        # --- 8 - Manejo de Eventos de mouse ---
        mse = EventoMouse(self.image,self.modelo.ventanas)
        self.mouseEvent = mse
        cv2.namedWindow('Objetos')
        cv2.setMouseCallback('Objetos',mse.onMouse)

    @property
    def mse(self):
        return self.mouseEvent
