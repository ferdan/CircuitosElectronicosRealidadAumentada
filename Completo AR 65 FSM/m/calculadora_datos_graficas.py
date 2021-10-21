# ************************************
#
#   Clase: --> Calculadora_datos_graficas 
#   Modulo: -> calculadora_datos_graficas.py
#
# Descripción:
#   Auxiliar de graficador.py que calcula, entre otras cosas, coordenadas de etiquetas, flechas y circulos.
#
# Fecha: julio 28/2021
#
# ************************************

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import math
import statistics
from engineering_notation import EngNumber
import cv2

class calculadora_datos_graficas:
    # -------------------------------------------------------
    #           CONSTRUCTOR
    # -------------------------------------------------------
    def __init__(self):

        print("")
        print(" CONSTRUCTOR:  Clase: Calculadora_datos_graficas")

    # -------------------------------------------------------
    # Calcula la ecuacion de una recta (pendiente m y ordenada al origen b) dados dos puntos
    # 
    # -------------------------------------------------------
    def ec_recta_dos_puntos(self,p1,p2):
        xp1,yp1 = p1
        xp2,yp2 = p2
        m = float('inf')
        b = float('inf')
        if xp2 - xp1 != 0:
            m = (yp2 - yp1) / (xp2 - xp1)
            b = (-xp1*yp2 - yp1*xp2) / (xp2 - xp1)
        
        #print("m: "+str(m)+", b: "+str(b))
        return m,b

    # -------------------------------------------------------
    # Calcula la ecuacion de una recta perpendicular (pendiente m y ordenada al origen b) dado un punto y una pendiente
    # 
    # -------------------------------------------------------
    def ec_recta_punto_pendiente_perpendicular(self,p1,m):
        xp1,yp1 = p1
        
        if m == 0:
            mp = float('inf')
        else:
            mp = -1 / m
        
        bp = (-mp*xp1 + yp1)
        #print("m: "+str(mp)+", b: "+str(bp))
        return mp,bp

    # -------------------------------------------------------
    # Calcula el valor absoluto de la distancia dados dos puntos
    # 
    # -------------------------------------------------------
    def distancia_entre_puntos(self,p1,p2):
        xp1,yp1 = p1
        xp2,yp2 = p2

        d = math.sqrt((xp2-xp1)**2+(yp2-yp1)**2)
        return d

    # -------------------------------------------------------
    # Calcula las coordenadas de dos puntos equidistantes dado un punto, la pendiente de una recta y la distancia entre ellos. 
    # 
    # -------------------------------------------------------
    def puntos_equidistantes_sobre_recta_desde_punto(self,p1,m,d):
        xp1,yp1 = p1
        x3a = xp1
        x3b = xp1
        y3a = yp1 + d
        y3b = yp1 - d
        
        if m < 9223372036854775807 and m != 0: # la recta no es vertical ni horizontal
            ec_puntos = np.poly1d([1+m**2,-2*xp1*(1+m**2),(1+m**2)*xp1-d**2])
            print(ec_puntos)
            x3a,x3b = ec_puntos.r
            print(ec_puntos.r)
            y3a = m * x3a - m * xp1 + yp1
            y3b = m * x3b - m * xp1 + yp1
        if m == 0: # la recta es horizontal
            #print('aqui')
            x3a = xp1 - d
            x3b = xp1 + d
            y3a = yp1
            y3b = yp1
        '''print(x3a)
        print(y3a)
        print(x3b)
        print(y3b)'''
        return int(x3a),int(y3a),int(x3b),int(y3b)

    # -------------------------------------------------------
    # Obtiene todos los indices de un elemento repetido en una lista.  
    # Tomado de https://stackoverflow.com/questions/5419204/index-of-duplicates-items-in-a-python-list
    # -------------------------------------------------------
    def list_duplicates_of(self,seq,item):
        start_at = -1
        locs = []
        while True:
            try:
                loc = seq.index(item,start_at+1)
            except ValueError:
                break
            else:
                locs.append(loc)
                start_at = loc
        return locs

    # -------------------------------------------------------
    # Obtiene una representacion en binario de un numero en decimal 
    # 
    # -------------------------------------------------------
    def decimal_a_binario(self,decimal,num_bits):
        #str_bin = '0b'
        str_bin = ''
        for i in range(num_bits-1,-1,-1):
            bstr = decimal & int(pow(2,i))
            bstr >>= i
            str_bin +=str(bstr)
        return str_bin

    # -------------------------------------------------------
    # Obtiene los bits que son diferentes entre dos transiciones de estados
    # 
    # -------------------------------------------------------
    def obtener_bits_cambiantes(self,fsm1,transiciones,estado):
        diff = 0
        if len(transiciones) > 1:
            for k in range(1,len(transiciones)):
                diff_orx = fsm1.tabla_transiciones_estados[estado][transiciones[0]] ^ fsm1.tabla_transiciones_estados[estado][transiciones[k]]
                diff |= diff_orx
        return diff

    # -------------------------------------------------------
    # Obtiene una representacion en binario de un numero en decimal, que ademas incluye condiciones de no importa (representado por una "X")
    # 
    # -------------------------------------------------------
    def obtener_str_de_binario_transicion(self,bits,binario,diff):
        str_transicion =''
        for k in range(bits,-1,-1):
            if diff >= math.pow(2,k):
                diff -= math.pow(2,k)
                str_transicion += 'X'
            else:
                binstr = binario & int(math.pow(2,k))
                binstr >>= k
                str_transicion += str(binstr)
        return str_transicion

    # -------------------------------------------------------
    # Obtiene las coordenadas de las intersecciones entre un circulo y una recta. 
    # Tomado de https://stackoverflow.com/questions/30844482/what-is-most-efficient-way-to-find-the-intersection-of-a-line-and-a-circle-in-py
    # -------------------------------------------------------
    def circle_line_segment_intersection(self, circle_center, circle_radius, pt1, pt2, full_line=True, tangent_tol=1e-9):
        """ Find the points at which a circle intersects a line-segment.  This can happen at 0, 1, or 2 points.

        :param circle_center: The (x, y) location of the circle center
        :param circle_radius: The radius of the circle
        :param pt1: The (x, y) location of the first point of the segment
        :param pt2: The (x, y) location of the second point of the segment
        :param full_line: True to find intersections along full line - not just in the segment.  False will just return intersections within the segment.
        :param tangent_tol: Numerical tolerance at which we decide the intersections are close enough to consider it a tangent
        :return Sequence[Tuple[float, float]]: A list of length 0, 1, or 2, where each element is a point at which the circle intercepts a line segment.

        Note: We follow: http://mathworld.wolfram.com/Circle-LineIntersection.html
        """

        (p1x, p1y), (p2x, p2y), (cx, cy) = pt1, pt2, circle_center
        (x1, y1), (x2, y2) = (p1x - cx, p1y - cy), (p2x - cx, p2y - cy)
        dx, dy = (x2 - x1), (y2 - y1)
        dr = (dx ** 2 + dy ** 2)**.5
        big_d = x1 * y2 - x2 * y1
        discriminant = circle_radius ** 2 * dr ** 2 - big_d ** 2

        if discriminant < 0:  # No intersection between circle and line
            return []
        else:  # There may be 0, 1, or 2 intersections with the segment
            intersections = [
                [int(cx + (big_d * dy + sign * (-1 if dy < 0 else 1) * dx * discriminant**.5) / dr ** 2),
                int(cy + (-big_d * dx + sign * abs(dy) * discriminant**.5) / dr ** 2)]
                for sign in ((1, -1) if dy < 0 else (-1, 1))]  # This makes sure the order along the segment is correct
            if not full_line:  # If only considering the segment, filter out intersections that do not fall within the segment
                fraction_along_segment = [(xi - p1x) / dx if abs(dx) > abs(dy) else (yi - p1y) / dy for xi, yi in intersections]
                intersections = [pt for pt, frac in zip(intersections, fraction_along_segment) if 0 <= frac <= 1]
            if len(intersections) == 2 and abs(discriminant) <= tangent_tol:  # If line is tangent to circle, return just one point (as both intersections have same location)
                return [intersections[0]]
            else:
                return intersections

    # -------------------------------------------------------
    # Obtiene las coordenadas utilizadas para dibujar lineas entre estados para el diagrama de estados
    # Se siguio la siguiente secuencia de pasos:
    # 1. Encontrar las intersecciones entre la circunferencia del estado actual y la linea que une los centros de la circunferencia del estado actual y la del centro que es de transicion. 
    # 2. Calcular la recta perpendicular a la línea generada en el paso anterior sobre el punto de interseccion.
    # 3. Calcular la interseccion de la recta perpendicular anterior con la circunferencia del estado actual. Se deben obtener dos soluciones. 
    #    Hay dos casos especiales que son que la pendiente de la recta del paso 1 sea horizontal o vertical:
    #   a. Cuando la pendiente m tiende a infinito, se calcula las coordenadas de los puntos que equidistan de la interseccion del paso 1 y se ubican sobre la recta perpendicular
    #   b. Si la pendiente m no tienda a infinito o m es igual a cero, se utiliza un metodo mas sencillo. Se toma la interseccion del paso 1 como centro de una nueva circunferencia
    #      y se buscan las intersecciones con la circunferencia del estado actual.
    # 4. Calcular las intersecciones con la circunferencia de transicion
    #    Hay dos casos especiales que igual son dependiendo de la pendiente de la recta del paso 1 si es horizontal o vertial:
    #   a. Cuando la pendiente m tiende a infinito, se realiza el mismo procedimiento descrito en los pasos 1, 2 y 3.a, esta vez con la circunferencia de transicion. 
    #   b. Si la pendiente m no tiende a infinito, se calcula la ecuacion que una las circunferencias del estado actual y la de transicion en los puntos calculados en el paso 3
    #      para encontrar las intersecciones con la circunferencia de transicion. 
    # -------------------------------------------------------
    
    def obtener_puntos_lineas_transicion(self,canvas2,xcoords,ycoords,c_radio,length_lineas,c_actual,c_transicion):
        lineas_transiciones = []

        # Se obtienen las intersecciones de la recta que une los centros de las circunferencias del estado actual y de transicion y la circunferencia del estado actual
        inters_origen = self.circle_line_segment_intersection((xcoords[c_actual],ycoords[c_actual]),c_radio[1],(xcoords[c_actual],ycoords[c_actual]),(xcoords[c_transicion],ycoords[c_transicion]),False,1e-9)
        #print("inters_origen: "+str(inters_origen), "len(inters_origen): "+str(len(inters_origen)))

        # Calcula la ecuacion de la recta que une los centros de las circunferencias del estado actual y de transicion
        m,b = self.ec_recta_dos_puntos(inters_origen[0],[xcoords[c_transicion],ycoords[c_transicion]])
        #recta = np.poly1d([m,b])

        # Calcula la ecuacion de la recta perpendicular a la enterior y sobre el punto de interseccion
        mp,bp = self.ec_recta_punto_pendiente_perpendicular(inters_origen[0],m)
        recta_p = np.poly1d([mp,bp])
        #print('recta perpendicular calculada')
        #print("m: "+str(m)+" , mp: "+str(mp))
        
        if mp > 9223372036854775807:# la recta recta_p es perpendicular
            #print('calcular puntos con recta perpendicular')
            xp1,yp1,xp2,yp2 = self.puntos_equidistantes_sobre_recta_desde_punto((inters_origen[0][0],inters_origen[0][1]),mp,length_lineas)
            lineas_transiciones.append([xp1,yp1])
            lineas_transiciones.append([xp2,yp2])
            #print(lineas_transiciones)
            
        else:# la recta recta_p no es perpendicular
            if m > 9223372036854775807:# la recta recta_p es horizontal (la recta que une los centros de las circunferencias del estado actual y de transicion es vertical)
                #print('calcular puntos con circunferencia especial')
                # Se realiza un ajuste para obtener las intersecciones con la circunferencia del estado actual utilizando el punto de interseccion obtenido anteriormente como centro de una circunferecia
                lineas_transiciones = self.circle_line_segment_intersection(inters_origen[0],length_lineas,(xcoords[c_actual]-50,int(recta_p(xcoords[c_actual]))),(xcoords[c_transicion]+50,int(recta_p(xcoords[c_transicion]))),True,1e-9)
                
            else:
                #print('calcular puntos con circunferencia')
                # Se obtienen las intersecciones con la circunferencia del estado actual utilizando el punto de interseccion obtenido anteriormente como centro de una circunferecia
                lineas_transiciones = self.circle_line_segment_intersection(inters_origen[0],length_lineas,(xcoords[c_actual],int(recta_p(xcoords[c_actual]))),(xcoords[c_transicion],int(recta_p(xcoords[c_transicion]))),True,1e-9)
                
        #print('primeras dos transiciones calculadas')
        #print("lineas_transiciones: "+str(lineas_transiciones))

        # Se calculan las intersecciones con la circunferencia de transicion 
        if m < 9223372036854775807:# la recta que une los centros de las circunferencias del estado actual y de transicion no es vertical
            for i in [0,1]:
                # Se calcula una recta que une alguna de las intersecciones anteriores con la circunferencia de transicion
                recta_transicion = np.poly1d([m,-m*lineas_transiciones[i][0]+lineas_transiciones[i][1]])

                #print(str(lineas_transiciones[i][0])+" , "+str(recta_transicion(lineas_transiciones[i][0])))
                #print(str(xcoords[c_transicion])+" , "+str(recta_transicion(xcoords[c_transicion])))

                # Puntos de inicio y final de esta recta
                ptr0 = (lineas_transiciones[i][0],recta_transicion(lineas_transiciones[i][0]))
                ptr1 = (xcoords[c_transicion],recta_transicion(xcoords[c_transicion]))
                
                #print("ptr0: "+str(ptr0))
                #print("ptr1: "+str(ptr1))

                # Se obtienen las coordenadas de las intersecciones con la circunferencia de transicion con la recta recta_transicion
                p_transicion = self.circle_line_segment_intersection((xcoords[c_transicion],ycoords[c_transicion]),c_radio[1],ptr0,ptr1,False,1e-9)

                p_transicion = np.reshape(p_transicion,-1)
                p_transicion = p_transicion.tolist()
                lineas_transiciones.append(p_transicion)
                
        else:# la recta que une los centros de las circunferencias del estado actual y de transicion es vertical
            # Obtiene las coordenadas de la interseccion entre la recta que une los centros de las circunferencias de estado actual y de transicion y la circunferencia de transicion
            inters_fin = self.circle_line_segment_intersection((xcoords[c_transicion],ycoords[c_transicion]),c_radio[1],(xcoords[c_transicion],ycoords[c_transicion]),(xcoords[c_actual],ycoords[c_actual]),False,1e-9)
            #print("inters_fin: "+str(inters_fin), "len(inters_fin): "+str(len(inters_fin)))
            
            #cv2.circle(canvas2, tuple(inters_fin[0]), 5, (0,255,0), 3)

            # Calcula la recta perpendicular a la anterior en el punto de la interseccion
            mp,bp = self.ec_recta_punto_pendiente_perpendicular(inters_fin[0],m)
            #recta_p_aux = np.poly1d([mp,bp])
            #print(": "+str(recta_p_aux))

            # Se obtienen los puntos equidistantes al punto de interseccion sobre la recta perpendicular. 
            xp1,yp1,xp2,yp2 = self.puntos_equidistantes_sobre_recta_desde_punto((inters_fin[0][0],inters_fin[0][1]),mp,length_lineas)
            
            lineas_transiciones.append([xp1,yp1])
            lineas_transiciones.append([xp2,yp2])
            #print(lineas_transiciones)
            
        #print("lineas_transiciones: "+str(lineas_transiciones))
        #for i in [0,1,2,3]:
            #cv2.circle(canvas2, tuple(lineas_transiciones[i]), 5, (0,0,0), 3)

        return lineas_transiciones

    # -------------------------------------------------------
    # Obtiene las coordenadas de las etiquetas para las lineas de transiciones del diagrama de estados.  
    # 
    # -------------------------------------------------------
    def obtener_coordenadas_labels(self,p1,p2):
        xp1,yp1 = p1
        xp2,yp2 = p2
        print("p1: "+str(xp1)+" , "+str(yp1))
        print("p2: "+str(xp2)+" , "+str(yp2))
        
        x_lb = min(xp1,xp2) + int(abs(xp2 - xp1)/2)
        y_lb = min(yp1,yp2) + int(abs(yp2 - yp1)/2)

        print("punto medio: "+str(x_lb)+" , "+str(y_lb))
        
        if xp1 < xp2:
            if yp1 < yp2:
                x_lb += 0
                y_lb -= 0
            elif yp1 > yp2:
                x_lb -= 30
                y_lb -= 8
            else:
                x_lb -= 17
                y_lb -= 8
        elif xp1 > xp2:
            if yp1 < yp2:
                x_lb += 5
                y_lb += 10
            elif yp1 > yp2:
                x_lb += 5
                y_lb += 0
            else:
                x_lb -= 17
                y_lb += 18
        else:
            if yp1 < yp2:
                x_lb += 2
            elif yp1 > yp2:
                x_lb -= 33
        return x_lb,y_lb

    # -------------------------------------------------------
    # Obtiene las intersecciones dadas dos circunferencias, dadas las coordenadas de su centro y radio. 
    # Tomado de https://stackoverflow.com/questions/55816902/finding-the-intersection-of-two-circles
    # -------------------------------------------------------
    def get_intersections(self, x0, y0, r0, x1, y1, r1):
        # circle 1: (x0, y0), radius r0
        # circle 2: (x1, y1), radius r1

        d = math.sqrt((x1-x0)**2 + (y1-y0)**2)
        
        # non intersecting
        if d > r0 + r1 :
            return None
        # One circle within other
        if d < abs(r0-r1):
            return None
        # coincident circles
        if d == 0 and r0 == r1:
            return None
        else:
            a=(r0**2-r1**2+d**2)/(2*d)
            h=math.sqrt(r0**2-a**2)
            x2=x0+a*(x1-x0)/d   
            y2=y0+a*(y1-y0)/d   
            x3=x2+h*(y1-y0)/d     
            y3=y2-h*(x1-x0)/d 

            x4=x2-h*(y1-y0)/d
            y4=y2+h*(x1-x0)/d
            
            return (x3, y3, x4, y4)
