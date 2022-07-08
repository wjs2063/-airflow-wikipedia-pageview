# -airflow-wikipedia-pageview
Apache-Airflow 를 이용한 회사별 pageview 파이프라인 구축

--------------------------------------------------------------------------------------------- 

## 파이프라인 구축시 DB 정규화를 해야할까? 
해답: 

원천데이터에서 되어있지않다면 굳이 할필요가없다. 이유는 보통 DW 에서 역정규화를 시켜서 데이터 테이블을 관리하는경우가 많음 ( 한눈에 보기위해서 ) 
왜 역정규화를 시킬까? join 을 해서 조회해야하는경우라면 굉장한 시간이 들수있다. 이러한경우때문에 그냥 전체테이블로 관리하는경우가많음.

--------------------------------------------------------------------------------------------- 

## 들어가기에 앞서

왜 docker에서 airflow yml파일을 보면 postgresql 이 앞도적으로 많을까? ( mysql,postgresql,orcale,sqlite 등 수많이존재한다) 
  
---------------------------------------------------------------------------------------------   
    
#### mysql 장점 : 보안수준이높음, 설명서많음, 속도가 빠름, 백업솔루션이나 수평적확장용이,가벼움,설치쉬움,호환성  
#### mysql 단점 : DMBS 에대한 개발 이 느림, FULL JOIN 절에 대한 지원이없다  

--------------------------------------------------------------------------------------------- 
 
#### 언제 mysql 을 사용하면좋을까? : 분산작업이 필요한경우에 적합, 웹사이트 및 웹 애플리케이션에 적합    
#### 언제 mysql 을 사용하면안될까? : 동시성과 대용량 데이터 볼륨이 요구되는경우에는 적합하지않음, 응용프로그램을 여러사용자가 한번에많이쓰는경우 부적합   

---------------------------------------------------------------------------------------------  

#### postgresql 장점 : 무료,호환성(모든플랫폼지원), 확장성 용이, 모든언어지원 , 트랜잭션처리용이함, 보안성 높음, 성능높음(파티셔닝하면 성능이더높음)  
#### postgresql 단점 : 데이터 압축부족 ( 대용량애플리케이션성능에 부정적인영향), postgresql에 ML 라이브러리가 없음, 백업 능력이 부족함   

---------------------------------------------------------------------------------------------  

#### sqlite 장점 : 사용용이성, 경량화 ,성능, 안정적임, 유연성(여러언어지원),호환성과 이식성,비용절감 
#### sqlite 단점 : 트래픽이많으면 부적합, 날짜,시간 클래스 지원 x 

---------------------------------------------------------------------------------------------  

airflow connections 추가하기   
airflow webserver 접속후 -> Admin에 connections 클릭 -> add 클릭 -> conn_id : my_postgres ( postgressqloperator 의 id 입력 , type=postgressql, host:localhost,login:postgres, password:postgres,   



______________________________________________________________________________________________

## Error
1. HTTPConnectionPool(host='18b42363a6c0', port=8793): Max retries exceeded with url: /log/wikipedia/_extract_gz/2022-06-30T00:00:00+00:00/1.log (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x4004923880>: Failed to establish a new connection: [Errno 111] Connection refused'))
이유 : Connection refused 지속적인 요청을 해서 해당 url에서 거부 였지만 파일경로설정제대로해주고나니 정상작동 

2.could not translate host name "wiki_results" to address: Name or service not known
해결법: 도커컨테이너 가 제대로 생성되었는지 확인해본다 ( 안생겨서 찾을수없는 것)
