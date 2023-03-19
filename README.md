# LAB_Project
# 쿠버네티스 환경에서 Cilium Hubble 및 NetData API를 이용한 네트워크 로그 수집 및 이상탐지 모델

<img width="643" alt="스크린샷 2023-02-24 오후 8 24 02" src="https://user-images.githubusercontent.com/93313445/221167832-721669b0-a361-4ce5-ac38-76e33ac85b0a.png">




### 1. 쿠버네티스(k8s) 환경 구성: Master(8g,80g) + worker1(8g,80g) + worker2(8g,80g), CNI: Cilium, Openstack, Ubuntu 22.04 //완성

### 2. Cilium Hubble 설정 및 Hubble Observe 명령어를 사용해서 MongoDB에 Network Flow 데이터 수집 및 singe layer 데이터로 변환(3s 에 한번씩)
- 실제로 cilium hubble은 대략 3~4초 분량의 네트워크 플로우 데이터를 보여준다. 따라서 3s가 누락되는 데이터 없이 오버헤드가 가장 적다.

### 3. Cilium Hubble의 Metrics 데이터는 사용하기 불편한점이 존재. 따라서 NetData API로 실시간 ICMP, TCP, UDP 포트의 개수를 REST API로 받는다.

### 4. 수집된 데이터를 Anomaly Detection에 맞게 선별 및 가공 MongoDB로 연결 및 스트리밍

### 5. Scikit-Learn 사용해서 네트워크 이상 데이터 비지도학습 및 판별 가능(Isolation Forest, One Class SVM, Robust Covariance) 


