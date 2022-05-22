import paho.mqtt.client as mqttClient
import time
import AnomalyDetection
import configuration


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected 
        Connected = True  # Signal connection
    else:
        print("Connection failed")

def on_message(client, userdata, msg):
    print("\nMessage received: " + msg.payload.decode())
    sensor_value = float(msg.payload.decode())
    LIST = [AnomalyDetection.get_time_stamp(), sensor_value]
    flag = 0
    print("This is the Sensor Value : ", sensor_value)
    if sensor_value <= configuration.minimum:
        if flag != 1:
            current_time = AnomalyDetection.get_date_time()
            message = "Anomaly detected in Temperature \n " + str(current_time) + "\n Sensor Value : " + str(sensor_value) + "\n - RPi"
            print("\nRequesting to send Message...")
            return_response = AnomalyDetection.send_message(message,AnomalyDetection.platform)
            print("Return Response : ", return_response)
        flag = 1
    elif sensor_value >= configuration.maximum:
        if flag != 1:
            current_time = AnomalyDetection.get_date_time()
            message = "Anomaly detected in Temperature \n " + str(current_time) + "\n Sensor Value : " + str(sensor_value) + "\n - RPi"
            print("\nRequesting to send Message....")
            return_response = AnomalyDetection.send_message(message,AnomalyDetection.platform)
            print("Return Response : ", return_response)
        flag = 1
    else:
        flag = 0
    anomalyData = AnomalyDetection.anomaly(sensor_value,flag)
    flag = anomalyData[2]
    LIST.append(flag)
    LIST.append(anomalyData[0])
    LIST.append(anomalyData[1])
    AnomalyDetection.store_data(LIST)
    LIST.clear()


Connected = False  
broker_address = "192.168.225.71"  # Broker address
port = 1883  # Broker port


client = mqttClient.Client("Rpi")
client.on_connect = on_connect 
client.on_message = on_message 
client.connect(broker_address, port=port,keepalive=600)
client.loop_start()
time.sleep(4)

while not Connected:  # Wait for connection
    time.sleep(0.1)
client.subscribe("temp")

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("exiting")
    client.disconnect()
    client.loop_stop()
