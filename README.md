# Airflow BigQuery Pipeline

ETL pipeline that fetches live cryptocurrency prices from the CoinGecko API, stores raw data in Google Cloud Storage, transforms it, and loads it into BigQuery for reporting — orchestrated with Apache Airflow running locally via Docker.

---

## Overview

This project demonstrates an end-to-end data engineering pipeline designed to ingest, process, and store cryptocurrency data using modern cloud technologies. The pipeline is structured to reflect real-world data workflows with a focus on scalability and cost efficiency.

---

## Use Case

* Track cryptocurrency prices over time
* Enable historical trend analysis
* Provide a data foundation for analytics and reporting

---

## Architecture

CoinGecko API → Apache Airflow (local) → Google Cloud Storage (raw JSON) → BigQuery (coin_prices table)

---

## Tech Stack

* Apache Airflow 2.x (LocalExecutor, Docker)
* Google Cloud Storage (data lake layer)
* Google BigQuery (analytics layer)
* Python 3.11
* Docker and Docker Compose
* GitHub Actions (CI/CD for DAG deployment)

---

## Pipeline Overview

The DAG `coingecko_to_bigquery` runs daily and performs the following tasks:

1. `fetch_and_upload_to_gcs`

   * Calls CoinGecko API for multiple cryptocurrencies
   * Stores raw JSON data in GCS at `raw/{date}/coin_prices.json`

2. `load_gcs_to_bigquery`

   * Reads raw data from GCS
   * Transforms it into structured format
   * Loads data into BigQuery table `crypto_data.coin_prices`

---

## BigQuery Schema

| Column         | Type   | Description            |
| -------------- | ------ | ---------------------- |
| date           | DATE   | Price fetch date       |
| coin_id        | STRING | Coin identifier        |
| price_usd      | FLOAT  | Price in USD           |
| market_cap_usd | FLOAT  | Market capitalization  |
| volume_24h_usd | FLOAT  | 24-hour trading volume |
| change_24h_pct | FLOAT  | 24-hour price change   |

---

## Data Volume and Cost Considerations

This project uses a limited dataset per run due to API constraints and GCP free-tier usage.

The pipeline is designed to scale by:

* Increasing the number of coins ingested
* Increasing ingestion frequency
* Supporting larger datasets and additional sources

---

## Key Features

* End-to-end ETL pipeline using Apache Airflow
* Multi-source API ingestion (multiple cryptocurrencies)
* Raw data storage in Google Cloud Storage
* Structured data processing in BigQuery
* Cost-efficient design aligned with cloud free-tier usage
* CI/CD integration using GitHub Actions

---

## Future Improvements

* Add retry and error handling mechanisms in Airflow
* Implement structured logging and monitoring
* Parameterize pipeline inputs for flexibility
* Integrate dbt for transformation workflows
* Extend pipeline to support streaming ingestion (Pub/Sub)

---

## Authentication

Authentication is handled using Application Default Credentials:

```bash
gcloud auth application-default login
```

No service account keys are stored in the repository.

---

## How to Run Locally

### Prerequisites

* Docker Desktop (8GB RAM recommended)
* Google Cloud SDK installed
* GCP project with BigQuery and Cloud Storage APIs enabled

### Setup

```bash
git clone https://github.com/Subhash21c/airflow-bigquery-pipeline.git
cd airflow-bigquery-pipeline

gcloud auth application-default login

echo "AIRFLOW_UID=50000" > .env

docker compose build
docker compose up airflow-init
docker compose up -d
```

Access Airflow UI at:
http://localhost:8080

---

## Project Structure

```
airflow-bigquery-pipeline/
├── dags/
│   └── coingecko_to_bq.py
├── Dockerfile
├── requirements.txt
├── docker-compose.yaml
└── .gitignore
```

---

## Screenshots

Airflow DAG — successful run
<img width="1806" height="732" alt="image" src="https://github.com/user-attachments/assets/8220b54e-8207-4663-8c50-054b477546e0" />

BigQuery — coin_prices table preview
<img width="1463" height="755" alt="image" src="https://github.com/user-attachments/assets/0087a650-4610-433a-8173-e5d56982cf6c" />

---

## Author

Subhash Chandra Putla
Data Engineer | GCP | Airflow | BigQuery

---

## Notes

This project focuses on practical data engineering concepts including orchestration, cloud integration, and scalable pipeline design suitable for real-world applications.
