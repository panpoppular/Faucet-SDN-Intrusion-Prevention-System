#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

#define OLED_RESET LED_BUILTIN
Adafruit_SSD1306 display(OLED_RESET);

/* Put your SSID & Password */
const char* ssid = "********";  // Enter SSID here
const char* password = "******";  //Enter Password here

/* Put IP Address details */
IPAddress local_ip(192,168,5,50);
IPAddress gateway(192,168,5,1);
IPAddress subnet(255,255,255,0);
IPAddress dns(192,168,5,1);
ESP8266WebServer server(80);

int pin = 14; //GPIO14 D5
unsigned long duration;
unsigned long starttime;
unsigned long sampletime_ms = 5000; //30sec
unsigned long lowpulseoccupancy = 0;
float ratio = 0;
float concentration = 0;

String SendHTML(){
  String ptr = "<!DOCTYPE html> <html>\n";
  ptr +="<head><meta http-equiv='refresh' content='2' name=\"viewport\" content=\"width=device-width, initial-scale=1.0, user-scalable=no\">\n";
  ptr +="<title>Web server</title>\n";
  ptr +="<style>html { font-family: Helvetica; display: inline-block; margin: 0px auto; text-align: center;}\n";
  ptr +="body{margin-top: 50px;} h1 {color: #444444;margin: 50px auto 30px;} h3 {color: #444444;margin-bottom: 50px;}\n";
  ptr +=".button {display: block;width: 240px;background-color: #1abc9c;border: none;color: white;padding: 13px 30px;text-decoration: none;font-size: 25px;margin: 0px auto 35px;cursor: pointer;border-radius: 4px;}\n";
  ptr +=".button-on {background-color: #1abc9c;}\n";
  ptr +=".button-on:active {background-color: #16a085;}\n";
  ptr +=".button-off {background-color: #34495e;}\n";
  ptr +=".button-off:active {background-color: #2c3e50;}\n";
  ptr +="p {font-size: 14px;color: #888;margin-bottom: 10px;}\n";
  ptr +="</style>\n";
  ptr +="</head>\n";
  ptr +="<body>\n";
  ptr +="<h1>ESP8266 Web server</h1>\n";
  
  ptr += "<a class=\"button button-on\" href=\"/\">";
  ptr += String(concentration) + " pcs/0.01cf";
  ptr += "</a>\n";

  ptr +="</body>\n";
  ptr +="</html>\n";
  return ptr;
}

void handle_OnConnect() {
  server.send(200, "text/html", SendHTML()); 
}

void handle_NotFound(){
  server.send(404, "text/plain", "404 Not found");
}

void setup() {
  Serial.begin(115200);
  //   pinMode(LED1pin, OUTPUT);
  //   pinMode(LED2pin, OUTPUT);

  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.display();
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.println("initializing");
  display.display();

  WiFi.config(local_ip, dns, gateway, subnet);
  WiFi.begin(ssid, password);
  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(WiFi.localIP());

  pinMode(pin,INPUT);

  server.on("/", handle_OnConnect);
  server.onNotFound(handle_NotFound);

  server.begin();
  Serial.println("HTTP server started");
  display.clearDisplay();

  starttime = millis();
}
void loop() {
  server.handleClient();
  
  duration = pulseIn(pin, LOW);
  lowpulseoccupancy = lowpulseoccupancy+duration;
  
  if ((millis()-starttime) > sampletime_ms) {
    ratio = lowpulseoccupancy/(sampletime_ms*10.0);  // Integer percentage 0=>100
    concentration = 1.1*pow(ratio,3)-3.8*pow(ratio,2)+520*ratio+0.62; // using spec sheet curve
    Serial.print(lowpulseoccupancy);
    Serial.print(", ");
    Serial.print(ratio);
    Serial.print(", ");
    Serial.println(concentration);
    display.clearDisplay();
    display.setCursor(2, 12);
    display.println(String(concentration) + " pcs/0.01cf");
    display.display();
    lowpulseoccupancy = 0;
    starttime = millis();
  }
}
