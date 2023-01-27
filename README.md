# jeju-travel-route-recommendation-system
제주도 관광지 최단 여행 경로 추천 시스템

## 개요 
본 프로그램은 여행 계획 수립시 여행객의 **효율적인 관광지 방문 경로** 계획하는데 도움을 주고자 개발되었다.  
이를 위해, 본 프로그램은 **Brute-Force | Dynamic Programming | 2-opt**의 3가지 알고리즘을 활용해,  
관광지간 최단 폐쇄 경로를 산출하고 사용자에게 해당 경로를 추천한다.

<br>

## API
> <img src="https://img.shields.io/badge/google%20distance%20matrix%20api-F05032?style=for-the-badge&logo=google&logoColor=white">

본 프로그램은 **Google Distance Matrix API** 를 활용해,  
각 관광지간 **실시간 차량 이동 시간**을 계산하여 시스템에 반영한다.


<br>

## Data Set
![image](https://user-images.githubusercontent.com/45115733/215095823-ccded06d-2af5-45cf-8110-a9d32786b119.png)  

본 프로그램은 제주관광공사에 제공하는 제주 관광지 정보를 가공하여,  
(관광지 이름, 관광지 주소)로 구성된 총 3710개의 데이터를 활용한다.

<br>

## Algorithm
본 프로그램의 Flow Chart는 다음과 같다.  
<br>
![image](https://user-images.githubusercontent.com/45115733/215096394-b6b00950-8a6d-4c6f-bbd5-44952954a219.png)

1. **시작점 입력**  
사용자로부터 시작점의 명칭을 입력받는다
2. **관광지 입력**  
사용자로부터 관광지의 명칭을 입력받고, API를 활용해 이동시간 그래프를 구성한다
3. **최단 폐쇄 경로 계산**  
3가지 알고리즘을 활용해 최단 폐쇄 경로를 계산하고, 만약 입력 제한 시간을 초과하면 우선순위를 기준으로 최단 폐쇄 경로를 재산출한다.

자세한 알고리즘 설명은 [presentation.pdf](https://github.com/82KJ/jeju-travel-route-recommendation-system/blob/main/presentation.pdf)를 참고해주세요.


