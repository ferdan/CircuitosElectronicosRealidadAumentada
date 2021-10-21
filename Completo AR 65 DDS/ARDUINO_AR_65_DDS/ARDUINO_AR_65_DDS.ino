/***************************************************

  PROGRAMA: 08062021

  Trazador de curvas para un circuito DDS

  Este programa se ejecuta en conjunto con:

  ARDUINO: ARDUINO AR 65 DDS.ino (entradas) 25062021-A
  PYTHON:  Completo AR 65 DDS.py  (monitor) 25062021-P
  
  TARJETA UTILIZADA: Arduino Megao2560
  CONVERTIDORES DIGITALES ANALOGICOS UTILIZADOS: PCF8591
                 
  8 / junio / 2021
  
*****************************************************/

#include "Wire.h"
#define PCF_DDS 0x48 // I2C bus address

// **************************************************************

// **************************************************************
//     SELECCION DE MUESTRAS CON ó SIN 'Filtrado Circular'
//      'true' <- CON Filtrado || circular de 4 muestras
//      'false' <- SIN Filtrado
// **************************************************************
 boolean Filtrado_Circular = false;
// **************************************************************

/**
 * ---------------------------------------------------------------------------------------------------------
 * Declaracion de arreglos:
 * numero_entradas_analogicas -> indica el numero de canales analogicos a leer del circuito
 * canales_medidos[2] -> son los voltajes analogicos medidos directamente del Arduino [0,1023]
 * voltajes[2] -> son los voltajes escalados del arreglo anterior [0,5]
 * ---------------------------------------------------------------------------------------------------------
 */
const int numero_entradas_analogicas = 2;
int canales_medidos[numero_entradas_analogicas];
double voltajes[numero_entradas_analogicas-1];
/**
 * ---------------------------------------------------------------------------------------------------------
 *   Definicion de variables para el cálculo del FILTRO CIRCULAR (Promediador)
 *   Este filtro permite promediar cada lectura analogica de arduino mediante un filtro circular
 *   buffer_promediador[bufferSize]
 *   bufferSize = tamaño del buffer
 * ---------------------------------------------------------------------------------------------------------
 */
 const int bufferSize = 32;  // Numero de muestras a promediar
 int promedios_calculados[numero_entradas_analogicas];
 int buffer_promediador[numero_entradas_analogicas][bufferSize];
 int index[numero_entradas_analogicas];
 int canales[numero_entradas_analogicas];

/**
 * ---------------------------------------------------------------------------------------------------------
 * Definicion del pin de la señal senoidal
 * PinDDS -> Es el voltaje a la salida del PCF_DDS
 * ---------------------------------------------------------------------------------------------------------     
 */
const int PinDDS = A0;  // Pin de entrada senoidal

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
unsigned long sampleTime = 100;
const double numMuestras = 50;

/**
 * ---------------------------------------------------------------------------------------------------------
 * Vcc -> valor medido de la fuente de voltaje que se utiliza como alimentacion del trazador de curvas
 * ---------------------------------------------------------------------------------------------------------
 */
const double Vcc=5.0;

/**
 * ---------------------------------------------------------------------------------------------------------
 * i_muestra -> Indica el numero de la muestra que se toma. Para cada conjunto de muestras, puede variar 
 *              entre [0,numMuestras]
 * sine -> Realiza un barrido con un numero de muestras igual a numMuestras para cada curva medida
 * ---------------------------------------------------------------------------------------------------------
 */
int i_muestra=0;
byte sine;

/**
 * Inicializa tanto la comunicacion serial como la comunicacion I2C para comunicarse con los dos PCF8591
 * 
 */
void setup() {
  Wire.begin();
  // --- Inicializa velocidad de transmision serial ---
  Serial.begin(9600);

  // --- Sincronizacion de comunicacion serial ---
  Serial.println("inicio");
}

/**
 * Se mide al menos una curva para graficar la senal senoidal. 
 * 
 */
void loop() {
  // --- Toma muestras cada sampleTime ms ---
  if (millis()-lastTime > sampleTime) {
    lastTime = millis(); // Actualiza el tiempo de la ultima vez que se tomaron muestras
    barrer_voltaje_senoidal();
  }
}

/**
 * Obtiene el valor binario entre 0x00 y 0xFF a partir de la ecuacion de la forma de onda senoidal
 * 
 */
void barrer_voltaje_senoidal(){
  // --- Barre durante 50 muestras ---
  for (int i_muestra=0; i_muestra<250; i_muestra+=5){
    sine = byte(127.5*(1+sin((1000/sampleTime)*TWO_PI*i_muestra/(numMuestras-1))));
    establecer_voltaje_senoidal(sine);

    leer_procesar_enviar_muestras();
  }
}

/**
 * Establece el valor binario en el PCF8591. Este valor binario sera convertido a un voltaje 
 * @param valor -> Es un numero en formato hexadecimal [0,255] que representa un voltaje [0,5V]
 * 
 */
void establecer_voltaje_senoidal(int valor){
  Wire.beginTransmission(PCF_DDS); // wake up PCF_Vcc
  Wire.write(0x40); // control byte - turn on DAC (binary 1000000)
  Wire.write(valor);
  Wire.endTransmission(); // end tranmission
}

/**
 * Realiza la lectura, escalado y envio de datos por el puerto serial
 * 
 */
void leer_procesar_enviar_muestras(){
  // --- Lecura de  los canales ---
    lectura_canales(); // Lee el voltaje senoidal del circuito
    
    // --- Escalamiento de canales ---
    escalar_canales(Vcc); // Escala el voltaje senoidal leido al voltaje de alimentacion Vcc
    
    // --- Transmision de cada valor al programa en Python ---
    enviar_datos_seriales(); // Envia el voltaje senoidal
}

/**
 * Lee el voltaje senoidal del circuito.
 * 
 */
void lectura_canales()
{
  canales_medidos[0] = analogRead(PinDDS);
  canales_medidos[1] = sine;
  
  if (Filtrado_Circular)
  {
     // --- CON FILTRADO CIRCULAR con buffer circular de 32 muestras ---
    for (int b=0; b<bufferSize; b++)
    {
      // Filtrado circular en cada lectura. SIN mezclar muestras en tiempos diferentes
      agregar_lecturas_buffer(canales_medidos);
      promediador_lecturas_circular(canales_medidos);
    }
  } else {
    // --- SIN FILTRADO CIRCULAR ---
    for(int j=0; j<numero_entradas_analogicas; j++)
    {
      canales[j] = canales_medidos[j];
    }
  }
}

/**
 * Escala el canal de voltaje senoidal, que varia entre [0,1023] a un numero que representa el voltaje [0,5]
 * 
 */
void escalar_canales(double Vcc_ref)
{
  voltajes[0] = scaling(canales[0], 0, 1023, 0, Vcc_ref);
}

/**
 * Envia todos los datos por el puerto serial
 * En orden, se envia: 
 *    1. Voltaje de la senal senoidal
 *    2. Numero en binario que genera ese voltaje
 * 
 */
void enviar_datos_seriales()
{
  Serial.println(voltajes[0]); // Voltaje
  Serial.println(canales[1]); // Valor binario
}

/**
 * Escala valores que se sabe que varian entre un intervalo definido [in_min,in_max] a otro intervalo [out_min,out_max]
 * @param x -> es el valor a escalar
 * @param in_min -> es el valor minimo que puede tomar x
 * @param in_max -> es el valor maximo que puede tomar x
 * @param out_min -> es el valor minimo al cual se escala x
 * @param out_max -> es el valor maximo al cual se escala x
 * 
 */
float scaling(float x, float in_min, float in_max, float out_min, float out_max)
{
  return (x-in_min)*(out_max-out_min)/(in_max-in_min)+out_min;
}

// *******************************************************************
//
//  FILTRO CIRCULAR (promediador) con buffer de 32 muestras 
//
// *******************************************************************
// --- Inicializacion del buffer ---
void agregar_lecturas_buffer(int canales_medidos[])
{
  for(int i=0; i<numero_entradas_analogicas; i++)
  {
    buffer_promediador[i][index[i]] = canales_medidos[i];
    index[i] += 1;
    if (index[i] >= bufferSize) index[i] = 0;
  }
}

// --- Filtro circular: promediador ---
void promediador_lecturas_circular(int canales_medidos[])
{
  for(int i=0; i<numero_entradas_analogicas; i++)
  {
    long sum = 0;
    for (int k=0; k<bufferSize; k++)
    {
      sum += buffer_promediador[i][k];
    }
    canales[i] = (int)(sum/bufferSize);
  }
}
