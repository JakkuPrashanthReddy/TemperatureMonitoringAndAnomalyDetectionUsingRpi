#include <ESP8266WiFi.h>
#include <PubSubClient.h>

float sensorValue =0;
float TemperatureC=0;
float TemperatureF=0;
float TemperatureK=0;
int SensorPin = A0;

const char* ssid = "xxxxxxxxxx";          // your network SSID (name)
const char* password = "xxxxxxxxxxxxx";   // your network password
const char* mqtt_server = "192.168.225.71"; // MQTT broker IP address

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() 
{
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) 
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}
void reconnect() 
{
  // Loop until we're reconnected
  while (!client.connected()) 
  {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("arduinoClient_temperature_sensor")) 
    {
      Serial.println("connected");
    } 
    else 
    {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void setup()
{
  //Set the pin mode
  pinMode(SensorPin, INPUT);
  pinMode(LED_BUILTIN,OUTPUT);
  //Set and start the serial port
  Serial.begin(115200);
  setup_wifi(); 
  client.setServer(mqtt_server, 1883);
}

void loop()
{
  sensorValue = analogRead(SensorPin);
  Serial.print("sensorvalue:");
  Serial.print(sensorValue);
  TemperatureC=(330*sensorValue)/1024;     // 330 when connected to 3v3 and 500 when connected to 5v
  Serial.println();
  Serial.print("Temp - ");
  Serial.print(TemperatureC);Serial.print("°C | ");
  TemperatureF = TemperatureC * 9/5 + 32 ;
  Serial.print(TemperatureF);Serial.print("°F | ");
  TemperatureK = TemperatureC + 273.15;
  Serial.print(TemperatureK);Serial.print("K");
  Serial.println(" ");
  if (!client.connected()) 
  {
    reconnect();
  }
  client.loop();
  client.publish("temp", String(TemperatureC).c_str());
  digitalWrite(LED_BUILTIN,HIGH);
  delay(1000); // Delay to watch better the results
  digitalWrite(LED_BUILTIN,LOW);
}
