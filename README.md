# Airflow BigQuery Pipeline

ETL pipeline that fetches live cryptocurrency prices from the CoinGecko API,
stores raw data in Google Cloud Storage, transforms it, and loads it into BigQuery
for reporting — orchestrated with Apache Airflow running locally via Docker.

## Architecture

## Tech Stack

- Apache Airflow 2.x (LocalExecutor, Docker)
- Google Cloud Storage (raw data lake layer)
- Google BigQuery (reporting layer)
- Python 3.11
- Docker + Docker Compose
- GitHub Actions (CI/CD — auto-deploys DAGs to GCS on push)

## Pipeline Overview

The DAG `coingecko_to_bigquery` runs daily and performs two tasks:

1. `fetch_and_upload_to_gcs` — calls CoinGecko API for Bitcoin, Ethereum
   and Solana prices, uploads raw JSON to GCS at `raw/{date}/coin_prices.json`
2. `load_gcs_to_bigquery` — reads raw JSON from GCS, flattens to rows,
   appends to BigQuery table `crypto_data.coin_prices`

## BigQuery Schema

| Column | Type | Description |
|---|---|---|
| date | DATE | Price fetch date |
| coin_id | STRING | Coin identifier (bitcoin, ethereum, solana) |
| price_usd | FLOAT | Price in USD |
| market_cap_usd | FLOAT | Market cap in USD |
| volume_24h_usd | FLOAT | 24h trading volume in USD |
| change_24h_pct | FLOAT | 24h price change percentage |

## Authentication

Uses Application Default Credentials via `gcloud auth application-default login`.
No service account keys are stored or committed to this repository.

## How to Run Locally

### Prerequisites
- Docker Desktop (8GB RAM recommended)
- Google Cloud SDK installed
- GCP project with BigQuery and Cloud Storage APIs enabled

### Setup
```bash
# 1. Clone the repo
git clone https://github.com/Subhash21c/airflow-bigquery-pipeline.git
cd airflow-bigquery-pipeline

# 2. Authenticate with GCP
gcloud auth application-default login

# 3. Create .env file
echo "AIRFLOW_UID=50000" > .env

# 4. Build and start Airflow
docker compose build
docker compose up airflow-init
docker compose up -d

# 5. Open Airflow UI
# Go to http://localhost:8080
# Username: airflow / Password: airflow
# Trigger the DAG: coingecko_to_bigquery
```

## Project Structure

## Screenshots

### Airflow DAG — successful run
[Add your Airflow UI screenshot here]

### BigQuery — coin_prices table preview
[Add your BigQuery preview screenshot here]
