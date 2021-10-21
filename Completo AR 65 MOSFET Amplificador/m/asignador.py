# *************************************
#
#   Clase: --> Asignador 
#   Modulo: -> asignador.py
#
# Descripción:
#   Asigna las ventanas de cada marcador a:
#    1) Graficas realizadas en "matplotlib"
#    2) Texto/Dibujos realizados por el programador
#
# Fecha: abril 10/2021
#
# ************************************

class Asignador:

    # -------------------------------------------------------
    #           CONSTRUCTOR
    # -------------------------------------------------------
    def __init__(self,ventanas,graficas,textoDibujos):

        print("")
        print(" En CLASE Asignador:: CONSTRUCTOR")
        global v    # --- Arreglo "ventanas" ---     
        global g    # --- Arreglo "graficas" ---
        global td   # --- Arreglo "texto-dibujos" ---
        global oa   # --- Arreglo "objetos-asignados" ---
        v = ventanas
        g = graficas
        td = textoDibujos
        oa = []

    def asignar_graficas_ventanas(self):

        print(" ")
        print(" En CLASE Asigandor::")
        print("**************************************************")
        print("    --- Asignacion de graficas a ventanas ---")
        print("**************************************************")
##        v[0].asignar_tipo_grafica(g[0])
##        v[1].asignar_tipo_grafica(g[1])
##        v[2].asignar_tipo_grafica(g[2])
##        v[3].asignar_tipo_grafica(g[3])
        oa.append({'grafica': g[0]})
        oa.append({'grafica': g[1]})
        oa.append({'grafica': g[2]})
        oa.append({'textoDibujo': "informacion"})
        
        for i in range(len(v)):
            v[i].asignar_objeto_ventana(oa[i])

    def asignar_textosDibujos_ventanas(self):

        print(" ")
        print(" En CLASE Asigandor::")
        print("**************************************************")
        print(" --- Asignacion de Textos/Dibujos a ventanas ---")
        print("**************************************************")
        #v[3].asignar_texto_dibujo(g[3])
