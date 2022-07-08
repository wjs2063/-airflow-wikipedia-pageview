# """
# Documentation of pageview format: https://wikitech.wikimedia.org/wiki/Analytics/Data_Lake/Traffic/Pageviews
# """

from urllib import request

import airflow.utils.dates
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
import time

dag = DAG(
    dag_id="wikipedia_dag",
    start_date=airflow.utils.dates.days_ago(7),
    # 시간별로 
    schedule_interval="@hourly",
    template_searchpath="/opt/airflow",
    max_active_runs=1,
)


def _get_data(year, month, day, hour, output_path):
    url = (
        "https://dumps.wikimedia.org/other/pageviews/"
        #
        f"{year}/{year}-{month:0>2}/pageviews-{year}{month:0>2}{day:0>2}-{hour:0>2}0000.gz"
    )
    # url retrieve를 통해 output_path에 바로 저장
    try:
        request.urlretrieve(url, output_path)
    except NewConnectionError as connecterror:
        print(connecterror)
        time.sleep(2)
        request.urlretrieve(url, output_path)



get_pageview_data = PythonOperator(
    task_id="get_pageview_data",
    python_callable=_get_data,
    op_kwargs={
        "year": "{{ execution_date.year }}",
        "month": "{{ execution_date.month }}",
        "day": "{{ execution_date.day }}",
        "hour": "{{ execution_date.hour }}",
        "output_path": "/opt/airflow/wikipageviews.gz",
    },
    dag=dag,
)


extract_gz = BashOperator(
    task_id="_extract_gz", bash_command="gunzip --force /opt/airflow/wikipageviews.gz", dag=dag
)


def _fetch_pageviews(pagenames, execution_date):
    result = dict.fromkeys(pagenames, 0)
    with open("/opt/airflow/wikipageviews", "r") as f:
        for line in f:
            domain_code, page_title, view_counts, _ = line.split(" ")
            if domain_code == "en" and page_title in pagenames:
                result[page_title] = view_counts

    with open("/opt/airflow/postgres_query.sql", "a") as f:
        for pagename, pageviewcount in result.items():
            f.write(
                "INSERT INTO pageview_counts VALUES ("
                f"'{pagename}', {pageviewcount}, '{execution_date}'"
                ");\n"
            )


fetch_pageviews = PythonOperator(
    task_id="fetch_pageviews",
    python_callable=_fetch_pageviews,
    op_kwargs={"pagenames": {"Naver","SAMSUNG","Airbnb","Google", "Amazon","Microsoft", "Facebook","NVIDIA","Nvidia_3D_Vision","Tesla","Intel","Apple",}},
    dag=dag,
)

write_to_postgres = PostgresOperator(
    task_id="write_to_postgres",
    postgres_conn_id="my_postgres",
    sql="postgres_query.sql",
    dag=dag,
)

# task 의존성 정의
get_pageview_data >> extract_gz >> fetch_pageviews >> write_to_postgres