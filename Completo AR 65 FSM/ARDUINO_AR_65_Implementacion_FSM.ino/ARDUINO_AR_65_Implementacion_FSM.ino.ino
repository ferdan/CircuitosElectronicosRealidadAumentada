/***************************************************

  PROGRAMA: 26072021

  Implementacion de una maquina de estados finitos

  Este programa se ejecuta en conjunto con:

  ARDUINO (1): ARDUINO AR 65 Implemenracion FSM.ino 
  ARDUINO (2): ARDUINO AR 65 Prueba y Lectura FSM.ino 
  PYTHON:  Completo AR 65 FSM.py  (monitor) 25062021-P
  
  TARJETA UTILIZADA: Arduino UNO, expandible a Arduino MEGA
  Opcional: Utilizar LEDs conresistencias para observar el funcionamiento del circuito
                 
  28 / julio / 2021
  
*****************************************************/

/**
 * ---------------------------------------------------------------------------------------------------------
 * Declaracion de arreglos de pines digitales
 * pin_entradas[] -> son los pines en donde se leeran las entradas que llegan la maquina de estados finitos
 * pin_lecturas[] -> son los pines de donde se escribiran las salidas de la maquina de estados finitos
 * pin_estados[] -> son los pines que escribira el estado en el que se encuentra la maquina de estados finitos
 * 
 * Como se observa, se pueden implementar maquinas de estados con las siguientes caracteristicas:
 *  - Hasta cuatro entradas
 *  - Hasta cuatro salidas
 *  - Hasta 16 estados diferentes
 * Este programa se probo sobre un Arduino UNO, pero es facilmente expandible si se implementara, por ejemplo,
 * en un Arduino MEGA
 * ---------------------------------------------------------------------------------------------------------
 */
const int pin_entradas[] = {2,3,4,5};
const int pin_salidas[] = {6,7,8,9};
const byte pin_estados[] = {A0,A1,A2,A3};

/**
 * ---------------------------------------------------------------------------------------------------------
 * Declaracion de pines de control
 * pinCLK -> Define el pin del reloj que se utilizara para enviar senales de reloj a la maquina de estados
 * pinReset -> Define el pin de reset que inicializara la maquina de estados
 * 
 * clk -> Es el estado del reloj
 * reset -> Indica si hay que reiniciar la maquina de estados
 * ---------------------------------------------------------------------------------------------------------
 */
int pinCLK = 10;
int pinReset = 11;
int clk = 0;
int reset = 0;

/**
 * ---------------------------------------------------------------------------------------------------------
 * Variables para el control del tiempo de muestreo
 * lastime -> guarda el ultimo instante de tiempo en el que enviaron datos por el puerto serie
 * sampleTime -> duracion entre cada muestra tomada
 * numMuestras -> numero de muestras tomadas por cada curva
 * 
 * Por lo tanto, la frecuencia de cada conjunto de muestras es de 2Hz (numMuestras x sampleTime)/1000
 * ---------------------------------------------------------------------------------------------------------
 */
unsigned long lastTime = 0;
unsigned long sampleTime = 1000;
double firstTime = 0;

/**
 * ---------------------------------------------------------------------------------------------------------
 * Variables de la maquina de estados
 * entrada -> Es el valor de entrada a la maquina
 * salida -> Es el valor de salida que genera la maquina
 * 
 * ---------------------------------------------------------------------------------------------------------
 */
int entrada = 0x00;
int salida = 0x00;

// Ejemplo de un control para proteccion contra corto circuito para fuente de alimentacion
/**
 * ---------------------------------------------------------------------------------------------------------
 * estado_inicial -> Indica el estado en el cual empieza la maquina
 * estado_actual -> Indica el estado actual de la maquina
 * estado_futuro -> Indica el estado al cual va a cambiar la maquina en el siguiente pulso de reloj
 * ---------------------------------------------------------------------------------------------------------
 */
const int estado_inicial = 0;
byte estado_actual = 0;
byte estado_futuro = 0;

/**
 * ---------------------------------------------------------------------------------------------------------
 * num_estados -> Indica cuantos estados tiene la maquina
 * bits_transicion -> Indica cuantos bits tiene las numero de las entradas de transiciones que permiten cambiar entre estados
 * bits_salida -> Indica la cantidad de bits de salida de la maquina de estados
 * ---------------------------------------------------------------------------------------------------------
 */
const int num_estados = 4;
const int bits_transicion = 3;
const int bits_salida = 3;

/**
 * ---------------------------------------------------------------------------------------------------------
 * Las siguientes tablas especifican el funcionamiento de la maquina de estados finitos
 * El prefijo 0B indica que el numero que sigue esta en binario
 * El tamano de estas tablas esta determinador por las constantes num_estados, bits_salida y bits_transicion
 * Cada estado de la maquina corresponde a una entrada de la tabla, como se indica en cada una de las tablas. 
 * 
 * tabla_transiciones_estados -> Indica cuales son las transiciones con las que la maquina cambia de estado
 *                               Las transiciones que no aparecen, se asume que la maquina no cambia de estado
 *                               IMPORTANTE: Se completan la tabla con -1 para las transiciones en las que no hay cambio de estado
 *                               
 * tabla_transiciones_estado_futuro -> Indica el estado al cual va a cambiar la maquina en el siguiente pulso
 *                                     de reloj. Cada estado especificado en esta tabla corresponde a la 
 *                                     transicion de la tabla tabla_transiciones_estados
 *                                     
 * tabla_output_por_estado -> Indica la salida del estado actual de la maquina
 * ---------------------------------------------------------------------------------------------------------
 */
const int tabla_transiciones_estados[num_estados][round(pow(2,bits_transicion))] = {
                                      {0B100,0B101,-1,-1,-1,-1,-1,-1},                       //estado 0: Apagado
                                      {0B000,0B001,0B010,0B011,0B101,0B111,-1,-1},           //estado 1: Encendido funcionando
                                      {0B000,0B001,0B010,0B011,0B110,0B111,-1,-1},           //estado 2: Corto circuito
                                      {0B000,0B001,0B010,0B011,0B100,0B101,-1,-1}            //estado 3: Reset
                                      };

const int tabla_transiciones_estado_futuro[num_estados][round(pow(2,bits_transicion))] = {
                                      {1,1},              //estado 0: Apagado
                                      {0,0,0,0,2,2},      //estado 1: Encendido funcionando
                                      {0,0,0,0,3,3},      //estado 2: Corto circuito
                                      {0,0,0,0,1,2}       //estado 3: Reset
                                      };

const int tabla_output_por_estado[num_estados] = {
                                      (0B000),     //estado 0: Apagado
                                      (0B100),     //estado 1: Encendido funcionando
                                      (0B001),     //estado 2: Corto circuito
                                      (0B011)      //estado 3: Reset
                                      };

/**
 * Inicializa todos los pines a utilizar, inicializa el reloj y la maquina de estados, la comunicacion serial y la comunicacion I2C para comunicarse con los dos PCF8591
 * 
 */
void setup() {
  // Inicializa los pines en donde se escribira el estado de la maquina 
  for(int i=0;i<sizeof(pin_estados)/sizeof(pin_estados[0]);i++)
  {
    pinMode(pin_estados[i],OUTPUT);
  }

  // Inicializa los pines en donde se leera la entrada a la maquina
  for(int i=0;i<sizeof(pin_entradas)/sizeof(pin_entradas[0]);i++)
  {
    pinMode(pin_entradas[i],INPUT);
  }

  // Inicializa los pines en donde se escribira la salida de la maquina 
  for(int i=0;i<sizeof(pin_salidas)/sizeof(pin_salidas[0]);i++)
  {
    pinMode(pin_salidas[i],OUTPUT);
  }

  // Se inicializan los pines en donde se leera el reloj y el reset
  pinMode(pinCLK,INPUT);
  pinMode(pinReset,INPUT);

  // --- Inicializa velocidad de transmision serial ---
  Serial.begin(9600);
  
  // --- Sincronizacion de comunicacion serial ---
  Serial.println("inicio");
  estado_actual = estado_inicial;
  fsm();
  firstTime = millis();
}

void loop() {
  // Lee e identifica un cambio a 1 en el pin del reloj
  // La maquina realiza cambios en los flancos positivos del pin del reloj
  clk = digitalRead(pinCLK);
  if(clk == 1)
  {
    // Lee el pin de reset. Si es 1 se inicializa la maquina de estados finitos a su estado inicial
    // De lo contrario continua con el funcionamiento de la maquina
    reset = digitalRead(pinReset);
    if(reset == 0)
    {
      estado_actual = estado_inicial;
    }
    fsm();

    // Espera a que el pin de reloj cambie a 0 para continuar
    while(clk == 1){clk = digitalRead(pinCLK);};
  }

  // (Opcional) Cada sampleTime milisegundos envia informacion al puerto serie para observar su comportamiento
  /*if ((millis()-lastTime) >= sampleTime) 
  {
    //Serial.println(millis()-firstTime);
    //Serial.println(millis()-lastTime);
    lastTime = millis(); // Actualiza el tiempo de la ultima vez que se tomaron muestras
    //imprimir_estado_maquina();

  }*/
}

/**
 * Implementa el funcionamiento de la maquina de estados finitos, de acuerdo a los parametros establecidos al principio del programa
 * 
 */
void fsm()
{
  // Lee la entrada
  leer_entradas();

  // Determina si cambia de estado
  funcion_fsm();
  //escribir_salidas(pin_salidas,salida);

  // Escribe la salida correspondiente al estado actual de la maquina de estados
  escribir_salidas();

  // Escribe el estado actual de la maquina de estados
  escribir_estados();

  // (Opcional) Envia datos seriales sobre la entrada, estado y salida de la maquina de estados
  //enviar_datos_seriales();

  // Actualiza el estado para el siguiente pulso de reloj
  estado_actual = estado_futuro;
}


/**
 * Envia al puerto serial la entrada, estado y salida de la maquina de estados
 * 
 */
void enviar_datos_seriales(){
  if(estado_actual != estado_futuro)
  {
    //Serial.print("Entrada: ");
    Serial.println(entrada);
    //Serial.print(", Estado actual: ");
    Serial.println(estado_actual);
    //Serial.print(", salida: ");
    Serial.println(salida);
  }
}
  
/**
 * Implementa el funcionamiento de la maquina de estados, de acuerdo a los parametros establecidos al inicio del programa
 * 
 */
void funcion_fsm()
{
  //imprimir_tamano_tablas();
  // Actualiza la salida de la maquina
  salida = tabla_output_por_estado[estado_actual];

  // Verifica si hay que hacer algun cambio de estado, comparando con las posibles entradas que indican un cambio de estado
  for(int i=0;i<(sizeof(tabla_transiciones_estados[estado_actual])/2);i++)
  {
    //imprimir_comparacion_estado(i);
    if(entrada == tabla_transiciones_estados[estado_actual][i])
    {
      estado_futuro = tabla_transiciones_estado_futuro[estado_actual][i];
      //imprimir_cambio_estado();
      return;
    }
  }
}

/**
 * Lee las entradas en binario que le llegan a la maquina de estados
 * Convierte este valor leido en un valor en decimal
 * 
 */
void leer_entradas()
{
  entrada = 0x00;
  for(int i=0;i<bits_transicion;i++){
    //imprimir_antes_suma_entrada();
    entrada += (byte)round(digitalRead(pin_entradas[i])*pow(2,i));
    //imprimir_despues_suma_entrada(i);
  }
  //Serial.print("entrada(final): ");
  //Serial.println(entrada);
}

/**
 * Escribe la salida de la maquina de estados
 * De un valor en decimal lo convierte en binario
 * 
 */
void escribir_salidas()
{
  int temp = salida;
  for(int i=(sizeof(pin_salidas)/2)-1;i>=0;i--)
  {
    //imprimir_estado_salida(i,salida);
    if(salida>=(pow(2,i)))
    {
      salida -= round(pow(2,i));
      digitalWrite(pin_salidas[i],HIGH);
      //imprimir_salida_i(i,1);
    }
    else
    {
      digitalWrite(pin_salidas[i],LOW);
      //imprimir_salida_i(i,0);
    }
  }
  salida = temp;
}

/**
 * Escribe el estado actual de la maquina de estados
 * De un valor en decimal lo convierte en binario
 * 
 */
void escribir_estados()
{
  int temp = estado_actual;
  //Serial.print("estado actual: ");
  //Serial.println(estado_actual);
  for(int i=(sizeof(pin_estados)/2)-1;i>=0;i--)
  {
    //imprimir_estado_salida(i,estado_actual);
    if(estado_actual>=(pow(2,i)))
    {
      estado_actual -= round(pow(2,i));
      digitalWrite(pin_estados[i],HIGH);
      //imprimir_salida_i(i,1);
    }
    else
    {
      digitalWrite(pin_estados[i],LOW);
      //imprimir_salida_i(i,0);
    }
  }
  //delay(500);
  estado_actual = temp;
}

// Las siguientes subrutinas despliegan informacion extra sobre lo que ocurre en el programa

/**
 * Imprime en el monitor serial el tamano de las tablas de la maquina de estados
 * 
 */
void imprimir_tamano_tablas(){
  Serial.print("sizeof(tabla_transiciones_estados): ");
  Serial.println(sizeof(tabla_transiciones_estados[estado_actual])/2);
  Serial.print("sizeof(tabla_transiciones_estado_futuro): ");
  Serial.println(sizeof(tabla_transiciones_estado_futuro[0])/2);
  Serial.print("sizeof(tabla_output_por_estado): ");
  Serial.println(sizeof(tabla_output_por_estado[0])/2);
}

/**
 * Imprime en el monitor serial si con la entrada leida es necesario realizar un cambio de estado
 * 
 */
void imprimir_comparacion_estado(int i){
  Serial.print("iteracion ");
  Serial.print(i);
  Serial.print(": ");
  Serial.print(entrada);
  Serial.print(" == ");
  Serial.print(tabla_transiciones_estados[estado_actual][i]);
  Serial.print(" : ");
  Serial.println(entrada == tabla_transiciones_estados[estado_actual][i]);
}

/**
 * Imprime en el monitor serial el cambio de estado
 * 
 */
void imprimir_cambio_estado(){
  Serial.print("Cambio de estado! ");
  Serial.print("Estado actual: ");
  Serial.print(estado_actual);
  
  Serial.print(", salida: ");
  Serial.println(salida);
  Serial.print("Nuevo estado: ");
  Serial.println(estado_futuro);
}

/**
 * Imprime en el monitor serial el valor leido en decimal antes de modificarlo
 * 
 */
void imprimir_antes_suma_entrada(){
  Serial.print("entrada(antes): "); 
  Serial.print(entrada);
  Serial.print(" :: ");
}

/**
 * Imprime en el monitor serial el valor leido en decimal despues de modificarlo
 * 
 */
void imprimir_despues_suma_entrada(int i){
  Serial.print(i);
  Serial.print(": ");
  Serial.print(digitalRead(pin_entradas[i]));
  Serial.print("*");
  Serial.print(pow(2,i));
  Serial.print(" = ");
  Serial.print(digitalRead(pin_entradas[i])*pow(2,i));
  Serial.print(", ");
  Serial.print("entrada(despues): ");
  Serial.println(entrada);
}

/**
 * Imprime en el monitor serial la salida de la maquina, si un bit fue 0 o 1
 * 
 */
void imprimir_estado_salida(int i,int salida){
  Serial.print("salida >= (pow(2,i)): ");
  Serial.print(salida);
  Serial.print(" >= ");
  Serial.print((pow(2,i)));
  Serial.print(" : ");
  Serial.println(salida >= round(pow(2,i)) ? "HIGH" : "LOW");
}

/**
 * Imprime en el monitor serial tanto la salida como el estado actual de la maquina
 * 
 */
void imprimir_salida_i(int i,int estado){
  Serial.print("Salida ");
  Serial.print(i);
  Serial.print(": ");
  Serial.println(estado);
}
