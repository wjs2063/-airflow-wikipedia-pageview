# -airflow-wikipedia-pageview
Apache-Airflow 를 이용한 회사별 pageview 파이프라인 구축  
Tableau를이용한 데이터 시각화  
--------------------------------------------------------------------------------------------- 



## 들어가기에 앞서

### DB 의 본질 C R U D 

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
## POSTGRESQL vs MYSQL        
#### POSTGRE SQL -> BSD 라이선스 : 소스변경하고 숨긴후 재배포해도 문제가 되지않음 https://www.olis.or.kr/license/Detailselect.do?lId=1090&mapcode=010021 (확인가능) 
#### POSTGRE SQL -> UPDATE 방식이 delete and insert 형식이라서 시간이 오래걸림 ( mysql에 비해)     
#### POSTGRE SQL -> 클러스터 백업방식을 이용 : 디스크로부터 데이터를 읽어오는 시간을 줄이기위해 자주 사용되는 데이터를  디스크 같은위치에 저장해놓는방법       
#### POSTGRE SQL -> 읽기 및 쓰기 작업에 유리하므로 읽기,쓰기가 빈번한 대규모 시스템에서 최적화된 성능을 발휘할수있다 . 단 UPDATE 가빈번하다면 서버가 불안정한경우가많다고한다       

반대로 

#### MYSQL 은 : 외부에 판매할시 소스코드 공개를 의무화해야함
#### MYSQL -> 높은 유연성과 확장성 , 다양한테이터와 유연하게 연결가능 , 높은 읽기 속도자랑 ,많은 클라우드시스템에서 지원 


### 결론 : 복잡한 읽기쓰기 ? -> POSTGRE SQL ,  빠른 읽기를 원한다? -> MYSQL 




--------------------------------------------------------------------------------------------- 
# USAGE

``` 
    docker-compose up -d
```
---------------------------------------------------------------------------------------------   
#PORT MAPPING  
-              ==============5432===========5433============localhost========8080============ 
-                              |              |                                |       
-                              |              |                                |    
-                            5432           5432                             8080
-              ============postgresql====wiki_results======================webserver=========
---------------------------------------------------------------------------------------------    

airflow connections 추가하기    

airflow webserver 접속후 -> Admin에 connections 클릭 -> add 클릭 -> conn_id : my_postgres ( postgressqloperator 의 id 입력 , type=postgressql,   host:localhost,login:postgres, password:postgres   

추가후에 wiki_results 컨테이너에 접속한다 /bin/bash 접속후    psql -U airflow -h localhost 명령어 실행 후 \l 하면 database 나옴   
---------------------------------------------------------------------------------------------
Tableau  랑 연결작업

postgresql 과 연결 시작

서버: localhost or 해당 ip   
port : 포트포워딩 해준 port 번호적어주기   
database : 설정한 db명 적어주기    
계정,비밀번호 설정한 대로 입력해주기    

TABLEAU 에서 작업중 생겼던 Error  

1.PostgreSQL 데이터 원본 'ShowData'과(와) 통신하는 동안 오류가 발생했습니다.  
잘못된 연결: 데이터 원본에 연결할 수 없습니다.  
오류 코드:8D4946CF  
데이터를 로드하는 동안 오류가 발생했습니다.  
ERROR: current transaction is aborted, commands ignored until end of transaction block;  
Error while executing the query  
SELECT "pageview_counts"."datetime" AS "datetime",  
  "pageview_counts"."pagename" AS "pagename",  
  "pageview_counts"."pageviewcount" AS "pageviewcount"  
FROM "public"."pageview_counts" "pageview_counts"  
LIMIT 10000   
도커컨테이너의 db 서버와 tableau 를 연결후 sql문으로 테이터 추출할때 생겼던 오류 (scheduler 서버또한 켜두고 실시간 으로 진행하던도중)   
해결법: 실시간이라 transaction과정에서 뭔가 오류가떳던모양인지... 아직 해결 못함. 일단은 실시간보다는 Datagrip(workbench)로 파일을 따로 저장한후 진행  

---------------------------------------------------------------------------------------------    
### postgresql 명령어

terminal에서 docker container 로 접속 docker exec -it [컨테이너이름] /bin/bash  
psql -U airflow 




\d [table 명] : table 정보 조회    
\d+ : table 에 용량까지 나옴    
select * from pageview_counts; -> 제대로 저장되어있는지 확인하기 ( 그냥 단순 누적으로 구성되어있음 )  


select k.pagename,k.hr AS "hour", k.average AS "average pageviews" FROM (SELECT pagename,date_part('hour',datetime) AS hr, AVG(pageviewcount) AS average,ROW_NUMBER() OVER (PARTITION BY pagename ORDER BY AVG(pageviewcount) DESC ) from pageview_counts GROUP BY pagename,hr ) as k where row_number=1;

결과: 페이지당 가장있기있는 시간, 평균페이지 뷰 를 보여주게된다.  


아래는 결과사진   



<img width="1305" alt="스크린샷 2022-07-08 오후 11 24 25" src="https://user-images.githubusercontent.com/76778082/178012363-179d6dc2-7216-4120-bdd8-4acf65493673.png">




______________________________________________________________________________________________

## Error
- 1. HTTPConnectionPool(host='18b42363a6c0', port=8793): Max retries exceeded with url: /log/wikipedia/_extract_gz/2022-06-30T00:00:00+00:00/1.log (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x4004923880>: Failed to establish a new connection: [Errno 111] Connection refused'))  
이유 : Connection refused 지속적인 요청을 해서 해당 url에서 거부 였지만 파일경로설정제대로해주고나니 정상작동  
try except 로 time sleep() 도 걸어주면서 시도해보았으나 좀처럼 해결되지않았음, 
결국 문제는 지속적인 http 요청이 문제인것은 맞으나 왜 지속적으로 요청을 하게되었나? 였음 파일 경로문제로 해당 파일에 결과가 계속 저장되지않아서 계속 요청했던것으로 보임
      

- 2.could not translate host name "wiki_results" to address: Name or service not known  
해결법: 도커컨테이너 가 제대로 생성되었는지 확인해본다 ( 안생겨서 찾을수없는 것)  

______________________________________________________________________________________________

## 파이프라인 구축시 DB 정규화를 해야할까?   
해답:   

원천데이터에서 되어있지않다면 굳이 할필요가없다. 이유는 보통 DW 에서 역정규화를 시켜서 데이터 테이블을 관리하는경우가 많음 ( 한눈에 보기위해서 )   
왜 역정규화를 시킬까? join 을 해서 조회해야하는경우라면 굉장한 시간이 들수있다. 이러한경우때문에 그냥 전체테이블로 관리하는경우가많음.  

--------------------------------------------------------------------------------------------- 

잘 실행된 결과 


<img width="1359" alt="스크린샷 2022-07-08 오후 11 16 19" src="https://user-images.githubusercontent.com/76778082/178012743-3569c61c-0408-4335-ac9a-305d48148417.png">

