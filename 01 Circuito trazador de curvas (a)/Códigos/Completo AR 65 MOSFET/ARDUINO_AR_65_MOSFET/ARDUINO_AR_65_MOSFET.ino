/***************************************************

  PROGRAMA: 28072021

  Trazador de curvas para un transistor MOSFET utilizando DACs

  Este programa se ejecuta en conjunto con:

  ARDUINO: ARDUINO_AR_65_MOSFET.ino (entradas) 08062021-A
  PYTHON:  Completo_AR_65_MOSFET.py  (monitor) 08062021-P
  
  TARJETA UTILIZADA: Arduino MEGA
  TRANSISTOR DE PRUEBA: 2N7000
  CONVERTIDORES DIGITALES ANALOGICOS UTILIZADOS: PCF8591
                 
  28 / julio / 2021
  
*****************************************************/

/**
 * ---------------------------------------------------------------------------------------------------------
 * PCF_Vgg -> controla el voltaje Vgg del trazador de curvas
 * PCF_Vdd -> controla el voltaje Vdd del trazador de curvas
 * ---------------------------------------------------------------------------------------------------------
 */
#include "Wire.h"
#define PCF_Vgg 0x48 // I2C bus address
#define PCF_Vdd 0x49 // I2C bus address

// **************************************************************
//     SELECCION DE MUESTRAS CON ó SIN 'Filtrado Circular'
//      'true' <- CON Filtrado || circular de 4 muestras
//      'false' <- SIN Filtrado
// **************************************************************
 boolean Filtrado_Circular = true;
// **************************************************************

/**
 * ---------------------------------------------------------------------------------------------------------
 * Declaracion de arreglos:
 * canales_medidos[4] -> son los voltajes analogicos medidos directamente del Arduino [0,1023]
 * voltajes[4] -> son los voltajes escalados del arreglo anterior [0,5]
 * corrientes[2] -> son las corrientes calculadas como la diferencia del arreglo de voltajes anterior
 * ---------------------------------------------------------------------------------------------------------
 */
const int numero_entradas_analogicas = 4;
int canales_medidos[numero_entradas_analogicas];
double voltajes[numero_entradas_analogicas];
double corrientes[2];

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
 * Definicion de pines para los 4 canales del ADC
 * PinVgg -> Es el voltaje a la salida del PCF_Vgg
 * PinVdd -> Es el voltaje a la salida del PCF_Vdd
 * PinVgs -> Es el voltaje en base-emisor del transistor MOSFET
 * PinVds -> Es el voltaje en colector-emisor del transistor MOSFET
 * 
 * NOTA: Entre Vgg y Vgs no hay resistencia
 *       Entre Vdd y Vds hay una resistencia Rc de 2.2 kohm (valor nominal)
 * ---------------------------------------------------------------------------------------------------------     
 */
const int PinVgg = A0;  // Pin de entrada analogica canal 0
const int PinVgs = A1;  // Pin de entrada analogica canal 1
const int PinVdd = A2;  // Pin de entrada analogica canal 2
const int PinVds = A3;  // Pin de entrada analogica canal 3

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
 * Vdd -> valor medido de la fuente de voltaje que se utiliza como alimentacion del trazador de curvas
 * Vth -> valor observado experimentalmente de la curva Id vs Vgs en donde se observa que comienza a crecer 
 *        el voltaje Vgs con respecto a la corriente Id (voltaje de umbral)
 * ---------------------------------------------------------------------------------------------------------
 */
const double Vdd=5.0;
const double Vth=1.8;

/**
 * ---------------------------------------------------------------------------------------------------------
 * i_muestra -> Indica el numero de la muestra que se toma. Para cada conjunto de muestras, puede variar 
 *              entre [0,numMuestras]
 * numero_curva -> Indica la curva de la cual se toman muestras. Las curvas con numero_curva = 0 hasta 3, 
 *                 se utilizan para graficar Id vs Vds. La curva con numero_curva = 4 se utiliza para 
 *                 graficar las demas curvas
 * barrido_recta -> Realiza un barrido con un numero de muestras igual a numMuestras para cada curva medida
 * voltaje_obtencion_curva -> Valor de voltaje propuesto Vdd en formato hexadecimal para las curvas Id vs Vds. 
 *                            Posteriormente, este mismo valor es Vgg para las demas curvas
 * ---------------------------------------------------------------------------------------------------------
 */
int i_muestra=0;
int numero_curva=0;
byte barrido_recta;
byte voltaje_obtencion_curva = 0x74;


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
 * Se miden cinco curvas para graficar Id vs Vds. Posteriormente se toma una ultima curva para graficar las demas curvas
 * 
 */
void loop() {
  // --- Toma muestras cada sampleTime ms ---
  if (millis()-lastTime > sampleTime) {
    
    lastTime = millis(); // Actualiza el tiempo de la ultima vez que se tomaron muestras

    if(numero_curva<5) // ¿Se toman muestras de las primeras 5 curvas para Id vs Vds?
    {
      int valor;
      // --- 5 Curvas para Id vs Vds [MOSFET] ---    
      valor = map(numero_curva,0,5,102,125); //probar tambien con 116 - 132
    
      establecer_voltaje_Vgg(valor);
      barrer_voltaje_Vdd();
    }
    else if(numero_curva==5)
    {
      // --- 1 Curva para Ig vs Vgs , Id vs Vgs , entre otras --- 
      establecer_voltaje_Vdd(255);
      barrer_voltaje_Vgg();
    }
    else
    {
      numero_curva = 0;
    }
  }
}

/**
 * Establece un valor de voltaje a Vgg en el PCF8591 correspondiente
 * @param valor -> Es un numero en formato hexadecimal [0,255] que representa un voltaje [0,5V]
 * 
 */
void establecer_voltaje_Vgg(int valor){
  Wire.beginTransmission(PCF_Vgg); // wake up PCF_Vgg
  Wire.write(0x40); // control byte - turn on DAC (binary 1000000)
  Wire.write(valor);
  Wire.endTransmission(); // end tranmission
}

/**
 * Establece un valor de voltaje a Vdd en el PCF8591 correspondiente
 * @param valor -> Es un numero en formato hexadecimal [0,255] que representa un voltaje [0,5V]
 * 
 */
void establecer_voltaje_Vdd(int valor){
  Wire.beginTransmission(PCF_Vdd); // wake up PCF_Vdd
  Wire.write(0x40); // control byte - turn on DAC (binary 1000000)
  Wire.write(valor);
  Wire.endTransmission(); // end tranmission
}

/**
 * Actualiza Vdd con diferentes valores de entre 0V y 5V
 * Despues envia por el puerto serie las muestras leidas
 * 
 */
void barrer_voltaje_Vdd(){
  // --- Barre durante 50 muestras ---
  for (int i_muestra=0; i_muestra<250; i_muestra+=5){
    establecer_voltaje_Vdd(i_muestra);
    leer_procesar_enviar_muestras();
  }
  numero_curva++; // Indica que se tomaran muestras de la siguiente curva
}

/**
 * Actualiza Vgg con diferentes valores de entre 0V y 5V
 * Despues envia por el puerto serie las muestras leidas
 * 
 */
void barrer_voltaje_Vgg(){
    // --- Transistor MOSFET: valores de Vgg mayores a Vth ---
    for (int i_muestra=0; i_muestra<150; i_muestra+=3){
      establecer_voltaje_Vgg(i_muestra);
      leer_procesar_enviar_muestras();
    }
  numero_curva++; // Indica que se tomaran muestras de la siguiente curva
}

/**
 * Lee los canales analogicos del circuito Vdd, Vds, Vgg y Vgs (4 voltajes)
 * Escala los canales al voltaje de la fuente de alimentacion
 * Calcula las corrientes a partir de la resta de voltajes
 * Envia los datos de todos los canales por el puerto serie
 * 
 */
void leer_procesar_enviar_muestras(){
    // --- Lecura de  los canales ---
    leer_canales(); // Lee los 4 voltajes del circuito
    
    // --- Escalamiento de canales ---
    escalar_canales(Vdd); // Escala los 4 voltajes leidos al voltaje de alimentacion Vdd
    
    // -- calculo de corrientes
    calcular_corrientes(); // Calcula las corrientes con los voltajes escalados
    
    // --- Transmision de cada valor al programa en Python ---
    enviar_datos_seriales(); // Envia los 4 voltajes escalados y las 2 corrientes calculadas
}

/**
 * Lee los 4 voltajes del circuito. [Vgg,Vgs,Vdd,Vds]
 * 
 */
void leer_canales()
{
  if (Filtrado_Circular)
  {
    // --- CON FILTRADO CIRCULAR con buffer circular de 32 muestras ---
    for (int b=0; b<bufferSize; b++)
    {
      canales_medidos[0] = analogRead(PinVgg); // Vgg
      canales_medidos[1] = analogRead(PinVgs); // Vgs
      canales_medidos[2] = analogRead(PinVdd); // Vdd
      canales_medidos[3] = analogRead(PinVds); // Vds
  
      // Filtrado circular en cada lectura. SIN mezclar muestras en tiempos diferentes
      agregar_lecturas_buffer(canales_medidos);
      promediador_lecturas_circular(canales_medidos);
    }
  } else {
    // --- SIN FILTRADO CIRCULAR ---
    canales_medidos[0] = analogRead(PinVgg); // Vgg
    canales_medidos[1] = analogRead(PinVgs); // Vgs
    canales_medidos[2] = analogRead(PinVdd); // Vdd
    canales_medidos[3] = analogRead(PinVds); // Vds

    for(int j=0; j<4; j++)
    {
      canales[j] = canales_medidos[j];
    }
  }
}

/**
 * Escala los 4 canales de voltaje, que varian entre [0,1023] a un numero que representa el voltaje [0,5]
 * 
 */
void escalar_canales(double Vdd_ref)
{
  for(int i=0;i<numero_entradas_analogicas;i++)
  {
    voltajes[i] = scaling(canales[i], 0, 1023, 0, Vdd_ref);  // Vgg,Vbs,Vdd,Vds
  }
}

/**
 * Calcula las corrientes con los valores de voltaje escalados [Ig,Id]
 * NOTA: Las corrientes Ig e Id no estan escaladas al valor medido de las resistencias Rg y Rd. 
 *       Solo son una diferencia de voltajes. Ig = Vgg - Vgs
 *                                            Id = Vdd - Vds
 * 
 */
void calcular_corrientes()
{
  for(int i=0;i<(numero_entradas_analogicas/2);i++)
  {
    corrientes[i] = (voltajes[i*2]-voltajes[i*2+1]); 
  }
}

/**
 * Envia todos los datos por el puerto serial
 * En orden, se envian: [Vgg,Vgs,Ig,Vdd,Vds,Id]
 * 
 */
void enviar_datos_seriales()
{
  for(int i=0;i<(numero_entradas_analogicas/2);i++)
  {
    Serial.println(voltajes[i*2],4); //Vgg,Vdd
    Serial.println(voltajes[i*2+1],4); //Vgs,Vds
    Serial.println(corrientes[i],4); //Ig,Id
  }
}

/**
 * Escala valores que se sabe que varian entre un intervalo definido [in_min,in_max] a otro intervalo [out_min,out_max]
 * @param x -> es el valor a escalar
 * @param in_min -> es el valor minimo que puede tomar x antes del escalado
 * @param in_max -> es el valor maximo que puede tomar x antes del escalado
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
//  FILTRO CIRCULAR (promediador) con buffer de 32 muetars 
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
