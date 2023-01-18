# Cilium_Hubble_NetworkLogger

## cilium hubble을 이용한 실시간 네트워크 플로우 로그 수집기
## 별도의 Hubble API를 제공하지 않아서 subprocess로 CLI에서 수행되는 명령어를 반복실행 + 포트포워드 연결 종료시 확인 후 재 연결, jsonpb 형태로 MongoDB에 넣어주는 형태
## 추후 grpc와 protobuf를 사용해서 동일한 기능 구현 예정

