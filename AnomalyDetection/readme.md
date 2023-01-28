# Cilium Hubble로 수집된 Network Flow 데이터를 사용하 네트워크 이상탐지(Anomaly Detection) 모델

## - 환경: 우분투 22.04(OpenStack), 쿠버네티스, MicroService Demo(Sock-Shop)

## - 사용 라이브러리: pymongo, pandas, tensorflow, skleran, numpy, joblib

## - DB에 새롭게 추가된 데이터가 감지되면 해당 데이터를 호출 -> 데이터를 원-핫 인코더로 인코딩 -> 인코딩 된 데이터를 모델로 판별 -> 이상탐지로 판별되면 출력 후 학습 -> 모델 & 인코더 다시 호출

### - 현재는 학습이 더 필요해 보인다. 60개 정도의 데이터가 들어오면 그중에서 10개 정도만 정상데이터로 판별 하는 듯 하다. 학습이 더 필요해 보인다. 데이터르 한줄씩 가져오지 말고 한번에 가져온 데이터를 사용하는 방법도 고려해 본다.

### - detector.py의 정확도는 80% 전후다. 슬라이딩 윈도우 알고리즘을 활용해서 이상 데이터가 감지되면 가장 오래된 데이터를 지우고 이상감지 데이터를 데이터셋에 append해서 isolation forest 모델과 인코더에 재학습 시킨다. 실제 데이터 생성 시간과 3~11초 정도 차이가 발생한다. 이상 감지 데이터는 db의 별도의 anomaly collection에 저장한다. 
