from scapy.all import *
from collections import defaultdict
import time
import subprocess
import json
import requests
from sklearn.ensemble import IsolationForest
import numpy as np
import time
import pandas as pd
import threading
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from collections import Counter

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["logs"]
collection = db["network_flows"]

ans = []

# 모델 초기화
model = IsolationForest(n_estimators=100, contamination=0.08, n_jobs = -1, random_state=42)

# 데이터 수집
data_count = 0
received_data = pd.DataFrame(columns=['tcp_packets', 'udp_packets', 'icmp_packets'])


url_tcp = "http://localhost:19999/api/v1/data?chart=ipv4.tcppackets&points=3&after=-3&options=seconds"
url_udp = "http://localhost:19999/api/v1/data?chart=ipv4.udppackets&points=3&after=-3&options=seconds"
url_icmp = "http://localhost:19999/api/v1/data?chart=ipv4.icmp&points=3&after=-3&options=seconds"

url_packets = "http://localhost:19999/api/v1/data?chart=ipv4.packets&points=3&after=-3&options=seconds"

ck = 0
cnt = 0

while 1:
    response_tcp = requests.get(url_tcp)
    tcp_data = response_tcp.json()["data"]
    tcp_sum = 0

    for d in tcp_data:
        tcp_sum += d[1]

    response_udp = requests.get(url_udp)
    udp_data = response_udp.json()["data"]
    udp_sum = 0

    for d in udp_data:
        udp_sum += d[1]


    response_icmp = requests.get(url_icmp)
    icmp_data = response_icmp.json()["data"]
    icmp_sum = 0

    for d in icmp_data:
        icmp_sum += d[1]
    
    
    packet_sum = 0
    packet_sum = packet_sum + udp_sum + tcp_sum + icmp_sum
    packet_sum = packet_sum * packet_sum


    if len(received_data) < 20:
        cnt = cnt + 1
        received_data.loc[len(received_data)] = [tcp_sum, udp_sum, icmp_sum]
        print(cnt)
    
    else:
        # 모델 학습
        if ck == 0:
            train_data = received_data.values
            model.fit(train_data)
            ck = 1
        else:
            # 새로운 데이터 포인트 예측
            new_data = np.array([[tcp_sum, udp_sum, icmp_sum]])
            score = model.decision_function(new_data)[0]
            preds = model.predict(new_data)
            #print(score)

            if preds[0] == -1:
                # 출력
                #print(f"Score: {score}")
                #print("Packet: ",tcp_sum,udp_sum,icmp_sum)
                #print()
                data = collection.find().sort("_id", -1).limit(200)

                pick_data = np.array([tcp_sum,udp_sum,icmp_sum])
 
                max_index = np.argmax(pick_data)
                if max_index == 0:
                    # 'TCP' 값을 포함하는 'flow_Summary' 필드에서 'destination_port' 값을 가져옵니다.
                    ports = [d['destination_port'] for d in data if 'flow_Summary' in d and 'TCP' in d['flow_Summary']]

                    # 가장 많이 등장한 값 3개를 구합니다.
                    top_ports = Counter(ports).most_common(5)
                    print("TCP Flood가 의심됩니다.")
                    print("의심 포트: ", top_ports)

                elif max_index == 1:
                    # 'UDP' 값을 포함하는 'flow_Summary' 필드에서 'destination_port' 값을 가져옵니다.
                    ports = [d['destination_port'] for d in data if 'flow_Summary' in d and 'UDP' in d['flow_Summary']]

                    # 가장 많이 등장한 값 3개를 구합니다.
                    top_ports = Counter(ports).most_common(5)
                    print("UDP Flood가 의심됩니다.")
                    print("의심 포트: ", top_ports)

                else:
                    # 'TCP' 값을 포함하는 'flow_Summary' 필드에서 'destination_port' 값을 가져옵니다.
                    ports = [d['destination_port'] for d in data if 'flow_Summary' in d and 'ICMP' in d['flow_Summary']]

                    # 가장 많이 등장한 값 3개를 구합니다.
                    top_ports = Counter(ports).most_common(5)
                    print("ICMP Flood가 의심됩니다.")
                    print("의심 포트: ",top_ports)
                print()
    time.sleep(3)
