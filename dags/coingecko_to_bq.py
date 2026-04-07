from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import json
import os
from google.cloud import storage, bigquery

# ── config ──────────────────────────────────────────────
PROJECT_ID   = "project-8adddde0-36db-4a98-805"       # ← replace this
BUCKET_NAME  = "airflow-coingecko-raw"     # ← your bucket name
DATASET_ID   = "crypto_data"
TABLE_ID     = "coin_prices"
COINS        = ["bitcoin", "ethereum", "solana"]
# ────────────────────────────────────────────────────────


def fetch_and_upload_to_gcs(**context):
    """Fetch coin prices from CoinGecko API and upload raw JSON to GCS."""
    
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ",".join(COINS),
        "vs_currencies": "usd",
        "include_market_cap": "true",
        "include_24hr_vol": "true",
        "include_24hr_change": "true",
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    # Add timestamp to the data
    payload = {
        "fetched_at": context["ds"],
        "data": data
    }

    # Upload to GCS
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)
    blob_name = f"raw/{context['ds']}/coin_prices.json"
    blob = bucket.blob(blob_name)
    blob.upload_from_string(
        json.dumps(payload),
        content_type="application/json"
    )

    print(f"Uploaded raw data to gs://{BUCKET_NAME}/{blob_name}")
    return blob_name


def load_gcs_to_bigquery(**context):
    """Read raw JSON from GCS, transform, and load to BigQuery."""

    # Read from GCS
    gcs_client = storage.Client(project=PROJECT_ID)
    bucket = gcs_client.bucket(BUCKET_NAME)
    blob_name = f"raw/{context['ds']}/coin_prices.json"
    blob = bucket.blob(blob_name)
    raw = json.loads(blob.download_as_text())

    # Transform to flat rows
    rows = []
    for coin_id, metrics in raw["data"].items():
        rows.append({
            "date":              raw["fetched_at"],
            "coin_id":           coin_id,
            "price_usd":         metrics.get("usd"),
            "market_cap_usd":    metrics.get("usd_market_cap"),
            "volume_24h_usd":    metrics.get("usd_24h_vol"),
            "change_24h_pct":    metrics.get("usd_24h_change"),
        })

    # Load to BigQuery
    bq_client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    job_config = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("date",           "DATE"),
            bigquery.SchemaField("coin_id",        "STRING"),
            bigquery.SchemaField("price_usd",      "FLOAT"),
            bigquery.SchemaField("market_cap_usd", "FLOAT"),
            bigquery.SchemaField("volume_24h_usd", "FLOAT"),
            bigquery.SchemaField("change_24h_pct", "FLOAT"),
        ],
        write_disposition="WRITE_APPEND",
    )

    job = bq_client.load_table_from_json(rows, table_ref, job_config=job_config)
    job.result()

    print(f"Loaded {len(rows)} rows into {table_ref}")


# ── DAG definition ───────────────────────────────────────
default_args = {
    "owner": "subhash",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="coingecko_to_bigquery",
    description="Fetch crypto prices from CoinGecko and load to BigQuery via GCS",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
    tags=["gcp", "bigquery", "coingecko", "portfolio"],
) as dag:

    fetch_task = PythonOperator(
        task_id="fetch_and_upload_to_gcs",
        python_callable=fetch_and_upload_to_gcs,
    )

    load_task = PythonOperator(
        task_id="load_gcs_to_bigquery",
        python_callable=load_gcs_to_bigquery,
    )

    fetch_task >> load_task