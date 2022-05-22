import json
import math
import statistics
import time
from csv import writer
from datetime import datetime
import pandas as pd
import requests
import configuration
import smtplib
from email.message import EmailMessage

print("Temperature monitoring and Anomaly Detection Has Started...")
print("choose Your Messaging Platform from the Following")
print("1.Telegram\n2.Email")
platform = int(input())
while platform !=1 and platform != 2:
    platform = int(input("Enter a Valid Option:"))
if platform==1:
    print("You Have Choosen Telegram as Your Messaging Platform\n")
elif platform==2:
    print("You Have Choosen Email as Your Messaging Platform\n")


def send_message(message_,msgptfm):
    def telegram():
        url = "https://api.telegram.org/" + configuration.bot_id + "/sendMessage"
        data_ = {
            "chat_id": configuration.chat_id,
            "text": message_
        }
        try:
            response_ = requests.request("GET", url, params=data_)
            response_ = requests.post(url)
            telegram_data = json.loads(response_.text)
            return telegram_data["ok"]
        except Exception as exception:
            print("\nThere is an Error in sending Telegram Message......")
            print("This is the Error : ", exception)
    def email():
        body = message_
        msg = EmailMessage()
        msg.set_content(body)
        
        msg['subject'] = "Anomaly Detected"
        msg['to'] = configuration.to
        msg['from']= configuration.user

        server = smtplib.SMTP("smtp.gmail.com",587)
        server.starttls()
        server.login(configuration.user, configuration.password)
        server.send_message(msg)
        server.quit()
        return 'emailSent'
    def default():
        return 'Unknown'
    switcher = {
        1:telegram,
        2:email
        }
    def switch(case):
        return switcher.get(case,default)()
    switch(msgptfm)
            
def get_date_time():
    now = datetime.now()
    current_time_ = now.strftime("Date : %B %d, %Y \n Time : %H:%M:%S")
    return current_time_


def get_time_stamp():
    now = datetime.now()
    time_stamp = now.strftime("%d/%m/%y %H:%M:%S")
    return time_stamp


def store_data(List):
    with open('temperature_log.csv', 'a') as f:
        Writer = writer(f)
        Writer.writerow(List)
        f.close()
        print("Data Stored Successfully...")


def compute_bounds(frame_list):
    if len(frame_list) < configuration.frame_size:
        return None
    if len(frame_list) > configuration.frame_size:
        del frame_list[0: len(frame_list) - configuration.frame_size]

    Variance = statistics.variance(frame_list)
    print("Variance : ", Variance)
    Zn = configuration.Multiplication_factor * math.sqrt(Variance / len(frame_list))
    print("z-score : ", Zn)
    Higher_Bound = frame_list[-1] + Zn
    Lower_Bound = frame_list[-1] - Zn
    return [Higher_Bound, Lower_Bound]


def anomaly(sensorValue,flag):
    col_list = ['Timestamp', 'SensorValue', 'flag', 'HigherBound', 'LowerBound']
    df = pd.read_csv('temperature_log.csv', usecols=col_list)
    f_list = df['SensorValue']
    frame_list = [x for x in f_list if math.isnan(x) == False]

    bound = compute_bounds(frame_list)
    print("This are boundaries :", bound)
    if not bound:
        required_data_count = configuration.frame_size - len(frame_list)
        print("Not enough data to compute Z-score. Need ", required_data_count, " more data points")
        frame_list.append(int(sensorValue))
        return [0, 0,flag]

    time_ = get_date_time()
    if sensorValue > bound[0] and flag == 0:
        print("sensor value crossed boundary", bound[0])
        msg = "Something went Wrong with Temperature......\n Anomaly detected \n " + time_ + "\n Sensor Value : " + str(sensorValue) + "\n UpperBoundary : " + str(bound[0]) + "\n LowerBoundary : " + str(bound[1]) + "\n - RPi"
        print(msg)
        print("\nRequesting to send Message.....")
        returnResponse = send_message(msg,platform)
        print("Response : ", returnResponse)
        flag = 1
    elif sensorValue < bound[1] and flag == 0:
        print("sensor value crossed boundary", bound[1])
        msg = "Something went Wrong with Temperature......\n Anomaly detected \n " + time_ + "\n Sensor Value : " + str(sensorValue) + "\n UpperBoundary : " + str(bound[0]) + "\n LowerBoundary : " + str(bound[1]) + "\n - RPi"
        print(msg)
        print("\nRequesting to send Message......")
        returnResponse = send_message(msg,platform)
        print("Response : ", returnResponse)
        flag = 1
    else:
        print("No Anomaly Detected")
        flag = 0
    bound.append(flag)
    return bound
