# LAB_Project
## LAB실 개인과제(쿠버네티스를 이용한 네트워크 플로우 수집 및 데이터 활용)

### 1. 쿠버네티스(k8s) 환경 구성: Master(4g,20g) + worker1(4g,20g) + worker2(4g,20g), CNI: Cilium, Openstack, Ubuntu 22.04 //완성

### 2. Cilium Hubble 설정 및 Hubble Observe 명령어를 사용해서 MongoDB에 Network Flow 데이터 수집 및 singe layer 데이터로 변환(30s 에 한번씩) //완성(gRPC, Protobuf 추가 공부 필요)

### 3. 수집된 데이터를 Anomaly Detection에 맞게 선별 및 가공 및 Kafka와 MongoDB 연결 // 어느정도 완성(기능적으로 구현은 되나 오버헤드가 있음)

### 4. tensorflow lite, ligth ML, caffee2 같은 가벼운 프레임워크로 데이터를 사용해서 실시간 모델 학습(온라인 학습) // 예정

