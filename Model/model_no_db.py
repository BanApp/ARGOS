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


def extract_data(data, new_data, prefix):
    if isinstance(data, list):
        for index, item in enumerate(data):
            extract_data(item, new_data, prefix + str(index) + "_")
    elif isinstance(data, dict):
        for key, value in data.items():
            if key in ["source_port", "destination_port"]:
                new_key = key + ' '
            else:
                new_key = prefix + key.replace("'", '"') + "_"
            extract_data(value, new_data, new_key)
    else:
        new_key = prefix[:-1].replace("'", '"')
        new_data[new_key] = data


prev_tcp_ports = []
prev_udp_ports = []
prev_icmp_ports = []

while 1:
    command_flow = "hubble observe --output=json"
    result = subprocess.run(command_flow, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ans = result.stdout.decode()
    ans = ans.split("\n")

    # TCP, UDP, ICMP 포트를 저장할 리스트 초기화
    tcp_ports = []
    udp_ports = []
    icmp_ports = []

    for i in ans:
        new_data = {}
        try:
            json_data = json.loads(i)
            extract_data(json_data, new_data, "")
            # TCP, UDP, ICMP 포트를 저장할 리스트 초기화
            d = new_data
            summary = d['flow_Summary']

            if 'TCP' in summary and d['destination_port'] not in tcp_ports:
                tcp_ports.append(d['destination_port'])
            if 'UDP' in summary and d['destination_port'] not in udp_ports:
                udp_ports.append(d['destination_port'])
            if 'ICMP' in summary and d['destination_port'] not in icmp_ports:
                icmp_ports.append(d['destination_port'])
            t = d['time']    
        except:
            pass
    
    common_tcp_ports = list(set(tcp_ports) & set(prev_tcp_ports))
    common_udp_ports = list(set(udp_ports) & set(prev_udp_ports))
    common_icmp_ports = list(set(icmp_ports) & set(prev_icmp_ports))

    prev_tcp_ports = tcp_ports.copy()
    prev_udp_ports = udp_ports.copy()
    prev_icmp_ports = icmp_ports.copy()

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


    if len(received_data) < 100:
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
                
                pick_data = np.array([tcp_sum,udp_sum,icmp_sum])
 
                max_index = np.argmax(pick_data)
                if max_index == 0:
                    print("TCP Flood가 의심됩니다.")
                    print("의심 포트: ", *common_tcp_ports)

                elif max_index == 1:
                    print("UDP Flood가 의심됩니다.")
                    print("의심 포트: ", *common_udp_ports)

                else:
                    print("ICMP Flood가 의심됩니다.")
                    print("의심 포트: ",*common_icmp_ports)
                print()
                
    time.sleep(3)
