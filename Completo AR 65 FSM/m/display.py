# *************************************
#
#   Clase: --> Display 
#   Modulo: -> display.py
#
# Descripción:
#   Genera los cuadros de display de texto y sus
#   areas de graficacion respectiva
#
# Fecha: marzo 27/2021
#
# ************************************

import cv2
import time
import imutils

# ------------------------------------------------------------
#           Propiedades de la clase Display
# ------------------------------------------------------------

# self.dicionario <- 'diccionario' del Arreglo de "dicionarios por cada marcador"

# --- Estructura del diccionario ---------------------------------------
#
#     Cada MARCADOR tiene asociado el siguiente 'diccionario' (ejemplo numerico)
#     {'id': 10,
#      'id': 20,
#      'centro_marcador': {'cX': 382, 'cY': 354},
#      'x': 382, 'y': 354,
#      'cuadrado_marcador': {'topRight': (369, 341), 'bottomRight': (397, 341),
#                            'bottomLeft': (396, 369), 'topLeft': (368, 368)},
#      'rectangulo_marcador': {'x': 777, 'y': 165},
#      'posicion_x': 0,
#      'posicion_renglon': {'x': 5, 'y': 528},
#      'ventana': 'superior',
#      'posicion_y': 140,
#      'posicion_columna': {'x': 65, 'y': 140}}
# ----------------------------------------------------------------------

x_inicial = 5
y_inicial = 5

easing = 0.05 # 0.2
spring = 0.1
friction = 0.7 #0.95

x_velocity = 0
y_velocity = 0

class Display:
    
    def __init__(self, modelo, image, datos_diccionario,
                 titulos_marcadores, parametros_display):

        self.modelo = modelo
        
        self.diccionario = datos_diccionario
        
        self.image = image
        h, w, channels = image.shape
        self.screen_width = w
        self.screen_height = h
        
        self.titulos_marcadores = titulos_marcadores
        self.pd = parametros_display
        
        self.x = self.diccionario['x']
        self.y = self.diccionario['y']
        self.centrar_display_marcador()
        self.inicializar_parametros()

    def centrar_display_marcador(self):
        self.esquina_x = int(self.diccionario['x'] - self.pd['ancho_display']/2)
        self.esquina_y = int(self.diccionario['y'] - self.pd['alto_display']/2)

    def inicializar_parametros(self):

        self.flag_abrirVentanaDisplay = False
        self.flag_abrirVentanaDisplay_MAXIMO = False
        
        self.x = 5
        self.y = 5
        self.ancho_display = self.pd['ancho_display']
        self.alto_display = self.pd['alto_display']
        self.targetX = self.esquina_x   # spring -> traget 'x'
        self.targetY = self.esquina_y   # spring -> target 'y'
        self.x_velocity = 0             # spring -> velocidad 'x'
        self.y_velocity = 0             # spring -> velocidad 'y'
        self.color = (255,0,0)          # Azul oscuro
        
        self.secuenciador = 0           # Secuenciador
        self.flag = 1                   # Secuenciador
        self.switch_inicio = 1          # Secuenciador

        self.permitir_ocupar_areaImagen = True  # Manejo del Area de Imagen para:
        self.permitir_abrir_ventana = True  # Manejo de ventanas de informacion
        self.posicion_estable = True        # Manejo de ventanas de informacion

    def asignar_imagen_sobrepuesta(self,img):

        self.imagen = cv2.imread(img)
        self.h0, self.w0 = self.imagen.shape[:2]
        # --------------------------------------------------------------
        #    img2 --> Imagen superpuesta a mostrar en tamaño DISPLAY 
        # --------------------------------------------------------------
        self.img2 = imutils.resize(cv2.imread(img),self.pd['ancho_display'])
        h2, w2 = self.img2.shape[:2]
        self.himg2 = h2
        self.wimg2 = w2

        # --------------------------------------------------------------
        #    img3 --> Imagen superpuesta a mostrar en tamaño MAXIMO 
        # --------------------------------------------------------------
        ancho_maximo = self.screen_width - 20
        self.img3 = imutils.resize(cv2.imread(img),ancho_maximo)
        h3, w3 = self.img3.shape[:2]
        self.himg3 = h3
        self.wimg3 = w3

    def posicionar_ventana_mouse(self, mouseX, mouseY):
        # --- Se activa desde la clase Controlador -> clase Evento Mouse ---
        #     metodo:  onMouse(self, event, x, y, flags, param)
        # ------------------------------------------------------------------
        
        # --- Referencia de marcadores -------------------------------------
        # Se define un cuadro de 20x20 alrededor del centro del marcador
        # como un 'area' detectable para indicar que el 'mouse' se encuentra
        # sobre el 'marcador'
        # ------------------------------------------------------------------
        lat_izq = self.diccionario['x']-10
        lat_der = self.diccionario['x']+10
        inf = self.diccionario['y']-10
        sup = self.diccionario['y']+10

        # --- Posicionar 'ventana' en RENGLON superior/inferior ------------
        if mouseY <= 20:
            self.permitir_abrir_ventana = True
            self.targetX = self.diccionario['posicion_renglon']['x']
            self.targetY = self.diccionario['posicion_renglon']['y']
        # ------------------------------------------------------------------

        # --- Posisionar 'ventana' en COLUMNA izquierda --------------------
        elif mouseX <= 50:
            self.permitir_abrir_ventana = False
            self.targetX = self.diccionario['posicion_columna']['x']
            self.targetY = self.diccionario['posicion_columna']['y']
                   
        # --- Posicionar 'ventana' SOBRE marcadores: MOUSE sobre el 'marcador' ---
        elif mouseX>=lat_izq and mouseX<=lat_der and mouseY>=inf and mouseY<=sup:
            self.permitir_abrir_ventana = False
            self.targetY = self.diccionario['rectangulo_marcador']['y']
            self.targetX = self.diccionario['rectangulo_marcador']['x']
            print(" ")
            print(" En CLASE Display::")
            print(" -> CURSOR sobre el MARCADOR",self.diccionario['id'])
        # ------------------------------------------------------------------
        
        self.move_springing_posicion()
        
    def mouse_sobre_controlesVentana(self,mouse_x,mouse_y):
        # --- Se activa desde la clase Controlador -> clase Evento Mouse ---
        #     metodo:  onMouse(self, event, x, y, flags, param)
        # ------------------------------------------------------------------

        # --- Referencia de controles de ventana Max/Min -------------------
        # Se define una zona de 25x30 (ancho=25, alto=30 en la parte derecha
        # de la 'ventana', para detectar la posicion del 'mouse' en dicha zona
        # ------------------------------------------------------------------  
        sup_der = self.x + self.ancho_display
        sup_izq = self.x + self.ancho_display - 25
        inf_izq = self.y
        inf_der = self.y+self.alto_display

        # --- Referencia de controles de ventana Maximizar TOTAL -----------
        # Se define una zona de 25x30 (ancho=25, alto=30 en la parte derecha-10
        # de la 'ventana', para detectar la posicion del 'mouse' en dicha zona
        # ------------------------------------------------------------------  
        max_s_d = self.x + self.ancho_display - 35   # superior_derecha
        max_s_i = self.x + self.ancho_display - 60   # supeior_izquierda
        max_i_i = self.y                             # inferior_izquierda
        max_i_d = self.y+self.alto_display           # inferior_derecha

        # --- MOUSE sobre los controles Max/Min en la 'ventana' ---
        if mouse_x>=sup_izq and mouse_x<=sup_der and mouse_y>=inf_izq and mouse_y<=inf_der:
            # --- La ventana de graficacion se ABRE ---
            if self.flag_abrirVentanaDisplay:
                self.flag_abrirVentanaDisplay = False
            # --- La ventana de graficacion se CIERRA ---
            else:
                self.flag_abrirVentanaDisplay = True
            print(" ")
            print(" En CLASE Display::")
            print(" -> CURSOR sobre control Max/min -> MARCADOR",self.diccionario['id'])

        # --- MOUSE sobre el control Maximizar TOTAL en la 'ventana' ---
        if mouse_x>=max_s_i and mouse_x<=max_s_d and mouse_y>=max_i_i and mouse_y<=max_i_d:
            # --- La ventana de graficacion se ABRE ---
            if self.flag_abrirVentanaDisplay_MAXIMO:
                self.flag_abrirVentanaDisplay_MAXIMO = False
            # --- La ventana de graficacion se CIERRA ---
            else:
                self.flag_abrirVentanaDisplay_MAXIMO = True
            print(" ")
            print(" En CLASE Display::")
            print(" -> CURSOR sobre Maximizar TOTAL -> MARCADOR",self.diccionario['id'])
                
    def actualizar_imagen_display(self,img):

        # --- Imagen para superposicion y transparencia ---
        overlay = img.copy()

        # ----------------------------------------------------------------------
        #               Dibujar "circulo" sobre el marcador
        #  Dibujar "linea" que conecta el marcador con el DISPLAY principal
        # ----------------------------------------------------------------------
        self.dibujar_circuloLinea_marcador(overlay)
        
        # ----------------------------------------------------------------------
        #           Creacion del DISPLAY PRINCIPAL (DISPLAY)
        # ----------------------------------------------------------------------
        self.crear_display_principal(overlay)

        # ----------------------------------------------------------------------
        #            Creacion de la VENTANA SECUNDARIA
        #           [Graficacion o diccionario] --> (DISPLAY)
        # ----------------------------------------------------------------------

        # --- ABRIR Ventana de INFORMACION (Grafica o Texto/Dibujo) ---
        if self.flag_abrirVentanaDisplay and self.permitir_abrir_ventana and self.posicion_estable:
            
            # --- Adjuntar Ventana de GRAFICACION ---
            self.adjuntar_ventana_graficacion(overlay)
            # --- Dibujar control de minimizar ventana graficacion ---
            cv2.rectangle(overlay, (self.x + self.ancho_display - 20,
                                self.y + 18),
                      (self.x + self.ancho_display - 8,
                       self.y + 20),
                      (255,255,255), 1)
            
            # ------------------------------------------------------------------
            #     INICIO DE CONTROLES DE MAXIMIZACION / MINIMIZACION MAXIMA
            # ------------------------------------------------------------------
            if self.permitir_ocupar_areaImagen and self.flag_abrirVentanaDisplay_MAXIMO:
                # ------------------------------------------------------------------
                #     Se solicita permiso a la clase Modelo para usar el area de
                #     imagen. La clase Modelo quita el permiso a todas las demás
                #     ventanas para que no usen el area de imagen
                #     metodo:  solicitud_permiso_usoAreaImagen(self, canal)
                #                   - permitir_abrir_ventana = False
                #                   - permitir_ocupar_areaImagen = False
                #     Para la ventana solicitantes:
                #                   - permitir_ocupar_areaImagen = True
                # ------------------------------------------------------------------
                self.modelo.solicitud_permiso_usoAreaImagen(self.diccionario['id'])
                # --- Adjuntar Ventana de GRAFICACION MAXIMA ---
                self.adjuntar_ventana_graficacionMAXIMA(overlay)
                # --- Dibujar control de Minimizar TOTAL ventana graficacion ---
                cv2.rectangle(overlay, (self.x + self.ancho_display - 35,
                                    self.y + 18),
                          (self.x + self.ancho_display - 60,
                           self.y + 20),
                          (0,255,0), 1)

            else:
                # ------------------------------------------------------------------
                #     Se solicita permiso a la clase Modelo para LIBERAR el area de
                #     imagen. La clase Modelo OTORGA el permiso a todas las demás
                #     ventanas para que puedan usar el area de imagen
                #     metodo:  solicitud_liberar_usoAreaImagen(self)
                #                   - permitir_abrir_ventana = True
                #                   - permitir_ocupar_areaImagen = True
                # ------------------------------------------------------------------
                self.modelo.solicitud_liberar_usoAreaImagen()
                # --- Dibujar control de Maximizar TOTAL ventana graficacion ---
                cv2.rectangle(overlay, (self.x + self.ancho_display - 35,
                                    self.y + 8),
                          (self.x + self.ancho_display - 60,
                           self.y + 20),
                          (0,255,0), 1)
            # ------------------------------------------------------------------
            #      FIN DE CONTROLES DE MAXIMIZACION / MINIMIZACION MAXIMA
            # ------------------------------------------------------------------
            
        # --- CERRAR Ventana de INFORMACION (Graficacion o diccionario) ---
        elif self.permitir_abrir_ventana and self.posicion_estable:
            # --- Dibujar control de maximizar ventana graficacion --
            cv2.rectangle(overlay, (self.x + self.ancho_display - 20,
                                self.y + 8),
                      (self.x + self.ancho_display - 8,
                       self.y + 20),
                      (255,255,255), 1)

        # ----------------------------------------------------------------------
        #       Superposición de las dos imagenes con transparencia     
        # ----------------------------------------------------------------------    
        alpha = 0.8 # 0.6 el mejor
        cv2.addWeighted(overlay,alpha,img,1-alpha,0,img)
        
    def dibujar_circuloLinea_marcador(self,overlay):

        # --- Linea de conexion entre "marcadores" y Ventana de diccionario [Display]
        cv2.line(overlay,(self.x ,self.y),
                 (self.diccionario['x'],self.diccionario['y']),
                 (255, 255, 255), 1)
        
        # --- Circunferencia sobre "marcadores"
        cv2.circle(overlay, (self.diccionario['x'],self.diccionario['y']),
                    10, (255,255,255), 2)
        #print("- D:",self.diccionario['id']," self.x = ",self.x," self.y = ",self.y)

    def crear_display_principal(self,overlay):

        # --- MARCO del DISPLAY [fondo azul] ---
        cv2.rectangle(overlay, (self.x,self.y),
                      (self.x + self.ancho_display,
                       self.y + self.alto_display),
                      self.color, -1)
        
        # --- TEXTO/diccionario DISPLAY [letras/digitos blancol]
        #cv2.putText(overlay, "CH{} {}".format(self.diccionario['id'],self.diccionario['id'])
        # --- IDENTIFICADOR del DISPLAY ---
        m = "m" + str(self.diccionario['id'])
        titulo = self.titulos_marcadores[m]
        cv2.putText(overlay, "M{} ".format(self.diccionario['id']),
                      (self.x + 15,
                       self.y + 19),
                       cv2.FONT_HERSHEY_SIMPLEX,
                       0.5, (255, 255, 255), 2, cv2.LINE_AA)
        # --- TITULO del DISPLAY ---
        cv2.putText(overlay, titulo,
                      (self.x + 50,
                       self.y + 19),
                       cv2.FONT_HERSHEY_SIMPLEX,
                       0.5, (255, 255, 255), 2, cv2.LINE_AA)
        
    def adjuntar_ventana_graficacion(self,overlay):

        # --- Pantalla GRAFICA: grafica de "matplotlib" ---
        if self.diccionario['ventana'] == "inferior":
            pip_h = self.y + self.alto_display
            pip_w = self.x  
            h1, w1 = self.img2.shape[:2]
            overlay[pip_h:pip_h+h1,pip_w:pip_w+w1] = self.img2  # make it PIP
            # --- Marco de pantalla grafica ---
            cv2.rectangle(overlay, (self.x,self.y + self.alto_display),
                        (self.x + w1, self.y + self.alto_display + h1),
                        self.color, 1)

        elif self.diccionario['ventana'] == "superior":
            pip_h = self.y
            pip_w = self.x
            h1, w1 = self.img2.shape[:2]
            overlay[pip_h-h1:pip_h,pip_w:pip_w+w1] = self.img2  # make it PIP
            # --- Marco de pantalla grafica ---
            cv2.rectangle(overlay, (self.x,self.y),
                        (self.x + w1, self.y - h1),
                        self.color, 1)

    def adjuntar_ventana_graficacionMAXIMA(self,overlay):

        pip_h = int((self.screen_height - self.h0)/2)
        pip_w = int((self.screen_width - self.w0)/2)
        h0 = self.h0
        w0 = self.w0

        overlay[pip_h:pip_h+h0,pip_w:pip_w+w0] = self.imagen  # make it PIP
        # --- Marco de pantalla grafica ---
        cv2.rectangle(overlay, (pip_w, pip_h), (pip_w+w0, pip_h+h0), self.color, 1)
        
    def programar_secuencia_inicial(self):
        # --- Se activa desde la clase Controlador -> clase Evento Mouse ---
        #     metodo:  mover_objetos(self,imagen)
        # ------------------------------------------------------------------
        
        if self.secuenciador <= 30: # 150
            if self.flag == 1:
                self.secuenciador += 1
            else:
                self.secuenciador -= 1
        
        if self.secuenciador == 30: # 150
            self.flag = 0
            self.cambiar_aposicion_SuperiorInferior()  
            self.switch_inicio = 0   
        if self.secuenciador == 0:
            self.flag = 1
            self.cambiar_aposicion_marcador() 
    
    def cambiar_aposicion_SuperiorInferior(self):
        self.targetX = self.diccionario['posicion_renglon']['x']
        self.targetY = self.diccionario['posicion_renglon']['y']

    def cambiar_aposicion_marcador(self):
        self.targetX = self.diccionario['rectagulo_marcador']['x']
        self.targetY = self.diccionario['rectagulo_marcador']['y']
       
    def move_springing_posicion(self):

        self.x, self.y = self.spring(self.targetX,self.x,self.targetY,self.y)

    def spring(self,Tx,x,Ty,y):

        self.check_screen_bounds()
        
        dx = Tx - x
        dy = Ty - y
        
        if dx>0 and dx<=4: x = Tx
        if dy>0 and dy<=4: y = Ty

        if x == Tx and y == Ty: self.posicion_estable = True
        else: self.posicion_estable = False
        
        ax = dx*spring
        ay = dy*spring
        
        self.x_velocity += ax
        self.y_velocity += ay
        
        self.x_velocity *= friction
        self.y_velocity *= friction

        x += self.x_velocity
        y += self.y_velocity

        x = int(x)
        y = int(y)

        return (x, y)

    def check_screen_bounds(self):

        if self.x < 5: self.x_velocity = -self.x_velocity
        if self.y < 0: self.y_velocity = -self.y_velocity
        if (self.x + self.ancho_display) > self.screen_width - 20:
            self.x_velocity = -self.x_velocity
        if (self.y + self.alto_display) > self.screen_height:
            self.y_velocity = -self.y_velocity            
                    
    def print_diccionario_display(self):
        print(" ")
        print(" En CLASE Display::")
        print("**************************************************")
        print(" -- Muestras recibidas de Arduino por cada canal --")
        print("**************************************************")
        print(" - DISPLAY",diccionario['id'],": *****************************")
        print(self.diccionario)

