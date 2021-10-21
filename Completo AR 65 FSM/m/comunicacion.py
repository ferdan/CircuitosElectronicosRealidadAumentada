# *************************************
#
# Clase: --> Comunicación 
# Modulo: -> comunicacion.py
#
# Descripción:
#   Intenta la conexión con ARDUINO a través
#   del puerto Seral USB
#
# Fecha: marzo 25/2021
#
# ************************************

import serial
import time

class Comunicacion:

    # -------------------------------------------------------
    #           CONSTRUCTOR
    # -------------------------------------------------------
    def __init__(self):
        
        self.inicializar_variables_comunicacion()
        

    def inicializar_variables_comunicacion(self):
        # -------------------------------------------------------
        #  Definicion de variables de comunicacion serial (USB)
        # -------------------------------------------------------
        global puertoSerie
        global baudRate
        puertoSerie = 'COM5'    # Puerto serial de conexión con Arduino (USB)
        baudRate = 9600         # Velocidad de transmisión: 9600 baudios

    def iniciar_conexion_arduino(self):
        # ------------------------------------------------------
        #          Manejo del puerto serial (USB)
        # ------------------------------------------------------
        # --- Conexión con el puerto serial asignado a Arduino ---
        print("")
        print(" En CLASE Comunicacion::")
        print(" Comunicacion:: puertoSerie = ",puertoSerie)
        try:
            # Instance serial object
            conexionSerial = serial.Serial(puertoSerie, baudRate, timeout = 1)
            #time.sleep(1)   # (5) Retardo de espera para establecer comunicacion serial
            print("******************************")
            print(" --- CONECTADO CON ARDUINO ---")
            print("******************************")
            return conexionSerial
        except:
            print("******************************")
            print(" FALLO LA CONEXION CON ARDUINO")
            print("******************************")
