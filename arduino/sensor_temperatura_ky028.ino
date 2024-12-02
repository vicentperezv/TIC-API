#include <math.h> // Biblioteca para cálculos matemáticos

// Definiciones de pines
int ledPin = 2; // Pin donde está conectado el LED
byte NTCPin = A0; // Pin analógico de Arduino donde se conecta el pin AO del termistor
int sensorRuidoPin = 4; // Pin digital para el sensor de sonido KY-037 (DO)

// Pines para el LED RGB
int redpin = 11;   // seleccionar pin para el color rojo del LED
int greenpin = 10; // seleccionar pin para el color verde del LED
int bluepin = 9;   // seleccionar pin para el color azul del LED

// Parámetros del termistor
#define SERIESRESISTOR 10000
#define NOMINAL_RESISTANCE 50000
#define NOMINAL_TEMPERATURE 25
#define BCOEFFICIENT 3950

int val; // Variable para controlar los valores PWM
bool rgbActivo = false; // Variable para saber si el RGB está activo
bool ruidoActivo = false; // Variable para saber si el modo de sensor de ruido está activo

void setup() {
    Serial.begin(9600);          // Inicialización de la comunicación serial
    pinMode(ledPin, OUTPUT);     // Configuración del LED como salida
    digitalWrite(ledPin, LOW);   // Asegurarse de que el LED esté apagado al inicio

    // Configurar los pines RGB como salida
    pinMode(redpin, OUTPUT);
    pinMode(greenpin, OUTPUT);
    pinMode(bluepin, OUTPUT);

    // Configurar el pin del sensor de ruido como entrada
    pinMode(sensorRuidoPin, INPUT);
}

void loop() {
    // Leer comando desde la comunicación serial
    if (Serial.available() > 0) {
        String comando = Serial.readStringUntil('\n');

        if (comando == "modo1") {
            // Modo 1: Encender LED
            digitalWrite(ledPin, HIGH);
            Serial.println("Modo 1 activo: LED encendido");
        } 
        else if (comando == "modo2") {
            // Modo 2: Apagar LED
            digitalWrite(ledPin, LOW);
            Serial.println("Modo 2 activo: LED apagado");
        } 
        else if (comando == "modo3") {
            // Modo 3: Leer la temperatura del sensor NTC y enviarla por el puerto serial
            float ADCvalue = analogRead(NTCPin);
            float voltage = (ADCvalue * 5.0) / 1023.0;
            float resistance = (5.0 * SERIESRESISTOR / voltage) - SERIESRESISTOR;

            // Cálculo de la temperatura con Steinhart-Hart
            float steinhart;
            steinhart = resistance / NOMINAL_RESISTANCE;
            steinhart = log(steinhart);
            steinhart /= BCOEFFICIENT;
            steinhart += 1.0 / (NOMINAL_TEMPERATURE + 273.15);
            steinhart = 1.0 / steinhart;
            steinhart -= 273.15;

            // Enviar solo el valor numérico de la temperatura
            Serial.println(steinhart);
        } 
        else if (comando == "modo4") {
            // Modo 4: Activar el LED RGB y realizar animación
            rgbActivo = true;
            Serial.println("Modo 4 activo: RGB encendido y animando");
        } 
        else if (comando == "modo5") {
            // Modo 5: Desactivar el LED RGB
            rgbActivo = false;
            apagarRGB();
            Serial.println("Modo 5 activo: RGB apagado");
        }
        else if (comando == "modo6") {
            // Modo 6: Activar la respuesta al ruido
            ruidoActivo = true;
            Serial.println("Modo 6 activo: LED controlado por ruido");
        }
        else if (comando == "modo7") {
            // Modo 7: Desactivar la respuesta al ruido
            ruidoActivo = false;
            Serial.println("Modo 7 activo: Modo de ruido desactivado");
        }
        else {
            Serial.println("Comando no reconocido");
        }
    }

    // Si el RGB está activo, ejecutar la animación
    if (rgbActivo) {
        animarRGB();
    }

    // Si el modo ruido está activo, verificar si se detecta ruido y encender el LED
    if (ruidoActivo) {
        int ruidoDetectado = digitalRead(sensorRuidoPin);
        if (ruidoDetectado == HIGH) {
            digitalWrite(ledPin, HIGH);
        } else {
            digitalWrite(ledPin, LOW);
        }
    }
}

void animarRGB() {
    // Decrementamos los valores de PWM de 255 a 0
    for (val = 255; val > 0 && rgbActivo; val--) {
        analogWrite(redpin, val);
        analogWrite(greenpin, 255 - val);
        analogWrite(bluepin, 128 - val);
        delay(50);
    }

    // Incrementamos los valores de PWM de 0 a 255
    for (val = 0; val < 255 && rgbActivo; val++) {
        analogWrite(redpin, val);
        analogWrite(greenpin, 255 - val);
        analogWrite(bluepin, 128 - val);
        delay(50);
    }
}

void apagarRGB() {
    // Apagar todos los colores del LED RGB
    analogWrite(redpin, 0);
    analogWrite(greenpin, 0);
    analogWrite(bluepin, 0);
}

