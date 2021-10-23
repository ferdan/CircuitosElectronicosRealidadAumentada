# *************************************
#
#   Clase: --> FSM 
#   Modulo: -> FSM.py
#
# Descripción:
#   - Describir la maquina de estados finitos
#
#
# Fecha: julio 26/2021
#
# ************************************

class fsm():
    def __init__(self):
        print("")
        print(" CONSTRUCTOR:  Clase: fsm")

        # Copiar del programa de ARDUINO IMPLEMENTACION FSM todos los datos de la maquina de estados y adaptarlo a la sintaxis de python
        
        # ---------------------------------------------------------------------------------------------------------
        # num_estados -> indica cuantos estados tiene la maquina
        # bits_transicion -> Indica cuantos bits tiene las transiciones que permiten cambiar entre estados
        # bits_salida -> Indica la cantidad de bits de salida de la maquina de estados
        # ---------------------------------------------------------------------------------------------------------

        self.num_estados = 4
        self.bits_transicion = 3
        self.bits_salida = 3
        self.estado_inicial = 0
        self.estado_final = 1

        # ---------------------------------------------------------------------------------------------------------
        # Las siguientes tablas especifican el funcionamiento de la maquina de estados finitos
        # El tamano de estas tablas esta determinador por las constantes num_estados, bits_salida y bits_transicion
        # Cada estado de la maquina corresponde a una entrada de la tabla, como se indica en cada una de las tablas. 
        # 
        # tabla_transiciones_estados -> Indica cuales son las transiciones con las que la maquina cambia de estado
        #                               Las transiciones que no aparecen, se asume que la maquina no cambia de estado
        #                               IMPORTANTE: Se completan la tabla con -1 para las transiciones en las que no hay cambio de estado
        #                               
        # tabla_transiciones_estado_futuro -> Indica el estado al cual va a cambiar la maquina en el siguiente pulso
        #                                     de reloj. Cada estado especificado en esta tabla corresponde a la 
        #                                     transicion de la tabla tabla_transiciones_estados
        #                                     
        # tabla_output_por_estado -> Indica la salida del estado actual de la maquina
        # ---------------------------------------------------------------------------------------------------------

        self.tabla_transiciones_estados = [
                                          [0B100,0B101],                                # estado 0: Apagado
                                          [0B000,0B001,0B010,0B011,0B101,0B111],        # estado 1: Encendido funcionando
                                          [0B000,0B001,0B010,0B011,0B110,0B111],        # estado 2: Corto circuito
                                          [0B000,0B001,0B010,0B011,0B100,0B101]         # estado 3: Reset
                                          ]

        self.tabla_transiciones_estado_futuro = [
                                                [1,1],              # estado 0
                                                [0,0,0,0,2,2],        # estado 1
                                                [0,0,0,0,3,3],      # estado 2
                                                [0,0,0,0,1,2]       # estado 3
                                                ]

        self.tabla_output_por_estado = [
                                       0B000,     # estado 0
                                       0B100,     # estado 1
                                       0B001,     # estado 2
                                       0B011      # estado 3
                                       ]

        self.tabla_nombres_estados = [
                                     'q0 Apagado',
                                     'q1 Encendido funcionando',
                                     'q2 Corto circuito',
                                     'q3 Reset'
                                     ]
        
        self.tabla_nombres_salidas = [
                                     'bit 2: Relevador ON/OFF',
                                     'bit 1: LED de Reset',
                                     'bit 0: LED de Corto circuito'
                                     ]

        self.tabla_nombres_entradas = [
                                      'bit 2: Boton de Alimentacion',
                                      'bit 1: Boton de Reset',
                                      'bit 0: Sensor de Corto Circuito'
                                      ]

