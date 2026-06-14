#include <WiFi.h>
#include <WebServer.h>
#include "HX711.h"

#define DT 4
#define SCK 5

HX711 scale;
WebServer server(80);

const char* ssid = "ESP32_Loadcell";
const char* password = "12345678";

float calibration_factor = 420.0;

// ===== VAR =====
float lastWeight = 0;
unsigned long lastTime = 0;

// ===== HTML UI =====
String html = R"rawliteral(

)rawliteral";


// ===== ROUTE =====
void handleRoot(){
  server.send(200,"text/html",html);
}

void handleData(){

  float weight = scale.get_units(2); // gram
  unsigned long now = millis();

  float dt = (now - lastTime) / 1000.0;
  float acc = 0;

  if(dt > 0){
    float dw = weight - lastWeight;

    // FILTER NOISE
    if(abs(dw) < 1.5) dw = 0;

    acc = (dw / 1000.0) / dt;
  }

  lastWeight = weight;
  lastTime = now;

  float m = weight / 1000.0;
  float g = 9.8;
  float apparent = m * g;

  String json = "{";
  json += "\"massa\":" + String(m,3) + ",";
  json += "\"percepatan\":" + String(acc,3) + ",";
  json += "\"berat\":" + String(apparent,3);
  json += "}";

  server.send(200,"application/json",json);
}

// ===== SETUP =====
void setup(){
  Serial.begin(115200);

  scale.begin(DT,SCK);
  scale.set_scale(calibration_factor);
  scale.tare();

  WiFi.softAP(ssid,password);

  server.on("/",handleRoot);
  server.on("/data",handleData);

  server.begin();
}

// ===== LOOP =====
void loop(){
  server.handleClient();
}