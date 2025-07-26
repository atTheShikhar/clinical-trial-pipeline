# Overview

Reads raw clinical studies data from Google Cloud Storage bucket. Transforms the data by excluding unnecessary details, parsing relevant details and stores the data to `DuckLake` partitioned by `start_year` and `start_month`.

Makes use of `DuckDB` to read raw `json` files as table. Also uses `DuckLake` extension to store the processed data to another bucket.
After the final transformation, the following table structure is created:
```
{
    nct_id: 'VARCHAR', 
    brief_title: 'VARCHAR', 
    conditions: 'VARCHAR[]', 
    intervention_names: 'VARCHAR[]', 
    overall_status: 'VARCHAR', 
    start_date: 'DATE', 
    primary_completion_date: 'DATE',
    start_year: 'INT',
    start_month: 'INT'
}
```


## Setup instructions
1. Make sure `python 3.10` is [installed](https://www.python.org/downloads/).
2. This project uses `uv` [package manager](https://docs.astral.sh/uv/guides/install-python/). 
3. Create a [Service Account](https://cloud.google.com/iam/docs/service-accounts-create) on Google Cloud with read and write access to both `raw` and `ducklake` buckets.
4. Generate the [HMAC keys](https://cloud.google.com/storage/docs/authentication/managing-hmackeys) for the above service account. This will be used by DuckDB to authenticate with Google Cloud in order to access GCS bucket.
5. Set the following environment variables.
```env
GCP_KEY_ID="<HMAC Access_ID>"
GCP_SECRET="<HMAC Secret>"
RAW_GCS_BUCKET="gs://<raw_gcs_bucket_name>"
DUCKLAKE_GCS_BUCKET="gs://<ducklake_gcs_bucket_name>"
MYSQL_USER="<Mysql username>"
MYSQL_PWD="<Mysql password>"
MYSQL_HOST="<Mysql Hostname>"
MYSQL_DATABASE="<Your DuckLake Metadata Dbname>"
MYSQL_TCP_PORT=<MySQL db password>
```

## Usage 
1. Create and load virtual environment to avoid polluting global python dependecies:
```bash
uv venv
source .venv/bin/activate # on unix like system
```
2. Install the project dependencies using 
```bash
uv sync --frozen --no-cache
```
3. Plan the changes with prod environment. This will apply the tranformation and load the relevant data to the destination.
```bash
sqlmesh plan prod
```
