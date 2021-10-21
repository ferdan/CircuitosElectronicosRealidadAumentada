/***************************************************

  PROGRAMA: 26072021

  Prueba y lectura de una maquina de estados finitos

  Este programa se ejecuta en conjunto con:

  ARDUINO (1): ARDUINO AR 65 Implemenracion FSM.ino 
  ARDUINO (2): ARDUINO AR 65 Prueba y Lectura FSM.ino 
  PYTHON:  Completo AR 65 FSM.py  (monitor) 25062021-P
  
  TARJETA UTILIZADA: Arduino Mega
  Opcional: Utilizar LEDs conresistencias para observar el funcionamiento del circuito
                 
  28 / julio / 2021
  
*****************************************************/


/**
 * ---------------------------------------------------------------------------------------------------------
 * Declaracion de arreglos de pines digitales
 * pin_escrituras[] -> son los pines en donde se escribiran las entradas a la maquina de estados finitos
 * pin_lecturas[] -> son los pines de donde se leeran las salidas de la maquina de estados finitos
 * pin_estados[] -> son los pines que leera el estado en el que se encuentra la maquina de estados finitos
 * 
 * Como se observa, se pueden implementar maquinas de estados con las siguientes caracteristicas:
 *  - Hasta cuatro entradas
 *  - Hasta cuatro salidas
 *  - Hasta 16 estados diferentes
 *  
 *  Este programa se puede expandir a pines, modificando los arreglos. 
 * ---------------------------------------------------------------------------------------------------------
 */
// Declare multiple analog pins:
// https://forum.arduino.cc/t/analog-pin-numbers-dont-match-standard-pinout-mega2560/610772/6
// See answer no.6 from david_2008

const int pin_escrituras[] = {2,3,4,5};
const int pin_lecturas[] = {6,7,8,9};
const byte pin_estados[] = {A0,A1,A2,A3};

/**
 * ---------------------------------------------------------------------------------------------------------
 * Declaracion de pines de control
 * pinCLK -> Define el pin del reloj que se utilizara para enviar pulsos de reloj a la maquina de estados
 * pinReset -> Define el pin de reset que inicializara la maquina de estados
 * ---------------------------------------------------------------------------------------------------------
 */
int pinCLK = 10;
int pinReset = 11;

/**
 * ---------------------------------------------------------------------------------------------------------
 * Variables para el control del tiempo de muestreo
 * lastime -> guarda el ultimo instante de tiempo en el que enviaron datos por el puerto serie
 * sampleTime -> duracion entre cada muestra tomada
 * numMuestras -> numero de muestras tomadas por cada curva
 * 
 * ---------------------------------------------------------------------------------------------------------
 */
unsigned long lastTime = 0;
unsigned long sampleTime = 100;
double firstTime = 0;

/**
 * ---------------------------------------------------------------------------------------------------------
 * Variables para la prueba de la maquina de estados
 * lectura -> Es el valor leido de la salida de la maquina
 * escritura -> Es el valor que se le escribe a la maquina
 * estado -> Es el valor leido del estado en el que se encuentra de la maquina
 * 
 * ---------------------------------------------------------------------------------------------------------
 */
int lectura = 0;
int escritura = 0;
int estado = 0;

// Ejemplo de un control para proteccion contra corto circuito para fuente de alimentacion
/**
 * tabla_vectores_escritura_prueba[] -> contiene las entradas a escribir a la maquina de estados finitos
 * 
 */
const int tabla_vectores_escritura_prueba[] = {0B000,0B100,0B101,0B111,0B101,0B100,0B110,0B100,0B100,0B000};

/**
 * Inicializa todos los pines a utilizar, inicializa el reloj, la frecuencia de operacion, la comunicacion serial y la comunicacion I2C para comunicarse con los dos PCF8591
 * Para cambiar la frecuenacia del PWM de pines en Arduino Mega:
 * https://forum.arduino.cc/t/mega-2560-pwm-frequency/71434/2
 * 
 */
void setup() {

  // Se limpian los registros que definen la frecuencia de los pines PWM
  int myEraser = 7;
  TCCR0B &= ~myEraser;
  TCCR1B &= ~myEraser;
  TCCR2B &= ~myEraser;
  TCCR3B &= ~myEraser;
  TCCR4B &= ~myEraser;

  // Se configuran los registros para la frecuencia de los pines PWM
  int myPrescaler = 3;
  TCCR0B |= myPrescaler;
  TCCR1B |= myPrescaler;
  TCCR2B |= myPrescaler;
  TCCR3B |= myPrescaler;
  TCCR4B |= myPrescaler;
  
  
  // Inicializa los pines en donde se leera el estado de la maquina 
  for(int i=0;i<sizeof(pin_estados)/sizeof(pin_estados[0]);i++)
  {
    pinMode(pin_estados[i],INPUT);
  }

  // Inicializa los pines en donde se escribiran las entradas de la maquina
  for(int i=0;i<sizeof(pin_escrituras)/sizeof(pin_escrituras[0]);i++)
  {
    pinMode(pin_escrituras[i],OUTPUT);
  }

  // Inicializa los pines en donde se leeran las salidas de la maquina
  for(int i=0;i<sizeof(pin_lecturas)/sizeof(pin_lecturas[0]);i++)
  {
    pinMode(pin_lecturas[i],INPUT);
  }

  // Se inicializan los pines del reloj y de reset
  pinMode(pinCLK,OUTPUT);
  pinMode(pinReset,OUTPUT);

  // Se inicializa la señal de reloj, escribiendo un voltaje PWM
  analogWrite(pinCLK,127);

  // --- Inicializa velocidad de transmision serial ---
  Serial.begin(9600);

  // Manda un pulso de reset para inicializar la maquina de estados finitos
  digitalWrite(pinReset,~HIGH);
  delay(sampleTime/50);
  digitalWrite(pinReset,~LOW);
  delay(sampleTime-sampleTime/50);

  firstTime = millis();

  // --- Sincronizacion de comunicacion serial ---
  Serial.println("inicio");
  leer_salidas();
  leer_estados();
  enviar_datos_seriales();

}

int i=0;

void loop() {
  // Obtiene el siguiente valor binario a escribir a la entrada de la maquina de estados finitos
  if(i<(sizeof(tabla_vectores_escritura_prueba)/2)-1) { i++; } else { i=0; }

  // Escribe a la entrada de la maquina uno de los valores de la tabla de vectores de prueba
  escritura = tabla_vectores_escritura_prueba[i];
  
  //imprimir_entrada_a_escribir();

  // Escribe un valor a la entrada de la maquina de estados finitos
  escribir_entradas();

  delay(20);
  // Lee la salida y el estado en el que se encuentra la maquina de estados finitos
  leer_salidas();
  leer_estados();

  // Envia datos por el puerto serial
  enviar_datos_seriales();

  delay(sampleTime);
}

/**
 * Envia el valor que se le envio a la maquina, la salida y el estado de misma
 * 
 */
void enviar_datos_seriales(){
  //Serial.print("Escritura: ");
  Serial.println(escritura);
  //Serial.print(" , Estado: ");
  Serial.println(estado);
  //Serial.print(" , Lectura: ");
  Serial.println(lectura);
}

/**
 * Escribe un valor en binario a la entrada de la maquina de estados finitos
 * Convierte el valor en decimal a escribir a binario
 * 
 */
void escribir_entradas()
{
  int temp = escritura;
  for(int i=(sizeof(pin_escrituras)/2)-1;i>=0;i--){
    //imprimir_estado_escritura(i,escritura);
    if(escritura>=(pow(2,i)))
    {
      escritura -= round(pow(2,i));
      digitalWrite(pin_escrituras[i],HIGH);
      //imprimir_escritura_i(i,1);
    }
    else
    {
      digitalWrite(pin_escrituras[i],LOW);
      //imprimir_escritura_i(i,0);
    }
  }
  escritura = temp;
}

/**
 * Lee un valor binario a la salida de la maquina de estados finitos
 * Convierte este valor en binario leido a un valor decimal
 * 
 */
void leer_salidas()
{
  lectura = 0x00;

  for(int i=0;i<sizeof(pin_lecturas)/2;i++){
    //imprimir_antes_suma_lectura();
    lectura += (byte)(digitalRead(pin_lecturas[i])*pow(2,i)+0.5);
    //imprimir_comparacion_estado(i);
  }
  //lectura = byte(lectura);
  //imprimir_despues_suma_lectura();
}

/**
 * Lee un valor binario correspondiente al estado de la maquina de estados finitos
 * Convierte este valor en binario leido a un valor decimal
 * 
 */
void leer_estados()
{
  estado = 0x00;
  for(int i=0;i<sizeof(pin_estados)/2;i++){

    //imprimir_pin_estados(i);
    estado += (byte)(digitalRead(pin_estados[i])*pow(2,i)+0.5);
  }
}

// Las siguientes subrutinas despliegan informacion extra sobre lo que ocurre en el programa

/**
 * Imprime en el monitor serial el estdao de los pines que leen el estado en el que se encuentra la maquina
 * 
 */
void imprimir_pin_estados(int i){
    Serial.print("pin_estados[");
    Serial.print(i);
    Serial.print("]: ");
    Serial.print(analogRead(pin_estados[1]));
    Serial.print(" : ");
    Serial.println(digitalRead(pin_estados[i]));
}

/**
 * Imprime en el monitor serial el valor de conversion a decimal antes de modificarlo
 * 
 */
void imprimir_antes_suma_lectura(){
  Serial.print("lectura(antes): "); 
  Serial.print(lectura);
  Serial.print(" :: ");
}

/**
 * Imprime en el monitor serial el valor de conversion a decimal despues de modificarlo
 * 
 */
void imprimir_despues_suma_lectura(){
  Serial.print("lectura(despues): ");
  Serial.println(lectura);
}

/**
 * Imprime en el monitor serial si algun bit de la lectua de salida fue 1 o 0
 * 
 */
void imprimir_comparacion_lectura(int i){
  Serial.print(i);
  Serial.print(": ");
  Serial.print(digitalRead(pin_lecturas[i]));
  Serial.print("*");
  Serial.print(pow(2,i));
  Serial.print(" = ");
  Serial.print(digitalRead(pin_lecturas[i])*pow(2,i));
  Serial.print(", ");
  Serial.print("lectura(despues): ");
  Serial.println(lectura);
}

/**
 * Imprime en el monitor serial la salida y el estado de la maquina despues de escribirle una entrada
 * 
 */
void imprimir_escritura_i(int i,int estado){
  Serial.print("Salida ");
  Serial.print(i);
  Serial.print(": ");
  Serial.println(estado);
}

/**
 * Imprime en el monitor serial si algun bit en la escritura de la entrada a la maquina fue 0 o 1
 * 
 */
void imprimir_estado_escritura(int i,int salida){
  Serial.print("escritura >= (pow(2,i)): ");
  Serial.print(escritura);
  Serial.print(" >= ");
  Serial.print((pow(2,i)));
  Serial.print(" : ");
  Serial.println(escritura >= round(pow(2,i)));
}

/**
 * Imprime en el monitor serial la entrada a escribir a la maquina
 * 
 */
void imprimir_entrada_a_escribir(int i){
  Serial.print("Entrada a escribir ");
  Serial.print(i);
  Serial.print(": ");
  Serial.println(tabla_vectores_escritura_prueba[i]);
}
