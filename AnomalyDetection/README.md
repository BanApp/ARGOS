## 모델 학습 코드 & 모델 호출 및 사용

### 1. trainer_isolation_forest.py: isolation_forest를 이용한 비지도 학습. 작동은 하나 모든 데이터를 outlier로 분류함. 데이터를 더 쌓아서 다시 해볼 필요가 있다.

### 2. Trainer.py : AutoEncoder 사용, 재학습시 데이터를 읽어오지 못하는 오류가 발생.

### 3. Detecotr+Pipeline.py : MongoDB에 새로운 데이터가 쌓이면 해당 데이터를 가져와서 판단, trainer_isolation_forest.py를 통해 학습된 모델을 사용.
