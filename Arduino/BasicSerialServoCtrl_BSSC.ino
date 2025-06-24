#include <Servo.h>

// Freenove Hexapod V2/Mega2560 manual servo test
// Send "S:{index}:{angle}" over Serial to control servos
// Send +V to enable verbosity/serial text output, -V to disable it.

#define DEBUG_SERIAL Serial  // Change to Serial1, Serial2, or Serial3 if ESP/RF24 is using pins 0/1 or if you need to change serial output(text/feedback) port.


//Servo count. if you add or remove servos, make sure to change the servoPins array to reflect the amount and proper PWM/control pins for the new servos. 
const int NUM_SERVOS = 18;
Servo servos[NUM_SERVOS];
int lastAngles[NUM_SERVOS];
bool verbose = false;  // Serial output toggle



// PWM/Control pins for servos
const int servosPins[NUM_SERVOS] = {
  22, 23, 24, 25, 26, 27, 28, 29, 30,
  31, 32, 33, 34, 35, 36, 37, 38, 39
};


//power pins for servos
const int servosPowersPins[] = { A15, A14, A13 };


void setup() {
  DEBUG_SERIAL.begin(115200);

  for (int i = 0; i < 3; i++) {
    pinMode(servosPowersPins[i], OUTPUT);
    digitalWrite(servosPowersPins[i], HIGH);
  }

  for (int i = 0; i < NUM_SERVOS; i++) {
    servos[i].attach(servosPins[i]);
    lastAngles[i] = -1;
  }

  DEBUG_SERIAL.println("Boot complete. Send +V to enable output.");
}

void loop() {
  if (DEBUG_SERIAL.available()) {
    String input = DEBUG_SERIAL.readStringUntil('\n');
    input.trim();  // Remove newline/whitespace

    // Verbosity control
    if (input == "+V") {
      verbose = true;
      DEBUG_SERIAL.println("Verbosity ON");
      return;
    }
    if (input == "-V") {
      verbose = false;
      DEBUG_SERIAL.println("Verbosity OFF");
      return;
    }

    // Servo control: S:{index}:{angle}
    if (input.startsWith("S:")) {
      int first = input.indexOf(':');
      int second = input.indexOf(':', first + 1);
      int index = input.substring(first + 1, second).toInt();
      int angle = input.substring(second + 1).toInt();

      if (index >= 0 && index < NUM_SERVOS) {
        if (lastAngles[index] != angle) {
          servos[index].write(angle);
          lastAngles[index] = angle;

          if (verbose) {
            DEBUG_SERIAL.print("Moved servo ");
            DEBUG_SERIAL.print(index);
            DEBUG_SERIAL.print(" to ");
            DEBUG_SERIAL.println(angle);
          }
        } else if (verbose) {
          DEBUG_SERIAL.print("Servo ");
          DEBUG_SERIAL.print(index);
          DEBUG_SERIAL.print(" already at ");
          DEBUG_SERIAL.println(angle);
        }
      } else if (verbose) {
        DEBUG_SERIAL.println("Invalid servo index.");
      }
    }

    // Clear buffer
    while (DEBUG_SERIAL.available()) DEBUG_SERIAL.read();
  }
}
