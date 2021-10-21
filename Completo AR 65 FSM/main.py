# *************************************
#
#   PROYECTO de Realidad Aumentada - Version 3.0
#
#   Programa main.py
#
# Descripción:
#   Identifica los marcadores ArUco colocados sobre la imagen
#   de un circuito en protoboard y genera ventanas flotantes
#   ["display" + "graficas"], mostrando la información recibida
#   de ARDUNIO para cada marcador
#
#  Clases de apoyo:
#   MODELO DE PROGRAMACION:  Modelo - Vista - Controlador (aproximacion)
#
#  Fecha: agosto 3/2021
#
# ************************************

import imutils
import cv2

from modelo import Modelo
from controlador import Controlador
from vista import Vista

# *** LECTURA de imagen y ACONDICIONAMIENTO **************************

# --- Proto con marcadores a 10% de su tamaño con marco ---
image = cv2.imread("i/FSM1.jpg")   # Imagen con 4 marcadores

print("")
print("En main:: imagen -> FSM1.jpg")
print("")

# --- Sin importar el tamaño de la imagen, se escala a width = 600 ---
image = imutils.resize(image, width=1000)
# *** FIN de LECTURA de imagen y ACONDICIONAMIENTO *******************


# *** PROGRAMA PRINCIPAL *********************************************

# --- MODELO propuesto para AR ---
model = Modelo(image)
# --- CONTROL de eventos de mouse ---
control = Controlador(image,model)
# --- LOOP infinito ---
vista = Vista(image,control.mse)
# *** FIN de Programa Principal **************************************

cv2.destroyAllWindows()

