import time
import json
import requests

from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.cluster import KMeans
from sklearn.covariance import EllipticEnvelope

import numpy as np
import time
import pandas as pd

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from collections import Counter

from progress.bar import IncrementalBar


# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["logs"]
collection = db["network_flows"]

ans = []


print("\033[95m  ___  ______  _____  _____  _____ ")
print(" / _ \ | ___ \|  __ \|  _  |/  ___|")
print("/ /_\ \| |_/ /| |  \/| | | |\ `--. ")
print("|  _  ||    / | | __ | | | | `--. \\")
print("| | | || |\ \ | |_\ \\ \_/ //\__/ /")
print("\_| |_/\_| \_| \____/ \___/ \____/ ")
print("                                   \033[0m")
print()

print("┌─────────────────────────────────────┐")
print("│   Network Anomaly Detection(v1.0)   │")
print("│                                     │")
print("│Observability Platform: Cilium Hubble│")
print("│Packet Collection: Netdata API       │")
print("│DataBase: MONGO DB                   │")
print("│                                     │")
print("│==========Detectable Attack==========│")
print("│                                     │")
print("│1. TCP Flood                         │")
print("│2. UDP Flood                         │")
print("│3. ICMP Flood                        │")
print("│4. PORT Scanning                     │")
print("│5. Other packet count-based attacks  │")
print("│                                     │")
print("│============How to use it============│")
print("│                                     │")
print("│1. Select the model to use           │")
print("│2. Enter learning time (seconds)     │")
print("│3. Port output if Anomaly Detected   │")
print("└─────────────────────────────────────┘")

print()

print("╔═════════════════════════════════════╗")
print("║               <MODEL>               ║")
print("║                                     ║")
print("║       [1] Isolation Forest          ║")
print("║       [2] OneClassSVM               ║")
print("║       [3] Robust Covariance         ║")
print("║       [4] KMeans                    ║")
print("║                                     ║")
print("╚═════════════════════════════════════╝")
print()

m_pick = int(input("Please select a model: "))
print()
d_len = int(input("Enter learning time (seconds): "))
print()
if m_pick == 1:
    # 모델 IF
    print("Model: Isolation Forest")
    print()
    model = IsolationForest(n_estimators=100, contamination=0.01, n_jobs = -1, random_state=42)

elif m_pick == 2:
    print("Model: OneClassSVM")
    print()
    model = OneClassSVM(kernel='rbf', nu=0.01)

elif m_pick == 3:
    print("Model: Robust Covariance")
    print()
    model = EllipticEnvelope(contamination=0.01)

elif m_pick == 4:
    print("Model: KMeans")
    print()
    model = KMeans(n_clusters=10, n_init=10, max_iter=300, random_state=42)

print()
# 데이터 수집
data_count = 0
#received_data = pd.DataFrame(columns=['tcp_packets', 'udp_packets', 'icmp_packets'])
received_data = pd.DataFrame(columns=['packets'])

url_tcp = "http://localhost:19999/api/v1/data?chart=ipv4.tcppackets&points=1&after=-1&options=seconds"
url_udp = "http://localhost:19999/api/v1/data?chart=ipv4.udppackets&points=1&after=-1&options=seconds"
url_icmp = "http://localhost:19999/api/v1/data?chart=ipv4.icmp&points=1&after=-1&options=seconds"

url_packets = "http://localhost:19999/api/v1/data?chart=ipv4.packets&points=1&after=-1&options=seconds"

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

    if len(received_data) < d_len:
        print("\033[A\033[A")
        with IncrementalBar('Processing', max=d_len) as bar:
            cnt = cnt + 1
            bar.next(cnt)
        #received_data.loc[len(received_data)] = [tcp_sum, udp_sum, icmp_sum]
        received_data.loc[len(received_data)] = [packet_sum]
    else:
        # 모델 학습
        if ck == 0:
            train_data = received_data.values
            model.fit(train_data)
            ck = 1
        else:
            # 새로운 데이터 포인트 예측
            new_data = np.array([[tcp_sum, udp_sum, icmp_sum]])
            new_data = np.array([[packet_sum]])
            #score = model.decision_function(new_data)[0]

            preds = model.predict(new_data)
            #print(preds)
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
                    top_ports = Counter(ports).most_common(3)
                    print("┌──────────────────────────────────────────┐")
                    print("│TCP Flood!                                │")
                    print(f"│Port: {', '.join(str(port) for port in top_ports).ljust(36)}│")
                    print(f"│TCP Packet: \033[95m{str(int(tcp_sum)).ljust(30)}\033[0m│")
                    print("└──────────────────────────────────────────┘")
                    print()

                elif max_index == 1:
                    # 'UDP' 값을 포함하는 'flow_Summary' 필드에서 'destination_port' 값을 가져옵니다.
                    ports = [d['destination_port'] for d in data if 'flow_Summary' in d and 'UDP' in d['flow_Summary']]

                    # 가장 많이 등장한 값 3개를 구합니다.
                    top_ports = Counter(ports).most_common(3)
                    print("┌──────────────────────────────────────────┐")
                    print("│UDP Flood!                                │")
                    print(f"│Port: {', '.join(str(port) for port in top_ports).ljust(36)}│")
                    print(f"│UDP Packet: \033[95m{str(int(udp_sum)).ljust(30)}\033[0m│")
                    print("└──────────────────────────────────────────┘")
                    print()
                        

                else:
                    #ports = [d['destination_port'] for d in data if 'flow_Summary' in d and 'ICMP' in d['flow_Summary']]

                    # 가장 많이 등장한 값 3개를 구합니다.
                    #top_ports = Counter(ports).most_common(3)
                    print("┌──────────────────────────────────────────┐")
                    print("│ICMP Flood!                               │")
                    print(f"│ICMP Packet: \033[95m{str(int(icmp_sum)).ljust(29)}\033[0m│")
                    print("└──────────────────────────────────────────┘")
                    print()
                print()
    time.sleep(1)
