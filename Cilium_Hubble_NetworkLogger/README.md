# Cilium_Hubble_NetworkLogger

## cilium hubble을 이용한 실시간 네트워크 플로우 로그 수집기

## 별도의 Hubble API를 제공하지 않아서 subprocess로 CLI에서 수행되는 명령어를 반복실행 + 포트포워드 연결 종료시 확인 후 재 연결, jsonpb 형태로 MongoDB에 넣어주는 형태 추후 grpc와 protobuf를 사용해서 동일한 기능 구현 예정

## 1. net_log_collector.py의 경우 json 형태로 몽고db에 넣도록 단순하게 반복하는 코드

## 2. logger_final.py의 경우 json 형태로 반환된 데이터를 multi layerd 데이터 형태에서 single layerd 데이터 형태로 바꿔서 추후 비지도 머신러닝 학습에 사용하기 편한 데이터로 몽고DB에 저장하는 코드.

