# *************************************
#
# Clase: --> EventoMouse 
# Modulo: -> eventomouse.py
#
# Descripción:
#   Manejo de eventos de mouse: onMouse
#       - Boton izquierdo ABAJO
#       - Mover mouse
#       - Boton izquierdo ARRIBA
#
# Fecha: marzo 30/2021
#
# ************************************

import cv2

class EventoMouse:

    def __init__(self,imagen,ventanas):
        
        print(" CONSTRUCTOR:  Clase: Mouse")
        self.img = imagen
        self.ventanas = ventanas
        self.inicializar_parametros_mouse()

    def inicializar_parametros_mouse(self):
        
        self.mouseX = 0
        self.mouseY = 0

    def mover_objetos(self,imagen):
        
        for ventana in self.ventanas:
            ventana.move_springing_posicion()
            ventana.actualizar_imagen_display(imagen)
            if ventana.switch_inicio == 1:
                ventana.programar_secuencia_inicial()
                  
    def onMouse(self, event, x, y, flags, param):
        
        global dist_x, dist_y
        # --- Boton izquierdo presionado ---
        if event == cv2.EVENT_LBUTTONDOWN:
            print("*******************************")
            print(" En Clase: EventoMouse")
            print('x = %d, y = %d'%(x, y))
            print("*******************************")
            self.mouseX = x
            self.mouseY = y
            for ventana in self.ventanas:
                ventana.posicionar_ventana_mouse(self.mouseX,self.mouseY)
                if ventana.permitir_abrir_ventana:                
                    ventana.mouse_sobre_controlesVentana(self.mouseX,self.mouseY)

                          
