#  Airflow Weather ETL Pipeline

##  Overview

This project is an end-to-end ETL (Extract, Transform, Load) data pipeline built using **Apache Airflow**, **Docker**, **AWS S3**, and **PostgreSQL**.

The pipeline fetches real-time weather data from the OpenWeather API, processes it, and stores it in both S3 and Postgres for analytics.

---

##  Architecture Diagram

```
                +----------------------+
                |  OpenWeather API     |
                +----------+-----------+
                           |
                           v
                    [Extract Task]
                           |
                           v
                    [Transform Task]
                           |
              +------------+-------------+
              |                          |
              v                          v
      [Load to S3]               [Load to Postgres]
              |                          |
              v                          v
        AWS S3 Bucket              PostgreSQL DB

                (Orchestrated by Apache Airflow)
```

---

##  Tech Stack

* Apache Airflow
* Python
* Docker & Docker Compose
* AWS S3 (via boto3)
* PostgreSQL
* OpenWeather API

---

##  Pipeline Workflow

### 1. Extract

* Fetches weather data from OpenWeather API
* Stores raw JSON locally

### 2. Transform

* Extracts relevant fields:

  * city
  * temperature
  * humidity
  * weather description
  * timestamp
* Saves cleaned data

### 3. Load to S3

* Uploads transformed JSON to S3 bucket
* Organized by date partitions

### 4. Load to PostgreSQL

* Inserts structured data into `weather_data` table

---

##  Project Structure

```
airflow-etl-project/
│
├── dags/
│   └── etl_pipeline.py
├── docker-compose.yaml
├── .env
└── README.md
```

---

##  Airflow Configuration

### Variables

| Key       | Value                    |
| --------- | ------------------------ |
| API_KEY   | Your OpenWeather API key |
| S3_BUCKET | Your S3 bucket name      |

### Connections

#### Postgres

* Conn Id: `postgres_default`
* Host: `postgres`
* DB: `airflow`
* User: `airflow`
* Password: `airflow`

#### AWS

* Conn Id: `aws_default`
* Configure with Access Key & Secret

---

##  How to Run

### 1. Start services

```
docker compose up airflow-init
docker compose up -d
```

### 2. Access Airflow UI

```
http://localhost:8080
```

### 3. Trigger DAG

* DAG: `etl_weather_pipeline`

---

##  Verification

### Check Postgres

```sql
SELECT * FROM weather_data;
```

### Check S3

```
s3://<bucket>/processed/weather/<date>/data.json
```

---

##  Features

* Automated scheduling using Airflow
* Retry logic for robustness
* Modular ETL design
* Dockerized setup for portability

---

##  Future Improvements

* Add data validation checks
* Implement alerting (Slack/Email)
* CI/CD pipeline using Jenkins
* Partitioned storage in S3
* Dashboard using BI tools

---

##  Resume Highlight

> Built a production-style ETL pipeline using Apache Airflow to ingest real-time API data, transform it, and store in AWS S3 and PostgreSQL. Implemented task orchestration, retry mechanisms, and containerized deployment using Docker.

---

##  Author

Gaurang Sahu
